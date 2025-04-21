import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent,
  Divider,
  Button,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Chip,
  LinearProgress,
  IconButton,
  Alert,
  useTheme,
  alpha,
  Tooltip,
  Switch,
  FormControlLabel,
  Paper
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  Warning, 
  Check, 
  FlashOn,
  MonetizationOn,
  Timeline,
  Autorenew,
  BarChart,
  ShowChart,
  Settings,
  Refresh,
  Cancel,
  ThumbUp,
  ThumbDown,
  KeyboardArrowUp,
  KeyboardArrowDown,
  Security,
  CheckCircle
} from '@mui/icons-material';
import axios from 'axios';
import { motion } from 'framer-motion';

// Define API base URL based on environment
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '';

// Generate mock data for fallback
const generateMockData = () => {
  return {
    performance: {
      dailyPnL: 3.2,
      weeklyPnL: 8.5,
      monthlyPnL: 12.7,
      winRate: 68,
      totalTrades: 25,
      avgWin: 5.2,
      avgLoss: -1.8,
      biggestWin: 12.3,
      biggestLoss: -3.5
    },
    riskStatus: {
      currentExposure: 35,
      maxExposure: 80,
      dailyPnLRisk: 15,
      marketCondition: 'Bullish',
      volatilityLevel: 'Moderate',
      riskLevel: 'Moderate',
      warningMessage: null,
      controls: {
        autoTrading: true,
        odteOnly: true
      }
    },
    tradeSetups: [
      {
        id: 'setup_1',
        symbol: 'SPX',
        type: 'CALL',
        strategy: '0DTE Momentum',
        price: 4520.50,
        confidence: 0.87,
        recommendation: 'BUY SPX CALL @ 4525',
        expiration: '0DTE',
        timestamp: new Date().toISOString()
      },
      {
        id: 'setup_2',
        symbol: 'QQQ',
        type: 'PUT', 
        strategy: '0DTE Reversal',
        price: 378.25,
        confidence: 0.76,
        recommendation: 'BUY QQQ PUT @ 378',
        expiration: '0DTE',
        timestamp: new Date().toISOString()
      },
      {
        id: 'setup_3',
        symbol: 'TSLA',
        type: 'CALL',
        strategy: 'Pre-Market Gap & Go',
        price: 242.50,
        confidence: 0.82,
        recommendation: 'BUY TSLA CALL @ 245',
        expiration: '3DTE',
        timestamp: new Date().toISOString()
      }
    ],
    systemHealth: {
      components: {
        dataFetcher: { status: 'operational', latency: 120 },
        signalGenerator: { status: 'operational', latency: 450 },
        riskManager: { status: 'operational', latency: 85 },
        executionEngine: { status: 'operational', latency: 220 }
      },
      lastUpdated: new Date().toISOString()
    }
  };
};

const CEODashboard = ({ data }) => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    performance: null,
    tradeSetups: [],
    riskStatus: null,
    systemHealth: null
  });

  // Settings
  const [settings, setSettings] = useState({
    autoTrading: false,
    riskLevel: 'moderate',
    maxDailyTrades: 5,
    stopLossPercent: 2.0,
    odteOnly: true
  });

  useEffect(() => {
    fetchDashboardData();
    // Also fetch settings
    fetchSettings();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Simplify API call logic - try only the correct endpoint with proper error handling
      console.log('Fetching CEO dashboard data');
      
      try {
        const dashboardResponse = await axios.get(`${API_BASE_URL}/api/ceo-dashboard`, { 
          timeout: 8000 // Increased timeout
        });
        
        if (dashboardResponse.data && dashboardResponse.data.success) {
          console.log('CEO dashboard data received:', dashboardResponse.data);
          setDashboardData(dashboardResponse.data);
          return; // Exit if successful
        }
      } catch (error) {
        console.log('API call failed:', error.message);
        // Continue to fallback
      }
      
      // If we reach here, use mock data
      console.log('Using mock dashboard data');
      setDashboardData(generateMockData());
    } catch (error) {
      console.error('Error fetching CEO dashboard data:', error);
      setError('Could not load CEO dashboard data. Using sample data instead.');
      setDashboardData(generateMockData());
    } finally {
      setLoading(false);
    }
  };
  
  const fetchSettings = async () => {
    try {
      // Try to fetch settings from API
      console.log('Fetching CEO settings');
      const settingsResponse = await axios.get(`${API_BASE_URL}/api/ceo-settings`, { 
        timeout: 8000 // Increased timeout
      });
      
      if (settingsResponse.data && settingsResponse.data.success) {
        console.log('Settings received successfully');
        setSettings(settingsResponse.data.settings);
      } else {
        console.log('Invalid settings response format, using defaults');
      }
    } catch (error) {
      console.error('Error fetching CEO settings:', error.message);
      // Keep using default settings
    }
  };

  const handleRefresh = () => {
    fetchDashboardData();
  };

  const handleSettingChange = async (setting, value) => {
    // Update local state
    setSettings(prev => ({
      ...prev,
      [setting]: value
    }));
    
    try {
      // Save settings to API
      const response = await axios.post(`${API_BASE_URL}/ceo-settings`, {
        ...settings,
        [setting]: value
      });
      
      if (response.data && response.data.success) {
        console.log('Settings updated successfully:', response.data);
      } else {
        console.error('Failed to update settings:', response.data);
      }
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  const handleApproveSetup = async (setupId) => {
    try {
      console.log(`Approving setup ${setupId}`);
      
      // Call the API to approve the trade setup
      const response = await axios.post(`${API_BASE_URL}/approve-trade-setup`, { 
        setupId: setupId 
      });
      
      if (response.data && response.data.success) {
        console.log('Trade setup approved:', response.data);
        // Refresh data to get updated state
        fetchDashboardData();
      } else {
        console.error('Failed to approve trade:', response.data);
      }
    } catch (error) {
      console.error('Error approving trade setup:', error);
    }
  };

  const handleRejectSetup = async (setupId) => {
    try {
      console.log(`Rejecting setup ${setupId}`);
      
      // Call the API to reject the trade setup
      const response = await axios.post(`${API_BASE_URL}/reject-trade-setup`, { 
        setupId: setupId 
      });
      
      if (response.data && response.data.success) {
        console.log('Trade setup rejected:', response.data);
        // Refresh data to get updated state
        fetchDashboardData();
      } else {
        console.error('Failed to reject trade:', response.data);
      }
    } catch (error) {
      console.error('Error rejecting trade setup:', error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ py: 2 }}>
    <Box sx={{ mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          CEO Command Center
        </Typography>
        {data ? (
          <Chip 
            label="Real Data" 
            color="success" 
            size="small" 
            sx={{ mb: 1 }} 
          />
        ) : (
          <Chip 
            label="Sample Data" 
            color="warning" 
          size="small"
            sx={{ mb: 1 }} 
          />
        )}
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper 
            elevation={0} 
            sx={{ 
              height: '100%', 
              borderRadius: 2,
              bgcolor: 'background.default',
              border: `1px solid ${theme.palette.divider}`
            }}
          >
            {renderPerformanceMetrics(dashboardData)}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper 
            elevation={0} 
            sx={{ 
              height: '100%', 
              borderRadius: 2,
              bgcolor: 'background.default',
              border: `1px solid ${theme.palette.divider}`
            }}
          >
            {renderRiskManagement(dashboardData, settings, handleSettingChange)}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper 
            elevation={0} 
            sx={{ 
              height: '100%',
              borderRadius: 2,
              bgcolor: 'background.default',
              border: `1px solid ${theme.palette.divider}`
            }}
          >
            {renderTopTradeSetups(dashboardData, handleApproveSetup, handleRejectSetup)}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

const renderPerformanceMetrics = (dashboardData) => {
  const metrics = dashboardData.performance || generateMockData().performance;
  
  return (
    <Box sx={{ height: '100%', p: 2 }}>
      <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box component="span" sx={{ mr: 1, display: 'flex', alignItems: 'center' }}>
          <Box component="span" sx={{ color: 'text.secondary', fontSize: '1.5rem' }}>
            $
          </Box>
        </Box>
                Performance Metrics
              </Typography>

      <Grid container spacing={3}>
        <Grid item xs={6} sm={3}>
          <Typography variant="subtitle2" color="text.secondary">
            Daily P&L
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              color: metrics.dailyPnL >= 0 ? 'success.main' : 'error.main',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            {metrics.dailyPnL >= 0 ? '+' : ''}{metrics.dailyPnL}%
                  </Typography>
                </Grid>
                
        <Grid item xs={6} sm={3}>
          <Typography variant="subtitle2" color="text.secondary">
            Win Rate
          </Typography>
          <Typography variant="h6">
            {metrics.winRate}%
                  </Typography>
                </Grid>

        <Grid item xs={6} sm={3}>
          <Typography variant="subtitle2" color="text.secondary">
            Weekly P&L
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              color: metrics.weeklyPnL >= 0 ? 'success.main' : 'error.main',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            {metrics.weeklyPnL >= 0 ? '+' : ''}{metrics.weeklyPnL}%
                  </Typography>
                </Grid>

        <Grid item xs={6} sm={3}>
          <Typography variant="subtitle2" color="text.secondary">
            Total Trades
          </Typography>
          <Typography variant="h6">
            {metrics.totalTrades}
                  </Typography>
                </Grid>
              </Grid>

      <Grid container spacing={3} sx={{ mt: 1 }}>
                <Grid item xs={6}>
          <Typography variant="subtitle2" color="text.secondary">
            Avg Win
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              color: 'success.main',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            +{metrics.avgWin}%
                  </Typography>
                </Grid>

                <Grid item xs={6}>
          <Typography variant="subtitle2" color="text.secondary">
            Avg Loss
                  </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              color: 'error.main',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            {metrics.avgLoss}%
          </Typography>
        </Grid>
      </Grid>
    </Box>
  );
};

const renderRiskManagement = (dashboardData, settings, handleSettingChange) => {
  const riskData = dashboardData?.riskStatus || generateMockData().riskStatus;
  
  // Ensure controls is defined
  if (!riskData.controls) {
    riskData.controls = {
      autoTrading: false,
      odteOnly: true
    };
  }
  
  return (
    <Box sx={{ height: '100%', p: 2 }}>
      <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box component="span" sx={{ mr: 1, display: 'flex', alignItems: 'center' }}>
          <Box component="span" sx={{ color: 'warning.main', fontSize: '1.5rem' }}>
            !
          </Box>
        </Box>
                Risk Management
              </Typography>

      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
        Current Exposure
                </Typography>
      <Box 
                  sx={{ 
          width: '100%', 
                    height: 8,
          bgcolor: 'background.paper',
                    borderRadius: 1,
          overflow: 'hidden',
          mb: 2
        }}
      >
        <Box 
          sx={{ 
            width: `${riskData.currentExposure}%`, 
            height: '100%', 
            bgcolor: riskData.currentExposure > 70 
              ? 'error.main' 
              : riskData.currentExposure > 50 
                        ? 'warning.main' 
                : 'success.main',
            transition: 'width 0.5s ease'
                  }}
                />
              </Box>

      <Grid container spacing={2}>
                <Grid item xs={6}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Market Condition
          </Typography>
                  <Chip 
            label={riskData.marketCondition} 
            color={riskData.marketCondition === 'bearish' ? 'error' : 
                  riskData.marketCondition === 'bullish' ? 'success' : 'default'}
                    size="small"
            sx={{ textTransform: 'capitalize' }}
                  />
                </Grid>

                <Grid item xs={6}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Risk Level
          </Typography>
                  <Chip 
            label={riskData.riskLevel} 
            color={riskData.riskLevel === 'high' ? 'error' : 
                  riskData.riskLevel === 'moderate' ? 'warning' : 'success'}
                    size="small"
            sx={{ textTransform: 'capitalize' }}
                  />
                </Grid>
              </Grid>

      <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 2, mb: 1 }}>
        Controls
      </Typography>
              <Grid container spacing={1}>
        <Grid item xs={6}>
                  <FormControlLabel 
                    control={
                      <Switch 
                size="small" 
                checked={riskData.controls.autoTrading} 
                color="primary"
                        onChange={(e) => handleSettingChange('autoTrading', e.target.checked)}
                      />
                    } 
                    label="Auto Trading" 
                  />
                </Grid>
        
        <Grid item xs={6}>
                  <FormControlLabel 
                    control={
                      <Switch 
                size="small" 
                checked={riskData.controls.odteOnly} 
                color="primary"
                        onChange={(e) => handleSettingChange('odteOnly', e.target.checked)}
                      />
                    } 
                    label="0DTE Only" 
                  />
                </Grid>
              </Grid>
    </Box>
  );
};

const renderTopTradeSetups = (dashboardData, handleApproveSetup, handleRejectSetup) => {
  const tradeSetups = dashboardData.tradeSetups || generateMockData().tradeSetups;
  
  return (
    <Box sx={{ height: '100%', p: 2 }}>
      <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box component="span" sx={{ mr: 1, display: 'flex', alignItems: 'center' }}>
          <Box component="span" sx={{ color: 'info.main', fontSize: '1.5rem' }}>
            ⚡
          </Box>
        </Box>
        Top Trade Setups
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        {tradeSetups.map((setup, index) => (
          <Paper 
            key={index}
            variant="outlined"
            sx={{ 
              p: 1.5, 
              display: 'flex', 
              alignItems: 'center',
              borderLeft: '4px solid',
              borderLeftColor: setup.type === 'PUT' ? 'error.main' : 'success.main'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mr: 1 }}>
              {setup.type === 'CALL' ? (
                <TrendingUp color="success" />
              ) : (
                <TrendingDown color="error" />
              )}
            </Box>
            
            <Box sx={{ flexGrow: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                <Typography variant="subtitle2" component="span">
                  {setup.symbol} {setup.type}
                </Typography>
                <Chip 
                  label={`${Math.round(setup.confidence * 100)}%`} 
                  size="small" 
                  color={setup.confidence > 0.8 ? "success" : "warning"}
                  sx={{ ml: 1, height: 20 }}
                />
                <Chip 
                  label={setup.expiration} 
                  size="small" 
                  variant="outlined"
                  sx={{ ml: 1, height: 20 }}
                />
              </Box>
              <Typography variant="caption" color="text.secondary">
                {setup.recommendation} - {setup.strategy}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', ml: 1 }}>
                          <Tooltip title="Approve">
                            <IconButton 
                              edge="end" 
                              size="small" 
                              color="success"
                              onClick={() => handleApproveSetup(setup.id)}
                              sx={{ mr: 1 }}
                            >
                              <ThumbUp />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Reject">
                            <IconButton 
                              edge="end" 
                              size="small" 
                              color="error"
                              onClick={() => handleRejectSetup(setup.id)}
                            >
                              <ThumbDown />
                            </IconButton>
                          </Tooltip>
                        </Box>
          </Paper>
        ))}
                    </Box>
    </Box>
  );
};

export default CEODashboard; 