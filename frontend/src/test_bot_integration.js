/**
 * Bot Status API Integration Test Script
 * 
 * This script tests the connection between the frontend and the bot status API.
 * Run it with: node test_bot_integration.js
 */
const http = require('http');
const https = require('https');

// API endpoint to test
const API_ENDPOINT = '/api/bot/status';
const API_HOST = 'localhost';
const API_PORT = 5000;

console.log(`Testing Bot Status API Integration at http://${API_HOST}:${API_PORT}${API_ENDPOINT}`);

// Make the request to the API
const request = http.request({
  host: API_HOST,
  port: API_PORT,
  path: API_ENDPOINT,
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
}, (response) => {
  console.log(`API Response Status Code: ${response.statusCode}`);
  console.log(`API Response Headers: ${JSON.stringify(response.headers)}`);
  
  let data = '';
  
  response.on('data', (chunk) => {
    data += chunk;
  });
  
  response.on('end', () => {
    try {
      const parsedData = JSON.parse(data);
      console.log('\nBot Status API Response:');
      console.log(JSON.stringify(parsedData, null, 2));
      
      // Check for expected data structure
      const hasAutonomousBot = parsedData.hasOwnProperty('autonomous_bot');
      const hasRsiBot = parsedData.hasOwnProperty('rsi_bot');
      const hasDualBot = parsedData.hasOwnProperty('dual_bot');
      
      console.log('\nAPI Response Validation:');
      console.log(`- Has autonomous_bot: ${hasAutonomousBot ? 'Yes' : 'No'}`);
      console.log(`- Has rsi_bot: ${hasRsiBot ? 'Yes' : 'No'}`);
      console.log(`- Has dual_bot: ${hasDualBot ? 'Yes' : 'No'}`);
      
      // Overall validation
      if (hasAutonomousBot && hasRsiBot && hasDualBot) {
        console.log('\n✅ SUCCESS: API returned the expected data structure');
      } else {
        console.log('\n❌ ERROR: API response is missing expected data');
      }
    } catch (e) {
      console.error('Error parsing JSON response:', e.message);
      console.log('Raw response:', data);
    }
  });
});

request.on('error', (error) => {
  console.error(`\n❌ ERROR: Failed to connect to the API: ${error.message}`);
  
  if (error.code === 'ECONNREFUSED') {
    console.log('\nTroubleshooting tips:');
    console.log('1. Make sure the API server is running at http://localhost:5000');
    console.log('2. Check if there are any CORS issues (the browser might block the requests)');
    console.log('3. Verify the endpoint path is correct: /api/bot/status');
  }
});

request.end(); 