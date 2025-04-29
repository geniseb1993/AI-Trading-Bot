/**
 * Combined Script to start both the API server and the frontend app
 * Run with: node start-ui-with-api.js
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const API_SCRIPT = 'run_api.py';
const API_PORT = 5000;
const PYTHON_CMD = 'python';
const UI_PORT = 3000;
const UI_DIR = path.join(__dirname, 'frontend');

// Colors for console output
const colors = {
  api: '\x1b[36m', // Cyan
  ui: '\x1b[32m',  // Green
  error: '\x1b[31m', // Red
  warning: '\x1b[33m', // Yellow
  reset: '\x1b[0m'
};

console.log(`${colors.reset}=== AI Trading Bot System Starter ===`);

// Check if Python is available
const checkPython = spawn(PYTHON_CMD, ['--version']);
checkPython.on('error', (err) => {
  console.error(`${colors.error}Error: Python not found. Please make sure Python is installed and in PATH.${colors.reset}`);
  process.exit(1);
});

// Check if API script exists
if (!fs.existsSync(API_SCRIPT)) {
  console.error(`${colors.error}Error: API script ${API_SCRIPT} not found.${colors.reset}`);
  process.exit(1);
}

// Function to start the API server
function startAPIServer() {
  console.log(`${colors.api}Starting API server on port ${API_PORT}...${colors.reset}`);
  
  const apiProcess = spawn(PYTHON_CMD, [API_SCRIPT]);
  
  apiProcess.stdout.on('data', (data) => {
    console.log(`${colors.api}[API] ${data.toString().trim()}${colors.reset}`);
  });
  
  apiProcess.stderr.on('data', (data) => {
    console.error(`${colors.error}[API ERROR] ${data.toString().trim()}${colors.reset}`);
  });
  
  apiProcess.on('close', (code) => {
    console.log(`${colors.warning}[API] Process exited with code ${code}${colors.reset}`);
  });
  
  return apiProcess;
}

// Function to start the UI
function startUI() {
  console.log(`${colors.ui}Starting frontend app on port ${UI_PORT}...${colors.reset}`);
  
  // Check if we're in the right directory
  if (!fs.existsSync(path.join(UI_DIR, 'package.json'))) {
    console.error(`${colors.error}Error: package.json not found in ${UI_DIR}. Make sure you're in the right directory.${colors.reset}`);
    process.exit(1);
  }
  
  const uiProcess = spawn('npm', ['start'], { cwd: UI_DIR, shell: true });
  
  uiProcess.stdout.on('data', (data) => {
    console.log(`${colors.ui}[UI] ${data.toString().trim()}${colors.reset}`);
  });
  
  uiProcess.stderr.on('data', (data) => {
    const output = data.toString().trim();
    // Filter out non-error npm messages that come through stderr
    if (!output.includes('compiled successfully') && !output.includes('Starting the development server')) {
      console.error(`${colors.error}[UI ERROR] ${output}${colors.reset}`);
    } else {
      console.log(`${colors.ui}[UI] ${output}${colors.reset}`);
    }
  });
  
  uiProcess.on('close', (code) => {
    console.log(`${colors.warning}[UI] Process exited with code ${code}${colors.reset}`);
  });
  
  return uiProcess;
}

// Start both processes
const apiProcess = startAPIServer();

// Wait a bit for the API to start before starting the UI
setTimeout(() => {
  const uiProcess = startUI();
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log(`${colors.reset}\nShutting down...${colors.reset}`);
    apiProcess.kill();
    uiProcess.kill();
    process.exit(0);
  });
  
}, 3000); // Wait 3 seconds

console.log(`${colors.reset}Press Ctrl+C to stop both servers.${colors.reset}`); 