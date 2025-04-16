import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button,
  Paper,
  TextField,
  MenuItem,
  Grid,
  useTheme,
  Switch,
  FormControlLabel,
  Alert,
  Card,
  CardContent,
  Divider,
  Stack,
  IconButton
} from '@mui/material';
import { Refresh as RefreshIcon, CheckCircle as CheckIcon, Error as ErrorIcon } from '@mui/icons-material';
import TradingViewWidget from '../components/TradingViewWidget';

/**
 * Debug page for testing TradingView widgets
 */
const Debug = () => {
  const theme = useTheme();
  const [symbol, setSymbol] = useState('NASDAQ:AAPL');
  const [interval, setInterval] = useState('D');
  const [key, setKey] = useState(0); // Used to force a remount of the widget
  const [connectionStatus, setConnectionStatus] = useState(null);
  
  // Check TradingView connectivity
  useEffect(() => {
    checkTradingViewConnectivity();
  }, []);
  
  const handleSymbolChange = (e) => {
    setSymbol(e.target.value);
  };

  const handleIntervalChange = (e) => {
    setInterval(e.target.value);
  };

  const handleRefresh = () => {
    // Force remount by changing the key
    setKey(prevKey => prevKey + 1);
  };
  
  // Function to check if TradingView resources are accessible
  const checkTradingViewConnectivity = () => {
    setConnectionStatus('checking');
    
    const endpoints = [
      { url: 'https://s3.tradingview.com/tv.js', name: 'Main TradingView Script' },
      { url: 'https://s3.tradingview.com/favicon.ico', name: 'TradingView Icon' }
    ];
    
    // Test function for a single URL
    const testEndpoint = (endpoint) => {
      return new Promise((resolve) => {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
          controller.abort();
          resolve({ ...endpoint, status: 'timeout' });
        }, 5000);
        
        fetch(endpoint.url, { 
          method: 'HEAD',
          mode: 'no-cors', // This is important for cross-origin requests
          signal: controller.signal
        })
        .then(() => {
          clearTimeout(timeoutId);
          resolve({ ...endpoint, status: 'success' });
        })
        .catch(error => {
          clearTimeout(timeoutId);
          resolve({ ...endpoint, status: 'error', error: error.toString() });
        });
      });
    };
    
    // Test all endpoints
    Promise.all(endpoints.map(testEndpoint))
      .then(results => {
        console.log('TradingView connectivity test results:', results);
        setConnectionStatus(results);
      });
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        TradingView Widget Debug
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Resource Connectivity Test
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Button 
                variant="contained" 
                startIcon={<RefreshIcon />}
                onClick={checkTradingViewConnectivity}
                sx={{ mb: 2 }}
              >
                Test TradingView Connectivity
              </Button>
              
              {connectionStatus === 'checking' && (
                <Alert severity="info">Checking connectivity to TradingView resources...</Alert>
              )}
              
              {connectionStatus && Array.isArray(connectionStatus) && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>Results:</Typography>
                  
                  {connectionStatus.map((result, index) => (
                    <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      {result.status === 'success' ? (
                        <CheckIcon color="success" sx={{ mr: 1 }} />
                      ) : (
                        <ErrorIcon color="error" sx={{ mr: 1 }} />
                      )}
                      <Typography variant="body2">
                        {result.name}: {result.status === 'success' ? 'Accessible' : 'Not accessible'}
                      </Typography>
                    </Box>
                  ))}
                  
                  <Alert severity="info" sx={{ mt: 2 }}>
                    If TradingView resources are not accessible, check ad blockers and network settings.
                  </Alert>
                </Box>
              )}
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="h6" gutterBottom>
              Chart Configuration
            </Typography>
            
            <Grid container spacing={2} alignItems="center" sx={{ mb: 2 }}>
              <Grid item xs={12} sm={4}>
                <TextField
                  label="Symbol"
                  value={symbol}
                  onChange={handleSymbolChange}
                  fullWidth
                  helperText="Format: EXCHANGE:SYMBOL (e.g., NASDAQ:AAPL)"
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  select
                  label="Interval"
                  value={interval}
                  onChange={handleIntervalChange}
                  fullWidth
                >
                  <MenuItem value="1">1 Minute</MenuItem>
                  <MenuItem value="5">5 Minutes</MenuItem>
                  <MenuItem value="15">15 Minutes</MenuItem>
                  <MenuItem value="60">1 Hour</MenuItem>
                  <MenuItem value="D">1 Day</MenuItem>
                  <MenuItem value="W">1 Week</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button 
                  variant="contained" 
                  onClick={handleRefresh}
                  startIcon={<RefreshIcon />}
                  fullWidth
                >
                  Refresh Widget
                </Button>
              </Grid>
            </Grid>
            
            <Typography variant="subtitle1" gutterBottom>
              Current Configuration:
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              Symbol: {symbol}, Interval: {interval}, Key: {key}
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Paper sx={{ height: '600px', overflow: 'hidden' }}>
            <TradingViewWidget 
              symbol={symbol}
              interval={interval}
              containerId={`debug_chart_${symbol}`}
              key={`${symbol}_${interval}_${key}`} // Adding key to force remount
            />
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Troubleshooting Guide</Typography>
              
              <Typography variant="subtitle1" gutterBottom>
                Common Issues:
              </Typography>
              
              <Box component="ul" sx={{ pl: 2 }}>
                <li>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Ad Blockers:</strong> TradingView scripts may be blocked by ad blockers. Try disabling ad blockers for this site.
                  </Typography>
                </li>
                
                <li>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Network Issues:</strong> If you're behind a corporate firewall or using a VPN, it might block access to TradingView resources.
                  </Typography>
                </li>
                
                <li>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Invalid Symbol Format:</strong> Make sure to include the exchange prefix (e.g., "NASDAQ:AAPL" not just "AAPL").
                  </Typography>
                </li>
                
                <li>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Script Loading Timing:</strong> Sometimes the script needs more time to load. Try refreshing the widget.
                  </Typography>
                </li>
                
                <li>
                  <Typography variant="body2">
                    <strong>Browser Console:</strong> Check the browser console (F12) for more detailed error messages.
                  </Typography>
                </li>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Debug; 