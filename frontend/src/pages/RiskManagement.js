import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Slider,
  FormControlLabel,
  Switch,
  TextField,
  Button,
  Divider,
  Alert,
  RadioGroup,
  Radio,
  FormControl,
  FormLabel,
  InputAdornment,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
} from '@mui/material';
import { 
  ExpandMore, 
  Info, 
  Save, 
  Refresh, 
  Security, 
  AssessmentOutlined,
  AutoGraph,
  SmartToy,
  TrendingUp,
  Warning,
  CheckCircleOutline,
  BarChart,
} from '@mui/icons-material';
import ScrollIndicator from '../components/ScrollIndicator';

const RiskManagement = () => {
  // State for risk management settings
  const [settings, setSettings] = useState({
    risk_management: {
      max_position_size: 2.0,
      max_daily_risk: 5.0,
      default_risk_reward: 2.0,
      adaptive_stops: true,
      max_positions: 5,
      correlation_limit: 0.7,
      use_ai_risk_management: true,
      risk_profile: "moderate"
    },
    ai_risk_management: {
      volatility_multiplier: 2.0,
      risk_tolerance_factor: 1.0,
      max_position_size_percent: 5.0,
      risk_per_trade_percent: 1.0,
      use_gpt_for_risk: true,
      min_risk_score: 60,
      reward_risk_ratio_min: 1.5,
      auto_adjust_position_size: true
    }
  });

  // State for risk analysis
  const [riskAnalysis, setRiskAnalysis] = useState({
    portfolio_value: 10000,
    total_exposure: 0,
    exposure_percent: 0,
    total_risk_percent: 0,
    max_risk_percent: 5.0,
    available_risk_percent: 5.0,
    num_positions: 0,
    sector_exposure_percent: {},
    daily_trades: 0,
    max_daily_trades: 5
  });

  // State for AI risk metrics
  const [aiRiskMetrics, setAiRiskMetrics] = useState({
    last_adjustment_time: new Date().toISOString(),
    market_volatility: 'MODERATE',
    volatility_level: 0.018,
    risk_score_threshold: 65,
    avg_position_size: 2.5,
    last_adjustment_factor: 0.85,
    trades_evaluated: 24,
    trades_approved: 18,
    trades_rejected: 6,
    avg_risk_score: 72
  });

  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);
  const [testSymbol, setTestSymbol] = useState('AAPL');
  const [testResult, setTestResult] = useState(null);
  const [testLoading, setTestLoading] = useState(false);
  const [portfolioValue, setPortfolioValue] = useState(10000);
  
  // Add ref for scrollable container
  const pageRef = useRef(null);

  // Load settings on component mount
  useEffect(() => {
    fetchSettings();
    fetchRiskAnalysis();
    fetchAiRiskMetrics();
  }, []);

  // Fetch current settings from API
  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/risk-management/settings');
      if (response.data && response.data.success) {
        setSettings(response.data.settings);
      }
    } catch (err) {
      console.error('Error fetching risk management settings:', err);
      setError('Failed to load risk management settings');
    } finally {
      setLoading(false);
    }
  };

  // Fetch current risk analysis
  const fetchRiskAnalysis = async () => {
    try {
      const response = await axios.get('/api/risk-management/analysis');
      if (response.data && response.data.success) {
        setRiskAnalysis(response.data.analysis);
      }
    } catch (err) {
      console.error('Error fetching risk analysis:', err);
    }
  };

  // Fetch AI risk metrics (mock function - would be implemented with real API)
  const fetchAiRiskMetrics = async () => {
    try {
      // This would be replaced with actual API call
      // const response = await axios.get('/api/risk-management/ai-metrics');
      // setAiRiskMetrics(response.data.metrics);
      
      // For now, just simulate data
      setAiRiskMetrics({
        last_adjustment_time: new Date().toISOString(),
        market_volatility: ['LOW', 'MODERATE', 'HIGH'][Math.floor(Math.random() * 3)],
        volatility_level: (0.01 + Math.random() * 0.03).toFixed(3),
        risk_score_threshold: Math.floor(55 + Math.random() * 15),
        avg_position_size: (1 + Math.random() * 4).toFixed(1),
        last_adjustment_factor: (0.7 + Math.random() * 0.6).toFixed(2),
        trades_evaluated: Math.floor(20 + Math.random() * 15),
        trades_approved: Math.floor(15 + Math.random() * 10),
        trades_rejected: Math.floor(1 + Math.random() * 8),
        avg_risk_score: Math.floor(60 + Math.random() * 30)
      });
    } catch (err) {
      console.error('Error fetching AI risk metrics:', err);
    }
  };

  // Save settings to API
  const saveSettings = async () => {
    try {
      setLoading(true);
      setSaved(false);
      const response = await axios.post('/api/risk-management/settings', settings);
      if (response.data && response.data.success) {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      }
    } catch (err) {
      console.error('Error saving risk management settings:', err);
      setError('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  // Test risk management with a symbol
  const testRiskManagement = async () => {
    try {
      setTestLoading(true);
      setTestResult(null);
      const response = await axios.post('/api/risk-management/test', {
        symbol: testSymbol,
        portfolio_value: portfolioValue
      });
      if (response.data && response.data.success) {
        setTestResult(response.data.result);
      }
    } catch (err) {
      console.error('Error testing risk management:', err);
      setError('Failed to test risk management');
    } finally {
      setTestLoading(false);
    }
  };

  // Handle settings changes
  const handleBasicSettingChange = (e) => {
    const { name, value, checked, type } = e.target;
    setSettings({
      ...settings,
      risk_management: {
        ...(settings.risk_management || {}),
        [name]: type === 'checkbox' ? checked : parseFloat(value)
      }
    });
  };

  const handleAISettingChange = (e) => {
    const { name, value, checked, type } = e.target;
    setSettings({
      ...settings,
      ai_risk_management: {
        ...(settings.ai_risk_management || {}),
        [name]: type === 'checkbox' ? checked : parseFloat(value)
      }
    });
  };

  const handleRiskProfileChange = (e) => {
    setSettings({
      ...settings,
      risk_management: {
        ...(settings.risk_management || {}),
        risk_profile: e.target.value
      }
    });
  };

  // Helper function to format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Helper function to get color based on volatility
  const getVolatilityColor = (volatility) => {
    if (volatility === 'LOW') return 'success.main';
    if (volatility === 'MODERATE') return 'warning.main';
    return 'error.main';
  };

  // Helper function to get risk score color
  const getRiskScoreColor = (score) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'warning.main';
    return 'error.main';
  };

  return (
    <Box className="p-4" ref={pageRef}>
      <Typography variant="h4" className="mb-4 font-bold">
        Dynamic Risk Management
      </Typography>

      {error && (
        <Alert severity="error" className="mb-4" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {saved && (
        <Alert severity="success" className="mb-4">
          Settings saved successfully
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Portfolio Risk Summary */}
        <Grid item xs={12}>
          <Card className="shadow-md">
            <CardContent>
              <Typography variant="h6" className="mb-2 font-semibold">
                <Box display="flex" alignItems="center">
                  <BarChart className="mr-2" />
                  Portfolio Risk Summary
                </Box>
              </Typography>
              <Divider className="mb-2" />
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Portfolio Value
                      </Typography>
                      <Typography variant="h6">
                        ${(riskAnalysis.portfolio_value || 0).toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Current Exposure
                      </Typography>
                      <Typography variant="h6">
                        {(riskAnalysis.exposure_percent || 0).toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Current Risk
                      </Typography>
                      <Typography variant="h6">
                        {(riskAnalysis.total_risk_percent || 0).toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Available Risk
                      </Typography>
                      <Typography variant="h6">
                        {(riskAnalysis.available_risk_percent || 0).toFixed(1)}%
                      </Typography>
                    </Grid>
                  </Grid>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={fetchRiskAnalysis}
                      startIcon={<Refresh />}
                      className="mb-2"
                    >
                      Refresh Analysis
                    </Button>
                  </Box>
                  <Box>
                    <TextField
                      label="Portfolio Value"
                      type="number"
                      value={portfolioValue}
                      onChange={(e) => setPortfolioValue(parseFloat(e.target.value))}
                      InputProps={{
                        startAdornment: <InputAdornment position="start">$</InputAdornment>,
                      }}
                      variant="outlined"
                      size="small"
                      className="mb-2"
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Autonomous Bot Risk Settings */}
        <Grid item xs={12} md={6}>
          <Card className="shadow-md">
            <CardContent>
              <Typography variant="h6" className="mb-2 font-semibold">
                <Box display="flex" alignItems="center">
                  <SmartToy className="mr-2" />
                  Autonomous Bot Risk Settings
                </Box>
              </Typography>
              <Divider className="mb-2" />
              
              <FormControl className="mb-3 w-full">
                <FormLabel component="legend">Risk Profile</FormLabel>
                <RadioGroup
                  row
                  name="risk_profile"
                  value={settings.risk_management?.risk_profile || "moderate"}
                  onChange={handleRiskProfileChange}
                >
                  <FormControlLabel value="conservative" control={<Radio />} label="Conservative" />
                  <FormControlLabel value="moderate" control={<Radio />} label="Moderate" />
                  <FormControlLabel value="aggressive" control={<Radio />} label="Aggressive" />
                </RadioGroup>
              </FormControl>
              
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box display="flex" alignItems="center">
                    <AutoGraph className="mr-2" />
                    <Typography variant="subtitle1">AI Risk Management</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.risk_management?.use_ai_risk_management || false}
                        onChange={(e) => handleBasicSettingChange({
                          target: {
                            name: 'use_ai_risk_management',
                            checked: e.target.checked,
                            type: 'checkbox'
                          }
                        })}
                      />
                    }
                    label="Use AI for Dynamic Risk Management"
                    className="mb-2"
                  />
                  
                  <Typography variant="body2" className="text-gray-600 mb-3">
                    When enabled, the AI will automatically adjust risk parameters based on market conditions and portfolio performance.
                  </Typography>
                
                  <Box className="my-3">
                    <Divider />
                    <Typography variant="body2" className="mt-2">
                      <strong>How Autonomous Risk Management Works:</strong>
                    </Typography>
                    
                    <Box className="pl-2 mt-1">
                      <Typography variant="body2" className="mt-1">
                        • Continuously monitors market volatility and adapts position sizing
                      </Typography>
                      <Typography variant="body2" className="mt-1">
                        • Analyzes correlations between assets to prevent overexposure
                      </Typography>
                      <Typography variant="body2" className="mt-1">
                        • Adjusts stop-loss levels based on asset volatility
                      </Typography>
                      <Typography variant="body2" className="mt-1">
                        • Identifies support/resistance levels for profit targets
                      </Typography>
                      <Typography variant="body2" className="mt-1">
                        • Evaluates overall portfolio risk and prevents excessive exposure
                      </Typography>
                    </Box>
                  </Box>
                </AccordionDetails>
              </Accordion>
              
              <Grid container spacing={2} className="mt-2">
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" gutterBottom>
                    Max Position Size (%)
                  </Typography>
                  <Slider
                    value={settings.ai_risk_management?.max_position_size_percent || 5.0}
                    onChange={(e, newValue) => handleAISettingChange({
                      target: { name: 'max_position_size_percent', value: newValue }
                    })}
                    min={0.5}
                    max={10}
                    step={0.5}
                    marks={[
                      { value: 0.5, label: '0.5%' },
                      { value: 10, label: '10%' }
                    ]}
                    valueLabelDisplay="auto"
                    valueLabelFormat={(value) => `${value}%`}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" gutterBottom>
                    Risk Per Trade (%)
                  </Typography>
                  <Slider
                    value={settings.ai_risk_management?.risk_per_trade_percent || 1.0}
                    onChange={(e, newValue) => handleAISettingChange({
                      target: { name: 'risk_per_trade_percent', value: newValue }
                    })}
                    min={0.1}
                    max={2}
                    step={0.1}
                    marks={[
                      { value: 0.1, label: '0.1%' },
                      { value: 2, label: '2%' }
                    ]}
                    valueLabelDisplay="auto"
                    valueLabelFormat={(value) => `${value}%`}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* AI Risk Metrics */}
        <Grid item xs={12} md={6}>
          <Card className="shadow-md">
            <CardContent>
              <Typography variant="h6" className="mb-2 font-semibold">
                <Box display="flex" alignItems="center">
                  <Security className="mr-2" />
                  AI Risk Management Metrics
                </Box>
              </Typography>
              <Divider className="mb-2" />
              
              <Box display="flex" justifyContent="space-between" alignItems="center" className="mb-3">
                <Typography variant="body2">
                  <strong>Last Update:</strong> {formatDate(aiRiskMetrics.last_adjustment_time)}
                </Typography>
                <Chip 
                  label={`Volatility: ${aiRiskMetrics.market_volatility}`} 
                  color={aiRiskMetrics.market_volatility === 'LOW' ? 'success' : aiRiskMetrics.market_volatility === 'MODERATE' ? 'warning' : 'error'}
                  size="small"
                />
              </Box>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box display="flex" alignItems="center">
                    <TrendingUp className="mr-2" />
                    <Typography variant="subtitle1">Performance Metrics</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Trades Evaluated
                      </Typography>
                      <Typography variant="h6">
                        {aiRiskMetrics.trades_evaluated}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Average Risk Score
                      </Typography>
                      <Typography variant="h6" color={getRiskScoreColor(aiRiskMetrics.avg_risk_score)}>
                        {aiRiskMetrics.avg_risk_score}/100
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Trades Approved
                      </Typography>
                      <Typography variant="h6" color="success.main">
                        {aiRiskMetrics.trades_approved}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Trades Rejected
                      </Typography>
                      <Typography variant="h6" color="error.main">
                        {aiRiskMetrics.trades_rejected}
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Approval Rate
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={(aiRiskMetrics.trades_approved / aiRiskMetrics.trades_evaluated) * 100} 
                        color="success"
                        sx={{ height: 10, borderRadius: 5 }}
                      />
                      <Typography variant="body2" align="right" className="mt-1">
                        {((aiRiskMetrics.trades_approved / aiRiskMetrics.trades_evaluated) * 100).toFixed(0)}%
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
              
              <Grid container spacing={2} className="mt-3">
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.ai_risk_management?.auto_adjust_position_size || false}
                        onChange={(e) => handleAISettingChange({
                          target: {
                            name: 'auto_adjust_position_size',
                            checked: e.target.checked,
                            type: 'checkbox'
                          }
                        })}
                      />
                    }
                    label="Auto-Adjust Position Size"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.ai_risk_management?.use_gpt_for_risk || false}
                        onChange={(e) => handleAISettingChange({
                          target: {
                            name: 'use_gpt_for_risk',
                            checked: e.target.checked,
                            type: 'checkbox'
                          }
                        })}
                      />
                    }
                    label="Use GPT for Risk Analysis"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" gutterBottom>
                    <Tooltip title="Adjusts risk based on market volatility">
                      <Box display="inline-flex" alignItems="center">
                        Volatility Multiplier <Info fontSize="small" className="ml-1" />
                      </Box>
                    </Tooltip>
                  </Typography>
                  <Slider
                    value={settings.ai_risk_management?.volatility_multiplier || 2.0}
                    onChange={(e, newValue) => handleAISettingChange({
                      target: { name: 'volatility_multiplier', value: newValue }
                    })}
                    min={0.5}
                    max={5}
                    step={0.1}
                    valueLabelDisplay="auto"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" gutterBottom>
                    <Tooltip title="Controls how aggressively AI adapts to changing market conditions">
                      <Box display="inline-flex" alignItems="center">
                        Risk Tolerance Factor <Info fontSize="small" className="ml-1" />
                      </Box>
                    </Tooltip>
                  </Typography>
                  <Slider
                    value={settings.ai_risk_management?.risk_tolerance_factor || 1.0}
                    onChange={(e, newValue) => handleAISettingChange({
                      target: { name: 'risk_tolerance_factor', value: newValue }
                    })}
                    min={0.1}
                    max={3}
                    step={0.1}
                    valueLabelDisplay="auto"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" gutterBottom>
                    Minimum Risk Score
                  </Typography>
                  <Slider
                    value={settings.ai_risk_management?.min_risk_score || 60}
                    onChange={(e, newValue) => handleAISettingChange({
                      target: { name: 'min_risk_score', value: newValue }
                    })}
                    min={0}
                    max={100}
                    step={5}
                    marks={[
                      { value: 0, label: '0' },
                      { value: 50, label: '50' },
                      { value: 100, label: '100' }
                    ]}
                    valueLabelDisplay="auto"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" gutterBottom>
                    Min Reward/Risk Ratio
                  </Typography>
                  <Slider
                    value={settings.ai_risk_management?.reward_risk_ratio_min || 1.5}
                    onChange={(e, newValue) => handleAISettingChange({
                      target: { name: 'reward_risk_ratio_min', value: newValue }
                    })}
                    min={1}
                    max={5}
                    step={0.1}
                    marks={[
                      { value: 1, label: '1:1' },
                      { value: 3, label: '3:1' },
                      { value: 5, label: '5:1' }
                    ]}
                    valueLabelDisplay="auto"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Risk Test Tool */}
        <Grid item xs={12}>
          <Card className="shadow-md">
            <CardContent>
              <Typography variant="h6" className="mb-2 font-semibold">
                <Box display="flex" alignItems="center">
                  <Warning className="mr-2" />
                  Test Risk Management
                </Box>
              </Typography>
              <Divider className="mb-2" />
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <TextField
                    label="Symbol"
                    value={testSymbol}
                    onChange={(e) => setTestSymbol(e.target.value)}
                    variant="outlined"
                    size="small"
                    fullWidth
                    className="mb-2"
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={testRiskManagement}
                    disabled={testLoading}
                    startIcon={testLoading ? <CircularProgress size={24} /> : null}
                    fullWidth
                  >
                    Test Risk Parameters
                  </Button>
                </Grid>
              </Grid>
              
              {testResult && (
                <Box className="mt-4">
                  <Typography variant="subtitle1" gutterBottom>
                    <Box display="flex" alignItems="center">
                      <CheckCircleOutline className="mr-2" color="success" />
                      Risk Assessment Results:
                    </Box>
                  </Typography>
                  <TableContainer component={Paper}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Parameter</TableCell>
                          <TableCell align="right">Value</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        <TableRow>
                          <TableCell>Position Size</TableCell>
                          <TableCell align="right">${testResult.position_size?.toFixed(2) || 'N/A'}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Risk Amount</TableCell>
                          <TableCell align="right">${testResult.risk_amount?.toFixed(2) || 'N/A'}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Risk Percentage</TableCell>
                          <TableCell align="right">{testResult.risk_percentage?.toFixed(2) || 'N/A'}%</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Stop Loss</TableCell>
                          <TableCell align="right">${testResult.stop_loss?.toFixed(2) || 'N/A'}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Take Profit</TableCell>
                          <TableCell align="right">${testResult.take_profit?.toFixed(2) || 'N/A'}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>AI Risk Score</TableCell>
                          <TableCell align="right">{testResult.ai_risk_score || 'N/A'}/100</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Save Settings Button */}
        <Grid item xs={12}>
          <Box display="flex" justifyContent="flex-end">
            <Button
              variant="contained"
              color="primary"
              onClick={saveSettings}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={24} /> : <Save />}
              size="large"
            >
              Save Risk Settings
            </Button>
          </Box>
        </Grid>
      </Grid>
      
      {/* Add scroll indicator */}
      <ScrollIndicator 
        containerRef={pageRef} 
        position="bottom-right" 
        threshold={200}
        offsetBottom={30}
      />
    </Box>
  );
};

export default RiskManagement; 