const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  console.log('Setting up proxy middleware...');
  
  // Function to check if the backend server is running
  const checkBackendStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/test', { 
        timeout: 5000,
        signal: AbortSignal.timeout(5000)
      });
      if (response.ok) {
        console.log('✅ Backend server is accessible');
        return true;
      } else {
        console.error('❌ Backend server responded with status:', response.status);
        return false;
      }
    } catch (error) {
      console.error('❌ Backend server is not accessible:', error.message);
      return false;
    }
  };
  
  // Try to check backend status
  checkBackendStatus().then(isRunning => {
    if (!isRunning) {
      console.error('');
      console.error('⚠️ BACKEND SERVER IS NOT RUNNING OR NOT ACCESSIBLE ⚠️');
      console.error('');
      console.error('Please start the Flask backend server using one of these methods:');
      console.error('1. Run the run-server.bat file (RECOMMENDED)');
      console.error('2. Run the start-all.bat file');
      console.error('3. Open a command prompt and run: python minimal_flask_server.py');
      console.error('');
      console.error('Fallback data will be used for all API requests.');
      console.error('');
    }
  });
  
  // Create a proxy for API requests
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
      secure: false,
      timeout: 5000,
      proxyTimeout: 5000,
      // For troubleshooting
      onProxyReq: (proxyReq, req, res) => {
        console.log(`Proxying request to: ${req.method} ${req.originalUrl}`);
      },
      onProxyRes: (proxyRes, req, res) => {
        console.log(`Proxy response: ${req.method} ${req.originalUrl}, status: ${proxyRes.statusCode}`);
      },
      onError: (err, req, res) => {
        console.error(`Proxy error: ${err.message}`);
        
        if (!res.headersSent) {
          res.writeHead(200, { 'Content-Type': 'application/json' });
          
          // Generate appropriate fallback data based on the endpoint
          let responseData = { 
            success: true, 
            message: 'Using fallback data - API server is unavailable'
          };
          
          // Handle market signals endpoint
          if (req.url.includes('/market/ai_signals/')) {
            const symbol = req.url.split('/').pop();
            responseData.data = generateMockSignalData(symbol);
          } 
          // Handle market data endpoint
          else if (req.url.includes('/market-data/')) {
            const symbol = req.url.split('/').pop().split('?')[0];
            responseData.data = {
              symbol: symbol,
              timestamp: new Date().toISOString(),
              bars: generateMockBars(symbol, 30)
            };
          }
          
          res.end(JSON.stringify(responseData));
        }
      }
    })
  );
  
  console.log('Proxy middleware configured successfully');
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