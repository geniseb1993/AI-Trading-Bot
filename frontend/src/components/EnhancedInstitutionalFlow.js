import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  Box, 
  Typography, 
  CircularProgress, 
  Card, 
  CardContent, 
  Grid, 
  TextField, 
  Button, 
  Chip,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Tooltip,
  IconButton,
  Tabs,
  Tab,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  ExpandMore as ExpandMoreIcon,
  Insights as InsightsIcon,
  MilitaryTech as MilitaryTechIcon,
  Collections as CollectionsIcon
} from '@mui/icons-material';

const EnhancedInstitutionalFlow = () => {
  // State
  const [symbols, setSymbols] = useState([]);
  const [inputSymbol, setInputSymbol] = useState('');
  const [daysBack, setDaysBack] = useState(30);
  const [selectedTab, setSelectedTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [flowData, setFlowData] = useState({});
  const [smartMoneyMoves, setSmartMoneyMoves] = useState([]);
  const [error, setError] = useState(null);
  const [isRealData, setIsRealData] = useState(false);
  const [dataSource, setDataSource] = useState('mock');
  
  // Function to analyze institutional flow
  const analyzeFlow = useCallback(async () => {
    if (symbols.length === 0) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('/api/institutional-flow/enhanced-analysis', {
        symbols,
        days_back: daysBack,
        include_raw_data: false
      });
      
      if (response.data && response.data.success) {
        setFlowData(response.data.flow_analysis || {});
        setSmartMoneyMoves(response.data.smart_money_moves || []);
        setIsRealData(response.data.is_real_data === true);
        setDataSource(response.data.data_source || 'mock');
        setError(null);
      } else {
        throw new Error(response.data.error || 'Failed to fetch institutional flow data');
      }
    } catch (err) {
      console.error(err);
      setError('Failed to fetch enhanced institutional flow data. Server might be down.');
      
      // Generate fallback mock data
      generateMockData();
    } finally {
      setLoading(false);
    }
  }, [symbols, daysBack]);
  
  // Generate mock data if API fails
  const generateMockData = () => {
    const mockFlowData = {};
    const mockSmartMoney = [];
    
    // Generate mock flow data for each symbol
    symbols.forEach(symbol => {
      const optionsSignal = (Math.random() * 2 - 1) * 0.8; // Between -0.8 and 0.8
      const darkPoolSignal = (Math.random() * 2 - 1) * 0.9; // Between -0.9 and 0.9
      const blockTradeSignal = (Math.random() * 2 - 1) * 0.7; // Between -0.7 and 0.7
      
      // Combined signal with weights
      const signal = (
        optionsSignal * 0.65 + 
        darkPoolSignal * 0.75 + 
        blockTradeSignal * 0.6
      ) / 2; // Normalize to range
      
      const confidence = 0.5 + Math.random() * 0.4; // Between 0.5 and 0.9
      
      mockFlowData[symbol] = {
        symbol,
        signal,
        options_signal: optionsSignal,
        dark_pool_signal: darkPoolSignal,
        block_trade_signal: blockTradeSignal,
        price_correlations: {
          short_term: (Math.random() * 2 - 1) * 0.7,
          medium_term: (Math.random() * 2 - 1) * 0.5,
          long_term: (Math.random() * 2 - 1) * 0.3
        },
        confidence,
        has_significant_flow: Math.abs(signal) > 0.55,
        details: `Mock institutional flow data for ${symbol}. API server might be down.`,
        timestamp: new Date().toISOString()
      };
      
      // Generate some smart money moves
      if (Math.random() > 0.7) {
        mockSmartMoney.push({
          type: Math.random() > 0.5 ? 'OPTIONS' : 'DARK_POOL',
          symbol,
          sentiment: Math.random() > 0.5 ? 'bullish' : 'bearish',
          confidence: 0.7 + Math.random() * 0.25,
          description: `Large ${Math.random() > 0.5 ? 'call' : 'put'} activity detected with significant premium`,
          timestamp: new Date().toISOString()
        });
      }
    });
    
    setFlowData(mockFlowData);
    setSmartMoneyMoves(mockSmartMoney);
    setIsRealData(false);
    setDataSource('mock');
  };
  
  // Effect to run analysis when symbols change
  useEffect(() => {
    if (symbols.length > 0) {
      analyzeFlow();
    }
  }, [symbols, analyzeFlow]);
  
  // Handle adding a symbol
  const handleAddSymbol = () => {
    if (!inputSymbol || inputSymbol.trim() === '') return;
    
    const formattedSymbol = inputSymbol.trim().toUpperCase();
    if (!symbols.includes(formattedSymbol)) {
      setSymbols([...symbols, formattedSymbol]);
      setInputSymbol('');
    }
  };
  
  // Handle removing a symbol
  const handleRemoveSymbol = (symbolToRemove) => {
    setSymbols(symbols.filter(s => s !== symbolToRemove));
  };
  
  // Handle days back change
  const handleDaysBackChange = (event) => {
    const value = parseInt(event.target.value, 10);
    if (!isNaN(value) && value > 0) {
      setDaysBack(value);
    }
  };
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };
  
  // Render a signal strength indicator
  const renderSignalStrength = (signal, size = 'medium') => {
    if (signal === undefined || signal === null) return <TrendingFlatIcon />;
    
    const strengthColor = 
      signal > 0.7 ? 'success.main' :
      signal > 0.3 ? 'success.light' :
      signal < -0.7 ? 'error.main' :
      signal < -0.3 ? 'error.light' :
      'warning.main';
    
    const IconComponent = 
      signal > 0.3 ? TrendingUpIcon :
      signal < -0.3 ? TrendingDownIcon :
      TrendingFlatIcon;
    
    return (
      <Box display="flex" alignItems="center">
        <IconComponent fontSize={size} sx={{ color: strengthColor }} />
        <Typography 
          variant={size === 'small' ? 'body2' : 'body1'} 
          color={strengthColor}
          fontWeight="bold"
          ml={0.5}
        >
          {(signal * 100).toFixed(1)}%
        </Typography>
      </Box>
    );
  };
  
  // Render confidence indicator
  const renderConfidence = (confidence) => {
    if (confidence === undefined || confidence === null) return null;
    
    const confidenceColor = 
      confidence > 0.8 ? 'success.main' :
      confidence > 0.6 ? 'primary.main' :
      'warning.main';
    
    return (
      <Tooltip title={`Analysis confidence: ${(confidence * 100).toFixed(0)}%`}>
        <Box>
          <LinearProgress 
            variant="determinate" 
            value={confidence * 100} 
            sx={{ height: 10, borderRadius: 5, bgcolor: 'grey.200' }}
            color={confidence > 0.8 ? 'success' : confidence > 0.6 ? 'primary' : 'warning'}
          />
        </Box>
      </Tooltip>
    );
  };
  
  // Render flow analysis summary for a symbol
  const renderSymbolAnalysis = (symbol, analysis) => {
    if (!analysis) return null;
    
    return (
      <Card key={symbol} sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="h5" component="h2">{symbol}</Typography>
            <Box display="flex" alignItems="center">
              {renderSignalStrength(analysis.signal)}
              <IconButton size="small" onClick={() => handleRemoveSymbol(symbol)} sx={{ ml: 1 }}>
                <Tooltip title="Remove symbol">
                  <RefreshIcon fontSize="small" />
                </Tooltip>
              </IconButton>
            </Box>
          </Box>
          
          {renderConfidence(analysis.confidence)}
          
          <Divider sx={{ my: 1.5 }} />
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Options Flow</Typography>
                {renderSignalStrength(analysis.options_signal, 'small')}
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Dark Pool</Typography>
                {renderSignalStrength(analysis.dark_pool_signal, 'small')}
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Block Trades</Typography>
                {renderSignalStrength(analysis.block_trade_signal, 'small')}
              </Box>
            </Grid>
          </Grid>
          
          <Divider sx={{ my: 1.5 }} />
          
          <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-line' }}>
            {analysis.details}
          </Typography>
          
          <Accordion sx={{ mt: 2 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Price Correlations</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">Short-term</Typography>
                  {renderSignalStrength(analysis.price_correlations?.short_term, 'small')}
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">Medium-term</Typography>
                  {renderSignalStrength(analysis.price_correlations?.medium_term, 'small')}
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">Long-term</Typography>
                  {renderSignalStrength(analysis.price_correlations?.long_term, 'small')}
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </CardContent>
      </Card>
    );
  };
  
  // Render the smart money moves table
  const renderSmartMoneyMoves = () => {
    if (smartMoneyMoves.length === 0) {
      return (
        <Alert severity="info" sx={{ mt: 2 }}>No significant smart money moves detected in the analyzed period.</Alert>
      );
    }
    
    return (
      <TableContainer component={Paper} sx={{ mt: 2 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Sentiment</TableCell>
              <TableCell>Confidence</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Time</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {smartMoneyMoves.map((move, index) => (
              <TableRow key={index} hover>
                <TableCell>
                  <Chip label={move.symbol} size="small" color="primary" variant="outlined" />
                </TableCell>
                <TableCell>
                  {move.type === 'OPTIONS' ? 'Options' : 
                   move.type === 'DARK_POOL' ? 'Dark Pool' : 
                   move.type === 'BLOCK_TRADE' ? 'Block Trade' : move.type}
                </TableCell>
                <TableCell>
                  <Chip 
                    label={move.sentiment} 
                    size="small" 
                    color={move.sentiment === 'bullish' ? 'success' : 'error'} 
                    variant="outlined"
                    icon={move.sentiment === 'bullish' ? <TrendingUpIcon /> : <TrendingDownIcon />}
                  />
                </TableCell>
                <TableCell>
                  {(move.confidence * 100).toFixed(0)}%
                </TableCell>
                <TableCell>{move.description}</TableCell>
                <TableCell>
                  {new Date(move.timestamp).toLocaleString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };
  
  // Render flow summary
  const renderFlowSummary = () => {
    const symbolAnalyses = Object.entries(flowData).map(([symbol, analysis]) => 
      renderSymbolAnalysis(symbol, analysis)
    );
    
    if (symbolAnalyses.length === 0) {
      return (
        <Alert severity="info">
          Add symbols to analyze institutional flow data.
        </Alert>
      );
    }
    
    return symbolAnalyses;
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Enhanced Institutional Flow
          <Tooltip title="Advanced analysis of institutional order flow, dark pool transactions, and block trades">
            <InfoIcon fontSize="small" sx={{ ml: 1, color: 'info.main' }} />
          </Tooltip>
        </Typography>
        
        <Chip 
          icon={isRealData ? <InsightsIcon /> : <CollectionsIcon />}
          label={isRealData ? `Real Data: ${dataSource}` : "Mock Data"} 
          color={isRealData ? "success" : "warning"}
          variant="outlined"
        />
      </Box>
      
      <Paper sx={{ mb: 3, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Box display="flex" alignItems="center">
              <TextField
                label="Add Symbol"
                value={inputSymbol}
                onChange={(e) => setInputSymbol(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddSymbol()}
                size="small"
                sx={{ mr: 1 }}
              />
              <Button 
                variant="contained" 
                color="primary" 
                onClick={handleAddSymbol}
                startIcon={<AddIcon />}
                size="small"
              >
                Add
              </Button>
            </Box>
          </Grid>
          
          <Grid item xs={6} md={3}>
            <TextField
              label="Days Back"
              type="number"
              value={daysBack}
              onChange={handleDaysBackChange}
              size="small"
              inputProps={{ min: 1, max: 90 }}
              fullWidth
            />
          </Grid>
          
          <Grid item xs={6} md={3}>
            <Button 
              variant="outlined" 
              onClick={analyzeFlow}
              startIcon={<RefreshIcon />}
              fullWidth
              disabled={loading || symbols.length === 0}
            >
              Refresh
            </Button>
          </Grid>
          
          <Grid item xs={12}>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {symbols.map(symbol => (
                <Chip 
                  key={symbol}
                  label={symbol}
                  onDelete={() => handleRemoveSymbol(symbol)}
                  color="primary"
                />
              ))}
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          variant="fullWidth"
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab 
            icon={<InsightsIcon />} 
            label="Flow Analysis" 
            iconPosition="start"
          />
          <Tab 
            icon={<MilitaryTechIcon />} 
            label="Smart Money" 
            iconPosition="start"
          />
        </Tabs>
      </Paper>
      
      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : (
        <Box>
          {selectedTab === 0 && renderFlowSummary()}
          {selectedTab === 1 && renderSmartMoneyMoves()}
        </Box>
      )}
    </Box>
  );
};

export default EnhancedInstitutionalFlow; 