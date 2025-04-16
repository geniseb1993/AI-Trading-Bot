import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

// Notification priority levels
export const NotificationPriority = {
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low'
};

// Notification groups
export const NotificationGroup = {
  TRADE: 'trade',
  SYSTEM: 'system',
  ALERT: 'alert',
  ERROR: 'error'
};

// Create context
const NotificationContext = createContext();

// Context provider component
export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState(null);
  const [notificationSettings, setNotificationSettings] = useState({
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
  });

  // Load notifications and settings from localStorage on initial render
  useEffect(() => {
      const savedNotifications = localStorage.getItem('notifications');
    const savedSettings = localStorage.getItem('notificationSettings');
    
      if (savedNotifications) {
      try {
        setNotifications(JSON.parse(savedNotifications));
      } catch (error) {
        console.error('Error parsing saved notifications:', error);
      }
    }
    
    if (savedSettings) {
      try {
        setNotificationSettings(JSON.parse(savedSettings));
    } catch (error) {
        console.error('Error parsing saved notification settings:', error);
      }
    }
  }, []);

  // Save notifications to localStorage when they change
  useEffect(() => {
      localStorage.setItem('notifications', JSON.stringify(notifications));
  }, [notifications]);
  
  // Save notification settings to localStorage when they change
  useEffect(() => {
    localStorage.setItem('notificationSettings', JSON.stringify(notificationSettings));
  }, [notificationSettings]);

  const addNotification = useCallback(({
    id = Date.now(),
    message,
    type = 'info',
    priority = NotificationPriority.MEDIUM,
    group = NotificationGroup.SYSTEM,
    template = null,
    templateData = null,
    timestamp = new Date().toISOString(),
    read = false
  }) => {
    setNotifications(prev => [{
      id,
      message,
      type,
      priority,
      group,
      template,
      templateData,
      timestamp,
      read
    }, ...prev]);

    if (!read) {
      setUnreadCount(prev => prev + 1);
    }
  }, []);

  const markAsRead = useCallback((notificationId) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === notificationId
          ? { ...notification, read: true }
          : notification
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, read: true }))
    );
    setUnreadCount(0);
  }, []);

  const removeNotification = useCallback((notificationId) => {
    setNotifications(prev =>
      prev.filter(notification => notification.id !== notificationId)
    );
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
    setUnreadCount(0);
  }, []);

  const updateNotificationSettings = useCallback((newSettings) => {
    setNotificationSettings(prev => ({
      ...prev,
      ...newSettings
    }));
  }, []);

  const getFilteredNotifications = useCallback(({
    priority = null,
    group = null,
    read = null,
    limit = 50
  } = {}) => {
    return notifications
      .filter(notification => {
        if (priority && notification.priority !== priority) return false;
        if (group && notification.group !== group) return false;
        if (read !== null && notification.read !== read) return false;
        return true;
      })
      .slice(0, limit);
  }, [notifications]);

  // Send desktop notification
  const sendDesktopNotification = useCallback((notification) => {
    try {
      console.log("Attempting to send desktop notification:", notification);
      
      if (!notificationSettings.desktop) {
        console.warn("Desktop notifications are disabled in settings");
        return false;
      }
      
      // Check browser support and permission
      if (!("Notification" in window)) {
        console.error("Browser does not support desktop notifications");
        return false;
      }
      
      if (Notification.permission === "granted") {
        // Create notification
        new Notification(notification.title, {
          body: notification.message,
          icon: "/logo192.png"
        });
        console.log("Desktop notification sent successfully");
        return true;
      } 
      else if (Notification.permission !== "denied") {
        // Request permission
        Notification.requestPermission().then(permission => {
          if (permission === "granted") {
            new Notification(notification.title, {
              body: notification.message,
              icon: "/logo192.png"
            });
            console.log("Desktop notification sent after permission grant");
            return true;
          }
        });
      }
      
      console.warn("Notification permission not granted");
      return false;
    } catch (error) {
      console.error("Error sending desktop notification:", error);
      return false;
    }
  }, [notificationSettings.desktop]);

  // Send voice notification using Hume AI API
  const sendVoiceNotification = useCallback((notification) => {
    try {
      console.log("Attempting to send voice notification:", notification);
      
      if (!notificationSettings.voice) {
        console.warn("Voice notifications are disabled in settings");
        return false;
      }
      
      const useHumeAI = notificationSettings.voice?.useHumeAI === true;
      console.log(`Voice settings - useHumeAI: ${useHumeAI}`);
      
      // First try to use Hume AI for voice
      if (useHumeAI) {
        console.log("Sending voice notification via Hume AI API");
        
        // Make API call to backend for Hume AI speech
        axios.post('/api/notifications/speak', {
          message: `${notification.title}. ${notification.message}`,
          priority: notification.priority || NotificationPriority.MEDIUM,
          use_hume: true
        })
        .then(response => {
          console.log("Hume AI API response:", response.data);
          if (!response.data.success) {
            console.warn("Hume AI failed, falling back to browser speech");
            // Fall back to browser speech if Hume fails
            useBrowserSpeech(notification);
          }
        })
        .catch(error => {
          console.error("Error calling Hume API:", error);
          // Fall back to browser speech on error
          console.warn("Error with Hume AI, falling back to browser speech");
          useBrowserSpeech(notification);
        });
        
        return true;
      } else {
        // Use browser speech synthesis if Hume is disabled
        console.log("Using browser speech synthesis (Hume AI disabled in settings)");
        return useBrowserSpeech(notification);
      }
    } catch (error) {
      console.error("Error in voice notification:", error);
      // Attempt browser speech as last resort
      return useBrowserSpeech(notification);
    }
  }, [notificationSettings.voice]);
  
  // Helper function for browser speech
  const useBrowserSpeech = useCallback((notification) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance();
      utterance.text = `${notification.title}. ${notification.message}`;
      utterance.rate = notificationSettings.voice?.rate ? notificationSettings.voice.rate / 100 : 1;
      utterance.volume = notificationSettings.voice?.volume || 0.8;
      
      window.speechSynthesis.speak(utterance);
      console.log("Browser speech synthesis used");
      return true;
    } else {
      console.error("Browser does not support speech synthesis");
      return false;
    }
  }, [notificationSettings.voice]);

  // Show a notification
  const showNotification = (title, message, severity = 'info') => {
    const id = Date.now();
    const newNotification = {
      id,
      title,
      message,
      severity,
      timestamp: new Date().toISOString()
    };
    
    setNotifications(prev => [...prev, newNotification]);
    
    // Auto-remove notification after 5 seconds
    setTimeout(() => {
      removeNotification(id);
    }, 5000);
    
    return id;
  };

  // The context value
  const contextValue = {
    notifications,
    unreadCount,
    isConnected,
    notificationSettings,
    addNotification,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll: clearNotifications,
    updateNotificationSettings,
    getFilteredNotifications,
    sendDesktopNotification,
    sendVoiceNotification,
    showNotification
  };

  // Expose context to window for troubleshooting
  if (typeof window !== 'undefined') {
    window.__NOTIFICATION_CONTEXT__ = contextValue;
  }

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
    </NotificationContext.Provider>
  );
}; 

// Custom hook for using the notification context
export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

export default NotificationContext; 