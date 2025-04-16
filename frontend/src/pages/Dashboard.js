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
  Alert
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  Refresh
} from '@mui/icons-material';
import axios from 'axios';

// Custom components
import PageLayout from '../components/PageLayout';

// Import dashboard widgets
import PortfolioValue from '../components/dashboard/PortfolioValue';
import PerformanceChart from '../components/dashboard/PerformanceChart';
import ActiveTrades from '../components/dashboard/ActiveTrades';
import TradingBotStatus from '../components/dashboard/TradingBotStatus';
import RecentAlerts from '../components/dashboard/RecentAlerts';
import MarketOverview from '../components/dashboard/MarketOverview';

// Define API base URL based on environment
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// Card component for dashboard sections
const DashboardCard = ({ title, children, headerAction }) => {
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
        {children}
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
              positions: []
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
      
      // Use mock data as fallback
      const mockData = generateMockData();
      setDashboardData(mockData);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch missing data if main dashboard API didn't return all needed data
  const fetchMissingData = async (formattedData) => {
    // Get bot status if missing
    if (!formattedData.botStatus) {
      try {
        const botResponse = await axios.get(`${API_BASE_URL}/api/bot/status`, { timeout: 3000 });
        if (botResponse.data && botResponse.data.success) {
          const botData = botResponse.data.data || botResponse.data;
          formattedData.botStatus = Array.isArray(botData) ? botData : [botData];
        }
      } catch (error) {
        console.log('Bot status API error:', error.message);
      }
    }
    
    // Get alerts if missing
    if (!formattedData.recentAlerts) {
      try {
        const alertsResponse = await axios.get(`${API_BASE_URL}/api/activity-log`, { timeout: 3000 });
        if (alertsResponse.data && alertsResponse.data.success) {
          const alertsData = alertsResponse.data.data || alertsResponse.data;
          formattedData.recentAlerts = alertsData.slice(0, 10).map(alert => ({
            id: alert.id || `alert-${Math.random().toString(36).substring(2, 9)}`,
            title: alert.title || alert.activity_type || 'Alert',
            message: alert.message || alert.details || 'System notification',
            timestamp: alert.timestamp || alert.created_at || new Date().toISOString(),
            type: alert.type || 'info'
          }));
        }
      } catch (error) {
        console.log('Activity log API error:', error.message);
      }
    }
    
    // Fill in any missing data with mock data
    const mockData = generateMockData();
    
    // Create composite data object, preferring real data but falling back to mock
    Object.keys(formattedData).forEach(key => {
      if (!formattedData[key]) {
        formattedData[key] = mockData[key];
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
    
    // Fetch portfolio data
    try {
      const portfolioResponse = await axios.get(`${API_BASE_URL}/api/user-portfolio`, { timeout: 3000 });
      if (portfolioResponse.data && portfolioResponse.data.success) {
        console.log('Portfolio data loaded');
        data.portfolio = portfolioResponse.data.portfolio;
      }
    } catch (error) {
      console.log('Portfolio API error:', error.message);
    }
    
    // Fetch performance data
    try {
      const performanceResponse = await axios.get(`${API_BASE_URL}/api/portfolio-performance`, { timeout: 3000 });
      if (performanceResponse.data && performanceResponse.data.success) {
        console.log('Performance data loaded');
        const performanceData = performanceResponse.data.portfolio_performance || performanceResponse.data;
        data.performance = {
          history: performanceData.map(day => ({
            date: day.date || new Date().toISOString().split('T')[0],
            value: parseFloat(day.portfolio_value) || 0
          }))
        };
      }
    } catch (error) {
      console.log('Performance API error:', error.message);
    }
    
    // Fetch active trades
    try {
      const tradesResponse = await axios.get(`${API_BASE_URL}/api/active-trades`, { timeout: 3000 });
      if (tradesResponse.data && tradesResponse.data.success) {
        console.log('Active trades loaded');
        const tradesData = tradesResponse.data.active_trades || tradesResponse.data;
        data.activeTrades = tradesData.map(trade => ({
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
    } catch (error) {
      console.log('Trades API error:', error.message);
    }
    
    // Fetch bot status
    try {
      const botResponse = await axios.get(`${API_BASE_URL}/api/bot/status`, { timeout: 3000 });
      if (botResponse.data && botResponse.data.success) {
        console.log('Bot status loaded');
        const botData = botResponse.data.data || botResponse.data;
        data.botStatus = Array.isArray(botData) ? botData : [botData];
      }
    } catch (error) {
      console.log('Bot API error:', error.message);
    }
    
    // Fetch recent alerts
    try {
      const alertsResponse = await axios.get(`${API_BASE_URL}/api/activity-log`, { timeout: 3000 });
      if (alertsResponse.data) {
        console.log('Alerts loaded');
        const alertsData = alertsResponse.data.data || alertsResponse.data;
        data.recentAlerts = alertsData.slice(0, 10).map(alert => ({
          id: alert.id || `alert-${Math.random().toString(36).substring(2, 9)}`,
          title: alert.title || alert.activity_type || 'Alert',
          message: alert.message || alert.details || 'System notification',
          timestamp: alert.timestamp || alert.created_at || new Date().toISOString(),
          type: alert.type || 'info'
        }));
      }
    } catch (error) {
      console.log('Alerts API error:', error.message);
    }
    
    // Fetch market overview
    try {
      const marketResponse = await axios.get(`${API_BASE_URL}/api/market-data`, { timeout: 3000 });
      if (marketResponse.data && marketResponse.data.success) {
        console.log('Market data loaded');
        data.marketOverview = marketResponse.data;
      } else {
        // Try market overview endpoint as fallback
        const marketOverviewResponse = await axios.get(`${API_BASE_URL}/api/market-overview`, { timeout: 3000 });
        if (marketOverviewResponse.data && marketOverviewResponse.data.success) {
          console.log('Market overview loaded');
          data.marketOverview = marketOverviewResponse.data.market_data;
        }
      }
    } catch (error) {
      console.log('Market data API error:', error.message);
    }
    
    // Fill in any missing data with mock data
    const mockData = generateMockData();
    
    // Create composite data object, preferring real data but falling back to mock
    const compositeData = {
      portfolio: data.portfolio || mockData.portfolio,
      performance: data.performance || mockData.performance,
      activeTrades: data.activeTrades || mockData.activeTrades,
      botStatus: data.botStatus || mockData.botStatus,
      recentAlerts: data.recentAlerts || mockData.recentAlerts,
      marketOverview: data.marketOverview || mockData.marketOverview
    };
    
    // Update state with the composed data
    setDashboardData(compositeData);
    
    // Show warning if we had to use any mock data
    const mockDataUsed = Object.keys(data).some(key => data[key] === null);
    if (mockDataUsed) {
      setError('Some data could not be loaded from API. Using sample data for those sections.');
    }
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
        ]
      },
      performance: {
        history: Array.from({ length: 30 }, (_, i) => ({
          date: new Date(Date.now() - (29 - i) * 86400000).toISOString().split('T')[0],
          value: 20000 + 100 * i + Math.random() * 500
        }))
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
        volatilityIndex: 18.5
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
              <DashboardCard title="Portfolio Overview">
                <PortfolioValue portfolioData={dashboardData?.portfolio} />
              </DashboardCard>
                    </Box>

            <Box sx={{ flex: '2 1 0', width: '100%' }}>
              <DashboardCard title="Performance">
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
              <DashboardCard title="Active Trades">
                <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                  <ActiveTrades trades={dashboardData?.activeTrades} />
                </Box>
              </DashboardCard>
            </Box>
            
            <Box sx={{ flex: '1 1 0', width: '100%' }}>
              <DashboardCard title="Trading Bots">
                <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                  {dashboardData?.botStatus?.map(bot => (
                    <Box 
                      key={bot.id} 
                      sx={{ 
                        mb: 2,
                        p: 2,
                        borderRadius: 1,
                        bgcolor: bot.status === 'active' 
                          ? alpha(theme.palette.success.main, 0.1)
                          : alpha(theme.palette.grey[500], 0.1)
                      }}
                    >
                      <TradingBotStatus botData={bot} />
                    </Box>
                  ))}
                </Box>
              </DashboardCard>
            </Box>
          </Box>
          
          {/* Row 3: Market Overview & Alerts */}
          <Box 
            sx={{ 
              display: 'flex',
              flexDirection: { xs: 'column', lg: 'row' },
              gap: 3
            }}
          >
            <Box sx={{ flex: '2 1 0', width: '100%' }}>
              <DashboardCard title="Market Overview">
                <MarketOverview />
              </DashboardCard>
            </Box>
            
            <Box sx={{ flex: '1 1 0', width: '100%' }}>
              <DashboardCard title="Recent Alerts">
                <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                  <RecentAlerts alerts={dashboardData?.recentAlerts} />
                </Box>
              </DashboardCard>
            </Box>
          </Box>
    </Box>
      </Container>
    </PageLayout>
  );
};

export default Dashboard; 