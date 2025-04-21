import React, { useMemo } from 'react';
import { 
  Box, 
  Typography, 
  List, 
  ListItem, 
  Divider, 
  Chip, 
  IconButton, 
  Tooltip,
  CircularProgress,
  Alert,
  useTheme,
  Button
} from '@mui/material';
import { 
  PlayArrow, 
  Pause, 
  Settings, 
  TrendingUp, 
  TrendingDown,
  Refresh,
  Error as ErrorIcon,
  Info
} from '@mui/icons-material';

/**
 * TradingBotStatus component displays the status of trading bots
 * 
 * @param {Object} props
 * @param {Array} props.bots - Array of trading bot objects
 * @param {boolean} props.loading - Whether the bot data is loading
 * @param {string} props.error - Error message if any
 * @param {Function} props.onRefresh - Function to refresh bot data
 * @param {Function} props.onBotAction - Function to handle bot actions (start/stop)
 * @returns {JSX.Element}
 */
const TradingBotStatus = ({ 
  bots, 
  loading = false, 
  error = null,
  onRefresh = () => {}, 
  onBotAction = () => {} 
}) => {
  const theme = useTheme();
  
  // Ensure bots is always an array
  const processedBots = useMemo(() => {
    // If bots is undefined or null, return empty array
    if (!bots) return [];
    
    // If bots is already an array, return it
    if (Array.isArray(bots)) return bots;
    
    // If bots has a data property that's an array, return that
    if (bots.data && Array.isArray(bots.data)) return bots.data;
    
    // If bots is an object with values that can be extracted
    if (typeof bots === 'object') {
      try {
        // Try to convert object values to an array
        return Object.values(bots).filter(item => item && typeof item === 'object');
      } catch (e) {
        console.error("Error processing bots:", e);
        return [];
      }
    }
    
    // Default to empty array
    return [];
  }, [bots]);

  // If loading, show loading spinner
  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%',
        width: '100%',
        gap: 2
      }}>
        <CircularProgress />
        <Typography>Loading bot status...</Typography>
      </Box>
    );
  }
  
  // If error, show error message with refresh button
  if (error) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%',
        width: '100%',
        p: 2
      }}>
        <Alert 
          severity="error" 
          icon={<ErrorIcon />}
          action={
            <IconButton
              color="inherit"
              size="small"
              onClick={onRefresh}
            >
              <Refresh />
            </IconButton>
          }
          sx={{ width: '100%', mb: 2 }}
        >
          {error}
        </Alert>
      </Box>
    );
  }
  
  if (!processedBots || processedBots.length === 0) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%',
        width: '100%',
        gap: 2
      }}>
        <Typography>No trading bots available</Typography>
        <Button 
          variant="outlined" 
          startIcon={<Refresh />} 
          onClick={onRefresh}
          size="small"
        >
          Refresh
        </Button>
      </Box>
    );
  }

  // Format datetime
  const formatTime = (dateString) => {
    if (!dateString) return 'Never';
    
    try {
      const date = new Date(dateString);
      // If date is invalid, throw an error
      if (isNaN(date.getTime())) {
        throw new Error('Invalid date');
      }
      
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.round(diffMs / 60000);
      
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins} min ago`;
      
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours} hours ago`;
      
      const diffDays = Math.floor(diffHours / 24);
      return `${diffDays} days ago`;
    } catch (err) {
      console.error(`Error formatting date (${dateString}):`, err);
      return 'Invalid date';
    }
  };

  return (
    <Box sx={{ 
      width: '100%', 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        p: 1
      }}>
        <Typography variant="h6">Trading Bots</Typography>
        <Tooltip title="Refresh status">
          <IconButton onClick={onRefresh} size="small">
            <Refresh fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      
      <List sx={{ 
        width: '100%', 
        height: '100%',
        flexGrow: 1,
        overflow: 'auto',
        p: 0,
        m: 0,
        '&::-webkit-scrollbar': {
          width: '6px',
        },
        '&::-webkit-scrollbar-thumb': {
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '3px',
        },
      }}>
        {processedBots.map((bot, index) => (
          <React.Fragment key={bot.id || `bot-${index}`}>
            {index > 0 && <Divider component="li" sx={{ my: 0.5 }} />}
            <ListItem
              sx={{ 
                py: 1.5,
                px: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
              }}
            >
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                width: '100%',
                mb: 1
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="subtitle1" fontWeight="bold" sx={{ mr: 1 }}>
                    {bot.name || 'Unnamed Bot'}
                  </Typography>
                  <Chip 
                    label={bot.status === 'active' ? 'Active' : 'Paused'}
                    color={bot.status === 'active' ? 'success' : 'warning'}
                    size="small"
                  />
                  {bot.isRealData === false && (
                    <Chip 
                      label="Demo"
                      color="warning"
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  )}
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Tooltip 
                    title={bot.status === 'active' ? "Stop Bot" : "Start Bot"}
                    arrow
                  >
                    <IconButton 
                      color={bot.status === 'active' ? 'error' : 'success'} 
                      onClick={() => {
                        // Add more detailed logging to understand the bot status
                        console.log(`TradingBotStatus: Clicking button for bot with ID=${bot.id}`);
                        console.log(`TradingBotStatus: Current bot status=${bot.status}, will trigger ${bot.status === 'active' ? 'stop' : 'start'} action`);
                        console.log(`TradingBotStatus: Full bot data:`, bot);
                        
                        onBotAction(bot.id, bot.status === 'active' ? 'stop' : 'start');
                      }}
                      disabled={loading}
                    >
                      {bot.status === 'active' ? <Pause /> : <PlayArrow />}
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Bot Settings">
                    <IconButton size="small">
                      <Settings fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                width: '100%'
              }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Last Trade
                  </Typography>
                  <Typography variant="body2">
                    {formatTime(bot.lastTrade)}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Active Strategies
                  </Typography>
                  <Typography variant="body2" align="center">
                    {bot.activeStrategies || 0}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    24h PNL
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {typeof bot.pnl24h === 'number' && bot.pnl24h > 0 ? (
                      <TrendingUp fontSize="small" color="success" sx={{ mr: 0.5 }} />
                    ) : typeof bot.pnl24h === 'number' && bot.pnl24h < 0 ? (
                      <TrendingDown fontSize="small" color="error" sx={{ mr: 0.5 }} />
                    ) : null}
                    <Typography 
                      variant="body2" 
                      fontWeight="bold"
                      color={typeof bot.pnl24h === 'number' && bot.pnl24h > 0 ? 'success.main' : 
                             typeof bot.pnl24h === 'number' && bot.pnl24h < 0 ? 'error.main' : 
                             'text.primary'}
                    >
                      {typeof bot.pnl24h === 'number' ? 
                        (bot.pnl24h > 0 ? '+' : '') + bot.pnl24h + '%' : 
                        '0.0%'}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </ListItem>
          </React.Fragment>
        ))}
      </List>
    </Box>
  );
};

export default TradingBotStatus; 