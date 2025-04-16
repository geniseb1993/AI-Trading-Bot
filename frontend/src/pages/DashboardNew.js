import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Box, 
  Grid, 
  Typography, 
  Button, 
  Card, 
  CardContent, 
  CardHeader,
  Divider,
  TextField,
  MenuItem,
  useTheme,
  alpha,
  CircularProgress,
  Alert
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  Refresh, 
  PriceCheck,
  Analytics,
  Add
} from '@mui/icons-material';
import { ResponsivePie } from '@nivo/pie';
import axios from 'axios';
import { motion } from 'framer-motion';

// Custom components
import StatsCard from '../components/StatsCard';
import TradingSignalItem from '../components/TradingSignalItem';
import TradingChart from '../components/TradingChart';
import PageLayout from '../components/PageLayout';
import ContentCard from '../components/ContentCard';
import ContentGrid from '../components/ContentGrid';

// Import dashboard widgets
import PortfolioValue from '../components/dashboard/PortfolioValue';
import PerformanceChart from '../components/dashboard/PerformanceChart';
import ActiveTrades from '../components/dashboard/ActiveTrades';
import TradingBotStatus from '../components/dashboard/TradingBotStatus';
import RecentAlerts from '../components/dashboard/RecentAlerts';
import MarketOverview from '../components/dashboard/MarketOverview';

// Define API base URL based on environment
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const Dashboard = () => {
  console.log("LOADING NEW DASHBOARD COMPONENT v1.0");
  
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [timeframe, setTimeframe] = useState('7');
  const [buySignals, setBuySignals] = useState([]);
  const [shortSignals, setShortSignals] = useState([]);
  const [apiConnected, setApiConnected] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState(null);
  const unmountedRef = useRef(false);
  const retryCount = useRef(0);
  const maxRetries = 3;

  // Sample data to demonstrate the UI
  const performanceData = [
    { id: 'Win Rate', value: 76, color: theme.palette.success.main },
    { id: 'Loss Rate', value: 24, color: theme.palette.error.main },
  ];

  // Helper function to configure axios
  const configureAxios = useCallback(() => {
    // Get token from storage if available
    const token = localStorage.getItem('auth_token');
    
    // Configure axios defaults
    axios.defaults.baseURL = API_BASE_URL;
    
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    
    // Add response interceptor for handling common errors
    axios.interceptors.response.use(
      response => response,
      error => {
        if (error.response && error.response.status === 401) {
          // Handle unauthorized access
          console.warn('Authentication required for API access');
        }
        return Promise.reject(error);
      }
    );
  }, []);

  // Define fetchSignals with better error handling
  const fetchSignals = useCallback(async () => {
    if (unmountedRef.current) return;
    
    try {
      // Try to fetch signals from the API
      try {
        console.log('Attempting to fetch signals from:', `${API_BASE_URL}/api/get-saved-signals`);
        const response = await axios.get('/api/get-saved-signals');
        
        if (response.data && response.data.success && !unmountedRef.current) {
          console.log('Successfully connected to API and retrieved signals');
          setBuySignals(response.data.buy_signals);
          setShortSignals(response.data.short_signals);
          setApiConnected(true);
          return true;
        }
      } catch (error) {
        if (unmountedRef.current) return false;
        
        console.log('Error connecting to API:', error.message);
        console.log('API Error details:', error.response?.data || 'No response data');
        setApiConnected(false);
        
        // Set sample data for demo purposes
        setBuySignals([
          { symbol: 'TSLA', date: '2025-04-01', signal_score: 8.5 },
          { symbol: 'SPY', date: '2025-04-01', signal_score: 7.2 },
          { symbol: 'QQQ', date: '2025-03-31', signal_score: 6.8 },
        ]);
        setShortSignals([
          { symbol: 'XYZ', date: '2025-04-01', signal_score: 4.2 },
        ]);
        return false;
      }
    } catch (error) {
      if (unmountedRef.current) return false;
      console.error('Error in dashboard setup:', error.message);
      return false;
    }
  }, []);

  // Generate mock data function - used as fallback
  const generateMockData = useCallback(() => {
    // Generate sample data for demonstration
    const mockData = {
      portfolio: {
        totalValue: 25430.87,
        dailyChange: 345.21,
        dailyChangePercent: 1.37,
        weeklyChange: 1245.76,
        weeklyChangePercent: 5.15,
        allocation: [
          { asset: 'BTC', value: 12500.34, percent: 49.15 },
          { asset: 'ETH', value: 8750.42, percent: 34.41 },
          { asset: 'BNB', value: 2180.11, percent: 8.57 },
          { asset: 'USDT', value: 2000.00, percent: 7.87 }
        ]
      },
      performance: {
        history: Array.from({ length: 30 }, (_, i) => {
          const date = new Date();
          date.setDate(date.getDate() - (29 - i));
          return {
            date: date.toISOString().split('T')[0],
            value: 20000 + Math.floor(i * 200) + Math.random() * 500
          };
        })
      },
      activeTrades: [
        {
          id: 'trade-123',
          symbol: 'BTCUSDT',
          side: 'BUY',
          entryPrice: 27365.45,
          currentPrice: 27845.12,
          quantity: 0.5,
          pnl: 239.84,
          pnlPercent: 1.75,
          openTime: '2023-04-15T08:30:22Z'
        },
        {
          id: 'trade-124',
          symbol: 'ETHUSDT',
          side: 'BUY',
          entryPrice: 1845.32,
          currentPrice: 1923.45,
          quantity: 3.2,
          pnl: 250.02,
          pnlPercent: 4.23,
          openTime: '2023-04-16T14:22:10Z'
        },
        {
          id: 'trade-125',
          symbol: 'BNBUSDT',
          side: 'SELL',
          entryPrice: 328.45,
          currentPrice: 320.18,
          quantity: 4.5,
          pnl: 37.22,
          pnlPercent: 2.52,
          openTime: '2023-04-17T09:45:33Z'
        }
      ],
      botStatus: [
        {
          id: 'bot-1',
          name: 'EMA Crossover Bot',
          status: 'active',
          lastTrade: '2023-04-17T15:45:20Z',
          pnl24h: 3.2,
          activeStrategies: 2
        },
        {
          id: 'bot-2',
          name: 'RSI Strategy Bot',
          status: 'paused',
          lastTrade: '2023-04-16T22:12:44Z',
          pnl24h: 0,
          activeStrategies: 0
        }
      ],
      recentAlerts: [
        {
          id: 'alert-1',
          symbol: 'BTCUSDT',
          type: 'price',
          condition: 'above',
          value: 28000,
          triggeredAt: '2023-04-17T10:23:45Z',
          status: 'triggered'
        },
        {
          id: 'alert-2',
          symbol: 'ETHUSDT',
          type: 'indicator',
          condition: 'RSI below 30',
          value: null,
          triggeredAt: '2023-04-17T08:11:22Z',
          status: 'triggered'
        }
      ],
      marketOverview: {
        topGainers: [
          { symbol: 'AVAXUSDT', price: 18.24, change: 12.5 },
          { symbol: 'SOLUSDT', price: 22.48, change: 8.7 },
          { symbol: 'DOTUSDT', price: 6.92, change: 6.2 }
        ],
        topLosers: [
          { symbol: 'ATOMUSDT', price: 11.82, change: -5.3 },
          { symbol: 'LINKUSDT', price: 14.23, change: -3.8 },
          { symbol: 'ETCUSDT', price: 19.76, change: -2.4 }
        ],
        btcDominance: 43.2,
        globalMarketCap: 1.27, // in trillions
        fear_greed_index: 65 // 0-100 scale
      }
    };
    
    setDashboardData(mockData);
    return mockData;
  }, []);

  // Enhanced fetchDashboardData with retries
  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('Attempting to fetch dashboard data from:', `${API_BASE_URL}/api/dashboard`);
      const response = await axios.get('/api/dashboard');
      
      if (response.data && response.data.success) {
        console.log('Dashboard data received successfully:', response.data);
        const dashboardData = response.data;
        setDashboardData(dashboardData);
        retryCount.current = 0;
        return true;
      } else {
        throw new Error('Invalid response format from API');
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error.message);
      
      // Check if we should retry or use mock data
      if (retryCount.current < maxRetries) {
        retryCount.current++;
        setError(`Connection attempt ${retryCount.current}/${maxRetries} failed. Retrying...`);
        return false;
      } else {
        setError('Could not connect to backend. Using sample data instead.');
        // Use mock data as a last resort
        generateMockData();
        retryCount.current = 0;
        return false;
      }
    } finally {
      setLoading(false);
    }
  }, [generateMockData]);

  // Initialize dashboard on mount
  useEffect(() => {
    unmountedRef.current = false;
    
    // Configure axios
    configureAxios();
    
    // Initialize with mock data immediately for a better UX
    generateMockData();
    
    // Then try to fetch real data
    const initializeDashboard = async () => {
      setLoading(true);
      
      // Try to fetch dashboard data first
      const dashboardSuccess = await fetchDashboardData();
      
      // If dashboard data failed, try signals
      if (!dashboardSuccess) {
        await fetchSignals();
      }
      
      setLoading(false);
    };
    
    initializeDashboard();
    
    return () => {
      unmountedRef.current = true;
    };
  }, [configureAxios, fetchDashboardData, fetchSignals, generateMockData]);

  // Helper function to parse CSV data
  const parseCSV = (csvText) => {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',');
    
    return lines.slice(1)
      .filter(line => line.trim() !== '')
      .map(line => {
        const values = line.split(',');
        const entry = {};
        
        headers.forEach((header, index) => {
          entry[header] = values[index];
        });
        
        return entry;
      });
  };

  // Handle refresh button click
  const handleRefresh = () => {
    retryCount.current = 0;
    fetchDashboardData();
    fetchSignals();
  };

  // Wrapping performance chart with error boundary div to prevent ResizeObserver errors
  const renderPerformanceChart = () => {
    try {
      return (
        <Box sx={{ height: 200, width: '100%', position: 'relative' }}>
          <ResponsivePie
            data={performanceData}
            margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
            innerRadius={0.6}
            padAngle={0.5}
            cornerRadius={3}
            activeOuterRadiusOffset={8}
            colors={{ datum: 'data.color' }}
            borderWidth={1}
            borderColor={{ from: 'color', modifiers: [['darker', 0.2]] }}
          />
        </Box>
      );
    } catch (error) {
      console.error('Error rendering performance chart:', error);
      return (
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100%' 
        }}>
          <Typography>Chart unavailable</Typography>
        </Box>
      );
    }
  };

  if (loading) {
    return (
      <PageLayout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
          <CircularProgress />
        </Box>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
      )}
      
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" component="h1" sx={{ fontFamily: 'Orbitron' }}>
            Trading Dashboard
          </Typography>
          <Button
            startIcon={<Refresh />} 
            onClick={handleRefresh}
            variant="contained"
            size="small"
            sx={{ fontFamily: 'Orbitron' }}
          >
            Refresh Data
          </Button>
        </Box>

        <Grid container spacing={3}>
          {/* Row 1: Portfolio & Performance */}
          <Grid item xs={12} lg={8}>
            <Card sx={{ 
              height: '100%', 
              borderRadius: 2,
              boxShadow: 3,
              background: `linear-gradient(to bottom right, ${alpha(theme.palette.background.paper, 0.8)}, ${alpha(theme.palette.background.paper, 0.6)})`,
              backdropFilter: 'blur(10px)'
            }}>
              <CardHeader 
                title={<Typography variant="h6" sx={{ fontFamily: 'Orbitron' }}>Portfolio Overview</Typography>}
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent sx={{ p: 0, height: 'calc(100% - 64px)', overflow: 'hidden' }}>
                <PortfolioValue portfolioData={dashboardData?.portfolio || {}} />
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} lg={4}>
            <Card sx={{ 
              height: '100%', 
              borderRadius: 2,
              boxShadow: 3,
              background: `linear-gradient(to bottom right, ${alpha(theme.palette.background.paper, 0.8)}, ${alpha(theme.palette.background.paper, 0.6)})`,
              backdropFilter: 'blur(10px)'
            }}>
              <CardHeader 
                title={<Typography variant="h6" sx={{ fontFamily: 'Orbitron' }}>Performance</Typography>}
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent sx={{ p: 0, height: 'calc(100% - 64px)', overflow: 'hidden' }}>
                <PerformanceChart 
                  data={dashboardData?.performance?.history || []} 
                  height={220}
                />
              </CardContent>
            </Card>
          </Grid>
          
          {/* Row 2: Market Overview & Trading Bots */}
          <Grid item xs={12} lg={8}>
            <Card sx={{ 
              height: '100%', 
              borderRadius: 2,
              boxShadow: 3,
              background: `linear-gradient(to bottom right, ${alpha(theme.palette.background.paper, 0.8)}, ${alpha(theme.palette.background.paper, 0.6)})`,
              backdropFilter: 'blur(10px)'
            }}>
              <CardHeader 
                title={<Typography variant="h6" sx={{ fontFamily: 'Orbitron' }}>Market Overview</Typography>}
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent sx={{ p: 0, height: 'calc(100% - 64px)', overflow: 'hidden' }}>
                <MarketOverview />
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} lg={4}>
            <Card sx={{ 
              height: '100%', 
              borderRadius: 2,
              boxShadow: 3,
              background: `linear-gradient(to bottom right, ${alpha(theme.palette.background.paper, 0.8)}, ${alpha(theme.palette.background.paper, 0.6)})`,
              backdropFilter: 'blur(10px)'
            }}>
              <CardHeader 
                title={<Typography variant="h6" sx={{ fontFamily: 'Orbitron' }}>Trading Bots</Typography>}
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent sx={{ p: 2, height: 'calc(100% - 64px)', overflow: 'auto' }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {dashboardData?.botStatus?.map(bot => (
                    <TradingBotStatus key={bot.id} botData={bot} />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          {/* Row 3: Active Positions & Recent Alerts */}
          <Grid item xs={12} md={6}>
            <Card sx={{ 
              height: '100%', 
              borderRadius: 2,
              boxShadow: 3,
              background: `linear-gradient(to bottom right, ${alpha(theme.palette.background.paper, 0.8)}, ${alpha(theme.palette.background.paper, 0.6)})`,
              backdropFilter: 'blur(10px)'
            }}>
              <CardHeader 
                title={<Typography variant="h6" sx={{ fontFamily: 'Orbitron' }}>Active Positions</Typography>}
                action={
                  <Button size="small" startIcon={<Add />} sx={{ mt: 1 }}>
                    New
                  </Button>
                }
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent sx={{ p: 2, height: 'calc(100% - 64px)', overflow: 'auto' }}>
                <ActiveTrades trades={dashboardData?.activeTrades || []} />
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card sx={{ 
              height: '100%', 
              borderRadius: 2,
              boxShadow: 3,
              background: `linear-gradient(to bottom right, ${alpha(theme.palette.background.paper, 0.8)}, ${alpha(theme.palette.background.paper, 0.6)})`,
              backdropFilter: 'blur(10px)'
            }}>
              <CardHeader 
                title={<Typography variant="h6" sx={{ fontFamily: 'Orbitron' }}>Recent Alerts</Typography>}
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent sx={{ p: 2, height: 'calc(100% - 64px)', overflow: 'auto' }}>
                <RecentAlerts alerts={dashboardData?.recentAlerts || []} />
              </CardContent>
            </Card>
          </Grid>
          
          {/* Row 4: Trading Signals */}
          <Grid item xs={12}>
            <Card sx={{ 
              borderRadius: 2,
              boxShadow: 3,
              background: `linear-gradient(to bottom right, ${alpha(theme.palette.background.paper, 0.8)}, ${alpha(theme.palette.background.paper, 0.6)})`,
              backdropFilter: 'blur(10px)'
            }}>
              <CardHeader 
                title={<Typography variant="h6" sx={{ fontFamily: 'Orbitron' }}>Trading Signals</Typography>}
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent sx={{ p: 2 }}>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" color="success.main" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                      <TrendingUp sx={{ mr: 1 }} />
                      Buy Signals
                    </Typography>
                    <Box sx={{ maxHeight: 300, overflow: 'auto', pr: 1 }}>
                      {buySignals.length > 0 ? (
                        buySignals.map((signal, index) => (
                          <TradingSignalItem key={index} signal={signal} type="buy" />
                        ))
                      ) : (
                        <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                          No buy signals available
                        </Typography>
                      )}
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" color="error.main" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                      <TrendingDown sx={{ mr: 1 }} />
                      Short Signals
                    </Typography>
                    <Box sx={{ maxHeight: 300, overflow: 'auto', pr: 1 }}>
                      {shortSignals.length > 0 ? (
                        shortSignals.map((signal, index) => (
                          <TradingSignalItem key={index} signal={signal} type="short" />
                        ))
                      ) : (
                        <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                          No short signals available
                        </Typography>
                      )}
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </PageLayout>
  );
};

export default Dashboard; 