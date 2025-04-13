import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { 
  Bell, 
  Check, 
  X, 
  AlertTriangle, 
  Info, 
  CheckCircle, 
  Trash2, 
  CheckSquare, 
  Filter,
  Search
} from 'lucide-react';
import { useNotificationContext } from '../contexts/NotificationContext';
import Layout from '../components/Layout';

const NotificationsPage = () => {
  const router = useRouter();
  const { 
    notifications, 
    markAsRead, 
    markAllAsRead, 
    clearAll, 
    removeNotification 
  } = useNotificationContext();
  
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Filter notifications based on selected filter and search term
  const filteredNotifications = notifications.filter(notification => {
    // Apply type filter
    if (filter !== 'all' && notification.type !== filter) {
      return false;
    }
    
    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return (
        notification.title.toLowerCase().includes(searchLower) ||
        notification.message.toLowerCase().includes(searchLower) ||
        (notification.data.symbol && notification.data.symbol.toLowerCase().includes(searchLower))
      );
    }
    
    return true;
  });
  
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
  
  // Format timestamp to readable date and time
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  // Handle notification click
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
  };
  
  return (
    <Layout>
      <Head>
        <title>Notifications | AI Trading Bot</title>
      </Head>
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          <div className="flex space-x-2">
            <button
              onClick={markAllAsRead}
              className="flex items-center px-3 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200"
            >
              <CheckSquare className="h-4 w-4 mr-1" />
              Mark all as read
            </button>
            <button
              onClick={clearAll}
              className="flex items-center px-3 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200"
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Clear all
            </button>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 border-b border-gray-200">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 md:space-x-4">
              <div className="relative flex-grow">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="Search notifications..."
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              <div className="flex items-center">
                <Filter className="h-5 w-5 text-gray-400 mr-2" />
                <select
                  className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                >
                  <option value="all">All Types</option>
                  <option value="trade_entry">Trade Entry</option>
                  <option value="trade_exit">Trade Exit</option>
                  <option value="stop_loss">Stop Loss</option>
                  <option value="profit_target">Profit Target</option>
                  <option value="risk_breach">Risk Breach</option>
                  <option value="system_error">System Error</option>
                  <option value="market_alert">Market Alert</option>
                </select>
              </div>
            </div>
          </div>
          
          {filteredNotifications.length === 0 ? (
            <div className="p-8 text-center">
              <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-1">No notifications</h3>
              <p className="text-gray-500">
                {searchTerm || filter !== 'all' 
                  ? 'No notifications match your search criteria' 
                  : 'You have no notifications yet'}
              </p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {filteredNotifications.map((notification) => (
                <li 
                  key={notification.id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer ${
                    !notification.read ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => handleNotificationClick(notification)}
                >
                  <div className="flex items-start">
                    <div className="flex-shrink-0 mt-0.5">
                      {getNotificationIcon(notification.type)}
                    </div>
                    <div className="ml-3 flex-1">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900">
                          {notification.title}
                        </p>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(notification.timestamp)}
                          </span>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              removeNotification(notification.id);
                            }}
                            className="text-gray-400 hover:text-red-500"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      <p className="mt-1 text-sm text-gray-500">
                        {notification.message}
                      </p>
                      
                      {/* Display additional data based on notification type */}
                      {notification.type === 'trade_entry' && (
                        <div className="mt-2 flex items-center space-x-4 text-xs">
                          <span className="px-2 py-1 bg-green-100 text-green-800 rounded">
                            {notification.data.direction}
                          </span>
                          <span className="text-gray-600">
                            Price: ${notification.data.price}
                          </span>
                        </div>
                      )}
                      
                      {notification.type === 'market_alert' && (
                        <div className="mt-2 flex items-center space-x-4 text-xs">
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                            {notification.data.alertType}
                          </span>
                        </div>
                      )}
                      
                      {notification.type === 'risk_breach' && (
                        <div className="mt-2 flex items-center space-x-4 text-xs">
                          <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded">
                            Risk Level: {notification.data.riskLevel}
                          </span>
                          <span className="text-gray-600">
                            Exposure: {(notification.data.currentExposure * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default NotificationsPage; 