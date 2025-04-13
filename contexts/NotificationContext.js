import React, { createContext, useContext, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

// Create context
const NotificationContext = createContext();

// Custom hook to use the notification context
export const useNotification = () => useContext(NotificationContext);

// Notification priorities
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

// Provider component
export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
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

  // Connect to WebSocket for real-time notifications
  useEffect(() => {
    // This would be replaced with your actual WebSocket connection
    // For now, we'll simulate it with a timer
    const connectWebSocket = () => {
      setIsConnected(true);
      
      // Simulate receiving notifications
      const interval = setInterval(() => {
        // Only add notifications occasionally to avoid flooding
        if (Math.random() > 0.7) {
          addNotification(generateRandomNotification());
        }
      }, 30000); // Check every 30 seconds
      
      return interval;
    };
    
    const interval = connectWebSocket();
    
    return () => {
      clearInterval(interval);
      setIsConnected(false);
    };
  }, []);

  // Generate a random notification for demonstration
  const generateRandomNotification = () => {
    const types = ['trade_entry', 'trade_exit', 'stop_loss', 'profit_target', 'risk_breach', 'system_error', 'market_alert'];
    const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'];
    const type = types[Math.floor(Math.random() * types.length)];
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    
    let title, message, data;
    
    switch (type) {
      case 'trade_entry':
        title = `New Trade: ${symbol}`;
        message = `Entered LONG position at $${(Math.random() * 100 + 100).toFixed(2)}`;
        data = { symbol, price: (Math.random() * 100 + 100).toFixed(2), direction: 'LONG' };
        break;
      case 'trade_exit':
        title = `Trade Exit: ${symbol}`;
        message = `Exited position at $${(Math.random() * 100 + 100).toFixed(2)}`;
        data = { symbol, price: (Math.random() * 100 + 100).toFixed(2) };
        break;
      case 'stop_loss':
        title = `Stop Loss Triggered: ${symbol}`;
        message = `Position stopped out at $${(Math.random() * 100 + 100).toFixed(2)}`;
        data = { symbol, price: (Math.random() * 100 + 100).toFixed(2) };
        break;
      case 'profit_target':
        title = `Profit Target Hit: ${symbol}`;
        message = `Position closed at profit target $${(Math.random() * 100 + 100).toFixed(2)}`;
        data = { symbol, price: (Math.random() * 100 + 100).toFixed(2) };
        break;
      case 'risk_breach':
        title = `Risk Management Alert`;
        message = `Account risk level exceeded threshold`;
        data = { riskLevel: 'HIGH', currentExposure: (Math.random() * 0.1).toFixed(3) };
        break;
      case 'system_error':
        title = `System Error`;
        message = `Connection to market data feed lost`;
        data = { errorType: 'ConnectionError', component: 'Market Data' };
        break;
      case 'market_alert':
        title = `Market Alert: ${symbol}`;
        message = `Unusual volume detected`;
        data = { symbol, alertType: 'VOLATILITY_SPIKE' };
        break;
      default:
        title = `Notification`;
        message = `This is a notification`;
        data = {};
    }
    
    return {
      id: uuidv4(),
      type,
      title,
      message,
      data,
      priority: NotificationPriority.MEDIUM,
      group: NotificationGroup.TRADE,
      timestamp: new Date().toISOString(),
      read: false
    };
  };

  // Add a new notification
  const addNotification = async (notif) => {
    console.log("Adding notification:", notif);
    // Create a notification with default fields if not provided
    const notification = {
      id: notif.id || Date.now(),
      type: notif.type || 'info',
      title: notif.title || 'Notification',
      message: notif.message || '',
      data: notif.data || {},
      priority: notif.priority || NotificationPriority.MEDIUM,
      group: notif.group || NotificationGroup.SYSTEM,
      timestamp: notif.timestamp || new Date().toISOString(),
      read: false
    };

    setNotifications(prev => [notification, ...prev]);
    
    // Send desktop notification if enabled
    if (notificationSettings.desktop) {
      console.log("Desktop notifications enabled, sending notification");
      try {
        await sendDesktopNotification(notification);
      } catch (error) {
        console.error("Failed to send desktop notification:", error);
      }
    } else {
      console.log("Desktop notifications disabled");
    }
    
    // Send voice notification if enabled
    if (notificationSettings.voice) {
      console.log("Voice notifications enabled, sending notification");
      try {
        await sendVoiceNotification(notification);
      } catch (error) {
        console.error("Failed to send voice notification:", error);
      }
    } else {
      console.log("Voice notifications disabled");
    }
    
    // Return the created notification
    return notification;
  };
  
  // Send desktop notification
  const sendDesktopNotification = async (notification) => {
    try {
      console.log("Sending desktop notification:", notification);
      
      if (!notificationSettings.desktop) {
        console.warn("Desktop notifications are disabled in settings");
        return false;
      }
      
      // Check if browser supports notifications
      if (!("Notification" in window)) {
        console.error("This browser does not support desktop notifications");
        return false;
      }
      
      // Check if permission is already granted
      if (Notification.permission === "granted") {
        // Create and show the notification directly
        new Notification(notification.title, {
          body: notification.message,
          icon: "/logo192.png" // Update with your app's logo path
        });
        return true;
      } 
      else if (Notification.permission !== "denied") {
        // Request permission
        const permission = await Notification.requestPermission();
        if (permission === "granted") {
          // Create and show the notification
          new Notification(notification.title, {
            body: notification.message,
            icon: "/logo192.png" // Update with your app's logo path
          });
          return true;
        }
      }
      
      console.warn("Desktop notification permission denied");
      return false;
    } catch (error) {
      console.error("Error sending desktop notification:", error);
      return false;
    }
  };
  
  // Send voice notification to backend
  const sendVoiceNotification = async (notification) => {
    try {
      console.log("Sending voice notification:", notification);
      
      if (!notificationSettings.voice) {
        console.warn("Voice notifications are disabled in settings");
        return false;
      }
      
      // First try to use the Hume AI API
      if (notificationSettings.voice?.useHumeAI) {
        try {
          console.log("Attempting to use Hume AI for voice notification");
          const response = await axios.post('/api/notifications/speak', {
            message: `${notification.title}. ${notification.message}`,
            priority: notification.priority || NotificationPriority.MEDIUM,
            use_hume: true
          });
          
          console.log("Hume AI voice notification API response:", response.data);
          if (response.data.success) {
            return true;
          } else {
            console.warn("Hume AI request failed, falling back to browser speech synthesis");
          }
        } catch (apiError) {
          console.error("Error calling Hume voice API:", apiError);
          console.warn("Falling back to browser speech synthesis");
        }
      } else {
        console.log("Hume AI is disabled in settings, using browser speech synthesis");
      }
      
      // Fall back to browser speech synthesis if Hume is disabled or fails
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance();
        utterance.text = `${notification.title}. ${notification.message}`;
        utterance.rate = notificationSettings.voice?.rate ? notificationSettings.voice.rate / 100 : 1;
        utterance.volume = notificationSettings.voice?.volume || 0.8;
        
        window.speechSynthesis.speak(utterance);
        console.log("Voice notification sent using browser speech synthesis");
        return true;
      } else {
        console.error("Browser does not support speech synthesis");
        return false;
      }
    } catch (error) {
      console.error("Error sending voice notification:", error);
      return false;
    }
  };
  
  // Send notification to backend service
  const sendToBackendNotificationService = async (notification) => {
    try {
      await axios.post('/api/notifications', {
        message: notification.message,
        title: notification.title,
        notification_type: notification.type,
        priority: notification.priority || NotificationPriority.MEDIUM,
        group: notification.group || NotificationGroup.TRADE,
        data: notification.data || {}
      });
    } catch (error) {
      console.error('Error sending to backend notification service:', error);
    }
  };

  // Mark a notification as read
  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  };

  // Mark all notifications as read
  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    );
  };

  // Clear all notifications
  const clearAll = () => {
    setNotifications([]);
  };

  // Remove a notification
  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  };
  
  // Update notification settings
  const updateNotificationSettings = (newSettings) => {
    setNotificationSettings(prev => ({
      ...prev,
      ...newSettings
    }));
  };
  
  // Get unread count
  const getUnreadCount = () => {
    return notifications.filter(notification => !notification.read).length;
  };

  // Value object to be provided to consumers
  const value = {
    notifications,
    isConnected,
    notificationSettings,
    addNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    removeNotification,
    updateNotificationSettings,
    unreadCount: getUnreadCount(),
    sendDesktopNotification,
    sendVoiceNotification
  };
  
  // Expose context to window for troubleshooting
  if (typeof window !== 'undefined') {
    window.__NOTIFICATION_CONTEXT__ = value;
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext; 