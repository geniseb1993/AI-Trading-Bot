import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Alert,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  Refresh as RefreshIcon,
  Add as AddIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import axios from 'axios';

const MarketDataViewer = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeSource, setActiveSource] = useState('');
  const [dataType, setDataType] = useState('bars');
  const [symbols, setSymbols] = useState(['SPY']);
  const [newSymbol, setNewSymbol] = useState('');
  const [marketData, setMarketData] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(null);
  const [timeframe, setTimeframe] = useState('1Min');

  useEffect(() => {
    // Fetch the active market data source
    const fetchActiveSource = async () => {
      try {
        const response = await axios.get('/api/market-data/sources');
        if (response.data.success) {
          setActiveSource(response.data.active_source);
        } else {
          setError('Failed to fetch active market data source: ' + response.data.error);
        }
      } catch (err) {
        setError('Error fetching active market data source: ' + (err.response?.data?.error || err.message));
      }
    };

    fetchActiveSource();
    fetchMarketData();

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchMarketData();
      }, 5000); // Refresh every 5 seconds
      setRefreshInterval(interval);
    } else if (refreshInterval) {
      clearInterval(refreshInterval);
      setRefreshInterval(null);
    }

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [autoRefresh, symbols, dataType, timeframe]);

  const fetchMarketData = async () => {
    if (symbols.length === 0) return;
    
    try {
      setLoading(true);
      const response = await axios.post('/api/market-data/get-data', {
        symbols,
        data_type: dataType,
        timeframe
      });
      
      if (response.data.success) {
        setMarketData(response.data);
      } else {
        setError('Failed to fetch market data: ' + response.data.error);
      }
    } catch (err) {
      setError('Error fetching market data: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const addSymbol = () => {
    if (newSymbol && !symbols.includes(newSymbol.toUpperCase())) {
      setSymbols([...symbols, newSymbol.toUpperCase()]);
      setNewSymbol('');
    }
  };

  const removeSymbol = (symbol) => {
    setSymbols(symbols.filter(s => s !== symbol));
  };

  const renderBarsData = () => {
    if (!marketData || !marketData.data || Object.keys(marketData.data).length === 0) {
      return <Typography>No data available</Typography>;
    }

    // Extract bars data structure
    const data = marketData.data;
    
    // Handle different possible data structures
    let bars = [];
    
    if (Array.isArray(data)) {
      // If it's an array of bars
      bars = data;
    } else if (data.bars) {
      // If it has a 'bars' property (Alpaca structure)
      const barsData = data.bars;
      Object.entries(barsData).forEach(([symbol, symbolBars]) => {
        if (Array.isArray(symbolBars)) {
          symbolBars.forEach(bar => {
            bars.push({
              symbol,
              ...bar
            });
          });
        }
      });
    } else {
      // Try to extract data from a generic structure
      Object.entries(data).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach(item => {
            if (item.open !== undefined && item.close !== undefined) {
              bars.push({
                symbol: key,
                ...item
              });
            }
          });
        }
      });
    }

    if (bars.length === 0) {
      return <Typography>No bars data available in the response</Typography>;
    }

    return (
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Open</TableCell>
              <TableCell>High</TableCell>
              <TableCell>Low</TableCell>
              <TableCell>Close</TableCell>
              <TableCell>Volume</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {bars.slice(0, 20).map((bar, index) => (
              <TableRow key={index}>
                <TableCell>{bar.symbol}</TableCell>
                <TableCell>{bar.t || bar.timestamp || bar.time || 'N/A'}</TableCell>
                <TableCell>{Number(bar.o || bar.open).toFixed(2)}</TableCell>
                <TableCell>{Number(bar.h || bar.high).toFixed(2)}</TableCell>
                <TableCell>{Number(bar.l || bar.low).toFixed(2)}</TableCell>
                <TableCell>{Number(bar.c || bar.close).toFixed(2)}</TableCell>
                <TableCell>{bar.v || bar.volume || 'N/A'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {bars.length > 20 && (
          <Typography variant="caption" sx={{ mt: 1, display: 'block', textAlign: 'right' }}>
            Showing 20 of {bars.length} rows
          </Typography>
        )}
      </TableContainer>
    );
  };

  const renderQuotesData = () => {
    if (!marketData || !marketData.data || Object.keys(marketData.data).length === 0) {
      return <Typography>No data available</Typography>;
    }

    // Extract quotes data structure
    const data = marketData.data;
    
    // Handle different possible data structures
    let quotes = [];
    
    if (Array.isArray(data)) {
      // If it's an array of quotes
      quotes = data;
    } else if (data.quotes) {
      // If it has a 'quotes' property (Alpaca structure)
      const quotesData = data.quotes;
      Object.entries(quotesData).forEach(([symbol, quote]) => {
        quotes.push({
          symbol,
          ...quote
        });
      });
    } else {
      // Try to extract data from a generic structure
      Object.entries(data).forEach(([key, value]) => {
        if (value.ask_price !== undefined || value.bid_price !== undefined) {
          quotes.push({
            symbol: key,
            ...value
          });
        }
      });
    }

    if (quotes.length === 0) {
      return <Typography>No quotes data available in the response</Typography>;
    }

    return (
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Bid Price</TableCell>
              <TableCell>Bid Size</TableCell>
              <TableCell>Ask Price</TableCell>
              <TableCell>Ask Size</TableCell>
              <TableCell>Time</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {quotes.map((quote, index) => (
              <TableRow key={index}>
                <TableCell>{quote.symbol}</TableCell>
                <TableCell>{Number(quote.bp || quote.bid_price || quote.bid || 0).toFixed(2)}</TableCell>
                <TableCell>{quote.bs || quote.bid_size || 'N/A'}</TableCell>
                <TableCell>{Number(quote.ap || quote.ask_price || quote.ask || 0).toFixed(2)}</TableCell>
                <TableCell>{quote.as || quote.ask_size || 'N/A'}</TableCell>
                <TableCell>{quote.t || quote.timestamp || quote.time || 'N/A'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderTradesData = () => {
    if (!marketData || !marketData.data || Object.keys(marketData.data).length === 0) {
      return <Typography>No data available</Typography>;
    }

    // Extract trades data structure
    const data = marketData.data;
    
    // Handle different possible data structures
    let trades = [];
    
    if (Array.isArray(data)) {
      // If it's an array of trades
      trades = data;
    } else if (data.trades) {
      // If it has a 'trades' property (Alpaca structure)
      const tradesData = data.trades;
      Object.entries(tradesData).forEach(([symbol, trade]) => {
        trades.push({
          symbol,
          ...trade
        });
      });
    } else {
      // Try to extract data from a generic structure
      Object.entries(data).forEach(([key, value]) => {
        if (value.price !== undefined || value.size !== undefined) {
          trades.push({
            symbol: key,
            ...value
          });
        }
      });
    }

    if (trades.length === 0) {
      return <Typography>No trades data available in the response</Typography>;
    }

    return (
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Price</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Exchange</TableCell>
              <TableCell>Time</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {trades.map((trade, index) => (
              <TableRow key={index}>
                <TableCell>{trade.symbol}</TableCell>
                <TableCell>{Number(trade.p || trade.price).toFixed(2)}</TableCell>
                <TableCell>{trade.s || trade.size || 'N/A'}</TableCell>
                <TableCell>{trade.x || trade.exchange || 'N/A'}</TableCell>
                <TableCell>{trade.t || trade.timestamp || trade.time || 'N/A'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderMarketData = () => {
    if (!marketData) {
      return <Typography>No data available</Typography>;
    }

    switch (dataType) {
      case 'bars':
        return renderBarsData();
      case 'quotes':
        return renderQuotesData();
      case 'trades':
        return renderTradesData();
      default:
        return <Typography>Unsupported data type: {dataType}</Typography>;
    }
  };

  return (
    <Box sx={{ mt: 3, mb: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Market Data Viewer
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel id="data-type-label">Data Type</InputLabel>
              <Select
                labelId="data-type-label"
                value={dataType}
                onChange={(e) => setDataType(e.target.value)}
                label="Data Type"
              >
                <MenuItem value="bars">Bars</MenuItem>
                <MenuItem value="quotes">Quotes</MenuItem>
                <MenuItem value="trades">Trades</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {dataType === 'bars' && (
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel id="timeframe-label">Timeframe</InputLabel>
                <Select
                  labelId="timeframe-label"
                  value={timeframe}
                  onChange={(e) => setTimeframe(e.target.value)}
                  label="Timeframe"
                >
                  <MenuItem value="1Min">1 Minute</MenuItem>
                  <MenuItem value="5Min">5 Minutes</MenuItem>
                  <MenuItem value="15Min">15 Minutes</MenuItem>
                  <MenuItem value="1Hour">1 Hour</MenuItem>
                  <MenuItem value="1Day">1 Day</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          )}
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel id="auto-refresh-label">Auto Refresh</InputLabel>
              <Select
                labelId="auto-refresh-label"
                value={autoRefresh ? 'true' : 'false'}
                onChange={(e) => setAutoRefresh(e.target.value === 'true')}
                label="Auto Refresh"
              >
                <MenuItem value="true">On (Every 5s)</MenuItem>
                <MenuItem value="false">Off</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ height: '100%', display: 'flex', alignItems: 'center' }}>
              <Button
                variant="contained"
                startIcon={<RefreshIcon />}
                onClick={fetchMarketData}
                disabled={loading}
                fullWidth
              >
                {loading ? 'Loading...' : 'Refresh Data'}
              </Button>
            </Box>
          </Grid>
        </Grid>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Symbols
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
            {symbols.map((symbol) => (
              <Chip
                key={symbol}
                label={symbol}
                onDelete={() => removeSymbol(symbol)}
                color="primary"
                variant="outlined"
              />
            ))}
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TextField
              label="Add Symbol"
              size="small"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
              sx={{ mr: 1 }}
            />
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={addSymbol}
              disabled={!newSymbol}
            >
              Add
            </Button>
          </Box>
        </Box>
        
        <Typography variant="subtitle1" gutterBottom>
          Data Source: {activeSource.charAt(0).toUpperCase() + activeSource.slice(1).replace('_', ' ')}
        </Typography>
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box sx={{ overflowX: 'auto' }}>
            {renderMarketData()}
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default MarketDataViewer; 