import axios from 'axios';

// API base URL - Set to match dual_bot API server port
const API_BASE_URL = '/api';
// Market data API URL - Fixed direct endpoint
const MARKET_DATA_URL = 'http://localhost:5001/api';

// Flag to enable/disable mock data - Set to false to use real data
const USE_MOCK_DATA = false;
// Set to false to fail rather than fallback to mock data - this helps debug data issues
const AUTO_FALLBACK = false;  

// Configure axios with defaults for this service
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // Increased timeout to 10 seconds for slower connections
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  withCredentials: true // Enable credentials for CORS
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
  },
  tradingHistory: [
    {
      id: "mock-1",
      symbol: "QQQ",
      strategy: "Options Flow",
      entryDate: "2025-04-10T14:30:00Z",
      exitDate: "2025-04-11T15:45:00Z",
      entryPrice: 450.25,
      exitPrice: 455.75,
      profit: 1350,
      profitPercent: 5.5,
      tradeType: "LONG"
    },
    {
      id: "mock-2",
      symbol: "TSLA",
      strategy: "Momentum",
      entryDate: "2025-04-15T10:15:00Z",
      exitDate: "2025-04-17T11:30:00Z",
      entryPrice: 180.50,
      exitPrice: 187.25,
      profit: 840,
      profitPercent: 3.7,
      tradeType: "LONG"
    }
  ],
  performance: {
    totalTrades: 45,
    winRate: 68.5,
    profitFactor: 2.3,
    averageProfit: 850,
    netProfit: 38250,
    maxDrawdown: 12500,
    dailyReturns: [
      { date: "2025-04-01", return: 1.5 },
      { date: "2025-04-02", return: 0.8 },
      { date: "2025-04-03", return: -0.5 },
      { date: "2025-04-04", return: 2.1 },
      { date: "2025-04-05", return: 0.3 }
    ]
  },
  alerts: [
    {
      id: "alert-1",
      timestamp: "2025-04-26T09:45:00Z",
      symbol: "SPY",
      message: "Bullish divergence detected on SPY 4h chart",
      source: "TradingView",
      status: "new"
    },
    {
      id: "alert-2",
      timestamp: "2025-04-26T10:15:00Z",
      symbol: "QQQ",
      message: "QQQ crossing above 20-day EMA",
      source: "TradingView",
      status: "read"
    }
  ],
  institutionalFlow: {
    darkPool: [
      {
        symbol: "AAPL",
        timestamp: "2025-04-26T14:30:00Z",
        price: 185.75,
        volume: 250000,
        sentiment: "bullish",
        source: "Mock Data"
      },
      {
        symbol: "MSFT",
        timestamp: "2025-04-26T14:15:00Z",
        price: 415.50,
        volume: 180000,
        sentiment: "neutral",
        source: "Mock Data"
      }
    ],
    optionsFlow: [
      {
        symbol: "SPY",
        timestamp: "2025-04-26T13:45:00Z",
        strike: 485,
        expiration: "2025-05-15",
        premium: 1250000,
        sentiment: "bullish",
        contractType: "CALL",
        source: "Mock Data"
      },
      {
        symbol: "QQQ",
        timestamp: "2025-04-26T14:05:00Z",
        strike: 440,
        expiration: "2025-05-15",
        premium: 950000,
        sentiment: "bullish",
        contractType: "CALL",
        source: "Mock Data"
      }
    ]
  },
  tradeSetups: [
    {
      id: "setup-1",
      symbol: "AAPL",
      setup: "Bull Flag",
      confidence: 0.85,
      timeframe: "1D",
      entryPrice: 186.50,
      stopLoss: 182.75,
      targetPrice: 195.00,
      timestamp: "2025-04-26T16:00:00Z",
      source: "Mock Data"
    },
    {
      id: "setup-2",
      symbol: "MSFT",
      setup: "Cup and Handle",
      confidence: 0.78,
      timeframe: "4H",
      entryPrice: 418.25,
      stopLoss: 412.50,
      targetPrice: 430.00,
      timestamp: "2025-04-26T16:00:00Z",
      source: "Mock Data"
    }
  ]
};

// Global connection status tracking
let _connectionStatus = 'unknown'; // 'connected', 'disconnected', 'partial', 'unknown'
let _lastConnectionAttempt = null;
let _connectionAttempts = 0;

// Helper function to handle API requests with fallback to mock data
const apiRequest = async (endpoint, method = 'GET', data = null, retries = 1) => {
  // Remove leading slash if present to prevent double slashes
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
  
  // If using mock data by default, return mock data immediately
  if (USE_MOCK_DATA) {
    const mockKey = normalizedEndpoint.split('/').pop().replace(/[-]/g, '');
    if (mockData[mockKey]) {
      console.log(`[DualBot] Using mock data for: ${normalizedEndpoint}`);
      return mockData[mockKey];
    } else if (normalizedEndpoint.includes('market-data') || normalizedEndpoint.includes('signals')) {
      console.log(`[DualBot] Using market data mock for: ${normalizedEndpoint}`);
      return mockData.marketData;
    } else if (normalizedEndpoint.includes('status')) {
      console.log(`[DualBot] Using status mock for: ${normalizedEndpoint}`);
      return mockData.status;
    }
  }

  try {
    // Use the market data URL for market-data endpoints
    const baseUrl = normalizedEndpoint.includes('market-data') ? 
      MARKET_DATA_URL : 
      API_BASE_URL;
    
    // Attempt to make the real API call
    console.log(`[DualBot] Making API request to: ${baseUrl}/${normalizedEndpoint} (${method})`);
    const response = await axios({
      url: `${baseUrl}/${normalizedEndpoint}`,
      method,
      data,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });
    
    // Update connection status on successful response
    _connectionStatus = 'connected';
    _lastConnectionAttempt = new Date();
    _connectionAttempts = 0;
    
    return response.data;
  } catch (error) {
    console.error(`[DualBot] API request failed for ${normalizedEndpoint}:`, error);
    
    // Only retry critical endpoints and with fewer retries
    if (retries > 0 && (normalizedEndpoint.includes('signals') || normalizedEndpoint.includes('status'))) {
      console.log(`[DualBot] Retrying request to ${normalizedEndpoint}. Attempts remaining: ${retries}`);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Shorter wait
      return apiRequest(normalizedEndpoint, method, data, retries - 1);
    }
    
    // Update connection status on failure
    _connectionStatus = 'disconnected';
    _lastConnectionAttempt = new Date();
    _connectionAttempts++;
    
    // Always fall back to mock data if AUTO_FALLBACK is enabled
    if (AUTO_FALLBACK) {
      console.log(`[DualBot] AUTO_FALLBACK enabled. Using mock data for: ${normalizedEndpoint}`);
      
      // Handle various endpoint types
      if (normalizedEndpoint.includes('trading-history')) {
        return mockData.tradingHistory;
      }
      else if (normalizedEndpoint.includes('performance')) {
        return mockData.performance;
      }
      else if (normalizedEndpoint.includes('alerts')) {
        return mockData.alerts;
      }
      else if (normalizedEndpoint.includes('institutional-flow')) {
        return mockData.institutionalFlow;
      }
      else if (normalizedEndpoint.includes('trade-setups')) {
        return mockData.tradeSetups;
      }
      else if (normalizedEndpoint.includes('market-data') || normalizedEndpoint.includes('signals')) {
        console.log(`[DualBot] Falling back to market data mock for: ${normalizedEndpoint}`);
        return mockData.marketData;
      }
      else if (normalizedEndpoint.includes('status')) {
        console.log(`[DualBot] Falling back to status mock for: ${normalizedEndpoint}`);
        return mockData.status;
      }
      else if (normalizedEndpoint.includes('config')) {
        console.log(`[DualBot] Falling back to config mock for: ${normalizedEndpoint}`);
        return mockData.config;
      }
      else if (normalizedEndpoint.includes('options')) {
        console.log(`[DualBot] Falling back to options data mock for: ${normalizedEndpoint}`);
        return mockData.optionsData;
      }
      else if (normalizedEndpoint.includes('news')) {
        console.log(`[DualBot] Falling back to news mock for: ${normalizedEndpoint}`);
        return mockData.news;
      }
      else if (normalizedEndpoint.includes('scan')) {
        console.log(`[DualBot] Falling back to recommendation mock for: ${normalizedEndpoint}`);
        return mockData.recommendation;
      }
      else if (normalizedEndpoint.includes('risk')) {
        console.log(`[DualBot] Falling back to risk assessment mock for: ${normalizedEndpoint}`);
        return mockData.riskAssessment;
      }
      else {
        // Generic fallback for any other endpoint
        console.log(`[DualBot] No specific mock data for ${normalizedEndpoint}, using generic mock`);
        return { success: true, message: "Mock data response", timestamp: new Date().toISOString() };
      }
    }
    
    throw error;
  }
};

const dualBotService = {
  // Check connection status
  checkConnectionStatus: async () => {
    // Only check once every 10 seconds to avoid excessive calls
    const now = new Date();
    if (_lastConnectionAttempt && (now - _lastConnectionAttempt) < 10000) {
      console.log(`[DualBot] Using cached connection status: ${_connectionStatus}`);
      return {
        status: _connectionStatus,
        timestamp: _lastConnectionAttempt
      };
    }

    _lastConnectionAttempt = now;
    _connectionAttempts++;

    try {
      console.log('[DualBot] Checking API connection status...');
      // Try health endpoint first
      const healthResponse = await apiClient.get('/health', { timeout: 3000 });
      
      if (healthResponse.status === 200 && healthResponse.data?.status === 'healthy') {
        _connectionStatus = 'connected';
        _connectionAttempts = 0;
        console.log('[DualBot] API connection is healthy');
        
        // Try another endpoint to confirm full connectivity
        try {
          const statusResponse = await apiClient.get('/status', { timeout: 3000 });
          if (statusResponse.status === 200) {
            console.log('[DualBot] Confirmed access to status endpoint');
          }
        } catch (err) {
          console.warn('[DualBot] Health endpoint works but status endpoint failed');
          _connectionStatus = 'partial';
        }
      } else {
        console.warn('[DualBot] Health check returned unexpected response');
        _connectionStatus = 'partial';
      }
    } catch (error) {
      console.error('[DualBot] Connection check failed:', error.message);
      _connectionStatus = 'disconnected';
      
      // After 3 failed attempts, set to use mock data
      if (_connectionAttempts >= 3 && AUTO_FALLBACK) {
        console.log('[DualBot] Multiple connection failures, forcing mock data mode');
        Object.defineProperty(dualBotService, '_useMockData', {
          value: true,
          writable: true
        });
      }
    }
    
    return {
      status: _connectionStatus,
      timestamp: _lastConnectionAttempt,
      attempts: _connectionAttempts
    };
  },

  // Test CORS
  testCorsConnection: async () => {
    try {
      // Call the check connection method first
      const connectionStatus = await dualBotService.checkConnectionStatus();
      
      if (connectionStatus.status === 'disconnected') {
        console.log('[DualBot] Using mock data due to disconnected status');
        return {
          success: false,
          message: 'CORS connection test failed. API server is not accessible.',
          error: 'Connection refused'
        };
      }
      
      console.log('[DualBot] Testing CORS connection...');
      // Use our specially designed CORS test endpoint
      const response = await apiRequest('test-frontend-cors');
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
      // Try dual-bot/status endpoint first
      try {
        const response = await apiRequest('dual-bot/status');
      if (response && response.success && response.status) {
        return response.status;
      } else if (response && response.status === true) {
        // Direct status object response
        return response;
        }
      } catch (dualBotError) {
        console.log('[DualBot] Dual bot status endpoint failed, trying regular status endpoint');
      }
      
      // Try the regular status endpoint as fallback
      try {
        const directStatus = await apiRequest('status');
        if (directStatus) {
          return directStatus;
        }
      } catch (directError) {
        console.error('[DualBot] Both status endpoints failed');
        if (!AUTO_FALLBACK) {
          throw new Error('Failed to get bot status from any endpoint');
        }
      }
      
      // If all else fails and AUTO_FALLBACK is enabled, use mock data
      if (AUTO_FALLBACK) {
      console.log('[DualBot] Using mock status data');
      return mockData.status;
      }
      
      throw new Error('Failed to get bot status and AUTO_FALLBACK is disabled');
    } catch (error) {
      console.error('[DualBot] Error getting bot status:', error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return mockData.status;
      }
      throw error;
    }
  },
  
  // Market data
  getMarketData: async (symbol) => {
    try {
      // Get direct market data for the symbol
      try {
        const marketData = await apiRequest(`market-data/${symbol}`);
        if (marketData && marketData.symbol) {
          return marketData;
        }
      } catch (marketError) {
        console.error(`[DualBot] Error getting market data for ${symbol}:`, marketError);
        
      // Fallback to signals endpoint if market-data is not available
        try {
          const response = await apiRequest(`dual-bot/signals`);
      // Extract signal data and transform it to match expected market data format
      if (response && response.success && response.signals) {
        // Look for a signal matching the requested symbol or use the first one
        const signal = response.signals.find(s => s.symbol === symbol) || response.signals[0];
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
        } catch (signalError) {
          console.error(`[DualBot] Signals endpoint failed as fallback:`, signalError);
          if (!AUTO_FALLBACK) {
            throw new Error(`Failed to get market data for ${symbol} from any endpoint`);
          }
        }
      }
      
      // If all else fails and AUTO_FALLBACK is enabled, use mock data
      if (AUTO_FALLBACK) {
      console.log(`[DualBot] Using mock data for ${symbol}`);
        return { ...mockData.marketData, symbol }; // Return mock data with the requested symbol
      }
      
      throw new Error(`Failed to get market data for ${symbol} and AUTO_FALLBACK is disabled`);
    } catch (error) {
      console.error(`[DualBot] Error getting market data for ${symbol}:`, error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return { ...mockData.marketData, symbol };
      }
      throw error;
    }
  },
  
  // Options data
  getOptionsData: async (symbol) => {
    try {
      return await apiRequest(`options-data/${symbol}`);
    } catch (error) {
      console.error(`[DualBot] Error getting options data for ${symbol}:`, error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return { ...mockData.optionsData, symbol };
      }
      throw error;
    }
  },
  
  // News
  getNews: async (symbol) => {
    try {
      return await apiRequest(`news/${symbol}`);
    } catch (error) {
      console.error(`[DualBot] Error getting news for ${symbol}:`, error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return mockData.news;
      }
      throw error;
    }
  },
  
  // Get TradingView alerts
  getTradingViewAlerts: async () => {
    try {
      return await apiRequest('tradingview/alerts');
    } catch (error) {
      console.error('[DualBot] Error getting TradingView alerts:', error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return mockData.alerts || []; // Ensure we return an array even if mockData.alerts is undefined
      }
      throw error;
    }
  },
  
  // Get trading history
  getTradingHistory: async () => {
    try {
      return await apiRequest('bot/trading-history', 'GET');
    } catch (error) {
      console.error('[DualBot] Error getting trading history:', error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return mockData.tradingHistory || [];
      }
      throw error;
    }
  },
  
  // Get performance data
  getPerformanceData: async () => {
    try {
      return await apiRequest('bot/performance', 'GET');
    } catch (error) {
      console.error('[DualBot] Error getting performance data:', error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return mockData.performance;
      }
      throw error;
    }
  },
  
  // Get institutional flow data
  getInstitutionalFlow: async () => {
    try {
      return await apiRequest('institutional-flow');
    } catch (error) {
      console.error('[DualBot] Error getting institutional flow data:', error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return mockData.institutionalFlow;
      }
      throw error;
    }
  },
  
  // Get trade setups
  getTradeSetups: async () => {
    try {
      return await apiRequest('trade-setups');
    } catch (error) {
      console.error('[DualBot] Error getting trade setups:', error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return mockData.tradeSetups;
      }
      throw error;
    }
  },
  
  // Scan for trades
  scanForTrades: async (symbol) => {
    try {
      const response = await apiRequest('dual-bot/signals');
      // Extract signal data and transform it to match expected recommendation format
      if (response && response.success && response.signals) {
        // Look for a signal matching the requested symbol or use the first one
        const signal = response.signals.find(s => s.symbol === symbol) || response.signals[0];
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
      
      // If we can't extract signal data or the specific requested symbol isn't found,
      // try the direct scan endpoint
      try {
        const scanResponse = await apiRequest('scan', 'POST', { 
          symbol, 
          strategy: 'options' 
        });
        if (scanResponse && scanResponse.symbol) {
          return scanResponse;
        }
      } catch (scanError) {
        console.error(`[DualBot] Scan endpoint failed:`, scanError);
        if (!AUTO_FALLBACK) {
          throw new Error(`Failed to scan trades for ${symbol} from any endpoint`);
        }
      }
      
      // If all else fails and AUTO_FALLBACK is enabled, use mock data
      if (AUTO_FALLBACK) {
      console.log(`[DualBot] Using mock recommendation data for ${symbol}`);
        return { ...mockData.recommendation, symbol };
      }
      
      throw new Error(`Failed to scan trades for ${symbol} and AUTO_FALLBACK is disabled`);
    } catch (error) {
      console.error(`[DualBot] Error scanning for trades for ${symbol}:`, error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return { ...mockData.recommendation, symbol };
      }
      throw error;
    }
  },
  
  // Risk assessment
  assessRisk: async (recommendation, marketContext) => {
    try {
      // Try to use the assess-risk endpoint
      try {
        const response = await apiRequest('assess-risk', 'POST', { 
          recommendation, 
          market_context: marketContext 
        });
        return response;
      } catch (assessError) {
        console.error('[DualBot] Assess risk endpoint failed:', assessError);
        if (!AUTO_FALLBACK) {
          throw new Error('Failed to assess risk');
        }
      }
      
      // If endpoint fails and AUTO_FALLBACK is enabled, use mock data
      if (AUTO_FALLBACK) {
        console.log('[DualBot] Using mock data for risk assessment');
      
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
      }
      
      throw new Error('Failed to assess risk and AUTO_FALLBACK is disabled');
    } catch (error) {
      console.error('[DualBot] Error assessing risk:', error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return mockData.riskAssessment;
      }
      throw error;
    }
  },
  
  // Check if position should be closed
  checkPosition: async (position, marketData) => {
    try {
      return await apiRequest('check-position', 'POST', { 
        position, 
        market_data: marketData 
      });
    } catch (error) {
      console.error('[DualBot] Error checking position:', error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
        return { should_close: false, reason: 'Mock data: position still valid' };
      }
      throw error;
    }
  },
  
  // Get config
  getConfig: async () => {
    try {
      return await apiRequest('config');
    } catch (error) {
      console.error('[DualBot] Error getting config:', error);
      if (USE_MOCK_DATA || AUTO_FALLBACK) {
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
  },
  
  // Check if using mock data
  isUsingMockData: () => {
    return USE_MOCK_DATA || dualBotService._useMockData || false;
  },
  
  // Get connection status
  getConnectionStatus: () => {
    return {
      status: _connectionStatus,
      lastChecked: _lastConnectionAttempt,
      attempts: _connectionAttempts
    };
  }
};

export default dualBotService; 
