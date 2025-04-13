import React, { useState, useRef, useEffect, useContext } from 'react';
import {
  Badge,
  IconButton,
  Menu,
  MenuItem,
  Typography,
  Box,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Tooltip,
  Button
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Circle as CircleIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  NotificationsActive as NotificationsActiveIcon,
  NotificationsOff as NotificationsOffIcon,
  VolumeUp as VolumeUpIcon
} from '@mui/icons-material';
import NotificationContext, { NotificationPriority, NotificationGroup } from '../contexts/NotificationContext';
import { formatDistanceToNow } from 'date-fns';
import NotificationSettings from './NotificationSettings';

const priorityColors = {
  [NotificationPriority.HIGH]: 'error',
  [NotificationPriority.MEDIUM]: 'warning',
  [NotificationPriority.LOW]: 'info'
};

const groupIcons = {
  [NotificationGroup.TRADE]: <CircleIcon color="primary" />,
  [NotificationGroup.SYSTEM]: <InfoIcon color="info" />,
  [NotificationGroup.ALERT]: <WarningIcon color="warning" />,
  [NotificationGroup.ERROR]: <ErrorIcon color="error" />
};

// Default notification settings if they're not available
const defaultSettings = {
  desktop: true,
  voice: true,
  sound: true,
  email: false,
  sms: false,
  priorityLevels: {
    [NotificationPriority.HIGH]: true,
    [NotificationPriority.MEDIUM]: true,
    [NotificationPriority.LOW]: true
  },
  voice: {
    rate: 150,
    volume: 0.8,
    useHumeAI: true
  }
};

const NotificationBell = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [selectedPriority, setSelectedPriority] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const menuRef = useRef(null);
  
  // Use useContext directly to ensure we get the notification context
  const notificationContext = useContext(NotificationContext);
  
  const {
    notifications = [],
    notificationSettings,
    addNotification,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    updateNotificationSettings,
    unreadCount = 0,
    sendDesktopNotification,
    sendVoiceNotification
  } = notificationContext || {};

  // Use the default settings if notificationSettings is undefined
  const settings = notificationSettings || defaultSettings;

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setSelectedGroup(null);
    setSelectedPriority(null);
  };

  const handleNotificationClick = (notification) => {
    if (!notification.read && markAsRead) {
      markAsRead(notification.id);
    }
    // Handle notification click (e.g., navigate to relevant page)
    handleClose();
  };

  const handleFilterChange = (group, priority) => {
    setSelectedGroup(group === selectedGroup ? null : group);
    setSelectedPriority(priority === selectedPriority ? null : priority);
  };

  const handleClearAll = () => {
    if (clearAll) {
      clearAll();
    }
    handleClose();
  };

  const handleMarkAllAsRead = () => {
    if (markAllAsRead) {
    markAllAsRead();
    }
  };

  const handleSettingsClick = () => {
    handleClose();
    setSettingsOpen(true);
  };
  
  const handleCloseSettings = () => {
    setSettingsOpen(false);
  };
  
  const handleToggleDesktopNotifications = () => {
    if (updateNotificationSettings) {
      updateNotificationSettings({
        desktop: !settings.desktop
      });
    }
  };
  
  const handleToggleVoiceNotifications = () => {
    if (updateNotificationSettings) {
      updateNotificationSettings({
        voice: !settings.voice
      });
    }
  };
  
  const testNotification = () => {
    try {
      console.log("Testing notification system");
      
      const testNotif = {
        id: Date.now(),
        type: 'test',
        title: 'Test Notification',
        message: 'This is a test notification to check if notifications are working correctly.',
        data: {},
        priority: NotificationPriority.MEDIUM,
        group: NotificationGroup.SYSTEM,
        timestamp: new Date().toISOString(),
        read: false
      };
      
      // Add notification to the list
      if (addNotification) {
        console.log("Adding notification to list");
        addNotification(testNotif);
      }
      
      // Log notification context for debugging
      console.log("Notification context:", notificationContext);
      console.log("Voice settings:", settings.voice);
      
      // Ensure desktop notification works by calling it directly
      if (sendDesktopNotification) {
        console.log("Sending desktop notification directly");
        sendDesktopNotification(testNotif);
      } else {
        console.warn("Desktop notification function not available");
        
        // Fallback for desktop notifications
        if ("Notification" in window && Notification.permission === "granted") {
          console.log("Using native browser notification as fallback");
          new Notification(testNotif.title, {
            body: testNotif.message,
            icon: "/logo192.png"
          });
        }
      }
      
      // Ensure voice notification works by calling it directly
      if (sendVoiceNotification) {
        console.log("Sending voice notification directly");
        // Force Hume AI for test notifications if it's enabled in settings
        const humeEnabled = settings.voice?.useHumeAI === true;
        console.log("Hume AI enabled:", humeEnabled);
        
        sendVoiceNotification({
          ...testNotif,
          message: humeEnabled 
            ? "This is a test of the Hume AI voice notification system. If you're hearing this in a natural voice, it's working correctly."
            : "This is a test of the browser voice notification system"
        });
      } else {
        console.warn("Voice notification function not available");
        
        // Fallback for voice notifications
        if ('speechSynthesis' in window) {
          console.log("Using browser speech synthesis as fallback");
          const utterance = new SpeechSynthesisUtterance(
            `${testNotif.title}. ${testNotif.message}`
          );
          window.speechSynthesis.speak(utterance);
        }
      }
      
      console.log("Test notification complete");
    } catch (error) {
      console.error("Error in test notification:", error);
    }
    
    handleClose();
  };

  // Filter notifications based on selected filters
  const filteredNotifications = (notifications || [])
    .filter(notification => {
      if (selectedGroup && notification.group !== selectedGroup) return false;
      if (selectedPriority && notification.priority !== selectedPriority) return false;
      return true;
    })
    .slice(0, 50); // Limit to 50 notifications

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        handleClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <>
      <Tooltip title="Notifications">
        <IconButton
          color="inherit"
          onClick={handleClick}
          sx={{ position: 'relative' }}
        >
          <Badge badgeContent={unreadCount} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>
      </Tooltip>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: {
            width: 360,
            maxHeight: 480
          }
        }}
      >
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Notifications</Typography>
          <Box>
            <IconButton size="small" onClick={handleSettingsClick} title="Notification Settings">
              <SettingsIcon />
            </IconButton>
            <IconButton size="small" onClick={handleClearAll} title="Clear All Notifications">
              <DeleteIcon />
            </IconButton>
          </Box>
        </Box>

        <Divider />
        
        <Box sx={{ p: 1, display: 'flex', gap: 1, justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <IconButton 
              size="small" 
              color={settings.desktop ? "primary" : "default"}
              onClick={handleToggleDesktopNotifications}
              title={settings.desktop ? "Desktop Notifications On" : "Desktop Notifications Off"}
            >
              {settings.desktop ? <NotificationsActiveIcon /> : <NotificationsOffIcon />}
            </IconButton>
            <IconButton 
              size="small" 
              color={settings.voice ? "primary" : "default"}
              onClick={handleToggleVoiceNotifications}
              title={settings.voice ? "Voice Notifications On" : "Voice Notifications Off"}
            >
              <VolumeUpIcon />
            </IconButton>
          </Box>
          <Button 
            size="small" 
            variant="outlined" 
            onClick={testNotification}
          >
            Test Notification
          </Button>
        </Box>

        <Divider />

        <Box sx={{ p: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {Object.values(NotificationGroup).map((group) => (
            <Chip
              key={group}
              label={group}
              size="small"
              onClick={() => handleFilterChange(group, selectedPriority)}
              color={selectedGroup === group ? 'primary' : 'default'}
              variant={selectedGroup === group ? 'filled' : 'outlined'}
            />
          ))}
        </Box>
        
        <Box sx={{ p: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {Object.values(NotificationPriority).map((priority) => (
            <Chip
              key={priority}
              label={priority}
              size="small"
              onClick={() => handleFilterChange(selectedGroup, priority)}
              color={selectedPriority === priority ? priorityColors[priority] : 'default'}
              variant={selectedPriority === priority ? 'filled' : 'outlined'}
            />
          ))}
        </Box>

        <Divider />

        {unreadCount > 0 && (
          <Box sx={{ p: 1 }}>
            <Button
              fullWidth
              variant="outlined"
              size="small"
              onClick={handleMarkAllAsRead}
            >
              Mark all as read
            </Button>
          </Box>
        )}

        <List sx={{ p: 0 }}>
          {filteredNotifications.length > 0 ? (
            filteredNotifications.map((notification) => (
              <React.Fragment key={notification.id}>
                <ListItem
                  button
                  onClick={() => handleNotificationClick(notification)}
                  sx={{
                    bgcolor: notification.read ? 'transparent' : 'action.hover',
                    '&:hover': { bgcolor: 'action.selected' }
                  }}
                >
                  <ListItemIcon>
                    {groupIcons[notification.group] || <InfoIcon />}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="body2" fontWeight={notification.read ? 'normal' : 'bold'}>
                        {notification.title || notification.message}
                      </Typography>
                    }
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Typography variant="caption">
                          {notification.timestamp ? formatDistanceToNow(new Date(notification.timestamp), { addSuffix: true }) : ''}
                        </Typography>
                        <Chip
                          label={notification.priority}
                          size="small"
                          color={priorityColors[notification.priority] || 'default'}
                          sx={{ height: 20, fontSize: '0.7rem' }}
                        />
                      </Box>
                    }
                  />
                </ListItem>
                <Divider />
              </React.Fragment>
            ))
          ) : (
            <ListItem>
              <ListItemText
                primary="No notifications"
                secondary="You're all caught up!"
              />
            </ListItem>
          )}
        </List>
      </Menu>
      
      <NotificationSettings 
        open={settingsOpen} 
        onClose={handleCloseSettings}
      />
    </>
  );
};

export default NotificationBell; 