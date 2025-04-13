import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, CircularProgress,
  Alert, Grid, TextField, Button, Select, MenuItem,
  FormControl, InputLabel, Chip, Card, CardContent,
  CardHeader, Divider, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Tooltip, IconButton,
  LinearProgress
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';
import InfoIcon from '@mui/icons-material/Info';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

const InstitutionalFlow = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [symbols, setSymbols] = useState(['SPY', 'QQQ', 'AAPL']);
  const [newSymbol, setNewSymbol] = useState('');
  const [daysBack, setDaysBack] = useState(7);
  const [flowResults, setFlowResults] = useState({});
  const [flowTimestamp, setFlowTimestamp] = useState(null);
  const [activeTab, setActiveTab] = useState('summary'); // 'summary', 'options', 'darkpool'

  useEffect(() => {
    // Run analysis on initial load if we have symbols
    if (symbols.length > 0) {
      analyzeFlow();
    }
  }, []);

  const analyzeFlow = async () => {
    if (symbols.length === 0) {
      setError('Please add at least one symbol to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await fetch('/api/execution-model/analyze/flow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbols,
          days_back: daysBack
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to analyze institutional flow');
      }

      const data = await response.json();
      setFlowResults(data.flow_analysis || {});
      setFlowTimestamp(data.timestamp);
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

  const getSignalColor = (signal) => {
    if (signal > 0.5) return 'success.main';
    if (signal < -0.5) return 'error.main';
    if (signal >= 0.2) return 'success.light';
    if (signal <= -0.2) return 'error.light';
    return 'text.secondary';
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const renderSignalIndicator = (signal) => {
    // Normalize signal to 0-100 range for progress bar
    const normalizedValue = ((signal + 1) / 2) * 100;
    
    return (
      <Box sx={{ position: 'relative', display: 'inline-flex', width: '100%', alignItems: 'center' }}>
        <Box sx={{ width: '100%', mr: 1 }}>
          <LinearProgress 
            variant="determinate" 
            value={normalizedValue} 
            color={signal > 0 ? "success" : "error"}
            sx={{ 
              height: 10, 
              borderRadius: 5,
              backgroundColor: signal > 0 ? 'success.light' : 'error.light',
              '& .MuiLinearProgress-bar': {
                backgroundColor: signal > 0 ? 'success.main' : 'error.main'
              }
            }}
          />
        </Box>
        <Box sx={{ minWidth: 45 }}>
          <Typography variant="body2" color={getSignalColor(signal)}>
            {signal > 0 ? '+' : ''}{(signal * 100).toFixed(0)}%
          </Typography>
        </Box>
      </Box>
    );
  };

  const renderConfidenceChip = (confidence) => {
    let color = 'default';
    let label = 'Unknown';
    
    if (confidence > 0.8) {
      color = 'success';
      label = 'High';
    } else if (confidence > 0.5) {
      color = 'primary';
      label = 'Medium';
    } else {
      color = 'warning';
      label = 'Low';
    }
    
    return (
      <Chip 
        label={`${label} (${(confidence * 100).toFixed(0)}%)`} 
        color={color} 
        size="small" 
        variant="outlined"
      />
    );
  };

  const renderFlowSummary = () => {
    if (Object.keys(flowResults).length === 0) {
      return (
        <Typography color="textSecondary" align="center" py={4}>
          No flow analysis results available yet. Click Analyze to start.
        </Typography>
      );
    }

    return (
      <Grid container spacing={2}>
        {symbols.map(symbol => {
          const analysis = flowResults[symbol];
          
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
                      No flow data available for this symbol
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
                      {analysis.signal > 0.2 ? 
                        <TrendingUpIcon color="success" /> : 
                        analysis.signal < -0.2 ? 
                        <TrendingDownIcon color="error" /> : 
                        <TrendingFlatIcon color="inherit" />
                      }
                    </Box>
                  }
                  subheader={renderConfidenceChip(analysis.confidence)}
                  action={
                    <IconButton size="small" onClick={() => handleRemoveSymbol(symbol)}>
                      <DeleteIcon />
                    </IconButton>
                  }
                />
                <Divider />
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>Overall Flow Signal</Typography>
                  {renderSignalIndicator(analysis.signal)}
                  
                  <Grid container spacing={2} mt={1}>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Options Signal</Typography>
                      {renderSignalIndicator(analysis.options_signal)}
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Dark Pool Signal</Typography>
                      {renderSignalIndicator(analysis.dark_pool_signal)}
                    </Grid>
                  </Grid>
                  
                  <Typography variant="subtitle2" mt={2}>Analysis Details</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {analysis.details}
                  </Typography>
                  
                  <Box mt={2} display="flex" justifyContent="center">
                    <Chip 
                      icon={analysis.has_significant_flow ? <InfoIcon /> : <HelpOutlineIcon />}
                      label={analysis.has_significant_flow ? 
                        "Significant institutional activity" : 
                        "No significant institutional activity"}
                      color={analysis.has_significant_flow ? "primary" : "default"}
                      size="small"
                    />
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
      <Typography variant="h5" mb={2}>Institutional Flow Analysis</Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(false)}>
          Flow analysis completed successfully!
        </Alert>
      )}
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={5}>
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
          
          <Grid item xs={12} md={5}>
            <FormControl fullWidth size="small">
              <InputLabel>Days to Look Back</InputLabel>
              <Select
                value={daysBack}
                label="Days to Look Back"
                onChange={(e) => setDaysBack(e.target.value)}
              >
                <MenuItem value={1}>1 Day</MenuItem>
                <MenuItem value={3}>3 Days</MenuItem>
                <MenuItem value={7}>7 Days</MenuItem>
                <MenuItem value={14}>14 Days</MenuItem>
                <MenuItem value={30}>30 Days</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              onClick={analyzeFlow}
              disabled={loading || symbols.length === 0}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
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
      
      {flowTimestamp && (
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="caption" color="textSecondary">
            Last analyzed: {new Date(flowTimestamp).toLocaleString()}
          </Typography>
          <Button
            size="small"
            startIcon={<RefreshIcon />}
            onClick={analyzeFlow}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      )}
      
      <Box sx={{ mb: 2 }}>
        <Paper variant="outlined">
          <Box sx={{ p: 2, backgroundColor: 'info.light', color: 'info.contrastText' }}>
            <Typography>
              <InfoIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
              Institutional flow analysis examines unusual options activity and dark pool transactions 
              to identify potential "smart money" moves by institutional investors.
            </Typography>
          </Box>
        </Paper>
      </Box>
      
      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : (
        renderFlowSummary()
      )}
    </Box>
  );
};

export default InstitutionalFlow; 