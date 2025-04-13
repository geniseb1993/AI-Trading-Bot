/**
 * AI Trading Bot Cron Scheduler
 * 
 * This module implements scheduled tasks for the AI Trading Bot using node-cron.
 * It handles trading cycles, market data updates, performance reports, and system maintenance.
 */

const cron = require('node-cron');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { format } = require('date-fns');

// Configuration
const API_BASE_URL = 'http://localhost:5000/api';
const LOG_DIR = path.join(__dirname, 'logs');
const CONFIG_FILE = path.join(__dirname, 'cron-config.json');

// Market hours (Eastern Time - adjust for your market)
const MARKET_OPEN_HOUR = 9; // 9:30 AM ET standard market open
const MARKET_CLOSE_HOUR = 16; // 4:00 PM ET standard market close

// Ensure log directory exists
if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
}

// Load configuration
let config = {
    marketDataInterval: 15, // minutes
    tradingCycleMorning: '30 9 * * 1-5', // 9:30 AM ET Monday-Friday
    tradingCycleEvening: '0 15 * * 1-5', // 3:00 PM ET Monday-Friday 
    additionalTradingCycles: ['0 11 * * 1-5', '0 13 * * 1-5'], // 11 AM and 1 PM ET
    dailyReport: '0 17 * * 1-5', // 5 PM ET Monday-Friday
    weeklyReport: '0 18 * * 5', // 6 PM ET Friday
    dataCleanup: '0 2 * * 0', // 2 AM ET Sunday
    systemHealthCheck: '*/30 * * * *', // Every 30 minutes
    enabled: {
        marketData: true,
        tradingCycles: true,
        reports: true,
        maintenance: true
    }
};

// Load config from file if it exists
try {
    if (fs.existsSync(CONFIG_FILE)) {
        const fileConfig = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
        config = { ...config, ...fileConfig };
        console.log('Loaded configuration from cron-config.json');
    }
} catch (error) {
    console.error('Error loading configuration:', error.message);
}

// Save config to file
const saveConfig = () => {
    try {
        fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
        console.log('Configuration saved to cron-config.json');
    } catch (error) {
        console.error('Error saving configuration:', error.message);
    }
};

// Initialize if config file doesn't exist
if (!fs.existsSync(CONFIG_FILE)) {
    saveConfig();
}

// Logger
const log = (message, type = 'INFO') => {
    const timestamp = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
    const logEntry = `[${timestamp}] [${type}] ${message}`;
    
    console.log(logEntry);
    
    // Also write to file
    const logFile = path.join(LOG_DIR, `cron-${format(new Date(), 'yyyy-MM-dd')}.log`);
    fs.appendFileSync(logFile, logEntry + '\n');
};

// API callers
const apiCall = async (endpoint, method = 'GET', data = null) => {
    try {
        const url = `${API_BASE_URL}${endpoint}`;
        const options = {
            method,
            url,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.data = data;
        }
        
        const response = await axios(options);
        return response.data;
    } catch (error) {
        log(`API call failed: ${endpoint} - ${error.message}`, 'ERROR');
        return { success: false, error: error.message };
    }
};

// Task handlers
const tasks = {
    /**
     * Update market data for tracked symbols
     */
    updateMarketData: async () => {
        if (!config.enabled.marketData) return;
        
        // Check if market is currently open (simplified check)
        const now = new Date();
        const hour = now.getHours();
        const day = now.getDay();
        
        // Only run during market hours on weekdays (Mon-Fri)
        if (day === 0 || day === 6 || hour < MARKET_OPEN_HOUR || hour >= MARKET_CLOSE_HOUR) {
            log('Market is closed. Skipping market data update.');
            return;
        }
        
        log('Starting market data update task');
        try {
            // Get list of tracked symbols
            const marketDataConfig = await apiCall('/market-data/config');
            
            if (!marketDataConfig.success) {
                log('Failed to fetch market data configuration', 'ERROR');
                return;
            }
            
            const symbols = marketDataConfig.data.tracked_symbols || [];
            
            if (symbols.length === 0) {
                log('No symbols configured for tracking. Skipping market data update.');
                return;
            }
            
            // Update market data for each symbol
            log(`Updating market data for ${symbols.length} symbols`);
            const result = await apiCall('/market-data/get-data', 'POST', { symbols });
            
            if (result.success) {
                log(`Market data updated successfully for ${symbols.length} symbols`);
            } else {
                log(`Failed to update market data: ${result.error}`, 'ERROR');
            }
        } catch (error) {
            log(`Error in market data update task: ${error.message}`, 'ERROR');
        }
    },
    
    /**
     * Run a trading cycle with the bot
     */
    runTradingCycle: async () => {
        if (!config.enabled.tradingCycles) return;
        
        log('Starting trading cycle task');
        try {
            // Check bot status first
            const statusResult = await apiCall('/bot/status');
            
            if (!statusResult.success) {
                log('Failed to get bot status', 'ERROR');
                return;
            }
            
            // Only run if bot is active
            if (statusResult.data.status !== 'active') {
                log(`Bot is not active (current status: ${statusResult.data.status}). Skipping trading cycle.`);
                return;
            }
            
            // Run trading cycle
            log('Executing trading cycle');
            const result = await apiCall('/bot/run-cycle', 'POST');
            
            if (result.success) {
                log(`Trading cycle completed: ${result.message}`);
            } else {
                log(`Failed to run trading cycle: ${result.error}`, 'ERROR');
            }
        } catch (error) {
            log(`Error in trading cycle task: ${error.message}`, 'ERROR');
        }
    },
    
    /**
     * Generate daily performance report
     */
    generateDailyReport: async () => {
        if (!config.enabled.reports) return;
        
        log('Generating daily performance report');
        try {
            // Get portfolio performance
            const performance = await apiCall('/bot/performance?days=1');
            
            if (!performance.success) {
                log('Failed to get portfolio performance', 'ERROR');
                return;
            }
            
            // Get active trades
            const trades = await apiCall('/bot/active-trades');
            
            if (!trades.success) {
                log('Failed to get active trades', 'ERROR');
                return;
            }
            
            // Get trading history
            const history = await apiCall('/bot/history?limit=10');
            
            if (!history.success) {
                log('Failed to get trading history', 'ERROR');
                return;
            }
            
            // Compile report
            const report = {
                timestamp: new Date().toISOString(),
                date: format(new Date(), 'yyyy-MM-dd'),
                performance: performance.data,
                activeTrades: trades.data,
                recentTrades: history.data
            };
            
            // Save report to file
            const reportFile = path.join(
                LOG_DIR, 
                `daily-report-${format(new Date(), 'yyyy-MM-dd')}.json`
            );
            
            fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
            log(`Daily report saved to ${reportFile}`);
            
            // TODO: Add email/notification of report when needed
        } catch (error) {
            log(`Error generating daily report: ${error.message}`, 'ERROR');
        }
    },
    
    /**
     * Generate weekly performance report
     */
    generateWeeklyReport: async () => {
        if (!config.enabled.reports) return;
        
        log('Generating weekly performance report');
        try {
            // Get portfolio performance for the week
            const performance = await apiCall('/bot/performance?days=7');
            
            if (!performance.success) {
                log('Failed to get portfolio performance', 'ERROR');
                return;
            }
            
            // Get trading history for the week
            const history = await apiCall('/bot/history?limit=100');
            
            if (!history.success) {
                log('Failed to get trading history', 'ERROR');
                return;
            }
            
            // Compile report
            const report = {
                timestamp: new Date().toISOString(),
                weekEnding: format(new Date(), 'yyyy-MM-dd'),
                weeklyPerformance: performance.data,
                weeklyTrades: history.data
            };
            
            // Save report to file
            const reportFile = path.join(
                LOG_DIR, 
                `weekly-report-${format(new Date(), 'yyyy-[Week]ww')}.json`
            );
            
            fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
            log(`Weekly report saved to ${reportFile}`);
            
            // TODO: Add email/notification of report when needed
        } catch (error) {
            log(`Error generating weekly report: ${error.message}`, 'ERROR');
        }
    },
    
    /**
     * Clean up historical data (logs, old reports)
     */
    cleanupHistoricalData: async () => {
        if (!config.enabled.maintenance) return;
        
        log('Starting historical data cleanup task');
        try {
            // Clean up old logs (keep last 30 days)
            const logFiles = fs.readdirSync(LOG_DIR);
            const now = new Date();
            const thirtyDaysAgo = new Date(now.setDate(now.getDate() - 30));
            
            let cleanedFiles = 0;
            
            for (const file of logFiles) {
                if (file.startsWith('cron-') || file.startsWith('daily-report-')) {
                    // Extract date from filename
                    const dateMatch = file.match(/\d{4}-\d{2}-\d{2}/);
                    
                    if (dateMatch) {
                        const fileDate = new Date(dateMatch[0]);
                        
                        if (fileDate < thirtyDaysAgo) {
                            fs.unlinkSync(path.join(LOG_DIR, file));
                            cleanedFiles++;
                        }
                    }
                }
            }
            
            log(`Cleaned up ${cleanedFiles} old log files`);
            
            // Weekly reports are kept indefinitely by default
        } catch (error) {
            log(`Error in historical data cleanup: ${error.message}`, 'ERROR');
        }
    },
    
    /**
     * Perform system health check
     */
    systemHealthCheck: async () => {
        if (!config.enabled.maintenance) return;
        
        log('Starting system health check');
        try {
            // Check API server status
            const apiStatus = await apiCall('/test');
            
            if (!apiStatus.success) {
                log('API server health check failed', 'ERROR');
                // TODO: Add notification for critical system health issues
            } else {
                log('API server is healthy');
            }
            
            // Check bot status
            const botStatus = await apiCall('/bot/status');
            
            if (!botStatus.success) {
                log('Failed to get bot status during health check', 'ERROR');
            } else {
                log(`Bot status: ${botStatus.data.status}`);
                
                // If bot should be active but is paused, attempt to restart
                if (botStatus.data.should_be_active && botStatus.data.status !== 'active') {
                    log('Bot should be active but is not. Attempting to restart...', 'WARNING');
                    
                    const startResult = await apiCall('/bot/start', 'POST');
                    
                    if (startResult.success) {
                        log(`Successfully restarted bot: ${startResult.message}`);
                    } else {
                        log(`Failed to restart bot: ${startResult.error}`, 'ERROR');
                        // TODO: Add notification for failed bot restart
                    }
                }
            }
        } catch (error) {
            log(`Error in system health check: ${error.message}`, 'ERROR');
        }
    }
};

// Schedule all cron jobs
const scheduleJobs = () => {
    // Market data updates (every X minutes during market hours)
    cron.schedule(`*/${config.marketDataInterval} ${MARKET_OPEN_HOUR}-${MARKET_CLOSE_HOUR} * * 1-5`, () => {
        tasks.updateMarketData();
    });
    
    // Trading cycles
    cron.schedule(config.tradingCycleMorning, () => {
        log('Running morning trading cycle');
        tasks.runTradingCycle();
    });
    
    cron.schedule(config.tradingCycleEvening, () => {
        log('Running evening trading cycle');
        tasks.runTradingCycle();
    });
    
    // Additional trading cycles
    config.additionalTradingCycles.forEach((schedule, index) => {
        cron.schedule(schedule, () => {
            log(`Running additional trading cycle #${index + 1}`);
            tasks.runTradingCycle();
        });
    });
    
    // Daily report
    cron.schedule(config.dailyReport, () => {
        tasks.generateDailyReport();
    });
    
    // Weekly report
    cron.schedule(config.weeklyReport, () => {
        tasks.generateWeeklyReport();
    });
    
    // Data cleanup
    cron.schedule(config.dataCleanup, () => {
        tasks.cleanupHistoricalData();
    });
    
    // System health check
    cron.schedule(config.systemHealthCheck, () => {
        tasks.systemHealthCheck();
    });
    
    log('All cronjobs scheduled successfully');
};

// API for managing the scheduler
const startServer = () => {
    const express = require('express');
    const cronApp = express();
    const PORT = process.env.CRON_PORT || 5050;
    
    cronApp.use(express.json());
    
    // Status endpoint
    cronApp.get('/status', (req, res) => {
        res.json({
            status: 'running',
            config
        });
    });
    
    // Update configuration
    cronApp.post('/config', (req, res) => {
        try {
            const newConfig = req.body;
            
            // Validate incoming config
            if (typeof newConfig !== 'object') {
                return res.status(400).json({ 
                    success: false, 
                    error: 'Invalid configuration format' 
                });
            }
            
            // Update config
            config = { ...config, ...newConfig };
            
            // Save updated config
            saveConfig();
            
            res.json({ 
                success: true, 
                message: 'Configuration updated successfully',
                config
            });
        } catch (error) {
            res.status(500).json({ 
                success: false, 
                error: `Failed to update configuration: ${error.message}` 
            });
        }
    });
    
    // Manual task triggers
    cronApp.post('/run/:task', async (req, res) => {
        const { task } = req.params;
        
        if (!tasks[task]) {
            return res.status(404).json({ 
                success: false, 
                error: `Task "${task}" not found` 
            });
        }
        
        try {
            log(`Manually running task: ${task}`);
            await tasks[task]();
            
            res.json({ 
                success: true, 
                message: `Task "${task}" executed successfully` 
            });
        } catch (error) {
            res.status(500).json({ 
                success: false, 
                error: `Failed to run task "${task}": ${error.message}` 
            });
        }
    });
    
    // Start the server
    cronApp.listen(PORT, () => {
        log(`Cron scheduler management API running on port ${PORT}`);
    });
};

// Initialize
const init = () => {
    log('Starting AI Trading Bot Cron Scheduler');
    scheduleJobs();
    startServer();
};

// Start the scheduler
init(); 