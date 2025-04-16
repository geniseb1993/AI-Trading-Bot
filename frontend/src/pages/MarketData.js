import React, { useState, useEffect } from 'react';
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

// Import TradingView widget
import TradingViewWidget from '../components/TradingViewWidget';

// Define API base URL based on environment
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

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

  useEffect(() => {
    fetchMarketData();
  }, []);
  
  const fetchMarketData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/market-data/${symbol}?timeframe=${timeframe}&days=${days}`);
      if (response.data && response.data.success) {
        console.log('Received market data:', response.data);
        setMarketData(response.data.bars || []);
        setMarketOverview(response.data.market_overview || {
          stats: {},
          technical_indicators: {},
          market_sentiment: {},
          sector_performance: [],
          upcoming_events: []
        });
        setIsRealData(response.data.isRealData === true);
        setDataSource(response.data.source || 'unknown');
      } else {
        // If API returns unsuccessful but responds, show error
        const errorMessage = response.data?.message || 'Failed to fetch market data';
        console.error(errorMessage);
        setError(errorMessage);
        setMarketData([]); // Clear any existing data
      }
    } catch (error) {
      console.error('Failed to fetch from API:', error);
      setError('Failed to connect to market data service. Please try again later.');
      setMarketData([]); // Clear any existing data
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
    setViewMode(newValue);
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
    <Card 
      component={motion.div}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      sx={{
        mb: 3,
        height: '100%',
        backgroundColor: alpha(theme.palette.background.paper, 0.7),
        backdropFilter: 'blur(10px)',
        border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
        boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.35)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`,
        borderRadius: 2,
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        '&:hover': {
          boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.4)}, 0 0 12px ${alpha(theme.palette.primary.main, 0.25)}`,
          transform: 'translateY(-2px)'
        }
      }}
    >
      <CardHeader
        title={
          <Typography variant="h6" fontFamily="Orbitron" display="flex" alignItems="center" gap={1}>
            <Inventory fontSize="small" />
            Data Controls
          </Typography>
        }
        sx={{ 
          padding: viewMode === 'chart' ? '8px 16px' : '12px 20px',
          backgroundColor: alpha(theme.palette.primary.main, 0.1),
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`
        }}
      />
      <CardContent sx={{ padding: viewMode === 'chart' ? '12px' : '16px' }}>
        <Grid container spacing={viewMode === 'chart' ? 1 : 2} alignItems="center">
          <Grid item xs={12} sm={viewMode === 'chart' ? 3 : 6} md={viewMode === 'chart' ? 2 : 3}>
            <FormControl fullWidth size={viewMode === 'chart' ? "small" : "medium"}>
              <InputLabel id="symbol-label">Symbol</InputLabel>
              <Select
                labelId="symbol-label"
                value={symbol}
                label="Symbol"
                onChange={handleSymbolChange}
                sx={{ fontFamily: 'Roboto Mono' }}
              >
                {popularSymbols.map(sym => (
                  <MenuItem key={sym} value={sym} sx={{ fontFamily: 'Roboto Mono' }}>{sym}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={viewMode === 'chart' ? 3 : 6} md={viewMode === 'chart' ? 2 : 3}>
            <FormControl fullWidth size={viewMode === 'chart' ? "small" : "medium"}>
              <InputLabel id="timeframe-label">Timeframe</InputLabel>
              <Select
                labelId="timeframe-label"
                value={timeframe}
                label="Timeframe"
                onChange={handleTimeframeChange}
              >
                {timeframes.map(tf => (
                  <MenuItem key={tf.value} value={tf.value}>{tf.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={viewMode === 'chart' ? 2 : 6} md={viewMode === 'chart' ? 1 : 2}>
            <TextField
              fullWidth
              label="Days"
              type="number"
              value={days}
              onChange={handleDaysChange}
              InputProps={{ inputProps: { min: 1, max: 365 } }}
              size={viewMode === 'chart' ? "small" : "medium"}
            />
          </Grid>
          <Grid item xs={12} sm={viewMode === 'chart' ? 4 : 6} md={viewMode === 'chart' ? 3 : 4}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleRefresh}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Refresh />}
              disabled={loading}
              fullWidth
              size={viewMode === 'chart' ? "small" : "medium"}
              sx={{ 
                height: viewMode === 'chart' ? '40px' : '56px', 
                fontFamily: 'Orbitron' 
              }}
            >
              Refresh Data
            </Button>
          </Grid>
          <Grid item xs={12} sm={viewMode === 'chart' ? 12 : 6} md={viewMode === 'chart' ? 4 : 12}>
            <Box sx={{ 
              mt: viewMode === 'chart' ? 0 : 2, 
              borderTop: viewMode === 'chart' ? 'none' : `1px solid ${alpha(theme.palette.divider, 0.1)}`, 
              pt: viewMode === 'chart' ? 0 : 1, 
              display: 'flex', 
              justifyContent: 'center' 
            }}>
              <Tabs
                value={viewMode}
                onChange={handleViewModeChange}
                aria-label="view mode tabs"
                indicatorColor="primary"
                textColor="primary"
                variant={viewMode === 'chart' ? "scrollable" : "standard"}
                scrollButtons={viewMode === 'chart' ? "auto" : false}
                sx={{ 
                  minHeight: viewMode === 'chart' ? '40px' : '48px',
                  '& .MuiTab-root': {
                    minHeight: viewMode === 'chart' ? '40px' : '48px',
                    py: viewMode === 'chart' ? 0 : 1
                  }
                }}
              >
                <Tab icon={<Assessment />} value="overview" label="Market Overview" />
                <Tab icon={<ShowChart />} value="chart" label="Chart View" />
                <Tab icon={<TableChart />} value="table" label="Table View" />
              </Tabs>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  // Card for the market overview
  const MarketOverviewCard = () => {
    const stats = marketOverview.stats || {};
    const technicalIndicators = marketOverview.technical_indicators || {};
    const sentiment = marketOverview.market_sentiment || {};
    const sectorPerformance = marketOverview.sector_performance || [];
    const upcomingEvents = marketOverview.upcoming_events || [];
    
    return (
      <Card 
        component={motion.div}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        sx={{
          flexGrow: 1,
          height: 'calc(100vh - 320px)',
          minHeight: '500px',
          backgroundColor: alpha(theme.palette.background.paper, 0.7),
          backdropFilter: 'blur(10px)',
          border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
          boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.35)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`,
          borderRadius: 2,
          overflow: 'hidden',
          transition: 'all 0.3s ease',
          position: 'relative',
          '&:hover': {
            boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.4)}, 0 0 12px ${alpha(theme.palette.primary.main, 0.25)}`,
            transform: 'translateY(-2px)'
          }
        }}
      >
        <CardHeader
          title={
            <Typography variant="h6" fontFamily="Orbitron" display="flex" alignItems="center" gap={1}>
              <Assessment fontSize="small" />
              {symbol} Market Overview
            </Typography>
          }
          sx={{ 
            padding: '12px 20px',
            backgroundColor: alpha(theme.palette.primary.main, 0.1),
            borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`
          }}
        />
        <CardContent sx={{ height: 'calc(100% - 80px)', p: 2, overflowY: 'auto' }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', flexDirection: 'column', p: 3 }}>
              <Typography variant="h6" color="error" gutterBottom>Error</Typography>
              <Typography variant="body1" color="error" align="center">{error}</Typography>
              <Button 
                variant="contained" 
                color="primary" 
                sx={{ mt: 2 }} 
                onClick={handleRefresh}
              >
                Try Again
              </Button>
            </Box>
          ) : (
            <Grid container spacing={3}>
              {/* Key Statistics */}
              <Grid item xs={12} md={6}>
                <Card 
                  elevation={0}
                  sx={{ 
                    backgroundColor: alpha(theme.palette.background.paper, 0.5),
                    height: '100%'
                  }}
                >
                  <CardHeader 
                    title={
                      <Typography variant="h6" fontFamily="Orbitron">
                        Key Statistics
                      </Typography>
                    }
                    sx={{ pb: 1 }}
                  />
                  <CardContent>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="text.secondary">52-Week High</Typography>
                        <Typography variant="body1" fontWeight="bold" fontFamily="Roboto Mono">${stats['52_week_high'] || 'N/A'}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="text.secondary">52-Week Low</Typography>
                        <Typography variant="body1" fontWeight="bold" fontFamily="Roboto Mono">${stats['52_week_low'] || 'N/A'}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="text.secondary">Avg. Volume</Typography>
                        <Typography variant="body1" fontWeight="bold" fontFamily="Roboto Mono">{stats.avg_volume?.toLocaleString() || 'N/A'}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="text.secondary">Volatility</Typography>
                        <Typography variant="body1" fontWeight="bold" fontFamily="Roboto Mono">{stats.volatility}%</Typography>
                      </Grid>
                      <Grid item xs={12}>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="subtitle2" color="text.secondary">Performance</Typography>
                      </Grid>
                      <Grid item xs={3}>
                        <Typography variant="subtitle2" color="text.secondary">1M</Typography>
                        <Typography 
                          variant="body1" 
                          fontWeight="bold" 
                          fontFamily="Roboto Mono"
                          color={stats.performance_1m >= 0 ? 'success.main' : 'error.main'}
                        >
                          {stats.performance_1m >= 0 ? '+' : ''}{stats.performance_1m}%
                        </Typography>
                      </Grid>
                      <Grid item xs={3}>
                        <Typography variant="subtitle2" color="text.secondary">3M</Typography>
                        <Typography 
                          variant="body1" 
                          fontWeight="bold" 
                          fontFamily="Roboto Mono"
                          color={stats.performance_3m >= 0 ? 'success.main' : 'error.main'}
                        >
                          {stats.performance_3m >= 0 ? '+' : ''}{stats.performance_3m}%
                        </Typography>
                      </Grid>
                      <Grid item xs={3}>
                        <Typography variant="subtitle2" color="text.secondary">YTD</Typography>
                        <Typography 
                          variant="body1" 
                          fontWeight="bold" 
                          fontFamily="Roboto Mono"
                          color={stats.performance_ytd >= 0 ? 'success.main' : 'error.main'}
                        >
                          {stats.performance_ytd >= 0 ? '+' : ''}{stats.performance_ytd}%
                        </Typography>
                      </Grid>
                      <Grid item xs={3}>
                        <Typography variant="subtitle2" color="text.secondary">1Y</Typography>
                        <Typography 
                          variant="body1" 
                          fontWeight="bold" 
                          fontFamily="Roboto Mono"
                          color={stats.performance_1y >= 0 ? 'success.main' : 'error.main'}
                        >
                          {stats.performance_1y >= 0 ? '+' : ''}{stats.performance_1y}%
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Technical Indicators */}
              <Grid item xs={12} md={6}>
                <Card 
                  elevation={0}
                  sx={{ 
                    backgroundColor: alpha(theme.palette.background.paper, 0.5),
                    height: '100%'
                  }}
                >
                  <CardHeader 
                    title={
                      <Typography variant="h6" fontFamily="Orbitron">
                        Technical Indicators
                      </Typography>
                    }
                    sx={{ pb: 1 }}
                  />
                  <CardContent>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="text.secondary">RSI (14)</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography 
                            variant="body1" 
                            fontWeight="bold" 
                            fontFamily="Roboto Mono"
                            color={
                              technicalIndicators.rsi > 70 ? 'error.main' : 
                              technicalIndicators.rsi < 30 ? 'success.main' : 
                              'text.primary'
                            }
                          >
                            {technicalIndicators.rsi || 'N/A'}
                          </Typography>
                          <Tooltip title={
                            technicalIndicators.rsi > 70 ? 'Overbought' : 
                            technicalIndicators.rsi < 30 ? 'Oversold' : 
                            'Neutral'
                          }>
                            <Info fontSize="small" sx={{ ml: 1, opacity: 0.7 }} />
                          </Tooltip>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="text.secondary">MACD</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography 
                            variant="body1" 
                            fontWeight="bold" 
                            fontFamily="Roboto Mono"
                            color={
                              (technicalIndicators.macd?.value || 0) >= 0 ? 'success.main' : 'error.main'
                            }
                          >
                            {technicalIndicators.macd?.value || 'N/A'}
                          </Typography>
                          <Tooltip title={`Signal: ${technicalIndicators.macd?.signal || 'N/A'}, Histogram: ${technicalIndicators.macd?.histogram || 'N/A'}`}>
                            <Info fontSize="small" sx={{ ml: 1, opacity: 0.7 }} />
                          </Tooltip>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="subtitle2" color="text.secondary">Bollinger Bands</Typography>
                      </Grid>
                      
                      <Grid item xs={4}>
                        <Typography variant="caption" color="text.secondary">Upper</Typography>
                        <Typography variant="body2" fontFamily="Roboto Mono">
                          ${technicalIndicators.bollinger_bands?.upper || 'N/A'}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={4}>
                        <Typography variant="caption" color="text.secondary">Middle</Typography>
                        <Typography variant="body2" fontFamily="Roboto Mono">
                          ${technicalIndicators.bollinger_bands?.middle || 'N/A'}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={4}>
                        <Typography variant="caption" color="text.secondary">Lower</Typography>
                        <Typography variant="body2" fontFamily="Roboto Mono">
                          ${technicalIndicators.bollinger_bands?.lower || 'N/A'}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="subtitle2" color="text.secondary">Moving Averages</Typography>
                      </Grid>
                      
                      <Grid item xs={6} sm={4}>
                        <Typography variant="caption" color="text.secondary">SMA 20</Typography>
                        <Typography 
                          variant="body2" 
                          fontFamily="Roboto Mono"
                          color={
                            marketData.length > 0 && (technicalIndicators.moving_averages?.sma_20 || 0) > marketData[marketData.length-1].close ? 
                            'error.main' : 'success.main'
                          }
                        >
                          ${technicalIndicators.moving_averages?.sma_20 || 'N/A'}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6} sm={4}>
                        <Typography variant="caption" color="text.secondary">SMA 50</Typography>
                        <Typography 
                          variant="body2" 
                          fontFamily="Roboto Mono"
                          color={
                            marketData.length > 0 && (technicalIndicators.moving_averages?.sma_50 || 0) > marketData[marketData.length-1].close ? 
                            'error.main' : 'success.main'
                          }
                        >
                          ${technicalIndicators.moving_averages?.sma_50 || 'N/A'}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6} sm={4}>
                        <Typography variant="caption" color="text.secondary">SMA 200</Typography>
                        <Typography 
                          variant="body2" 
                          fontFamily="Roboto Mono"
                          color={
                            marketData.length > 0 && (technicalIndicators.moving_averages?.sma_200 || 0) > marketData[marketData.length-1].close ? 
                            'error.main' : 'success.main'
                          }
                        >
                          ${technicalIndicators.moving_averages?.sma_200 || 'N/A'}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Market Sentiment */}
              <Grid item xs={12} md={6}>
                <Card 
                  elevation={0}
                  sx={{ 
                    backgroundColor: alpha(theme.palette.background.paper, 0.5),
                    height: '100%'
                  }}
                >
                  <CardHeader 
                    title={
                      <Typography variant="h6" fontFamily="Orbitron">
                        Market Sentiment
                      </Typography>
                    }
                    sx={{ pb: 1 }}
                  />
                  <CardContent>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="text.secondary">Analysts Rating</Typography>
                        <Chip 
                          label={sentiment.analysts_rating || 'N/A'} 
                          size="small"
                          color={
                            sentiment.analysts_rating === 'Strong Buy' || sentiment.analysts_rating === 'Buy' ? 'success' :
                            sentiment.analysts_rating === 'Hold' ? 'warning' :
                            sentiment.analysts_rating === 'Sell' || sentiment.analysts_rating === 'Strong Sell' ? 'error' :
                            'default'
                          }
                        />
                        <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                          Based on {sentiment.analyst_count || 0} analysts
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="text.secondary">Social Sentiment</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                          {sentiment.social_sentiment >= 0 ? 
                            <TrendingUp fontSize="small" color="success" sx={{ mr: 1 }} /> : 
                            <TrendingDown fontSize="small" color="error" sx={{ mr: 1 }} />
                          }
                          <Typography 
                            variant="body1" 
                            fontWeight="bold"
                            color={sentiment.social_sentiment >= 0 ? 'success.main' : 'error.main'}
                          >
                            {sentiment.social_sentiment}
                          </Typography>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="subtitle2" color="text.secondary">Price Targets</Typography>
                      </Grid>
                      
                      <Grid item xs={4}>
                        <Typography variant="caption" color="text.secondary">Low</Typography>
                        <Typography variant="body2" fontFamily="Roboto Mono" color="error.main">
                          ${sentiment.price_target?.low || 'N/A'}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={4}>
                        <Typography variant="caption" color="text.secondary">Average</Typography>
                        <Typography variant="body2" fontFamily="Roboto Mono" fontWeight="bold">
                          ${sentiment.price_target?.average || 'N/A'}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={4}>
                        <Typography variant="caption" color="text.secondary">High</Typography>
                        <Typography variant="body2" fontFamily="Roboto Mono" color="success.main">
                          ${sentiment.price_target?.high || 'N/A'}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Divider sx={{ my: 1 }} />
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="text.secondary">Institutional Ownership</Typography>
                        <Typography variant="body1" fontWeight="bold" fontFamily="Roboto Mono">
                          {sentiment.institutional_ownership || 0}%
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="text.secondary">Short Interest</Typography>
                        <Typography 
                          variant="body1" 
                          fontWeight="bold" 
                          fontFamily="Roboto Mono"
                          color={
                            (sentiment.short_interest || 0) > 20 ? 'error.main' : 
                            (sentiment.short_interest || 0) > 10 ? 'warning.main' : 
                            'text.primary'
                          }
                        >
                          {sentiment.short_interest || 0}%
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Sector Performance */}
              <Grid item xs={12} md={6}>
                <Card 
                  elevation={0}
                  sx={{ 
                    backgroundColor: alpha(theme.palette.background.paper, 0.5),
                    height: '100%'
                  }}
                >
                  <CardHeader 
                    title={
                      <Typography variant="h6" fontFamily="Orbitron">
                        Sector Performance
                      </Typography>
                    }
                    sx={{ pb: 1 }}
                  />
                  <CardContent>
                    <TableContainer sx={{ maxHeight: 200 }}>
                      <Table size="small" stickyHeader>
                        <TableHead>
                          <TableRow>
                            <TableCell>Sector</TableCell>
                            <TableCell align="right">1D</TableCell>
                            <TableCell align="right">1M</TableCell>
                            <TableCell align="right">YTD</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {sectorPerformance.map((sector, index) => (
                            <TableRow key={index}>
                              <TableCell>{sector.name}</TableCell>
                              <TableCell 
                                align="right"
                                sx={{ 
                                  color: sector.performance_1d >= 0 ? 'success.main' : 'error.main',
                                  fontWeight: 'bold'
                                }}
                              >
                                {sector.performance_1d >= 0 ? '+' : ''}{sector.performance_1d}%
                              </TableCell>
                              <TableCell 
                                align="right"
                                sx={{ 
                                  color: sector.performance_1m >= 0 ? 'success.main' : 'error.main',
                                  fontWeight: 'bold'
                                }}
                              >
                                {sector.performance_1m >= 0 ? '+' : ''}{sector.performance_1m}%
                              </TableCell>
                              <TableCell 
                                align="right"
                                sx={{ 
                                  color: sector.performance_ytd >= 0 ? 'success.main' : 'error.main',
                                  fontWeight: 'bold'
                                }}
                              >
                                {sector.performance_ytd >= 0 ? '+' : ''}{sector.performance_ytd}%
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Upcoming Events */}
              <Grid item xs={12}>
                <Card 
                  elevation={0}
                  sx={{ 
                    backgroundColor: alpha(theme.palette.background.paper, 0.5),
                    height: '100%',
                    mb: 2
                  }}
                >
                  <CardHeader 
                    title={
                      <Typography variant="h6" fontFamily="Orbitron">
                        Upcoming Events
                      </Typography>
                    }
                    sx={{ pb: 1 }}
                  />
                  <CardContent>
                    {upcomingEvents.length > 0 ? (
                      <List>
                        {upcomingEvents.map((event, index) => (
                          <ListItem 
                            key={index}
                            sx={{ 
                              borderLeft: `4px solid ${theme.palette.primary.main}`,
                              pl: 2,
                              mb: 1,
                              backgroundColor: alpha(theme.palette.background.paper, 0.3),
                              borderRadius: '0 4px 4px 0'
                            }}
                          >
                            <ListItemIcon>
                              <Event color="primary" />
                            </ListItemIcon>
                            <ListItemText
                              primary={event.type}
                              secondary={
                                <React.Fragment>
                                  <Typography component="span" variant="body2" color="text.primary">
                                    {event.date}
                                  </Typography>
                                  {" — "}{event.description}
                                </React.Fragment>
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Box sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="body1" color="text.secondary">
                          No upcoming events scheduled
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <PageLayout>
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: viewMode === 'chart' ? 1 : 3,
        mt: viewMode === 'chart' ? 0 : 1,
      }}>
        <Typography 
          variant="h4" 
          component={motion.h4}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          sx={{ 
            fontWeight: 'bold',
            color: 'primary.main',
            fontFamily: 'Orbitron',
            display: 'flex', 
            alignItems: 'center',
            gap: 1,
            fontSize: viewMode === 'chart' ? '1.5rem' : '2rem'
          }}
        >
          <Assessment fontSize={viewMode === 'chart' ? 'medium' : 'large'} />
          Market Data Explorer
        </Typography>
      </Box>
      
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        height: viewMode === 'chart' ? 'calc(100vh - 100px)' : 'calc(100vh - 140px)',
        px: viewMode === 'chart' ? 1 : 2
      }}>
        <ControlsCard />
        
        {/* Render the appropriate component based on view mode */}
        {viewMode === 'overview' && <MarketOverviewCard />}
        {viewMode === 'chart' && (
          <Card 
            component={motion.div}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            sx={{
              flexGrow: 1,
              height: 'calc(100vh - 250px)',
              minHeight: '600px',
              backgroundColor: alpha(theme.palette.background.paper, 0.7),
              backdropFilter: 'blur(10px)',
              border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
              boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.35)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`,
              borderRadius: 2,
              overflow: 'hidden',
              transition: 'all 0.3s ease',
              position: 'relative',
              '&:hover': {
                boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.4)}, 0 0 12px ${alpha(theme.palette.primary.main, 0.25)}`,
                transform: 'translateY(-2px)'
              }
            }}
          >
            <CardHeader
              title={
                <Typography variant="h6" fontFamily="Orbitron" display="flex" alignItems="center" gap={1}>
                  <ShowChart fontSize="small" />
                  {symbol} Chart
                </Typography>
              }
              action={
                <Button
                  variant="outlined"
                  size="small"
                  color="primary"
                  onClick={() => window.open(`https://www.tradingview.com/chart/?symbol=${formatSymbolForTradingView(symbol)}`, '_blank')}
                  startIcon={<Analytics />}
                  sx={{ mr: 1 }}
                >
                  Open in TradingView
                </Button>
              }
              sx={{ 
                padding: '12px 20px',
                backgroundColor: alpha(theme.palette.primary.main, 0.1),
                borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`
              }}
            />
            <CardContent sx={{ height: 'calc(100% - 80px)', p: 0 }}>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                  <CircularProgress />
                </Box>
              ) : error ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', flexDirection: 'column', p: 3 }}>
                  <Typography variant="h6" color="error" gutterBottom>Error</Typography>
                  <Typography variant="body1" color="error" align="center">{error}</Typography>
                  <Button 
                    variant="contained" 
                    color="primary" 
                    sx={{ mt: 2 }} 
                    onClick={handleRefresh}
                  >
                    Try Again
                  </Button>
                </Box>
              ) : marketData.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', flexDirection: 'column', p: 3 }}>
                  <Typography variant="h6" gutterBottom>No Data Available</Typography>
                  <Typography variant="body1" align="center">No market data is available for the selected symbol and timeframe.</Typography>
                </Box>
              ) : (
                <Box sx={{ height: '100%', width: '100%' }}>
                  {/* Use TradingView chart for chart view */}
                  <TradingViewWidget 
                    symbol={formatSymbolForTradingView(symbol)}
                    interval={getTradingViewInterval()}
                    height="100%"
                    width="100%"
                    key={`${symbol}_${timeframe}`}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        )}
        {viewMode === 'table' && (
          <Card 
            component={motion.div}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            sx={{
              flexGrow: 1,
              height: 'calc(100vh - 320px)',
              minHeight: '500px',
              backgroundColor: alpha(theme.palette.background.paper, 0.7),
              backdropFilter: 'blur(10px)',
              border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
              boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.35)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`,
              borderRadius: 2,
              overflow: 'hidden',
              transition: 'all 0.3s ease',
              position: 'relative',
              '&:hover': {
                boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.4)}, 0 0 12px ${alpha(theme.palette.primary.main, 0.25)}`,
                transform: 'translateY(-2px)'
              }
            }}
          >
            <CardHeader
              title={
                <Typography variant="h6" fontFamily="Orbitron" display="flex" alignItems="center" gap={1}>
                  <TableChart fontSize="small" />
                  {symbol} Price History
                </Typography>
              }
              sx={{ 
                padding: '12px 20px',
                backgroundColor: alpha(theme.palette.primary.main, 0.1),
                borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`
              }}
            />
            <CardContent sx={{ height: 'calc(100% - 80px)', p: 0 }}>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                  <CircularProgress />
                </Box>
              ) : error ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', flexDirection: 'column', p: 3 }}>
                  <Typography variant="h6" color="error" gutterBottom>Error</Typography>
                  <Typography variant="body1" color="error" align="center">{error}</Typography>
                  <Button 
                    variant="contained" 
                    color="primary" 
                    sx={{ mt: 2 }} 
                    onClick={handleRefresh}
                  >
                    Try Again
                  </Button>
                </Box>
              ) : marketData.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', flexDirection: 'column', p: 3 }}>
                  <Typography variant="h6" gutterBottom>No Data Available</Typography>
                  <Typography variant="body1" align="center">No market data is available for the selected symbol and timeframe.</Typography>
                </Box>
              ) : (
                <Box sx={{ height: '100%', width: '100%' }}>
                  <TableContainer sx={{ maxHeight: 'calc(100vh - 220px)', overflow: 'auto' }}>
                    <Table stickyHeader>
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 'bold', fontFamily: 'Orbitron', backgroundColor: alpha(theme.palette.background.paper, 0.9) }}>Date</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 'bold', fontFamily: 'Orbitron', backgroundColor: alpha(theme.palette.background.paper, 0.9) }}>Open</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 'bold', fontFamily: 'Orbitron', backgroundColor: alpha(theme.palette.background.paper, 0.9) }}>High</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 'bold', fontFamily: 'Orbitron', backgroundColor: alpha(theme.palette.background.paper, 0.9) }}>Low</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 'bold', fontFamily: 'Orbitron', backgroundColor: alpha(theme.palette.background.paper, 0.9) }}>Close</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 'bold', fontFamily: 'Orbitron', backgroundColor: alpha(theme.palette.background.paper, 0.9) }}>Volume</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 'bold', fontFamily: 'Orbitron', backgroundColor: alpha(theme.palette.background.paper, 0.9) }}>Change</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {marketData.map((row, index) => (
                          <TableRow 
                            key={index}
                            sx={{ 
                              '&:nth-of-type(odd)': { bgcolor: alpha(theme.palette.background.paper, 0.4) },
                              '&:nth-of-type(even)': { bgcolor: alpha(theme.palette.background.paper, 0.2) },
                              '&:hover': { 
                                bgcolor: alpha(theme.palette.primary.main, 0.1),
                                transition: 'background-color 0.2s ease'
                              },
                              transition: 'background-color 0.2s ease'
                            }}
                          >
                            <TableCell component="th" scope="row" sx={{ fontFamily: 'Roboto Mono' }}>
                              {row.date}
                            </TableCell>
                            <TableCell align="right" sx={{ fontFamily: 'Roboto Mono' }}>${row.open.toFixed(2)}</TableCell>
                            <TableCell align="right" sx={{ fontFamily: 'Roboto Mono' }}>${row.high.toFixed(2)}</TableCell>
                            <TableCell align="right" sx={{ fontFamily: 'Roboto Mono' }}>${row.low.toFixed(2)}</TableCell>
                            <TableCell align="right" sx={{ fontFamily: 'Roboto Mono' }}>${row.close.toFixed(2)}</TableCell>
                            <TableCell align="right" sx={{ fontFamily: 'Roboto Mono' }}>{row.volume.toLocaleString()}</TableCell>
                            <TableCell 
                              align="right"
                              sx={{ 
                                color: row.change >= 0 ? 'success.main' : 'error.main',
                                fontWeight: 'bold',
                                fontFamily: 'Roboto Mono',
                                bgcolor: row.change >= 0 
                                  ? alpha(theme.palette.success.main, 0.1) 
                                  : alpha(theme.palette.error.main, 0.1)
                              }}
                            >
                              {row.change >= 0 ? `+${row.change.toFixed(2)}%` : `${row.change.toFixed(2)}%`}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </CardContent>
          </Card>
        )}
      </Box>
    </PageLayout>
  );
};

export default MarketData; 