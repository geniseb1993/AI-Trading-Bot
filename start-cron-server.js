/**
 * Start Cron Job Scheduler
 * 
 * This script starts the cron job scheduler for the AI Trading Bot,
 * with proper error handling and logging.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Check if required dependencies are installed
const checkDependencies = () => {
  const packageJsonPath = path.join(__dirname, 'package.json');
  
  if (!fs.existsSync(packageJsonPath)) {
    console.error('package.json not found. Please run this from the project root.');
    return false;
  }
  
  const requiredDeps = ['node-cron', 'axios', 'date-fns', 'express'];
  const missingDeps = [];
  
  try {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
    
    for (const dep of requiredDeps) {
      if (!dependencies[dep]) {
        missingDeps.push(dep);
      }
    }
    
    if (missingDeps.length > 0) {
      console.error(`Missing dependencies: ${missingDeps.join(', ')}`);
      console.error(`Please install them using: npm install ${missingDeps.join(' ')}`);
      return false;
    }
    
    return true;
  } catch (error) {
    console.error(`Error checking dependencies: ${error.message}`);
    return false;
  }
};

// Start cron server
const startCronServer = () => {
  console.log('Starting cron job scheduler...');
  
  const cronProcess = spawn('node', ['cron-scheduler.js'], {
    stdio: 'inherit',
    detached: false
  });
  
  cronProcess.on('error', (error) => {
    console.error(`Failed to start cron scheduler: ${error.message}`);
  });
  
  process.on('SIGINT', () => {
    console.log('Stopping cron scheduler...');
    cronProcess.kill('SIGINT');
    process.exit();
  });
  
  console.log('Cron scheduler started. Press Ctrl+C to stop.');
};

// Main function
const main = () => {
  console.log('=== AI Trading Bot Cron Job Scheduler ===');
  
  if (!checkDependencies()) {
    process.exit(1);
  }
  
  startCronServer();
};

// Run the main function
main(); 