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
  CircularProgress
} from '@mui/material';
import axios from 'axios';

const MarketDataConfig = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [sources, setSources] = useState([]);
  const [activeSource, setActiveSource] = useState('');
  const [config, setConfig] = useState({});
  const [updatedConfig, setUpdatedConfig] = useState({});
  const [showApiKeys, setShowApiKeys] = useState(false);

  useEffect(() => {
    fetchSources();
    fetchConfig();
  }, []);

  const fetchSources = async () => {
    try {
      const response = await axios.get('/api/market-data/sources');
      if (response.data.success) {
        setSources(response.data.sources || []);
        setActiveSource(response.data.active_source || '');
      } else {
        throw new Error(response.data.error || 'Failed to fetch sources');
      }
    } catch (err) {
      console.error('Error fetching market data sources:', err);
      setError('Failed to load market data sources');
      
      // Provide mock sources when API is down
      setSources(['alpaca', 'interactive_brokers', 'tradingview', 'unusual_whales']);
      setActiveSource('alpaca');
    }
  };

  const fetchConfig = async () => {
    try {
      const response = await axios.get('/api/market-data/config');
      if (response.data.success) {
        setConfig(response.data.config || {});
      } else {
        throw new Error(response.data.error || 'Failed to fetch config');
      }
    } catch (err) {
      console.error('Error fetching market data config:', err);
      setError('Failed to load market data configuration');
      
      // Provide mock configuration when API is down
      setConfig({
        active_source: 'alpaca',
        alpaca: {
          api_key: '**********',
          api_secret: '**********',
          paper_trading: true
        },
        interactive_brokers: {
          tws_port: 7497,
          client_id: 1
        },
        tradingview: {
          webhook_port: 5001
        },
        unusual_whales: {
          api_key: '**********'
        }
      });
    }
  };

  const handleSourceChange = async (event) => {
    const newSource = event.target.value;
    try {
      setLoading(true);
      const response = await axios.post('/api/market-data/set-source', { source: newSource });
      if (response.data.success) {
        setActiveSource(newSource);
        setSuccess(`Active market data source set to ${newSource}`);
      } else {
        setError('Failed to set active source: ' + response.data.error);
      }
    } catch (err) {
      setError('Error setting active source: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = (source, key, value) => {
    setUpdatedConfig((prevConfig) => {
      const newConfig = { ...prevConfig };
      if (source === 'active_source') {
        newConfig[source] = value;
      } else {
        if (!newConfig[source]) {
          newConfig[source] = {};
        }
        newConfig[source][key] = value;
      }
      return newConfig;
    });
  };

  const saveConfig = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/market-data/update-config', updatedConfig);
      if (response.data.success) {
        setConfig(updatedConfig);
        setSuccess('Market data configuration updated successfully');
      } else {
        setError('Failed to update configuration: ' + response.data.error);
      }
    } catch (err) {
      setError('Error updating configuration: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const renderConfigForm = () => {
    if (!config || Object.keys(config).length === 0) {
      return <Typography>No configuration available</Typography>;
    }

    return Object.entries(config)
      .filter(([source]) => source !== 'active_source')
      .map(([source, sourceConfig]) => (
        <Card key={source} sx={{ mb: 3 }}>
          <CardHeader
            title={`${source.charAt(0).toUpperCase() + source.slice(1).replace('_', ' ')} Configuration`}
            action={
              <FormControlLabel
                control={<Switch checked={activeSource === source} onChange={() => handleSourceChange({ target: { value: source } })} />}
                label="Active"
              />
            }
          />
          <Divider />
          <CardContent>
            <Grid container spacing={2}>
              {Object.entries(sourceConfig).map(([key, value]) => {
                const isSecret = key.toLowerCase().includes('key') || 
                                key.toLowerCase().includes('secret') || 
                                key.toLowerCase().includes('token');
                
                if (isSecret && !showApiKeys && value === '**********') {
                  return (
                    <Grid item xs={12} sm={6} key={key}>
                      <TextField
                        fullWidth
                        label={key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}
                        type="password"
                        value={updatedConfig[source]?.[key] || ''}
                        onChange={(e) => handleConfigChange(source, key, e.target.value)}
                        placeholder="Enter new value to update"
                      />
                    </Grid>
                  );
                }
                
                return (
                  <Grid item xs={12} sm={6} key={key}>
                    <TextField
                      fullWidth
                      label={key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}
                      value={updatedConfig[source]?.[key] || ''}
                      onChange={(e) => handleConfigChange(source, key, e.target.value)}
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
          Market Data Configuration
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
                <InputLabel id="active-source-label">Active Market Data Source</InputLabel>
                <Select
                  labelId="active-source-label"
                  value={activeSource}
                  onChange={handleSourceChange}
                  label="Active Market Data Source"
                >
                  {sources.map((source) => (
                    <MenuItem key={source} value={source}>
                      {source.charAt(0).toUpperCase() + source.slice(1).replace('_', ' ')}
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
                disabled={loading}
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

export default MarketDataConfig; 