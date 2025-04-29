import React, { useState, useEffect } from 'react';
import { Box, Card, CardContent, Typography, Grid, Paper, Chip, Button, CircularProgress, Divider, Alert, AlertTitle, TextField, MenuItem, FormControl, InputLabel, Select } from '@mui/material';
import { CheckCircle, Error, Refresh, TrendingUp, TrendingDown, Warning, Info as InfoIcon, Analytics, BarChart } from '@mui/icons-material';
import dualBotService from '../services/dualBotService';
import { alpha } from '@mui/material/styles';

// Mock data for when API is unavailable
const mockData = {
  status: {
    status: true,
    active_positions: [],
    last_update: new Date().toISOString()
  },
  marketData: {
    symbol: 'QQQ',
    price: 456.78,
    timestamp: new Date().toISOString()
  },
  recommendation: {
    symbol: 'QQQ',
    trade_type: 'BUY_CALL',
    strike: 460,
    expiration: '2023-12-15',
    entry_price: 3.25,
    target_price: 5.50,
    stop_loss: 1.75,
    confidence: 0.82,
    rationale: 'Strong bullish momentum with increasing volume and positive technicals'
  },
  riskAssessment: {
    approved: true,
    risk_score: 7.2,
    market_conditions: 'Favorable',
    concerns: 'Slightly elevated IV, consider reducing position size',
    summary: 'This trade has a positive risk/reward ratio with defined exit points'
  }
};

const DualBotDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [botStatus, setBotStatus] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [riskAssessment, setRiskAssessment] = useState(null);
  const [useMockData, setUseMockData] = useState(false);
  const [symbol, setSymbol] = useState('QQQ');
  const [availableSymbols, setAvailableSymbols] = useState(['QQQ', 'TSLA', 'PLTR', 'AAPL', 'NVDA']);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [connectionDetails, setConnectionDetails] = useState(null);

  const checkConnectionStatus = async () => {
    try {
      const status = await dualBotService.checkConnectionStatus();
      setConnectionDetails(status);
      
      if (status.status === 'connected') {
        setConnectionStatus('connected');
        setError(null);
      } else if (status.status === 'partial') {
        setConnectionStatus('partial');
        setError('Some API endpoints are not responding correctly. Limited functionality available.');
      } else {
        setConnectionStatus('disconnected');
        setError('Cannot connect to the Dual Bot API. Using mock data instead.');
        setUseMockData(true);
      }
      
      return status.status;
    } catch (err) {
      console.error('Error checking connection status:', err);
      setConnectionStatus('disconnected');
      setError('Connection check failed. Using mock data instead.');
      setUseMockData(true);
      return 'disconnected';
    }
  };

  const fetchDualBotData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // First check the connection status
      const connStatus = await checkConnectionStatus();
      
      if (connStatus === 'disconnected') {
        console.log('Using mock data due to disconnected status');
        setUseMockData(true);
      }
      
      // Try to get configuration
      try {
        const config = await dualBotService.getConfig();
        if (config?.symbols?.length) {
          setAvailableSymbols(config.symbols);
        }
      } catch (err) {
        console.error('Failed to fetch config:', err);
      }
      
      // Get bot status
      try {
        const status = await dualBotService.getBotStatus();
        console.log('Bot status response:', status);
        setBotStatus(status);
      } catch (err) {
        console.error('Failed to fetch bot status:', err);
        setError(prev => prev || `Failed to fetch bot status: ${err.message}`);
      }
      
      // Get market data for symbol
      try {
        const marketDataResult = await dualBotService.getMarketData(symbol);
        console.log('Market data response:', marketDataResult);
        setMarketData(marketDataResult);
      } catch (err) {
        console.error(`Failed to fetch market data for ${symbol}:`, err);
        setError(prev => prev || `Failed to fetch market data: ${err.message}`);
      }

      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching dual bot data:', err);
      setError(`Failed to connect to the Dual Bot API: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSymbolChange = (event) => {
    setSymbol(event.target.value);
  };

  // Get a trading recommendation
  const getRecommendation = async () => {
    try {
      setActionLoading(true);
      setError(null);
      const result = await dualBotService.scanForTrades(symbol);
      setRecommendation(result);
      // Clear previous risk assessment whenever a new recommendation is generated
      setRiskAssessment(null);
    } catch (err) {
      console.error('Error getting recommendation:', err);
      setError(`Failed to get trade recommendation for ${symbol}. ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  // Assess risk for the recommendation
  const assessRisk = async () => {
    try {
      if (!recommendation) {
        setError('Cannot assess risk: No recommendation available');
        return;
      }
      
      setActionLoading(true);
      setError(null);
      
      const marketContext = {
        price: marketData?.price || 0,
        volatility: 'medium',
        market_condition: 'bullish',
        timestamp: new Date().toISOString()
      };
      
      const result = await dualBotService.assessRisk(recommendation, marketContext);
      setRiskAssessment(result);
    } catch (err) {
      console.error('Error assessing risk:', err);
      setError(`Failed to assess risk for ${symbol} recommendation. ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    // Check connection status first
    const initialSetup = async () => {
      await checkConnectionStatus();
      fetchDualBotData();
    };
    
    initialSetup();
    
    // Fetch data every 60 seconds
    const interval = setInterval(fetchDualBotData, 60000);
    
    // Check connection status every 30 seconds
    const connectionInterval = setInterval(checkConnectionStatus, 30000);
    
    return () => {
      clearInterval(interval);
      clearInterval(connectionInterval);
    };
  }, []);

  // Fetch market data when symbol changes
  useEffect(() => {
    if (symbol) {
      const fetchMarketData = async () => {
        try {
          setError(null);
          const marketDataResult = await dualBotService.getMarketData(symbol);
          setMarketData(marketDataResult);
        } catch (err) {
          console.error(`Failed to fetch market data for ${symbol}:`, err);
          setError(`Failed to fetch market data for ${symbol}`);
        }
      };
      
      fetchMarketData();
      // Clear recommendation and risk assessment when symbol changes
      setRecommendation(null);
      setRiskAssessment(null);
    }
  }, [symbol]);

  const renderSystemHealth = () => {
    if (!botStatus || !botStatus.components) {
      return (
        <Typography color="text.secondary">
          System health information not available
        </Typography>
      );
    }

    const { components } = botStatus;
    
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        {Object.entries(components).map(([name, isActive]) => (
          <Box key={name} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {isActive ? (
              <CheckCircle color="success" fontSize="small" />
            ) : (
              <Error color="error" fontSize="small" />
            )}
            <Typography variant="body2">
              {name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}: {isActive ? 'Active' : 'Inactive'}
            </Typography>
          </Box>
        ))}
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
          Last Updated: {new Date(botStatus.last_updated).toLocaleString()}
        </Typography>
      </Box>
    );
  };

  const renderMarketData = () => {
    if (!marketData) {
      return (
        <Typography color="text.secondary">
          Market data not available
        </Typography>
      );
    }
    
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          {marketData.symbol || 'Unknown Symbol'}
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4">
            ${marketData.price?.toFixed(2) || 'N/A'}
          </Typography>
          <Chip 
            label="Live Data"
            color="success"
            size="small"
            sx={{ ml: 1 }}
          />
        </Box>
        <Divider sx={{ my: 2 }} />
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {marketData.volume && (
            <Typography variant="body2">
              Volume: {marketData.volume.toLocaleString()}
            </Typography>
          )}
          {marketData.indicators && (
            <>
              <Typography variant="body2">
                EMA9: {marketData.indicators.ema_9?.toFixed(2) || 'N/A'}
              </Typography>
              <Typography variant="body2">
                EMA21: {marketData.indicators.ema_21?.toFixed(2) || 'N/A'}
              </Typography>
            </>
          )}
          <Typography variant="caption" color="text.secondary">
            Last Updated: {marketData.timestamp ? new Date(marketData.timestamp).toLocaleString() : new Date().toLocaleString()}
          </Typography>
        </Box>
      </Box>
    );
  };

  // Add a connection status component
  const renderConnectionStatus = () => {
    const getStatusColor = () => {
      switch (connectionStatus) {
        case 'connected': return 'success.main';
        case 'partial': return 'warning.main';
        case 'disconnected': return 'error.main';
        default: return 'info.main';
      }
    };
    
    const getStatusIcon = () => {
      switch (connectionStatus) {
        case 'connected': return <CheckCircle color="success" />;
        case 'partial': return <Warning color="warning" />;
        case 'disconnected': return <Error color="error" />;
        default: return <InfoIcon color="info" />;
      }
    };
    
    const getStatusText = () => {
      switch (connectionStatus) {
        case 'connected': return 'Connected to API Server';
        case 'partial': return 'Partial API Connection';
        case 'disconnected': return 'Using Mock Data (API Disconnected)';
        default: return 'Checking Connection...';
      }
    };
    
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        {getStatusIcon()}
        <Typography color={getStatusColor()}>
          {getStatusText()}
        </Typography>
        {connectionStatus !== 'connected' && (
          <Button 
            size="small" 
            variant="outlined" 
            startIcon={<Refresh />}
            onClick={checkConnectionStatus}
          >
            Retry
          </Button>
        )}
      </Box>
    );
  };

  if (loading && !botStatus && !marketData) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px', flexDirection: 'column' }}>
        <CircularProgress sx={{ mb: 2 }} />
        <Typography variant="body1">Connecting to Dual Bot API...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <BarChart sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h4" component="h1" gutterBottom>
            Dual Bot Dashboard
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Chip 
            icon={
              connectionStatus === 'connected' ? <CheckCircle /> : 
              connectionStatus === 'partial' ? <Warning /> : 
              <Error />
            }
            label={
              connectionStatus === 'connected' ? 'API Connected' : 
              connectionStatus === 'partial' ? 'Partial Connection' : 
              'API Disconnected'
            }
            color={
              connectionStatus === 'connected' ? 'success' : 
              connectionStatus === 'partial' ? 'warning' : 
              'error'
            }
            size="small"
            sx={{ mr: 2 }}
          />
          <Button 
            variant="outlined" 
            startIcon={<Refresh />} 
            onClick={fetchDualBotData}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {useMockData && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <AlertTitle>Using Demo Data</AlertTitle>
          Currently using simulated data. The Dual Bot API is not fully connected.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Bot Status Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Bot Status
              </Typography>
              {renderSystemHealth()}
            </CardContent>
          </Card>
        </Grid>

        {/* Symbol Selection and Market Data Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Market Data
                </Typography>
                
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel id="symbol-select-label">Symbol</InputLabel>
                  <Select
                    labelId="symbol-select-label"
                    id="symbol-select"
                    value={symbol}
                    label="Symbol"
                    onChange={handleSymbolChange}
                  >
                    {availableSymbols.map((sym) => (
                      <MenuItem key={sym} value={sym}>{sym}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
              
              {renderMarketData()}
            </CardContent>
          </Card>
        </Grid>

        {/* Bottom Panel - Trade Recommendations and Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Trading Actions
            </Typography>
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
              <Button 
                variant="contained" 
                startIcon={<Analytics />}
                onClick={getRecommendation}
                disabled={actionLoading}
              >
                Get Trade Recommendation
              </Button>
              
              <Button 
                variant="outlined"
                onClick={assessRisk}
                disabled={actionLoading || !recommendation}
              >
                Assess Risk
              </Button>
            </Box>
            
            {actionLoading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                <CircularProgress size={24} />
              </Box>
            )}
            
            {recommendation && (
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Trade Recommendation
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body1" fontWeight="bold">
                          {recommendation.symbol} - {recommendation.trade_type}
                        </Typography>
                        <Chip 
                          label={`Confidence: ${(recommendation.confidence * 100).toFixed(0)}%`}
                          color={recommendation.confidence > 0.7 ? "success" : recommendation.confidence > 0.5 ? "warning" : "error"}
                          size="small"
                          sx={{ mt: 1 }}
                        />
                      </Box>
                      
                      <Typography variant="body2">
                        Entry: ${recommendation.entry_price?.toFixed(2) || 'N/A'}
                      </Typography>
                      <Typography variant="body2">
                        Target: ${recommendation.target_price?.toFixed(2) || 'N/A'}
                      </Typography>
                      <Typography variant="body2">
                        Stop Loss: ${recommendation.stop_loss?.toFixed(2) || 'N/A'}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        {recommendation.rationale || 'No additional rationale provided.'}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            )}
            
            {riskAssessment && (
              <Card sx={{ 
                bgcolor: riskAssessment.approved ? alpha('#e6f4ea', 0.9) : alpha('#fce8e6', 0.9),
                color: 'text.primary', 
                border: '1px solid',
                borderColor: riskAssessment.approved ? 'success.light' : 'error.light',
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6" color={riskAssessment.approved ? "success.main" : "error.main"} sx={{ fontWeight: 'bold' }}>
                      Risk Assessment
                    </Typography>
                    <Chip 
                      label={riskAssessment.approved ? "Approved" : "Rejected"}
                      color={riskAssessment.approved ? "success" : "error"}
                      size="small"
                      sx={{ ml: 2 }}
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
                    <Chip 
                      label={`Risk Score: ${riskAssessment.risk_score?.toFixed(1) || 'N/A'}`}
                      color={
                        riskAssessment.risk_score > 8 ? "error" : 
                        riskAssessment.risk_score > 5 ? "warning" : "success"
                      }
                      size="small"
                    />
                    <Chip 
                      label={`Market: ${riskAssessment.market_conditions || 'Unknown'}`}
                      size="small"
                    />
                  </Box>
                  
                  {riskAssessment.concerns && (
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ color: 'warning.dark', fontWeight: 'medium' }}>{riskAssessment.concerns}</Typography>
                    </Alert>
                  )}
                  
                  <Typography variant="body2" sx={{ mb: 2, color: 'text.primary', fontWeight: 'medium' }}>
                    {riskAssessment.summary}
                  </Typography>
                  
                  {/* Enhanced Risk Assessment Details */}
                  <Paper elevation={1} sx={{ 
                    bgcolor: 'background.paper', 
                    p: 2, 
                    mt: 2,
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    border: '1px solid',
                    borderColor: 'divider',
                  }}>
                    <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold', color: 'text.primary' }}>
                      Detailed Risk Assessment
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 'medium' }}>Risk Category</Typography>
                        <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 'medium' }}>
                          {riskAssessment.risk_level || 
                            (riskAssessment.risk_score > 8 ? "HIGH" : 
                            riskAssessment.risk_score > 5 ? "MEDIUM" : "LOW")}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 'medium' }}>Confidence Level</Typography>
                        <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 'medium' }}>
                          {riskAssessment.confidence ? `${(riskAssessment.confidence * 100).toFixed(0)}%` : 'NaN%'}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 'medium' }}>Key Market Indicators</Typography>
                        <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 'medium' }}>
                          {riskAssessment.market_conditions} 
                          {riskAssessment.market_indicators && ` with ${riskAssessment.market_indicators}`}
                        </Typography>
                      </Grid>
                      
                      {/* Risk Factors Section */}
                      {riskAssessment.risk_factors && (
                        <Grid item xs={12}>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 'medium' }}>Risk Factors</Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {Object.entries(riskAssessment.risk_factors).map(([factor, value]) => (
                              <Chip 
                                key={factor}
                                label={`${factor.replace('_', ' ')}: ${value}`}
                                size="small"
                                color={
                                  value === 'High' || value === 'Poor' || value === 'Negative' || value === 'Weak' 
                                    ? 'warning' 
                                    : 'default'
                                }
                                sx={{ 
                                  textTransform: 'capitalize',
                                  color: 'text.primary',
                                  fontWeight: 'medium',
                                }}
                              />
                            ))}
                          </Box>
                        </Grid>
                      )}
                      
                      {/* Position Sizing */}
                      {riskAssessment.position_sizing && (
                        <Grid item xs={12}>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 'medium' }}>Position Sizing</Typography>
                          <Box sx={{ display: 'flex', gap: 2 }}>
                            <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 'medium' }}>
                              <strong>Recommended:</strong> {riskAssessment.position_sizing.recommended_size}
                            </Typography>
                            <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 'medium' }}>
                              <strong>Max Risk:</strong> {riskAssessment.position_sizing.max_risk_percent}
                            </Typography>
                          </Box>
                        </Grid>
                      )}
                      
                      {/* Alternative Strategies */}
                      {riskAssessment.alternative_strategies && riskAssessment.alternative_strategies.length > 0 && (
                        <Grid item xs={12}>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 'medium' }}>Alternative Strategies</Typography>
                          <ul style={{ margin: 0, paddingLeft: '1.2rem' }}>
                            {riskAssessment.alternative_strategies.map((strategy, index) => (
                              <li key={index}>
                                <Typography variant="body2" sx={{ color: 'text.primary', fontWeight: 'medium' }}>{strategy}</Typography>
                              </li>
                            ))}
                          </ul>
                        </Grid>
                      )}
                      
                      <Grid item xs={12} sx={{ mt: 1 }}>
                        <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 'medium' }}>Final Recommendation</Typography>
                        <Typography variant="body1" fontWeight="bold" color={riskAssessment.approved ? "success.dark" : "error.dark"}>
                          {riskAssessment.approved ? 
                            "Proceed with trade as recommended" : 
                            "Avoid this trade or reduce position size significantly"}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Paper>
                </CardContent>
              </Card>
            )}
          </Paper>
        </Grid>
      </Grid>
      
      {lastUpdated && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 3, display: 'block', textAlign: 'right' }}>
          Dashboard last updated: {lastUpdated.toLocaleString()}
        </Typography>
      )}
    </Box>
  );
};

export default DualBotDashboard; 