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
  useTheme,
  alpha
} from '@mui/material';
import { 
  Notifications, 
  Delete, 
  Warning, 
  Check, 
  ErrorOutline
} from '@mui/icons-material';

/**
 * RecentAlerts component displays recent price and indicator alerts
 * 
 * @param {Object} props
 * @param {Array} props.alerts - Array of alert objects
 * @returns {JSX.Element}
 */
const RecentAlerts = ({ alerts }) => {
  const theme = useTheme();
  
  // Process the alerts data to ensure it's an array
  const processedAlerts = useMemo(() => {
    // If alerts is undefined or null, return empty array
    if (!alerts) return [];
    
    // If alerts is already an array, return it
    if (Array.isArray(alerts)) return alerts;
    
    // If alerts is an object with a data property that's an array, return that
    if (alerts.data && Array.isArray(alerts.data)) return alerts.data;

    // If alerts has values that can be extracted
    if (typeof alerts === 'object') {
      try {
        // Try to convert object values to an array
        return Object.values(alerts).filter(item => item && typeof item === 'object');
      } catch (e) {
        console.error("Error processing alerts:", e);
        return [];
      }
    }
    
    // Default to empty array
    return [];
  }, [alerts]);
  
  if (!processedAlerts || processedAlerts.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Typography>No recent alerts</Typography>
      </Box>
    );
  }

  // Format datetime
  const formatTime = (dateString) => {
    if (!dateString) return 'Pending';
    
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

  // Get alert type icon
  const getAlertIcon = (type, status) => {
    if (status === 'triggered') {
      return <Check fontSize="small" color="success" />;
    } else if (status === 'active') {
      return type === 'price' ? <Warning fontSize="small" color="warning" /> : <Notifications fontSize="small" color="info" />;
    } else {
      return <ErrorOutline fontSize="small" color="error" />;
    }
  };

  // Get alert description
  const getAlertDescription = (alert) => {
    if (!alert) return 'Unknown alert';
    
    if (alert.message) {
      return alert.message;
    } else if (alert.type === 'price') {
      return `Price ${alert.condition || ''} ${alert.value ? '$' + alert.value : ''}`;
    } else if (alert.condition) {
      return alert.condition;
    } else {
      return alert.type || 'Alert triggered';
    }
  };

  return (
    <List sx={{ 
      width: '100%', 
      maxHeight: '300px', 
      overflow: 'auto',
      '&::-webkit-scrollbar': {
        width: '8px',
      },
      '&::-webkit-scrollbar-thumb': {
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '4px',
      },
    }}>
      {processedAlerts.map((alert, index) => (
        <React.Fragment key={alert.id || `alert-${index}`}>
          {index > 0 && <Divider component="li" />}
          <ListItem
            sx={{ 
              py: 2,
              display: 'flex',
              flexDirection: {
                xs: 'column',
                md: 'row'
              },
              alignItems: {
                xs: 'flex-start',
                md: 'center'
              },
            }}
          >
            {/* Alert symbol and type */}
            <Box sx={{ 
              display: 'flex',
              alignItems: 'center',
              minWidth: '140px',
              mr: {
                xs: 0,
                md: 2
              },
              mb: {
                xs: 1,
                md: 0
              }
            }}>
              <Chip 
                label={alert.symbol || 'UNKNOWN'}
                color="primary"
                size="small"
                sx={{ mr: 1 }}
              />
              <Chip 
                label={alert.type || 'alert'}
                color={(alert.type === 'price' || alert.type === 'warning') ? 'warning' : 
                       alert.type === 'error' ? 'error' : 
                       alert.type === 'success' ? 'success' : 'info'}
                size="small"
                icon={alert.type === 'price' ? <Warning fontSize="small" /> : 
                      alert.type === 'error' ? <ErrorOutline fontSize="small" /> :
                      alert.type === 'success' ? <Check fontSize="small" /> :
                      <Notifications fontSize="small" />}
              />
            </Box>
            
            {/* Alert condition */}
            <Box sx={{ 
              display: 'flex',
              alignItems: 'center',
              flexGrow: 1,
              mr: {
                xs: 0,
                md: 2
              },
              mb: {
                xs: 1,
                md: 0
              }
            }}>
              <Typography variant="body2">
                {getAlertDescription(alert)}
              </Typography>
            </Box>
            
            {/* Status and time */}
            <Box sx={{ 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              minWidth: '180px',
              mr: {
                xs: 0,
                md: 2
              },
              mb: {
                xs: 1,
                md: 0
              }
            }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center',
                backgroundColor: alpha(
                  alert.status === 'triggered' || alert.type === 'success' 
                    ? theme.palette.success.main 
                    : alert.status === 'active' || alert.type === 'warning' 
                      ? theme.palette.warning.main 
                      : (alert.status === 'error' || alert.type === 'error')
                        ? theme.palette.error.main
                        : theme.palette.info.main, 
                  0.1
                ),
                borderRadius: 1,
                px: 1,
                py: 0.5
              }}>
                {getAlertIcon(alert.type, alert.status)}
                <Typography 
                  variant="body2" 
                  fontWeight="medium"
                  sx={{ ml: 0.5 }}
                  color={
                    alert.status === 'triggered' || alert.type === 'success'
                      ? 'success.main' 
                      : alert.status === 'active' || alert.type === 'warning'
                        ? 'warning.main' 
                        : (alert.status === 'error' || alert.type === 'error')
                          ? 'error.main'
                          : 'info.main'
                  }
                >
                  {alert.status || alert.priority || 'info'}
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ 
              display: 'flex',
              flexDirection: 'column',
              alignItems: {
                xs: 'flex-start',
                md: 'flex-end'
              },
              minWidth: {
                xs: '100%',
                md: 'auto'
              },
            }}>
              <Typography variant="caption" color="text.secondary">
                {alert.triggeredAt ? formatTime(alert.triggeredAt) : 
                 alert.timestamp ? formatTime(alert.timestamp) : 'Waiting to trigger'}
              </Typography>
              <Tooltip title="Delete Alert">
                <IconButton size="small" color="error">
                  <Delete fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </ListItem>
        </React.Fragment>
      ))}
    </List>
  );
};

export default RecentAlerts; 