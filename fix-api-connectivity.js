/**
 * Dual Bot API Connectivity Fix Script
 * 
 * This script diagnoses and attempts to fix common connectivity issues 
 * between the frontend and the Dual Bot API server.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Configuration
const API_HOST = 'localhost';
const API_PORT = 5001;
const API_SERVER_FILE = 'dual_bot_api_server.py';
const FRONTEND_CONFIG_FILES = [
  'frontend/src/services/apiService.js',
  'frontend/src/services/dualBotService.js',
  'frontend/src/setupProxy.js'
];

// List of essential endpoints to test
const ESSENTIAL_ENDPOINTS = [
  '/api/health',
  '/api/status',
  '/api/dual-bot/status'
];

// Main function
async function main() {
  console.log('======================================');
  console.log('  Dual Bot API Connectivity Fixer');
  console.log('======================================');
  console.log('This script will diagnose and fix common connectivity issues.\n');
  
  // Step 1: Check if the API server file exists
  if (!fs.existsSync(API_SERVER_FILE)) {
    console.error(`❌ ERROR: ${API_SERVER_FILE} not found in the current directory.`);
    console.log('Make sure you are running this script from the project root directory.');
    return false;
  }
  
  // Step 2: Check if the API server is running
  const isServerRunning = await checkServerRunning();
  
  if (!isServerRunning) {
    console.log('API server is not running. Attempting to start it...');
    const serverStarted = await startAPIServer();
    
    if (!serverStarted) {
      console.error('❌ Failed to start the API server. Please check for errors in the API server.');
      return false;
    }
  }
  
  // Step 3: Test critical endpoints
  console.log('\nTesting essential API endpoints...');
  const endpointResults = await testEndpoints(ESSENTIAL_ENDPOINTS);
  
  // Step 4: Check frontend configurations
  console.log('\nChecking frontend configuration files...');
  const configResults = checkFrontendConfigs();
  
  // Step 5: Summarize findings and recommendations
  console.log('\n======================================');
  console.log('  Connectivity Diagnosis Summary');
  console.log('======================================');
  
  if (isServerRunning) {
    console.log('✅ API Server Status: Running');
  } else {
    console.log('❌ API Server Status: Not Running');
  }
  
  // Endpoint results
  console.log('\n--- Endpoint Test Results ---');
  let allEndpointsWorking = true;
  
  for (const result of endpointResults) {
    if (result.success) {
      console.log(`✅ ${result.endpoint}: SUCCESS`);
    } else {
      console.log(`❌ ${result.endpoint}: FAILED - ${result.error || 'Unknown error'}`);
      allEndpointsWorking = false;
    }
  }
  
  // Config file results
  console.log('\n--- Configuration Files ---');
  let allConfigsCorrect = true;
  
  for (const config of configResults) {
    if (config.correct) {
      console.log(`✅ ${config.file}: Correct configuration`);
    } else {
      console.log(`❌ ${config.file}: ${config.issues.join(', ')}`);
      allConfigsCorrect = false;
    }
  }
  
  // Final verdict
  console.log('\n--- Final Diagnosis ---');
  
  if (isServerRunning && allEndpointsWorking && allConfigsCorrect) {
    console.log('✅ GOOD NEWS: All connectivity checks passed!');
    console.log('The API server is running correctly and the frontend is properly configured.');
    return true;
  } else {
    console.log('❌ ISSUES DETECTED: There are connectivity problems that need to be addressed.');
    
    // Provide specific recommendations
    console.log('\n--- Recommendations ---');
    
    if (!isServerRunning) {
      console.log('1. Start the API server by running:');
      console.log('   python dual_bot_api_server.py');
    }
    
    if (!allEndpointsWorking) {
      console.log('2. Check the API server logs for errors:');
      console.log('   Look in dual_bot_api_server.log for any error messages.');
    }
    
    if (!allConfigsCorrect) {
      console.log('3. Fix the frontend configuration files:');
      for (const config of configResults) {
        if (!config.correct) {
          console.log(`   - ${config.file}: ${config.issues.join(', ')}`);
        }
      }
    }
    
    return false;
  }
}

// Check if the API server is running
async function checkServerRunning() {
  try {
    console.log('Checking if API server is running...');
    const result = await testEndpoint('/api/health');
    return result.success;
  } catch (error) {
    console.log('API server is not running or not accessible.');
    return false;
  }
}

// Start the API server
function startAPIServer() {
  return new Promise((resolve) => {
    console.log(`Attempting to start ${API_SERVER_FILE}...`);
    
    try {
      // Use python executable to start the server
      const pythonProcess = spawn('python', [API_SERVER_FILE], {
        detached: true,
        stdio: 'ignore'
      });
      
      // Detach the process so it runs independently
      pythonProcess.unref();
      
      console.log(`Started API server with PID ${pythonProcess.pid}`);
      console.log('Waiting for server to initialize...');
      
      // Wait for the server to start up
      setTimeout(async () => {
        try {
          const serverRunning = await checkServerRunning();
          resolve(serverRunning);
        } catch (e) {
          console.error('Error checking if server started:', e.message);
          resolve(false);
        }
      }, 5000); // Give it 5 seconds to start
    } catch (error) {
      console.error('Failed to start API server:', error.message);
      resolve(false);
    }
  });
}

// Test a single endpoint
function testEndpoint(endpoint) {
  return new Promise((resolve, reject) => {
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
            result = { error: 'Invalid JSON response' };
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
            success: false,
            error: e.message
          });
        }
      });
    });
    
    req.on('error', (e) => {
      reject({
        endpoint,
        success: false,
        error: e.message
      });
    });
    
    req.on('timeout', () => {
      req.abort();
      reject({
        endpoint,
        success: false,
        error: 'Request timed out'
      });
    });
    
    req.end();
  });
}

// Test multiple endpoints
async function testEndpoints(endpoints) {
  const results = [];
  
  for (const endpoint of endpoints) {
    try {
      const result = await testEndpoint(endpoint);
      results.push(result);
    } catch (error) {
      results.push(error);
    }
  }
  
  return results;
}

// Check frontend configuration files
function checkFrontendConfigs() {
  const results = [];
  
  for (const file of FRONTEND_CONFIG_FILES) {
    try {
      if (!fs.existsSync(file)) {
        results.push({
          file,
          correct: false,
          issues: ['File not found']
        });
        continue;
      }
      
      const content = fs.readFileSync(file, 'utf8');
      const issues = [];
      
      // Check for common issues based on the file
      if (file.includes('apiService.js')) {
        if (!content.includes('/api/health')) {
          issues.push('Missing or incorrect health endpoint');
        }
        
        if (!content.includes('/api/status') && !content.includes('/dual-bot/status')) {
          issues.push('Missing or incorrect status endpoint');
        }
        
        // Check API base URL
        if (!content.includes('localhost:5001')) {
          issues.push('Incorrect API host or port');
        }
      }
      
      if (file.includes('dualBotService.js')) {
        if (!content.includes('localhost:5001/api')) {
          issues.push('Incorrect API base URL');
        }
      }
      
      if (file.includes('setupProxy.js')) {
        if (!content.includes('localhost') || !content.includes('5001')) {
          issues.push('Incorrect proxy configuration');
        }
      }
      
      results.push({
        file,
        correct: issues.length === 0,
        issues
      });
    } catch (error) {
      results.push({
        file,
        correct: false,
        issues: [`Error reading file: ${error.message}`]
      });
    }
  }
  
  return results;
}

// Run the main function
main()
  .then(success => {
    if (success) {
      console.log('\nAll checks completed successfully. The system is properly configured.');
    } else {
      console.log('\nPlease address the issues above to fix API connectivity problems.');
    }
  })
  .catch(error => {
    console.error('Error running diagnostics:', error);
  }); 