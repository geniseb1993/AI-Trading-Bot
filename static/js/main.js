/**
 * Main JavaScript for Vicki AI Trading Bot
 * This script initializes the dashboard UI and provides fallback mechanisms.
 */

// Clear fallback timer if JS loaded successfully
if (window.fallbackTimer) {
    clearTimeout(window.fallbackTimer);
    console.log('Cleared fallback timer - main.js loaded successfully');
}

// Main initialization function
(function() {
    console.log('Vicki AI Trading Bot - Main script initializing');
    
    // Function to load the dashboard UI
    function loadDashboardUI() {
        console.log('Loading dashboard UI');
        
        // Get the root element
        const root = document.getElementById('root');
        if (!root) {
            console.error('Root element not found');
            return false;
        }
        
        try {
            // Remove loading indicator if present
            const loader = root.querySelector('.app-loading');
            if (loader) {
                root.removeChild(loader);
            }
            
            // Create the dashboard UI
            root.innerHTML = `
            <div style="display: flex; min-height: 100vh;">
                <!-- Sidebar -->
                <div style="width: 220px; background-color: #111; padding: 20px; border-right: 2px solid #ff00ff;">
                    <div style="text-align: center; margin-bottom: 40px;">
                        <img src="/static/images/logo.png" alt="Vicki Logo" style="width: 80px; height: 80px; border-radius: 50%;" 
                             onerror="this.onerror=null; this.src='/static/images/vicky.png'; if (this.src.includes('static/images/vicky.png')) this.onerror=function(){this.style.display='none'; this.parentNode.innerHTML += '<div style=\"width: 80px; height: 80px; border-radius: 50%; background-color: #ff00ff; margin: 0 auto; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;\">V</div>';}">
                        <h2 style="color: #ff00ff; margin-top: 10px;">VICKY</h2>
                    </div>
                    
                    <div style="margin-bottom: 30px;">
                        <div style="display: flex; align-items: center; padding: 10px; background-color: #1e1e2f; margin-bottom: 10px; cursor: pointer; border-left: 4px solid #ff00ff; color: white;">
                            <span style="margin-right: 10px;">📊</span>
                            <span>Dashboard</span>
                        </div>
                        <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                            <span style="margin-right: 10px;">📈</span>
                            <span>Live Market</span>
                        </div>
                        <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                            <span style="margin-right: 10px;">🔍</span>
                            <span>Signals</span>
                        </div>
                        <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                            <span style="margin-right: 10px;">⏱️</span>
                            <span>Backtest</span>
                        </div>
                        <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                            <span style="margin-right: 10px;">📊</span>
                            <span>Market Data</span>
                        </div>
                        <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                            <span style="margin-right: 10px;">📢</span>
                            <span>TradingView Alerts</span>
                        </div>
                        <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                            <span style="margin-right: 10px;">⚙️</span>
                            <span>API Configuration</span>
                        </div>
                        <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                            <span style="margin-right: 10px;">📊</span>
                            <span>Market Analysis</span>
                        </div>
                        <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                            <span style="margin-right: 10px;">💼</span>
                            <span>Institutional Flow</span>
                        </div>
                        <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                            <span style="margin-right: 10px;">⚙️</span>
                            <span>Trade Setups</span>
                        </div>
                        <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; cursor: pointer; color: #aaa;">
                            <span style="margin-right: 10px;">🛡️</span>
                            <span>Risk Management</span>
                        </div>
                    </div>
                    
                    <div style="position: absolute; bottom: 20px; left: 20px; font-size: 12px; color: #666;">
                        v2.0 · Vicky
                    </div>
                </div>
                
                <!-- Main Content -->
                <div style="flex: 1; padding: 20px;">
                    <!-- Header with Bell Icon -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <div></div>
                        <div style="display: flex; align-items: center;">
                            <div style="margin-right: 15px; font-size: 20px; cursor: pointer;">🔔</div>
                            <button style="background-color: #1c1c2e; color: #ff00ff; border: 2px solid #ff00ff; padding: 8px 16px; border-radius: 4px; cursor: pointer;">CLOSE VAULT</button>
                        </div>
                    </div>
                    
                    <!-- Dashboard Content -->
                    <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                        <!-- Portfolio Overview -->
                        <div style="flex-basis: calc(60% - 20px); background-color: #1c1c2e; border-radius: 10px; padding: 20px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <h2 style="margin: 0; color: #ddd;">Portfolio Overview</h2>
                                <button style="background-color: #1c1c2e; color: #aaa; border: 1px solid #333; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Mock Data</button>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div>
                                    <h1 style="font-size: 3rem; margin: 20px 0; color: #fff;">$25,430.87</h1>
                                    <div style="color: #4caf50; margin-bottom: 10px;">
                                        <span style="font-size: 1.2rem;">+345.21 (+1.37%)</span>
                                        <span style="margin-left: 10px; color: #aaa;">Today</span>
                                    </div>
                                    <div style="color: #4caf50; margin-bottom: 10px;">
                                        <span style="font-size: 1.2rem;">+0.00 (+0%)</span>
                                        <span style="margin-left: 10px; color: #aaa;">This Week</span>
                                    </div>
                                </div>
                                
                                <div>
                                    <h3 style="color: #ddd; margin-bottom: 15px;">Asset Allocation</h3>
                                    <!-- Asset allocation would go here -->
                                </div>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; margin-top: 30px;">
                                <div style="background-color: #171727; padding: 15px; border-radius: 8px; width: 22%;">
                                    <div style="color: #aaa;">AAPL</div>
                                    <div style="color: #aaa; font-size: 0.8rem;">34.4%</div>
                                    <div style="height: 5px; background-color: #222; margin: 10px 0;">
                                        <div style="height: 100%; width: 34.4%; background-color: #ff00ff;"></div>
                                    </div>
                                    <div style="font-weight: bold;">$8,750.42</div>
                                </div>
                                
                                <div style="background-color: #171727; padding: 15px; border-radius: 8px; width: 22%;">
                                    <div style="color: #aaa;">MSFT</div>
                                    <div style="color: #aaa; font-size: 0.8rem;">24.6%</div>
                                    <div style="height: 5px; background-color: #222; margin: 10px 0;">
                                        <div style="height: 100%; width: 24.6%; background-color: #ff00ff;"></div>
                                    </div>
                                    <div style="font-weight: bold;">$6,250.34</div>
                                </div>
                                
                                <div style="background-color: #171727; padding: 15px; border-radius: 8px; width: 22%;">
                                    <div style="color: #aaa;">AMZN</div>
                                    <div style="color: #aaa; font-size: 0.8rem;">21.4%</div>
                                    <div style="height: 5px; background-color: #222; margin: 10px 0;">
                                        <div style="height: 100%; width: 21.4%; background-color: #ff00ff;"></div>
                                    </div>
                                    <div style="font-weight: bold;">$5,430.11</div>
                                </div>
                                
                                <div style="background-color: #171727; padding: 15px; border-radius: 8px; width: 22%;">
                                    <div style="color: #aaa;">CASH</div>
                                    <div style="color: #aaa; font-size: 0.8rem;">19.7%</div>
                                    <div style="height: 5px; background-color: #222; margin: 10px 0;">
                                        <div style="height: 100%; width: 19.7%; background-color: #ff00ff;"></div>
                                    </div>
                                    <div style="font-weight: bold;">$5,000.00</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Performance Panel -->
                        <div style="flex-basis: calc(40% - 20px); background-color: #1c1c2e; border-radius: 10px; padding: 20px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <h2 style="margin: 0; color: #ddd;">Performance</h2>
                                <button style="background-color: #1c1c2e; color: #aaa; border: 1px solid #333; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Mock Data</button>
                            </div>
                            
                            <div style="height: 200px; display: flex; justify-content: center; align-items: center;">
                                <p style="color: #aaa;">No performance data available</p>
                            </div>
                        </div>
                        
                        <!-- Active Trades -->
                        <div style="flex-basis: calc(60% - 20px); background-color: #1c1c2e; border-radius: 10px; padding: 20px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <h2 style="margin: 0; color: #ddd;">Active Trades</h2>
                                <button style="background-color: #1c1c2e; color: #aaa; border: 1px solid #333; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Mock Data</button>
                            </div>
                            
                            <div style="display: flex; align-items: center; background-color: #171727; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                                <div style="width: 100px; text-align: center; background-color: #660066; color: white; padding: 5px; border-radius: 5px; margin-right: 10px;">UNKNOWN</div>
                                <div style="width: 60px; text-align: center; background-color: #4caf50; color: black; padding: 5px; border-radius: 5px; margin-right: 30px;">BUY</div>
                                <div style="flex: 1;">
                                    <div style="margin-bottom: 5px;">
                                        <span style="color: #aaa; margin-right: 5px;">Entry:</span>
                                        <span>$500.71</span>
                                    </div>
                                    <div>
                                        <span style="color: #aaa; margin-right: 5px;">Current:</span>
                                        <span>$490.33</span>
                                    </div>
                                </div>
                                <div style="flex: 1;">
                                    <div style="margin-bottom: 5px; color: #f44336;">-10.38</div>
                                    <div style="color: #f44336;">-2.07%</div>
                                </div>
                                <div style="width: 80px; text-align: right;">
                                    <div style="margin-bottom: 5px; color: #aaa;">N/A</div>
                                    <div>Qty: 1</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Trading Bot Status -->
                        <div style="flex-basis: calc(40% - 20px); background-color: #1c1c2e; border-radius: 10px; padding: 20px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <h2 style="margin: 0; color: #ddd;">Trading Bot Status</h2>
                                <button style="background-color: #1c1c2e; color: #aaa; border: 1px solid #333; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Mock Data</button>
                            </div>
                            
                            <h3 style="color: #ddd; margin-bottom: 15px;">Trading Bots</h3>
                            
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                                <div style="display: flex; align-items: center;">
                                    <div style="margin-right: 10px; height: 20px; width: 20px; border-radius: 50%; background-color: #4caf50;"></div>
                                    <div>AI Trading Bot</div>
                                </div>
                                <div style="background-color: #4caf50; color: black; padding: 5px 15px; border-radius: 5px;">Active</div>
                            </div>
                            
                            <button style="width: 100%; background-color: #ff00ff; color: white; border: none; padding: 15px; border-radius: 5px; cursor: pointer; font-weight: bold;">TEST TRADING ALERT</button>
                        </div>
                    </div>
                </div>
            </div>
            `;
            
            return true;
        } catch (error) {
            console.error('Error loading dashboard UI:', error);
            return false;
        }
    }
    
    // Try to load the dashboard UI
    try {
        // First check if we're on the right page with a root element
        if (document.getElementById('root')) {
            console.log('Found root element, loading UI');
            
            // Wait a short time to ensure DOM is ready
            setTimeout(function() {
                const uiLoaded = loadDashboardUI();
                if (uiLoaded) {
                    console.log('Dashboard UI loaded successfully');
                } else {
                    console.error('Failed to load dashboard UI');
                }
            }, 100);
        } else {
            console.warn('No root element found, might be on a different page');
        }
    } catch (error) {
        console.error('Critical error loading UI:', error);
    }
    
    // Add event to report successful load
    window.addEventListener('load', function() {
        console.log('Window fully loaded with dashboard UI');
        
        // Check if any images failed to load
        setTimeout(function() {
            document.querySelectorAll('img').forEach(function(img) {
                if (!img.complete || img.naturalHeight === 0) {
                    console.warn('Image failed to load:', img.src);
                }
            });
        }, 1000);
    });
})(); 