const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  console.log('Setting up proxy middleware...');
  
  // Function to check if the backend server is running
  const checkBackendStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/test');
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
      console.error('1. Run the start-servers.bat file');
      console.error('2. Open a command prompt and run: cd api && python app.py');
      console.error('');
      console.error('Mock data will be used where possible.');
      console.error('');
    }
  });
  
  // Function to handle proxy errors
  const handleProxyError = (err, req, res) => {
    console.error('Proxy Error:', err);
    console.error('Failed request:', req.method, req.path);
    
    res.writeHead(500, {
      'Content-Type': 'application/json',
    });
    
    const json = {
      error: 'Proxy Error',
      message: err.message || 'Failed to connect to backend server',
      details: 'The backend server might be down or unreachable. Make sure your Flask server is running on port 5000.',
      path: req.path,
      method: req.method,
      mock: true
    };
    
    // For certain endpoints, provide mock data
    if (req.path.includes('/api/market-data/sources')) {
      json.success = true;
      json.sources = ['alpaca', 'interactive_brokers', 'tradingview', 'unusual_whales'];
      json.active_source = 'alpaca';
    } else if (req.path.includes('/api/market-data/config')) {
      json.success = true;
      json.config = {
        active_source: 'alpaca',
        alpaca: { api_key: '***', api_secret: '***', paper_trading: true },
        interactive_brokers: { host: 'localhost', port: 7497, client_id: 1 },
        tradingview: { webhook_port: 5001 },
        unusual_whales: { api_key: '***' }
      };
    } else if (req.path.includes('/api/execution-model/analyze/flow')) {
      json.success = true;
      json.flow_analysis = {};
      json.timestamp = new Date().toISOString();
    } else if (req.path.includes('/api/execution-model/analyze/market')) {
      json.success = true;
      json.analysis = {};
      json.timestamp = new Date().toISOString();
    }
    
    res.end(JSON.stringify(json, null, 2));
  };
  
  // Create proxy middleware with enhanced configuration
  const apiProxy = createProxyMiddleware({
    target: 'http://localhost:5000',
    changeOrigin: true,
    logLevel: 'warn',
    pathRewrite: { '^/api': '/api' },
    onProxyReq: (proxyReq, req, res) => {
      console.log(`Proxying ${req.method} request to: ${req.path}`);
      
      if (req.body) {
        const bodyData = JSON.stringify(req.body);
        proxyReq.setHeader('Content-Type', 'application/json');
        proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
        proxyReq.write(bodyData);
      }
    },
    onProxyRes: (proxyRes, req, res) => {
      console.log(`Received response for: ${req.path}, status: ${proxyRes.statusCode}`);
    },
    onError: handleProxyError
  });
  
  // Apply the proxy middleware
  app.use('/api', apiProxy);
  
  console.log('Proxy middleware configured successfully');
}; 