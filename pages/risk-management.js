import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
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
} from '@mui/material';
import { 
  ExpandMore, 
  Info, 
  Save, 
  Refresh, 
  Security, 
  AssessmentOutlined 
} from '@mui/icons-material';

const RiskManagementPage = () => {
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

  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);
  const [testSymbol, setTestSymbol] = useState('AAPL');
  const [testResult, setTestResult] = useState(null);
  const [testLoading, setTestLoading] = useState(false);
  const [portfolioValue, setPortfolioValue] = useState(10000);

  // Load settings on component mount
  useEffect(() => {
    fetchSettings();
    fetchRiskAnalysis();
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
        ...settings.risk_management,
        [name]: type === 'checkbox' ? checked : parseFloat(value)
      }
    });
  };

  const handleAISettingChange = (e) => {
    const { name, value, checked, type } = e.target;
    setSettings({
      ...settings,
      ai_risk_management: {
        ...settings.ai_risk_management,
        [name]: type === 'checkbox' ? checked : parseFloat(value)
      }
    });
  };

  const handleRiskProfileChange = (e) => {
    setSettings({
      ...settings,
      risk_management: {
        ...settings.risk_management,
        risk_profile: e.target.value
      }
    });
  };

  return (
    <Layout>
      <Box className="p-4">
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
                  Portfolio Risk Summary
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Portfolio Value
                        </Typography>
                        <Typography variant="h6">
                          ${riskAnalysis.portfolio_value.toLocaleString()}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Current Exposure
                        </Typography>
                        <Typography variant="h6">
                          {riskAnalysis.exposure_percent.toFixed(1)}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Current Risk
                        </Typography>
                        <Typography variant="h6">
                          {riskAnalysis.total_risk_percent.toFixed(1)}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Available Risk
                        </Typography>
                        <Typography variant="h6">
                          {riskAnalysis.available_risk_percent.toFixed(1)}%
                        </Typography>
                      </Grid>
                    </Grid>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Open Positions
                        </Typography>
                        <Typography variant="h6">
                          {riskAnalysis.num_positions} / {riskAnalysis.max_positions}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Daily Trades
                        </Typography>
                        <Typography variant="h6">
                          {riskAnalysis.daily_trades} / {riskAnalysis.max_daily_trades}
                        </Typography>
                      </Grid>
                      <Grid item xs={12}>
                        <Button 
                          variant="outlined" 
                          startIcon={<Refresh />} 
                          onClick={fetchRiskAnalysis} 
                          fullWidth
                        >
                          Refresh Analysis
                        </Button>
                      </Grid>
                    </Grid>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Basic Risk Settings */}
          <Grid item xs={12} md={6}>
            <Card className="shadow-md h-full">
              <CardContent>
                <Typography variant="h6" className="mb-2 font-semibold">
                  Basic Risk Parameters
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      Max Position Size (% of portfolio)
                    </Typography>
                    <Slider
                      name="max_position_size"
                      value={settings.risk_management.max_position_size}
                      onChange={(e, value) => setSettings({
                        ...settings,
                        risk_management: {
                          ...settings.risk_management,
                          max_position_size: value
                        }
                      })}
                      step={0.1}
                      min={0.5}
                      max={10}
                      valueLabelDisplay="auto"
                      valueLabelFormat={(value) => `${value}%`}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      Max Daily Risk (% of portfolio)
                    </Typography>
                    <Slider
                      name="max_daily_risk"
                      value={settings.risk_management.max_daily_risk}
                      onChange={(e, value) => setSettings({
                        ...settings,
                        risk_management: {
                          ...settings.risk_management,
                          max_daily_risk: value
                        }
                      })}
                      step={0.5}
                      min={1}
                      max={10}
                      valueLabelDisplay="auto"
                      valueLabelFormat={(value) => `${value}%`}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      Default Risk/Reward Ratio
                    </Typography>
                    <Slider
                      name="default_risk_reward"
                      value={settings.risk_management.default_risk_reward}
                      onChange={(e, value) => setSettings({
                        ...settings,
                        risk_management: {
                          ...settings.risk_management,
                          default_risk_reward: value
                        }
                      })}
                      step={0.1}
                      min={1}
                      max={5}
                      valueLabelDisplay="auto"
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Max Positions"
                      name="max_positions"
                      type="number"
                      value={settings.risk_management.max_positions}
                      onChange={handleBasicSettingChange}
                      InputProps={{ inputProps: { min: 1, max: 20 } }}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Correlation Limit"
                      name="correlation_limit"
                      type="number"
                      value={settings.risk_management.correlation_limit}
                      onChange={handleBasicSettingChange}
                      InputProps={{ 
                        inputProps: { min: 0, max: 1, step: 0.1 },
                        endAdornment: (
                          <InputAdornment position="end">
                            <Tooltip title="Maximum correlation allowed between positions (0-1)">
                              <Info fontSize="small" />
                            </Tooltip>
                          </InputAdornment>
                        )
                      }}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.risk_management.adaptive_stops}
                          onChange={handleBasicSettingChange}
                          name="adaptive_stops"
                          color="primary"
                        />
                      }
                      label="Use Adaptive Stop-Loss"
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.risk_management.use_ai_risk_management}
                          onChange={handleBasicSettingChange}
                          name="use_ai_risk_management"
                          color="primary"
                        />
                      }
                      label="Enable AI-Powered Risk Management"
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <FormControl component="fieldset">
                      <FormLabel component="legend">Risk Profile</FormLabel>
                      <RadioGroup
                        row
                        name="risk_profile"
                        value={settings.risk_management.risk_profile}
                        onChange={handleRiskProfileChange}
                      >
                        <FormControlLabel
                          value="conservative"
                          control={<Radio />}
                          label="Conservative"
                        />
                        <FormControlLabel
                          value="moderate"
                          control={<Radio />}
                          label="Moderate"
                        />
                        <FormControlLabel
                          value="aggressive"
                          control={<Radio />}
                          label="Aggressive"
                        />
                      </RadioGroup>
                    </FormControl>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* AI Risk Settings */}
          <Grid item xs={12} md={6}>
            <Card className="shadow-md h-full">
              <CardContent>
                <Typography variant="h6" className="mb-2 font-semibold">
                  AI Risk Management
                </Typography>

                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      Volatility Multiplier (Stop-Loss)
                      <Tooltip title="Multiplier for ATR in stop-loss calculation. Higher values create wider stops.">
                        <Info fontSize="small" className="ml-1" />
                      </Tooltip>
                    </Typography>
                    <Slider
                      name="volatility_multiplier"
                      value={settings.ai_risk_management.volatility_multiplier}
                      onChange={(e, value) => setSettings({
                        ...settings,
                        ai_risk_management: {
                          ...settings.ai_risk_management,
                          volatility_multiplier: value
                        }
                      })}
                      step={0.1}
                      min={0.5}
                      max={4}
                      valueLabelDisplay="auto"
                      disabled={!settings.risk_management.use_ai_risk_management}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      Risk Tolerance Factor
                      <Tooltip title="Scaling factor for risk tolerance. Higher values increase risk.">
                        <Info fontSize="small" className="ml-1" />
                      </Tooltip>
                    </Typography>
                    <Slider
                      name="risk_tolerance_factor"
                      value={settings.ai_risk_management.risk_tolerance_factor}
                      onChange={(e, value) => setSettings({
                        ...settings,
                        ai_risk_management: {
                          ...settings.ai_risk_management,
                          risk_tolerance_factor: value
                        }
                      })}
                      step={0.1}
                      min={0.5}
                      max={2}
                      valueLabelDisplay="auto"
                      disabled={!settings.risk_management.use_ai_risk_management}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      Risk Per Trade (% of portfolio)
                    </Typography>
                    <Slider
                      name="risk_per_trade_percent"
                      value={settings.ai_risk_management.risk_per_trade_percent}
                      onChange={(e, value) => setSettings({
                        ...settings,
                        ai_risk_management: {
                          ...settings.ai_risk_management,
                          risk_per_trade_percent: value
                        }
                      })}
                      step={0.1}
                      min={0.1}
                      max={3}
                      valueLabelDisplay="auto"
                      valueLabelFormat={(value) => `${value}%`}
                      disabled={!settings.risk_management.use_ai_risk_management}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      Minimum Risk Score Threshold (0-100)
                    </Typography>
                    <Slider
                      name="min_risk_score"
                      value={settings.ai_risk_management.min_risk_score}
                      onChange={(e, value) => setSettings({
                        ...settings,
                        ai_risk_management: {
                          ...settings.ai_risk_management,
                          min_risk_score: value
                        }
                      })}
                      step={5}
                      min={0}
                      max={100}
                      valueLabelDisplay="auto"
                      disabled={!settings.risk_management.use_ai_risk_management}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Min Reward/Risk Ratio"
                      name="reward_risk_ratio_min"
                      type="number"
                      value={settings.ai_risk_management.reward_risk_ratio_min}
                      onChange={handleAISettingChange}
                      InputProps={{ inputProps: { min: 1, max: 5, step: 0.1 } }}
                      disabled={!settings.risk_management.use_ai_risk_management}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Max Position Size %"
                      name="max_position_size_percent"
                      type="number"
                      value={settings.ai_risk_management.max_position_size_percent}
                      onChange={handleAISettingChange}
                      InputProps={{ inputProps: { min: 1, max: 20, step: 0.5 } }}
                      disabled={!settings.risk_management.use_ai_risk_management}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.ai_risk_management.use_gpt_for_risk}
                          onChange={handleAISettingChange}
                          name="use_gpt_for_risk"
                          color="primary"
                          disabled={!settings.risk_management.use_ai_risk_management}
                        />
                      }
                      label="Use GPT for Advanced Risk Analysis"
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.ai_risk_management.auto_adjust_position_size}
                          onChange={handleAISettingChange}
                          name="auto_adjust_position_size"
                          color="primary"
                          disabled={!settings.risk_management.use_ai_risk_management}
                        />
                      }
                      label="Auto-Adjust Position Size Based on Setup Quality"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Test Risk Management */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6" className="font-semibold flex items-center">
                  <AssessmentOutlined className="mr-2" />
                  Test Risk Management
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6} md={3}>
                    <TextField
                      fullWidth
                      label="Symbol"
                      value={testSymbol}
                      onChange={(e) => setTestSymbol(e.target.value.toUpperCase())}
                      placeholder="e.g. AAPL"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <TextField
                      fullWidth
                      label="Portfolio Value"
                      type="number"
                      value={portfolioValue}
                      onChange={(e) => setPortfolioValue(parseFloat(e.target.value))}
                      InputProps={{
                        startAdornment: <InputAdornment position="start">$</InputAdornment>,
                      }}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={testRiskManagement}
                      disabled={testLoading}
                      startIcon={testLoading ? <CircularProgress size={20} /> : null}
                      fullWidth
                      sx={{ height: '56px' }}
                    >
                      Test Risk Management
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      variant="outlined"
                      onClick={() => setTestResult(null)}
                      disabled={!testResult}
                      fullWidth
                      sx={{ height: '56px' }}
                    >
                      Clear Results
                    </Button>
                  </Grid>

                  {testResult && (
                    <Grid item xs={12}>
                      <TableContainer component={Paper}>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Metric</TableCell>
                              <TableCell>Value</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            <TableRow>
                              <TableCell>Symbol</TableCell>
                              <TableCell>{testResult.symbol}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Risk Score</TableCell>
                              <TableCell>{testResult.risk_score}/100</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Recommendation</TableCell>
                              <TableCell>
                                <span className={`px-2 py-1 rounded ${
                                  testResult.recommendation === 'ACCEPT' ? 'bg-green-100 text-green-800' :
                                  testResult.recommendation === 'CAUTION' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {testResult.recommendation}
                                </span>
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Position Size</TableCell>
                              <TableCell>{testResult.position_size} shares</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Risk Amount</TableCell>
                              <TableCell>${testResult.risk_amount?.toFixed(2)}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Risk Percent</TableCell>
                              <TableCell>{testResult.risk_percent?.toFixed(2)}%</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Risk/Reward Ratio</TableCell>
                              <TableCell>1:{testResult.risk_reward_ratio?.toFixed(2)}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Suggested Stop Loss</TableCell>
                              <TableCell>${testResult.stop_loss?.toFixed(2)}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Suggested Profit Target</TableCell>
                              <TableCell>${testResult.profit_target?.toFixed(2)}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Volatility Assessment</TableCell>
                              <TableCell>{testResult.volatility_assessment}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Reason</TableCell>
                              <TableCell>{testResult.reason}</TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Grid>
                  )}
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>

          {/* Save Settings Button */}
          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Save />}
              onClick={saveSettings}
              disabled={loading}
              fullWidth
              sx={{ py: 1.5 }}
            >
              Save Risk Management Settings
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Layout>
  );
};

export default RiskManagementPage; 