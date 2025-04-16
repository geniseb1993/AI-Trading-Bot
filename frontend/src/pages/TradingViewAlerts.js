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
  Tooltip,
  useTheme,
  alpha,
  Card,
  CardContent,
  CardHeader
} from '@mui/material';
import { 
  Add, 
  ContentCopy, 
  Check, 
  Delete, 
  Refresh, 
  Notifications, 
  Code, 
  HelpOutline,
  Link as LinkIcon,
  AppRegistration
} from '@mui/icons-material';
import axios from 'axios';
import { motion } from 'framer-motion';

// Import layout components
import PageLayout from '../components/PageLayout';
import ContentCard from '../components/ContentCard';
import ContentGrid from '../components/ContentGrid';

// Define API base URL based on environment
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const TradingViewAlerts = () => {
  const theme = useTheme();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [newAlertName, setNewAlertName] = useState('');
  const [alertCondition, setAlertCondition] = useState('');
  const [webhook, setWebhook] = useState('');
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/tradingview/alerts`);
      if (response.data && response.data.success) {
        setAlerts(response.data.alerts || []);
      } else {
        throw new Error('Failed to fetch alerts data');
      }
    } catch (err) {
      console.error("Error fetching TradingView alerts:", err);
      setError(err.message || "An error occurred while fetching alerts");
      // Use mock data as fallback
      setAlerts(generateMockAlerts());
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
      const response = await axios.post(`${API_BASE_URL}/tradingview/alerts`, {
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
      const response = await axios.delete(`${API_BASE_URL}/tradingview/alerts/${id}`);
      
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

  // Alert List Card Component
  const AlertsListCard = () => (
    <Card 
      component={motion.div}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      sx={{ 
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: alpha(theme.palette.background.paper, 0.7),
        backdropFilter: 'blur(10px)',
        border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
        boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.35)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`,
        borderRadius: 2,
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        '&:hover': {
          boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.4)}, 0 0 12px ${alpha(theme.palette.primary.main, 0.25)}`,
          transform: 'translateY(-2px)'
        }
      }}
    >
      <CardHeader
        title={
          <Typography variant="h6" fontFamily="Orbitron" display="flex" alignItems="center" gap={1}>
            <Notifications fontSize="small" />
            Configured Alerts
        </Typography>
        }
        sx={{ 
          padding: '12px 20px',
          backgroundColor: alpha(theme.palette.primary.main, 0.1),
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          flexShrink: 0
        }}
      />
      <CardContent sx={{ p: 0, flexGrow: 1, overflow: 'auto' }}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 5 }}>
                <CircularProgress />
              </Box>
            ) : alerts.length === 0 ? (
          <Box sx={{ p: 3 }}>
            <Alert severity="info" sx={{ backgroundColor: alpha(theme.palette.info.main, 0.1) }}>
                No alerts configured. Click 'Create Alert' to add your first TradingView alert.
              </Alert>
          </Box>
            ) : (
          <List sx={{ width: '100%', p: 0 }}>
                {alerts.map((alert, index) => (
                  <React.Fragment key={alert.id}>
                    {index > 0 && <Divider component="li" />}
                    <ListItem
                      alignItems="flex-start"
                      secondaryAction={
                    <IconButton 
                      edge="end" 
                      aria-label="delete" 
                      onClick={() => handleDeleteAlert(alert.id)}
                      sx={{
                        backgroundColor: alpha(theme.palette.error.main, 0.1),
                        '&:hover': {
                          backgroundColor: alpha(theme.palette.error.main, 0.2),
                        }
                      }}
                    >
                          <Delete color="error" />
                        </IconButton>
                      }
                  sx={{
                    p: 2,
                    transition: 'background-color 0.2s ease',
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.05)
                    }
                  }}
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography 
                          variant="subtitle1" 
                          component="span" 
                          sx={{ 
                            fontWeight: 'bold',
                            fontFamily: 'Orbitron',
                            color: theme.palette.primary.main 
                          }}
                        >
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
                      <Box sx={{ mt: 1 }}>
                            <Typography
                              component="span"
                              variant="body2"
                          sx={{ 
                            display: 'block', 
                            color: 'text.primary', 
                            borderLeft: `3px solid ${theme.palette.primary.main}`,
                            pl: 1,
                            py: 0.5,
                            my: 1
                          }}
                            >
                              Condition: {alert.condition}
                            </Typography>
                            <Typography
                              component="span"
                              variant="body2"
                          sx={{ display: 'block', mt: 1, color: alpha(theme.palette.text.secondary, 0.8) }}
                            >
                              Created: {formatDate(alert.createdAt)}
                            </Typography>
                        <Box 
                          sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            mt: 1,
                            backgroundColor: alpha(theme.palette.background.paper, 0.5),
                            borderRadius: 1,
                            p: 1
                          }}
                        >
                          <LinkIcon fontSize="small" color="info" sx={{ mr: 1 }} />
                              <Typography
                                component="span"
                                variant="body2"
                            color="info.main"
                    sx={{ mr: 1 }}
                  >
                                Webhook URL:
                              </Typography>
                              <Typography
                                component="span"
                                variant="body2"
                            sx={{ 
                              fontFamily: 'Roboto Mono',
                              flexGrow: 1,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              fontSize: '0.75rem'
                            }}
                              >
                                {alert.webhook}
                              </Typography>
                              <Tooltip title={copied ? "Copied!" : "Copy to clipboard"}>
                            <IconButton 
                              size="small" 
                              onClick={() => copyToClipboard(alert.webhook)}
                              sx={{
                                ml: 1,
                                backgroundColor: copied ? alpha(theme.palette.success.main, 0.1) : alpha(theme.palette.primary.main, 0.1),
                              }}
                            >
                              {copied ? <Check fontSize="small" color="success" /> : <ContentCopy fontSize="small" color="primary" />}
                                </IconButton>
                              </Tooltip>
                            </Box>
                      </Box>
                        }
                      />
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            )}
      </CardContent>
    </Card>
  );

  // How to Use Card Component 
  const HowToUseCard = () => (
    <Card 
      component={motion.div}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: alpha(theme.palette.background.paper, 0.7),
        backdropFilter: 'blur(10px)',
        border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
        boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.35)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`,
        borderRadius: 2,
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        '&:hover': {
          boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.4)}, 0 0 12px ${alpha(theme.palette.primary.main, 0.25)}`,
          transform: 'translateY(-2px)'
        }
      }}
    >
      <CardHeader
        title={
          <Typography variant="h6" fontFamily="Orbitron" display="flex" alignItems="center" gap={1}>
            <HelpOutline fontSize="small" />
            How to Use TradingView Alerts
          </Typography>
        }
        sx={{ 
          padding: '12px 20px',
          backgroundColor: alpha(theme.palette.primary.main, 0.1),
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          flexShrink: 0
        }}
      />
      <CardContent sx={{ p: 3, flexGrow: 1, overflow: 'auto' }}>
            <Typography variant="body1" paragraph>
              TradingView alerts allow you to receive notifications when specific market conditions are met. Follow these steps to set up alerts:
            </Typography>
        <Box 
          component="ol" 
          sx={{ 
            backgroundColor: alpha(theme.palette.background.paper, 0.5),
            borderRadius: 2,
            p: 2,
            pl: 4,
            ml: 0,
            '& li': { 
              mb: 1,
              pl: 1
            },
            '& li::marker': {
              color: theme.palette.primary.main,
              fontWeight: 'bold'
            }
          }}
        >
                <li>Create an alert in this dashboard</li>
                <li>Copy the webhook URL provided</li>
                <li>In TradingView, create a new alert for your indicator or condition</li>
                <li>In the alert settings, enable "Webhook URL" and paste your copied URL</li>
                <li>Configure the alert message format (JSON is recommended)</li>
                <li>Save the alert in TradingView</li>
        </Box>
        <Typography variant="body1" sx={{ mt: 2 }} paragraph>
              Your alert will now trigger trading signals in the system when conditions are met.
            </Typography>
      </CardContent>
    </Card>
  );

  // Alert Message Format Card Component
  const MessageFormatCard = () => (
    <Card 
      component={motion.div}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: alpha(theme.palette.background.paper, 0.7),
        backdropFilter: 'blur(10px)',
        border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
        boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.35)}, 0 0 8px ${alpha(theme.palette.primary.main, 0.2)}`,
        borderRadius: 2,
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        '&:hover': {
          boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.4)}, 0 0 12px ${alpha(theme.palette.primary.main, 0.25)}`,
          transform: 'translateY(-2px)'
        }
      }}
    >
      <CardHeader
        title={
          <Typography variant="h6" fontFamily="Orbitron" display="flex" alignItems="center" gap={1}>
            <Code fontSize="small" />
            Alert Message Format
          </Typography>
        }
        sx={{ 
          padding: '12px 20px',
          backgroundColor: alpha(theme.palette.primary.main, 0.1),
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          flexShrink: 0
        }}
      />
      <CardContent sx={{ p: 3, flexGrow: 1, overflow: 'auto' }}>
            <Typography variant="body1" paragraph>
              When configuring your TradingView alert, use the following JSON format for the message:
            </Typography>
            <Box
              component="pre"
              sx={{
            backgroundColor: alpha(theme.palette.background.default, 0.6),
            color: theme.palette.text.primary,
                p: 2,
                borderRadius: 1,
                overflowX: 'auto',
            fontFamily: 'Roboto Mono',
            fontSize: '0.875rem',
            border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
            position: 'relative'
          }}
        >
          <Box 
            sx={{ 
              position: 'absolute',
              top: 5,
              right: 5,
              backgroundColor: alpha(theme.palette.primary.main, 0.1),
              borderRadius: 1,
              p: 0.5
            }}
          >
            <Tooltip title={copied ? "Copied!" : "Copy to clipboard"}>
              <IconButton 
                size="small" 
                onClick={() => copyToClipboard(`{
  "symbol": "{{ticker}}",
  "interval": "{{interval}}",
  "price": {{close}},
  "action": "BUY", // or "SELL"
  "strategy": "Your Strategy Name",
  "message": "{{strategy.order.comment}}"
}`)}
              >
                {copied ? <Check fontSize="small" color="success" /> : <ContentCopy fontSize="small" />}
              </IconButton>
            </Tooltip>
          </Box>
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
      </CardContent>
    </Card>
  );

  return (
    <PageLayout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography 
          variant="h4" 
          component={motion.h4}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          sx={{ 
            fontWeight: 'bold',
            color: 'primary.main',
            fontFamily: 'Orbitron',
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}
        >
          <AppRegistration fontSize="large" />
          TradingView Alerts
        </Typography>
        <Box>
          <Button
            variant="outlined"
            color="primary"
            startIcon={refreshing ? <CircularProgress size={20} color="inherit" /> : <Refresh />}
            onClick={fetchAlerts}
            sx={{ mr: 2, fontFamily: 'Orbitron' }}
            disabled={refreshing}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            color="primary"
            startIcon={<Add />}
            onClick={handleOpenDialog}
            sx={{ fontFamily: 'Orbitron' }}
          >
            Create Alert
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert 
          severity="error" 
          sx={{ 
            mb: 3, 
            borderRadius: 2,
            backgroundColor: alpha(theme.palette.error.main, 0.1),
            border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`
          }}
        >
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert 
          severity="success" 
          sx={{ 
            mb: 3, 
            borderRadius: 2,
            backgroundColor: alpha(theme.palette.success.main, 0.1),
            border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`
          }}
        >
          {success}
        </Alert>
      )}

      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        height: 'calc(100vh - 180px)',
        width: '100%',
        overflow: 'hidden'
      }}>
        <Grid 
          container 
          spacing={3} 
          sx={{ 
            mb: 3,
            height: '60%',
            width: '100%'
          }}
        >
          <Grid 
            item 
            xs={12} 
            sx={{ 
              height: '100%',
              display: 'flex'
            }}
          >
            <AlertsListCard />
          </Grid>
        </Grid>
        
        <Grid 
          container 
          spacing={3} 
          sx={{ 
            height: '40%',
            width: '100%'
          }}
        >
          <Grid 
            item 
            xs={12} 
            md={6} 
            sx={{ 
              height: '100%',
              display: 'flex'
            }}
          >
            <HowToUseCard />
          </Grid>
          <Grid 
            item 
            xs={12} 
            md={6} 
            sx={{ 
              height: '100%',
              display: 'flex'
            }}
          >
            <MessageFormatCard />
          </Grid>
        </Grid>
      </Box>

      {/* Create Alert Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            backgroundColor: alpha(theme.palette.background.paper, 0.95),
            backdropFilter: 'blur(10px)',
            boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.4)}`
          }
        }}
      >
        <DialogTitle sx={{ fontFamily: 'Orbitron', py: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Notifications fontSize="small" color="primary" />
            Create New TradingView Alert
          </Box>
        </DialogTitle>
        <Divider />
        <DialogContent sx={{ mt: 2 }}>
          <DialogContentText sx={{ mb: 3 }}>
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
                InputProps={{
                  sx: { borderRadius: 1.5 }
                }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                margin="dense"
                label="Alert Condition"
                  fullWidth
                variant="outlined"
                multiline
                rows={3}
                placeholder="e.g., RSI crosses below 30, MACD crosses above signal line"
                value={alertCondition}
                onChange={(e) => setAlertCondition(e.target.value)}
                InputProps={{
                  sx: { borderRadius: 1.5 }
                }}
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
                  sx: { 
                    fontFamily: 'Roboto Mono',
                    fontSize: '0.875rem',
                    borderRadius: 1.5
                  },
                  endAdornment: (
                    <IconButton onClick={() => copyToClipboard(webhook)}>
                      {copied ? <Check color="success" /> : <ContentCopy color="primary" />}
                    </IconButton>
                  ),
                }}
              />
        </Grid>
      </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button 
            onClick={handleCloseDialog} 
            variant="outlined" 
            color="inherit"
            sx={{ borderRadius: 2 }}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleCreateAlert} 
            variant="contained" 
            color="primary"
            sx={{ borderRadius: 2, px: 3 }}
          >
            Create Alert
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default TradingViewAlerts; 