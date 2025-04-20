const { createProxyMiddleware } = require('http-proxy-middleware');
const fs = require('fs');
const path = require('path');

// Enable this to log all API requests
const ENABLE_DEBUG_LOGGING = true;

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
  
  // Special handling for signal-related endpoints
  app.use(
    '/api/get-saved-signals',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
      onProxyReq: (proxyReq, req, res) => {
        logApiRequest(req, res, '🔄 Signals API Request');
      },
      onProxyRes: (proxyRes, req, res) => {
        logApiRequest(req, res, `✅ Signals API Response (${proxyRes.statusCode})`);
        
        // Debug response headers
        if (ENABLE_DEBUG_LOGGING) {
          console.log('Response headers:', proxyRes.headers);
        }
      },
      onError: (err, req, res) => {
        console.error('Proxy error:', err);
        logApiRequest(req, res, `❌ Signals API Error: ${err.message}`);
        
        // Return a meaningful error response
        res.writeHead(500, {
          'Content-Type': 'application/json',
        });
        res.end(JSON.stringify({ 
          success: false, 
          error: 'Proxy error: Could not connect to the API server'
        }));
      }
    })
  );
  
  // Main API proxy
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
      onProxyReq: (proxyReq, req, res) => {
        logApiRequest(req, res, 'Proxying API Request');
      },
      onError: (err, req, res) => {
        console.error('Proxy error:', err);
        logApiRequest(req, res, `Error: ${err.message}`);
        
        // Return a meaningful error response
        res.writeHead(500, {
          'Content-Type': 'application/json',
        });
        res.end(JSON.stringify({ 
          success: false, 
          error: 'Could not connect to the API server'
        }));
      }
    })
  );
};

// Generate mock signal data for a symbol
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