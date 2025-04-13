/**
 * AI Trading Bot - System Scheduler Setup
 * 
 * This script helps configure the AI Trading Bot cronjob scheduler
 * to run automatically with the system's task scheduler.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');

// Get the absolute path to the project directory
const PROJECT_DIR = path.resolve(__dirname);

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function askQuestion(question) {
  return new Promise(resolve => {
    rl.question(question, answer => {
      resolve(answer);
    });
  });
}

// Log helper
function log(message, type = 'INFO') {
  const timestamp = new Date().toISOString().replace('T', ' ').substr(0, 19);
  console.log(`[${timestamp}] [${type}] ${message}`);
}

// Check operating system
function checkOS() {
  const platform = os.platform();
  log(`Detected operating system: ${platform}`);
  
  if (platform === 'win32') {
    return 'windows';
  } else if (platform === 'darwin') {
    return 'mac';
  } else if (platform === 'linux') {
    return 'linux';
  } else {
    log(`Unsupported operating system: ${platform}`, 'ERROR');
    return null;
  }
}

// Create startup script
function createStartupScript(osType) {
  const scriptDir = path.join(PROJECT_DIR, 'scripts');
  if (!fs.existsSync(scriptDir)) {
    fs.mkdirSync(scriptDir, { recursive: true });
  }
  
  if (osType === 'windows') {
    // Create Windows batch file
    const batchFilePath = path.join(scriptDir, 'start-cron-scheduler.bat');
    const batchContent = `@echo off
echo Starting AI Trading Bot Cron Scheduler...
cd "${PROJECT_DIR}"
node cron-scheduler.js
`;
    fs.writeFileSync(batchFilePath, batchContent);
    log(`Created Windows batch file: ${batchFilePath}`);
    return batchFilePath;
  } else {
    // Create shell script for Mac/Linux
    const shellFilePath = path.join(scriptDir, 'start-cron-scheduler.sh');
    const shellContent = `#!/bin/bash
echo "Starting AI Trading Bot Cron Scheduler..."
cd "${PROJECT_DIR}"
node cron-scheduler.js
`;
    fs.writeFileSync(shellFilePath, shellContent);
    fs.chmodSync(shellFilePath, '755'); // Make executable
    log(`Created shell script: ${shellFilePath}`);
    return shellFilePath;
  }
}

// Setup Windows Task Scheduler
async function setupWindowsTaskScheduler(scriptPath) {
  log('Setting up Windows Task Scheduler...');
  
  const taskName = await askQuestion('Enter task name (default: AITradingBotScheduler): ');
  const finalTaskName = taskName || 'AITradingBotScheduler';
  
  const runAtStartup = await askQuestion('Run at system startup? (y/n, default: y): ');
  const runAtStartupBool = runAtStartup.toLowerCase() !== 'n';
  
  const createLogoutGap = 'PT30S'; // 30 second delay
  
  try {
    log('Creating scheduled task...');
    
    // For startup task
    if (runAtStartupBool) {
      execSync(`schtasks /create /tn "${finalTaskName}" /tr "${scriptPath}" /sc onstart /delay ${createLogoutGap} /f`);
      log('Scheduled task created to run at system startup');
    } else {
      // For daily task
      execSync(`schtasks /create /tn "${finalTaskName}" /tr "${scriptPath}" /sc daily /st 08:30 /f`);
      log('Scheduled task created to run daily at 8:30 AM');
    }
    
    return true;
  } catch (error) {
    log(`Error creating scheduled task: ${error.message}`, 'ERROR');
    log('You may need to run this script as an administrator', 'ERROR');
    return false;
  }
}

// Setup Linux/Mac crontab
async function setupCrontab(scriptPath) {
  log('Setting up crontab...');
  
  try {
    // Check if crontab is available
    execSync('command -v crontab');
    
    // Get current crontab
    const currentCrontab = execSync('crontab -l').toString().trim();
    
    // Prepare new crontab entry
    const runAtStartup = await askQuestion('Run at system startup? (y/n, default: y): ');
    const runAtStartupBool = runAtStartup.toLowerCase() !== 'n';
    
    let newEntry;
    if (runAtStartupBool) {
      newEntry = `@reboot ${scriptPath}`;
    } else {
      newEntry = `30 8 * * * ${scriptPath}`;
    }
    
    // Check if entry already exists
    if (currentCrontab.includes(scriptPath)) {
      log('Crontab entry already exists. Skipping...');
      return true;
    }
    
    // Combine and update crontab
    const newCrontab = currentCrontab ? `${currentCrontab}\n${newEntry}` : newEntry;
    fs.writeFileSync('/tmp/trading-bot-crontab', newCrontab);
    execSync('crontab /tmp/trading-bot-crontab');
    fs.unlinkSync('/tmp/trading-bot-crontab');
    
    log('Crontab updated successfully');
    if (runAtStartupBool) {
      log('Cron job scheduled to run at system startup');
    } else {
      log('Cron job scheduled to run daily at 8:30 AM');
    }
    
    return true;
  } catch (error) {
    log(`Error setting up crontab: ${error.message}`, 'ERROR');
    return false;
  }
}

// Main function
async function main() {
  log('=' .repeat(60));
  log('AI Trading Bot - System Scheduler Setup');
  log('=' .repeat(60));
  
  // Check operating system
  const osType = checkOS();
  if (!osType) {
    log('Exiting setup due to unsupported operating system', 'ERROR');
    rl.close();
    return;
  }
  
  // Create startup script
  const scriptPath = createStartupScript(osType);
  
  // Set up system scheduler
  let success = false;
  if (osType === 'windows') {
    success = await setupWindowsTaskScheduler(scriptPath);
  } else {
    success = await setupCrontab(scriptPath);
  }
  
  if (success) {
    log('System scheduler setup completed successfully');
    log('The AI Trading Bot cron scheduler will now run automatically');
  } else {
    log('System scheduler setup failed. Please check the error messages above.', 'ERROR');
    log('You can still run the cron scheduler manually with:', 'INFO');
    log(`node ${path.join(PROJECT_DIR, 'cron-scheduler.js')}`, 'INFO');
  }
  
  rl.close();
}

// Run main function
main(); 