import React, { useState, useEffect, useRef } from 'react';
import { Bell, BellOff, Check, X, AlertTriangle, Info, CheckCircle } from 'lucide-react';
import { useRouter } from 'next/router';
import { useNotificationContext } from '../contexts/NotificationContext';

const NotificationBell = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const bellRef = useRef(null);
  const router = useRouter();
  const { notifications, markAsRead, clearAll } = useNotificationContext();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (bellRef.current && !bellRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Update unread count when notifications change
  useEffect(() => {
    const count = notifications.filter(notification => !notification.read).length;
    setUnreadCount(count);
  }, [notifications]);

  // Get icon based on notification type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'trade_entry':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'trade_exit':
        return <Check className="h-5 w-5 text-blue-500" />;
      case 'stop_loss':
        return <X className="h-5 w-5 text-red-500" />;
      case 'profit_target':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'risk_breach':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'system_error':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'market_alert':
        return <Info className="h-5 w-5 text-blue-500" />;
      default:
        return <Info className="h-5 w-5 text-gray-500" />;
    }
  };

  // Navigate to the relevant page based on notification type
  const handleNotificationClick = (notification) => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
    
    // Navigate based on notification type and data
    switch (notification.type) {
      case 'trade_entry':
      case 'trade_exit':
      case 'stop_loss':
      case 'profit_target':
        router.push(`/trades/${notification.data.symbol}`);
        break;
      case 'risk_breach':
        router.push('/risk-management');
        break;
      case 'system_error':
        router.push('/system-status');
        break;
      case 'market_alert':
        router.push(`/market-analysis/${notification.data.symbol}`);
        break;
      default:
        router.push('/dashboard');
    }
    
    setIsOpen(false);
  };

  // Format timestamp to relative time
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  return (
    <div className="relative" ref={bellRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
        aria-label="Notifications"
      >
        {unreadCount > 0 ? (
          <Bell className="h-6 w-6" />
        ) : (
          <BellOff className="h-6 w-6" />
        )}
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-500 rounded-full">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg overflow-hidden z-50">
          <div className="p-3 border-b border-gray-200 flex justify-between items-center">
            <h3 className="text-sm font-medium text-gray-900">Notifications</h3>
            {notifications.length > 0 && (
              <button
                onClick={clearAll}
                className="text-xs text-gray-500 hover:text-gray-700"
              >
                Clear all
              </button>
            )}
          </div>
          
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No notifications
              </div>
            ) : (
              <ul className="divide-y divide-gray-200">
                {notifications.map((notification) => (
                  <li
                    key={notification.id}
                    className={`p-3 hover:bg-gray-50 cursor-pointer ${
                      !notification.read ? 'bg-blue-50' : ''
                    }`}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <div className="flex items-start">
                      <div className="flex-shrink-0 mt-0.5">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="ml-3 w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {notification.title}
                        </p>
                        <p className="mt-1 text-xs text-gray-500">
                          {notification.message}
                        </p>
                        <p className="mt-1 text-xs text-gray-400">
                          {formatTimestamp(notification.timestamp)}
                        </p>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
          
          {notifications.length > 0 && (
            <div className="p-2 border-t border-gray-200">
              <button
                onClick={() => router.push('/notifications')}
                className="w-full text-center text-xs text-blue-600 hover:text-blue-800"
              >
                View all notifications
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationBell; 