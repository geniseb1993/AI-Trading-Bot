import React, { useState, useEffect } from 'react';
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
  Avatar
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

// Import components
import TradingChart from '../components/TradingChart';
import InstitutionalFlowTable from '../components/InstitutionalFlowTable';
import CooldownTimer from '../components/execution_model/CooldownTimer';
// TradeJournalTable will be implemented later

const LiveMarket = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [timeframe, setTimeframe] = useState('7'); // Set to string "7" for 7 days
  const [tabValue, setTabValue] = useState(0);
  const [apiConnected, setApiConnected] = useState(false);
  const [cooldownStatus, setCooldownStatus] = useState(null);
  const [tradeSetups, setTradeSetups] = useState({});
  
  // Check API connection status on component mount
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        // Simulate API status check (replace with actual API check)
        setTimeout(() => {
          setApiConnected(false); // For now, set to false to use demo data
        }, 1000);
      } catch (error) {
        console.error("Failed to check API status:", error);
        setApiConnected(false);
      }
    };
    
    checkApiStatus();
    fetchCooldownStatus();
    fetchTradeSetups();
  }, []);
  
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
  
  const handleRefresh = () => {
    setLoading(true);
    fetchCooldownStatus();
    fetchTradeSetups();
    // Simulate API fetch
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

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

  // Create a card for trade setup
  const TradeSetupCard = ({ symbol }) => {
    const setup = tradeSetups[symbol];
    
    if (!setup) {
      return (
        <Paper 
          sx={{ 
            p: 2, 
            backgroundColor: alpha(theme.palette.background.paper, 0.5),
            borderRadius: 2,
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center'
          }}
        >
          <CircularProgress size={24} />
          <Typography variant="body2" sx={{ mt: 2 }}>
            Loading {symbol} data...
          </Typography>
        </Paper>
      );
    }
    
    const isBullish = setup.direction === 'long';
    const confidenceColor = setup.confidence > 80 ? 'success' : 
                          setup.confidence > 50 ? 'primary' : 'warning';
    
    return (
      <Paper 
        sx={{ 
          p: 2, 
          backgroundColor: alpha(
            isBullish ? theme.palette.success.main : theme.palette.error.main, 
            0.05
          ),
          borderRadius: 2,
          height: '100%',
          border: `1px solid ${alpha(
            isBullish ? theme.palette.success.main : theme.palette.error.main, 
            0.2
          )}`,
          '&:hover': {
            backgroundColor: alpha(
              isBullish ? theme.palette.success.main : theme.palette.error.main, 
              0.1
            ),
            boxShadow: `0 0 15px ${alpha(
              isBullish ? theme.palette.success.main : theme.palette.error.main, 
              0.2
            )}`
          },
          transition: 'all 0.3s ease'
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography 
            variant="h6" 
            sx={{ 
              fontFamily: 'Orbitron',
              color: isBullish ? theme.palette.success.main : theme.palette.error.main 
            }}
          >
            {symbol}
          </Typography>
          <Chip 
            label={`${setup.direction.toUpperCase()}`}
            size="small"
            color={isBullish ? "success" : "error"}
            icon={isBullish ? <TrendingUpIcon /> : <TrendingDownIcon />}
          />
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography 
            variant="h5" 
            sx={{ 
              fontFamily: 'Orbitron',
              fontWeight: 'bold'
            }}
          >
            ${setup.price.toFixed(2)}
          </Typography>
          <Chip 
            size="small"
            label={`${setup.confidence}% AI confidence`}
            color={confidenceColor}
            sx={{ ml: 1 }}
          />
        </Box>
        
        <Divider sx={{ my: 1, opacity: 0.2 }} />
        
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AccessTimeIcon fontSize="small" sx={{ mr: 0.5, opacity: 0.7 }} />
            <Typography variant="body2">TF: {setup.timeframe}</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <PriceCheckIcon fontSize="small" sx={{ mr: 0.5, opacity: 0.7 }} />
            <Typography variant="body2">Entry: ${setup.entry}</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography 
              variant="body2" 
              color="error"
              sx={{ display: 'flex', alignItems: 'center' }}
            >
              SL: ${setup.stopLoss}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography 
              variant="body2" 
              color="success"
              sx={{ display: 'flex', alignItems: 'center' }}
            >
              TP: ${setup.takeProfit}
            </Typography>
          </Box>
        </Box>
        
        <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
          AI Signals:
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          {setup.signals.map((signal, index) => (
            <Chip 
              key={index}
              size="small"
              label={signal.name}
              color={signal.bullish ? "success" : "error"}
              variant="outlined"
              sx={{ fontSize: '0.7rem' }}
            />
          ))}
        </Box>
      </Paper>
    );
  };

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
                title="Market Overview" 
                titleTypographyProps={{ 
                  fontFamily: 'Orbitron',
                  fontSize: '1.1rem'
                }} 
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent sx={{ p: 0, height: 'calc(100% - 64px)' }}>
                <TradingChart 
                  selectedSymbol={selectedSymbol} 
                  timeframe={getTimeframeInDays()} 
                  apiConnected={apiConnected} 
                />
              </CardContent>
            </Card>
          )}
          
          {tabValue === 1 && (
            <Card 
              sx={{ 
                minHeight: '600px', 
                backgroundColor: alpha(theme.palette.background.paper, 0.7),
                backdropFilter: 'blur(10px)',
                borderRadius: 2
              }}
            >
              <CardHeader 
                title="AI Trade Setups" 
                titleTypographyProps={{ 
                  fontFamily: 'Orbitron',
                  fontSize: '1.1rem'
                }} 
                sx={{ borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}
              />
              <CardContent>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={4}>
                    <CooldownTimer cooldownStatus={cooldownStatus} onRefresh={fetchCooldownStatus} />
                  </Grid>
                  
                  {['SPY', 'QQQ', 'AAPL'].map((symbol) => (
                    <Grid item xs={12} md={4} key={symbol}>
                      <TradeSetupCard symbol={symbol} />
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
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