import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Alert,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Chip,
  Grid
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import axios from 'axios';

const TradingViewAlerts = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [showWebhookInstructions, setShowWebhookInstructions] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(null);

  useEffect(() => {
    fetchAlerts();

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchAlerts();
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
  }, [autoRefresh]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/market-data/tradingview/webhooks');
      if (response.data.success) {
        setAlerts(response.data.alerts || []);
      } else {
        setError('Failed to fetch TradingView alerts: ' + response.data.error);
      }
    } catch (err) {
      setError('Error fetching TradingView alerts: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const clearAlerts = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/market-data/tradingview/clear-webhooks');
      if (response.data.success) {
        setAlerts([]);
        setSuccess('All TradingView alerts cleared');
      } else {
        setError('Failed to clear TradingView alerts: ' + response.data.error);
      }
    } catch (err) {
      setError('Error clearing TradingView alerts: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (e) {
      return timestamp || 'N/A';
    }
  };

  const renderAlertData = (data) => {
    if (!data) return 'No data';
    
    try {
      if (typeof data === 'string') {
        // Try to parse if it's a JSON string
        try {
          data = JSON.parse(data);
        } catch (e) {
          // It's just a string, not JSON
          return data;
        }
      }
      
      // If it's an object, render as key-value pairs
      return (
        <List dense sx={{ bgcolor: 'background.paper', borderRadius: 1 }}>
          {Object.entries(data).map(([key, value]) => (
            <React.Fragment key={key}>
              <ListItem>
                <ListItemText
                  primary={<Typography variant="caption" fontWeight="bold">{key}</Typography>}
                  secondary={
                    typeof value === 'object' 
                      ? JSON.stringify(value) 
                      : String(value)
                  }
                />
              </ListItem>
              <Divider component="li" />
            </React.Fragment>
          ))}
        </List>
      );
    } catch (e) {
      return String(data);
    }
  };

  return (
    <Box sx={{ mt: 3, mb: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          TradingView Webhook Alerts
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}
        
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={4}>
            <Button
              variant="contained"
              startIcon={<RefreshIcon />}
              onClick={fetchAlerts}
              disabled={loading}
              fullWidth
            >
              {loading ? 'Loading...' : 'Refresh Alerts'}
            </Button>
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <Button
              variant="outlined"
              color="primary"
              onClick={toggleAutoRefresh}
              fullWidth
            >
              {autoRefresh ? 'Disable Auto-Refresh' : 'Enable Auto-Refresh (5s)'}
            </Button>
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={clearAlerts}
              disabled={loading || alerts.length === 0}
              fullWidth
            >
              Clear All Alerts
            </Button>
          </Grid>
        </Grid>
        
        <Box sx={{ mb: 3 }}>
          <Button
            variant="text"
            startIcon={<CodeIcon />}
            onClick={() => setShowWebhookInstructions(!showWebhookInstructions)}
          >
            {showWebhookInstructions ? 'Hide Webhook Instructions' : 'Show Webhook Instructions'}
          </Button>
          
          {showWebhookInstructions && (
            <Card sx={{ mt: 2, backgroundColor: '#f5f5f5' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  How to Set Up TradingView Webhooks
                </Typography>
                
                <Typography variant="body2" paragraph>
                  1. In TradingView, create an alert and select "Webhook URL" as the notification method.
                </Typography>
                
                <Typography variant="body2" paragraph>
                  2. Enter the following webhook URL (replace YOUR_SERVER_IP with your server's IP or domain):
                </Typography>
                
                <Typography 
                  variant="body2" 
                  sx={{ 
                    backgroundColor: '#e0e0e0', 
                    p: 1, 
                    borderRadius: 1,
                    fontFamily: 'monospace'
                  }}
                >
                  http://YOUR_SERVER_IP:5001/tradingview-webhook
                </Typography>
                
                <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                  3. In the "Message" field, enter your JSON payload. Example:
                </Typography>
                
                <Typography 
                  variant="body2" 
                  sx={{ 
                    backgroundColor: '#e0e0e0', 
                    p: 1, 
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap'
                  }}
                >
{`{
  "symbol": "{{ticker}}",
  "action": "{{strategy.order.action}}",
  "price": {{close}},
  "time": "{{time}}"
}`}
                </Typography>
                
                <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                  4. Save the alert and it will send data to this dashboard when triggered.
                </Typography>
              </CardContent>
            </Card>
          )}
        </Box>
        
        <Typography variant="subtitle1" gutterBottom>
          Recent Alerts {alerts.length > 0 && `(${alerts.length})`}
        </Typography>
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {alerts.length === 0 ? (
              <Alert severity="info">
                No TradingView alerts received yet. Set up a webhook in TradingView to send alerts here.
              </Alert>
            ) : (
              <Box>
                {alerts.map((alert, index) => (
                  <Card key={index} sx={{ mb: 2 }}>
                    <CardHeader
                      title={
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="subtitle1">
                            Alert #{alerts.length - index}
                          </Typography>
                          {alert.data?.symbol && (
                            <Chip 
                              label={alert.data.symbol} 
                              size="small" 
                              color="primary" 
                              sx={{ ml: 1 }}
                            />
                          )}
                          {alert.data?.action && (
                            <Chip 
                              label={alert.data.action} 
                              size="small" 
                              color={alert.data.action.toLowerCase().includes('buy') ? 'success' : 'error'} 
                              sx={{ ml: 1 }}
                            />
                          )}
                        </Box>
                      }
                      subheader={`Received: ${formatTimestamp(alert.timestamp)}`}
                    />
                    <Divider />
                    <CardContent>
                      {renderAlertData(alert.data)}
                    </CardContent>
                  </Card>
                ))}
              </Box>
            )}
          </>
        )}
      </Paper>
    </Box>
  );
};

export default TradingViewAlerts; 