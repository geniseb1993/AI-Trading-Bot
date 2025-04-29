const { createProxyMiddleware } = require('http-proxy-middleware');
const fs = require('fs');
const path = require('path');

// Enable this to log all API requests
const ENABLE_DEBUG_LOGGING = true;

// Configuration
const MAIN_API_HOST = 'localhost';
const MAIN_API_PORT = 5001; // Main API server port
const MAIN_API_URL = `http://${MAIN_API_HOST}:${MAIN_API_PORT}`;

// Bot Management API configuration
const BOT_MANAGEMENT_HOST = 'localhost';
const BOT_MANAGEMENT_PORT = 5002; // Bot Management server port
const BOT_MANAGEMENT_URL = `http://${BOT_MANAGEMENT_HOST}:${BOT_MANAGEMENT_PORT}`;

// Routes that should be routed to the bot management server
const botManagementRoutes = [
  '/api/bot/status',
  '/api/bot/start/',
  '/api/bot/stop/',
  '/api/status',
  '/api/dual-bot/status',
  '/api/ai-activity/logs',
  '/api/ai-activity/activity-types'
];

// Routes that should be explicitly routed to the main API server
const mainApiRoutes = [
  '/api/configuration/',
  '/api/configuration/get-api-configs',
  '/api/configuration/update-api-configs',
  '/api/configuration/test-connection',
  '/api/market-data/',
  '/api/tradingview/',
  '/api/options-data/',
  '/api/institutional-flow',
  '/api/institutional-flow/',
  '/api/13f-filings',
  '/api/insider-trading'
];

// Helper function to check if a path should be routed to the bot management server
const shouldRouteToBotManagement = (path) => {
  for (const route of botManagementRoutes) {
    if (path.startsWith(route)) {
      return true;
    }
  }
  return false;
};

// Helper function to check if a path should be explicitly routed to the main API server
const shouldRouteToMainApi = (path) => {
  for (const route of mainApiRoutes) {
    if (path.startsWith(route)) {
      return true;
    }
  }
  return false;
};

// Add headers middleware to handle CORS issues
const addHeaders = (req, res, next) => {
  // For API requests, ensure CORS headers are properly set
  if (req.path.startsWith('/api')) {
    res.setHeader('Access-Control-Allow-Origin', req.headers.origin || 'http://localhost:3001');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,X-Requested-With,X-API-Key');
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    
    // Handle preflight OPTIONS requests
    if (req.method === 'OPTIONS') {
      res.statusCode = 200;
      res.end();
      return;
    }
  }
  next();
};

// Log function that writes to file and console
const logApiRequest = (req, res, message) => {
  if (!ENABLE_DEBUG_LOGGING) return;
  
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${message}\n  URL: ${req.url}\n  Method: ${req.method}\n`;
  
  console.log(logEntry);
  
  try {
    const logDir = path.join(__dirname, '..', 'logs');
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
    
    fs.appendFileSync(path.join(logDir, 'api-requests.log'), logEntry);
  } catch (err) {
    console.error('Error writing to log file:', err);
  }
};

// API request logger middleware
const requestLogger = (req, res, next) => {
  if (req.path.startsWith('/api')) {
    const isBotManagementRoute = shouldRouteToBotManagement(req.path);
    const targetServer = isBotManagementRoute ? 'Bot Management Server' : 'Main API Server';
    
    logApiRequest(req, res, `API Request (Target: ${targetServer})`);
    
    // Capture the original end method
    const originalEnd = res.end;
    
    // Override end method to log response
    res.end = function (chunk, encoding) {
      // Get response data
      let responseBody = '';
      if (chunk) {
        responseBody = chunk.toString('utf8');
        if (responseBody && responseBody.length > 1000) {
          responseBody = responseBody.substring(0, 1000) + '... [truncated]';
        }
      }
      
      if (ENABLE_DEBUG_LOGGING) {
        const logEntry = `[${new Date().toISOString()}] API Response (${targetServer})\n  URL: ${req.url}\n  Status: ${res.statusCode}\n  Body: ${responseBody}\n\n`;
        console.log(logEntry);
        
        try {
          const logDir = path.join(__dirname, '..', 'logs');
          fs.appendFileSync(path.join(logDir, 'api-responses.log'), logEntry);
        } catch (err) {
          console.error('Error writing response to log file:', err);
        }
      }
      
      // Call the original end method
      return originalEnd.call(this, chunk, encoding);
    };
  }
  next();
};

// Create router middleware that routes requests to the appropriate API server
const createRouterMiddleware = () => {
  return (req, res, next) => {
    // Route bot management requests to the bot management server
    if (shouldRouteToBotManagement(req.url)) {
      console.log(`[Router] Routing to Bot Management Server: ${req.url}`);
      
      // Modify request to ensure it works with the bot management server
      req.headers.host = `${BOT_MANAGEMENT_HOST}:${BOT_MANAGEMENT_PORT}`;
      
      // Call the bot management proxy
      return botManagementProxy(req, res, next);
    }
    
    // Route main API requests explicitly to the main API server
    if (shouldRouteToMainApi(req.url)) {
      console.log(`[Router] Explicitly routing to Main API Server: ${req.url}`);
      req.headers.host = `${MAIN_API_HOST}:${MAIN_API_PORT}`;
      return mainApiProxy(req, res, next);
    }
    
    // Default to main API proxy for all other API requests
    console.log(`[Router] Default routing to Main API Server: ${req.url}`);
    req.headers.host = `${MAIN_API_HOST}:${MAIN_API_PORT}`;
    return mainApiProxy(req, res, next);
  };
};

module.exports = function(app) {
  // Add request logger middleware
  app.use(requestLogger);
  
  // Add CORS headers middleware
  app.use(addHeaders);
  
  // Health check middleware - verify both API connections
  app.use('/api/health-check', (req, res) => {
    // Check both API servers and return status
    checkApiHealth(MAIN_API_URL, 'main')
      .then(mainStatus => {
        return checkApiHealth(BOT_MANAGEMENT_URL, 'bot-management')
          .then(botStatus => {
            res.json({
              status: 'connected',
              main_api: mainStatus,
              bot_management_api: botStatus
            });
          });
      })
      .catch(error => {
        res.status(503).json({
          status: 'disconnected',
          message: 'Cannot connect to API servers',
          error: error.message
        });
      });
  });
  
  // Create proxy for main API
  const mainApiProxy = createProxyMiddleware({
    target: MAIN_API_URL,
    changeOrigin: true,
    pathRewrite: { '^/api': '/api' },
    secure: false,
    logLevel: 'debug',
    onProxyReq: (proxyReq, req, res) => {
      // Add any custom headers if needed
      proxyReq.setHeader('X-Forwarded-Proto', 'http');
      proxyReq.setHeader('Origin', 'http://localhost:3001');
      
      // Fix the path to remove duplicate /api if needed
      const originalPath = proxyReq.path;
      if (originalPath.startsWith('/api/api/')) {
        const fixedPath = originalPath.replace('/api/api/', '/api/');
        proxyReq.path = fixedPath;
        console.log(`[Proxy] Fixed path from ${originalPath} to ${fixedPath}`);
      }
      
      // Log the proxy request
      logApiRequest(req, res, `🔄 Proxying API Request to Main API: ${proxyReq.path}`);
    },
    onProxyRes: (proxyRes, req, res) => {
      // Add CORS headers to the response if they don't exist
      if (!proxyRes.headers['access-control-allow-origin']) {
        proxyRes.headers['access-control-allow-origin'] = req.headers.origin || 'http://localhost:3001';
      }
      if (!proxyRes.headers['access-control-allow-credentials']) {
        proxyRes.headers['access-control-allow-credentials'] = 'true';
      }
      
      // Log successful proxy response
      logApiRequest(req, res, `✅ Main API Response (${proxyRes.statusCode})`);
    },
    onError: (err, req, res) => {
      console.error('Main API Proxy Error:', err);
      logApiRequest(req, res, `❌ Main API Error: ${err.message}`);
      
      handleProxyError(err, req, res, MAIN_API_URL, 'Main API');
    }
  });
  
  // Create proxy for bot management API
  const botManagementProxy = createProxyMiddleware({
    target: BOT_MANAGEMENT_URL,
    changeOrigin: true,
    pathRewrite: { '^/api': '/api' },
    secure: false,
    logLevel: 'debug',
    onProxyReq: (proxyReq, req, res) => {
      // Add any custom headers if needed
      proxyReq.setHeader('X-Forwarded-Proto', 'http');
      proxyReq.setHeader('Origin', 'http://localhost:3001');
      
      // Fix the path to remove duplicate /api if needed
      const originalPath = proxyReq.path;
      if (originalPath.startsWith('/api/api/')) {
        const fixedPath = originalPath.replace('/api/api/', '/api/');
        proxyReq.path = fixedPath;
        console.log(`[Proxy] Fixed path from ${originalPath} to ${fixedPath}`);
      }
      
      // Log the proxy request
      logApiRequest(req, res, `🔄 Proxying API Request to Bot Management: ${proxyReq.path}`);
    },
    onProxyRes: (proxyRes, req, res) => {
      // Add CORS headers to the response if they don't exist
      if (!proxyRes.headers['access-control-allow-origin']) {
        proxyRes.headers['access-control-allow-origin'] = req.headers.origin || 'http://localhost:3001';
      }
      if (!proxyRes.headers['access-control-allow-credentials']) {
        proxyRes.headers['access-control-allow-credentials'] = 'true';
      }
      
      // Log successful proxy response
      logApiRequest(req, res, `✅ Bot Management API Response (${proxyRes.statusCode})`);
    },
    onError: (err, req, res) => {
      console.error('Bot Management API Proxy Error:', err);
      logApiRequest(req, res, `❌ Bot Management API Error: ${err.message}`);
      
      handleProxyError(err, req, res, BOT_MANAGEMENT_URL, 'Bot Management API');
    }
  });
  
  // Use the router middleware for all API routes
  const routerMiddleware = createRouterMiddleware();
  app.use('/api', routerMiddleware);
};

// Helper function to handle proxy errors
function handleProxyError(err, req, res, apiUrl, serverName) {
  // Send a more detailed error response
  res.writeHead(502, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': req.headers.origin || 'http://localhost:3001',
    'Access-Control-Allow-Credentials': 'true'
  });
  
  let errorMessage = `Could not connect to the ${serverName} server`;
  let errorDetail = err.message;
  
  // More specific error messages based on the error
  if (err.code === 'ECONNREFUSED') {
    errorMessage = `${serverName} server is not running or refusing connections`;
    errorDetail = `Connection refused to ${apiUrl}. Please ensure the ${serverName} server is running.`;
  } else if (err.code === 'ETIMEDOUT') {
    errorMessage = `Connection to ${serverName} server timed out`;
  } else if (err.code === 'ENOTFOUND') {
    errorMessage = `Could not resolve ${serverName} server hostname`;
  }
  
  res.end(JSON.stringify({ 
    success: false, 
    status: 'error',
    message: errorMessage,
    error: errorDetail,
    api_url: apiUrl
  }));
}

// Helper function to check API health
function checkApiHealth(apiUrl, serverType) {
  return new Promise((resolve, reject) => {
    const http = require('http');
    const urlParts = new URL(apiUrl);
    
    const apiReq = http.request({
      host: urlParts.hostname,
      port: urlParts.port,
      path: '/api/health',
      method: 'GET',
      timeout: 2000
    }, (apiRes) => {
      let data = '';
      apiRes.on('data', (chunk) => {
        data += chunk;
      });
      apiRes.on('end', () => {
        try {
          const response = JSON.parse(data);
          resolve({
            status: 'connected',
            api_status: response.status,
            api_url: apiUrl
          });
        } catch (e) {
          resolve({
            status: 'error',
            message: 'Invalid response from API',
            error: e.message,
            api_url: apiUrl
          });
        }
      });
    });
    
    apiReq.on('error', (e) => {
      console.error(`${serverType} API Health Check Error:`, e.message);
      resolve({
        status: 'disconnected',
        message: `Cannot connect to ${serverType} API server`,
        error: e.message,
        api_url: apiUrl
      });
    });
    
    apiReq.on('timeout', () => {
      apiReq.abort();
      resolve({
        status: 'timeout',
        message: `${serverType} API server connection timeout`,
        api_url: apiUrl
      });
    });
    
    apiReq.end();
  });
}

// Generate mock signal data for a symbol if needed for fallbacks
function generateMockSignalData(symbol) {
  return {
    symbol: symbol,
    timestamp: new Date().toISOString(),
    signals: [
      {
        type: 'bullish',
        timeframe: '1d',
        confidence: 0.85,
        description: `Fallback bullish signal for ${symbol}`,
        indicators: [
          {name: 'RSI', value: 32, threshold: 30, signal: 'oversold'},
          {name: 'MACD', value: -0.5, threshold: 0, signal: 'crossover soon'}
        ]
      }
    ],
    ai_analysis: `Fallback AI analysis for ${symbol}. The API server is currently unavailable.`,
    risk_level: 'medium',
    opportunity_score: 7.5
  };
}

// Generate mock bars for market data
function generateMockBars(symbol, days) {
  const bars = [];
  const today = new Date();
  
  // Base price for popular symbols
  const basePrice = {
    'SPY': 450, 'QQQ': 350, 'AAPL': 180, 'MSFT': 350, 'TSLA': 200, 'NVDA': 450
  }[symbol] || 100;
  
  let price = basePrice;
  
  for (let i = 0; i < days; i++) {
    const date = new Date(today);
    date.setDate(date.getDate() - (days - i));
    
    // Random price movement
    const change = (Math.random() - 0.48) * 5;
    const open = price;
    const close = open + change;
    const high = Math.max(open, close) + Math.random() * 2;
    const low = Math.min(open, close) - Math.random() * 2;
    
    bars.push({
      date: date.toISOString().split('T')[0],
      symbol: symbol,
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume: Math.floor(Math.random() * 10000000) + 1000000,
      change: parseFloat(((close - open) / open * 100).toFixed(2))
    });
    
    price = close;
  }
  
  return bars;
} 