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
  Tab
} from '@mui/material';
import { Refresh, ShowChart, Inventory, TableChart } from '@mui/icons-material';
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
  const [viewMode, setViewMode] = useState('chart'); // 'chart' or 'table'
  const [error, setError] = useState(null); // Add error state
  const [isRealData, setIsRealData] = useState(false);
  const [dataSource, setDataSource] = useState('unknown');
  
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
    setError(null); // Reset error state
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/market-data/${symbol}?timeframe=${timeframe}&days=${days}`);
      if (response.data && response.data.success) {
        console.log('Received market data:', response.data);
        setMarketData(response.data.bars || []);
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
          padding: '12px 20px',
          backgroundColor: alpha(theme.palette.primary.main, 0.1),
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`
        }}
      />
      <CardContent>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
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
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
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
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              label="Days"
              type="number"
              value={days}
              onChange={handleDaysChange}
              InputProps={{ inputProps: { min: 1, max: 365 } }}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleRefresh}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Refresh />}
              disabled={loading}
              fullWidth
              sx={{ height: '56px', fontFamily: 'Orbitron' }}
            >
              Refresh Data
            </Button>
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 2, borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`, pt: 1, display: 'flex', justifyContent: 'center' }}>
          <Tabs
            value={viewMode}
            onChange={handleViewModeChange}
            aria-label="view mode tabs"
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab icon={<ShowChart />} value="chart" label="Chart View" />
            <Tab icon={<TableChart />} value="table" label="Table View" />
          </Tabs>
        </Box>
      </CardContent>
    </Card>
  );

  // Card for the chart view
  const ChartCard = () => (
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
            <ShowChart fontSize="small" />
            {symbol} Chart
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
        ) : viewMode === 'chart' ? (
          <Box sx={{ height: '100%', width: '100%' }}>
            {/* Use TradingView chart for chart view */}
            <TradingViewWidget 
              symbol={formatSymbolForTradingView(symbol)}
              interval={getTradingViewInterval()}
              height="100%"
              width="100%"
              key={`${symbol}_${timeframe}`} // Add key prop to force remount on symbol/timeframe change
            />
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
  );

  // Helper function to format symbols for TradingView
  const formatSymbolForTradingView = (symbol) => {
    // Special handling for popular symbols
    const symbolMapping = {
      'SPY': 'AMEX:SPY',
      'QQQ': 'NASDAQ:QQQ',
      'AAPL': 'NASDAQ:AAPL',
      'MSFT': 'NASDAQ:MSFT',
      'TSLA': 'NASDAQ:TSLA',
      'NVDA': 'NASDAQ:NVDA',
      'AMD': 'NASDAQ:AMD',
      'AMZN': 'NASDAQ:AMZN',
      'GOOGL': 'NASDAQ:GOOGL',
      'META': 'NASDAQ:META'
    };
    
    return symbolMapping[symbol] || `NASDAQ:${symbol}`;
  };

  return (
    <PageLayout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
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
            gap: 1
          }}
        >
          <ShowChart fontSize="large" />
          Market Data Explorer
        </Typography>
      </Box>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 140px)' }}>
        <ControlsCard />
        <ChartCard />
      </Box>
    </PageLayout>
  );
};

export default MarketData; 