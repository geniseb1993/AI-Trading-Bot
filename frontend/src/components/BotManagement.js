import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Snackbar,
  Chip
} from '@mui/material';
import { PlayArrow, Stop, Info, Refresh } from '@mui/icons-material';
import TradingBotStatus from './dashboard/TradingBotStatus';
import apiService from '../services/apiService';

const BotManagement = () => {
  const [botStatus, setBotStatus] = useState({
    autonomous_bot: { status: false },
    rsi_bot: { status: false },
    dual_bot: { status: false }
  });
  const [loading, setLoading] = useState({
    autonomous: false,
    rsi: false,
    dual: false
  });
  const [error, setError] = useState(null);
  const [debugInfo, setDebugInfo] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [lastRefresh, setLastRefresh] = useState(Date.now());

  useEffect(() => {
    fetchBotStatus();
    checkApiConnection();
    const interval = setInterval(fetchBotStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchBotStatus = async (forceRefresh = false) => {
    try {
      console.log('Fetching bot status...', new Date().toISOString());
      const response = await apiService.getBotStatus();
      
      console.log('Bot status response:', response.data);
      
      if (response.data) {
        // Check if autonomous_bot status is set
        if (response.data.autonomous_bot) {
          console.log('Autonomous bot status:', response.data.autonomous_bot.status);
        }
        
        // Check if RSI bot status is set
        if (response.data.rsi_bot) {
          console.log('RSI bot status:', response.data.rsi_bot.status);
        }
        
        // Check if dual bot status is set
        if (response.data.dual_bot) {
          console.log('Dual bot status:', response.data.dual_bot.status);
        }
        
        // Force a re-render by setting state
        setBotStatus({...response.data});
        setLastRefresh(Date.now());
        setError(null);
      } else {
        throw new Error('Empty response from API');
      }
    } catch (err) {
      console.error('Error fetching bot status:', err);
      setError(`Could not load trading bot data: ${err.message}`);
      
      // Set a basic structure to prevent UI errors
      setBotStatus({
        autonomous_bot: { status: false, error: "Connection error" },
        rsi_bot: { status: false, error: "Connection error" },
        dual_bot: { status: false, error: "Connection error" }
      });
    }
  };

  // Function to check API connection
  const checkApiConnection = async () => {
    try {
      console.log('Checking API connection...');
      const healthResponse = await apiService.checkHealth();
      console.log('API health check response:', healthResponse);
      
      // If we reach here, API is responding
      // Now check bot component availability
      const botStatusResponse = await apiService.getBotStatus({ maxRetries: 1 });
      
      // Create debug info object
      const debugData = {
        status: 'connected',
        components: {
          autonomous_bot: Boolean(botStatusResponse.data?.autonomous_bot),
          rsi_bot: Boolean(botStatusResponse.data?.rsi_bot),
          dual_bot: Boolean(botStatusResponse.data?.dual_bot)
        }
      };
      
      setDebugInfo(debugData);
      
      if (!debugData.components.dual_bot) {
        console.warn('Dual bot component not available in API');
      }
    } catch (err) {
      console.error('Error checking API connection:', err);
      setDebugInfo({ 
        status: 'error', 
        error: err.message,
        components: {
          autonomous_bot: false,
          rsi_bot: false,
          dual_bot: false
        }
      });
    }
  };

  const handleBotAction = async (botType, action) => {
    setLoading(prev => ({ ...prev, [botType]: true }));
    try {
      console.log(`${action}ing ${botType} bot...`);
      
      let response;
      if (action === 'start') {
        response = await apiService.startBot(botType);
      } else if (action === 'stop') {
        response = await apiService.stopBot(botType);
      } else {
        throw new Error(`Unknown action: ${action}`);
      }
      
      console.log(`${action} response:`, response.data);

      // Check if the response has the success field or status field
      if (response.data.success === true || response.data.status === 'success') {
        setSnackbar({
          open: true,
          message: response.data.message || `Successfully ${action}ed ${botType} bot`,
          severity: 'success'
        });
        
        // Update the local state immediately for better UI response
        const newStatus = action === 'start' ? "active" : "inactive";
        console.log(`Setting ${botType}_bot status to "${newStatus}"`);
        
        setBotStatus(prev => {
          const updatedStatus = {
            ...prev,
            [botType + '_bot']: {
              ...prev[botType + '_bot'],
              status: newStatus,
              last_update: new Date().toISOString()
            }
          };
          console.log('Updated bot status state:', updatedStatus);
          return updatedStatus;
        });
        
        // Then fetch status from server to ensure we're in sync
        setTimeout(() => fetchBotStatus(true), 500);
      } else {
        throw new Error(response.data.error || response.data.message || 'Operation failed');
      }
    } catch (err) {
      console.error(`Error ${action}ing ${botType} bot:`, err);
      let errorMessage = err.message;
      
      // Extract more detailed error if available
      if (err.response && err.response.data) {
        if (err.response.data.error) {
          errorMessage = err.response.data.error;
        } else if (err.response.data.message) {
          errorMessage = err.response.data.message;
        }
      }
      
      setSnackbar({
        open: true,
        message: `Failed to ${action} ${botType} bot: ${errorMessage}`,
        severity: 'error'
      });
    } finally {
      setLoading(prev => ({ ...prev, [botType]: false }));
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const renderBotCard = (title, botType, data) => {
    // Check explicitly for boolean true or string "active" to consider the bot running
    const isRunning = data?.status === true || data?.status === "active";
    const lastUpdate = data?.last_update || 'N/A';
    const isRealData = !data?.error;
    
    // Debug the status of the bot
    console.log(`BotManagement (component): ${title} status check:`, {
      rawStatus: data?.status, 
      statusType: typeof data?.status,
      isRunning: isRunning,
      statusEqualsTrue: data?.status === true,
      statusEqualsActive: data?.status === "active"
    });
    
    // Format the bot data for TradingBotStatus
    const botData = [{
      id: `${botType}-bot`,
      name: title,
      status: isRunning ? 'active' : 'paused',
      lastTrade: lastUpdate,
      activeStrategies: botType === 'autonomous' ? data?.active_trades?.length || 0 : 
                        botType === 'rsi' ? data?.active_signals?.length || 0 :
                        data?.active_positions?.length || 0,
      pnl24h: data?.pnl_24h || 0,
      isRealData: isRealData
    }];
    
    return (
      <Card sx={{ minWidth: 275, m: 2, height: '100%', position: 'relative' }}>
        {!isRealData && (
          <Chip
            icon={<Info />}
            label="Sample Data"
            size="small"
            color="warning"
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              zIndex: 1
            }}
          />
        )}
        <CardContent>
          <Typography variant="h5" component="div" gutterBottom>
            {title}
          </Typography>
          
          <TradingBotStatus 
            bots={botData} 
            loading={loading[botType]}
            error={null}
            onRefresh={fetchBotStatus}
            onBotAction={(_, action) => handleBotAction(botType, action)}
          />
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">
          Bot Management
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<Refresh />}
          onClick={() => fetchBotStatus(true)}
        >
          Refresh Status
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {/* Debug panel - only shows when there's an issue */}
      {debugInfo && (debugInfo.error || !debugInfo.components?.dual_bot) && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="subtitle1" fontWeight="bold">API Connection Debug Info</Typography>
          {debugInfo.error ? (
            <Typography>Connection Error: {debugInfo.error}</Typography>
          ) : (
            <>
              <Typography>API Connected: {debugInfo.status}</Typography>
              <Typography>Components Available:</Typography>
              <ul>
                <li>Autonomous Bot: {debugInfo.components?.autonomous_bot ? 'Yes' : 'No'}</li>
                <li>RSI Bot: {debugInfo.components?.rsi_bot ? 'Yes' : 'No'}</li>
                <li>Dual Bot: {debugInfo.components?.dual_bot ? 'Yes' : 'No'} 
                  {!debugInfo.components?.dual_bot && ' - This is why the Dual Bot is not working!'}
                </li>
              </ul>
              <Button 
                variant="contained" 
                size="small" 
                color="secondary" 
                onClick={checkApiConnection} 
                sx={{ mt: 1, mr: 1 }}
              >
                Refresh Connection
              </Button>
            </>
          )}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          {renderBotCard('Autonomous Trading Bot', 'autonomous', botStatus.autonomous_bot)}
        </Grid>
        <Grid item xs={12} md={4}>
          {renderBotCard('RSI Strategy Bot', 'rsi', botStatus.rsi_bot)}
        </Grid>
        <Grid item xs={12} md={4}>
          {/* Make the dual bot card stand out when it's missing */}
          <Box sx={{ 
            border: botStatus.dual_bot ? 'none' : '2px dashed #f44336',
            borderRadius: '4px',
            p: botStatus.dual_bot ? 0 : 1,
            position: 'relative'
          }}>
            {!botStatus.dual_bot && (
              <Typography 
                color="error" 
                variant="subtitle2" 
                sx={{ position: 'absolute', top: '-10px', left: '10px', bgcolor: 'background.paper', px: 1 }}
              >
                Missing Bot
              </Typography>
            )}
            {renderBotCard('Dual Bot', 'dual', botStatus.dual_bot)}
          </Box>
        </Grid>
      </Grid>
      
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default BotManagement; 