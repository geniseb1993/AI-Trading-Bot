import axios from 'axios';

// Constants
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001/api';
const CACHE_TIME = 5 * 60 * 1000; // 5 minutes in milliseconds

// Cache for API responses
const apiCache = new Map();

// Default headers
const defaultHeaders = {
  'Content-Type': 'application/json'
};

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: defaultHeaders,
  timeout: 10000 // 10 seconds timeout (reduced from 30 seconds)
});

// Separate instance for institutional flow with longer timeout
const institutionalFlowApi = axios.create({
  baseURL: API_BASE_URL,
  headers: defaultHeaders,
  timeout: 15000 // FIXED: Increased from 8000ms to 15000ms (15 seconds) to prevent timeouts
});

// Request interceptor to fix port 5000 issue
api.interceptors.request.use(
  config => {
    // Check if the URL contains port 5000 and replace it with 5001
    if (config.url && (config.url.includes(':5000/') || config.url.includes('localhost:5000'))) {
      console.log('Intercepted request to port 5000, redirecting to port 5001');
      
      // Fix the URL by replacing port 5000 with 5001
      if (config.url.includes(':5000/')) {
        config.url = config.url.replace(':5000/', ':5001/');
      } else {
        config.url = config.url.replace('localhost:5000', 'localhost:5001');
      }
      
      // Also fix baseURL if needed
      if (config.baseURL && config.baseURL.includes(':5000/')) {
        config.baseURL = config.baseURL.replace(':5000/', ':5001/');
      }
      
      console.log('Redirected to:', config.url);
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Apply the same interceptor to the institutional flow API instance
institutionalFlowApi.interceptors.request.use(api.interceptors.request.handlers[0].fulfilled);

// Response interceptor for handling common errors
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Special response interceptor for institutional flow API with fallback data
institutionalFlowApi.interceptors.response.use(
  response => response,
  error => {
    // Log the error
    console.error('API Error (institutionalFlow):', error);
    
    // For timeout errors, provide mock data as fallback
    if (error.code === 'ECONNABORTED' || (error.response && error.response.status === 504)) {
      console.log('Timeout occurred - using mock data fallback for institutional flow');
      
      // Extract information about the original request
      const originalRequest = error.config;
      const url = originalRequest.url;
      
      // Generate mock response based on the endpoint
      if (url.includes('/institutional-flow/get-data')) {
        // Parse the original request data
        let requestData = {};
        try {
          requestData = JSON.parse(originalRequest.data || '{}');
        } catch (e) {
          console.error('Error parsing original request data:', e);
        }
        
        // Generate appropriate mock response based on flow type
        const flowType = requestData.type || 'options-flow';
        
        return Promise.resolve({
          data: {
            success: true,
            timestamp: new Date().toISOString(),
            type: flowType,
            isRealData: false,
            source: 'mock (fallback)',
            data: generateMockFlowData(flowType, 10) // Generate 10 mock items
          }
        });
      }
    }
    
    return Promise.reject(error);
  }
);

// Helper function to generate mock flow data on client side as fallback
function generateMockFlowData(type, count = 10) {
  const result = [];
  const symbols = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'GOOGL', 'META', 'AMD'];
  
  for (let i = 0; i < count; i++) {
    if (type === 'options-flow' || type === 'options') {
      result.push({
        symbol: symbols[Math.floor(Math.random() * symbols.length)],
        type: Math.random() > 0.5 ? 'CALL' : 'PUT',
        volume: Math.floor(Math.random() * 500) * 10,
        premium: Math.floor(Math.random() * 100000),
        strike: Math.floor(Math.random() * 500),
        expiration: '2025-05-30',
        sweep: Math.random() > 0.7,
        block: Math.random() > 0.6,
        timestamp: new Date().toISOString()
      });
    } else if (type === 'dark-pool') {
      result.push({
        symbol: symbols[Math.floor(Math.random() * symbols.length)],
        side: Math.random() > 0.5 ? 'BUY' : 'SELL',
        volume: Math.floor(Math.random() * 50000),
        price: Math.floor(Math.random() * 500),
        value: Math.floor(Math.random() * 10000000),
        timestamp: new Date().toISOString(),
        off_hours: Math.random() > 0.7,
        exchange: ['NYSE', 'NASDAQ', 'IEX', 'CBOE'][Math.floor(Math.random() * 4)]
      });
    } else if (type === '13f') {
      result.push({
        institution: ['BlackRock', 'Vanguard', 'Fidelity', 'JPMorgan'][Math.floor(Math.random() * 4)],
        symbol: symbols[Math.floor(Math.random() * symbols.length)],
        shares: Math.floor(Math.random() * 1000000),
        value: Math.floor(Math.random() * 100000000),
        change: Math.floor(Math.random() * 100000) - 50000,
        filing_date: '2025-04-15'
      });
    } else if (type === 'insider') {
      result.push({
        name: ['John Smith', 'Jane Johnson', 'Robert Williams'][Math.floor(Math.random() * 3)],
        title: ['CEO', 'CFO', 'Director'][Math.floor(Math.random() * 3)],
        company: symbols[Math.floor(Math.random() * symbols.length)],
        symbol: symbols[Math.floor(Math.random() * symbols.length)],
        transaction_type: Math.random() > 0.4 ? 'BUY' : 'SELL',
        shares: Math.floor(Math.random() * 50000),
        price: Math.floor(Math.random() * 500),
        value: Math.floor(Math.random() * 10000000),
        trade_date: '2025-04-15'
      });
    }
  }
  
  return result;
}

// Also patch global axios to handle direct axios calls
axios.interceptors.request.use(
  config => {
    // Check if the URL contains port 5000 and replace it with 5001
    if (config.url && (config.url.includes(':5000/') || config.url.includes('localhost:5000'))) {
      console.log('Global interceptor: Redirecting request from port 5000 to 5001');
      
      // Fix the URL by replacing port 5000 with 5001
      if (config.url.includes(':5000/')) {
        config.url = config.url.replace(':5000/', ':5001/');
      } else {
        config.url = config.url.replace('localhost:5000', 'localhost:5001');
      }
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Helper to determine if cached data is still valid
const isCacheValid = (cacheKey) => {
  if (!apiCache.has(cacheKey)) return false;
  
  const { timestamp } = apiCache.get(cacheKey);
  const now = Date.now();
  
  return now - timestamp < CACHE_TIME;
};

// Generic fetch function with caching
const fetchData = async (endpoint, options = {}) => {
  const { 
    method = 'GET', 
    params = {}, 
    data = null, 
    useCache = true,
    cacheKey = `${method}:${endpoint}:${JSON.stringify(params)}`,
    domain = null,
    useInstitutionalFlowApi = endpoint.includes('institutional-flow'),
    fallbackEnabled = true // ADDED: option to enable/disable fallback 
  } = options;
  
  // IMPROVED: Check cache first if using cache and it's a GET request
  if (useCache && method === 'GET' && isCacheValid(cacheKey)) {
    console.log(`Using cached data for ${endpoint}`);
    const { data } = apiCache.get(cacheKey);
    return data;
  }
  
  try {
    // Use appropriate API instance based on endpoint
    const apiInstance = useInstitutionalFlowApi ? institutionalFlowApi : api;
    
    const response = await apiInstance({
      method,
      url: endpoint,
      params: method === 'GET' ? params : undefined,
      data: method !== 'GET' ? data : undefined
    });
    
    // IMPROVED: Cache successful responses (both GET and POST for institutional flow)
    if (useCache && (method === 'GET' || (useInstitutionalFlowApi && method === 'POST'))) {
      apiCache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now()
      });
      console.log(`Cached response for ${endpoint}`);
    }
    
    return response.data;
  } catch (error) {
    console.error(`API Error (${domain ? domain + ': ' : ''}${endpoint}):`, error);
    
    // IMPROVED: Enhanced fallback mechanism
    if (fallbackEnabled && useInstitutionalFlowApi && 
        (error.code === 'ECONNABORTED' || 
         (error.response && (error.response.status === 504 || error.response.status === 502)))) {
      console.log(`Timeout occurred - using fallback for ${endpoint}`);
      
      // Check if we have a cached version first (even if expired)
      if (apiCache.has(cacheKey)) {
        console.log(`Using expired cache as fallback for ${endpoint}`);
        const { data } = apiCache.get(cacheKey);
        return data;
      }
      
      // Otherwise generate mock data
      if (endpoint.includes('/get-data') && method === 'POST') {
        let requestData = {};
        try {
          requestData = typeof data === 'string' ? JSON.parse(data) : data || {};
        } catch (e) {
          console.error('Error parsing request data:', e);
        }
        
        const flowType = requestData.type || 'options-flow';
        
        const mockResponse = {
          success: true,
          timestamp: new Date().toISOString(),
          type: flowType,
          isRealData: false,
          source: 'mock (client fallback)',
          data: generateMockFlowData(flowType, 10)
        };
        
        // Cache the fallback data too
        apiCache.set(cacheKey, {
          data: mockResponse,
          timestamp: Date.now() - (CACHE_TIME / 2) // Set to half-expired
        });
        
        return mockResponse;
      }
    }
    
    throw error;
  }
};

// Clear specific cache or all cache
const clearCache = (cacheKey = null) => {
  if (cacheKey) {
    apiCache.delete(cacheKey);
  } else {
    apiCache.clear();
  }
};

// Domain-specific API services
const institutionalFlowService = {
  getFlowData: (params = {}) => 
    fetchData('/institutional-flow', { 
      params, 
      domain: 'institutionalFlow',
      cacheKey: `GET:/institutional-flow:${JSON.stringify(params)}`
    }),
    
  getEnhancedAnalysis: (data) => 
    fetchData('/institutional-flow/enhanced-analysis', { 
      method: 'POST', 
      data,
      useCache: true, // CHANGED: Enable caching for this endpoint
      domain: 'institutionalFlow',
      cacheKey: `POST:/institutional-flow/enhanced-analysis:${JSON.stringify(data)}`
    }),
    
  getFilteredData: (data) => 
    fetchData('/institutional-flow/get-data', {
      method: 'POST',
      data,
      useCache: true, // CHANGED: Enable caching for this endpoint
      domain: 'institutionalFlow',
      cacheKey: `POST:/institutional-flow/get-data:${JSON.stringify(data)}`
    }),
    
  clearFlowCache: () => {
    const cacheKeys = Array.from(apiCache.keys())
      .filter(key => key.includes('/institutional-flow'));
    
    cacheKeys.forEach(key => {
      console.log(`Clearing cache for ${key}`);
      apiCache.delete(key);
    });
  }
};

const riskManagementService = {
  getSettings: () => 
    fetchData('/risk-management/settings', { 
      domain: 'riskManagement',
      cacheKey: 'GET:/risk-management/settings:{}'
    }),
    
  saveSettings: (settings) => 
    fetchData('/risk-management/settings', { 
      method: 'POST', 
      data: settings,
      useCache: false,
      domain: 'riskManagement'
    }),
    
  getAnalysis: () => 
    fetchData('/risk-management/analysis', { 
      domain: 'riskManagement',
      cacheKey: 'GET:/risk-management/analysis:{}'
    }),
    
  analyzeSymbol: (symbol, settings) => 
    fetchData('/risk-management/analyze-symbol', { 
      method: 'POST', 
      data: { symbol, settings },
      useCache: false,
      domain: 'riskManagement'
    }),
    
  clearRiskCache: () => {
    const cacheKeys = Array.from(apiCache.keys())
      .filter(key => key.includes('/risk-management'));
    
    cacheKeys.forEach(key => apiCache.delete(key));
  }
};

const marketDataService = {
  getMarketData: (params = {}) =>
    fetchData('/market-data', {
      params,
      domain: 'marketData',
      cacheKey: `GET:/market-data:${JSON.stringify(params)}`
    }),
    
  getSymbolData: (symbol, params = {}) =>
    fetchData(`/market-data/${symbol}`, {
      params,
      domain: 'marketData',
      cacheKey: `GET:/market-data/${symbol}:${JSON.stringify(params)}`
    }),
    
  getMarketOverview: () =>
    fetchData('/market-data/overview', {
      domain: 'marketData',
      cacheKey: 'GET:/market-data/overview:{}'
    }),
    
  clearMarketDataCache: () => {
    const cacheKeys = Array.from(apiCache.keys())
      .filter(key => key.includes('/market-data'));
    
    cacheKeys.forEach(key => apiCache.delete(key));
  }
};

const apiConfigurationService = {
  getApiConfigs: () =>
    fetchData('/configuration/get-api-configs', {
      domain: 'apiConfiguration',
      cacheKey: 'GET:/configuration/get-api-configs:{}'
    }),
    
  saveApiConfigs: (configs) =>
    fetchData('/configuration/save-api-configs', {
      method: 'POST',
      data: configs,
      useCache: false,
      domain: 'apiConfiguration'
    }),
    
  testApiConnection: (service) =>
    fetchData('/configuration/test-connection', {
      method: 'POST',
      data: { service },
      useCache: false,
      domain: 'apiConfiguration'
    }),
    
  clearApiConfigCache: () => {
    const cacheKeys = Array.from(apiCache.keys())
      .filter(key => key.includes('/configuration'));
    
    cacheKeys.forEach(key => apiCache.delete(key));
  }
};

// Export domain-specific services and utilities
export {
  institutionalFlowService,
  riskManagementService,
  marketDataService,
  apiConfigurationService,
  clearCache
};

// Export default api instance for direct use if needed
export default api; 