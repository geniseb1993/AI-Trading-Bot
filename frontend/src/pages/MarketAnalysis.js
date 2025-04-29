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
  CircularProgress,
  Card,
  CardContent,
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Tab,
  Tabs,
  LinearProgress,
  Alert,
  Stack,
  Switch,
  FormControlLabel,
  TableCell
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  Refresh, 
  ShowChart,
  Check,
  Warning,
  Analytics
} from '@mui/icons-material';
import axios from 'axios';
import { motion } from 'framer-motion';

// Import TradingView widget for charts
import TradingViewWidget from '../components/TradingViewWidget';
// Import our TradingView integration service (now as a singleton instance)
import tradingViewService from '../services/TradingViewIntegration';

// Mock chart component - In a real app, you would use a charting library like recharts or chart.js
const MockChart = ({ title, height, color }) => {
  return (
    <Box 
      sx={{ 
        height: height || 300, 
        width: '100%', 
        bgcolor: 'background.paper',
        position: 'relative',
        borderRadius: 1,
        overflow: 'hidden'
      }}
    >
      <Box 
        sx={{ 
          height: '100%', 
          width: '100%', 
          background: `linear-gradient(180deg, ${color}22 0%, ${color}11 100%)`,
          position: 'relative'
        }}
      >
        {/* Random chart line */}
        <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
          <path
            d={`M0,${50 + Math.random() * 20} ${Array.from({ length: 20 }).map((_, i) => 
              `L${i * 5},${50 + Math.sin(i * 0.5) * 20 + Math.random() * 10}`).join(' ')} L100,${50 + Math.random() * 20}`}
            stroke={color}
            strokeWidth="2"
            fill="none"
          />
        </svg>
        
        <Box sx={{ position: 'absolute', top: 10, left: 10 }}>
          <Typography variant="subtitle2" color="text.secondary">{title}</Typography>
        </Box>
      </Box>
    </Box>
  );
};

// Component to display data source information
const DataSourceInfo = ({ isRealData, dataSource }) => {
  return (
    <Box sx={{ mt: 1, mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <Chip 
        icon={isRealData ? <Check /> : <Warning />}
        label={`Data Source: ${dataSource.charAt(0).toUpperCase() + dataSource.slice(1)}`}
        color={isRealData ? "success" : "warning"}
        variant="outlined"
        size="small"
      />
      <Typography variant="caption" color="text.secondary">
        {isRealData ? 'Using real-time market data' : 'Using mock data - check API connection'}
      </Typography>
    </Box>
  );
};

// Component to render TradingView chart
const TradingViewTab = ({ symbol, timeframe }) => {
  // Add state to track mounting
  const [mounted, setMounted] = useState(false);
  
  // Mark component as mounted after a short delay
  useEffect(() => {
    const timer = setTimeout(() => {
      setMounted(true);
    }, 300);
    return () => clearTimeout(timer);
  }, []);
  
  // Map component timeframe to TradingView interval format
  const mapTimeframeToInterval = (tf) => {
    const mapping = {
      '1d': 'D',
      '1w': 'W',
      '1m': 'M',
      '3m': '3M',
      'ytd': 'YTD',
      '1y': '12M'
    };
    return mapping[tf] || 'D';
  };

  // Format symbol for TradingView (add exchange prefix if needed)
  const formatSymbolForTradingView = (sym) => {
    // This is a simple mapping, extend as needed
    const tickerMap = {
      'SPY': 'AMEX:SPY',
      'QQQ': 'NASDAQ:QQQ',
      'DIA': 'AMEX:DIA',
      'IWM': 'AMEX:IWM',
      'XLK': 'AMEX:XLK',
      'XLF': 'AMEX:XLF',
      'XLV': 'AMEX:XLV',
      'XLE': 'AMEX:XLE'
    };
    
    return tickerMap[sym] || sym;
  };

  return (
    <Box sx={{ height: 600, width: '100%', mt: 2 }}>
      {mounted ? (
        <TradingViewWidget 
          symbol={formatSymbolForTradingView(symbol)}
          interval={mapTimeframeToInterval(timeframe)}
          key={`tv-widget-${symbol}-${timeframe}-${Math.random().toString(36).substring(2, 9)}`}
        />
      ) : (
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            height: '100%' 
          }}
        >
          <CircularProgress />
        </Box>
      )}
    </Box>
  );
};

const MarketAnalysis = () => {
  const [marketData, setMarketData] = useState({
    indices: [],
    sectors: [],
    breadth: {},
    fear_greed: {
      value: 50,
      rating: 'Neutral',
      components: {}
    },
    economic_indicators: []
  });
  const [loading, setLoading] = useState(false);
  const [timeframe, setTimeframe] = useState('1d');
  const [tabValue, setTabValue] = useState(0);
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [isRealData, setIsRealData] = useState(true);
  const [dataSource, setDataSource] = useState('tradingview');
  const [useRealData, setUseRealData] = useState(true);
  const [gptInsights, setGptInsights] = useState({
    market_summary: '',
    trade_suggestions: [],
    market_trends: [],
    loading: false
  });

  const timeframes = [
    { value: '1d', label: '1 Day' },
    { value: '1w', label: '1 Week' },
    { value: '1m', label: '1 Month' },
    { value: '3m', label: '3 Months' },
    { value: 'ytd', label: 'Year to Date' },
    { value: '1y', label: '1 Year' },
  ];

  const symbols = [
    { value: 'SPY', label: 'S&P 500 (SPY)' },
    { value: 'QQQ', label: 'Nasdaq 100 (QQQ)' },
    { value: 'DIA', label: 'Dow Jones (DIA)' },
    { value: 'IWM', label: 'Russell 2000 (IWM)' },
    { value: 'XLK', label: 'Technology (XLK)' },
    { value: 'XLF', label: 'Financials (XLF)' },
    { value: 'XLV', label: 'Healthcare (XLV)' },
    { value: 'XLE', label: 'Energy (XLE)' }
  ];

  useEffect(() => {
    // Always use real data
    setUseRealData(true);
  }, []);

  useEffect(() => {
    fetchMarketAnalysisData();
  }, [timeframe, useRealData]);

  const fetchMarketAnalysisData = async () => {
    setLoading(true);
    if (tabValue === 3) {
      // If on GPT Insights tab, also fetch AI insights
      fetchGPTInsights();
    }
    
    try {
      // Always try to fetch real data from TradingView first
      const tvData = await tradingViewService.getMarketAnalysis(timeframe);
      if (tvData) {
        // Map the TradingView data structure to our component's expected structure
        setMarketData({
          indices: tvData.major_indices || [],
          sectors: tvData.sector_performance || [],
          breadth: tvData.market_breadth || {},
          fear_greed: {
            value: tvData.market_sentiment?.fear_greed_index || 50,
            rating: tvData.market_sentiment?.sentiment || 'Neutral',
            components: tvData.market_sentiment?.components || {}
          },
          economic_indicators: tvData.economic_indicators || []
        });
        setIsRealData(true);
        setDataSource('tradingview');
      } else {
        // If TradingView integration fails, try API
        await fetchFromApi();
      }
    } catch (error) {
      console.error('Error fetching market analysis data:', error);
      // Try API as fallback
      try {
        await fetchFromApi();
      } catch (apiError) {
        console.error('API fallback also failed:', apiError);
        // Generate mock data only as last resort
        generateMockData();
      }
    } finally {
      setLoading(false);
    }
  };
  
  const fetchFromApi = async () => {
    try {
      // Try to fetch data from API
      const response = await axios.post('/api/market-analysis/get-data', {
        timeframe
      });
      
      if (response.data && response.data.success) {
        // Ensure all needed properties exist
        const data = response.data.data || {};
        setMarketData({
          indices: Array.isArray(data.indices) ? data.indices : [],
          sectors: Array.isArray(data.sectors) ? data.sectors : [],
          breadth: data.breadth || {},
          fear_greed: {
            value: data.fear_greed?.value || 50,
            rating: data.fear_greed?.rating || 'Neutral',
            components: data.fear_greed?.components || {}
          },
          economic_indicators: Array.isArray(data.economic_indicators) 
            ? data.economic_indicators : []
        });
        setIsRealData(response.data.isRealData === true);
        setDataSource(response.data.source || 'api');
      } else {
        // If API fails, generate mock data
        generateMockData();
      }
    } catch (error) {
      console.error('Error fetching from API:', error);
      throw error;
    }
  };

  const generateMockData = () => {
    // Generate mock market indices data
    const mockIndices = [
      { 
        name: 'S&P 500', 
        symbol: 'SPX', 
        price: 5250.43, 
        change: Math.random() * 2 - 0.5, 
        volume: 2543000000 
      },
      { 
        name: 'Dow Jones', 
        symbol: 'DJI', 
        price: 38765.42, 
        change: Math.random() * 2 - 0.5, 
        volume: 342000000 
      },
      { 
        name: 'Nasdaq', 
        symbol: 'COMP', 
        price: 16432.78, 
        change: Math.random() * 2 - 0.5, 
        volume: 5230000000 
      },
      { 
        name: 'Russell 2000', 
        symbol: 'RUT', 
        price: 2152.32, 
        change: Math.random() * 2 - 0.5, 
        volume: 1250000000 
      },
      { 
        name: 'VIX', 
        symbol: 'VIX', 
        price: 16.25, 
        change: Math.random() * 5 - 2.5, 
        volume: null 
      }
    ];

    // Generate mock sector performance data
    const mockSectors = [
      { name: 'Technology', change: Math.random() * 4 - 1.5, volume: 3240000000 },
      { name: 'Healthcare', change: Math.random() * 4 - 1.5, volume: 1820000000 },
      { name: 'Financials', change: Math.random() * 4 - 1.5, volume: 2150000000 },
      { name: 'Consumer Discretionary', change: Math.random() * 4 - 1.5, volume: 1970000000 },
      { name: 'Communication Services', change: Math.random() * 4 - 1.5, volume: 1650000000 },
      { name: 'Industrials', change: Math.random() * 4 - 1.5, volume: 1430000000 },
      { name: 'Consumer Staples', change: Math.random() * 3 - 1, volume: 1280000000 },
      { name: 'Energy', change: Math.random() * 5 - 2, volume: 1920000000 },
      { name: 'Utilities', change: Math.random() * 2 - 0.5, volume: 980000000 },
      { name: 'Real Estate', change: Math.random() * 3 - 1, volume: 1120000000 },
      { name: 'Materials', change: Math.random() * 3 - 1, volume: 1050000000 }
    ];

    // Generate mock market breadth data
    const mockBreadth = {
      advance_decline_ratio: parseFloat((Math.random() * 2 + 0.5).toFixed(2)),
      advancing_stocks: Math.floor(Math.random() * 2000 + 1000),
      declining_stocks: Math.floor(Math.random() * 1500 + 500),
      new_highs: Math.floor(Math.random() * 300 + 50),
      new_lows: Math.floor(Math.random() * 100 + 10),
      stocks_above_200d_ma: `${Math.floor(Math.random() * 30 + 50)}%`,
      stocks_above_50d_ma: `${Math.floor(Math.random() * 30 + 40)}%`,
      mcclellan_oscillator: parseFloat((Math.random() * 200 - 100).toFixed(2)),
      cumulative_volume: `${Math.random() > 0.5 ? '+' : '-'}${parseFloat((Math.random() * 2).toFixed(2))}B`
    };

    // Generate mock fear & greed data
    const mockFearGreedValue = Math.floor(Math.random() * 100);
    let mockFearGreedRating = "";
    
    // Determine the fear/greed rating based on the value
    if (mockFearGreedValue <= 25) {
      mockFearGreedRating = 'Extreme Fear';
    } else if (mockFearGreedValue <= 45) {
      mockFearGreedRating = 'Fear';
    } else if (mockFearGreedValue <= 55) {
      mockFearGreedRating = 'Neutral';
    } else if (mockFearGreedValue <= 75) {
      mockFearGreedRating = 'Greed';
    } else {
      mockFearGreedRating = 'Extreme Greed';
    }
    
    const mockFearGreed = {
      value: mockFearGreedValue,
      rating: mockFearGreedRating,
      components: {
        stock_price_strength: Math.floor(Math.random() * 100),
        stock_price_breadth: Math.floor(Math.random() * 100),
        put_call_ratio: Math.floor(Math.random() * 100),
        market_volatility: Math.floor(Math.random() * 100),
        safe_haven_demand: Math.floor(Math.random() * 100),
        junk_bond_demand: Math.floor(Math.random() * 100)
      }
    };

    // Generate mock economic indicators
    const mockEconomicIndicators = [
      { name: 'US 10Y Yield', value: (Math.random() * 2 + 3).toFixed(2) + '%', change: Math.random() * 10 - 5 },
      { name: 'US 2Y Yield', value: (Math.random() * 2 + 2.5).toFixed(2) + '%', change: Math.random() * 10 - 5 },
      { name: 'USD Index', value: (Math.random() * 10 + 100).toFixed(2), change: Math.random() * 2 - 1 },
      { name: 'Gold', value: '$' + Math.floor(Math.random() * 300 + 1800), change: Math.random() * 4 - 2 },
      { name: 'WTI Crude', value: '$' + (Math.random() * 20 + 70).toFixed(2), change: Math.random() * 6 - 3 },
      { name: 'Bitcoin', value: '$' + Math.floor(Math.random() * 10000 + 50000), change: Math.random() * 10 - 5 }
    ];

    setMarketData({
      indices: mockIndices,
      sectors: mockSectors,
      breadth: mockBreadth,
      fear_greed: mockFearGreed,
      economic_indicators: mockEconomicIndicators
    });
    
    setIsRealData(false);
    setDataSource('mock');
  };

  const fetchGPTInsights = async () => {
    setGptInsights(prev => ({ ...prev, loading: true }));
    try {
      const response = await axios.post('/api/ai-insights/market-analysis', {
        symbol: 'SPY', // Default to analyzing the overall market
        timeframe
      });
      
      if (response.data && response.data.success) {
        const insights = response.data.data;
        setGptInsights({
          market_summary: insights.market_summary || '',
          trade_suggestions: insights.trade_suggestions || [],
          market_trends: insights.market_trends || [],
          loading: false
        });
      } else {
        // If API fails, generate mock GPT insights
        generateSmartMockGPTInsights();
      }
    } catch (error) {
      console.error('Error fetching GPT insights:', error);
      // Generate mock GPT insights if API request fails
      generateSmartMockGPTInsights();
    }
  };

  // Only keeping initial parts of this function, the rest stays the same
  const generateSmartMockGPTInsights = () => {
    // Create a smarter mock summary based on market data
    let summary = '';
    const marketPerformance = marketData.indices.find(index => index.symbol === 'SPX' || index.symbol === 'SPY');
    
    if (marketPerformance) {
      const change = marketPerformance.change;
      if (change > 1) {
        summary = 'The market is showing significant strength today with broad-based buying across most sectors. This follows positive economic data and bullish sentiment from institutional investors.';
      } else if (change > 0.3) {
        summary = 'Markets are moderately higher today, continuing the recent uptrend. Investor sentiment remains cautiously optimistic but some technical indicators suggest the market may be approaching overbought territory in the short term.';
      } else if (change > -0.3) {
        summary = 'Markets are relatively flat today as investors digest recent gains and await further catalysts. Volume is below average, suggesting a lack of conviction in either direction.';
      } else if (change > -1) {
        summary = 'Markets are modestly lower today amid profit-taking and concerns about economic growth and inflation. Defensive sectors are outperforming while high-beta names are seeing pressure.';
      } else {
        summary = 'Markets are experiencing significant selling pressure today driven by risk-off sentiment. Macroeconomic concerns and technical breakdowns are contributing to the weakness, with elevated volatility suggesting heightened investor uncertainty.';
      }
    } else {
      summary = 'Market analysis indicates mixed performance across major indices. Leading sectors include technology and healthcare, while defensive sectors are lagging. Breadth indicators suggest the rally is narrowing, which could signal caution in the near term.';
    }
    
    // Set the mock GPT insights
    setGptInsights({
      market_summary: summary,
      trade_suggestions: [
        {
          ticker: 'SPY',
          direction: 'LONG',
          entry_price: '$450-455',
          target_price: '$470-480',
          stop_loss: '$440',
          timeframe: '2-4 weeks',
          rationale: 'Technical breakout above key resistance with improving fundamentals and positive seasonality'
        },
        {
          ticker: 'QQQ',
          direction: 'LONG',
          entry_price: '$370-375',
          target_price: '$400',
          stop_loss: '$360',
          timeframe: '3-6 weeks',
          rationale: 'Technology sector outperformance expected to continue with multiple expansion supported by AI growth narrative'
        },
        {
          ticker: 'XLF',
          direction: 'LONG',
          entry_price: '$35-36',
          target_price: '$39-40',
          stop_loss: '$34',
          timeframe: '1-3 months',
          rationale: 'Financials becoming attractive as rate cut expectations moderate and valuations remain compelling relative to broader market'
        }
      ],
      market_trends: [
        {
          title: 'Narrowing Market Breadth',
          description: 'Fewer stocks are participating in the market rally, with the advance-decline line showing divergence from price action, suggesting potential vulnerability',
          impact: 'NEGATIVE',
          confidence: 'MEDIUM'
        },
        {
          title: 'Sector Rotation',
          description: 'Ongoing rotation from high-growth tech into cyclicals and value sectors indicates broadening market participation which historically supports sustainable rallies',
          impact: 'POSITIVE',
          confidence: 'HIGH'
        },
        {
          title: 'Volatility Compression',
          description: 'VIX has declined to multi-month lows suggesting complacency, which often precedes market corrections or increased volatility events',
          impact: 'NEGATIVE',
          confidence: 'MEDIUM'
        }
      ],
      loading: false
    });
  };
  
  // Format symbol for TradingView
  const formatSymbolForTradingView = (symbol) => {
    // Special handling for SPY which needs the exchange prefix
    const symbolMapping = {
      'SPY': 'AMEX:SPY',
      'QQQ': 'NASDAQ:QQQ',
      'SPX': 'INDEX:SPX',
      'DJI': 'INDEX:DJI',
      'COMP': 'INDEX:COMP',
      'IWM': 'AMEX:IWM',
      'XLF': 'AMEX:XLF',
      'XLK': 'AMEX:XLK',
      'XLE': 'AMEX:XLE',
      'XLV': 'AMEX:XLV',
    };
    
    return symbolMapping[symbol] || `NASDAQ:${symbol}`;
  };

  // Convert timeframe to TradingView interval format
  const getTradingViewInterval = () => {
    const map = {
      '1d': 'D',
      '1w': 'W',
      '1m': 'M',
      '3m': '3M',
      'ytd': 'YTD',
      '1y': '12M'
    };
    return map[timeframe] || 'D';
  };

  const handleTimeframeChange = (event) => {
    setTimeframe(event.target.value);
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    if (newValue === 3) {
      fetchGPTInsights();
    }
  };

  const handleSymbolChange = (event) => {
    setSelectedSymbol(event.target.value);
  };
  
  const handleUseRealDataChange = (event) => {
    setUseRealData(event.target.checked);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom>Market Analysis</Typography>
      
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <FormControl sx={{ minWidth: 200, mr: 2 }}>
            <InputLabel id="timeframe-label">Timeframe</InputLabel>
            <Select
              labelId="timeframe-label"
              value={timeframe}
              onChange={handleTimeframeChange}
              label="Timeframe"
            >
              {timeframes.map((tf) => (
                <MenuItem key={tf.value} value={tf.value}>{tf.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel id="symbol-label">Symbol</InputLabel>
            <Select
              labelId="symbol-label"
              value={selectedSymbol}
              onChange={handleSymbolChange}
              label="Symbol"
            >
              {symbols.map((sym) => (
                <MenuItem key={sym.value} value={sym.value}>{sym.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            startIcon={<Refresh />}
            onClick={fetchMarketAnalysisData}
            disabled={loading}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <FormControlLabel
            control={
              <Switch 
                checked={useRealData}
                onChange={handleUseRealDataChange}
                color="primary"
              />
            }
            label="Use TradingView Data"
          />
        </Grid>
      </Grid>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Paper sx={{ mb: 3 }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              indicatorColor="primary"
              textColor="primary"
              variant="scrollable"
              scrollButtons="auto"
              aria-label="market analysis tabs"
            >
              <Tab icon={<ShowChart />} label="Chart" />
              <Tab icon={<Analytics />} label="Market Overview" />
              <Tab icon={<TrendingUp />} label="Sector Performance" />
              <Tab icon={<TrendingDown />} label="AI Insights" />
            </Tabs>
            
            <Box sx={{ p: 2 }}>
              {tabValue === 0 && (
                <>
                  <Paper sx={{ p: 2, mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" component="h2">Market Overview</Typography>
                      <Button 
                        startIcon={<Refresh />} 
                        onClick={fetchMarketAnalysisData}
                        disabled={loading}
                        size="small"
                      >
                        Refresh
                      </Button>
                    </Box>
                    
                    <Grid container spacing={2}>
                      {/* Render TradingView Chart */}
                      <Grid item xs={12}>
                        <TradingViewTab symbol={selectedSymbol} timeframe={timeframe} />
                      </Grid>
                    </Grid>
                  </Paper>
                  
                  <DataSourceInfo isRealData={isRealData} dataSource={dataSource} />
                </>
              )}
              {tabValue === 1 && (
                <Grid container spacing={2}>
                  {/* Major Indices */}
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, height: '100%' }}>
                      <Typography variant="h6" sx={{ mb: 2 }}>Major Indices</Typography>
                      <List>
                        {marketData.indices && marketData.indices.map((index, i) => (
                          <ListItem key={i} divider={i < marketData.indices.length - 1}>
                            <ListItemText primary={index.name} />
                            <Box>
                              <Typography 
                                variant="body2" 
                                sx={{ 
                                  color: index.change >= 0 ? 'success.main' : 'error.main',
                                  fontWeight: 'bold'
                                }}
                              >
                                {index.change >= 0 ? '+' : ''}{typeof index.change === 'number' ? index.change.toFixed(2) : 'N/A'}%
                              </Typography>
                            </Box>
                          </ListItem>
                        ))}
                      </List>
                    </Paper>
                  </Grid>
                  
                  {/* Sectors */}
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, height: '100%' }}>
                      <Typography variant="h6" sx={{ mb: 2 }}>Sector Performance</Typography>
                      <List>
                        {marketData.sectors && marketData.sectors.map((sector, i) => (
                          <ListItem key={i} divider={i < marketData.sectors.length - 1}>
                            <ListItemText primary={sector.name} />
                            <Box>
                              <Typography 
                                variant="body2" 
                                sx={{ 
                                  color: sector.change >= 0 ? 'success.main' : 'error.main',
                                  fontWeight: 'bold'
                                }}
                              >
                                {sector.change >= 0 ? '+' : ''}{typeof sector.change === 'number' ? sector.change.toFixed(2) : 'N/A'}%
                              </Typography>
                            </Box>
                          </ListItem>
                        ))}
                      </List>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <DataSourceInfo isRealData={isRealData} dataSource={dataSource} />
                  </Grid>
                </Grid>
              )}
              {tabValue === 2 && (
                <Grid container spacing={2}>
                  {/* Sector Performance content */}
                  {/* ... (your existing sector performance content) ... */}
                </Grid>
              )}
              {tabValue === 3 && (
                <Grid container spacing={2}>
                  {/* AI Insights content */}
                  {/* ... (your existing AI insights content) ... */}
                </Grid>
              )}
            </Box>
          </Paper>
          
          <DataSourceInfo isRealData={isRealData} dataSource={dataSource} />
        </>
      )}
    </Box>
  );
};

export default MarketAnalysis; 