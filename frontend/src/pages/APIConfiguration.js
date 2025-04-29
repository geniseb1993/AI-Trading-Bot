import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  TextField, 
  Button,
  Divider,
  FormControlLabel,
  Switch,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Alert,
  Snackbar,
  Card,
  CardContent,
  CardActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Tooltip,
  CircularProgress
} from '@mui/material';
import { 
  Save as SaveIcon, 
  CheckCircle as CheckCircleIcon, 
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Check as CheckIcon,
  Error as ErrorIconMUI
} from '@mui/icons-material';
import { useApiConfigurationData } from '../contexts/DataContext';
import { apiConfigurationService } from '../services/api';

const APIConfiguration = () => {
  // Use the domain-specific hook from DataContext
  const {
    data: apiConfigs,
    loading,
    error,
    updateData: setApiConfigs,
    setLoading,
    setError
  } = useApiConfigurationData();
  
  // Local component state
  const [showSecrets, setShowSecrets] = useState({
    alphavantage: false,
    polygon: false,
    tradingview: false,
    finnhub: false,
    marketaux: false,
    alpaca: false,
    unusual_whales: false,
    openai: false,
    humeai: false
  });
  
  const [testStatus, setTestStatus] = useState({});
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    fetchApiConfigs();
  }, []);

  const fetchApiConfigs = async () => {
    try {
      setLoading(true);
      const response = await apiConfigurationService.getApiConfigs();
      
      if (response && response.success) {
        setApiConfigs(response.configs || {});
      } else {
        console.log("Using default API configurations with pre-configured API keys");
        // Keep using the default values defined in state
      }
    } catch (error) {
      console.error('Error fetching API configurations:', error);
      setError('Failed to load API configurations');
    }
  };

  const handleInputChange = (service, field, value) => {
    setApiConfigs(prev => ({
      ...prev,
      [service]: {
        ...prev[service],
        [field]: value
      }
    }));
  };

  const toggleShowSecret = (service) => {
    setShowSecrets(prev => ({
      ...prev,
      [service]: !prev[service]
    }));
  };

  const saveConfigs = async () => {
    try {
      setLoading(true);
      const response = await apiConfigurationService.saveApiConfigs(apiConfigs);
      
      if (response && response.success) {
        setSnackbar({
          open: true,
          message: 'API configurations saved successfully!',
          severity: 'success'
        });
      } else {
        throw new Error(response.error || 'Failed to save API configurations');
      }
    } catch (error) {
      console.error('Error saving API configurations:', error);
      setSnackbar({
        open: true,
        message: `Error: ${error.message || 'Failed to save API configurations'}`,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (service) => {
    try {
      setTestStatus(prev => ({
        ...prev,
        [service]: { loading: true }
      }));
      
      const response = await apiConfigurationService.testApiConnection({ service });
      
      if (response && response.success) {
        setTestStatus(prev => ({
          ...prev,
          [service]: { 
            loading: false, 
            success: true,
            message: response.message || 'Connection successful!'
          }
        }));
      } else {
        throw new Error(response.error || 'Connection test failed');
      }
    } catch (error) {
      console.error(`Error testing ${service} connection:`, error);
      setTestStatus(prev => ({
        ...prev,
        [service]: { 
          loading: false, 
          success: false,
          message: error.message || 'Connection test failed'
        }
      }));
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({
      ...prev,
      open: false
    }));
  };

  const renderApiConfigCard = (serviceName, serviceConfig) => {
    const formattedServiceName = serviceName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
      
    return (
      <Grid item xs={12} md={6} key={serviceName}>
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">{formattedServiceName}</Typography>
              <Chip 
                label={testStatus[serviceName]?.success ? 'Connected' : 'Disconnected'} 
                color={testStatus[serviceName]?.success ? 'success' : 'error'}
                icon={testStatus[serviceName]?.success ? <CheckCircleIcon /> : <ErrorIcon />}
                size="small" 
              />
            </Box>
            
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              {serviceConfig.description}
            </Typography>
            
            <Grid container spacing={2}>
              {Object.entries(serviceConfig).map(([key, value]) => {
                // Skip non-form fields
                if (['connected', 'description'].includes(key)) return null;
                
                if (key === 'enabled') {
                  return (
                    <Grid item xs={12} key={key}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={value}
                            onChange={(e) => handleInputChange(serviceName, key, e.target.checked)}
                            color="primary"
                          />
                        }
                        label={`Enable ${formattedServiceName}`}
                      />
                    </Grid>
                  );
                }
                
                if (key.includes('secret') || key.includes('api_secret') || key.includes('password') || key.includes('api_key')) {
                  return (
                    <Grid item xs={12} sm={6} key={key}>
                      <TextField
                        fullWidth
                        label={key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                        value={value}
                        onChange={(e) => handleInputChange(serviceName, key, e.target.value)}
                        type={showSecrets[serviceName] ? 'text' : 'password'}
                        InputProps={{
                          endAdornment: (
                            <IconButton
                              aria-label="toggle password visibility"
                              onClick={() => toggleShowSecret(serviceName)}
                              edge="end"
                            >
                              {showSecrets[serviceName] ? <VisibilityOffIcon /> : <VisibilityIcon />}
                            </IconButton>
                          ),
                        }}
                      />
                    </Grid>
                  );
                }
                
                return (
                  <Grid item xs={12} sm={6} key={key}>
                    <TextField
                      fullWidth
                      label={key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                      value={value}
                      onChange={(e) => handleInputChange(serviceName, key, e.target.value)}
                    />
                  </Grid>
                );
              })}
            </Grid>
          </CardContent>
          
          <CardActions sx={{ justifyContent: 'flex-end' }}>
            <Button 
              size="small" 
              onClick={() => testConnection(serviceName)}
              disabled={testStatus[serviceName]?.loading || !serviceConfig.api_key}
              startIcon={
                testStatus[serviceName]?.loading ? <CircularProgress size={16} /> :
                testStatus[serviceName]?.success ? <CheckIcon /> : 
                testStatus[serviceName]?.success === false ? <ErrorIconMUI /> : null
              }
            >
              {testStatus[serviceName]?.loading ? 'Testing...' : testStatus[serviceName]?.success ? 'Connected' : 'Test Connection'}
            </Button>
          </CardActions>
        </Card>
      </Grid>
    );
  };

  return (
    <Box sx={{ p: 3, minHeight: '100vh' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">API Configuration</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<SaveIcon />}
          onClick={saveConfigs}
          disabled={loading}
        >
          {loading ? <CircularProgress size={20} /> : 'Save All Configurations'}
        </Button>
      </Box>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Configure your API connections below. API keys are securely stored and encrypted.
      </Alert>
      
      <Grid container spacing={3}>
        {Object.entries(apiConfigs).map(([serviceName, serviceConfig]) => 
          renderApiConfigCard(serviceName, serviceConfig)
        )}
      </Grid>
      
      <Box sx={{ mt: 4 }}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">API Connection Help</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <List>
              <ListItem>
                <ListItemText 
                  primary="Alpaca API" 
                  secondary="Sign up at alpaca.markets and create API keys in your dashboard. Choose paper trading for testing."
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="Interactive Brokers" 
                  secondary="Install TWS or IB Gateway and enable API connections in the settings. The default port is 7496 for TWS and 4001 for IB Gateway."
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="TradingView Webhooks" 
                  secondary="Create alerts in TradingView and set the webhook URL to your server: http://your-server-ip:5001/tradingview-webhook"
                />
              </ListItem>
              <Divider component="li" />
              <ListItem>
                <ListItemText 
                  primary="Unusual Whales" 
                  secondary="Your Unusual Whales API key is already configured and connected. This provides options flow data and unusual options activity detection."
                />
              </ListItem>
            </List>
          </AccordionDetails>
        </Accordion>
      </Box>
      
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default APIConfiguration; 