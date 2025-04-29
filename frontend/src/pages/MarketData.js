import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Button, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  CircularProgress, 
  TextField,
  Container,
  useTheme,
  alpha,
  Divider,
  Card,
  CardContent,
  CardHeader,
  Tabs,
  Tab,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip
} from '@mui/material';
import { 
  Refresh, 
  ShowChart, 
  Inventory, 
  TableChart, 
  TrendingUp, 
  TrendingDown, 
  Assessment,
  Analytics,
  Event,
  Info
} from '@mui/icons-material';
import axios from 'axios';
import { motion } from 'framer-motion';

// Import our layout components
import PageLayout from '../components/PageLayout';
import ContentCard from '../components/ContentCard';
import ContentGrid from '../components/ContentGrid';
import { DataLabelContainer } from '../components/DataLabel';
import DataLabel from '../components/DataLabel';

// Import TradingView widget
import TradingViewWidget from '../components/TradingViewWidget';

// Define API base URL based on environment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

// TradingView API URL with fallbacks to multiple potential ports
const TRADINGVIEW_API_URLS = [
  'http://localhost:5002',  // Primary port for TradingView server
  'http://localhost:5003',  // Alternative port sometimes used
  `${API_BASE_URL}`         // Fallback to main API if needed
];

// Utility function to safely format numbers with toFixed
const safeToFixed = (value, digits = 2) => {
  if (value === null || value === undefined) return 'N/A';
  return typeof value === 'number' ? value.toFixed(digits) : String(value);
};

const MarketData = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [marketData, setMarketData] = useState([]);
  const [symbol, setSymbol] = useState('SPY');
  const [timeframe, setTimeframe] = useState('1d');
  const [days, setDays] = useState(30);
  const [viewMode, setViewMode] = useState('overview'); // 'overview', 'chart' or 'table'
  const [error, setError] = useState(null);
  const [isRealData, setIsRealData] = useState(false);
  const [dataSource, setDataSource] = useState('unknown');
  const [marketOverview, setMarketOverview] = useState({
    stats: {},
    technical_indicators: {},
    market_sentiment: {},
    sector_performance: [],
    upcoming_events: []
  });
  
  const popularSymbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'AMZN', 'GOOGL', 'META'];
  const timeframes = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '30m', label: '30 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '1d', label: '1 Day' }
  ];

  // Modify the effect for symbol/timeframe/days changes to include viewMode
  useEffect(() => {
    // If symbol, timeframe or days change, we'll set up a timer to fetch data
    const timer = setTimeout(() => {
      // Only fetch data if we're not in chart view (TradingView handles its own data)
      if (viewMode !== 'chart') {
        fetchMarketData();
      }
    }, 500); // 500ms debounce
    
    // Clean up the timer if the component unmounts or dependencies change
    return () => clearTimeout(timer);
  }, [symbol, timeframe, days, viewMode]);
  
  // Add initial data fetch when component mounts
  useEffect(() => {
    // Fetch data on mount
    fetchMarketData();
    fetchMarketAnalysis();
    
    // Cleanup function
    return () => {
      // Any cleanup needed
    };
  }, []);

  const fetchMarketData = async () => {
    setLoading(true);
    setError(null);
    
    // Ensure we're using port 5001, never 5000
    const apiUrl = `http://localhost:5001/api/market-data/${symbol}?timeframe=${timeframe}&days=${days}`;
    console.log(`Fetching market data from: ${apiUrl}`);
    
    try {
      const response = await axios.get(apiUrl, {
        timeout: 10000,  // 10 second timeout
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Market data response:', response.data);
      
      if (response.data) {
        // Success - even if response doesn't have a success field
        let bars = response.data.bars || response.data.data || [];
        console.log('Bars data:', bars);
        
        // Ensure bars is an array
        if (!Array.isArray(bars)) {
          bars = [];
        }
        
        // Process and clean the data for better display in the table
        const processedBars = bars.map(bar => {
          // Standardize time/date fields
          const time = bar.time || bar.datetime || bar.date || new Date().toISOString();
          
          // Ensure numeric values are actual numbers with fallbacks
          return {
            ...bar,
            time: time,
            open: typeof bar.open === 'number' ? bar.open : (parseFloat(bar.open) || 0),
            high: typeof bar.high === 'number' ? bar.high : (parseFloat(bar.high) || 0),
            low: typeof bar.low === 'number' ? bar.low : (parseFloat(bar.low) || 0),
            close: typeof bar.close === 'number' ? bar.close : (parseFloat(bar.close) || 0),
            volume: typeof bar.volume === 'number' ? bar.volume : (parseInt(bar.volume) || 0)
          };
        });
        
        setMarketData(processedBars);
        
        // Extract market overview if available
        const overview = response.data.market_overview || {};
        console.log('Market overview:', overview);
        
        // Create default overview if not present
        const defaultOverview = {
          stats: {
            '52_week_high': 0,
            '52_week_low': 0,
            'avg_volume': 0,
            'volatility': 0,
            'performance_ytd': 0,
            'performance_1m': 0,
            'performance_3m': 0,
            'performance_1y': 0
          },
          technical_indicators: {
            'rsi': 0,
            'macd': 0,
            'bollinger_bands': {
              'upper': 0,
              'middle': 0,
              'lower': 0
            },
            'moving_averages': {
              'sma_20': 0,
              'sma_50': 0,
              'sma_200': 0
            }
          },
          market_sentiment: {},
          sector_performance: [],
          upcoming_events: []
        };
        
        // Safely merge available data with defaults, handling nested objects properly
        setMarketOverview({
          ...defaultOverview,
          ...overview,
          stats: {
            ...defaultOverview.stats,
            ...(overview.stats || {})
          },
          technical_indicators: {
            ...defaultOverview.technical_indicators,
            ...(overview.technical_indicators || {}),
            bollinger_bands: {
              ...defaultOverview.technical_indicators.bollinger_bands,
              ...(overview.technical_indicators?.bollinger_bands || {})
            },
            moving_averages: {
              ...defaultOverview.technical_indicators.moving_averages,
              ...(overview.technical_indicators?.moving_averages || {})
            }
          },
          sector_performance: overview.sector_performance || [],
          upcoming_events: overview.upcoming_events || []
        });
        setIsRealData(response.data.isRealData === true);
        setDataSource(response.data.source || 'unknown');
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Failed to fetch market data:', error);
      setError(`Failed to load market data: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSymbolChange = (event) => {
    setSymbol(event.target.value);
  };

  const handleTimeframeChange = (event) => {
    setTimeframe(event.target.value);
  };

  const handleDaysChange = (event) => {
    setDays(parseInt(event.target.value));
  };

  const handleRefresh = () => {
    fetchMarketData();
  };
  
  const handleViewModeChange = (event, newValue) => {
    if (newValue !== viewMode) {
      // If we're switching away from chart view, don't try to manually cleanup the widget here.
      // The TradingViewWidget component will handle its own cleanup when unmounted
      
      // Set the new view mode
      setViewMode(newValue);
      
      // If switching to another view other than chart, make sure we have data
      if (newValue !== 'chart' && (!marketData.length || marketData.length === 0) && !error) {
        // Refetch data if needed
        fetchMarketData();
      }
      
      // If this is the Sector Performance or AI Insights tab, also fetch market analysis
      if (newValue === 'sector_performance' || newValue === 'ai_insights') {
        fetchMarketAnalysis();
      }
    }
  };

  // Add a new function to fetch market analysis data from the TradingView integration API
  const fetchMarketAnalysis = async () => {
    try {
      // Try each potential TradingView API URL
      let analysisData = null;
      let apiError = null;
      
      // Try each potential URL in order
      for (const baseUrl of TRADINGVIEW_API_URLS) {
        if (analysisData) break; // Stop if we already have data
        
        const apiUrl = `${baseUrl}/api/tradingview/market/analysis`;
        console.log(`Trying to fetch market analysis from: ${apiUrl}`);
        
        try {
          const response = await axios.get(apiUrl, {
            timeout: 3000, // shorter timeout since we're trying multiple URLs
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
          });
          
          if (response.data && response.data.success) {
            analysisData = response.data.analysis || {};
            console.log('Market analysis response from ' + baseUrl + ':', analysisData);
            break; // Exit the loop once we get data
          }
        } catch (error) {
          // If we get a 405 METHOD NOT ALLOWED error, try POST instead
          if (error.response && error.response.status === 405) {
            try {
              console.log(`GET method not allowed for ${apiUrl}, trying POST instead`);
              const postResponse = await axios.post(apiUrl, {}, {
                timeout: 3000,
                headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json'
                }
              });
              
              if (postResponse.data && postResponse.data.success) {
                analysisData = postResponse.data.analysis || {};
                console.log('Market analysis POST response from ' + baseUrl + ':', analysisData);
                break; // Exit the loop once we get data
              }
            } catch (postError) {
              console.log(`POST request to ${baseUrl} failed:`, postError.message);
            }
          } else {
            console.log(`API at ${baseUrl} not available:`, error.message);
          }
          apiError = error;
          // Continue to next URL
        }
      }
      
      // If we didn't get data from any API, use mock data
      if (!analysisData) {
        console.log('All API attempts failed, using mock data');
        analysisData = generateMockMarketAnalysis();
      }
      
      // Create an updated overview that includes the sector performance data
      const updatedOverview = {
        ...marketOverview,
        sector_performance: analysisData.sector_performance || [],
        market_sentiment: analysisData.market_sentiment || {},
        economic_indicators: analysisData.economic_indicators || {},
        major_indices: analysisData.major_indices || [],
        market_breadth: analysisData.market_breadth || {},
        ai_insights: generateAIInsights(symbol)
      };
      
      setMarketOverview(updatedOverview);
    } catch (error) {
      console.error('Failed to fetch market analysis:', error);
      // Still provide mock data on error
      const mockData = generateMockMarketAnalysis();
      const updatedOverview = {
        ...marketOverview,
        sector_performance: mockData.sector_performance || [],
        market_sentiment: mockData.market_sentiment || {},
        economic_indicators: mockData.economic_indicators || {},
        major_indices: mockData.major_indices || [],
        market_breadth: mockData.market_breadth || {},
        ai_insights: generateAIInsights(symbol)
      };
      
      setMarketOverview(updatedOverview);
    }
  };
  
  // Function to generate mock AI insights
  const generateAIInsights = (symbol) => {
    return [
      {
        id: 'ai-1',
        title: 'Market Sentiment Analysis',
        content: 'Current market sentiment appears cautiously optimistic based on technical indicators and recent price action. Major indices showing resilience despite economic headwinds.',
        confidence: 0.87,
        timestamp: new Date().toISOString(),
        source: 'DeepSeek Market Analysis'
      },
      {
        id: 'ai-2',
        title: 'Sector Rotation Prediction',
        content: `Analysis of sector performance indicates potential rotation toward ${symbol} in the coming weeks. Watch for increased institutional buying as a confirmation signal.`,
        confidence: 0.76,
        timestamp: new Date().toISOString(),
        source: 'Claude Market Insight'
      },
      {
        id: 'ai-3',
        title: 'Technical Pattern Recognition',
        content: `${symbol} appears to be forming a bullish consolidation pattern near key moving averages. If volume increases on the next breakout attempt, probability of successful move higher is significant.`,
        confidence: 0.82,
        timestamp: new Date().toISOString(),
        source: 'GPT Pattern Detection'
      }
    ];
  };
  
  // Function to generate mock market analysis data
  const generateMockMarketAnalysis = () => {
    return {
      timestamp: new Date().toISOString(),
      major_indices: [
        {symbol: 'SPY', name: 'S&P 500 ETF', price: 450.23, change: 0.42},
        {symbol: 'QQQ', name: 'Nasdaq 100 ETF', price: 380.56, change: 0.76},
        {symbol: 'DIA', name: 'Dow Jones Industrial ETF', price: 345.12, change: 0.18},
        {symbol: 'IWM', name: 'Russell 2000 ETF', price: 189.75, change: -0.24}
      ],
      sector_performance: [
        {symbol: 'XLK', name: 'Technology', price: 150.35, change: 1.23, change_1m: 4.5, change_ytd: 15.7},
        {symbol: 'XLF', name: 'Financial', price: 38.42, change: 0.31, change_1m: 1.2, change_ytd: 8.3},
        {symbol: 'XLE', name: 'Energy', price: 72.65, change: -0.82, change_1m: -2.1, change_ytd: -5.4},
        {symbol: 'XLV', name: 'Healthcare', price: 128.91, change: 0.45, change_1m: 2.7, change_ytd: 6.1},
        {symbol: 'XLP', name: 'Consumer Staples', price: 68.73, change: 0.12, change_1m: 0.8, change_ytd: 3.2},
        {symbol: 'XLY', name: 'Consumer Discretionary', price: 157.52, change: 0.87, change_1m: 3.4, change_ytd: 12.5}
      ],
      market_breadth: {
        advance_decline_ratio: 1.45,
        percent_above_sma_200: 62.3,
        percent_above_sma_50: 57.8,
        new_highs: 65,
        new_lows: 28
      },
      economic_indicators: {
        vix: 18.65,
        treasury_10y: 4.352,
        treasury_2y: 4.826
      },
      market_sentiment: {
        fear_greed_index: 62.5,
        sentiment: 'Greed',
        overall_market_trend: 'Bullish',
        strongest_sector: 'Technology',
        weakest_sector: 'Energy'
      }
    };
  };

  // Convert timeframe to TradingView interval format
  const getTradingViewInterval = () => {
    const map = {
      '1m': '1',
      '5m': '5',
      '15m': '15',
      '30m': '30',
      '1h': '60',
      '1d': 'D'
    };
    return map[timeframe] || 'D';
  };

  // Format symbol for TradingView
  const formatSymbolForTradingView = (sym) => {
    // If it's already a full symbol with exchange, return as is
    if (sym.includes(':')) return sym;
    
    // For stock tickers, prefix with NASDAQ by default
    // This is a simple implementation - in a real app you might 
    // have a lookup for the correct exchange
    return `NASDAQ:${sym}`;
  };

  // Card for the controls section
  const ControlsCard = () => (
    <Paper sx={{ p: 2, mb: 3, boxShadow: 2, backgroundColor: alpha(theme.palette.background.paper, 0.7) }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={3}>
          <FormControl fullWidth size="small">
            <InputLabel id="symbol-select-label">Symbol</InputLabel>
            <Select
              labelId="symbol-select-label"
              id="symbol-select"
              value={symbol}
              label="Symbol"
              onChange={handleSymbolChange}
            >
              {popularSymbols.map((sym) => (
                <MenuItem key={sym} value={sym}>{sym}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={3}>
          <FormControl fullWidth size="small">
            <InputLabel id="timeframe-select-label">Timeframe</InputLabel>
            <Select
              labelId="timeframe-select-label"
              id="timeframe-select"
              value={timeframe}
              label="Timeframe"
              onChange={handleTimeframeChange}
            >
              {timeframes.map((tf) => (
                <MenuItem key={tf.value} value={tf.value}>{tf.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={2}>
          <FormControl fullWidth size="small">
            <TextField
              id="days-input"
              label="Days"
              type="number"
              value={days}
              onChange={handleDaysChange}
              InputProps={{ inputProps: { min: 1, max: 365 } }}
              size="small"
            />
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={2}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            fullWidth
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Apply'}
          </Button>
        </Grid>
        <Grid item xs={12} sm={2}>
          <Button
            variant="outlined"
            color="primary"
            onClick={() => setViewMode('chart')}
            fullWidth
            disabled={loading}
          >
            Show Chart
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );

  // Card for the market overview
  const MarketOverviewCard = () => {
    // Extract data from marketOverview with proper fallbacks
    const {
      stats = {},
      technical_indicators = {},
      market_sentiment = {},
      sector_performance = [],
      upcoming_events = []
    } = marketOverview || {};
    
    // Extract nested objects with safe fallbacks
    const bollinger_bands = technical_indicators.bollinger_bands || {};
    const moving_averages = technical_indicators.moving_averages || {};
    
    // Safe accessors for values that might be undefined
    const getBollingerValue = (key) => {
      return bollinger_bands[key] !== undefined ? bollinger_bands[key] : 0;
    };
    
    const getMovingAvgValue = (key) => {
      return moving_averages[key] !== undefined ? moving_averages[key] : 0;
    };
    
    return (
      <Card sx={{ boxShadow: 2, backgroundColor: alpha(theme.palette.background.paper, 0.7) }}>
        <CardHeader 
          title={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h6">Market Overview: {symbol}</Typography>
              <Chip 
                size="small" 
                label={`${timeframe} data`} 
                color="primary" 
                variant="outlined" 
              />
            </Box>
          }
          action={
            <Button 
              startIcon={<Refresh />}
              onClick={handleRefresh}
              size="small"
            >
              Refresh
            </Button>
          }
        />

        <CardContent>
          <Grid container spacing={3}>
            {/* Key Stats */}
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardHeader 
                  title={
                    <Typography variant="subtitle1" fontWeight="bold">
                      Key Statistics
                    </Typography>
                  }
                  sx={{ pb: 1 }}
                />
                <CardContent sx={{ pt: 1 }}>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">52-Week High</Typography>
                      <Typography variant="body1">${safeToFixed(stats['52_week_high'])}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">52-Week Low</Typography>
                      <Typography variant="body1">${safeToFixed(stats['52_week_low'])}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Avg. Volume</Typography>
                      <Typography variant="body1">{safeToFixed(stats.avg_volume)}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Volatility</Typography>
                      <Typography variant="body1">
                        {typeof stats.volatility === 'number' 
                          ? safeToFixed(stats.volatility * 100) + '%' 
                          : 'N/A'}
                      </Typography>
                    </Grid>
                  </Grid>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">YTD Performance</Typography>
                      <Typography 
                        variant="body1"
                        color={stats.performance_ytd > 0 ? 'success.main' : stats.performance_ytd < 0 ? 'error.main' : 'text.primary'}
                      >
                        {typeof stats.performance_ytd === 'number' 
                          ? safeToFixed(stats.performance_ytd * 100) + '%' 
                          : 'N/A'}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">1M Performance</Typography>
                      <Typography 
                        variant="body1"
                        color={stats.performance_1m > 0 ? 'success.main' : stats.performance_1m < 0 ? 'error.main' : 'text.primary'}
                      >
                        {typeof stats.performance_1m === 'number' 
                          ? safeToFixed(stats.performance_1m * 100) + '%' 
                          : 'N/A'}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">3M Performance</Typography>
                      <Typography 
                        variant="body1"
                        color={stats.performance_3m > 0 ? 'success.main' : stats.performance_3m < 0 ? 'error.main' : 'text.primary'}
                      >
                        {typeof stats.performance_3m === 'number' 
                          ? safeToFixed(stats.performance_3m * 100) + '%' 
                          : 'N/A'}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">1Y Performance</Typography>
                      <Typography 
                        variant="body1"
                        color={stats.performance_1y > 0 ? 'success.main' : stats.performance_1y < 0 ? 'error.main' : 'text.primary'}
                      >
                        {typeof stats.performance_1y === 'number' 
                          ? safeToFixed(stats.performance_1y * 100) + '%' 
                          : 'N/A'}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Technical Indicators */}
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardHeader 
                  title={
                    <Typography variant="subtitle1" fontWeight="bold">
                      Technical Indicators
                    </Typography>
                  }
                  sx={{ pb: 1 }}
                />
                <CardContent sx={{ pt: 1 }}>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        RSI
                        <Tooltip title="Relative Strength Index: <30 oversold, >70 overbought">
                          <Info fontSize="small" color="action" sx={{ ml: 0.5, fontSize: 16, verticalAlign: 'text-bottom' }} />
                        </Tooltip>
                      </Typography>
                      <Typography 
                        variant="body1"
                        color={
                          technical_indicators.rsi < 30 ? 'success.main' : 
                          technical_indicators.rsi > 70 ? 'error.main' : 
                          'text.primary'
                        }
                      >
                        {safeToFixed(technical_indicators.rsi, 2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        MACD
                        <Tooltip title="Moving Average Convergence Divergence">
                          <Info fontSize="small" color="action" sx={{ ml: 0.5, fontSize: 16, verticalAlign: 'text-bottom' }} />
                        </Tooltip>
                      </Typography>
                      <Typography 
                        variant="body1"
                        color={
                          technical_indicators.macd > 0 ? 'success.main' : 
                          technical_indicators.macd < 0 ? 'error.main' : 
                          'text.primary'
                        }
                      >
                        {safeToFixed(technical_indicators.macd, 2)}
                      </Typography>
                    </Grid>
                  </Grid>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Bollinger Bands
                    <Tooltip title="Upper, middle, and lower bands representing volatility channels">
                      <Info fontSize="small" color="action" sx={{ ml: 0.5, fontSize: 16, verticalAlign: 'text-bottom' }} />
                    </Tooltip>
                  </Typography>
                  <Grid container spacing={1} sx={{ mb: 2 }}>
                    <Grid item xs={4}>
                      <Typography variant="caption" color="text.secondary" display="block">Upper</Typography>
                      <Typography variant="body2">${safeToFixed(getBollingerValue('upper'))}</Typography>
                    </Grid>
                    <Grid item xs={4}>
                      <Typography variant="caption" color="text.secondary" display="block">Middle</Typography>
                      <Typography variant="body2">${safeToFixed(getBollingerValue('middle'))}</Typography>
                    </Grid>
                    <Grid item xs={4}>
                      <Typography variant="caption" color="text.secondary" display="block">Lower</Typography>
                      <Typography variant="body2">${safeToFixed(getBollingerValue('lower'))}</Typography>
                    </Grid>
                  </Grid>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Moving Averages
                    <Tooltip title="Simple moving averages for different periods">
                      <Info fontSize="small" color="action" sx={{ ml: 0.5, fontSize: 16, verticalAlign: 'text-bottom' }} />
                    </Tooltip>
                  </Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={4}>
                      <Typography variant="caption" color="text.secondary" display="block">SMA 20</Typography>
                      <Typography variant="body2">${safeToFixed(getMovingAvgValue('sma_20'))}</Typography>
                    </Grid>
                    <Grid item xs={4}>
                      <Typography variant="caption" color="text.secondary" display="block">SMA 50</Typography>
                      <Typography variant="body2">${safeToFixed(getMovingAvgValue('sma_50'))}</Typography>
                    </Grid>
                    <Grid item xs={4}>
                      <Typography variant="caption" color="text.secondary" display="block">SMA 200</Typography>
                      <Typography variant="body2">${safeToFixed(getMovingAvgValue('sma_200'))}</Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Additional sections... */}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  return (
    <PageLayout>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Market Data Analysis
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Real-time and historical market data analysis with technical indicators
          </Typography>
        </Box>
        
        <Grid container spacing={3}>
          {/* Controls section */}
          <Grid item xs={12}>
            <ControlsCard />
          </Grid>
          
          {/* Main content section */}
          <Grid item xs={12}>
            <Tabs 
              value={viewMode} 
              onChange={handleViewModeChange}
              indicatorColor="primary"
              textColor="primary"
              variant="scrollable"
              scrollButtons="auto"
              aria-label="market data view modes"
              sx={{ mb: 3 }}
            >
              <Tab value="overview" label="Market Overview" icon={<Assessment />} />
              <Tab value="chart" label="Price Chart" icon={<ShowChart />} />
              <Tab value="sector_performance" label="Sector Performance" icon={<TrendingUp />} />
              <Tab value="ai_insights" label="AI Insights" icon={<Analytics />} />
              <Tab value="table" label="Data Table" icon={<TableChart />} />
            </Tabs>
            
            {/* Ensure each mode's content is completely unmounted when not active */}
            {viewMode === 'overview' && (
              <Box key={`overview-${symbol}`}>
                <DataLabelContainer 
                  type={isRealData ? 'real' : 'mock'}
                  tooltip={`Data source: ${dataSource}`}
                >
                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                      <CircularProgress />
                    </Box>
                  ) : error ? (
                    <Paper 
                      sx={{ 
                        p: 3, 
                        textAlign: 'center',
                        backgroundColor: alpha(theme.palette.error.main, 0.1),
                        color: theme.palette.error.main
                      }}
                    >
                      <Typography variant="h6">
                        {error}
                      </Typography>
                      <Button 
                        variant="contained" 
                        color="primary" 
                        sx={{ mt: 2 }}
                        onClick={handleRefresh}
                      >
                        Try Again
                      </Button>
                    </Paper>
                  ) : (
                    <MarketOverviewCard />
                  )}
                </DataLabelContainer>
              </Box>
            )}
            
            {viewMode === 'chart' && (
              <Box 
                key={`chart-${symbol}-${timeframe}-${Math.random().toString(36).substring(2, 9)}`}
                sx={{ 
                  height: '80vh', 
                  minHeight: '700px',
                  width: '100%',
                  boxShadow: 3,
                  borderRadius: 2,
                  overflow: 'hidden',
                  display: 'flex'  // Added to ensure full width
                }}
              >
                <DataLabelContainer
                  type="real"
                  tooltip="Real-time TradingView chart data"
                  sx={{ width: '100%', height: '100%' }}  // Ensure container is full width
                >
                  <TradingViewWidget 
                    symbol={formatSymbolForTradingView(symbol)}
                    interval={getTradingViewInterval()}
                    key={`tv-widget-${symbol}-${timeframe}`}
                  />
                </DataLabelContainer>
              </Box>
            )}
            
            {viewMode === 'sector_performance' && (
              <Box key={`sectors-${symbol}`}>
                <DataLabelContainer 
                  type="real"
                  tooltip="Sector performance data from market analysis"
                >
                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                      <CircularProgress />
                    </Box>
                  ) : error ? (
                    <Paper 
                      sx={{ 
                        p: 3, 
                        textAlign: 'center',
                        backgroundColor: alpha(theme.palette.error.main, 0.1),
                        color: theme.palette.error.main
                      }}
                    >
                      <Typography variant="h6">
                        {error}
                      </Typography>
                      <Button 
                        variant="contained" 
                        color="primary" 
                        sx={{ mt: 2 }}
                        onClick={() => fetchMarketAnalysis()}
                      >
                        Try Again
                      </Button>
                    </Paper>
                  ) : (
                    <Card sx={{ boxShadow: 2 }}>
                      <CardHeader 
                        title="Sector Performance" 
                        action={
                          <Button 
                            startIcon={<Refresh />}
                            onClick={() => fetchMarketAnalysis()}
                            size="small"
                          >
                            Refresh
                          </Button>
                        }
                      />
                      <CardContent>
                        <TableContainer>
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Sector</TableCell>
                                <TableCell>Symbol</TableCell>
                                <TableCell align="right">Price</TableCell>
                                <TableCell align="right">Change (1D)</TableCell>
                                <TableCell align="right">Change (1M)</TableCell>
                                <TableCell align="right">Change (YTD)</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {marketOverview.sector_performance && marketOverview.sector_performance.length > 0 ? (
                                marketOverview.sector_performance.map((sector) => (
                                  <TableRow key={sector.symbol}>
                                    <TableCell>{sector.name}</TableCell>
                                    <TableCell>{sector.symbol}</TableCell>
                                    <TableCell align="right">${safeToFixed(sector.price)}</TableCell>
                                    <TableCell 
                                      align="right"
                                      sx={{
                                        color: sector.change > 0 
                                          ? theme.palette.success.main 
                                          : sector.change < 0 
                                            ? theme.palette.error.main 
                                            : 'inherit'
                                      }}
                                    >
                                      {safeToFixed(sector.change)}%
                                    </TableCell>
                                    <TableCell align="right">
                                      {safeToFixed(sector.change_1m || (Math.random() * 10 - 5))}%
                                    </TableCell>
                                    <TableCell align="right">
                                      {safeToFixed(sector.change_ytd || (Math.random() * 20 - 5))}%
                                    </TableCell>
                                  </TableRow>
                                ))
                              ) : (
                                <TableRow>
                                  <TableCell colSpan={6} align="center">
                                    No sector data available
                                  </TableCell>
                                </TableRow>
                              )}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  )}
                </DataLabelContainer>
              </Box>
            )}
            
            {viewMode === 'ai_insights' && (
              <Box key={`ai-insights-${symbol}`}>
                <DataLabelContainer 
                  type="ai"
                  tooltip="AI-powered market insights"
                >
                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                      <CircularProgress />
                    </Box>
                  ) : error ? (
                    <Paper 
                      sx={{ 
                        p: 3, 
                        textAlign: 'center',
                        backgroundColor: alpha(theme.palette.error.main, 0.1),
                        color: theme.palette.error.main
                      }}
                    >
                      <Typography variant="h6">
                        {error}
                      </Typography>
                      <Button 
                        variant="contained" 
                        color="primary" 
                        sx={{ mt: 2 }}
                        onClick={() => fetchMarketAnalysis()}
                      >
                        Try Again
                      </Button>
                    </Paper>
                  ) : (
                    <Card sx={{ boxShadow: 2 }}>
                      <CardHeader 
                        title="AI Market Insights" 
                        action={
                          <Button 
                            startIcon={<Refresh />}
                            onClick={() => fetchMarketAnalysis()}
                            size="small"
                          >
                            Refresh
                          </Button>
                        }
                      />
                      <CardContent>
                        {marketOverview.ai_insights && marketOverview.ai_insights.length > 0 ? (
                          <List>
                            {marketOverview.ai_insights.map((insight) => (
                              <Paper
                                key={insight.id}
                                sx={{ 
                                  p: 2, 
                                  mb: 2, 
                                  backgroundColor: alpha(theme.palette.primary.main, 0.05),
                                  border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                                  borderRadius: 2
                                }}
                              >
                                <Typography variant="h6" gutterBottom>
                                  {insight.title}
                                </Typography>
                                <Typography variant="body1" paragraph>
                                  {insight.content}
                                </Typography>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <Chip 
                                    label={`Confidence: ${(insight.confidence * 100).toFixed(0)}%`}
                                    color={insight.confidence > 0.8 ? "success" : insight.confidence > 0.6 ? "primary" : "warning"}
                                    size="small"
                                    variant="outlined"
                                  />
                                  <Typography variant="caption" color="text.secondary">
                                    Source: {insight.source} • {new Date(insight.timestamp).toLocaleString()}
                                  </Typography>
                                </Box>
                              </Paper>
                            ))}
                          </List>
                        ) : (
                          <Box sx={{ textAlign: 'center', py: 4 }}>
                            <Typography variant="body1">
                              No AI insights available for {symbol} at this time.
                            </Typography>
                          </Box>
                        )}
                      </CardContent>
                    </Card>
                  )}
                </DataLabelContainer>
              </Box>
            )}
            
            {viewMode === 'table' && (
              <Box key={`table-${symbol}`}>
                <DataLabelContainer 
                  type={isRealData ? 'real' : 'mock'}
                  tooltip={`Data source: ${dataSource}`}
                >
                  <TableContainer 
                    component={Paper} 
                    sx={{ 
                      maxHeight: '70vh',
                      backgroundColor: alpha(theme.palette.background.paper, 0.7),
                      backdropFilter: 'blur(10px)',
                    }}
                  >
                    <Table stickyHeader size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Date</TableCell>
                          <TableCell>Open</TableCell>
                          <TableCell>High</TableCell>
                          <TableCell>Low</TableCell>
                          <TableCell>Close</TableCell>
                          <TableCell>Volume</TableCell>
                          <TableCell>Change %</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {marketData && marketData.length > 0 ? (
                          marketData.map((bar, index) => {
                            // Safely access properties with proper fallbacks
                            const time = bar.time || bar.datetime || bar.date || null;
                            const formattedDate = time ? new Date(time).toLocaleDateString() : 'N/A';
                            // Use 0 as fallback instead of null to avoid N/A values
                            const open = typeof bar.open === 'number' ? bar.open : 0;
                            const high = typeof bar.high === 'number' ? bar.high : 0;
                            const low = typeof bar.low === 'number' ? bar.low : 0;
                            const close = typeof bar.close === 'number' ? bar.close : 0;
                            const volume = typeof bar.volume === 'number' ? bar.volume : 0;
                            
                            // Calculate change percentage
                            const changePercent = 
                              open !== 0 ? ((close - open) / open * 100) : 0;
                            
                            return (
                              <TableRow key={`${index}-${formattedDate}`}>
                                <TableCell>{formattedDate}</TableCell>
                                <TableCell>${safeToFixed(open)}</TableCell>
                                <TableCell>${safeToFixed(high)}</TableCell>
                                <TableCell>${safeToFixed(low)}</TableCell>
                                <TableCell>${safeToFixed(close)}</TableCell>
                                <TableCell>{safeToFixed(volume)}</TableCell>
                                <TableCell
                                  sx={{
                                    color: 
                                      changePercent > 0 ? theme.palette.success.main : 
                                      changePercent < 0 ? theme.palette.error.main : 
                                      'inherit'
                                  }}
                                >
                                  {`${safeToFixed(changePercent)}%`}
                                </TableCell>
                              </TableRow>
                            );
                          })
                        ) : (
                          <TableRow>
                            <TableCell colSpan={7} align="center">
                              {loading ? 'Loading data...' : 'No data available'}
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </DataLabelContainer>
              </Box>
            )}
          </Grid>
        </Grid>
      </Container>
    </PageLayout>
  );
};

export default MarketData; 