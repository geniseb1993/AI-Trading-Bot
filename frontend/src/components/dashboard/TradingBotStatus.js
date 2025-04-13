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
  Switch,
  useTheme
} from '@mui/material';
import { 
  PlayArrow, 
  Pause, 
  Settings, 
  TrendingUp, 
  TrendingDown 
} from '@mui/icons-material';

/**
 * TradingBotStatus component displays the status of trading bots
 * 
 * @param {Object} props
 * @param {Array} props.bots - Array of trading bot objects
 * @returns {JSX.Element}
 */
const TradingBotStatus = ({ bots }) => {
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
  
  if (!processedBots || processedBots.length === 0) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%',
        width: '100%'
      }}>
        <Typography>No trading bots</Typography>
      </Box>
    );
  }

  // Format datetime
  const formatTime = (dateString) => {
    if (!dateString) return 'N/A';
    
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'Invalid date';
      
      return date.toLocaleString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      console.error("Error formatting date:", e);
      return 'Date error';
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
                    label={bot.status || 'unknown'}
                    color={bot.status === 'active' ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Tooltip title={bot.status === 'active' ? 'Pause Bot' : 'Start Bot'}>
                    <IconButton size="small" color={bot.status === 'active' ? 'warning' : 'success'}>
                      {bot.status === 'active' ? <Pause fontSize="small" /> : <PlayArrow fontSize="small" />}
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