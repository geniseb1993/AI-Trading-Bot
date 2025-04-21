/**
 * API Endpoints Test Script
 * 
 * This script tests connectivity to all the API endpoints used in the frontend.
 * Run with: node check-api-endpoints.js
 */

const axios = require('axios');

// Configuration
const API_BASE_URL = 'http://localhost:5000';
const ENDPOINTS = [
  // With /api prefix
  '/api/health-check',
  '/api/bot/status',
  '/api/bot/trading-history',
  '/api/bot/performance',
  '/api/ceo-dashboard',
  '/api/ceo-settings',
  '/api/ai-activity/logs',
  '/api/ai-activity/activity-types',
  // Without /api prefix (as fallback)
  '/health-check',
  '/bot/status',
  '/bot/trading-history',
  '/bot/performance',
  '/ceo-dashboard',
  '/ceo-settings',
  '/ai-activity/logs',
  '/ai-activity/activity-types',
];

async function testEndpoints() {
  console.log('=== API Endpoints Test ===');
  console.log(`Base URL: ${API_BASE_URL}\n`);
  
  let successCount = 0;
  let failCount = 0;
  
  for (const endpoint of ENDPOINTS) {
    try {
      console.log(`Testing: ${endpoint}`);
      const response = await axios.get(`${API_BASE_URL}${endpoint}`, {
        timeout: 5000
      });
      
      console.log(`  Status: ${response.status} ${response.statusText}`);
      console.log(`  Response: ${typeof response.data === 'object' ? 'JSON Object' : typeof response.data}`);
      console.log('  Result: ✅ SUCCESS\n');
      successCount++;
    } catch (error) {
      console.log(`  Error: ${error.message}`);
      if (error.response) {
        console.log(`  Status: ${error.response.status} ${error.response.statusText}`);
      }
      console.log('  Result: ❌ FAILED\n');
      failCount++;
    }
  }
  
  console.log('=== Test Summary ===');
  console.log(`Total endpoints: ${ENDPOINTS.length}`);
  console.log(`Success: ${successCount}`);
  console.log(`Failed: ${failCount}`);
}

testEndpoints().catch(err => {
  console.error('Test script error:', err);
}); 