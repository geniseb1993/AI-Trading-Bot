import axios from 'axios';

// Constants
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';
const USE_MOCK_DATA = process.env.REACT_APP_USE_MOCK_DATA === 'true';
const AUTO_FALLBACK = true; // Automatically fallback to mock data when API fails

// Mock data for when API is not available
const mockData = {
  brokers: ['mock', 'alpaca', 'interactive_brokers', 'td_ameritrade'],
  activeBroker: 'mock',
  config: {
    active_broker: 'mock',
    mock: {
      use_real_data: false,
      simulated_slippage: 0.01,
      simulated_latency: 500
    },
    alpaca: {
      api_key: '**********',
      api_secret: '**********',
      paper_trading: true,
      base_url: 'https://paper-api.alpaca.markets'
    },
    interactive_brokers: {
      tws_port: 7497,
      client_id: 1,
      host: 'localhost',
      read_only: true
    },
    td_ameritrade: {
      api_key: '**********',
      refresh_token: '**********',
      callback_url: 'http://localhost:5000/callback'
    }
  }
};

/**
 * API request helper function with retry and mock fallback
 * @param {string} endpoint - API endpoint to request
 * @param {string} method - HTTP method (GET, POST, etc.)
 * @param {object} data - Optional data to send with request
 * @param {number} retries - Number of retries on failure
 * @returns {Promise} - Promise resolving to API response
 */
const apiRequest = async (endpoint, method = 'GET', data = null, retries = 1) => {
  if (USE_MOCK_DATA) {
    console.log(`[BrokerService] Using mock data for ${endpoint}`);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Return mock data based on endpoint
    if (endpoint.includes('available')) {
      return {
        success: true,
        brokers: mockData.brokers,
        active_broker: mockData.activeBroker
      };
    }
    else if (endpoint.includes('config')) {
      return {
        success: true,
        config: mockData.config
      };
    }
    else if (endpoint.includes('set-active')) {
      const broker = data.broker;
      mockData.activeBroker = broker;
      mockData.config.active_broker = broker;
      return {
        success: true,
        message: `Active broker set to ${broker}`
      };
    }
    else if (endpoint.includes('update-config')) {
      mockData.config = data;
      return {
        success: true,
        message: 'Broker configuration updated successfully'
      };
    }
    else if (endpoint.includes('test-connection')) {
      const broker = data.broker;
      return {
        success: true,
        message: `Connection to ${broker} successful (mock)`,
        details: {
          connected: true,
          timestamp: new Date().toISOString(),
          account_id: `mock-account-${Math.floor(Math.random() * 1000)}`
        }
      };
    }
    
    // Default mock response
    return {
      success: true,
      message: 'Mock data response'
    };
  }
  
  // Real API request logic
  try {
    const url = `${API_BASE_URL}/${endpoint}`;
    console.log(`[BrokerService] Requesting ${method} ${url}`);
    
    let response;
    if (method === 'GET') {
      response = await axios.get(url);
    } else if (method === 'POST') {
      response = await axios.post(url, data);
    } else if (method === 'PUT') {
      response = await axios.put(url, data);
    } else if (method === 'DELETE') {
      response = await axios.delete(url);
    }
    
    console.log(`[BrokerService] Response:`, response.data);
    return response.data;
  } catch (error) {
    console.error(`[BrokerService] Error (${retries} retries left):`, error.message);
    
    // Retry logic
    if (retries > 0) {
      console.log(`[BrokerService] Retrying...`);
      await new Promise(resolve => setTimeout(resolve, 1000));
      return apiRequest(endpoint, method, data, retries - 1);
    }
    
    // Fallback to mock data if enabled
    if (AUTO_FALLBACK) {
      console.log(`[BrokerService] Falling back to mock data`);
      return apiRequest(endpoint, method, data, 0);
    }
    
    throw error;
  }
};

/**
 * Broker Service - handles all broker API interactions
 */
const brokerService = {
  /**
   * Get available brokers
   * @returns {Promise} List of available brokers and active broker
   */
  getAvailableBrokers: async () => {
    try {
      return await apiRequest('broker/available');
    } catch (error) {
      console.error('[BrokerService] Error getting available brokers:', error);
      if (AUTO_FALLBACK) {
        return {
          success: true,
          brokers: mockData.brokers,
          active_broker: mockData.activeBroker
        };
      }
      throw error;
    }
  },
  
  /**
   * Get broker configuration
   * @returns {Promise} Current broker configuration
   */
  getConfig: async () => {
    try {
      return await apiRequest('broker/config');
    } catch (error) {
      console.error('[BrokerService] Error getting broker config:', error);
      if (AUTO_FALLBACK) {
        return {
          success: true,
          config: mockData.config
        };
      }
      throw error;
    }
  },
  
  /**
   * Set active broker
   * @param {string} broker - Broker to set as active
   * @returns {Promise} Result of operation
   */
  setActiveBroker: async (broker) => {
    try {
      return await apiRequest('broker/set-active', 'POST', { broker });
    } catch (error) {
      console.error('[BrokerService] Error setting active broker:', error);
      if (AUTO_FALLBACK) {
        mockData.activeBroker = broker;
        mockData.config.active_broker = broker;
        return {
          success: true,
          message: `Active broker set to ${broker} (mock)`
        };
      }
      throw error;
    }
  },
  
  /**
   * Update broker configuration
   * @param {object} config - New broker configuration
   * @returns {Promise} Result of operation
   */
  updateConfig: async (config) => {
    try {
      return await apiRequest('broker/update-config', 'POST', config);
    } catch (error) {
      console.error('[BrokerService] Error updating broker config:', error);
      if (AUTO_FALLBACK) {
        mockData.config = config;
        return {
          success: true,
          message: 'Broker configuration updated successfully (mock)'
        };
      }
      throw error;
    }
  },
  
  /**
   * Test connection to broker
   * @param {string} broker - Broker to test connection with
   * @returns {Promise} Connection test result
   */
  testConnection: async (broker) => {
    try {
      return await apiRequest('broker/test-connection', 'POST', { broker });
    } catch (error) {
      console.error('[BrokerService] Error testing broker connection:', error);
      if (AUTO_FALLBACK) {
        return {
          success: true,
          message: `Connection to ${broker} successful (mock)`,
          details: {
            connected: true,
            timestamp: new Date().toISOString(),
            account_id: `mock-account-${Math.floor(Math.random() * 1000)}`
          }
        };
      }
      throw error;
    }
  }
};

export default brokerService; 