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
  FormControlLabel
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
  ThumbDown
} from '@mui/icons-material';
import axios from 'axios';
import { motion } from 'framer-motion';

// Define API base URL based on environment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * Hook for fetching CEO dashboard data
 */
export const useCEODashboardData = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    performance: null,
    tradeSetups: [],
    riskStatus: null,
    systemHealth: null
  });
  const [settings, setSettings] = useState({
    autoTrading: false,
    riskLevel: 'moderate',
    maxDailyTrades: 5,
    stopLossPercent: 2.0,
    odteOnly: true
  });

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch CEO dashboard data
      const dashboardResponse = await axios.get(`${API_BASE_URL}/ceo-dashboard`);
      
      if (dashboardResponse.data && dashboardResponse.data.success) {
        setDashboardData(dashboardResponse.data);
      } else {
        // If API is not available, use mock data
        setDashboardData(generateMockData());
      }
    } catch (error) {
      console.error('Error fetching CEO dashboard data:', error);
      setError('Could not load CEO dashboard data. Using sample data instead.');
      setDashboardData(generateMockData());
    } finally {
      setLoading(false);
    }
  };

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
      riskStatus: {
        currentExposure: 35,
        maxExposure: 80,
        dailyPnLRisk: 15,
        marketCondition: 'Bullish',
        volatilityLevel: 'Moderate',
        riskLevel: 'Moderate',
        warningMessage: null
      },
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

  const handleSettingChange = (setting, value) => {
    setSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  // Initial data fetch
  useEffect(() => {
    fetchDashboardData();
  }, []);

  return {
    loading,
    error,
    dashboardData,
    settings,
    handleSettingChange,
    refreshData: fetchDashboardData
  };
};

/**
 * CEO Performance Metrics Component
 */
export const CEOPerformanceMetrics = ({ data, loading }) => {
  const theme = useTheme();
  
  if (loading || !data || !data.performance) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }
  
  return (
    <Box sx={{ mb: 2 }}>
      <Typography variant="h6" sx={{ mb: 2, fontFamily: 'Orbitron' }}>
        <MonetizationOn sx={{ mr: 1, verticalAlign: 'middle' }} />
        Performance Metrics
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">Daily P&L</Typography>
          <Typography variant="h6" sx={{ 
            color: data.performance.dailyPnL >= 0 ? 'success.main' : 'error.main',
            fontWeight: 'bold'
          }}>
            {data.performance.dailyPnL >= 0 ? '+' : ''}{data.performance.dailyPnL.toFixed(2)}%
          </Typography>
        </Grid>
        
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">Win Rate</Typography>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            {data.performance.winRate}%
          </Typography>
        </Grid>

        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">Weekly P&L</Typography>
          <Typography variant="h6" sx={{ 
            color: data.performance.weeklyPnL >= 0 ? 'success.main' : 'error.main',
            fontWeight: 'bold'
          }}>
            {data.performance.weeklyPnL >= 0 ? '+' : ''}{data.performance.weeklyPnL.toFixed(2)}%
          </Typography>
        </Grid>

        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">Total Trades</Typography>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            {data.performance.totalTrades}
          </Typography>
        </Grid>
      </Grid>

      <Divider sx={{ my: 2 }} />

      <Grid container spacing={2}>
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">Avg Win</Typography>
          <Typography variant="body1" color="success.main" sx={{ fontWeight: 'bold' }}>
            +{data.performance.avgWin.toFixed(2)}%
          </Typography>
        </Grid>

        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">Avg Loss</Typography>
          <Typography variant="body1" color="error.main" sx={{ fontWeight: 'bold' }}>
            {data.performance.avgLoss.toFixed(2)}%
          </Typography>
        </Grid>
      </Grid>
    </Box>
  );
};

/**
 * CEO Risk Management Component
 */
export const CEORiskManagement = ({ data, settings, onSettingChange, loading }) => {
  const theme = useTheme();
  
  if (loading || !data || !data.riskStatus) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }
  
  return (
    <Box sx={{ mb: 2 }}>
      <Typography variant="h6" sx={{ mb: 2, fontFamily: 'Orbitron' }}>
        <Warning sx={{ mr: 1, verticalAlign: 'middle' }} />
        Risk Management
      </Typography>

      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" display="flex" justifyContent="space-between">
          <span>Current Exposure</span>
          <span>{data.riskStatus.currentExposure}%</span>
        </Typography>
        <LinearProgress 
          variant="determinate" 
          value={data.riskStatus.currentExposure} 
          sx={{ 
            mt: 1,
            height: 8,
            borderRadius: 1,
            backgroundColor: alpha(theme.palette.primary.main, 0.1),
            '& .MuiLinearProgress-bar': {
              borderRadius: 1,
              backgroundColor: data.riskStatus.currentExposure > 60 
                ? 'warning.main' 
                : 'success.main'
            }
          }}
        />
      </Box>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">Market Condition</Typography>
          <Chip 
            label={data.riskStatus.marketCondition} 
            size="small"
            color={
              data.riskStatus.marketCondition === 'Bullish' 
                ? 'success' 
                : data.riskStatus.marketCondition === 'Bearish' 
                  ? 'error' 
                  : 'warning'
            }
            sx={{ mt: 0.5 }}
          />
        </Grid>

        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">Risk Level</Typography>
          <Chip 
            label={data.riskStatus.riskLevel} 
            size="small"
            color={
              data.riskStatus.riskLevel === 'Low' 
                ? 'success' 
                : data.riskStatus.riskLevel === 'High' 
                  ? 'error' 
                  : 'warning'
            }
            sx={{ mt: 0.5 }}
          />
        </Grid>
      </Grid>

      <Divider sx={{ my: 2 }} />

      <Typography variant="body2" sx={{ mb: 1 }}>Controls</Typography>
      <Grid container spacing={1}>
        <Grid item xs={12}>
          <FormControlLabel 
            control={
              <Switch 
                checked={settings.autoTrading} 
                onChange={(e) => onSettingChange('autoTrading', e.target.checked)}
                color="primary"
                size="small"
              />
            } 
            label="Auto Trading" 
          />
        </Grid>
        <Grid item xs={12}>
          <FormControlLabel 
            control={
              <Switch 
                checked={settings.odteOnly} 
                onChange={(e) => onSettingChange('odteOnly', e.target.checked)}
                color="primary"
                size="small"
              />
            } 
            label="0DTE Only" 
          />
        </Grid>
      </Grid>
    </Box>
  );
};

/**
 * CEO Trade Setups Component
 */
export const CEOTradeSetups = ({ data, loading, onApprove, onReject }) => {
  const theme = useTheme();
  
  if (loading || !data || !data.tradeSetups || data.tradeSetups.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }
  
  return (
    <Box sx={{ mb: 2 }}>
      <Typography variant="h6" sx={{ mb: 2, fontFamily: 'Orbitron' }}>
        <FlashOn sx={{ mr: 1, verticalAlign: 'middle' }} />
        Top Trade Setups
      </Typography>

      <List sx={{ width: '100%', p: 0 }}>
        {data.tradeSetups.map((setup, index) => (
          <React.Fragment key={setup.id}>
            {index > 0 && <Divider component="li" />}
            <ListItem 
              alignItems="flex-start"
              secondaryAction={
                <Box>
                  <Tooltip title="Approve">
                    <IconButton 
                      edge="end" 
                      size="small" 
                      color="success"
                      onClick={() => onApprove(setup.id)}
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
                      onClick={() => onReject(setup.id)}
                    >
                      <ThumbDown />
                    </IconButton>
                  </Tooltip>
                </Box>
              }
              sx={{ py: 1.5 }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {setup.type === 'CALL' ? (
                  <TrendingUp color="success" />
                ) : (
                  <TrendingDown color="error" />
                )}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
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
                }
                secondary={
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    {setup.recommendation} - {setup.strategy}
                  </Typography>
                }
              />
            </ListItem>
          </React.Fragment>
        ))}
      </List>
    </Box>
  );
};

/**
 * CEO System Health Component
 */
export const CEOSystemHealth = ({ data, loading }) => {
  const theme = useTheme();
  
  if (loading || !data || !data.systemHealth || !data.systemHealth.components) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }
  
  return (
    <Box sx={{ mb: 2 }}>
      <Typography variant="h6" sx={{ mb: 2, fontFamily: 'Orbitron' }}>
        <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
        System Health
      </Typography>

      <Grid container spacing={2}>
        {Object.entries(data.systemHealth.components).map(([name, componentData]) => (
          <Grid item xs={6} sm={3} key={name}>
            <Box sx={{ 
              p: 1.5, 
              borderRadius: 1,
              backgroundColor: alpha(
                componentData.status === 'operational' 
                  ? theme.palette.success.main 
                  : theme.palette.error.main, 
                0.1
              ),
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {componentData.status === 'operational' ? (
                <Check fontSize="small" color="success" />
              ) : (
                <Warning fontSize="small" color="error" />
              )}
              <Typography variant="body2" sx={{ 
                textTransform: 'capitalize',
                mt: 0.5,
                fontWeight: 'medium'
              }}>
                {name.replace(/([A-Z])/g, ' $1').trim()}
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {componentData.latency}ms
              </Typography>
            </Box>
          </Grid>
        ))}
      </Grid>

      <Typography variant="caption" sx={{ display: 'block', mt: 2, textAlign: 'right', color: 'text.secondary' }}>
        Last updated: {new Date(data.systemHealth.lastUpdated).toLocaleTimeString()}
      </Typography>
    </Box>
  );
}; 