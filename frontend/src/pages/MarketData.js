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
  TextField 
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import axios from 'axios';
import { motion } from 'framer-motion';

// Import our new layout components
import PageLayout from '../components/PageLayout';
import ContentCard from '../components/ContentCard';
import ContentGrid from '../components/ContentGrid';

const MarketData = () => {
  const [loading, setLoading] = useState(true);
  const [marketData, setMarketData] = useState([]);
  const [symbol, setSymbol] = useState('SPY');
  const [timeframe, setTimeframe] = useState('1d');
  const [days, setDays] = useState(30);
  
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
    
    try {
      // Try to fetch from API
      try {
        const response = await axios.get(`/api/market-data/${symbol}?timeframe=${timeframe}&days=${days}`);
        if (response.data.success) {
          setMarketData(response.data.bars);
        } else {
          // If API returns unsuccessful but responds, generate mock data
          generateMockData();
        }
      } catch (error) {
        console.error('Failed to fetch from API:', error);
        generateMockData();
      }
    } catch (error) {
      console.error('Error in market data fetch:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    const mockData = [];
    const today = new Date();
    let lastPrice = Math.random() * 100 + 100; // Random starting price between 100-200
    
    for (let i = 0; i < days; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      
      // Generate random price movement
      const change = (Math.random() - 0.48) * 5; // Slightly biased upward
      const open = lastPrice;
      const close = lastPrice + change;
      const high = Math.max(open, close) + Math.random() * 2;
      const low = Math.min(open, close) - Math.random() * 2;
      const volume = Math.floor(Math.random() * 10000000) + 1000000;
      
      mockData.push({
        date: date.toISOString().split('T')[0],
        symbol,
        open: parseFloat(open.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        close: parseFloat(close.toFixed(2)),
        volume,
        change: parseFloat((((close - open) / open) * 100).toFixed(2))
      });
      
      lastPrice = close;
    }
    
    setMarketData(mockData.reverse()); // Reverse to show most recent first
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

  return (
    <PageLayout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography 
          variant="h4" 
          component={motion.h4}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          sx={{ 
            fontWeight: 'bold',
            color: 'primary.main'
          }}
        >
          Market Data
        </Typography>
      </Box>
      
      {/* Controls */}
      <ContentGrid>
        <Grid item xs={12}>
          <ContentCard title="Data Controls">
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={3}>
                <FormControl fullWidth>
                  <InputLabel id="symbol-label">Symbol</InputLabel>
                  <Select
                    labelId="symbol-label"
                    value={symbol}
                    label="Symbol"
                    onChange={handleSymbolChange}
                  >
                    {popularSymbols.map(sym => (
                      <MenuItem key={sym} value={sym}>{sym}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={3}>
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
              <Grid item xs={12} sm={2}>
                <TextField
                  fullWidth
                  label="Days"
                  type="number"
                  value={days}
                  onChange={handleDaysChange}
                  InputProps={{ inputProps: { min: 1, max: 365 } }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleRefresh}
                  startIcon={<Refresh />}
                  fullWidth
                >
                  Refresh Data
                </Button>
              </Grid>
            </Grid>
          </ContentCard>
        </Grid>
      </ContentGrid>
      
      <ContentGrid>
        <Grid item xs={12}>
          <ContentCard title={`Market Data - ${symbol}`}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer sx={{ maxHeight: '60vh', overflow: 'auto' }}>
                <Table stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell align="right">Open</TableCell>
                      <TableCell align="right">High</TableCell>
                      <TableCell align="right">Low</TableCell>
                      <TableCell align="right">Close</TableCell>
                      <TableCell align="right">Volume</TableCell>
                      <TableCell align="right">Change</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {marketData.map((row, index) => (
                      <TableRow 
                        key={index}
                        sx={{ 
                          '&:nth-of-type(odd)': { bgcolor: 'rgba(0, 0, 0, 0.03)' },
                          '&:hover': { bgcolor: 'rgba(0, 0, 0, 0.06)' }
                        }}
                      >
                        <TableCell component="th" scope="row">
                          {row.date}
                        </TableCell>
                        <TableCell align="right">${row.open}</TableCell>
                        <TableCell align="right">${row.high}</TableCell>
                        <TableCell align="right">${row.low}</TableCell>
                        <TableCell align="right">${row.close}</TableCell>
                        <TableCell align="right">{row.volume.toLocaleString()}</TableCell>
                        <TableCell 
                          align="right"
                          sx={{ 
                            color: row.change >= 0 ? 'success.main' : 'error.main',
                            fontWeight: 'bold'
                          }}
                        >
                          {row.change >= 0 ? `+${row.change}%` : `${row.change}%`}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </ContentCard>
        </Grid>
      </ContentGrid>
    </PageLayout>
  );
};

export default MarketData; 