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
  LinearProgress
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  Refresh, 
  ShowChart,
  Check,
  Warning
} from '@mui/icons-material';
import axios from 'axios';

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

  useEffect(() => {
    fetchMarketAnalysisData();
  }, [timeframe]);

  const fetchMarketAnalysisData = async () => {
    setLoading(true);
    if (tabValue === 3) {
      // If on GPT Insights tab, also fetch AI insights
      fetchGPTInsights();
    }
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
      } else {
        // If API fails, generate mock data
        generateMockData();
      }
    } catch (error) {
      console.error('Error fetching market analysis data:', error);
      // Generate mock data if API request fails
      generateMockData();
    } finally {
      setLoading(false);
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
      {
        name: 'Unemployment Rate',
        value: `${parseFloat((Math.random() * 2 + 3).toFixed(1))}%`,
        previous: `${parseFloat((Math.random() * 2 + 3).toFixed(1))}%`,
        impact: Math.random() > 0.5 ? 'positive' : 'negative'
      },
      {
        name: 'GDP Growth Rate',
        value: `${parseFloat((Math.random() * 3 + 1).toFixed(1))}%`,
        previous: `${parseFloat((Math.random() * 3 + 1).toFixed(1))}%`,
        impact: Math.random() > 0.5 ? 'positive' : 'negative'
      },
      {
        name: 'Inflation Rate',
        value: `${parseFloat((Math.random() * 4 + 1).toFixed(1))}%`,
        previous: `${parseFloat((Math.random() * 4 + 1).toFixed(1))}%`,
        impact: Math.random() > 0.6 ? 'positive' : 'negative'
      },
      {
        name: 'Interest Rate',
        value: `${parseFloat((Math.random() * 3 + 3).toFixed(2))}%`,
        previous: `${parseFloat((Math.random() * 3 + 3).toFixed(2))}%`,
        impact: Math.random() > 0.4 ? 'positive' : 'negative'
      },
      {
        name: 'Consumer Sentiment',
        value: Math.floor(Math.random() * 30 + 70),
        previous: Math.floor(Math.random() * 30 + 70),
        impact: Math.random() > 0.5 ? 'positive' : 'negative'
      },
      {
        name: 'Retail Sales',
        value: `${parseFloat((Math.random() * 2 - 0.5).toFixed(1))}%`,
        previous: `${parseFloat((Math.random() * 2 - 0.5).toFixed(1))}%`,
        impact: Math.random() > 0.5 ? 'positive' : 'negative'
      }
    ];

    setMarketData({
      indices: mockIndices,
      sectors: mockSectors,
      breadth: mockBreadth,
      fear_greed: mockFearGreed,
      economic_indicators: mockEconomicIndicators
    });
  };

  const fetchGPTInsights = async () => {
    setGptInsights(prev => ({ ...prev, loading: true }));
    try {
      // Try to fetch GPT insights from API
      const response = await axios.post('/api/ai-insights/market-analysis', {
        timeframe
      });
      
      if (response.data && response.data.success) {
        setGptInsights({
          market_summary: response.data.market_summary || '',
          trade_suggestions: response.data.trade_suggestions || [],
          market_trends: response.data.market_trends || [],
          loading: false
        });
      } else {
        // If API fails, generate smart mock GPT insights
        generateSmartMockGPTInsights();
      }
    } catch (error) {
      console.error('Error fetching GPT insights:', error);
      // Generate smart mock GPT insights if API request fails
      generateSmartMockGPTInsights();
    }
  };

  const generateSmartMockGPTInsights = () => {
    // For now, we'll create intelligent mock data
    const market_sentiment = marketData.indices.reduce((acc, index) => acc + index.change, 0) > 0 ? 'bullish' : 'bearish';
    const market_volatility = Math.abs(marketData.indices.find(i => i.symbol === 'VIX')?.change || 0) > 2 ? 'high' : 'moderate';
    
    // Base factors that drive our mock analysis
    const tech_sentiment = marketData.sectors.find(s => s.name === 'Technology')?.change > 0;
    const financial_sector = marketData.sectors.find(s => s.name === 'Financials');
    const fed_policy = financial_sector?.change > 0; // Use financials as a proxy for Fed policy
    const inflation_trend = marketData.economic_indicators?.find(i => i.name === 'Inflation Rate')?.impact === 'negative';
    
    // Build strength metrics based on real sectors
    const sectors_strength = {};
    marketData.sectors.forEach(sector => {
      // Map the change (-5% to +5%) to a strength (0.2 to 0.9)
      sectors_strength[sector.name] = Math.max(0.2, Math.min(0.9, (sector.change + 5) / 10));
    });
    
    // Generate a coherent market summary based on the real market data
    const market_summary = `The market is currently showing ${market_sentiment} sentiment with ${market_volatility} volatility. 
    Major indices are ${market_sentiment === 'bullish' ? "trending upward, making new highs" : "experiencing downward pressure with key support levels being tested"} amid recent economic data.
    ${tech_sentiment ? "The technology sector is leading the market higher, with strong momentum in AI and semiconductor stocks." : "Technology stocks are underperforming, with concerns about valuation and growth prospects."} 
    ${fed_policy ? "The Federal Reserve's hawkish stance on interest rates is supporting financial stocks but pressuring rate-sensitive sectors." : "The Federal Reserve's dovish signals are boosting real estate and utilities sectors, while financials lag."}
    ${inflation_trend ? "Inflation data came in hotter than expected, which is contributing to market uncertainty." : "Inflation appears to be cooling, providing optimism for consumer stocks."}
    Technical indicators suggest a potential ${market_sentiment === 'bullish' ? "continuation of the current trend with potential for further upside" : "reversal in the near future if support levels hold"}. 
    The Fear & Greed Index is at ${marketData.fear_greed?.value || 50}, indicating a ${marketData.fear_greed?.rating || 'Neutral'} market stance.
    Breadth indicators show ${marketData.breadth?.advancing_stocks > marketData.breadth?.declining_stocks ? "healthy participation with more advancing than declining stocks" : "weak internals with declining stocks outnumbering advancers"}.`;
    
    // Generate trade suggestions based on our market scenario
    const top_sectors = Object.entries(sectors_strength).sort((a, b) => b[1] - a[1]).slice(0, 3);
    const bottom_sectors = Object.entries(sectors_strength).sort((a, b) => a[1] - b[1]).slice(0, 2);
    
    // Map sectors to representative stocks
    const sector_to_stocks = {
      'Technology': ['AAPL', 'MSFT', 'NVDA', 'AMD', 'CRM'],
      'Financials': ['JPM', 'BAC', 'GS', 'MS', 'V'],
      'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'NKE', 'SBUX'],
      'Energy': ['XOM', 'CVX', 'COP', 'PSX', 'EOG'],
      'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABT', 'MRK'],
      'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA'],
      'Industrials': ['HON', 'UNP', 'CAT', 'DE', 'GE'],
      'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP'],
      'Real Estate': ['AMT', 'PLD', 'CCI', 'SPG', 'EQIX'],
      'Materials': ['LIN', 'APD', 'ECL', 'NEM', 'FCX']
    };
    
    // Generate trade suggestions favoring top sectors (BUY) and fading bottom sectors (SELL)
    const trade_suggestions = [];
    
    // Add BUY recommendations from strong sectors
    top_sectors.forEach(([sector, strength]) => {
      const stock = sector_to_stocks[sector] ? sector_to_stocks[sector][Math.floor(Math.random() * sector_to_stocks[sector].length)] : 'SPY';
      const base_price = 100 + Math.random() * 900;  // Random base price between $100-$1000
      
      trade_suggestions.push({
        symbol: stock,
        action: 'BUY',
        confidence: Math.floor(strength * 100),
        reason: `Strong ${sector} sector momentum and favorable technical setup`,
        target_price: parseFloat((base_price * (1 + Math.random() * 0.15)).toFixed(2)),  // 0-15% upside
        stop_loss: parseFloat((base_price * (1 - Math.random() * 0.07)).toFixed(2))  // 0-7% downside protection
      });
    });
    
    // Add SELL recommendations from weak sectors
    bottom_sectors.forEach(([sector, strength]) => {
      const stock = sector_to_stocks[sector] ? sector_to_stocks[sector][Math.floor(Math.random() * sector_to_stocks[sector].length)] : 'SPY';
      const base_price = 100 + Math.random() * 900;
      
      trade_suggestions.push({
        symbol: stock,
        action: 'SELL',
        confidence: Math.floor((1-strength) * 100),
        reason: `Weak ${sector} sector performance and deteriorating technical indicators`,
        target_price: parseFloat((base_price * (1 - Math.random() * 0.12)).toFixed(2)),  // 0-12% downside target
        stop_loss: parseFloat((base_price * (1 + Math.random() * 0.05)).toFixed(2))  // 0-5% upside risk
      });
    });
    
    // Generate market trends based on our scenario
    // Use the Fear & Greed components if available
    const fear_greed_components = marketData.fear_greed?.components || {};
    const market_trends = [
      // Technology-related trend
      {
        trend: tech_sentiment ? 'AI and Semiconductor Growth' : 'Tech Sector Rotation',
        strength: tech_sentiment ? Math.floor((0.7 + Math.random() * 0.3) * 100) : Math.floor((0.4 + Math.random() * 0.3) * 100),
        duration: tech_sentiment ? 'Long-term' : 'Medium-term',
        affected_sectors: ['Technology', 'Communication Services', 'Consumer Discretionary'],
        analysis: tech_sentiment ? 'Continued strong demand for AI chips and infrastructure' 
                    : 'Rotation from high-growth tech to value-oriented technology subsectors'
      },
      // Federal Reserve policy trend
      {
        trend: fed_policy ? 'Federal Reserve Tightening Cycle' : 'Interest Rate Stabilization',
        strength: Math.floor((0.6 + Math.random() * 0.3) * 100),
        duration: 'Medium-term',
        affected_sectors: ['Financials', 'Real Estate', 'Utilities'],
        analysis: fed_policy ? 'Continued rate hikes affecting debt-heavy sectors'
                    : 'Potential pause in rate hikes supporting interest rate sensitive sectors'
      },
      // Inflation or economic trend based on actual economic indicators
      {
        trend: inflation_trend ? 'Inflationary Pressure' : 'Consumer Spending Resilience',
        strength: Math.floor((0.5 + Math.random() * 0.4) * 100),
        duration: 'Medium-term',
        affected_sectors: inflation_trend ? ['Energy', 'Materials', 'Consumer Staples'] 
                         : ['Consumer Discretionary', 'Communication Services', 'Financials'],
        analysis: inflation_trend ? 'Persistent inflation affecting profit margins across multiple sectors'
                   : 'Strong consumer balance sheets supporting discretionary spending despite economic concerns'
      }
    ];
    
    setGptInsights({
      market_summary,
      trade_suggestions,
      market_trends,
      loading: false
    });
  };

  const handleTimeframeChange = (event) => {
    setTimeframe(event.target.value);
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    
    // If switching to GPT Insights tab, make sure we load the insights
    if (newValue === 3) {
      fetchGPTInsights();
    }
  };

  const renderTabContent = () => {
    switch (tabValue) {
      case 0: // Market Overview
        return (
          <Grid container spacing={3}>
            {/* Market Indices */}
            <Grid item xs={12} lg={7}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Market Indices</Typography>
                <Grid container spacing={2}>
                  {Array.isArray(marketData.indices) && marketData.indices.map((index, i) => (
                    <Grid item xs={12} sm={6} md={4} key={i}>
                      <Card variant="outlined">
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <Box>
                              <Typography variant="subtitle1">{index.name}</Typography>
                              <Typography variant="h6">{index.price.toLocaleString()}</Typography>
                            </Box>
                            <Chip 
                              label={`${index.change > 0 ? '+' : ''}${index.change.toFixed(2)}%`}
                              color={index.change > 0 ? 'success' : 'error'}
                              size="small"
                              icon={index.change > 0 ? <TrendingUp /> : <TrendingDown />}
                            />
                          </Box>
                          <MockChart 
                            title={index.symbol} 
                            height={80} 
                            color={index.change > 0 ? '#4caf50' : '#f44336'} 
                          />
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
            
            {/* Fear & Greed */}
            <Grid item xs={12} md={6} lg={5}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Fear & Greed Index</Typography>
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <Typography variant="h2" color={
                    marketData.fear_greed?.value <= 25 ? 'error.dark' :
                    marketData.fear_greed?.value <= 45 ? 'error.main' :
                    marketData.fear_greed?.value <= 55 ? 'text.secondary' :
                    marketData.fear_greed?.value <= 75 ? 'success.main' : 'success.dark'
                  }>
                    {marketData.fear_greed?.value || 0}
                  </Typography>
                  <Chip 
                    label={marketData.fear_greed?.rating || 'Neutral'}
                    color={
                      marketData.fear_greed?.rating === 'Extreme Fear' ? 'error' :
                      marketData.fear_greed?.rating === 'Fear' ? 'warning' :
                      marketData.fear_greed?.rating === 'Neutral' ? 'default' :
                      marketData.fear_greed?.rating === 'Greed' ? 'success' : 'success'
                    }
                    sx={{ mb: 2 }}
                  />
                  
                  <Box sx={{ 
                    width: '100%', 
                    height: 30, 
                    bgcolor: 'background.paper', 
                    borderRadius: 1,
                    position: 'relative',
                    overflow: 'hidden',
                    mb: 3
                  }}>
                    <Box sx={{ 
                      width: '20%', 
                      height: '100%', 
                      bgcolor: 'error.dark',
                      position: 'absolute',
                      left: 0
                    }} />
                    <Box sx={{ 
                      width: '20%', 
                      height: '100%', 
                      bgcolor: 'error.main',
                      position: 'absolute',
                      left: '20%'
                    }} />
                    <Box sx={{ 
                      width: '20%', 
                      height: '100%', 
                      bgcolor: 'grey.400',
                      position: 'absolute',
                      left: '40%'
                    }} />
                    <Box sx={{ 
                      width: '20%', 
                      height: '100%', 
                      bgcolor: 'success.main',
                      position: 'absolute',
                      left: '60%'
                    }} />
                    <Box sx={{ 
                      width: '20%', 
                      height: '100%', 
                      bgcolor: 'success.dark',
                      position: 'absolute',
                      left: '80%'
                    }} />
                    <Box sx={{
                      position: 'absolute',
                      left: `${marketData.fear_greed?.value || 50}%`,
                      top: -10,
                      transform: 'translateX(-50%)',
                      width: 2,
                      height: 50,
                      bgcolor: 'text.primary'
                    }} />
                  </Box>
                  
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                    Updated {new Date().toLocaleDateString()}
                  </Typography>
                </Box>
                
                <Divider sx={{ mb: 2 }} />
                
                <Typography variant="subtitle2" sx={{ mb: 1 }}>Components</Typography>
                <Grid container spacing={2}>
                  {marketData.fear_greed?.components && Object.entries(marketData.fear_greed.components).map(([key, value], idx) => (
                    <Grid item xs={6} key={idx}>
                      <Box sx={{ 
                        p: 1, 
                        borderRadius: 1, 
                        bgcolor: 'background.paper',
                        border: 1,
                        borderColor: 'divider'
                      }}>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                          {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <Typography variant="subtitle2">{value}/100</Typography>
                          <Box sx={{ 
                            width: 10, 
                            height: 10, 
                            borderRadius: '50%',
                            bgcolor: value <= 25 ? 'error.dark' :
                                     value <= 45 ? 'error.main' :
                                     value <= 55 ? 'grey.400' :
                                     value <= 75 ? 'success.main' : 'success.dark'
                          }} />
                        </Box>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
            
            {/* Market Breadth */}
            <Grid item xs={12} md={6} lg={4}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Market Breadth</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText primary="Advance/Decline Ratio" secondary={marketData.breadth?.advance_decline_ratio || '-'} />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText 
                      primary="Advancers/Decliners" 
                      secondary={`${marketData.breadth?.advancing_stocks?.toLocaleString() || 0} / ${marketData.breadth?.declining_stocks?.toLocaleString() || 0}`} 
                    />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText 
                      primary="New Highs/Lows" 
                      secondary={`${marketData.breadth?.new_highs?.toLocaleString() || 0} / ${marketData.breadth?.new_lows?.toLocaleString() || 0}`} 
                    />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText primary="Stocks Above 200d MA" secondary={marketData.breadth?.stocks_above_200d_ma || '-'} />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText primary="Stocks Above 50d MA" secondary={marketData.breadth?.stocks_above_50d_ma || '-'} />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText primary="McClellan Oscillator" secondary={marketData.breadth?.mcclellan_oscillator || '-'} />
                  </ListItem>
                  <Divider component="li" />
                  <ListItem>
                    <ListItemText primary="Cumulative Volume" secondary={marketData.breadth?.cumulative_volume || '-'} />
                  </ListItem>
                </List>
              </Paper>
            </Grid>
            
            {/* Economic Indicators */}
            <Grid item xs={12} md={6} lg={4}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Economic Indicators</Typography>
                <List dense>
                  {Array.isArray(marketData.economic_indicators) && marketData.economic_indicators.map((indicator, idx) => (
                    <React.Fragment key={idx}>
                      <ListItem>
                        <ListItemText 
                          primary={indicator.name} 
                          secondary={`Current: ${indicator.value} | Previous: ${indicator.previous}`} 
                        />
                        {indicator.impact === 'positive' ? 
                          <Check color="success" /> : 
                          <Warning color="error" />
                        }
                      </ListItem>
                      {idx < marketData.economic_indicators.length - 1 && <Divider component="li" />}
                    </React.Fragment>
                  ))}
                </List>
              </Paper>
            </Grid>
            
            {/* Sector Performance */}
            <Grid item xs={12} lg={4}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Sector Performance</Typography>
                <List dense>
                  {Array.isArray(marketData.sectors) && marketData.sectors.map((sector, idx) => (
                    <React.Fragment key={idx}>
                      <ListItem>
                        <ListItemText primary={sector.name} />
                        <Chip 
                          label={`${sector.change > 0 ? '+' : ''}${sector.change.toFixed(2)}%`}
                          color={sector.change > 0 ? 'success' : 'error'}
                          size="small"
                          icon={sector.change > 0 ? <TrendingUp /> : <TrendingDown />}
                        />
                      </ListItem>
                      {idx < marketData.sectors.length - 1 && <Divider component="li" />}
                    </React.Fragment>
                  ))}
                </List>
              </Paper>
            </Grid>
          </Grid>
        );
        
      case 1: // Technical Analysis
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" sx={{ mb: 3 }}>S&P 500 Technical Analysis</Typography>
                <MockChart height={400} color="#2196f3" />
              </Paper>
            </Grid>
          </Grid>
        );
        
      case 2: // Sentiment Analysis
  return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" sx={{ mb: 3 }}>Market Sentiment Indicators</Typography>
                <Grid container spacing={2}>
                  {['Put/Call Ratio', 'VIX Term Structure', 'Smart Money Flow', 'Retail Sentiment', 'News Sentiment', 'Social Media Sentiment'].map((item, idx) => (
                    <Grid item xs={12} sm={6} md={4} key={idx}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="subtitle1">{item}</Typography>
                          <MockChart height={200} color={Math.random() > 0.5 ? '#4caf50' : '#f44336'} />
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        );
        
      case 3: // GPT Insights
        return (
          <Grid container spacing={3}>
            {/* GPT Market Summary */}
            <Grid item xs={12}>
              <Paper sx={{ p: 3, mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    GPT-Powered Market Summary
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<Refresh />}
                    size="small"
                    onClick={fetchGPTInsights}
                    disabled={gptInsights.loading}
                  >
                    Refresh Insights
                  </Button>
                </Box>
                {gptInsights.loading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                    {gptInsights.market_summary}
                  </Typography>
                )}
              </Paper>
            </Grid>
            
            {/* GPT Trade Suggestions */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  AI-Enhanced Trade Suggestions
                </Typography>
                {gptInsights.loading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <List>
                    {gptInsights.trade_suggestions.map((suggestion, idx) => (
                      <React.Fragment key={idx}>
                        <ListItem alignItems="flex-start">
                          <Box sx={{ width: '100%' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                              <Typography variant="h6">
                                {suggestion.symbol}
                              </Typography>
                              <Chip 
                                label={suggestion.action} 
                                color={suggestion.action === 'BUY' ? 'success' : 'error'} 
                                icon={suggestion.action === 'BUY' ? <TrendingUp /> : <TrendingDown />}
                              />
                            </Box>
                            
                            <Typography variant="body2" sx={{ mb: 1 }}>
                              {suggestion.reason}
                            </Typography>
                            
                            <Grid container spacing={2}>
                              <Grid item xs={4}>
                                <Typography variant="caption" color="text.secondary">Target</Typography>
                                <Typography variant="body2">${suggestion.target_price}</Typography>
                              </Grid>
                              <Grid item xs={4}>
                                <Typography variant="caption" color="text.secondary">Stop Loss</Typography>
                                <Typography variant="body2">${suggestion.stop_loss}</Typography>
                              </Grid>
                              <Grid item xs={4}>
                                <Typography variant="caption" color="text.secondary">Confidence</Typography>
                                <Typography variant="body2">{suggestion.confidence}%</Typography>
                              </Grid>
                            </Grid>
                          </Box>
                        </ListItem>
                        {idx < gptInsights.trade_suggestions.length - 1 && <Divider component="li" />}
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </Paper>
            </Grid>
            
            {/* GPT Market Trends */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  AI-Identified Market Trends
                </Typography>
                {gptInsights.loading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <List>
                    {gptInsights.market_trends.map((trend, idx) => (
                      <React.Fragment key={idx}>
                        <ListItem alignItems="flex-start">
                          <Box sx={{ width: '100%' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                              <Typography variant="subtitle1">
                                {trend.trend}
                              </Typography>
                              <Chip 
                                label={trend.duration} 
                                color={
                                  trend.duration === 'Long-term' ? 'primary' : 
                                  trend.duration === 'Medium-term' ? 'secondary' : 'default'
                                }
                                size="small"
                              />
                            </Box>
                            
                            <Typography variant="body2" sx={{ mb: 1 }}>
                              {trend.analysis}
                            </Typography>
                            
                            <Box sx={{ mb: 1 }}>
                              <Typography variant="caption" color="text.secondary">
                                Affected Sectors:
                              </Typography>
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                                {trend.affected_sectors.map((sector, i) => (
                                  <Chip key={i} label={sector} size="small" variant="outlined" />
                                ))}
                              </Box>
                            </Box>
                            
                            <Box>
                              <Typography variant="caption" color="text.secondary">
                                Trend Strength: {trend.strength}%
                              </Typography>
                              <LinearProgress 
                                variant="determinate" 
                                value={trend.strength} 
                                color={
                                  trend.strength >= 80 ? "success" : 
                                  trend.strength >= 60 ? "info" : 
                                  trend.strength >= 40 ? "warning" : "error"
                                }
                                sx={{ height: 6, borderRadius: 3, mt: 0.5 }}
                              />
                            </Box>
                          </Box>
                        </ListItem>
                        {idx < gptInsights.market_trends.length - 1 && <Divider component="li" />}
                      </React.Fragment>
                    ))}
                  </List>
                )}
          </Paper>
        </Grid>
      </Grid>
        );
        
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3, minHeight: '100vh' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Market Analysis</Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl sx={{ minWidth: 120 }} size="small">
            <InputLabel>Timeframe</InputLabel>
            <Select
              value={timeframe}
              label="Timeframe"
              onChange={handleTimeframeChange}
            >
              {timeframes.map(tf => (
                <MenuItem key={tf.value} value={tf.value}>{tf.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Button
            variant="contained"
            startIcon={<Refresh />}
            onClick={fetchMarketAnalysisData}
          >
            Refresh
          </Button>
        </Box>
      </Box>
      
      {/* Tabs Navigation */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Market Overview" icon={<ShowChart />} iconPosition="start" />
          <Tab label="Technical Analysis" />
          <Tab label="Sentiment Analysis" />
          <Tab label="GPT Insights" />
        </Tabs>
      </Paper>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      ) : (
        renderTabContent()
      )}
    </Box>
  );
};

export default MarketAnalysis; 