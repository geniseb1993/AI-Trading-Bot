import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, CircularProgress,
  Alert, Grid, TextField, Button, Select, MenuItem,
  FormControl, InputLabel, Chip, Card, CardContent,
  CardHeader, Divider, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Tooltip, IconButton
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';
import Volume from '@mui/icons-material/EqualizerOutlined';
import ShowChartIcon from '@mui/icons-material/ShowChart';

const MarketAnalysis = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [symbols, setSymbols] = useState(['SPY', 'QQQ', 'AAPL']);
  const [newSymbol, setNewSymbol] = useState('');
  const [timeframe, setTimeframe] = useState('1d');
  const [limit, setLimit] = useState(100);
  const [analysisResults, setAnalysisResults] = useState({});
  const [analysisTimestamp, setAnalysisTimestamp] = useState(null);

  useEffect(() => {
    // Run analysis on initial load if we have symbols
    if (symbols.length > 0) {
      analyzeMarket();
    }
  }, []);

  const analyzeMarket = async () => {
    if (symbols.length === 0) {
      setError('Please add at least one symbol to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await fetch('/api/execution-model/analyze/market', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbols,
          timeframe,
          limit
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to analyze market conditions');
      }

      const data = await response.json();
      setAnalysisResults(data.analysis || {});
      setAnalysisTimestamp(data.timestamp);
      setSuccess(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSymbol = () => {
    if (!newSymbol) return;
    
    const symbol = newSymbol.toUpperCase();
    if (symbols.includes(symbol)) {
      setError(`Symbol ${symbol} is already in the list`);
      return;
    }
    
    setSymbols([...symbols, symbol]);
    setNewSymbol('');
  };

  const handleRemoveSymbol = (symbolToRemove) => {
    setSymbols(symbols.filter(s => s !== symbolToRemove));
  };

  const renderTrendIcon = (trendDirection) => {
    if (trendDirection > 0) {
      return <TrendingUpIcon color="success" />;
    } else if (trendDirection < 0) {
      return <TrendingDownIcon color="error" />;
    } else {
      return <TrendingFlatIcon color="inherit" />;
    }
  };

  const getMarketRegimeChip = (regime) => {
    // Add a default value if regime is undefined
    if (!regime) {
      regime = 'unknown';
    }
    
    let color = 'default';
    
    switch (regime) {
      case 'trending_up':
        color = 'success';
        break;
      case 'trending_down':
        color = 'error';
        break;
      case 'volatile':
        color = 'warning';
        break;
      case 'ranging':
        color = 'info';
        break;
      case 'calm':
        color = 'primary';
        break;
      default:
        color = 'default';
    }
    
    return (
      <Chip 
        label={regime.replace('_', ' ')} 
        color={color} 
        size="small" 
        sx={{ textTransform: 'capitalize' }}
      />
    );
  };

  const renderAnalysisResults = () => {
    if (Object.keys(analysisResults).length === 0) {
      return (
        <Typography color="textSecondary" align="center" py={4}>
          No analysis results available yet. Click Analyze to start.
        </Typography>
      );
    }

    return (
      <Grid container spacing={2}>
        {symbols.map(symbol => {
          const analysis = analysisResults[symbol];
          
          if (!analysis) {
            return (
              <Grid item xs={12} md={6} lg={4} key={symbol}>
                <Card variant="outlined">
                  <CardHeader 
                    title={symbol}
                    action={
                      <IconButton size="small" onClick={() => handleRemoveSymbol(symbol)}>
                        <DeleteIcon />
                      </IconButton>
                    }
                  />
                  <CardContent>
                    <Typography color="error">
                      No analysis data available for this symbol
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            );
          }
          
          return (
            <Grid item xs={12} md={6} lg={4} key={symbol}>
              <Card variant="outlined">
                <CardHeader 
                  title={
                    <Box display="flex" alignItems="center">
                      {symbol}
                      {' '}
                      {renderTrendIcon(analysis.trend?.direction)}
                    </Box>
                  }
                  subheader={getMarketRegimeChip(analysis.market_regime)}
                  action={
                    <IconButton size="small" onClick={() => handleRemoveSymbol(symbol)}>
                      <DeleteIcon />
                    </IconButton>
                  }
                />
                <Divider />
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Volatility</Typography>
                      <Typography variant="body2">
                        ATR: {analysis.volatility?.atr.toFixed(2)}<br />
                        Hist Vol: {(analysis.volatility?.historical_volatility * 100).toFixed(2)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Trend</Typography>
                      <Typography variant="body2">
                        Direction: {analysis.trend?.direction > 0 ? 'Up' : analysis.trend?.direction < 0 ? 'Down' : 'Neutral'}<br />
                        Strength: {(analysis.trend?.strength * 100).toFixed(2)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Momentum</Typography>
                      <Typography variant="body2">
                        RSI: {analysis.momentum?.rsi.toFixed(2)}<br />
                        MACD: {analysis.momentum?.macd.toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Volume</Typography>
                      <Typography variant="body2">
                        Profile: {analysis.volume?.profile.toFixed(2)}x
                      </Typography>
                    </Grid>
                  </Grid>
                  
                  <Typography variant="subtitle2" mt={2}>Support/Resistance</Typography>
                  <Box>
                    <Typography variant="body2" component="div">
                      <strong>Support:</strong> {analysis.support_resistance?.support_levels.map(level => level.toFixed(2)).join(', ')}
                    </Typography>
                    <Typography variant="body2" component="div">
                      <strong>Resistance:</strong> {analysis.support_resistance?.resistance_levels.map(level => level.toFixed(2)).join(', ')}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    );
  };

  return (
    <Box>
      <Typography variant="h5" mb={2}>Market Condition Analysis</Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(false)}>
          Analysis completed successfully!
        </Alert>
      )}
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <Box display="flex" alignItems="center">
              <TextField
                fullWidth
                label="Add Symbol"
                variant="outlined"
                size="small"
                value={newSymbol}
                onChange={(e) => setNewSymbol(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddSymbol()}
              />
              <Button 
                variant="contained"
                color="primary"
                onClick={handleAddSymbol}
                startIcon={<AddIcon />}
                sx={{ ml: 1 }}
              >
                Add
              </Button>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Timeframe</InputLabel>
              <Select
                value={timeframe}
                label="Timeframe"
                onChange={(e) => setTimeframe(e.target.value)}
              >
                <MenuItem value="1m">1 Minute</MenuItem>
                <MenuItem value="5m">5 Minutes</MenuItem>
                <MenuItem value="15m">15 Minutes</MenuItem>
                <MenuItem value="30m">30 Minutes</MenuItem>
                <MenuItem value="1h">1 Hour</MenuItem>
                <MenuItem value="1d">1 Day</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Data Points"
              type="number"
              variant="outlined"
              size="small"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value) || 100)}
            />
          </Grid>
          
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              onClick={analyzeMarket}
              disabled={loading || symbols.length === 0}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <ShowChartIcon />}
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </Button>
          </Grid>
        </Grid>
        
        <Box mt={2} display="flex" flexWrap="wrap" gap={1}>
          {symbols.map((symbol) => (
            <Chip
              key={symbol}
              label={symbol}
              onDelete={() => handleRemoveSymbol(symbol)}
              color="primary"
              variant="outlined"
            />
          ))}
        </Box>
      </Paper>
      
      {analysisTimestamp && (
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="caption" color="textSecondary">
            Last analyzed: {new Date(analysisTimestamp).toLocaleString()}
          </Typography>
          <Button
            size="small"
            startIcon={<RefreshIcon />}
            onClick={analyzeMarket}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      )}
      
      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : (
        renderAnalysisResults()
      )}
    </Box>
  );
};

export default MarketAnalysis; 