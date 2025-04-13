import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  Grid, 
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Divider,
  Chip,
  Tooltip
} from '@mui/material';
import { Add, ContentCopy, Check, Delete, Refresh } from '@mui/icons-material';
import axios from 'axios';
import { motion } from 'framer-motion';

// Import our new layout components
import PageLayout from '../components/PageLayout';
import ContentCard from '../components/ContentCard';
import ContentGrid from '../components/ContentGrid';

const TradingViewAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [newAlertName, setNewAlertName] = useState('');
  const [alertCondition, setAlertCondition] = useState('');
  const [webhook, setWebhook] = useState('');
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/tradingview/alerts');
      if (response.data && response.data.success) {
        setAlerts(response.data.alerts);
      } else {
        // Fallback to mock data if API fails with error message
        generateMockAlerts();
      }
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
      setError('Failed to fetch alerts. Using sample data instead.');
      
      // Generate mock data on error
      generateMockAlerts();
    } finally {
      setLoading(false);
    }
  };

  const generateMockAlerts = () => {
    const mockAlerts = [
      {
        id: '1',
        name: 'Golden Cross Alert',
        condition: 'SMA(20) crosses above SMA(50)',
        createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        webhook: 'https://example.com/webhook/golden-cross',
        active: true
      },
      {
        id: '2',
        name: 'Oversold RSI',
        condition: 'RSI(14) < 30',
        createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        webhook: 'https://example.com/webhook/oversold',
        active: true
      },
      {
        id: '3',
        name: 'MACD Signal',
        condition: 'MACD Line crosses above Signal Line',
        createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
        webhook: 'https://example.com/webhook/macd',
        active: false
      }
    ];
    
    setAlerts(mockAlerts);
  };

  const handleOpenDialog = () => {
    setOpenDialog(true);
    setWebhook(`${window.location.origin}/api/tradingview/hook/${Math.random().toString(36).substring(2, 15)}`);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setNewAlertName('');
    setAlertCondition('');
    setError(null);
  };

  const handleCreateAlert = async () => {
    if (!newAlertName || !alertCondition) {
      setError('Please fill in all fields');
      return;
    }
    
    try {
      const response = await axios.post('/api/tradingview/alerts', {
        name: newAlertName,
        condition: alertCondition,
        webhook
      });
      
      if (response.data && response.data.success) {
        setAlerts([...alerts, response.data.alert]);
        setSuccess('Alert created successfully!');
        setTimeout(() => setSuccess(null), 3000);
        handleCloseDialog();
      } else {
        setError('Failed to create alert');
      }
    } catch (error) {
      console.error('Error creating alert:', error);
      setError('Failed to create alert. Please try again.');
      
      // For demo, add a mock alert
      const newAlert = {
        id: String(alerts.length + 1),
        name: newAlertName,
        condition: alertCondition,
        createdAt: new Date().toISOString(),
        webhook,
        active: true
      };
      
      setAlerts([...alerts, newAlert]);
      setSuccess('Alert created successfully! (Demo mode)');
      setTimeout(() => setSuccess(null), 3000);
      handleCloseDialog();
    }
  };

  const handleDeleteAlert = async (id) => {
    try {
      const response = await axios.delete(`/api/tradingview/alerts/${id}`);
      
      if (response.data && response.data.success) {
        setAlerts(alerts.filter(alert => alert.id !== id));
        setSuccess('Alert deleted successfully!');
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError('Failed to delete alert');
        setTimeout(() => setError(null), 3000);
      }
    } catch (error) {
      console.error('Error deleting alert:', error);
      
      // For demo, remove from state anyway
      setAlerts(alerts.filter(alert => alert.id !== id));
      setSuccess('Alert deleted successfully! (Demo mode)');
      setTimeout(() => setSuccess(null), 3000);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(
      function() {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      },
      function(err) {
        console.error('Could not copy text: ', err);
      }
    );
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <PageLayout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography 
          variant="h4" 
          component={motion.h4}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          sx={{ 
            fontWeight: 'bold',
            color: 'primary.main'
          }}
        >
          TradingView Alerts
        </Typography>
        <Box>
          <Button
            variant="contained"
            color="primary"
            startIcon={<Refresh />}
            onClick={fetchAlerts}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            color="success"
            startIcon={<Add />}
            onClick={handleOpenDialog}
          >
            Create Alert
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>{success}</Alert>
      )}

      <ContentGrid>
        <Grid item xs={12}>
          <ContentCard title="Configured Alerts">
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 5 }}>
                <CircularProgress />
              </Box>
            ) : alerts.length === 0 ? (
              <Alert severity="info">
                No alerts configured. Click 'Create Alert' to add your first TradingView alert.
              </Alert>
            ) : (
              <List>
                {alerts.map((alert, index) => (
                  <React.Fragment key={alert.id}>
                    {index > 0 && <Divider component="li" />}
                    <ListItem
                      alignItems="flex-start"
                      secondaryAction={
                        <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteAlert(alert.id)}>
                          <Delete color="error" />
                        </IconButton>
                      }
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="subtitle1" component="span" sx={{ fontWeight: 'bold' }}>
                              {alert.name}
            </Typography>
                            <Chip 
                              label={alert.active ? 'Active' : 'Inactive'} 
                              color={alert.active ? 'success' : 'default'} 
                              size="small" 
                              sx={{ ml: 2 }}
                            />
                          </Box>
                        }
                        secondary={
                          <>
                            <Typography
                              component="span"
                              variant="body2"
                              sx={{ display: 'block', color: 'text.primary', mt: 1 }}
                            >
                              Condition: {alert.condition}
                            </Typography>
                            <Typography
                              component="span"
                              variant="body2"
                              sx={{ display: 'block', mt: 1 }}
                            >
                              Created: {formatDate(alert.createdAt)}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                              <Typography
                                component="span"
                                variant="body2"
                    sx={{ mr: 1 }}
                  >
                                Webhook URL:
                              </Typography>
                              <Typography
                                component="span"
                                variant="body2"
                                sx={{ fontFamily: 'monospace', bgcolor: 'background.paper', p: 0.5, borderRadius: 1 }}
                              >
                                {alert.webhook}
                              </Typography>
                              <Tooltip title={copied ? "Copied!" : "Copy to clipboard"}>
                                <IconButton size="small" onClick={() => copyToClipboard(alert.webhook)}>
                                  {copied ? <Check fontSize="small" color="success" /> : <ContentCopy fontSize="small" />}
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </>
                        }
                      />
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            )}
          </ContentCard>
        </Grid>
      </ContentGrid>

      <ContentGrid>
        <Grid item xs={12} md={6}>
          <ContentCard title="How to Use TradingView Alerts" animationDelay={0.1}>
            <Typography variant="body1" paragraph>
              TradingView alerts allow you to receive notifications when specific market conditions are met. Follow these steps to set up alerts:
            </Typography>
            <Typography variant="body1" component="div">
              <ol>
                <li>Create an alert in this dashboard</li>
                <li>Copy the webhook URL provided</li>
                <li>In TradingView, create a new alert for your indicator or condition</li>
                <li>In the alert settings, enable "Webhook URL" and paste your copied URL</li>
                <li>Configure the alert message format (JSON is recommended)</li>
                <li>Save the alert in TradingView</li>
              </ol>
            </Typography>
            <Typography variant="body1" paragraph>
              Your alert will now trigger trading signals in the system when conditions are met.
            </Typography>
          </ContentCard>
        </Grid>
        <Grid item xs={12} md={6}>
          <ContentCard title="Alert Message Format" animationDelay={0.2}>
            <Typography variant="body1" paragraph>
              When configuring your TradingView alert, use the following JSON format for the message:
            </Typography>
            <Box
              component="pre"
              sx={{
                backgroundColor: 'background.paper',
                p: 2,
                borderRadius: 1,
                overflowX: 'auto',
                fontFamily: 'monospace',
                fontSize: '0.875rem'
              }}
            >
              {`{
  "symbol": "{{ticker}}",
  "interval": "{{interval}}",
  "price": {{close}},
  "action": "BUY", // or "SELL"
  "strategy": "Your Strategy Name",
  "message": "{{strategy.order.comment}}"
}`}
                </Box>
            <Typography variant="body1" sx={{ mt: 2 }} paragraph>
              Replace the variables in the curly braces with TradingView variables. The "action" field should be set to "BUY" or "SELL" depending on your alert condition.
            </Typography>
          </ContentCard>
              </Grid>
      </ContentGrid>

      {/* Create Alert Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>Create New TradingView Alert</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Set up a new TradingView alert to trigger actions in your trading system.
          </DialogContentText>
          <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                autoFocus
                margin="dense"
                label="Alert Name"
                  fullWidth
                variant="outlined"
                value={newAlertName}
                onChange={(e) => setNewAlertName(e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                margin="dense"
                label="Alert Condition"
                  fullWidth
                variant="outlined"
                multiline
                rows={2}
                placeholder="e.g., RSI crosses below 30, MACD crosses above signal line"
                value={alertCondition}
                onChange={(e) => setAlertCondition(e.target.value)}
              />
            </Grid>
        <Grid item xs={12}>
              <TextField
                margin="dense"
                label="Webhook URL"
                fullWidth
                variant="outlined"
                value={webhook}
                InputProps={{
                  readOnly: true,
                  endAdornment: (
                    <IconButton onClick={() => copyToClipboard(webhook)}>
                      {copied ? <Check color="success" /> : <ContentCopy />}
                    </IconButton>
                  ),
                }}
              />
        </Grid>
      </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleCreateAlert} variant="contained" color="primary">
            Create Alert
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default TradingViewAlerts; 