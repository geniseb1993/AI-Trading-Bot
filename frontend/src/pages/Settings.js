import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid,
  TextField,
  Button,
  Switch,
  FormGroup,
  FormControlLabel,
  Divider,
  useTheme,
  alpha,
  MenuItem,
  Slider,
  InputAdornment,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert
} from '@mui/material';
import { 
  Save, 
  ExpandMore,
  Notifications,
  Security,
  CloudSync,
  DataUsage,
  BarChart
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const Settings = () => {
  const theme = useTheme();
  const [saved, setSaved] = useState(false);
  
  // Example settings state
  const [settings, setSettings] = useState({
    general: {
      darkMode: true,
      notifications: true,
      autoRefresh: true,
      refreshInterval: 5,
    },
    trading: {
      initialCapital: 10000,
      maxPositions: 5,
      positionSize: 10,
      stopLoss: 5,
      takeProfit: 15,
      strategy: 'default',
    },
    signals: {
      emaFast: 12,
      emaSlow: 26,
      rsiPeriod: 14,
      rsiOverbought: 70,
      rsiOversold: 30,
      minimumScore: 7,
    },
    advanced: {
      apiKey: '••••••••••••••••••••••••',
      apiSecret: '••••••••••••••••••••••••',
      enableLogging: true,
      debugMode: false,
    }
  });

  const handleGeneralChange = (e) => {
    const { name, value, checked } = e.target;
    setSettings({
      ...settings,
      general: {
        ...settings.general,
        [name]: name === 'refreshInterval' ? Number(value) : checked !== undefined ? checked : value,
      }
    });
  };

  const handleTradingChange = (e) => {
    const { name, value } = e.target;
    setSettings({
      ...settings,
      trading: {
        ...settings.trading,
        [name]: name === 'strategy' ? value : Number(value),
      }
    });
  };

  const handleSignalsChange = (e) => {
    const { name, value } = e.target;
    setSettings({
      ...settings,
      signals: {
        ...settings.signals,
        [name]: Number(value),
      }
    });
  };

  const handleAdvancedChange = (e) => {
    const { name, value, checked } = e.target;
    setSettings({
      ...settings,
      advanced: {
        ...settings.advanced,
        [name]: checked !== undefined ? checked : value,
      }
    });
  };

  const handleSliderChange = (name, section) => (e, newValue) => {
    setSettings({
      ...settings,
      [section]: {
        ...settings[section],
        [name]: newValue,
      }
    });
  };

  const handleSave = () => {
    // In a real app, this would save to backend
    setSaved(true);
    
    // Clear the success message after 3 seconds
    setTimeout(() => {
      setSaved(false);
    }, 3000);
  };

  return (
    <Box sx={{ pb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography 
          variant="h4" 
          component={motion.h4}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          sx={{ 
            fontWeight: 'bold',
            color: theme.palette.primary.main
          }}
        >
          Settings
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<Save />}
          onClick={handleSave}
          sx={{ fontFamily: 'Orbitron' }}
        >
          Save Settings
        </Button>
      </Box>

      {saved && (
        <Alert 
          severity="success" 
          sx={{ mb: 3 }}
          component={motion.div}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          Settings saved successfully!
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* General Settings */}
        <Grid item xs={12} md={6}>
          <Card 
            component={motion.div}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            sx={{ 
              height: '100%',
              backgroundColor: alpha(theme.palette.background.paper, 0.7),
              backdropFilter: 'blur(10px)',
            }}
          >
            <CardContent>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 2,
                gap: 1
              }}>
                <DataUsage color="primary" />
                <Typography variant="h6" fontFamily="Orbitron">
                  General Settings
                </Typography>
              </Box>
              
              <Divider sx={{ mb: 3 }} />
              
              <FormGroup>
                <FormControlLabel 
                  control={
                    <Switch 
                      checked={settings.general.darkMode} 
                      onChange={handleGeneralChange} 
                      name="darkMode" 
                      color="primary"
                    />
                  } 
                  label="Dark Mode" 
                />
                
                <FormControlLabel 
                  control={
                    <Switch 
                      checked={settings.general.notifications} 
                      onChange={handleGeneralChange} 
                      name="notifications" 
                      color="primary"
                    />
                  } 
                  label="Enable Notifications" 
                />
                
                <FormControlLabel 
                  control={
                    <Switch 
                      checked={settings.general.autoRefresh} 
                      onChange={handleGeneralChange} 
                      name="autoRefresh" 
                      color="primary"
                    />
                  } 
                  label="Auto-Refresh Data" 
                />
                
                <Box sx={{ mt: 2, pl: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Refresh Interval (minutes)
                  </Typography>
                  <Slider
                    value={settings.general.refreshInterval}
                    min={1}
                    max={60}
                    step={1}
                    onChange={handleSliderChange('refreshInterval', 'general')}
                    valueLabelDisplay="auto"
                    disabled={!settings.general.autoRefresh}
                    sx={{ width: '90%' }}
                  />
                </Box>
              </FormGroup>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Trading Settings */}
        <Grid item xs={12} md={6}>
          <Card 
            component={motion.div}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            sx={{ 
              height: '100%',
              backgroundColor: alpha(theme.palette.background.paper, 0.7),
              backdropFilter: 'blur(10px)',
            }}
          >
            <CardContent>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 2,
                gap: 1
              }}>
                <BarChart color="primary" />
                <Typography variant="h6" fontFamily="Orbitron">
                  Trading Settings
                </Typography>
              </Box>
              
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Initial Capital ($)"
                    type="number"
                    name="initialCapital"
                    value={settings.trading.initialCapital}
                    onChange={handleTradingChange}
                    variant="outlined"
                    size="small"
                    InputProps={{
                      startAdornment: <InputAdornment position="start">$</InputAdornment>,
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Max Open Positions"
                    type="number"
                    name="maxPositions"
                    value={settings.trading.maxPositions}
                    onChange={handleTradingChange}
                    variant="outlined"
                    size="small"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Position Size (% of capital)
                    </Typography>
                    <Slider
                      value={settings.trading.positionSize}
                      min={1}
                      max={100}
                      step={1}
                      onChange={handleSliderChange('positionSize', 'trading')}
                      valueLabelDisplay="auto"
                      valueLabelFormat={(value) => `${value}%`}
                    />
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Trading Strategy"
                    name="strategy"
                    value={settings.trading.strategy}
                    onChange={handleTradingChange}
                    variant="outlined"
                    size="small"
                  >
                    <MenuItem value="default">Default Strategy</MenuItem>
                    <MenuItem value="conservative">Conservative</MenuItem>
                    <MenuItem value="aggressive">Aggressive</MenuItem>
                    <MenuItem value="custom">Custom</MenuItem>
                  </TextField>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Stop Loss (%)
                    </Typography>
                    <Slider
                      value={settings.trading.stopLoss}
                      min={1}
                      max={20}
                      step={0.5}
                      onChange={handleSliderChange('stopLoss', 'trading')}
                      valueLabelDisplay="auto"
                      valueLabelFormat={(value) => `${value}%`}
                    />
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Take Profit (%)
                    </Typography>
                    <Slider
                      value={settings.trading.takeProfit}
                      min={1}
                      max={50}
                      step={0.5}
                      onChange={handleSliderChange('takeProfit', 'trading')}
                      valueLabelDisplay="auto"
                      valueLabelFormat={(value) => `${value}%`}
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Signal Settings */}
        <Grid item xs={12} md={6}>
          <Card 
            component={motion.div}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            sx={{ 
              backgroundColor: alpha(theme.palette.background.paper, 0.7),
              backdropFilter: 'blur(10px)',
            }}
          >
            <CardContent>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 2,
                gap: 1
              }}>
                <Notifications color="primary" />
                <Typography variant="h6" fontFamily="Orbitron">
                  Signal Settings
                </Typography>
              </Box>
              
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="EMA Fast Period"
                    type="number"
                    name="emaFast"
                    value={settings.signals.emaFast}
                    onChange={handleSignalsChange}
                    variant="outlined"
                    size="small"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="EMA Slow Period"
                    type="number"
                    name="emaSlow"
                    value={settings.signals.emaSlow}
                    onChange={handleSignalsChange}
                    variant="outlined"
                    size="small"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="RSI Period"
                    type="number"
                    name="rsiPeriod"
                    value={settings.signals.rsiPeriod}
                    onChange={handleSignalsChange}
                    variant="outlined"
                    size="small"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Minimum Signal Score (1-10)
                    </Typography>
                    <Slider
                      value={settings.signals.minimumScore}
                      min={1}
                      max={10}
                      step={0.5}
                      onChange={handleSliderChange('minimumScore', 'signals')}
                      valueLabelDisplay="auto"
                    />
                  </Box>
                </Grid>
                
                <Grid item xs={12}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      RSI Thresholds
                    </Typography>
                    <Slider
                      value={[settings.signals.rsiOversold, settings.signals.rsiOverbought]}
                      min={0}
                      max={100}
                      step={1}
                      onChange={(e, newValue) => {
                        setSettings({
                          ...settings,
                          signals: {
                            ...settings.signals,
                            rsiOversold: newValue[0],
                            rsiOverbought: newValue[1],
                          }
                        });
                      }}
                      valueLabelDisplay="auto"
                      marks={[
                        { value: 0, label: '0' },
                        { value: 30, label: '30' },
                        { value: 70, label: '70' },
                        { value: 100, label: '100' },
                      ]}
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Advanced Settings */}
        <Grid item xs={12} md={6}>
          <Card 
            component={motion.div}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            sx={{ 
              backgroundColor: alpha(theme.palette.background.paper, 0.7),
              backdropFilter: 'blur(10px)',
            }}
          >
            <CardContent>
              <Accordion 
                sx={{ 
                  backgroundColor: 'transparent',
                  boxShadow: 'none',
                  '&:before': {
                    display: 'none',
                  },
                }}
              >
                <AccordionSummary
                  expandIcon={<ExpandMore />}
                  sx={{ px: 0 }}
                >
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    gap: 1
                  }}>
                    <Security color="primary" />
                    <Typography variant="h6" fontFamily="Orbitron">
                      Advanced Settings
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ px: 0 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="API Key"
                        type="password"
                        name="apiKey"
                        value={settings.advanced.apiKey}
                        onChange={handleAdvancedChange}
                        variant="outlined"
                        size="small"
                      />
                    </Grid>
                    
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="API Secret"
                        type="password"
                        name="apiSecret"
                        value={settings.advanced.apiSecret}
                        onChange={handleAdvancedChange}
                        variant="outlined"
                        size="small"
                      />
                    </Grid>
                    
                    <Grid item xs={12}>
                      <FormGroup>
                        <FormControlLabel 
                          control={
                            <Switch 
                              checked={settings.advanced.enableLogging} 
                              onChange={handleAdvancedChange} 
                              name="enableLogging" 
                              color="primary"
                            />
                          } 
                          label="Enable Logging" 
                        />
                        
                        <FormControlLabel 
                          control={
                            <Switch 
                              checked={settings.advanced.debugMode} 
                              onChange={handleAdvancedChange} 
                              name="debugMode" 
                              color="primary"
                            />
                          } 
                          label="Debug Mode" 
                        />
                      </FormGroup>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
              
              <Divider sx={{ mb: 3, mt: 1 }} />
              
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 2,
                gap: 1
              }}>
                <CloudSync color="primary" />
                <Typography variant="h6" fontFamily="Orbitron">
                  Data Management
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 3 }}>
                <Button variant="outlined" color="primary">
                  Export Settings
                </Button>
                <Button variant="outlined" color="primary">
                  Import Settings
                </Button>
                <Button variant="outlined" color="error">
                  Reset to Default
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Settings; 