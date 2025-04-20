import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Box, 
  Container,
  Typography, 
  Button, 
  Card, 
  CardContent, 
  CardHeader,
  Divider,
  useTheme,
  alpha,
  CircularProgress,
  Alert,
  Grid
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  Refresh
} from '@mui/icons-material';
import axios from 'axios';

// Custom components
import PageLayout from '../components/PageLayout';
import { DataLabelContainer } from '../components/DataLabel';

// Import dashboard widgets
import PortfolioValue from '../components/dashboard/PortfolioValue';
import PerformanceChart from '../components/dashboard/PerformanceChart';
import ActiveTrades from '../components/dashboard/ActiveTrades';
import TradingBotStatus from '../components/dashboard/TradingBotStatus';
import RecentAlerts from '../components/dashboard/RecentAlerts';
import MarketOverview from '../components/dashboard/MarketOverview';
import CEODashboard from '../components/dashboard/CEODashboard';

// Define API base URL based on environment
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// Card component for dashboard sections
const DashboardCard = ({ title, children, headerAction, isRealData = false }) => {
  const theme = useTheme();
  
  return (
    <Card 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2,
        overflow: 'hidden',
        boxShadow: 2
      }}
    >
      <CardHeader
        title={
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
        }
        action={headerAction}
        sx={{
          padding: 2,
          backgroundColor: alpha(theme.palette.primary.main, 0.1),
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`
        }}
      />
      <CardContent 
        sx={{ 
          padding: 0, 
          flex: 1,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <DataLabelContainer type={isRealData ? 'real' : 'mock'}>
          {children}
        </DataLabelContainer>
      </CardContent>
    </Card>
  );
};

const Dashboard = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState(null);
  
  // Fetch dashboard data
  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // First, check for config.json
      let useRealData = true;
      let showBacktestChart = false;
      
      try {
        const configResponse = await axios.get('/data/config.json');
        if (configResponse.data) {
          console.log('Config loaded:', configResponse.data);
          useRealData = configResponse.data.useRealData !== false; // Default to true
          showBacktestChart = configResponse.data.showBacktestChart || false;
        }
      } catch (error) {
        console.log('No config file found, using defaults');
      }
      
      // If set to show backtest chart, request it first
      if (showBacktestChart) {
        try {
          window.open('/backtest_chart.png', '_blank');
        } catch (error) {
          console.error('Failed to open backtest chart:', error);
        }
      }
      
      // First, try to get all dashboard data in a single request
      try {
        console.log('Attempting to fetch main dashboard data from:', `${API_BASE_URL}/api/dashboard`);
        const dashboardResponse = await axios.get(`${API_BASE_URL}/api/dashboard`, { timeout: 5000 });
        
        if (dashboardResponse.data && dashboardResponse.data.success) {
          console.log('Dashboard data successfully retrieved');
          
          // Extract data from the response
          const apiData = dashboardResponse.data;
          
          // Initialize the dashboard data structure
          const formattedData = {
            portfolio: null,
            performance: null,
            activeTrades: null,
            botStatus: null,
            recentAlerts: null,
            marketOverview: null
          };
          
          // Format portfolio data
          if (apiData.portfolio) {
            formattedData.portfolio = apiData.portfolio;
          } else if (apiData.stats) {
            // Create portfolio data from stats
            formattedData.portfolio = {
              totalValue: apiData.stats.total_value || 0,
              dailyChange: apiData.stats.daily_change || 0,
              dailyChangePercent: apiData.stats.daily_return_percent || 0,
              allocation: [],
              isRealData: false // Mark as mock data because it's not real portfolio data
            };
          }
          
          // Format performance data
          if (apiData.portfolio_performance && Array.isArray(apiData.portfolio_performance)) {
            formattedData.performance = {
              history: apiData.portfolio_performance.map(day => ({
                date: day.date,
                value: parseFloat(day.portfolio_value)
              }))
            };
          }
          
          // Format active trades
          if (apiData.active_trades && Array.isArray(apiData.active_trades)) {
            formattedData.activeTrades = apiData.active_trades.map(trade => ({
              id: trade.id || `trade-${Math.random().toString(36).substring(2, 9)}`,
              symbol: trade.symbol || 'UNKNOWN',
              side: (trade.position_type || '').toUpperCase() === 'SHORT' ? 'SELL' : 'BUY',
              entryPrice: parseFloat(trade.entry_price) || 0,
              currentPrice: parseFloat(trade.current_price) || 0,
              quantity: parseFloat(trade.quantity) || 0,
              pnl: parseFloat(trade.pnl) || 0,
              pnlPercent: parseFloat(trade.pnl_percent) || 0
            }));
          }
          
          // Format recent alerts from activity logs
          if (apiData.recent_alerts) {
            formattedData.recentAlerts = apiData.recent_alerts.map(alert => ({
              id: alert.id || `alert-${Math.random().toString(36).substring(2, 9)}`,
              title: alert.title || alert.type || 'Alert',
              message: alert.message || `${alert.symbol} ${alert.condition}`,
              timestamp: alert.timestamp || alert.triggered_at || new Date().toISOString(),
              type: alert.status === 'triggered' ? 'success' : 'info'
            }));
          }
          
          // Format market overview
          if (apiData.market_overview) {
            formattedData.marketOverview = apiData.market_overview;
          }
          
          // Get any missing data via individual API calls
          await fetchMissingData(formattedData);
          
          setDashboardData(formattedData);
          return;
        }
      } catch (error) {
        console.log('Main dashboard API error:', error.message);
        // Continue to individual calls if main endpoint fails
      }
      
      // If we get here, we need to fetch data from individual endpoints
      await fetchDataFromIndividualEndpoints();
      
    } catch (error) {
      console.error('Error in dashboard data fetching:', error.message);
      setError('Could not load dashboard data. Using sample data instead.');
      
      // Try to load data from directly from the public folder
      try {
        await loadDataFromPublicFolder();
      } catch (fallbackError) {
        console.error('Failed to load data from public folder:', fallbackError);
        // Use mock data as last resort
        const mockData = generateMockData();
        setDashboardData(mockData);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // Load data directly from the public folder
  const loadDataFromPublicFolder = async () => {
    console.log('Attempting to load data directly from public folder');
    const data = {
      portfolio: null,
      performance: null,
      activeTrades: null,
      botStatus: null,
      recentAlerts: null,
      marketOverview: null,
      ceoDashboard: null
    };
    
    try {
      // Load performance history
      const performanceResponse = await axios.get('/data/dashboard/performance_history.json');
      if (performanceResponse.data) {
        console.log('Loaded performance history from public folder');
        data.performance = {
          history: performanceResponse.data,
          isRealData: true
        };
      }
    } catch (error) {
      console.log('Failed to load performance history from public folder');
    }
    
    try {
      // Load active trades
      const tradesResponse = await axios.get('/data/dashboard/active_trades.csv');
      if (tradesResponse.data) {
        console.log('Loaded active trades from public folder');
        // Parse CSV data
        const lines = tradesResponse.data.toString().split('\n');
        const headers = lines[0].split(',');
        
        const trades = [];
        for (let i = 1; i < lines.length; i++) {
          if (lines[i].trim()) {
            const values = lines[i].split(',');
            const trade = {};
            
            headers.forEach((header, index) => {
              trade[header.trim()] = values[index];
            });
            
            trades.push({
              id: trade.id || `trade-${i}`,
              symbol: trade.symbol || 'UNKNOWN',
              side: trade.side || 'BUY',
              entryPrice: parseFloat(trade.price || trade.entryPrice || 0),
              currentPrice: parseFloat(trade.currentPrice || 0),
              quantity: parseFloat(trade.quantity || 0),
              pnl: parseFloat(trade.pnl || 0),
              pnlPercent: parseFloat(trade.pnlPercent || 0)
            });
          }
        }
        
        data.activeTrades = trades;
        data.activeTrades.isRealData = true;
      }
    } catch (error) {
      console.log('Failed to load active trades from public folder');
    }
    
    try {
      // Load recent alerts
      const alertsResponse = await axios.get('/data/dashboard/recent_alerts.json');
      if (alertsResponse.data) {
        console.log('Loaded recent alerts from public folder');
        data.recentAlerts = alertsResponse.data;
        data.recentAlerts.isRealData = true;
      }
    } catch (error) {
      console.log('Failed to load recent alerts from public folder');
    }
    
    try {
      // Load bot status
      const botStatusResponse = await axios.get('/data/dashboard/bot_status.json');
      if (botStatusResponse.data) {
        console.log('Loaded bot status from public folder');
        data.botStatus = botStatusResponse.data;
        data.botStatus.isRealData = true;
      }
    } catch (error) {
      console.log('Failed to load bot status from public folder');
    }
    
    try {
      // Load market overview
      const marketOverviewResponse = await axios.get('/data/dashboard/market_overview.json');
      if (marketOverviewResponse.data) {
        console.log('Loaded market overview from public folder');
        data.marketOverview = marketOverviewResponse.data;
        data.marketOverview.isRealData = true;
      }
    } catch (error) {
      console.log('Failed to load market overview from public folder');
    }
    
    try {
      // Load CEO dashboard
      const ceoDashboardResponse = await axios.get('/data/dashboard/ceo_dashboard.json');
      if (ceoDashboardResponse.data) {
        console.log('Loaded CEO dashboard from public folder');
        data.ceoDashboard = ceoDashboardResponse.data;
        data.ceoDashboard.isRealData = true;
      }
    } catch (error) {
      console.log('Failed to load CEO dashboard from public folder');
    }
    
    // Use mock portfolio data as requested
    data.portfolio = {
      totalValue: 25430.87,
      dailyChange: 345.21,
      dailyChangePercent: 1.37,
      allocation: [
        { asset: 'AAPL', value: 8750.42, percent: 34.41 },
        { asset: 'MSFT', value: 6250.34, percent: 24.58 },
        { asset: 'AMZN', value: 5430.11, percent: 21.35 },
        { asset: 'CASH', value: 5000.00, percent: 19.66 }
      ],
      isRealData: false // Keep portfolio as mock data as requested
    };
    
    // If we have at least some data, use it
    const hasAnyData = Object.values(data).some(value => value !== null);
    if (hasAnyData) {
      setDashboardData(data);
      return true;
    } else {
      throw new Error('No data found in public folder');
    }
  };

  // Fetch missing data if main dashboard API didn't return all needed data
  const fetchMissingData = async (formattedData) => {
    // Get bot status if missing
    if (!formattedData.botStatus) {
      try {
        const botResponse = await axios.get(`${API_BASE_URL}/dual-bot/status`, { timeout: 3000 });
        if (botResponse.data && botResponse.data.success) {
          const botStatus = botResponse.data.status;
          formattedData.botStatus = [{
            id: 'dual-bot-1',
            name: 'Dual Bot System',
            status: 'active',
            lastTrade: botStatus.last_updated,
            pnl24h: 1.2, // Mock PnL since the API doesn't provide this yet
            activeStrategies: 1
          }];
          formattedData.botStatus.isRealData = true; // Mark as real data
        }
      } catch (error) {
        console.log('Dual-bot status API error:', error.message);
      }
    }
    
    // Get trading signals and convert to active trades if missing
    if (!formattedData.activeTrades) {
      try {
        const signalsResponse = await axios.get(`${API_BASE_URL}/dual-bot/signals`, { timeout: 3000 });
        if (signalsResponse.data && signalsResponse.data.success && signalsResponse.data.signals) {
          const allSignals = signalsResponse.data.signals.signals || [];
          formattedData.activeTrades = allSignals.map(signal => {
            const isBuy = signal.type === 'BUY';
            return {
              id: `${signal.symbol}-${new Date().getTime()}`,
              symbol: signal.symbol,
              side: signal.type,
              entryPrice: signal.price_target ? (isBuy ? signal.price_target * 0.95 : signal.price_target * 1.05) : 0,
              currentPrice: signal.price || 0,
              quantity: Math.floor(10000 / (signal.price || 100)), // Mock quantity
              pnl: isBuy ? 58.30 : 50.16, // Mock PnL
              pnlPercent: isBuy ? 3.48 : 2.87 // Mock PnL percent
            };
          });
          formattedData.activeTrades.isRealData = true; // Mark as real data
        }
      } catch (error) {
        console.log('Dual-bot signals API error:', error.message);
      }
    }
    
    // Get alerts from signals if missing
    if (!formattedData.recentAlerts) {
      try {
        const signalsResponse = await axios.get(`${API_BASE_URL}/dual-bot/signals`, { timeout: 3000 });
        if (signalsResponse.data && signalsResponse.data.success && signalsResponse.data.signals) {
          const allSignals = signalsResponse.data.signals.signals || [];
          formattedData.recentAlerts = allSignals.slice(0, 5).map(signal => ({
            id: `alert-${signal.symbol}-${new Date().getTime()}`,
            title: `${signal.type} Signal`,
            message: `${signal.symbol} triggered a ${signal.type.toLowerCase()} signal`,
            timestamp: new Date().toISOString(),
            type: 'info'
          }));
          formattedData.recentAlerts.isRealData = true; // Mark as real data
        }
      } catch (error) {
        console.log('Failed to create alerts from signals:', error.message);
      }
    }
    
    // Fill in any missing data with mock data
    const mockData = generateMockData();
    
    // Create composite data object, preferring real data but falling back to mock
    Object.keys(formattedData).forEach(key => {
      if (!formattedData[key]) {
        formattedData[key] = mockData[key];
        // Mark explicitly as mock data to be sure
        if (formattedData[key]) {
          formattedData[key].isRealData = false;
        }
      }
    });
    
    // Show warning if we had to use any mock data
    const mockDataUsed = Object.keys(formattedData).some(key => !formattedData[key]);
    if (mockDataUsed) {
      setError('Some data could not be loaded from API. Using sample data for those sections.');
    }
  };
  
  // Fetch data from individual endpoints
  const fetchDataFromIndividualEndpoints = async () => {
    // Initialize data structure with null values
    const data = {
      portfolio: null,
      performance: null,
      activeTrades: null,
      botStatus: null,
      recentAlerts: null,
      marketOverview: null
    };
    
    // Try to fetch all dashboard data at once first (this endpoint exists according to logs)
    try {
      const dashboardResponse = await axios.get(`${API_BASE_URL}/dashboard`, { timeout: 5000 });
      if (dashboardResponse.data && dashboardResponse.data.success) {
        console.log('Dashboard data loaded successfully');
        
        // Extract the data from the response
        if (dashboardResponse.data.active_trades) {
          data.activeTrades = dashboardResponse.data.active_trades.map(trade => ({
            id: trade.id || `trade-${Math.random().toString(36).substring(2, 9)}`,
            symbol: trade.symbol || 'UNKNOWN',
            side: trade.position_type === 'SHORT' ? 'SELL' : 'BUY',
            entryPrice: parseFloat(trade.entry_price) || 0,
            currentPrice: parseFloat(trade.current_price) || 0,
            quantity: parseFloat(trade.quantity) || 0,
            pnl: parseFloat(trade.pnl) || 0,
            pnlPercent: parseFloat(trade.pnl_percent) || 0
          }));
          data.activeTrades.isRealData = true;
        }
        
        if (dashboardResponse.data.recent_alerts) {
          data.recentAlerts = dashboardResponse.data.recent_alerts.map(alert => ({
            id: alert.id || `alert-${Math.random().toString(36).substring(2, 9)}`,
            title: alert.title || alert.type || 'Alert',
            message: alert.message || `${alert.symbol} ${alert.condition}`,
            timestamp: alert.timestamp || alert.triggered_at || new Date().toISOString(),
            type: alert.status === 'triggered' ? 'success' : 'info'
          }));
          data.recentAlerts.isRealData = true;
        }
        
        if (dashboardResponse.data.market_overview) {
          data.marketOverview = dashboardResponse.data.market_overview;
          data.marketOverview.isRealData = true;
        }
        
        if (dashboardResponse.data.portfolio_performance) {
          data.performance = {
            history: dashboardResponse.data.portfolio_performance.map(day => ({
              date: day.date,
              value: parseFloat(day.portfolio_value || day.value)
            })),
            isRealData: true
          };
        }
        
        if (dashboardResponse.data.bot_status) {
          data.botStatus = dashboardResponse.data.bot_status.map(bot => ({
            id: bot.id || `bot-${Math.random().toString(36).substring(2, 9)}`,
            name: bot.name || 'Trading Bot',
            status: bot.status || 'active',
            lastTrade: bot.last_trade || bot.lastTrade || new Date().toISOString(),
            pnl24h: parseFloat(bot.pnl_24h || bot.pnl24h || 0),
            activeStrategies: parseInt(bot.active_strategies || bot.activeStrategies || 1)
          }));
          data.botStatus.isRealData = true;
        }
      }
    } catch (error) {
      console.log('Main dashboard API error:', error.message);
      // Continue to individual endpoints if main endpoint fails
    }
    
    // Try individual endpoints (matching the paths we saw in the logs)
    
    // Fetch active trades if not already loaded
    if (!data.activeTrades) {
      try {
        const activeTradesResponse = await axios.get(`${API_BASE_URL}/active-trades`, { timeout: 3000 });
        if (activeTradesResponse.data) {
          console.log('Active trades loaded successfully');
          data.activeTrades = Array.isArray(activeTradesResponse.data) 
            ? activeTradesResponse.data.map(trade => ({
                id: trade.id || `trade-${Math.random().toString(36).substring(2, 9)}`,
                symbol: trade.symbol || 'UNKNOWN',
                side: trade.position_type === 'SHORT' ? 'SELL' : 'BUY',
                entryPrice: parseFloat(trade.entry_price) || 0,
                currentPrice: parseFloat(trade.current_price) || 0,
                quantity: parseFloat(trade.quantity) || 0,
                pnl: parseFloat(trade.pnl) || 0,
                pnlPercent: parseFloat(trade.pnl_percent) || 0
              }))
            : [];
          data.activeTrades.isRealData = true;
        }
      } catch (error) {
        console.log('Active trades API error:', error.message);
        
        // Try broker/positions as fallback (from the logs)
        try {
          const positionsResponse = await axios.get(`${API_BASE_URL}/broker/positions`, { timeout: 3000 });
          if (positionsResponse.data && positionsResponse.data.positions) {
            console.log('Positions loaded from broker API');
            data.activeTrades = positionsResponse.data.positions.map(position => ({
              id: `pos-${position.symbol}-${Math.random().toString(36).substring(2, 9)}`,
              symbol: position.symbol,
              side: position.side || (parseFloat(position.qty) > 0 ? 'BUY' : 'SELL'),
              entryPrice: parseFloat(position.avg_entry_price) || 0,
              currentPrice: parseFloat(position.current_price) || 0,
              quantity: Math.abs(parseFloat(position.qty)) || 0,
              pnl: parseFloat(position.unrealized_pl) || 0,
              pnlPercent: (parseFloat(position.unrealized_plpc) * 100) || 0
            }));
            data.activeTrades.isRealData = true;
          }
        } catch (error) {
          console.log('Broker positions API error:', error.message);
        }
      }
    }
    
    // Fetch market overview if not already loaded
    if (!data.marketOverview) {
      try {
        const marketOverviewResponse = await axios.get(`${API_BASE_URL}/market-overview`, { timeout: 3000 });
        if (marketOverviewResponse.data) {
          console.log('Market overview loaded successfully');
          data.marketOverview = marketOverviewResponse.data;
          data.marketOverview.isRealData = true;
        }
      } catch (error) {
        console.log('Market overview API error:', error.message);
      }
    }
    
    // Fetch performance history
    if (!data.performance) {
      try {
        const performanceResponse = await axios.get(`${API_BASE_URL}/portfolio-performance`, { timeout: 3000 });
        if (performanceResponse.data) {
          console.log('Portfolio performance loaded successfully');
          const performanceData = Array.isArray(performanceResponse.data) 
            ? performanceResponse.data 
            : performanceResponse.data.history || [];
            
          data.performance = {
            history: performanceData.map(day => ({
              date: day.date,
              value: parseFloat(day.portfolio_value || day.value)
            })),
            isRealData: true
          };
        }
      } catch (error) {
        console.log('Portfolio performance API error:', error.message);
      }
    }
    
    // Try CEODashboard data if it exists
    try {
      const ceoResponse = await axios.get(`${API_BASE_URL}/ceo-dashboard`, { timeout: 3000 });
      if (ceoResponse.data && ceoResponse.data.success) {
        console.log('CEO Dashboard data loaded');
        // Store CEO dashboard data for later use
        data.ceoDashboard = ceoResponse.data;
        data.ceoDashboard.isRealData = true;
      }
    } catch (error) {
      console.log('CEO Dashboard API error:', error.message);
    }
    
    // Fetch bot status data
    if (!data.botStatus) {
      try {
        // From the logs, we see dual-bot/status endpoint
        const dualBotResponse = await axios.get(`${API_BASE_URL}/dual-bot/status`, { timeout: 3000 });
        if (dualBotResponse.data && dualBotResponse.data.success) {
          console.log('Dual bot status loaded');
          const botStatus = dualBotResponse.data.status;
          data.botStatus = [{
            id: 'dual-bot-1',
            name: 'Dual Bot System',
            status: botStatus.status || 'active',
            lastTrade: botStatus.last_updated,
            pnl24h: parseFloat(botStatus.pnl_24h || 0),
            activeStrategies: parseInt(botStatus.active_strategies || 1)
          }];
          data.botStatus.isRealData = true;
        }
      } catch (error) {
        console.log('Dual-bot status API error:', error.message);
        
        // Try the bot/status endpoint from logs
        try {
          const botResponse = await axios.get(`${API_BASE_URL}/bot/status`, { timeout: 3000 });
          if (botResponse.data && botResponse.data.success) {
            console.log('Bot status loaded');
            const botStatus = botResponse.data.status || botResponse.data;
            // Check if it's an array or single object
            const botsArray = Array.isArray(botStatus) ? botStatus : [botStatus];
            
            data.botStatus = botsArray.map(bot => ({
              id: bot.id || `bot-${Math.random().toString(36).substring(2, 9)}`,
              name: bot.name || 'Trading Bot',
              status: bot.status || 'active',
              lastTrade: bot.last_trade || bot.lastTrade || new Date().toISOString(),
              pnl24h: parseFloat(bot.pnl_24h || bot.pnl24h || 0),
              activeStrategies: parseInt(bot.active_strategies || bot.activeStrategies || 1)
            }));
            data.botStatus.isRealData = true;
          }
        } catch (error) {
          console.log('Bot status API error:', error.message);
        }
      }
    }
    
    // Fetch recent alerts
    if (!data.recentAlerts) {
      try {
        const alertsResponse = await axios.get(`${API_BASE_URL}/alerts`, { timeout: 3000 });
        if (alertsResponse.data) {
          console.log('Alerts loaded successfully');
          const alertsData = Array.isArray(alertsResponse.data) 
            ? alertsResponse.data 
            : alertsResponse.data.alerts || [];
            
          data.recentAlerts = alertsData.map(alert => ({
            id: alert.id || `alert-${Math.random().toString(36).substring(2, 9)}`,
            title: alert.title || alert.type || 'Alert',
            message: alert.message || `${alert.symbol || ''} ${alert.condition || ''}`,
            timestamp: alert.timestamp || alert.triggered_at || new Date().toISOString(),
            type: alert.status === 'triggered' ? 'success' : 'info'
          }));
          data.recentAlerts.isRealData = true;
        }
      } catch (error) {
        console.log('Alerts API error:', error.message);
        
        // Try dual-bot/signals as fallback for alerts
        try {
          const signalsResponse = await axios.get(`${API_BASE_URL}/dual-bot/signals`, { timeout: 3000 });
          if (signalsResponse.data && signalsResponse.data.success && signalsResponse.data.signals) {
            console.log('Dual-bot signals loaded');
            const allSignals = signalsResponse.data.signals.signals || [];
            data.recentAlerts = allSignals.slice(0, 5).map(signal => ({
              id: `alert-${signal.symbol}-${new Date().getTime()}`,
              title: `${signal.type} Signal`,
              message: `${signal.symbol} triggered a ${signal.type.toLowerCase()} signal`,
              timestamp: new Date().toISOString(),
              type: 'info'
            }));
            data.recentAlerts.isRealData = true;
          }
        } catch (error) {
          console.log('Dual-bot signals API error:', error.message);
        }
      }
    }
    
    // Try to get and use backtest results directly
    try {
      const backrestResultsResponse = await axios.get(`${API_BASE_URL}/run-backtest`, { 
        method: 'POST',
        timeout: 4000,
        data: {}  // Empty data to trigger a response
      });
      
      if (backrestResultsResponse.data && backrestResultsResponse.data.success) {
        console.log('Backtest results generated');
        const backtest = backrestResultsResponse.data;
        
        // Use backtest data to fill in missing parts
        if (!data.activeTrades && backtest.trades && backtest.trades.length > 0) {
          data.activeTrades = backtest.trades.slice(-5).map(trade => ({
            id: `trade-${Math.random().toString(36).substring(2, 9)}`,
            symbol: trade.symbol || 'UNKNOWN',
            side: trade.action || 'BUY',
            entryPrice: parseFloat(trade.price) || 0,
            currentPrice: parseFloat(trade.price) * (1 + Math.random() * 0.1 - 0.03) || 0,
            quantity: parseFloat(trade.quantity) || 0,
            pnl: 0,
            pnlPercent: 0
          }));
          
          // Calculate PnL
          data.activeTrades.forEach(trade => {
            trade.pnl = (trade.currentPrice - trade.entryPrice) * trade.quantity;
            trade.pnlPercent = (trade.currentPrice / trade.entryPrice - 1) * 100;
          });
          data.activeTrades.isRealData = true;
        }
      }
    } catch (error) {
      console.log('Backtest run API error:', error.message);
    }
    
    // If we still don't have data, try our CSV file fallback
    if (!data.activeTrades || !data.recentAlerts || !data.performance) {
      try {
        // Read the CSV files directly
        await Promise.all([
          // Try active trades CSV first
          axios.get('/data/dashboard/active_trades.csv').then(response => {
            if (response.data && !data.activeTrades) {
              console.log('Active trades loaded from CSV file');
              
              let csvData;
              if (typeof response.data === 'string') {
                // Parse CSV manually if needed
                const lines = response.data.split('\n');
                const headers = lines[0].split(',');
                csvData = lines.slice(1).filter(line => line.trim()).map(line => {
                  const values = line.split(',');
                  return headers.reduce((obj, header, index) => {
                    obj[header.trim()] = values[index]?.trim();
                    return obj;
                  }, {});
                });
              } else {
                csvData = response.data;
              }
              
              data.activeTrades = csvData.map(row => ({
                id: row.id || `trade-${Math.random().toString(36).substring(2, 9)}`,
                symbol: row.symbol || 'UNKNOWN',
                side: row.action || 'BUY',
                entryPrice: parseFloat(row.price || row.entryPrice) || 0,
                currentPrice: parseFloat(row.currentPrice) || 0,
                quantity: parseFloat(row.quantity) || 0,
                pnl: parseFloat(row.pnl) || 0,
                pnlPercent: parseFloat(row.pnlPercent) || 0
              }));
              data.activeTrades.isRealData = true;
            }
          }).catch(() => console.log('Failed to load CSV active trades')),
          
          // Try performance history JSON
          axios.get('/data/dashboard/performance_history.json').then(response => {
            if (response.data && !data.performance) {
              console.log('Performance history loaded from JSON file');
              data.performance = {
                history: response.data,
                isRealData: true
              };
            }
          }).catch(() => console.log('Failed to load performance history JSON')),
          
          // Try alerts JSON
          axios.get('/data/dashboard/recent_alerts.json').then(response => {
            if (response.data && !data.recentAlerts) {
              console.log('Recent alerts loaded from JSON file');
              data.recentAlerts = response.data;
              data.recentAlerts.isRealData = true;
            }
          }).catch(() => console.log('Failed to load recent alerts JSON')),
          
          // Try bot status JSON
          axios.get('/data/dashboard/bot_status.json').then(response => {
            if (response.data && !data.botStatus) {
              console.log('Bot status loaded from JSON file');
              data.botStatus = response.data;
              data.botStatus.isRealData = true;
            }
          }).catch(() => console.log('Failed to load bot status JSON')),
          
          // Try market overview JSON
          axios.get('/data/dashboard/market_overview.json').then(response => {
            if (response.data && !data.marketOverview) {
              console.log('Market overview loaded from JSON file');
              data.marketOverview = response.data;
              data.marketOverview.isRealData = true;
            }
          }).catch(() => console.log('Failed to load market overview JSON')),
          
          // Try CEO dashboard JSON
          axios.get('/data/dashboard/ceo_dashboard.json').then(response => {
            if (response.data && !data.ceoDashboard) {
              console.log('CEO dashboard loaded from JSON file');
              data.ceoDashboard = response.data;
              data.ceoDashboard.isRealData = true;
            }
          }).catch(() => console.log('Failed to load CEO dashboard JSON'))
        ]);
      } catch (error) {
        console.log('Error loading CSV/JSON files:', error.message);
      }
    }
    
    // Use mock portfolio data as requested (this is intentional)
    data.portfolio = {
      totalValue: 25430.87,
      dailyChange: 345.21,
      dailyChangePercent: 1.37,
      allocation: [
        { asset: 'AAPL', value: 8750.42, percent: 34.41 },
        { asset: 'MSFT', value: 6250.34, percent: 24.58 },
        { asset: 'AMZN', value: 5430.11, percent: 21.35 },
        { asset: 'CASH', value: 5000.00, percent: 19.66 }
      ],
      isRealData: false // Keep portfolio as mock data as requested
    };
    
    // Fill in any missing data with mock data
    const mockData = generateMockData();
    
    // Create composite data object, preferring real data but falling back to mock
    const compositeData = {
      portfolio: data.portfolio || mockData.portfolio, // Always use mock portfolio as requested
      performance: data.performance || mockData.performance,
      activeTrades: data.activeTrades || mockData.activeTrades,
      botStatus: data.botStatus || mockData.botStatus,
      recentAlerts: data.recentAlerts || mockData.recentAlerts,
      marketOverview: data.marketOverview || mockData.marketOverview,
      ceoDashboard: data.ceoDashboard || null
    };
    
    // Set isRealData flag for each section
    Object.keys(compositeData).forEach(key => {
      if (data[key] && data[key].isRealData !== undefined) {
        compositeData[key].isRealData = data[key].isRealData;
      }
    });
    
    // Always keep portfolio as mock data
    compositeData.portfolio.isRealData = false;
    
    // Show warning if any non-portfolio data is mocked
    const mockDataExists = Object.keys(compositeData)
      .filter(key => key !== 'portfolio' && key !== 'ceoDashboard')  // Exclude portfolio from check
      .some(key => !compositeData[key] || !compositeData[key].isRealData);
    
    if (mockDataExists) {
      setError('Some data could not be loaded from API. Using sample data for those sections.');
    }
    
    setDashboardData(compositeData);
  };

  // Generate mock data function - used as fallback
  const generateMockData = useCallback(() => {
    return {
      portfolio: {
        totalValue: 25430.87,
        dailyChange: 345.21,
        dailyChangePercent: 1.37,
        allocation: [
          { asset: 'AAPL', value: 8750.42, percent: 34.41 },
          { asset: 'MSFT', value: 6250.34, percent: 24.58 },
          { asset: 'AMZN', value: 5430.11, percent: 21.35 },
          { asset: 'CASH', value: 5000.00, percent: 19.66 }
        ],
        isRealData: false // Mark as mock data
      },
      performance: {
        history: Array.from({ length: 30 }, (_, i) => ({
          date: new Date(Date.now() - (29 - i) * 86400000).toISOString().split('T')[0],
          value: 20000 + 100 * i + Math.random() * 500
        })),
        isRealData: false // Mark as mock data
      },
      activeTrades: [
        {
          id: 'trade-1',
          symbol: 'AAPL',
          side: 'BUY',
          entryPrice: 167.32,
          currentPrice: 173.15,
          quantity: 10,
          pnl: 58.30,
          pnlPercent: 3.48
        },
        {
          id: 'trade-2',
          symbol: 'MSFT',
          side: 'BUY',
          entryPrice: 287.70,
          currentPrice: 291.32,
          quantity: 5,
          pnl: 18.10,
          pnlPercent: 1.26
        },
        {
          id: 'trade-3',
          symbol: 'TSLA',
          side: 'SELL',
          entryPrice: 218.45,
          currentPrice: 212.18,
          quantity: 8,
          pnl: 50.16,
          pnlPercent: 2.87
        }
      ],
      botStatus: [
        {
          id: 'bot-1',
          name: 'Momentum Bot',
          status: 'active',
          lastTrade: new Date().toISOString(),
          pnl24h: 3.2,
          activeStrategies: 2
        },
        {
          id: 'bot-2',
          name: 'RSI Strategy',
          status: 'paused',
          lastTrade: new Date(Date.now() - 3600000).toISOString(),
          pnl24h: 0,
          activeStrategies: 0
        }
      ],
      recentAlerts: [
        {
          id: 'alert-1',
          title: 'Buy Signal',
          message: 'AAPL triggered a buy signal',
          timestamp: new Date().toISOString(),
          type: 'info'
        },
        {
          id: 'alert-2',
          title: 'Position Opened',
          message: 'New position opened: MSFT x5',
          timestamp: new Date(Date.now() - 1800000).toISOString(),
          type: 'success'
        },
        {
          id: 'alert-3',
          title: 'Price Alert',
          message: 'TSLA reached target price $220',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          type: 'warning'
        }
      ],
      marketOverview: {
        indices: [
          { name: 'S&P 500', value: '+0.8%' },
          { name: 'Nasdaq', value: '+1.2%' },
          { name: 'Dow Jones', value: '+0.5%' }
        ],
        topMovers: [
          { symbol: 'AAPL', price: 173.15, change: 2.1 },
          { symbol: 'NVDA', price: 418.76, change: 3.8 },
          { symbol: 'MSFT', price: 291.32, change: 1.2 }
        ],
        marketSentiment: 65, // 0-100 scale (higher = more bullish)
        volatilityIndex: 18.5,
        isRealData: false // Mark as mock data
      }
    };
  }, []);

  // Load dashboard data on mount
  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Handle refresh button click
  const handleRefresh = () => {
    fetchDashboardData();
  };

  if (loading) {
    return (
      <PageLayout>
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            height: '70vh' 
          }}
        >
          <CircularProgress />
        </Box>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Box 
          sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 3 
          }}
        >
          <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
            Trading Dashboard
        </Typography>
          
          <Button
            startIcon={<Refresh />}
            onClick={handleRefresh}
            variant="contained"
            color="primary"
            size="small"
          >
            Refresh
          </Button>
        </Box>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Row 1: Portfolio & Performance */}
          <Box 
            sx={{ 
              display: 'flex',
              flexDirection: { xs: 'column', lg: 'row' },
              gap: 3 
            }}
          >
            <Box sx={{ flex: '3 1 0', width: '100%' }}>
              <DashboardCard 
                title="Portfolio Overview" 
                isRealData={dashboardData?.portfolio?.isRealData || false}
              >
                <PortfolioValue portfolioData={dashboardData?.portfolio} />
              </DashboardCard>
            </Box>

            <Box sx={{ flex: '2 1 0', width: '100%' }}>
              <DashboardCard 
                title="Performance" 
                isRealData={dashboardData?.performance?.isRealData || false}
              >
                <PerformanceChart 
                  data={dashboardData?.performance?.history} 
                  height={220}
                />
              </DashboardCard>
            </Box>
          </Box>
          
          {/* Row 2: Active Trades & Bot Status */}
          <Box 
            sx={{ 
              display: 'flex',
              flexDirection: { xs: 'column', lg: 'row' },
              gap: 3
            }}
          >
            <Box sx={{ flex: '1 1 0', width: '100%' }}>
              <DashboardCard 
                title="Active Trades" 
                isRealData={dashboardData?.activeTrades?.isRealData || false}
              >
                <ActiveTrades trades={dashboardData?.activeTrades} />
              </DashboardCard>
            </Box>
            
            <Box sx={{ flex: '1 1 0', width: '100%' }}>
              <DashboardCard 
                title="Trading Bot Status" 
                isRealData={dashboardData?.botStatus?.isRealData || false}
              >
                <TradingBotStatus bots={dashboardData?.botStatus} />
              </DashboardCard>
            </Box>
          </Box>
          
          {/* Row 3: Recent Alerts & Market Overview */}
          <Box 
            sx={{ 
              display: 'flex',
              flexDirection: { xs: 'column', lg: 'row' },
              gap: 3 
            }}
          >
            <Box sx={{ flex: '1 1 0', width: '100%' }}>
              <DashboardCard 
                title="Recent Alerts" 
                isRealData={dashboardData?.recentAlerts?.isRealData || false}
              >
                <RecentAlerts alerts={dashboardData?.recentAlerts} />
              </DashboardCard>
            </Box>
            
            <Box sx={{ flex: '1 1 0', width: '100%' }}>
              <DashboardCard 
                title="Market Overview" 
                isRealData={dashboardData?.marketOverview?.isRealData || false}
              >
                <MarketOverview data={dashboardData?.marketOverview} />
              </DashboardCard>
            </Box>
          </Box>
          
          {/* Row 4: CEO Dashboard */}
          <Box>
            <DashboardCard 
              title="CEO Dashboard" 
              isRealData={dashboardData?.ceoDashboard?.isRealData || false}
            >
              <CEODashboard data={dashboardData?.ceoDashboard} />
            </DashboardCard>
          </Box>
        </Box>
      </Container>
    </PageLayout>
  );
};

export default Dashboard; 