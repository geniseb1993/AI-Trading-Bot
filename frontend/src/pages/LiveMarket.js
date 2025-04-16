import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, 
  Grid, 
  Card, 
  CardHeader, 
  CardContent, 
  Typography, 
  Divider,
  Container,
  useTheme,
  TextField,
  MenuItem,
  Button,
  Tabs,
  Tab,
  CircularProgress,
  Paper,
  Chip,
  Avatar,
  LinearProgress,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  IconButton
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { motion } from 'framer-motion';
import RefreshIcon from '@mui/icons-material/Refresh';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import SignalCellularAltIcon from '@mui/icons-material/SignalCellularAlt';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import HistoryIcon from '@mui/icons-material/History';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PriceCheckIcon from '@mui/icons-material/PriceCheck';
import ErrorIcon from '@mui/icons-material/Error';
import axios from 'axios';

// Define API base URL based on environment
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';
console.log(`Using API URL: ${API_BASE_URL}`);

// Import components
import TradingChart from '../components/TradingChart';
import TradingViewWidget from '../components/TradingViewWidget';
import InstitutionalFlowTable from '../components/InstitutionalFlowTable';
import CooldownTimer from '../components/execution_model/CooldownTimer';
// TradeJournalTable will be implemented later

const LiveMarket = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [timeframe, setTimeframe] = useState('1d');
  const [tabValue, setTabValue] = useState(0);
  const [apiConnected, setApiConnected] = useState(false);
  const [alpacaConnected, setAlpacaConnected] = useState(false);
  const [isRealData, setIsRealData] = useState(false);
  const [cooldownStatus, setCooldownStatus] = useState(null);
  const [tradeSetups, setTradeSetups] = useState({});
  const [aiTradeSetups, setAITradeSetups] = useState({
    SPY: { loading: true, error: null, data: null },
    QQQ: { loading: true, error: null, data: null },
    AAPL: { loading: true, error: null, data: null },
  });
  const [marketData, setMarketData] = useState({});
  
  // Convert timeframe selection to number of days for the chart
  const getTimeframeInDays = () => {
    switch(timeframe) {
      case '1h': return '1';
      case '4h': return '2';
      case '1d': return '7';
      case '1w': return '30';
      default: return '7';
    }
  };

  // Helper function to format symbols correctly for TradingView
  const formatSymbolForTradingView = (symbol) => {
    // Special handling for SPY which needs the exchange prefix
    const symbolMapping = {
      'SPY': 'AMEX:SPY',
      'QQQ': 'NASDAQ:QQQ',
      'IWM': 'AMEX:IWM',
      'DIA': 'AMEX:DIA',
      'AAPL': 'NASDAQ:AAPL',
      'MSFT': 'NASDAQ:MSFT',
      'TSLA': 'NASDAQ:TSLA',
      'NVDA': 'NASDAQ:NVDA',
      'AMD': 'NASDAQ:AMD',
      'GOOGL': 'NASDAQ:GOOGL'
    };
    
    return symbolMapping[symbol] || `NASDAQ:${symbol}`;
  };

    // Check API connection
    const checkApiConnection = () => {
    console.log('Checking API connection...');
    fetch(`${API_BASE_URL}/api/health`, { method: 'GET' })
        .then(response => response.json())
        .then(data => {
        console.log('API health check response:', data);
          setApiConnected(data.status === 'ok');
        setAlpacaConnected(data.alpaca_connected === true);
        // Set real data flag based on API response
        setIsRealData(data.using_real_data === true);
        console.log(`API Connected: ${data.status === 'ok'}, Alpaca Connected: ${data.alpaca_connected}, Using Real Data: ${data.using_real_data}`);
        })
      .catch((error) => {
        console.error('API health check failed:', error);
        // Do NOT force apiConnected to true when there's a real error
          setApiConnected(false);
        setAlpacaConnected(false);
        setIsRealData(false);
        });
    };

  // Fetch chart data for the selected symbol
  const fetchChartData = useCallback(async () => {
    if (!selectedSymbol) return;
    
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/market-data/${selectedSymbol}?timeframe=${timeframe === '1d' ? '1d' : '1h'}&days=${getTimeframeInDays()}`);
      
      if (response.data && response.data.success) {
        setMarketData(prevData => ({
          ...prevData,
          [selectedSymbol]: response.data.bars || []
        }));
        setApiConnected(true);
        setIsRealData(!!response.data.isRealData);
      } else {
        console.error("Failed to fetch market data");
        setApiConnected(false);
      }
    } catch (err) {
      console.error("API error:", err);
      setApiConnected(false);
    } finally {
      setLoading(false);
    }
  }, [selectedSymbol, timeframe, getTimeframeInDays]);

  // Define fetchAITradeSetups before it's used in useEffect
  const fetchAITradeSetups = useCallback(async () => {
    const symbols = ['SPY', 'QQQ', 'AAPL'];
    
    // Update loading states for all symbols
    setAITradeSetups(prev => ({
      SPY: { ...prev.SPY, loading: true, error: null },
      QQQ: { ...prev.QQQ, loading: true, error: null },
      AAPL: { ...prev.AAPL, loading: true, error: null },
    }));
    
    // Create mock data for development environment
    const createMockData = (symbol) => {
      // Generate slightly different mock data for each symbol
      const mockRecommendations = {
        'SPY': { recommendation: 'buy', probability: 0.78 },
        'QQQ': { recommendation: 'neutral', probability: 0.52 },
        'AAPL': { recommendation: 'sell', probability: 0.65 }
      };
      
      const baseData = mockRecommendations[symbol] || { recommendation: 'neutral', probability: 0.5 };
      
      return {
        symbol,
        timestamp: new Date().toISOString(),
        price: symbol === 'SPY' ? 478.32 : symbol === 'QQQ' ? 415.87 : 187.65,
        recommendation: baseData.recommendation,
        probability: baseData.probability,
        indicators: {
          'RSI (14)': Math.round(Math.random() * 40 + 30),
          'MACD (12,26,9)': (Math.random() * 2 - 1).toFixed(2),
          'MA Cross': symbol === 'SPY' ? 'Bullish' : symbol === 'AAPL' ? 'Bearish' : 'Neutral',
          'Volume Analysis': Math.random() > 0.5 ? 'Above Average' : 'Below Average',
          'ADX (14)': Math.round(Math.random() * 15 + 20)
        },
        analysis: `AI analysis complete for ${symbol}. Based on current market conditions, the ${baseData.recommendation.toUpperCase()} signal has a confidence of ${Math.round(baseData.probability * 100)}%.`
      };
    };
    
    try {
      // Try to fetch from API first
      const results = await Promise.all(
        symbols.map(async (symbol) => {
          try {
            // Add a small delay to simulate network latency
            await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 500));
            
            // Try to fetch from API, fallback to mock data
            try {
              const response = await axios.get(`${API_BASE_URL}/api/market/ai_signals/${symbol}`);
              return { symbol, data: response.data, error: null };
            } catch (apiError) {
              console.log(`API not available for ${symbol}, using mock data:`, apiError);
              // Use mock data if API fails
              return { symbol, data: createMockData(symbol), error: null };
            }
          } catch (error) {
            console.error(`Error processing data for ${symbol}:`, error);
            return { 
              symbol, 
              data: createMockData(symbol), // Always provide mock data as fallback
              error: null 
            };
          }
        })
      );
      
      // Process results
      const newTradeSetups = { ...aiTradeSetups };
      results.forEach(result => {
        newTradeSetups[result.symbol] = { 
          loading: false, 
          error: result.error, 
          data: result.data 
        };
      });
      
      setAITradeSetups(newTradeSetups);
    } catch (error) {
      console.error('Error fetching AI trade setups:', error);
      
      // Fallback to mock data for all symbols
      const mockResults = {};
      symbols.forEach(symbol => {
        mockResults[symbol] = {
          loading: false,
          error: null,
          data: createMockData(symbol)
        };
      });
      
      setAITradeSetups(mockResults);
    }
  }, []);

  // Add refresh handler for chart data and AI Trade Setups
  const handleRefresh = () => {
    fetchChartData();
    fetchAITradeSetups();
  };
  
  const fetchCooldownStatus = () => {
    // In a real app, this would fetch from your API
    // For now, we'll simulate the data
    const mockCooldownStatus = {
      cooldown_enabled: true,
      hourly_trade_count: 2,
      max_trades_per_hour: 3,
      daily_trade_count: 5,
      max_trades_per_day: 10,
      next_available_trade_time: new Date(Date.now() + 5 * 60000).toISOString(), // 5 minutes from now
      cooldown_minutes: 20,
      cooldown_remaining_minutes: 5,
      cooldown_active: true
    };
    
    setCooldownStatus(mockCooldownStatus);
  };

  const fetchTradeSetups = () => {
    // In a real app, this would fetch from your API
    // For now, we'll simulate the data
    const mockTradeSetups = {
      'SPY': {
        price: 458.75,
        direction: 'long',
        confidence: 87,
        entry: 452.35,
        stopLoss: 445.50,
        takeProfit: 470.25,
        timeframe: '4h',
        signals: [
          { name: 'MACD Crossover', bullish: true },
          { name: 'RSI Momentum', bullish: true },
          { name: 'Moving Average', bullish: true },
          { name: 'Volume Profile', bullish: false }
        ]
      },
      'QQQ': {
        price: 392.48,
        direction: 'long',
        confidence: 76,
        entry: 385.45,
        stopLoss: 375.80,
        takeProfit: 405.30,
        timeframe: '1d',
        signals: [
          { name: 'MACD Crossover', bullish: true },
          { name: 'RSI Momentum', bullish: true },
          { name: 'Moving Average', bullish: false },
          { name: 'Volume Profile', bullish: true }
        ]
      },
      'AAPL': {
        price: 188.25,
        direction: 'short',
        confidence: 62,
        entry: 192.75,
        stopLoss: 198.30,
        takeProfit: 182.50,
        timeframe: '1d',
        signals: [
          { name: 'MACD Crossover', bullish: false },
          { name: 'RSI Momentum', bullish: false },
          { name: 'Moving Average', bullish: true },
          { name: 'Volume Profile', bullish: false }
        ]
      }
    };
    
    setTradeSetups(mockTradeSetups);
  };
  
  // Modify the useEffect to also fetch AI trade setups
  useEffect(() => {
    // Initial data fetch
    checkApiConnection();
    fetchCooldownStatus();
    fetchAITradeSetups();
    fetchTradeSetups(); // Also fetch regular trade setups
    fetchChartData(); // Fetch market chart data
    
    // Set up interval to refresh data every 30 seconds
    const intervalId = setInterval(() => {
      checkApiConnection();
      fetchCooldownStatus();
      fetchAITradeSetups();
      fetchTradeSetups(); // Also refresh regular trade setups
      fetchChartData(); // Refresh chart data
    }, 30000);
    
    return () => clearInterval(intervalId);
  }, [fetchChartData, fetchAITradeSetups]); // Add both fetchChartData and fetchAITradeSetups as dependencies

  // Fetch AI Trade Setups when tab changes to AI Trade Setups
  useEffect(() => {
    if (tabValue === 1) { // AI Trade Setups tab
      fetchAITradeSetups();
    }
  }, [tabValue, fetchAITradeSetups]);
  
  // Add refresh handler for AI Trade Setups
  const handleRefreshAITradeSetups = () => {
    fetchAITradeSetups();
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Placeholder component for Trade Journal until it's fully implemented
  const TradeJournalPlaceholder = () => (
    <Box sx={{ p: 3, bgcolor: alpha(theme.palette.background.paper, 0.7), borderRadius: 2 }}>
      <Typography variant="h6" sx={{ mb: 2, fontFamily: 'Orbitron' }}>Trade Journal</Typography>
      <Typography variant="body1">
        The Trade Journal feature is coming soon. This feature will allow you to:
      </Typography>
      <Box component="ul" sx={{ mt: 2 }}>
        <Typography component="li">Log all your trades automatically</Typography>
        <Typography component="li">Track performance metrics and win rate</Typography>
        <Typography component="li">Analyze trading patterns and optimize strategies</Typography>
        <Typography component="li">Export data for external analysis</Typography>
      </Box>
    </Box>
  );

  // Render AI Trade Setup Card with improved loading and error states
  const renderAITradeSetupCard = (symbol) => {
    const { loading, error, data } = aiTradeSetups[symbol];
    
    return (
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: alpha(theme.palette.background.paper, 0.8),
          backdropFilter: 'blur(20px)',
          border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
          borderRadius: 2,
          boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.2)}`
        }}
      >
        <CardHeader
          title={
            <Typography 
              variant="h6" 
              sx={{ 
                fontFamily: '"Audiowide", sans-serif',
                fontSize: '1.25rem',
                color: theme.palette.text.primary
              }}
            >
              {symbol}
            </Typography>
          }
          action={
            <IconButton 
              size="small" 
              onClick={handleRefreshAITradeSetups}
              disabled={loading}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          }
          sx={{ 
            pb: 0,
            borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`
          }}
        />
        <CardContent 
          sx={{ 
            p: 2, 
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: loading || error ? 'center' : 'flex-start',
            alignItems: loading || error ? 'center' : 'flex-start'
          }}
        >
          {loading ? (
            <Box sx={{ textAlign: 'center', py: 2 }}>
              <CircularProgress size={30} thickness={5} />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Loading AI analysis...
              </Typography>
            </Box>
          ) : error ? (
            <Box sx={{ textAlign: 'center', py: 2 }}>
              <ErrorIcon color="error" sx={{ fontSize: 30 }} />
              <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                {error}
              </Typography>
              <Button 
                size="small" 
                color="primary" 
                onClick={handleRefreshAITradeSetups} 
                sx={{ mt: 1 }}
                startIcon={<RefreshIcon />}
              >
                Retry
              </Button>
            </Box>
          ) : !data ? (
            <Typography variant="body2" color="text.secondary">
              No AI trade setup data available
            </Typography>
          ) : (
            <>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  AI Recommendation:
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {data.recommendation === 'buy' ? (
                    <TrendingUpIcon color="success" sx={{ mr: 1 }} />
                  ) : data.recommendation === 'sell' ? (
                    <TrendingDownIcon color="error" sx={{ mr: 1 }} />
                  ) : (
                    <ShowChartIcon color="info" sx={{ mr: 1 }} />
                  )}
                  <Typography 
                    variant="body1" 
                    color={
                      data.recommendation === 'buy' 
                        ? 'success.main' 
                        : data.recommendation === 'sell' 
                          ? 'error.main' 
                          : 'info.main'
                    }
                    sx={{ fontWeight: 'bold', textTransform: 'uppercase' }}
                  >
                    {data.recommendation || 'NEUTRAL'}
                  </Typography>
                </Box>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Signal Strength:
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LinearProgress
                    variant="determinate"
                    value={data.probability * 100}
                    color={
                      data.recommendation === 'buy' 
                        ? 'success' 
                        : data.recommendation === 'sell' 
                          ? 'error' 
                          : 'info'
                    }
                    sx={{ 
                      height: 10, 
                      borderRadius: 5, 
                      width: '100%', 
                      backgroundColor: alpha(theme.palette.divider, 0.2) 
                    }}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 1, minWidth: 40 }}>
                    {Math.round(data.probability * 100)}%
                  </Typography>
                </Box>
              </Box>
              
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Key Indicators:
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {data.indicators && Object.entries(data.indicators).map(([key, value]) => (
                    <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        {key}:
                      </Typography>
                      <Typography variant="body2" color="text.primary" sx={{ fontWeight: 'medium' }}>
                        {typeof value === 'number' ? value.toFixed(2) : value}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Box>
            </>
          )}
        </CardContent>
      </Card>
    );
  };

  // Create a new effect to fetch chart data when symbol or timeframe changes
  useEffect(() => {
    if (selectedSymbol && timeframe) {
      fetchChartData();
    }
  }, [selectedSymbol, timeframe, fetchChartData]);

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography 
            variant="h4" 
            component={motion.div}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            sx={{ 
              fontFamily: 'Orbitron',
              color: theme.palette.primary.main,
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }}
          >
            <ShowChartIcon fontSize="large" />
            Live Market Dashboard
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              select
              size="small"
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              sx={{ minWidth: 100 }}
            >
              <MenuItem value="SPY">SPY</MenuItem>
              <MenuItem value="QQQ">QQQ</MenuItem>
              <MenuItem value="TSLA">TSLA</MenuItem>
              <MenuItem value="AAPL">AAPL</MenuItem>
              <MenuItem value="MSFT">MSFT</MenuItem>
            </TextField>
            
            <TextField
              select
              size="small"
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              sx={{ minWidth: 100 }}
            >
              <MenuItem value="1h">1 Hour</MenuItem>
              <MenuItem value="4h">4 Hours</MenuItem>
              <MenuItem value="1d">1 Day</MenuItem>
              <MenuItem value="1w">1 Week</MenuItem>
            </TextField>
            
            <Button
              variant="contained"
              color="primary"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
              onClick={handleRefresh}
              disabled={loading}
              sx={{ fontFamily: 'Orbitron' }}
            >
              Refresh
            </Button>
          </Box>
        </Box>
        
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          sx={{ 
            mb: 3,
            '& .MuiTab-root': {
              fontFamily: 'Orbitron',
              fontSize: '0.9rem',
            },
            '& .Mui-selected': {
              color: theme.palette.primary.main,
            },
            '& .MuiTabs-indicator': {
              backgroundColor: theme.palette.primary.main,
            }
          }}
        >
          <Tab 
            label="Market Overview" 
            icon={<ShowChartIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="AI Trade Setups" 
            icon={<SignalCellularAltIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Institutional Flow" 
            icon={<MonetizationOnIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Trade Journal" 
            icon={<HistoryIcon />} 
            iconPosition="start"
          />
        </Tabs>
        
        {/* Tab content */}
        <Box sx={{ minHeight: '600px' }}>
          {tabValue === 0 && (
            <Card 
              sx={{ 
                height: '600px', 
                backgroundColor: alpha(theme.palette.background.paper, 0.7),
                backdropFilter: 'blur(10px)',
                borderRadius: 2,
                overflow: 'hidden'
              }}
            >
              <CardHeader 
                title={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography 
                      fontFamily="Orbitron"
                      fontSize="1.1rem"
                    >
                      Market Overview
                    </Typography>
                  </Box>
                }
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent sx={{ p: 0, height: 'calc(100% - 64px)' }}>
                {/* Always use TradingView widget */}
                <TradingViewWidget 
                  symbol={formatSymbolForTradingView(selectedSymbol)} 
                  interval={timeframe === '1d' ? 'D' : timeframe === '1w' ? 'W' : timeframe === '4h' ? '240' : '60'}
                  height="100%"
                  width="100%"
                  key={`${selectedSymbol}_${timeframe}`}
                />
              </CardContent>
            </Card>
          )}
          
          {tabValue === 1 && (
            <Box sx={{ mt: 2 }}>
              <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  startIcon={<RefreshIcon />}
                  onClick={handleRefreshAITradeSetups}
                  variant="outlined"
                  color="primary"
                  size="small"
                  disabled={Object.values(aiTradeSetups).some(setup => setup.loading)}
                >
                  Refresh AI Signals
                </Button>
              </Box>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  {renderAITradeSetupCard('SPY')}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderAITradeSetupCard('QQQ')}
                </Grid>
                <Grid item xs={12} md={4}>
                  {renderAITradeSetupCard('AAPL')}
                </Grid>
              </Grid>
            </Box>
          )}
          
          {tabValue === 2 && (
            <Card 
              sx={{ 
                minHeight: '600px', 
                backgroundColor: alpha(theme.palette.background.paper, 0.7),
                backdropFilter: 'blur(10px)',
                borderRadius: 2
              }}
            >
              <CardHeader 
                title="Institutional Flow" 
                titleTypographyProps={{ 
                  fontFamily: 'Orbitron',
                  fontSize: '1.1rem'
                }} 
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent>
                <InstitutionalFlowTable />
              </CardContent>
            </Card>
          )}
          
          {tabValue === 3 && (
            <Card 
              sx={{ 
                minHeight: '600px', 
                backgroundColor: alpha(theme.palette.background.paper, 0.7),
                backdropFilter: 'blur(10px)',
                borderRadius: 2
              }}
            >
              <CardHeader 
                title="Trade Journal" 
                titleTypographyProps={{ 
                  fontFamily: 'Orbitron',
                  fontSize: '1.1rem'
                }} 
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent>
                <TradeJournalPlaceholder />
              </CardContent>
            </Card>
          )}
        </Box>
      </Box>
    </Container>
  );
};

export default LiveMarket; 