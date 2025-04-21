const { createProxyMiddleware } = require('http-proxy-middleware');
const fs = require('fs');
const path = require('path');

// Enable this to log all API requests
const ENABLE_DEBUG_LOGGING = true;

// Configuration
const API_HOST = 'localhost';
const API_PORT = 5000;
const API_URL = `http://${API_HOST}:${API_PORT}`;

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
    logApiRequest(req, res, 'API Request');
    
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
        const logEntry = `[${new Date().toISOString()}] API Response\n  URL: ${req.url}\n  Status: ${res.statusCode}\n  Body: ${responseBody}\n\n`;
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

module.exports = function(app) {
  // Add request logger middleware
  app.use(requestLogger);
  
  // Health check middleware - verify API connection
  app.use('/api/health-check', (req, res) => {
    // Create a basic HTTP request to check if API is running
    const http = require('http');
    const apiReq = http.request({
      host: API_HOST,
      port: API_PORT,
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
          res.json({
            status: 'connected',
            api_status: response.status,
            api_url: API_URL
          });
        } catch (e) {
          res.status(500).json({
            status: 'error',
            message: 'Invalid response from API',
            error: e.message
          });
        }
      });
    });
    
    apiReq.on('error', (e) => {
      console.error('API Health Check Error:', e.message);
      res.status(503).json({
        status: 'disconnected',
        message: 'Cannot connect to API server',
        error: e.message,
        api_url: API_URL
      });
    });
    
    apiReq.on('timeout', () => {
      apiReq.abort();
      res.status(504).json({
        status: 'timeout',
        message: 'API server connection timeout',
        api_url: API_URL
      });
    });
    
    apiReq.end();
  });
  
  // Main API proxy configuration
  const proxyOptions = {
    target: API_URL,
    changeOrigin: true,
    pathRewrite: { '^/api': '/api' },
    secure: false,
    logLevel: 'debug',
    onProxyReq: (proxyReq, req, res) => {
      // Add any custom headers if needed
      proxyReq.setHeader('X-Forwarded-Proto', 'http');
      
      // Log the proxy request
      logApiRequest(req, res, '🔄 Proxying API Request');
    },
    onProxyRes: (proxyRes, req, res) => {
      // Log successful proxy response
      logApiRequest(req, res, `✅ API Response (${proxyRes.statusCode})`);
    },
    onError: (err, req, res) => {
      console.error('Proxy Error:', err);
      logApiRequest(req, res, `❌ API Error: ${err.message}`);
      
      // Send a more detailed error response
      res.writeHead(502, {
        'Content-Type': 'application/json',
      });
      
      let errorMessage = 'Could not connect to the API server';
      let errorDetail = err.message;
      
      // More specific error messages based on the error
      if (err.code === 'ECONNREFUSED') {
        errorMessage = 'API server is not running or refusing connections';
        errorDetail = `Connection refused to ${API_URL}. Please ensure the API server is running.`;
      } else if (err.code === 'ETIMEDOUT') {
        errorMessage = 'Connection to API server timed out';
      } else if (err.code === 'ENOTFOUND') {
        errorMessage = 'Could not resolve API server hostname';
      }
      
      res.end(JSON.stringify({ 
        success: false, 
        status: 'error',
        message: errorMessage,
        error: errorDetail,
        api_url: API_URL
      }));
    }
  };
  
  // Apply the proxy middleware to all /api routes
  app.use('/api', createProxyMiddleware(proxyOptions));
};

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