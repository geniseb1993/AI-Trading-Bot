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
  timeout: 30000 // 30 seconds timeout
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

// Response interceptor for handling common errors
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

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
    domain = null
  } = options;
  
  // Check cache first if using cache and it's a GET request
  if (useCache && method === 'GET' && isCacheValid(cacheKey)) {
    const { data } = apiCache.get(cacheKey);
    return data;
  }
  
  try {
    const response = await api({
      method,
      url: endpoint,
      params: method === 'GET' ? params : undefined,
      data: method !== 'GET' ? data : undefined
    });
    
    // Cache successful GET responses
    if (useCache && method === 'GET') {
      apiCache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now()
      });
    }
    
    return response.data;
  } catch (error) {
    console.error(`API Error (${domain ? domain + ': ' : ''}${endpoint}):`, error);
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
      useCache: false,
      domain: 'institutionalFlow'
    }),
    
  getFilteredData: (data) => 
    fetchData('/institutional-flow/get-data', {
      method: 'POST',
      data,
      useCache: false,
      domain: 'institutionalFlow'
    }),
    
  clearFlowCache: () => {
    const cacheKeys = Array.from(apiCache.keys())
      .filter(key => key.includes('/institutional-flow'));
    
    cacheKeys.forEach(key => apiCache.delete(key));
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