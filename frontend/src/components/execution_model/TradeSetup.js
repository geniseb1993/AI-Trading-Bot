import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, CircularProgress,
  Alert, Grid, TextField, Button, Select, MenuItem,
  FormControl, InputLabel, Chip, Card, CardContent,
  CardHeader, Divider, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Tooltip, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, LinearProgress,
  Accordion, AccordionSummary, AccordionDetails, Switch, FormControlLabel,
  Tabs, Tab
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import InfoIcon from '@mui/icons-material/Info';

const TradeSetup = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [symbols, setSymbols] = useState(['SPY', 'QQQ', 'AAPL']);
  const [newSymbol, setNewSymbol] = useState('');
  const [timeframe, setTimeframe] = useState('1d');
  const [limit, setLimit] = useState(100);
  const [tradeSetups, setTradeSetups] = useState([]);
  const [setupTimestamp, setSetupTimestamp] = useState(null);
  const [selectedSetup, setSelectedSetup] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [executingTrade, setExecutingTrade] = useState(false);
  const [tradeResult, setTradeResult] = useState(null);
  const [tradeResultDialog, setTradeResultDialog] = useState(false);
  const [onlyShowViableSetups, setOnlyShowViableSetups] = useState(true);

  useEffect(() => {
    // Generate setups on initial load if we have symbols
    if (symbols.length > 0) {
      generateSetups();
    }
  }, []);

  const generateSetups = async () => {
    if (symbols.length === 0) {
      setError('Please add at least one symbol to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await fetch('/api/execution-model/setup/generate', {
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
        throw new Error(errorData.error || 'Failed to generate trade setups');
      }

      const data = await response.json();
      setTradeSetups(data.trade_setups || []);
      setSetupTimestamp(data.timestamp);
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

  const handleOpenSetupDetails = (setup) => {
    setSelectedSetup(setup);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
  };

  const executeTrade = async (setup) => {
    setExecutingTrade(true);
    setTradeResult(null);
    
    try {
      const response = await fetch('/api/execution-model/execute/trade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          setup_id: setup.id,
          symbol: setup.symbol,
          direction: setup.direction,
          entry_price: setup.entry_price,
          stop_loss: setup.stop_loss,
          profit_target: setup.profit_target,
          position_size: setup.position_size
        }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to execute trade');
      }

      setTradeResult(data.trade_result);
      setTradeResultDialog(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setExecutingTrade(false);
      handleCloseDialog();
    }
  };

  const closeTradeResultDialog = () => {
    setTradeResultDialog(false);
    // Refresh trade setups after execution
    generateSetups();
  };

  const getSetupTypeChip = (type) => {
    // Handle undefined type
    if (!type) {
      type = 'unknown';
    }
    
    let color = 'default';
    
    switch (type.toLowerCase()) {
      case 'trend_following':
        color = 'primary';
        break;
      case 'mean_reversion':
        color = 'secondary';
        break;
      case 'breakout':
        color = 'success';
        break;
      case 'momentum':
        color = 'warning';
        break;
      default:
        color = 'default';
    }
    
    return (
      <Chip 
        label={type.replace(/_/g, ' ')} 
        color={color} 
        size="small" 
        sx={{ textTransform: 'capitalize' }}
      />
    );
  };

  const getDirectionChip = (direction) => {
    // Handle undefined direction
    if (!direction) {
      direction = 'UNKNOWN';
    }
    
    return (
      <Chip 
        icon={direction === 'LONG' ? <TrendingUpIcon /> : <TrendingDownIcon />}
        label={direction} 
        color={direction === 'LONG' ? 'success' : (direction === 'SHORT' ? 'error' : 'default')} 
        size="small" 
      />
    );
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success.main';
    if (confidence >= 0.6) return 'primary.main';
    if (confidence >= 0.4) return 'warning.main';
    return 'error.main';
  };

  const renderConfidenceMeter = (confidence) => {
    return (
      <Box display="flex" alignItems="center">
        <LinearProgress
          variant="determinate"
          value={confidence * 100}
          color={confidence >= 0.8 ? 'success' : confidence >= 0.6 ? 'primary' : confidence >= 0.4 ? 'warning' : 'error'}
          sx={{ flexGrow: 1, mr: 1, height: 8, borderRadius: 4 }}
        />
        <Typography variant="body2" color={getConfidenceColor(confidence)}>
          {(confidence * 100).toFixed(0)}%
        </Typography>
      </Box>
    );
  };

  const filterSetups = (setups) => {
    if (!onlyShowViableSetups) return setups;
    
    return setups.filter(setup => {
      // Filter based on confidence and risk/reward
      return setup.confidence >= 0.6 && setup.risk_reward >= 1.5;
    });
  };

  const renderTradeSetups = () => {
    if (tradeSetups.length === 0) {
      return (
        <Typography color="textSecondary" align="center" py={4}>
          No trade setups available yet. Click Generate to create trade setups.
        </Typography>
      );
    }

    const filteredSetups = filterSetups(tradeSetups);
    
    if (filteredSetups.length === 0) {
      return (
        <Typography color="textSecondary" align="center" py={4}>
          No viable trade setups found with current filter settings.
        </Typography>
      );
    }

    return (
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 750 }}>
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Direction</TableCell>
              <TableCell>Entry</TableCell>
              <TableCell>Stop Loss</TableCell>
              <TableCell>Target</TableCell>
              <TableCell>R:R</TableCell>
              <TableCell>Confidence</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredSetups.map((setup, index) => (
              <TableRow
                key={index}
                sx={{
                  '&:last-child td, &:last-child th': { border: 0 },
                  backgroundColor: setup.confidence >= 0.8 ? 'success.lighter' : 'inherit'
                }}
              >
                <TableCell component="th" scope="row">
                  {setup.symbol}
                </TableCell>
                <TableCell>{getSetupTypeChip(setup.type)}</TableCell>
                <TableCell>{getDirectionChip(setup.direction)}</TableCell>
                <TableCell>{setup.entry_price.toFixed(2)}</TableCell>
                <TableCell>{setup.stop_loss.toFixed(2)}</TableCell>
                <TableCell>{setup.profit_target.toFixed(2)}</TableCell>
                <TableCell>{setup.risk_reward}</TableCell>
                <TableCell>
                  {renderConfidenceMeter(setup.confidence)}
                </TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleOpenSetupDetails(setup)}
                  >
                    Details
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Box>
      <Typography variant="h5" mb={2}>Trade Setup Generator</Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(false)}>
          Generated {tradeSetups.length} trade setups!
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
            <FormControlLabel
              control={
                <Switch
                  checked={onlyShowViableSetups}
                  onChange={(e) => setOnlyShowViableSetups(e.target.checked)}
                  color="primary"
                />
              }
              label="Only viable setups"
            />
          </Grid>
          
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              onClick={generateSetups}
              disabled={loading || symbols.length === 0}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
            >
              {loading ? 'Generating...' : 'Generate'}
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
      
      {setupTimestamp && (
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="caption" color="textSecondary">
            Last generated: {new Date(setupTimestamp).toLocaleString()}
          </Typography>
          <Button
            size="small"
            startIcon={<RefreshIcon />}
            onClick={generateSetups}
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
        renderTradeSetups()
      )}

      {/* Trade Setup Detail Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        {selectedSetup && (
          <>
            <DialogTitle>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="h6">
                  {selectedSetup.symbol} {getDirectionChip(selectedSetup.direction)} Setup
                </Typography>
                {getSetupTypeChip(selectedSetup.type)}
              </Box>
            </DialogTitle>
            <DialogContent>
              <Box mb={3}>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2">Entry Price</Typography>
                    <Typography variant="h6">${selectedSetup.entry_price.toFixed(2)}</Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2">Stop Loss</Typography>
                    <Typography variant="h6" color="error.main">${selectedSetup.stop_loss.toFixed(2)}</Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2">Profit Target</Typography>
                    <Typography variant="h6" color="success.main">${selectedSetup.profit_target.toFixed(2)}</Typography>
                  </Grid>
                </Grid>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>Trade Details</Typography>
                  
                  <Box mb={2}>
                    <Typography variant="subtitle2">Position Size</Typography>
                    <Typography variant="body1">{selectedSetup.position_size} shares</Typography>
                  </Box>
                  
                  <Box mb={2}>
                    <Typography variant="subtitle2">Risk/Reward Ratio</Typography>
                    <Typography variant="body1">1:{selectedSetup.risk_reward}</Typography>
                  </Box>
                  
                  <Box mb={2}>
                    <Typography variant="subtitle2">Confidence</Typography>
                    {renderConfidenceMeter(selectedSetup.confidence)}
                  </Box>
                  
                  <Box mb={2}>
                    <Typography variant="subtitle2">Market Condition</Typography>
                    <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                      {selectedSetup.market_condition?.replace('_', ' ') || 'Unknown'}
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>Setup Reason</Typography>
                  <Typography variant="body2" paragraph>
                    {selectedSetup.setup_reason || 'No detailed reason provided.'}
                  </Typography>
                  
                  <Typography variant="subtitle1" gutterBottom>Technical Indicators</Typography>
                  <Grid container spacing={1}>
                    {selectedSetup.indicators && Object.entries(selectedSetup.indicators).map(([key, value]) => (
                      <Grid item xs={6} key={key}>
                        <Typography variant="subtitle2" sx={{ textTransform: 'capitalize' }}>
                          {key.replace(/_/g, ' ')}
                        </Typography>
                        <Typography variant="body2">
                          {typeof value === 'number' ? value.toFixed(2) : value.toString()}
                        </Typography>
                      </Grid>
                    ))}
                  </Grid>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog}>Close</Button>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => executeTrade(selectedSetup)}
                startIcon={executingTrade ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
                disabled={executingTrade}
              >
                {executingTrade ? 'Executing...' : 'Execute Trade'}
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Trade Execution Result Dialog */}
      <Dialog
        open={tradeResultDialog}
        onClose={closeTradeResultDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Trade Execution Result
        </DialogTitle>
        <DialogContent>
          {tradeResult && (
            <Box>
              <Alert 
                severity={tradeResult.executed ? "success" : "error"}
                icon={tradeResult.executed ? <CheckCircleOutlineIcon /> : <ErrorOutlineIcon />}
                sx={{ mb: 2 }}
              >
                {tradeResult.executed ? 
                  `Trade successfully executed for ${tradeResult.symbol}` : 
                  `Failed to execute trade: ${tradeResult.reason}`
                }
              </Alert>

              {tradeResult.executed && (
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Trade ID</Typography>
                    <Typography variant="body1">{tradeResult.trade_id}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Symbol</Typography>
                    <Typography variant="body1">{tradeResult.symbol}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Direction</Typography>
                    <Typography variant="body1">{tradeResult.direction}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Quantity</Typography>
                    <Typography variant="body1">{tradeResult.quantity}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Entry Price</Typography>
                    <Typography variant="body1">${tradeResult.entry_price?.toFixed(2)}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Stop Loss</Typography>
                    <Typography variant="body1">${tradeResult.stop_loss?.toFixed(2)}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Profit Target</Typography>
                    <Typography variant="body1">${tradeResult.profit_target?.toFixed(2)}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Execution Time</Typography>
                    <Typography variant="body1">
                      {new Date(tradeResult.timestamp).toLocaleString()}
                    </Typography>
                  </Grid>
                </Grid>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeTradeResultDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TradeSetup; 