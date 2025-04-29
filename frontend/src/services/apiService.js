import axios from 'axios';

// Set the API base URLs for all requests
const MAIN_API_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001/api';
const BOT_MANAGEMENT_API_URL = process.env.REACT_APP_BOT_MANAGEMENT_API_URL || 'http://localhost:5002/api';
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second
const USE_MOCK_DATA = false; // Set to false to use real data from API

// Routes that should be directed to the bot management server
const botManagementRoutes = [
  '/api/bot/status',
  '/api/bot/', // Base route for all bot operations
  '/api/status',
  '/api/dual-bot/status',
  '/api/ai-activity/logs',
  '/api/ai-activity/activity-types',
  '/api/bot/trading-history',
  '/api/bot/performance'
];

// Routes that should be explicitly directed to the main API server
const mainApiRoutes = [
  '/api/configuration/',
  '/api/market-data/',
  '/api/tradingview/',
  '/api/options-data/'
];

// Helper function to determine which API URL to use
const getApiUrlForEndpoint = (endpoint) => {
  // Remove leading slash if present for consistent comparison
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  // Add /api prefix if not already present
  const fullEndpoint = normalizedEndpoint.startsWith('/api/') ? normalizedEndpoint : `/api${normalizedEndpoint}`;

  // First check if this endpoint should explicitly go to the main API server
  for (const route of mainApiRoutes) {
    if (fullEndpoint.startsWith(route)) {
      console.log(`[API Router] Routing request to main API server: ${fullEndpoint}`);
      return MAIN_API_URL;
    }
  }

  // Then check if this endpoint should go to the bot management server
  for (const route of botManagementRoutes) {
    if (fullEndpoint.startsWith(route)) {
      console.log(`[API Router] Routing request to bot management server: ${fullEndpoint}`);
      return BOT_MANAGEMENT_API_URL;
    }
  }
  
  // Default to main API server
  console.log(`[API Router] Default routing to main API server: ${fullEndpoint}`);
  return MAIN_API_URL;
};

// Create an axios instance for each API server
const createApiClient = (baseURL) => {
  return axios.create({
    baseURL,
    timeout: 10000, // 10 seconds timeout
    headers: {
      'Content-Type': 'application/json'
    },
    // Add CORS handling to axios config
    withCredentials: false
  });
};

// Request interceptor to log all API requests
const addRequestInterceptor = (client) => {
  client.interceptors.request.use(
    (config) => {
      console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      console.error(`[API Request Error] ${error}`);
      return Promise.reject(error);
    }
  );
};

// Response interceptor to log all API responses
const addResponseInterceptor = (client) => {
  client.interceptors.response.use(
    (response) => {
      if (response.config.url && response.config.url.includes('health')) {
        // Don't log health check responses to reduce noise
        return response;
      }
      console.log(`[API Response] ${response.config.url}: Status ${response.status}`);
      return response;
    },
    (error) => {
      if (error.response) {
        console.error(`[API Error] ${error.response.status} ${error.config.url}: ${error.response.data.error || error.response.data.message || error.message}`);
      } else if (error.request) {
        console.error(`[API Error] No response received for ${error.config.url}`);
      } else {
        console.error(`[API Error] ${error.message}`);
      }
      return Promise.reject(error);
    }
  );
};

// Instantiate the main API client
const mainApiClient = createApiClient(MAIN_API_URL);
addRequestInterceptor(mainApiClient);
addResponseInterceptor(mainApiClient);

// Instantiate the bot management API client
const botManagementApiClient = createApiClient(BOT_MANAGEMENT_API_URL);
addRequestInterceptor(botManagementApiClient);
addResponseInterceptor(botManagementApiClient);

/**
 * Mock data for API responses
 * Used when USE_MOCK_DATA is true
 */
const mockData = {
  // Bot Status mock data
  botStatus: {
    autonomous_bot: {
      status: "inactive",
      last_active: "2023-10-15T14:30:00Z",
      trades_executed: 28,
      success_rate: 0.75,
      current_positions: 2,
      error_count: 0,
      uptime: "2d 4h 15m",
      next_scan: "2023-10-16T09:00:00Z",
      cpu_usage: 0.05,
      memory_usage: 128.5
    },
    rsi_bot: {
      status: "active",
      last_active: "2023-10-16T08:45:00Z",
      trades_executed: 42,
      success_rate: 0.82,
      current_positions: 3,
      error_count: 1,
      uptime: "5d 12h 30m",
      next_scan: "2023-10-16T09:15:00Z",
      cpu_usage: 0.08,
      memory_usage: 145.2
    },
    dual_bot: {
      status: "active",
      last_active: "2023-10-16T08:55:00Z",
      trades_executed: 36,
      success_rate: 0.88,
      current_positions: 4,
      error_count: 0,
      uptime: "3d 9h 45m",
      next_scan: "2023-10-16T09:25:00Z",
      cpu_usage: 0.12,
      memory_usage: 186.7
    }
  },
  
  // Trading History mock data
  tradingHistory: {
    success: true,
    data: [
      {
        id: "trade-001",
        symbol: "AAPL",
        entry_price: 182.45,
        exit_price: 189.32,
        entry_date: "2023-10-10T10:15:00Z",
        exit_date: "2023-10-12T14:30:00Z",
        profit_loss: 6.87,
        profit_loss_percent: 3.76,
        trade_type: "long",
        strategy: "momentum_breakout",
        status: "closed",
        risk_level: "medium",
        confidence_score: 0.85,
        notes: "Breakout above resistance with high volume"
      }
      // More trades would be here in a real implementation
    ]
  },
  
  // Performance data mock
  performance: {
    success: true,
    data: {
      total_trades: 106,
      winning_trades: 74,
      losing_trades: 32,
      win_rate: 0.698,
      average_profit: 3.2,
      average_loss: -1.8,
      profit_factor: 2.76,
      total_profit: 237.5,
      max_drawdown: -42.8,
      sharpe_ratio: 1.86,
      daily_performance: [
        { date: "2023-10-10", profit_loss: 12.4 },
        { date: "2023-10-11", profit_loss: -3.2 },
        { date: "2023-10-12", profit_loss: 8.7 },
        { date: "2023-10-13", profit_loss: 5.3 },
        { date: "2023-10-14", profit_loss: -1.8 },
        { date: "2023-10-15", profit_loss: 9.2 },
        { date: "2023-10-16", profit_loss: 4.5 }
      ]
    }
  },
  
  // CEO Dashboard mock data
  ceoDashboard: {
    success: true,
    data: {
      weekly_performance: 12.8,
      monthly_performance: 28.6,
      yearly_performance: 96.4,
      risk_status: {
        overall: "medium",
        autonomous_bot: "low",
        rsi_bot: "medium", 
        dual_bot: "medium"
      },
      top_performers: ["AAPL", "MSFT", "GOOGL"],
      worst_performers: ["META", "NFLX"],
      market_sentiment: "bullish",
      trading_volume: 128500,
      revenue_forecast: 1250000,
      ai_confidence: 0.86
    }
  },
  
  // CEO Settings mock data
  ceoSettings: {
    success: true,
    data: {
      risk_tolerance: "medium",
      max_trades_per_day: 15,
      max_allocation_per_trade: 0.05,
      allow_weekend_trading: false,
      trading_hours: {
        start: "09:30",
        end: "16:00"
      },
      preferred_sectors: ["Technology", "Healthcare", "Energy"],
      blacklisted_symbols: ["GME", "AMC"],
      notifications: {
        email: true,
        sms: false,
        trade_execution: true,
        daily_summary: true
      },
      api_keys: {
        trading_platform: "********",
        data_provider: "********"
      }
    }
  },
  
  // AI Activity Logs mock data
  aiActivityLogs: {
    success: true,
    data: [
      {
        id: "log-001",
        timestamp: "2023-10-16T08:15:32Z",
        activity_type: "market_analysis",
        description: "Completed daily market analysis with sentiment score of 0.76 (bullish)",
        model_used: "GPT-4-turbo",
        confidence: 0.88,
        execution_time: 3.2,
        tokens_used: 1845
      },
      {
        id: "log-002",
        timestamp: "2023-10-16T08:30:15Z",
        activity_type: "trade_recommendation",
        description: "Generated buy recommendation for AAPL with target price of $190.50",
        model_used: "DeepSeek-8B",
        confidence: 0.92,
        execution_time: 2.7,
        tokens_used: 1250
      },
      {
        id: "log-003",
        timestamp: "2023-10-16T08:45:22Z",
        activity_type: "risk_assessment",
        description: "Evaluated TSLA position with risk score of 0.65 (medium)",
        model_used: "GPT-4-turbo",
        confidence: 0.84,
        execution_time: 2.9,
        tokens_used: 1620
      }
    ]
  },
  
  // AI Activity Types mock data
  aiActivityTypes: {
    success: true,
    data: [
      {
        id: "act-001",
        name: "market_analysis",
        description: "Daily market sentiment and trend analysis",
        average_execution_time: 3.5,
        average_tokens: 1950
      },
      {
        id: "act-002",
        name: "trade_recommendation",
        description: "Generation of trade ideas with entry/exit points",
        average_execution_time: 2.8,
        average_tokens: 1350
      },
      {
        id: "act-003",
        name: "risk_assessment",
        description: "Evaluation of potential trades for risk factors",
        average_execution_time: 3.0,
        average_tokens: 1750
      },
      {
        id: "act-004",
        name: "portfolio_optimization",
        description: "Analysis of current positions and optimization recommendations",
        average_execution_time: 4.2,
        average_tokens: 2250
      }
    ]
  },
  
  // Dual Bot Recommendations mock data
  dualBotRecommendations: {
    success: true,
    data: [
      {
        id: "rec-001",
        symbol: "AAPL",
        direction: "long",
        confidence: 0.89,
        entry_price: 182.45,
        stop_loss: 178.30,
        take_profit: 191.80,
        timestamp: "2023-10-16T08:30:15Z",
        expiration: "2023-10-16T20:00:00Z",
        model: "DeepSeek-8B",
        reasoning: "Strong bullish momentum with recent product announcements and positive market sentiment. Technical indicators show support at $178.30 with resistance break above $180. Recent earnings exceeded expectations with strong guidance for next quarter.",
        metrics: {
          rsi: 58.4,
          macd: 2.15,
          volume_change: 0.28,
          price_to_earnings: 28.5
        },
        status: "pending_risk_assessment"
      },
      {
        id: "rec-002",
        symbol: "TSLA",
        direction: "short",
        confidence: 0.76,
        entry_price: 245.80,
        stop_loss: 252.60,
        take_profit: 228.40,
        timestamp: "2023-10-16T08:45:22Z",
        expiration: "2023-10-16T20:00:00Z",
        model: "DeepSeek-8B",
        reasoning: "Bearish divergence on daily chart with resistance at $250 level. Recent earnings missed estimates and production numbers show potential slowdown. Technical indicators suggest overbought conditions with volume decreasing on recent rallies.",
        metrics: {
          rsi: 72.8,
          macd: -1.32,
          volume_change: -0.15,
          price_to_earnings: 84.3
        },
        status: "pending_risk_assessment"
      }
    ]
  },
  
  // Dual Bot Risk Assessments mock data
  dualBotRiskAssessments: {
    success: true,
    data: [
      {
        id: "risk-001",
        recommendation_id: "rec-001",
        symbol: "AAPL",
        approved: true,
        confidence: 0.82,
        risk_level: "medium",
        timestamp: "2023-10-16T08:35:40Z",
        model: "GPT-4-turbo",
        reason: "Trade aligns with overall market sentiment and company fundamentals are strong. Stop loss is appropriate at 2.3% from entry, with potential reward-to-risk ratio of 2.8:1. Recent product announcements support bullish thesis, though broader market volatility adds some risk. Position sizing should be standard according to portfolio guidelines.",
        modifications: {
          original_stop_loss: 178.30,
          adjusted_stop_loss: 178.30,
          original_take_profit: 191.80,
          adjusted_take_profit: 191.80,
          position_size_recommendation: "standard"
        }
      },
      {
        id: "risk-002",
        recommendation_id: "rec-002",
        symbol: "TSLA",
        approved: false,
        confidence: 0.88,
        risk_level: "high",
        timestamp: "2023-10-16T08:50:12Z",
        model: "GPT-4-turbo",
        reason: "While technical indicators suggest a short position may be profitable, risk is elevated due to high stock volatility and upcoming product announcement scheduled tomorrow. Stock has shown erratic movement on news in the past with 15%+ single-day moves. The stop loss at 2.8% from entry is insufficient for TSLA's typical volatility profile. Additionally, short positions carry theoretically unlimited risk. Recommend reconsidering after product announcement or adjusting parameters for greater safety margin.",
        modifications: {
          original_stop_loss: 252.60,
          adjusted_stop_loss: 258.40,
          original_take_profit: 228.40,
          adjusted_take_profit: 228.40,
          position_size_recommendation: "reduce_by_50_percent"
        }
      }
    ]
  }
};

/**
 * Make an API request with retry logic and routing to the appropriate server
 * 
 * @param {Object} options - Request options
 * @param {string} options.url - API endpoint URL
 * @param {string} options.method - HTTP method (get, post, put, delete)
 * @param {Object} options.data - Request data for POST, PUT
 * @param {Object} options.params - Query parameters
 * @param {number} options.maxRetries - Max retry attempts (default: MAX_RETRIES)
 * @param {boolean} options.useCache - Whether to use cached response (default: false)
 * @returns {Promise} - API response
 */
export const apiRequest = async ({
  url,
  method = 'get',
  data = null,
  params = null,
  maxRetries = MAX_RETRIES,
  useCache = false
}) => {
  let retries = 0;
  let lastError = null;

  // Determine which API client to use
  const apiBaseUrl = getApiUrlForEndpoint(url);
  const apiClient = apiBaseUrl === BOT_MANAGEMENT_API_URL ? botManagementApiClient : mainApiClient;
  
  // Normalize the URL to remove any API base URL that might be included
  const normalizedUrl = url.replace(/^\/api\//, '/').replace(/^api\//, '/');

  // Simple in-memory cache for GET requests
  const cacheKey = useCache && method.toLowerCase() === 'get' ? `${normalizedUrl}:${JSON.stringify(params)}` : null;
  const cachedResponse = cacheKey ? sessionStorage.getItem(cacheKey) : null;
  
  if (cachedResponse) {
    try {
      const parsedResponse = JSON.parse(cachedResponse);
      const cacheTime = parsedResponse._cacheTime;
      const now = Date.now();
      
      // Use cache if less than 10 seconds old
      if (cacheTime && now - cacheTime < 10000) {
        console.log(`[API Cache] Using cached response for ${normalizedUrl}`);
        delete parsedResponse._cacheTime;
        return { data: parsedResponse, fromCache: true };
      }
    } catch (e) {
      console.warn('[API Cache] Error parsing cached response:', e);
    }
  }

  // If using mock data, check if we have a mock for this endpoint
  if (USE_MOCK_DATA) {
    // Special handling for bot action URLs to prevent API calls for these actions
    if (normalizedUrl.includes('/bot/start/') || normalizedUrl.includes('/bot/stop/') || normalizedUrl.includes('/bot/run-cycle/')) {
      // Extract bot type from URL
      let botType = '';
      if (normalizedUrl.includes('/bot/start/')) {
        botType = normalizedUrl.split('/bot/start/')[1];
      } else if (normalizedUrl.includes('/bot/stop/')) {
        botType = normalizedUrl.split('/bot/stop/')[1];
      } else if (normalizedUrl.includes('/bot/run-cycle/')) {
        botType = normalizedUrl.split('/bot/run-cycle/')[1];
      }
      
      console.log(`[API Mock] Special handling for bot action: ${normalizedUrl} (botType: ${botType})`);
      
      if (normalizedUrl.includes('/bot/start/')) {
        // Update mock data for start action
        const botKey = `${botType}_bot`;
        if (mockData.botStatus[botKey]) {
          mockData.botStatus[botKey].status = "active";
          console.log(`[API Mock] Updated mock data status for ${botKey} to "active"`);
        }
        
        return { 
          data: { 
            success: true, 
            message: `${botType} bot started (mock)`,
            status: "success"
          }, 
          fromMock: true 
        };
      } else if (normalizedUrl.includes('/bot/stop/')) {
        // Update mock data for stop action
        const botKey = `${botType}_bot`;
        if (mockData.botStatus[botKey]) {
          mockData.botStatus[botKey].status = "inactive";
          console.log(`[API Mock] Updated mock data status for ${botKey} to "inactive"`);
        }
        
        return { 
          data: { 
            success: true, 
            message: `${botType} bot stopped (mock)`,
            status: "success"
          }, 
          fromMock: true 
        };
      } else if (normalizedUrl.includes('/bot/run-cycle/')) {
        // Return mock data for run-cycle action (doesn't change status)
        return { 
          data: { 
            success: true, 
            message: `${botType} bot trading cycle executed (mock)`,
            status: "success"
          }, 
          fromMock: true 
        };
      }
    }
    
    const mockKey = getMockDataKey(normalizedUrl);
    if (mockKey) {
      console.log(`[API Mock] Using mock data for ${normalizedUrl}`);
      return { data: mockData[mockKey], fromMock: true };
    }
  }

  // Retry logic
  while (retries <= maxRetries) {
    try {
      const response = await apiClient({
        url: normalizedUrl,
        method,
        data,
        params
      });

      // Cache successful GET responses
      if (cacheKey && response.data) {
        try {
          const cacheData = { ...response.data, _cacheTime: Date.now() };
          sessionStorage.setItem(cacheKey, JSON.stringify(cacheData));
        } catch (e) {
          console.warn('[API Cache] Error caching response:', e);
        }
      }

      return response;
    } catch (error) {
      lastError = error;
      
      // Don't retry on 4xx client errors except 429 (too many requests)
      if (
        error.response && 
        error.response.status >= 400 && 
        error.response.status < 500 && 
        error.response.status !== 429
      ) {
        break;
      }
      
      retries++;
      
      if (retries <= maxRetries) {
        console.log(`[API Retry] Attempt ${retries}/${maxRetries} for ${normalizedUrl}`);
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * retries));
      }
    }
  }

  // If we reach this point, all retries failed
  // Check if we should use mock data as fallback
  if (USE_MOCK_DATA) {
    const mockKey = getMockDataKey(normalizedUrl);
    if (mockKey) {
      console.log(`[API Fallback] Using mock data for ${normalizedUrl} after failed API request`);
      return { data: mockData[mockKey], fromMock: true };
    }
  }

  if (lastError.response && lastError.response.status === 404) {
    console.error(`[API Error] Endpoint not found: ${normalizedUrl}`);
    throw new Error(`API endpoint not found: ${normalizedUrl}`);
  }
  
  if (lastError.code === 'ECONNABORTED') {
    console.error(`[API Error] Request timeout for ${normalizedUrl}`);
    throw new Error('Request timed out. Please check your connection and try again.');
  }
  
  if (lastError.code === 'ERR_NETWORK') {
    console.error(`[API Error] Network error for ${normalizedUrl}`);
    throw new Error('Network error. The API server may be unavailable.');
  }

  // Default error handling  
  const errorMessage = lastError.response?.data?.error || 
                      lastError.response?.data?.message || 
                      lastError.message || 
                      'Unknown API error';
                      
  throw new Error(errorMessage);
};

// Helper function to get the corresponding mock data key for a URL
function getMockDataKey(url) {
  if (url.includes('/bot/status')) {
    console.log('Returning mock botStatus data with current values:', {
      autonomous: mockData.botStatus.autonomous_bot.status,
      rsi: mockData.botStatus.rsi_bot.status,
      dual: mockData.botStatus.dual_bot.status
    });
    return 'botStatus';
  }
  if (url.includes('/bot/trading-history')) return 'tradingHistory';
  if (url.includes('/bot/performance')) return 'performance';
  if (url.includes('/ceo-dashboard')) return 'ceoDashboard';
  if (url.includes('/ceo-settings')) return 'ceoSettings';
  if (url.includes('/ai-activity/logs')) return 'aiActivityLogs';
  if (url.includes('/ai-activity/activity-types')) return 'aiActivityTypes';
  return null;
}

// Convenience methods for common API operations
export const apiService = {
  /**
   * Make a GET request to the API
   * @param {string} endpoint - API endpoint (without /api prefix)
   * @param {Object} params - Query parameters
   * @param {Object} options - Additional request options
   * @returns {Promise} - API response
   */
  get: (endpoint, params = {}, options = {}) => {
    return apiRequest({
      url: endpoint,
      method: 'get',
      params,
      ...options
    });
  },
  
  /**
   * Make a POST request to the API
   * @param {string} endpoint - API endpoint (without /api prefix)
   * @param {Object} data - Request body data
   * @param {Object} options - Additional request options
   * @returns {Promise} - API response
   */
  post: (endpoint, data = {}, options = {}) => {
    return apiRequest({
      url: endpoint,
      method: 'post',
      data,
      ...options
    });
  },
  
  /**
   * Check API server health
   * @returns {Promise} - Health check response
   */
  checkHealth: async () => {
    try {
      const response = await apiRequest({
        url: '/api/health',
        method: 'get',
        maxRetries: 1,
        useCache: false
      });
      return response.data;
    } catch (error) {
      console.error('[API Health Check] Error:', error.message);
      return {
        status: 'disconnected',
        message: error.message
      };
    }
  },
  
  /**
   * Get bot status from the API
   * @param {Object} options - Request options
   * @returns {Promise} - Bot status data
   */
  getBotStatus: async () => {
    let response = null;
    let error = null;
    
    // Try the dedicated bot status endpoint first
    try {
      response = await apiRequest({
        url: '/bot/status',
        method: 'get',
        maxRetries: 2
      });
      
      if (response && response.data) {
        console.log('[Bot Status] Successfully retrieved from /bot/status');
        return response;
      }
    } catch (e) {
      console.log('[Bot Status] Bot status endpoint failed, trying standard endpoint:', e.message);
      error = e;
    }
    
    // Try the standard status endpoint next
    try {
      response = await apiRequest({
        url: '/status',
        method: 'get',
        maxRetries: 2
      });
      
      if (response && response.data) {
        console.log('[Bot Status] Successfully retrieved from /status');
        return response;
      }
    } catch (e) {
      console.log('[Bot Status] Standard endpoint failed, trying dual-bot endpoint:', e.message);
      error = e;
    }
    
    // Try the dual-bot status endpoint as last resort
    try {
      response = await apiRequest({
        url: '/dual-bot/status',
        method: 'get',
        maxRetries: 2
      });
      
      if (response && response.data) {
        console.log('[Bot Status] Successfully retrieved from /dual-bot/status');
        return response;
      }
    } catch (e) {
      console.log('[Bot Status] All status endpoints failed. Using mock data as fallback.');
      error = e;
    }
    
    // All endpoints failed, use mock data as fallback
    if (mockData && mockData.botStatus) {
      console.log('[Bot Status] Using mock data as fallback');
      return {
        data: {
          success: true,
          autonomous_bot: mockData.botStatus.autonomous_bot,
          rsi_bot: mockData.botStatus.rsi_bot,
          dual_bot: mockData.botStatus.dual_bot
        }
      };
    }
    
    // If no mock data, throw the error
    throw error || new Error('Failed to retrieve bot status from all endpoints');
  },
  
  /**
   * Start a bot
   * @param {string} botType - Bot type (autonomous, rsi, dual)
   * @returns {Promise} - API response
   */
  startBot: (botType) => {
    try {
      console.log(`Attempting to start ${botType} bot...`);
      // Normalize botType to remove '-bot' if present
      const normalizedBotType = botType.replace('-bot', '');
      
      // If mock data is enabled, immediately return mock response without API call
      if (USE_MOCK_DATA) {
        console.log(`Using mock data for ${normalizedBotType} bot start. Setting status to "active" without API call.`);
        
        const botKey = `${normalizedBotType}_bot`;
        if (mockData.botStatus[botKey]) {
          mockData.botStatus[botKey].status = "active";
          console.log(`Updated mock data status for ${botKey} to "active"`, mockData.botStatus);
        } else {
          console.error(`Bot key ${botKey} not found in mock data`);
        }
        
        return Promise.resolve({ 
          data: { 
            success: true, 
            message: `${normalizedBotType} bot started (mock)`,
            status: "success"
          }, 
          fromMock: true 
        });
      }
      
      // Format bot ID to match server expectations - the server expects 'autonomous_bot', not just 'autonomous'
      const botId = `${normalizedBotType}_bot`;
      
      // Use the API endpoint format that exactly matches the server route: /api/bot/{botId}/start
      return apiRequest({
        url: `/api/bot/${botId}/start`,
        method: 'post'
      }).then(response => {
        console.log(`Bot start response:`, response.data);
        
        // Handle different response formats from the server
        if (response.data.success) {
          console.log(`Successfully started ${normalizedBotType} bot. Setting status to "active".`);
          return response;
        }
        
        return response;
      });
    } catch (error) {
      console.error(`[Start Bot] Error starting ${botType}:`, error.message);
      if (USE_MOCK_DATA) {
        console.log(`Using mock data for ${botType} bot start. Setting status to "active".`);
        
        // Normalize botType to remove '-bot' if present
        const normalizedBotType = botType.replace('-bot', '');
        const botKey = `${normalizedBotType}_bot`;
        
        if (mockData.botStatus[botKey]) {
          mockData.botStatus[botKey].status = "active";
          console.log(`Updated mock data status for ${botKey} to "active"`, mockData.botStatus);
        } else {
          console.error(`Bot key ${botKey} not found in mock data`);
        }
        
        return Promise.resolve({ 
          data: { 
            success: true, 
            message: `${normalizedBotType} bot started (mock)`,
            status: "success"
          }, 
          fromMock: true 
        });
      }
      throw error;
    }
  },
  
  /**
   * Stop a bot
   * @param {string} botType - Bot type (autonomous, rsi, dual)
   * @returns {Promise} - API response
   */
  stopBot: (botType) => {
    try {
      console.log(`Attempting to stop ${botType} bot...`);
      // Normalize botType to remove '-bot' if present
      const normalizedBotType = botType.replace('-bot', '');
      
      // If mock data is enabled, immediately return mock response without API call
      if (USE_MOCK_DATA) {
        console.log(`Using mock data for ${normalizedBotType} bot stop. Setting status to "inactive" without API call.`);
        
        const botKey = `${normalizedBotType}_bot`;
        if (mockData.botStatus[botKey]) {
          mockData.botStatus[botKey].status = "inactive";
          console.log(`Updated mock data status for ${botKey} to "inactive"`, mockData.botStatus);
        } else {
          console.error(`Bot key ${botKey} not found in mock data`);
        }
        
        return Promise.resolve({ 
          data: { 
            success: true, 
            message: `${normalizedBotType} bot stopped (mock)`,
            status: "success"
          }, 
          fromMock: true 
        });
      }
      
      // Format bot ID to match server expectations - the server expects 'autonomous_bot', not just 'autonomous'
      const botId = `${normalizedBotType}_bot`;
      
      // Use the API endpoint format that exactly matches the server route: /api/bot/{botId}/stop
      return apiRequest({
        url: `/api/bot/${botId}/stop`,
        method: 'post'
      }).then(response => {
        console.log(`Bot stop response:`, response.data);
        
        // Handle different response formats from the server
        if (response.data.success) {
          console.log(`Successfully stopped ${normalizedBotType} bot. Setting status to "inactive".`);
          return response;
        }
        
        return response;
      });
    } catch (error) {
      console.error(`[Stop Bot] Error stopping ${botType}:`, error.message);
      if (USE_MOCK_DATA) {
        console.log(`Using mock data for ${botType} bot stop. Setting status to "inactive".`);
        
        // Normalize botType to remove '-bot' if present
        const normalizedBotType = botType.replace('-bot', '');
        const botKey = `${normalizedBotType}_bot`;
        
        if (mockData.botStatus[botKey]) {
          mockData.botStatus[botKey].status = "inactive";
          console.log(`Updated mock data status for ${botKey} to "inactive"`, mockData.botStatus);
        } else {
          console.error(`Bot key ${botKey} not found in mock data`);
        }
        
        return Promise.resolve({ 
          data: { 
            success: true, 
            message: `${normalizedBotType} bot stopped (mock)`,
            status: "success"  
          }, 
          fromMock: true 
        });
      }
      throw error;
    }
  },
  
  /**
   * Run a trading cycle for a bot
   * @param {string} botType - Bot type (autonomous, rsi, dual)
   * @returns {Promise} - API response
   */
  runTradingCycle: (botType) => {
    try {
      console.log(`Attempting to run trading cycle for ${botType} bot...`);
      // Normalize botType to remove '-bot' if present
      const normalizedBotType = botType.replace('-bot', '');
      
      // If mock data is enabled, immediately return mock response without API call
      if (USE_MOCK_DATA) {
        console.log(`Using mock data for ${normalizedBotType} bot trading cycle without API call.`);
        
        // Running a trading cycle doesn't change the bot's status
        // But we could simulate some activity here if needed
        
        return Promise.resolve({ 
          data: { 
            success: true, 
            message: `${normalizedBotType} bot trading cycle executed (mock)`,
            status: "success"
          }, 
          fromMock: true 
        });
      }
      
    return apiRequest({
        url: `/api/bot/run-cycle/${normalizedBotType}`,
      method: 'post'
      }).then(response => {
        console.log(`Run trading cycle response:`, response.data);
        
        // Handle different response formats from the server
        if (response.data.success && response.data.status === "success") {
          console.log(`Successfully ran trading cycle for ${normalizedBotType} bot`);
          return response;
        }
        
        return response;
      });
    } catch (error) {
      console.error(`[Run Trading Cycle] Error for ${botType}:`, error.message);
      if (USE_MOCK_DATA) {
        console.log(`Using mock data for ${botType} bot trading cycle.`);
        
        // Normalize botType to remove '-bot' if present
        const normalizedBotType = botType.replace('-bot', '');
        
        return Promise.resolve({ 
          data: { 
            success: true, 
            message: `${normalizedBotType} bot trading cycle executed (mock)`,
            status: "success"
          }, 
          fromMock: true 
        });
      }
      throw error;
    }
  },
  
  /**
   * Get trading history from the API
   * @param {Object} options - Filter options
   * @returns {Promise} - Trading history data
   */
  getTradingHistory: async (options = {}) => {
    const { botId, strategy, tradeType, limit = 30, offset = 0 } = options;
    
    // Build query parameters
    const params = {};
    if (botId) params.bot_id = botId;
    if (strategy) params.strategy = strategy;
    if (tradeType) params.trade_type = tradeType;
    if (limit) params.limit = limit;
    if (offset) params.offset = offset;
    
    try {
      console.log('[Trading History] Fetching trading history...');
      const response = await apiRequest({
        url: '/bot/trading-history',
        method: 'get',
        params,
        maxRetries: 2
      });
      
      if (response && response.data) {
        console.log('[Trading History] Successfully retrieved trading history');
        return response;
      }
    } catch (error) {
      console.error('[Trading History] Error fetching trading history:', error.message);
      
      // Use mock data if real API fails
      if (USE_MOCK_DATA || error) {
        console.log('[Trading History] Using mock data as fallback');
        return {
          data: {
            success: true,
            trades: mockData.tradingHistory.data,
            total: mockData.tradingHistory.data.length
          }
        };
      }
      
      throw error;
    }
  },
  
  /**
   * Get performance data from the API
   * @param {Object} options - Filter options
   * @returns {Promise} - Performance data
   */
  getPerformanceData: async (options = {}) => {
    const { botId, days } = options;
    
    // Build query parameters
    const params = {};
    if (botId) params.bot_id = botId;
    if (days) params.time_range = `${days}d`;
    
    try {
      console.log('[Performance] Fetching performance data...');
      const response = await apiRequest({
        url: '/bot/performance',
        method: 'get',
        params,
        maxRetries: 2
      });
      
      if (response && response.data) {
        console.log('[Performance] Successfully retrieved performance data');
        return response;
      }
    } catch (error) {
      console.error('[Performance] Error fetching performance data:', error.message);
      
      // Use mock data if real API fails
      if (USE_MOCK_DATA || error) {
        console.log('[Performance] Using mock data as fallback');
        return {
          data: {
            success: true,
            data: mockData.performance.data
          }
        };
      }
      
      throw error;
    }
  },
  
  /**
   * Get dual bot recommendations
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Promise with the recommendations data
   */
  getDualBotRecommendations: async (options = {}) => {
    try {
      console.log('[API] Getting dual bot recommendations');
      return await apiRequest(`${API_BASE_URL}/api/dual-bot/recommendations`, {
        method: 'GET',
        ...options
      });
    } catch (error) {
      console.error('[API] Error getting dual bot recommendations:', error);
      if (USE_MOCK_DATA) {
        console.log('[API] Using mock data for dual bot recommendations');
        return mockData.dualBotRecommendations;
      }
      throw error;
    }
  },
  
  /**
   * Get dual bot risk assessments
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Promise with the risk assessments data
   */
  getDualBotRiskAssessments: async (options = {}) => {
    try {
      console.log('[API] Getting dual bot risk assessments');
      return await apiRequest(`${API_BASE_URL}/api/dual-bot/risk-assessments`, {
        method: 'GET',
        ...options
      });
    } catch (error) {
      console.error('[API] Error getting dual bot risk assessments:', error);
      if (USE_MOCK_DATA) {
        console.log('[API] Using mock data for dual bot risk assessments');
        return mockData.dualBotRiskAssessments;
      }
      throw error;
    }
  }
};

export default apiService; 