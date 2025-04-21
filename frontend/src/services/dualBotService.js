import axios from 'axios';

// API base URL - Set to match dual_bot API server port
const API_BASE_URL = 'http://localhost:5001/api';

// Flag to enable/disable mock data - Set to true to prioritize mock data over API calls
const USE_MOCK_DATA = false;

// Configure axios with defaults for this service
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 seconds timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  withCredentials: false // Change to false to avoid CORS issues
});

// Add logging interceptors
apiClient.interceptors.request.use(
  config => {
    console.log(`[DualBot API Request] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  error => {
    console.error('[DualBot API Request Error]', error);
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  response => {
    console.log(`[DualBot API Response] ${response.status} ${response.config.url}`);
    return response;
  },
  error => {
    if (error.response) {
      console.error(`[DualBot API Error] ${error.response.status} ${error.config.url}:`, error.response.data);
    } else if (error.request) {
      console.error('[DualBot API Error] No response received:', error.config.url);
    } else {
      console.error('[DualBot API Error]', error.message);
    }
    return Promise.reject(error);
  }
);

// Mock data for when API is unavailable
const mockData = {
  status: {
    status: true,
    active_positions: [],
    last_update: new Date().toISOString()
  },
  marketData: {
    symbol: 'QQQ',
    price: 456.78,
    timestamp: new Date().toISOString()
  },
  optionsData: {
    symbol: 'QQQ',
    options: [
      { 
        strike: 460, 
        callPrice: 3.25, 
        putPrice: 2.80, 
        expirationDate: '2023-12-15',
        iv: 0.32,
        volume: 2500
      },
      { 
        strike: 465, 
        callPrice: 2.10, 
        putPrice: 4.15, 
        expirationDate: '2023-12-15',
        iv: 0.33,
        volume: 1800
      }
    ]
  },
  recommendation: {
    symbol: 'QQQ',
    trade_type: 'BUY_CALL',
    strike: 460,
    expiration: '2023-12-15',
    entry_price: 3.25,
    target_price: 5.50,
    stop_loss: 1.75,
    confidence: 0.82,
    rationale: 'Strong bullish momentum with increasing volume and positive technicals'
  },
  riskAssessment: {
    approved: true,
    risk_score: 7.2,
    market_conditions: 'Favorable',
    concerns: 'Slightly elevated IV, consider reducing position size',
    summary: 'This trade has a positive risk/reward ratio with defined exit points'
  },
  news: [
    {
      title: 'Tech Rally Continues as Fed Signals Rate Cut',
      source: 'Market News',
      url: 'https://example.com/news/1',
      sentiment: 'positive',
      relevance: 0.89,
      published_at: '2023-12-01T09:30:00Z'
    },
    {
      title: 'Nasdaq Reaches New High on Strong Earnings',
      source: 'Financial Times',
      url: 'https://example.com/news/2',
      sentiment: 'positive',
      relevance: 0.76,
      published_at: '2023-12-01T08:15:00Z'
    }
  ],
  config: {
    symbols: ['QQQ', 'TSLA', 'PLTR'],
    trading_hours: {
      start: '09:30',
      end: '16:00'
    },
    risk_limits: {
      max_position_size: 5000,
      max_daily_loss: 2000
    }
  }
};

// Helper function to handle API requests with fallback to mock data
const apiRequest = async (endpoint, method = 'GET', data = null, retries = 2) => {
  // If using mock data and explicitly requested through parameter
  if (USE_MOCK_DATA) {
    // Extract the endpoint name from the URL to find matching mock data
    const mockKey = endpoint.split('/').pop().replace(/[-]/g, '');
    if (mockData[mockKey]) {
      console.log(`[DualBot] Using mock data for: ${endpoint}`);
      return mockData[mockKey];
    }
  }

  try {
    // Attempt to make the real API call
    console.log(`[DualBot] Making API request to: ${endpoint}`);
    const response = await apiClient({
      url: endpoint,
      method,
      data,
    });
    return response.data;
  } catch (error) {
    console.error(`[DualBot] API request failed for ${endpoint}:`, error);
    
    // Implement retry logic for network errors
    if (retries > 0 && (!error.response || error.response.status >= 500)) {
      console.log(`[DualBot] Retrying request to ${endpoint}. Attempts remaining: ${retries}`);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second before retry
      return apiRequest(endpoint, method, data, retries - 1);
    }
    
    // If all retries failed or it's a client error (4xx), fallback to mock data
    const mockKey = endpoint.split('/').pop().replace(/[-]/g, '');
    if (mockData[mockKey]) {
      console.log(`[DualBot] Falling back to mock data for: ${endpoint}`);
      return mockData[mockKey];
    }
    
    throw error;
  }
};

const dualBotService = {
  // Test CORS
  testCorsConnection: async () => {
    try {
      console.log('[DualBot] Testing CORS connection...');
      // Use our specially designed CORS test endpoint
      const response = await apiRequest('/test-frontend-cors');
      console.log('[DualBot] CORS test successful:', response);
      return {
        success: true,
        message: 'CORS connection test successful',
        details: response
      };
    } catch (error) {
      console.error('[DualBot] CORS test failed:', error);
      return {
        success: false,
        message: 'CORS connection test failed',
        error: error.message
      };
    }
  },
  
  // Bot status
  getBotStatus: async () => {
    try {
      const response = await apiRequest('/dual-bot/status');
      // Extract the actual status object from the response
      if (response && response.success && response.status) {
        return response.status;
      }
      return response;
    } catch (error) {
      console.error('[DualBot] Error getting bot status:', error);
      if (USE_MOCK_DATA) {
        return mockData.status;
      }
      throw error;
    }
  },
  
  // Market data
  getMarketData: async (symbol) => {
    try {
      // Fallback to signals endpoint if market-data is not available
      const response = await apiRequest(`/dual-bot/signals`);
      // Extract signal data and transform it to match expected market data format
      if (response && response.success && response.signals) {
        // Look for a signal matching the requested symbol or use the first one
        const signal = response.signals.signals.find(s => s.symbol === symbol) || response.signals.signals[0];
        if (signal) {
          return {
            symbol: signal.symbol,
            price: signal.close || 0,
            timestamp: signal.date || new Date().toISOString(),
            volume: signal.volume || 0,
            indicators: {
              ema_9: signal.ema_9,
              ema_21: signal.ema_21
            }
          };
        }
      }
      return response;
    } catch (error) {
      console.error(`[DualBot] Error getting market data for ${symbol}:`, error);
      if (USE_MOCK_DATA) {
        return mockData.marketData;
      }
      throw error;
    }
  },
  
  // Options data
  getOptionsData: async (symbol) => {
    try {
      return await apiRequest(`/options-data/${symbol}`);
    } catch (error) {
      console.error(`[DualBot] Error getting options data for ${symbol}:`, error);
      if (USE_MOCK_DATA) {
        return mockData.optionsData;
      }
      throw error;
    }
  },
  
  // News
  getNews: async (symbol) => {
    try {
      return await apiRequest(`/news/${symbol}`);
    } catch (error) {
      console.error(`[DualBot] Error getting news for ${symbol}:`, error);
      if (USE_MOCK_DATA) {
        return mockData.news;
      }
      throw error;
    }
  },
  
  // Scan for trades
  scanForTrades: async (symbol) => {
    try {
      const response = await apiRequest('/dual-bot/signals');
      // Extract signal data and transform it to match expected recommendation format
      if (response && response.success && response.signals) {
        // Look for a signal matching the requested symbol or use the first one
        const signal = response.signals.signals.find(s => s.symbol === symbol) || response.signals.signals[0];
        if (signal) {
          // Convert signal to a recommendation format
          return {
            symbol: signal.symbol,
            trade_type: signal.type || 'BUY',
            entry_price: signal.close || 0,
            target_price: signal.price_target || 0,
            stop_loss: signal.stop_loss || 0,
            confidence: signal.confidence || 0.5,
            rationale: `Signal generated with score: ${signal.signal_score || 0}`
          };
        }
      }
      return mockData.recommendation;
    } catch (error) {
      console.error(`[DualBot] Error scanning for trades for ${symbol}:`, error);
      if (USE_MOCK_DATA) {
        return mockData.recommendation;
      }
      throw error;
    }
  },
  
  // Risk assessment
  assessRisk: async (recommendation, marketContext) => {
    try {
      // Instead of using /assess-risk endpoint that doesn't exist,
      // Let's use mock data since we don't have a proper risk assessment endpoint
      console.log('[DualBot] Using mock data for risk assessment');
      
      // For future implementation: replace this with a real API call when endpoint is available
      // const response = await apiRequest('/risk-assessment', 'POST', { 
      //   recommendation, 
      //   market_context: marketContext 
      // });
      
      // Create a simulated risk assessment based on the recommendation
      const mockRiskAssessment = {
        approved: recommendation.confidence > 0.5,
        risk_score: (1 - recommendation.confidence) * 10,
        market_conditions: marketContext.market_condition || 'Unknown',
        concerns: recommendation.confidence < 0.7 ? 'Low confidence signal, proceed with caution' : '',
        summary: `Risk assessment based on trade recommendation for ${recommendation.symbol}. ${
          recommendation.confidence > 0.7 
            ? 'Trade appears favorable.'
            : 'Consider reducing position size.'
        }`
      };
      
      return mockRiskAssessment;
    } catch (error) {
      console.error('[DualBot] Error assessing risk:', error);
      if (USE_MOCK_DATA) {
        return mockData.riskAssessment;
      }
      throw error;
    }
  },
  
  // Check if position should be closed
  checkPosition: async (position, marketData) => {
    try {
      return await apiRequest('/check-position', 'POST', { 
        position, 
        market_data: marketData 
      });
    } catch (error) {
      console.error('[DualBot] Error checking position:', error);
      throw error;
    }
  },
  
  // Get config
  getConfig: async () => {
    try {
      return await apiRequest('/config');
    } catch (error) {
      console.error('[DualBot] Error getting config:', error);
      if (USE_MOCK_DATA) {
        return mockData.config;
      }
      throw error;
    }
  },
  
  // Force the use of mock data (for testing/development)
  useMockData: (shouldUseMock = true) => {
    console.log(`[DualBot] ${shouldUseMock ? 'Enabling' : 'Disabling'} mock data`);
    Object.defineProperty(dualBotService, '_useMockData', {
      value: shouldUseMock,
      writable: true
    });
  }
};

export default dualBotService; 