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
import ScrollableContent from '../components/ScrollableContent';

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
        
        // Try to fetch CSV files directly
        try {
          console.log('Trying to fetch CSV files directly from public folder');
          const buySignalsResponse = await axios.get('/buy_signals.csv');
          const shortSignalsResponse = await axios.get('/short_signals.csv');
          
          if (buySignalsResponse.data && shortSignalsResponse.data && !unmountedRef.current) {
            // Parse CSV data
            const parsedBuySignals = parseCSV(buySignalsResponse.data);
            const parsedShortSignals = parseCSV(shortSignalsResponse.data);
            
            setBuySignals(parsedBuySignals);
            setShortSignals(parsedShortSignals);
            console.log('Using CSV files from public folder');
            return true;
          } else {
            throw new Error('CSV files not properly loaded');
          }
        } catch (csvError) {
          if (unmountedRef.current) return false;
          
          console.log('Failed to load CSV files:', csvError.message);
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
        },
        {
          id: 'bot-3',
          name: 'MACD Strategy Bot',
          status: 'active',
          lastTrade: '2023-04-17T14:02:12Z',
          pnl24h: -1.5,
          activeStrategies: 1
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
        },
        {
          id: 'alert-3',
          symbol: 'BNBUSDT',
          type: 'price',
          condition: 'below',
          value: 300,
          triggeredAt: null,
          status: 'active'
        },
        {
          id: 'alert-4',
          symbol: 'ADAUSDT',
          type: 'indicator',
          condition: 'EMA crossover',
          value: null,
          triggeredAt: '2023-04-16T22:45:10Z',
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
        const dashboardData = {
          ...response.data,
          // Map the CSV data properly to our components
          portfolio: response.data.portfolio || {
            // Directly pass portfolio_performance to be processed by the updated PortfolioValue component
            portfolio_performance: response.data.portfolio_performance || []
          },
          performance: response.data.portfolio_performance || {
            history: (response.data.portfolio_performance || []).map(day => ({
              date: day.date || new Date().toISOString().split('T')[0],
              value: parseFloat(day.portfolio_value) || 0
            })) || []
          },
          // Map active trades properly
          activeTrades: (response.data.active_trades || []).map(trade => ({
            id: trade.symbol + '-' + (trade.entry_date || '').replace(/\s+/g, '-'),
            symbol: trade.symbol || 'UNKNOWN',
            side: (trade.position_type || '').toUpperCase() === 'SHORT' ? 'SELL' : 'BUY',
            entryPrice: parseFloat(trade.entry_price) || 0,
            currentPrice: parseFloat(trade.current_price) || 0,
            quantity: parseFloat(trade.quantity) || 0,
            pnl: parseFloat(trade.pnl) || 0,
            pnlPercent: parseFloat(trade.pnl_percent) || 0,
            openTime: trade.entry_date || new Date().toISOString()
          })) || [],
          // Map market overview properly
          marketOverview: {
            topGainers: ((response.data.market_overview?.market_data || [])
              .filter(item => parseFloat(item.daily_change_percent) > 0)
              .sort((a, b) => parseFloat(b.daily_change_percent) - parseFloat(a.daily_change_percent))
              .slice(0, 3)
              .map(item => ({
                symbol: item.symbol || 'Unknown',
                price: parseFloat(item.price) || 0,
                change: parseFloat(item.daily_change_percent) || 0
              }))) || [],
            topLosers: ((response.data.market_overview?.market_data || [])
              .filter(item => parseFloat(item.daily_change_percent) < 0)
              .sort((a, b) => parseFloat(a.daily_change_percent) - parseFloat(b.daily_change_percent))
              .slice(0, 3)
              .map(item => ({
                symbol: item.symbol || 'Unknown',
                price: parseFloat(item.price) || 0,
                change: parseFloat(item.daily_change_percent) || 0
              }))) || [],
            btcDominance: 48.5, // Static for now
            globalMarketCap: 2.34, // Static for now
            fear_greed_index: 65 // Static for now
          },
          // Map bot status (static for now)
          botStatus: Array.isArray(response.data.bot_status)
            ? response.data.bot_status
            : [
                {
                  id: 'bot-1',
                  name: 'EMA Crossover Bot',
                  status: 'active',
                  lastTrade: new Date().toISOString(),
                  pnl24h: 1.2,
                  activeStrategies: 1
                },
                {
                  id: 'bot-2',
                  name: 'RSI Strategy Bot',
                  status: 'paused',
                  lastTrade: new Date(Date.now() - 86400000).toISOString(),
                  pnl24h: 0,
                  activeStrategies: 0
                }
              ],
          // Map recent alerts from trading history
          recentAlerts: Array.isArray(response.data.trading_history) 
            ? response.data.trading_history.slice(0, 4).map(trade => ({
                id: 'alert-' + (trade.trade_id || Math.random().toString(36).substring(2, 9)),
                symbol: trade.symbol || 'UNKNOWN',
                type: parseFloat(trade.pnl || 0) > 0 ? 'success' : 'warning',
                message: `${trade.position_type || 'Unknown'} position closed with ${parseFloat(trade.pnl || 0) > 0 ? 'profit' : 'loss'} of $${Math.abs(parseFloat(trade.pnl || 0)).toFixed(2)}`,
                timestamp: trade.exit_date || new Date().toISOString(),
                priority: parseFloat(trade.pnl || 0) > 0 ? 'medium' : 'high'
              })) 
            : (Array.isArray(response.data.alerts) 
                ? response.data.alerts
                : []
              ),
        };
        
        setDashboardData(dashboardData);
        retryCount.current = 0;
        return true;
      } else {
        throw new Error('Invalid response format from API');
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error.message);
      console.error('API Error details:', error.response?.data || 'No response data');
      
      // Check if we should retry or use mock data
      if (retryCount.current < maxRetries) {
        retryCount.current++;
        setError(`Connection attempt ${retryCount.current}/${maxRetries} failed. Retrying...`);
        
        // Try to integrate data from other parts of the app
        await integrateExistingData();
        
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

  // Function to try to integrate data from other parts of the app
  const integrateExistingData = useCallback(async () => {
    try {
      // Try to fetch data from different endpoints that might be working
      const endpoints = [
        { url: '/api/market-data', dataKey: 'marketData' },
        { url: '/api/user-portfolio', dataKey: 'portfolio' },
        { url: '/api/active-trades', dataKey: 'trades' },
        { url: '/api/alerts', dataKey: 'alerts' }
      ];
      
      let integratedData = {};
      
      // Try each endpoint
      for (const endpoint of endpoints) {
        try {
          const response = await axios.get(endpoint.url);
          if (response.data && response.data.success) {
            console.log(`Successfully fetched data from ${endpoint.url}`);
            integratedData[endpoint.dataKey] = response.data;
          }
        } catch (endpointError) {
          console.log(`Could not fetch data from ${endpoint.url}:`, endpointError.message);
        }
      }
      
      // If we got any data, try to use it
      if (Object.keys(integratedData).length > 0) {
        console.log('Using integrated data from multiple endpoints:', integratedData);
        
        // Create a hybrid dataset using parts we could fetch and fill the rest with mock data
        const mockData = generateMockData();
        const hybridData = {
          ...mockData,
          ...(integratedData.portfolio && { portfolio: integratedData.portfolio }),
          ...(integratedData.marketData && { marketOverview: integratedData.marketData }),
          ...(integratedData.trades && { activeTrades: integratedData.trades }),
          ...(integratedData.alerts && { recentAlerts: integratedData.alerts })
        };
        
        setDashboardData(hybridData);
        setError('Partial data available. Some sections may display sample data.');
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error integrating existing data:', error.message);
      return false;
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
                    arcLinkLabelsSkipAngle={10}
                    arcLinkLabelsTextColor={theme.palette.text.primary}
                    arcLinkLabelsThickness={2}
                    arcLinkLabelsColor={{ from: 'color' }}
                    arcLabelsSkipAngle={10}
                    arcLabelsTextColor={{ from: 'color', modifiers: [['darker', 2]] }}
                    defs={[
                      {
                        id: 'dots',
                        type: 'patternDots',
                        background: 'inherit',
                        color: theme.palette.background.default,
                        size: 4,
                        padding: 1,
                        stagger: true
                      }
                    ]}
                    fill={[
                      { match: { id: 'Win Rate' }, id: 'dots' }
                    ]}
                    theme={{
                      tooltip: {
                        container: {
                          background: theme.palette.background.paper,
                          color: theme.palette.text.primary,
                          fontSize: 12,
                          borderRadius: 4,
                          boxShadow: '0 4px 10px rgba(0, 0, 0, 0.5)',
                        },
                      },
                    }}
            enableResponsive={false}
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
    <PageLayout scrollIndicator={true}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
      )}
      
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h1">
          Dashboard
        </Typography>
          <Button
            startIcon={<Refresh />} 
            onClick={handleRefresh}
            variant="outlined"
            size="small"
          >
            Refresh
          </Button>
        </Box>

      {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
        </Box>
        ) : (
          <Grid container spacing={3}>
            {/* Portfolio value overview */}
          <Grid item xs={12} lg={8}>
              <ContentCard title="Portfolio Overview">
                <PortfolioValue portfolioData={dashboardData?.portfolio || {}} />
            </ContentCard>
          </Grid>

            {/* Performance summary */}
          <Grid item xs={12} lg={4}>
              <ContentCard title="Performance">
                <PerformanceChart 
                  data={dashboardData?.performance?.history || []} 
                  height={220}
                />
              </ContentCard>
            </Grid>
            
            {/* Market Overview */}
            <Grid item xs={12} lg={8}>
              <ContentCard title="Market Overview">
                <MarketOverview />
            </ContentCard>
          </Grid>

            {/* Bot Status */}
            <Grid item xs={12} lg={4}>
              <ContentCard title="Trading Bots">
                <ScrollableContent 
                  maxHeight="300px"
                  sx={{ minHeight: '250px' }}
                >
                  {dashboardData?.botStatus?.map(bot => (
                    <Box key={bot.id} sx={{ mb: 2 }}>
                      <TradingBotStatus botData={bot} />
                    </Box>
                  ))}
                </ScrollableContent>
            </ContentCard>
            </Grid>

            {/* Active trades */}
          <Grid item xs={12} md={6}>
            <ContentCard 
                title="Active Positions"
              action={
                  <Button size="small" startIcon={<Add />}>
                    New
                </Button>
              }
            >
                <ScrollableContent 
                  maxHeight="400px"
                  sx={{ minHeight: '300px' }}
                >
                  <ActiveTrades trades={dashboardData?.activeTrades || []} />
                </ScrollableContent>
            </ContentCard>
          </Grid>

            {/* Recent alerts */}
          <Grid item xs={12} md={6}>
              <ContentCard title="Recent Alerts">
                <ScrollableContent 
                  maxHeight="400px"
                  sx={{ minHeight: '300px' }}
                >
                  <RecentAlerts alerts={dashboardData?.recentAlerts || []} />
                </ScrollableContent>
            </ContentCard>
        </Grid>

            {/* Trading Signals */}
          <Grid item xs={12}>
              <ContentCard title="Trading Signals">
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" color="success.main" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                      <TrendingUp sx={{ mr: 1 }} />
                      Buy Signals
                    </Typography>
                    <ScrollableContent 
                      maxHeight="300px"
                      sx={{ minHeight: '200px' }}
                    >
                      {buySignals.length > 0 ? (
                        buySignals.map((signal, index) => (
                          <TradingSignalItem key={index} signal={signal} type="buy" />
                        ))
                      ) : (
                        <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                          No buy signals available
                        </Typography>
                      )}
                    </ScrollableContent>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" color="error.main" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                      <TrendingDown sx={{ mr: 1 }} />
                      Short Signals
                    </Typography>
                    <ScrollableContent 
                      maxHeight="300px"
                      sx={{ minHeight: '200px' }}
                    >
                      {shortSignals.length > 0 ? (
                        shortSignals.map((signal, index) => (
                          <TradingSignalItem key={index} signal={signal} type="short" />
                        ))
                      ) : (
                        <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                          No short signals available
                        </Typography>
                      )}
                    </ScrollableContent>
                  </Grid>
                </Grid>
            </ContentCard>
      </Grid>
          </Grid>
        )}
    </Box>
    </PageLayout>
  );
};

export default Dashboard; 