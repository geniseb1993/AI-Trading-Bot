/**
 * Dual Bot API Connectivity Test
 * 
 * This script tests the connectivity between the frontend and the Dual Bot API server.
 * It checks all the essential endpoints used by the frontend.
 */

const http = require('http');

// Configuration
const API_HOST = 'localhost';
const API_PORT = 5001;

// List of endpoints to test
const endpoints = [
  '/api/health',
  '/api/status',
  '/api/dual-bot/status',
  '/api/market-data/QQQ',
  '/api/options-data/QQQ',
  '/api/news/QQQ',
  '/api/dual-bot/signals',
  '/api/config'
];

// Test a single endpoint
function testEndpoint(endpoint) {
  return new Promise((resolve, reject) => {
    console.log(`Testing ${endpoint}...`);
    
    const req = http.request({
      host: API_HOST,
      port: API_PORT,
      path: endpoint,
      method: 'GET',
      timeout: 3000
    }, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          let result;
          
          try {
            result = JSON.parse(data);
          } catch (e) {
            result = { error: 'Invalid JSON response', raw: data };
          }
          
          resolve({
            endpoint,
            status: res.statusCode,
            success: res.statusCode >= 200 && res.statusCode < 300,
            data: result
          });
        } catch (e) {
          reject({
            endpoint,
            status: 'error',
            error: e.message
          });
        }
      });
    });
    
    req.on('error', (e) => {
      reject({
        endpoint,
        status: 'error',
        error: e.message
      });
    });
    
    req.on('timeout', () => {
      req.abort();
      reject({
        endpoint,
        status: 'timeout',
        error: 'Request timed out'
      });
    });
    
    req.end();
  });
}

// Run all tests
async function runTests() {
  console.log('Starting Dual Bot API connectivity tests...');
  console.log(`Testing connection to ${API_HOST}:${API_PORT}`);
  console.log('----------------------------------------');
  
  const results = {
    timestamp: new Date().toISOString(),
    summary: {
      total: endpoints.length,
      success: 0,
      failed: 0
    },
    endpoints: []
  };
  
  for (const endpoint of endpoints) {
    try {
      const result = await testEndpoint(endpoint);
      results.endpoints.push(result);
      
      if (result.success) {
        results.summary.success++;
        console.log(`✅ ${endpoint}: SUCCESS (${result.status})`);
      } else {
        results.summary.failed++;
        console.log(`❌ ${endpoint}: FAILED (${result.status})`);
      }
    } catch (error) {
      results.summary.failed++;
      results.endpoints.push(error);
      console.log(`❌ ${endpoint}: ERROR - ${error.error}`);
    }
  }
  
  console.log('----------------------------------------');
  console.log(`Results: ${results.summary.success}/${results.summary.total} endpoints successful`);
  
  if (results.summary.failed > 0) {
    console.log('Some tests failed. Check the specific errors above.');
    console.log('Possible reasons:');
    console.log('1. Dual Bot API server is not running (run python dual_bot_api_server.py)');
    console.log('2. API server is running on a different port (check port in dual_bot_api_server.py)');
    console.log('3. Network or firewall issues preventing connection');
  } else {
    console.log('All endpoints are accessible!');
  }
  
  return results;
}

// Run the tests
runTests()
  .then(() => {
    console.log('Test completed.');
  })
  .catch(error => {
    console.error('Test failed with error:', error);
  }); 