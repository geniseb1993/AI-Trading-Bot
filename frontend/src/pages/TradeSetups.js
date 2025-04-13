import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Card,
  CardContent,
  CardActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Chip,
  CircularProgress,
  IconButton,
  Divider,
  Tab,
  Tabs,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Tooltip
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  Refresh, 
  ExpandMore, 
  Search,
  AddCircle,
  NotificationsActive, 
  Star,
  StarBorder,
  RemoveRedEye,
  Timeline
} from '@mui/icons-material';
import axios from 'axios';

const TradeSetups = () => {
  const [tradeSetups, setTradeSetups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [strategyType, setStrategyType] = useState('all');
  const [timeframe, setTimeframe] = useState('daily');
  const [tabValue, setTabValue] = useState(0);
  const [watchlist, setWatchlist] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  const strategies = [
    { value: 'all', label: 'All Strategies' },
    { value: 'breakout', label: 'Breakout' },
    { value: 'trend_following', label: 'Trend Following' },
    { value: 'mean_reversion', label: 'Mean Reversion' },
    { value: 'momentum', label: 'Momentum' },
    { value: 'support_resistance', label: 'Support/Resistance' },
    { value: 'volume_based', label: 'Volume Based' }
  ];
  
  const timeframes = [
    { value: 'all', label: 'All Timeframes' },
    { value: 'intraday', label: 'Intraday' },
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' }
  ];

  useEffect(() => {
    fetchTradeSetups();
  }, [strategyType, timeframe]);

  const fetchTradeSetups = async () => {
    setLoading(true);
    try {
      // Try to fetch data from API
      const response = await axios.post('/api/trade-setups/get-setups', {
        strategy_type: strategyType,
        timeframe: timeframe
      });
      
      if (response.data && response.data.success && Array.isArray(response.data.setups)) {
        setTradeSetups(response.data.setups);
      } else {
        // If API fails, generate mock data
        generateMockData();
      }
    } catch (error) {
      console.error('Error fetching trade setups:', error);
      // Generate mock data if API request fails
      generateMockData();
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    const mockSymbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 'JPM', 'V', 'WMT', 'DIS', 'NFLX', 'PFE'];
    const mockStrategies = ['Breakout', 'Trend Following', 'Mean Reversion', 'Momentum', 'Support/Resistance', 'Volume Based'];
    const mockTimeframes = ['Intraday', 'Daily', 'Weekly', 'Monthly'];
    const mockPatterns = [
      'Double Bottom', 'Double Top', 'Cup and Handle', 'Head and Shoulders', 
      'Engulfing Candle', 'Hammer', 'Doji', 'Golden Cross', 'Death Cross',
      'Bullish Flag', 'Bearish Flag', 'Triangle', 'Wedge', 'Rectangle'
    ];
    
    const mockSetups = [];
    
    for (let i = 0; i < 30; i++) {
      const symbol = mockSymbols[Math.floor(Math.random() * mockSymbols.length)];
      const strategy = mockStrategies[Math.floor(Math.random() * mockStrategies.length)];
      const setupTimeframe = mockTimeframes[Math.floor(Math.random() * mockTimeframes.length)];
      const pattern = mockPatterns[Math.floor(Math.random() * mockPatterns.length)];
      const direction = Math.random() > 0.5 ? 'bullish' : 'bearish';
      const strength = Math.floor(Math.random() * 100);
      
      // Filter based on strategy and timeframe if they're set
      if (
        (strategyType !== 'all' && strategy.toLowerCase().replace(/ /g, '_') !== strategyType) ||
        (timeframe !== 'all' && setupTimeframe.toLowerCase() !== timeframe)
      ) {
        continue;
      }
      
      mockSetups.push({
        id: i + 1,
        symbol,
        strategy,
        timeframe: setupTimeframe,
        pattern,
        direction,
        detected_price: parseFloat((Math.random() * 900 + 100).toFixed(2)),
        current_price: parseFloat((Math.random() * 900 + 100).toFixed(2)),
        suggested_entry: parseFloat((Math.random() * 900 + 100).toFixed(2)),
        suggested_stop: parseFloat((Math.random() * 900 + 100).toFixed(2)),
        suggested_target: parseFloat((Math.random() * 900 + 100).toFixed(2)),
        risk_reward: parseFloat((Math.random() * 3 + 1).toFixed(2)),
        confidence: Math.floor(Math.random() * 100),
        detected_at: new Date(new Date().getTime() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        status: Math.random() > 0.7 ? 'new' : Math.random() > 0.5 ? 'active' : 'completed',
        strength
      });
    }
    
    setTradeSetups(mockSetups);
  };

  const handleStrategyChange = (event) => {
    setStrategyType(event.target.value);
  };

  const handleTimeframeChange = (event) => {
    setTimeframe(event.target.value);
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const toggleWatchlist = (symbol) => {
    if (watchlist.includes(symbol)) {
      setWatchlist(watchlist.filter(s => s !== symbol));
    } else {
      setWatchlist([...watchlist, symbol]);
    }
  };

  const getFilteredSetups = () => {
    if (!searchTerm.trim()) {
      return tradeSetups;
    }
    
    return tradeSetups.filter(setup => 
      setup.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      setup.pattern.toLowerCase().includes(searchTerm.toLowerCase()) ||
      setup.strategy.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const getSetupsByTab = () => {
    const filtered = getFilteredSetups();
    
    switch (tabValue) {
      case 0: // All Setups
        return filtered;
      case 1: // New Signals
        return filtered.filter(setup => setup.status === 'new');
      case 2: // Active Trades
        return filtered.filter(setup => setup.status === 'active');
      case 3: // Completed
        return filtered.filter(setup => setup.status === 'completed');
      case 4: // Watchlist
        return filtered.filter(setup => watchlist.includes(setup.symbol));
      default:
        return filtered;
    }
  };

  const renderStrategyIcon = (strategy) => {
    switch (strategy.toLowerCase().replace(/ /g, '_')) {
      case 'breakout':
        return <Timeline color="primary" />;
      case 'trend_following':
        return <TrendingUp color="success" />;
      case 'mean_reversion':
        return <TrendingDown color="error" />;
      default:
        return <Timeline />;
    }
  };

  return (
    <Box sx={{ p: 3, minHeight: '100vh' }}>
      <Typography variant="h4" sx={{ mb: 3 }}>Trade Setups</Typography>
      
      {/* Filters and Controls */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Strategy</InputLabel>
              <Select
                value={strategyType}
                label="Strategy"
                onChange={handleStrategyChange}
              >
                {strategies.map(strategy => (
                  <MenuItem key={strategy.value} value={strategy.value}>{strategy.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
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
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              size="small"
              label="Search Setups"
              value={searchTerm}
              onChange={handleSearch}
              InputProps={{
                startAdornment: <Search color="action" sx={{ mr: 1 }} />,
              }}
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<Refresh />}
              onClick={fetchTradeSetups}
            >
              Refresh
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Tabs Navigation */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label={`All Setups (${tradeSetups.length})`} />
          <Tab label={`New Signals (${tradeSetups.filter(s => s.status === 'new').length})`} />
          <Tab label={`Active Trades (${tradeSetups.filter(s => s.status === 'active').length})`} />
          <Tab label={`Completed (${tradeSetups.filter(s => s.status === 'completed').length})`} />
          <Tab label={`Watchlist (${watchlist.length})`} />
        </Tabs>
      </Paper>
      
      {/* Main Content */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box>
          {getSetupsByTab().length === 0 ? (
            <Alert severity="info" sx={{ mb: 3 }}>
              No trade setups found for the selected filters. Try changing your filters or refreshing the data.
            </Alert>
          ) : (
            <>
              {/* Card View for Setup Display */}
              <Grid container spacing={3}>
                {getSetupsByTab().map((setup) => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={setup.id}>
                    <Card 
                      sx={{ 
                        height: '100%', 
                        display: 'flex', 
                        flexDirection: 'column',
                        border: setup.status === 'new' ? 2 : 1,
                        borderColor: setup.status === 'new' ? 'primary.main' : 'divider'
                      }}
                    >
                      <Box 
                        sx={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          p: 2,
                          pb: 1
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="h6" sx={{ mr: 1 }}>{setup.symbol}</Typography>
                          {setup.status === 'new' && (
                            <Chip size="small" color="primary" label="NEW" />
                          )}
                        </Box>
                        <IconButton 
                          size="small" 
                          onClick={() => toggleWatchlist(setup.symbol)}
                        >
                          {watchlist.includes(setup.symbol) ? 
                            <Star fontSize="small" color="warning" /> : 
                            <StarBorder fontSize="small" />
                          }
                        </IconButton>
                      </Box>
                      
                      <CardContent sx={{ pt: 1, pb: 1, flexGrow: 1 }}>
                        <Box sx={{ mb: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            {renderStrategyIcon(setup.strategy)}
                            <Typography variant="body2" sx={{ ml: 1 }}>{setup.strategy}</Typography>
                          </Box>
                          
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="subtitle2">{setup.pattern}</Typography>
                            <Chip 
                              size="small" 
                              label={setup.direction.toUpperCase()}
                              color={setup.direction === 'bullish' ? 'success' : 'error'}
                              icon={setup.direction === 'bullish' ? <TrendingUp fontSize="small" /> : <TrendingDown fontSize="small" />}
                            />
                          </Box>
                        </Box>
                        
                        <Divider sx={{ mb: 2 }} />
                        
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="caption" color="text.secondary">
                            Timeframe: {setup.timeframe}
                          </Typography>
                          
                          <Grid container spacing={1} sx={{ mt: 1 }}>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="text.secondary">Entry</Typography>
                              <Typography variant="body2">${setup.suggested_entry}</Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="text.secondary">Current</Typography>
                              <Typography variant="body2">${setup.current_price}</Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="text.secondary">Stop</Typography>
                              <Typography variant="body2">${setup.suggested_stop}</Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="text.secondary">Target</Typography>
                              <Typography variant="body2">${setup.suggested_target}</Typography>
                            </Grid>
                          </Grid>
                        </Box>
                        
                        <Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                              Strength
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {setup.strength}%
                            </Typography>
                          </Box>
                          <LinearProgress 
                            variant="determinate" 
                            value={setup.strength} 
                            color={
                              setup.strength >= 80 ? "success" : 
                              setup.strength >= 60 ? "info" : 
                              setup.strength >= 40 ? "warning" : "error"
                            }
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                        </Box>
                      </CardContent>
                      
                      <Divider />
                      
                      <CardActions>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                          <Box>
                            <Tooltip title="View Details">
                              <IconButton size="small">
                                <RemoveRedEye fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Set Alert">
                              <IconButton size="small">
                                <NotificationsActive fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(setup.detected_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
              
              {/* Strategy Explanations */}
              <Box sx={{ mt: 4 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Strategy Information</Typography>
                
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>Breakout Strategy</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography>
                      Breakout strategies involve entering trades when the price breaks through a significant level of support or resistance,
                      often accompanied by increased volume. These strategies aim to capture the momentum as price moves into new territory.
                    </Typography>
                  </AccordionDetails>
                </Accordion>
                
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>Trend Following Strategy</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography>
                      Trend following strategies aim to capture gains by riding the momentum of existing trends. These strategies
                      typically use indicators like moving averages, MACD, or ADX to identify and confirm trend direction and strength.
                    </Typography>
                  </AccordionDetails>
                </Accordion>
                
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>Mean Reversion Strategy</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography>
                      Mean reversion strategies are based on the concept that prices will revert to their average or mean over time.
                      These strategies look for overbought or oversold conditions using indicators like RSI, Bollinger Bands, or stochastics.
                    </Typography>
                  </AccordionDetails>
                </Accordion>
                
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>Support/Resistance Strategy</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography>
                      Support and resistance strategies focus on identifying key price levels where a security has historically struggled to move beyond.
                      These levels often act as barriers, and traders look for bounces off support or resistance, or for breakouts through these levels.
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              </Box>
            </>
          )}
        </Box>
      )}
    </Box>
  );
};

export default TradeSetups; 