import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  CircularProgress,
  useTheme,
  alpha,
  Chip,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Error as ErrorIcon,
  Refresh
} from '@mui/icons-material';
import axios from 'axios';

/**
 * DualBotDashboard component integrates Dual Bot data with existing dashboard components
 */
const DualBotDashboard = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [botStatus, setBotStatus] = useState(null);
  const [signals, setSignals] = useState([]);

  useEffect(() => {
    fetchBotStatus();
    fetchSignals();
  }, []);

  const fetchBotStatus = async () => {
    try {
      const response = await axios.get('/api/dual-bot/status');
      if (response.data.success) {
        setBotStatus(response.data.status);
      } else {
        setError('Failed to fetch bot status');
      }
    } catch (error) {
      setError(`Error fetching bot status: ${error.message}`);
    }
  };

  const fetchSignals = async () => {
    try {
      const response = await axios.get('/api/dual-bot/signals');
      if (response.data.success) {
        setSignals(response.data.data.signals || []);
      } else {
        setError('Failed to fetch signals');
      }
    } catch (error) {
      setError(`Error fetching signals: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setLoading(true);
    fetchBotStatus();
    fetchSignals();
  };

  const renderComponentStatus = (isActive, name) => {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {isActive ? (
          <CheckCircle color="success" />
        ) : (
          <ErrorIcon color="error" />
        )}
        <Typography variant="body1">
          {name}: {isActive ? 'Active' : 'Inactive'}
        </Typography>
      </Box>
    );
  };

  const renderSignal = (signal) => {
    const isBuy = signal.type === 'BUY';
    return (
      <Card 
        key={`${signal.symbol}-${signal.time}`}
        sx={{ 
          mb: 2,
          backgroundColor: alpha(
            isBuy ? theme.palette.success.main : theme.palette.error.main,
            0.1
          )
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" sx={{ fontFamily: 'Orbitron' }}>
              {signal.symbol}
            </Typography>
            <Chip
              icon={isBuy ? <TrendingUp /> : <TrendingDown />}
              label={signal.type}
              color={isBuy ? 'success' : 'error'}
            />
          </Box>
          <Divider sx={{ my: 1 }} />
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Price: ${signal.price.toFixed(2)}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Confidence: {(signal.confidence * 100).toFixed(0)}%
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="caption" color="text.secondary">
                Volume: {signal.volume.toLocaleString()}
              </Typography>
            </Grid>
            {signal.indicators && (
              <Grid item xs={12}>
                <Typography variant="caption" color="text.secondary" component="div">
                  EMA9: {signal.indicators.ema_9?.toFixed(2)}
                </Typography>
                <Typography variant="caption" color="text.secondary" component="div">
                  EMA21: {signal.indicators.ema_21?.toFixed(2)}
                </Typography>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Card sx={{ mb: 3, backgroundColor: alpha(theme.palette.error.main, 0.1) }}>
          <CardContent>
            <Typography color="error" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ErrorIcon />
              {error}
            </Typography>
          </CardContent>
        </Card>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontFamily: 'Orbitron' }}>
          Dual Bot Dashboard
        </Typography>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={handleRefresh}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontFamily: 'Orbitron' }}>
                Bot Status
              </Typography>
              {botStatus && botStatus.components && (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {renderComponentStatus(botStatus.components.data_fetcher, 'Data Fetcher')}
                  {renderComponentStatus(botStatus.components.signal_generator, 'Signal Generator')}
                  {renderComponentStatus(botStatus.components.risk_manager, 'Risk Manager')}
                  {renderComponentStatus(botStatus.components.execution_engine, 'Execution Engine')}
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    Last Updated: {new Date(botStatus.last_updated).toLocaleString()}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontFamily: 'Orbitron' }}>
                Active Signals
              </Typography>
              {signals.length > 0 ? (
                signals.map(renderSignal)
              ) : (
                <Typography color="text.secondary" sx={{ textAlign: 'center' }}>
                  No active signals
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DualBotDashboard; 