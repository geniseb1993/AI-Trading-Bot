import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Alert,
  Grid,
  Switch,
  FormControlLabel,
  Card,
  CardContent,
  CardHeader,
  Divider,
  CircularProgress,
  Chip
} from '@mui/material';
import axios from 'axios';
import brokerService from '../services/brokerService';

const BrokerSettings = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [brokers, setBrokers] = useState([]);
  const [activeBroker, setActiveBroker] = useState('');
  const [config, setConfig] = useState({});
  const [updatedConfig, setUpdatedConfig] = useState({});
  const [showApiKeys, setShowApiKeys] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatuses, setConnectionStatuses] = useState({});

  useEffect(() => {
    fetchBrokers();
    fetchConfig();
  }, []);

  const fetchBrokers = async () => {
    try {
      const response = await brokerService.getAvailableBrokers();
      if (response.success) {
        setBrokers(response.brokers || []);
        setActiveBroker(response.active_broker || '');
      } else {
        throw new Error(response.error || 'Failed to fetch brokers');
      }
    } catch (err) {
      console.error('Error fetching brokers:', err);
      setError('Failed to load broker list');
    } finally {
      setLoading(false);
    }
  };

  const fetchConfig = async () => {
    try {
      const response = await brokerService.getConfig();
      if (response.success) {
        setConfig(response.config || {});
        setUpdatedConfig(response.config || {});
      } else {
        throw new Error(response.error || 'Failed to fetch config');
      }
    } catch (err) {
      console.error('Error fetching broker config:', err);
      setError('Failed to load broker configuration');
    }
  };

  const handleBrokerChange = async (event) => {
    const newBroker = event.target.value;
    try {
      setLoading(true);
      const response = await brokerService.setActiveBroker(newBroker);
      if (response.success) {
        setActiveBroker(newBroker);
        setSuccess(`Active broker set to ${newBroker}`);
      } else {
        setError('Failed to set active broker: ' + response.error);
      }
    } catch (err) {
      setError('Error setting active broker: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = (broker, key, value) => {
    setUpdatedConfig((prevConfig) => {
      const newConfig = { ...prevConfig };
      if (broker === 'active_broker') {
        newConfig[broker] = value;
      } else {
        if (!newConfig[broker]) {
          newConfig[broker] = {};
        }
        newConfig[broker][key] = value;
      }
      return newConfig;
    });
  };

  const saveConfig = async () => {
    try {
      setLoading(true);
      const response = await brokerService.updateConfig(updatedConfig);
      if (response.success) {
        setConfig(updatedConfig);
        setSuccess('Broker configuration updated successfully');
      } else {
        setError('Failed to update configuration: ' + response.error);
      }
    } catch (err) {
      setError('Error updating configuration: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (broker) => {
    try {
      setTestingConnection(true);
      setConnectionStatuses(prev => ({
        ...prev,
        [broker]: { status: 'testing', message: 'Testing connection...' }
      }));
      
      const response = await brokerService.testConnection(broker);
      
      if (response.success) {
        setConnectionStatuses(prev => ({
          ...prev,
          [broker]: { 
            status: 'success',
            message: response.message,
            details: response.details
          }
        }));
      } else {
        setConnectionStatuses(prev => ({
          ...prev,
          [broker]: { 
            status: 'error',
            message: response.error || 'Connection test failed' 
          }
        }));
      }
    } catch (err) {
      setConnectionStatuses(prev => ({
        ...prev,
        [broker]: { 
          status: 'error',
          message: err.message || 'Connection test failed' 
        }
      }));
    } finally {
      setTestingConnection(false);
    }
  };

  const renderConnectionStatus = (broker) => {
    const status = connectionStatuses[broker];
    
    if (!status) {
      return null;
    }
    
    if (status.status === 'testing') {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
          <CircularProgress size={16} sx={{ mr: 1 }} />
          <Typography variant="body2">{status.message}</Typography>
        </Box>
      );
    }
    
    if (status.status === 'success') {
      return (
        <Box sx={{ mt: 1 }}>
          <Chip 
            label="Connected" 
            size="small" 
            color="success" 
            sx={{ mb: 1 }}
          />
          {status.details && (
            <Typography variant="body2" sx={{ mt: 0.5 }}>
              Account ID: {status.details.account_id || 'Unknown'}
            </Typography>
          )}
        </Box>
      );
    }
    
    if (status.status === 'error') {
      return (
        <Box sx={{ mt: 1 }}>
          <Chip 
            label="Connection Failed" 
            size="small" 
            color="error" 
            sx={{ mb: 1 }}
          />
          <Typography variant="body2" color="error" sx={{ mt: 0.5 }}>
            {status.message}
          </Typography>
        </Box>
      );
    }
    
    return null;
  };

  const renderConfigForm = () => {
    if (!config || Object.keys(config).length === 0) {
      return <Typography>No configuration available</Typography>;
    }

    return Object.entries(config)
      .filter(([broker]) => broker !== 'active_broker')
      .map(([broker, brokerConfig]) => (
        <Card key={broker} sx={{ mb: 3 }}>
          <CardHeader 
            title={broker.charAt(0).toUpperCase() + broker.slice(1).replace('_', ' ')} 
            subheader={broker === activeBroker ? 'Active Broker' : 'Inactive'}
            sx={{
              bgcolor: broker === activeBroker ? 'primary.main' : 'background.paper',
              color: broker === activeBroker ? 'primary.contrastText' : 'text.primary',
              '& .MuiCardHeader-subheader': {
                color: broker === activeBroker ? 'primary.contrastText' : 'text.secondary',
                opacity: broker === activeBroker ? 0.8 : 0.6
              }
            }}
            action={
              <Button 
                variant="outlined" 
                size="small"
                color={broker === activeBroker ? 'inherit' : 'primary'}
                onClick={() => testConnection(broker)}
                disabled={testingConnection}
                sx={{ 
                  mr: 1,
                  color: broker === activeBroker ? 'primary.contrastText' : 'primary.main',
                  borderColor: broker === activeBroker ? 'primary.contrastText' : 'primary.main'
                }}
              >
                Test Connection
              </Button>
            }
          />
          <Divider />
          <CardContent>
            {renderConnectionStatus(broker)}
            <Grid container spacing={2} sx={{ mt: 1 }}>
              {Object.entries(brokerConfig).map(([key, value]) => {
                const isSecret = key.toLowerCase().includes('key') || 
                               key.toLowerCase().includes('secret') ||
                               key.toLowerCase().includes('token') ||
                               key.toLowerCase().includes('password');
                               
                const isBoolean = typeof value === 'boolean';
                
                if (isBoolean) {
                  return (
                    <Grid item xs={12} sm={6} key={key}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={updatedConfig[broker]?.[key] || false}
                            onChange={(e) => handleConfigChange(broker, key, e.target.checked)}
                            color="primary"
                          />
                        }
                        label={key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}
                      />
                    </Grid>
                  );
                }
                
                return (
                  <Grid item xs={12} sm={6} key={key}>
                    <TextField
                      fullWidth
                      label={key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}
                      value={updatedConfig[broker]?.[key] || ''}
                      onChange={(e) => handleConfigChange(broker, key, e.target.value)}
                      type={isSecret && !showApiKeys ? 'password' : 'text'}
                    />
                  </Grid>
                );
              })}
            </Grid>
          </CardContent>
        </Card>
      ));
  };

  return (
    <Box sx={{ mt: 3, mb: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Broker Configuration
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
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Box sx={{ mb: 3 }}>
              <FormControl fullWidth>
                <InputLabel id="active-broker-label">Active Broker</InputLabel>
                <Select
                  labelId="active-broker-label"
                  value={activeBroker}
                  onChange={handleBrokerChange}
                  label="Active Broker"
                >
                  {brokers.map((broker) => (
                    <MenuItem key={broker} value={broker}>
                      {broker.charAt(0).toUpperCase() + broker.slice(1).replace('_', ' ')}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
            
            <Box sx={{ mb: 3 }}>
              <FormControlLabel
                control={<Switch checked={showApiKeys} onChange={() => setShowApiKeys(!showApiKeys)} />}
                label="Show API Keys"
              />
            </Box>
            
            {renderConfigForm()}
            
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                color="primary"
                onClick={saveConfig}
                disabled={loading || testingConnection}
              >
                Save Configuration
              </Button>
            </Box>
          </>
        )}
      </Paper>
    </Box>
  );
};

export default BrokerSettings; 