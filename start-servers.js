const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

// Log with timestamp and server type
function log(server, message, color = colors.reset) {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`${color}[${timestamp}] [${server}] ${message}${colors.reset}`);
}

// Kill all child processes on exit
const processesToKill = [];
process.on('SIGINT', () => {
  log('MAIN', 'Shutting down all servers...', colors.yellow);
  processesToKill.forEach(proc => {
    if (!proc.killed) {
      proc.kill();
    }
  });
  process.exit(0);
});

// Check if Python is installed
function checkPythonInstallation() {
  const pythonCommand = os.platform() === 'win32' ? 'python --version' : 'python3 --version';
  
  try {
    const cmd = os.platform() === 'win32' ? 'python' : 'python3';
    const args = ['--version'];
    const pythonProcess = spawn(cmd, args, { shell: true });
    
    pythonProcess.on('error', (err) => {
      log('MAIN', `Error checking Python: ${err.message}`, colors.red);
      log('MAIN', 'Please install Python and try again.', colors.red);
      process.exit(1);
    });
    
    pythonProcess.stdout.on('data', (data) => {
      log('MAIN', `Python detected: ${data.toString().trim()}`, colors.green);
    });
    
    pythonProcess.stderr.on('data', (data) => {
      log('MAIN', `Python check stderr: ${data.toString().trim()}`, colors.yellow);
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        log('MAIN', `Python check exited with code ${code}`, colors.red);
        log('MAIN', 'Please install Python and try again.', colors.red);
        process.exit(1);
      }
    });
  } catch (err) {
    log('MAIN', `Failed to check Python: ${err.message}`, colors.red);
    process.exit(1);
  }
}

// Check if required Python packages are installed
function checkPythonPackages() {
  log('MAIN', 'Checking required Python packages...', colors.blue);
  
  const cmd = os.platform() === 'win32' ? 'python' : 'python3';
  const checkScript = `
import sys
required = ['flask', 'flask_cors', 'pandas', 'plyer', 'pyttsx3', 'pygame', 'hume', 'python-dotenv']
missing = []
for pkg in required:
    try:
        __import__(pkg.replace('-', '_'))
        print(f"✓ {pkg}")
    except ImportError:
        missing.append(pkg)
        print(f"✗ {pkg}")
if missing:
    print(f"Missing packages: {', '.join(missing)}")
    sys.exit(1)
sys.exit(0)
  `;
  
  const pythonProcess = spawn(cmd, ['-c', checkScript], { shell: true });
  
  pythonProcess.stdout.on('data', (data) => {
    const output = data.toString().trim();
    if (output.includes('✓')) {
      log('MAIN', output, colors.green);
    } else if (output.includes('✗')) {
      log('MAIN', output, colors.red);
    } else if (output.includes('Missing packages')) {
      log('MAIN', output, colors.red);
      log('MAIN', 'Installing missing packages...', colors.yellow);
      const installCmd = os.platform() === 'win32' ? 'python' : 'python3';
      const missingPackages = output.split(': ')[1];
      const installProcess = spawn(installCmd, ['-m', 'pip', 'install', ...missingPackages.split(', ')], { shell: true });
      
      installProcess.stdout.on('data', (data) => {
        log('MAIN', data.toString().trim(), colors.yellow);
      });
      
      installProcess.stderr.on('data', (data) => {
        log('MAIN', data.toString().trim(), colors.yellow);
      });
      
      installProcess.on('close', (code) => {
        if (code === 0) {
          log('MAIN', 'Successfully installed missing packages!', colors.green);
        } else {
          log('MAIN', `Failed to install packages. Please run: pip install ${missingPackages}`, colors.red);
        }
      });
    }
  });
  
  pythonProcess.stderr.on('data', (data) => {
    log('MAIN', data.toString().trim(), colors.red);
  });
  
  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      log('MAIN', 'Some required Python packages are missing.', colors.yellow);
    } else {
      log('MAIN', 'All required Python packages are installed!', colors.green);
    }
  });
}

// Start the Flask API server
function startBackend() {
  log('BACKEND', 'Starting Flask API server...', colors.cyan);

  // First, check if the server is already running
  checkBackendHealth(true).then(isRunning => {
    if (isRunning) {
      log('BACKEND', 'Flask API server is already running!', colors.green);
      return;
    }

  const pythonCmd = os.platform() === 'win32' ? 'python' : 'python3';
  const backendProcess = spawn(pythonCmd, ['start-api.py'], { 
    shell: true,
      cwd: process.cwd(),
      env: {
        ...process.env,
        APP_ENV: 'production' // Ensure production environment
      }
  });
  
  processesToKill.push(backendProcess);

  backendProcess.stdout.on('data', (data) => {
    const output = data.toString().trim();
    if (output) {
      log('BACKEND', output, colors.cyan);
    }
  });

  backendProcess.stderr.on('data', (data) => {
    const output = data.toString().trim();
    if (output) {
      // Check for server running message
      if (output.includes('Running on http')) {
        log('BACKEND', 'Server started successfully!', colors.green);
      } else {
        log('BACKEND', output, colors.yellow);
      }
    }
  });

  backendProcess.on('close', (code) => {
    if (code !== 0) {
      log('BACKEND', `API server exited with code ${code}`, colors.red);
    }
  });

  backendProcess.on('error', (err) => {
    log('BACKEND', `Failed to start API server: ${err.message}`, colors.red);
  });
  });
}

// Start the React frontend server
function startFrontend() {
  log('FRONTEND', 'Starting React frontend server...', colors.magenta);

  const frontendPath = path.join(process.cwd(), 'frontend');
  
  if (!fs.existsSync(frontendPath)) {
    log('FRONTEND', `Frontend directory not found at ${frontendPath}`, colors.red);
    log('FRONTEND', 'Make sure you are running this script from the project root directory', colors.red);
    process.exit(1);
  }

  // Install frontend dependencies if node_modules doesn't exist
  const frontendNodeModules = path.join(frontendPath, 'node_modules');
  if (!fs.existsSync(frontendNodeModules)) {
    log('FRONTEND', 'Installing frontend dependencies...', colors.yellow);
    const npmCmd = os.platform() === 'win32' ? 'npm.cmd' : 'npm';
    const installProcess = spawn(npmCmd, ['install'], { 
      shell: true,
      cwd: frontendPath
    });
    
    installProcess.stdout.on('data', (data) => {
      log('FRONTEND', data.toString().trim(), colors.yellow);
    });
    
    installProcess.stderr.on('data', (data) => {
      log('FRONTEND', data.toString().trim(), colors.yellow);
    });
    
    installProcess.on('close', (code) => {
      if (code === 0) {
        log('FRONTEND', 'Frontend dependencies installed successfully!', colors.green);
        startFrontendServer(frontendPath);
      } else {
        log('FRONTEND', `Failed to install frontend dependencies. Please run 'npm install' in the frontend directory.`, colors.red);
        process.exit(1);
      }
    });
  } else {
    startFrontendServer(frontendPath);
  }
}

function startFrontendServer(frontendPath) {
  const npmCmd = os.platform() === 'win32' ? 'npm.cmd' : 'npm';
  const frontendProcess = spawn(npmCmd, ['start'], { 
    shell: true,
    cwd: frontendPath
  });
  
  processesToKill.push(frontendProcess);

  frontendProcess.stdout.on('data', (data) => {
    const output = data.toString().trim();
    if (output) {
      // Check for server running message
      if (output.includes('localhost:')) {
        log('FRONTEND', 'Server started successfully!', colors.green);
        
        // Extract the port number
        const portMatch = output.match(/localhost:(\d+)/);
        if (portMatch && portMatch[1]) {
          const frontendPort = portMatch[1];
          log('FRONTEND', `Frontend available at http://localhost:${frontendPort}`, colors.green);
          
          // Set up a more comprehensive health check system
          setInterval(() => {
            checkFrontendHealth(frontendPort);
            checkBackendHealth();
          }, 30000); // Check every 30 seconds
        }
      }
      log('FRONTEND', output, colors.magenta);
    }
  });

  frontendProcess.stderr.on('data', (data) => {
    const output = data.toString().trim();
    if (output) {
      // Look for proxy errors
      if (output.includes('ECONNREFUSED')) {
        log('FRONTEND', 'Error connecting to API server! Make sure the backend is running properly.', colors.red);
        
        // Try to restart the backend if it's down
        log('BACKEND', 'Attempting to restart the backend server...', colors.yellow);
        startBackend();
      } else {
        log('FRONTEND', output, colors.yellow);
      }
    }
  });

  frontendProcess.on('close', (code) => {
    if (code !== 0) {
      log('FRONTEND', `Frontend server exited with code ${code}`, colors.red);
    }
  });

  frontendProcess.on('error', (err) => {
    log('FRONTEND', `Failed to start frontend server: ${err.message}`, colors.red);
  });
}

// Check API server health
function checkBackendHealth(silent = false) {
  return new Promise((resolve) => {
    if (!silent) {
    log('HEALTH', 'Checking API server health...', colors.blue);
    }
    
    const options = {
      hostname: 'localhost',
      port: 5000,
      path: '/api/test',
      method: 'GET',
      timeout: 3000
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
      if (res.statusCode === 200) {
          try {
            const responseData = JSON.parse(data);
            if (!silent) {
              log('HEALTH', `API server is healthy! Environment: ${responseData.environment || 'unknown'}`, colors.green);
            }
            resolve(true);
          } catch (e) {
            if (!silent) {
              log('HEALTH', 'API server responded with invalid JSON', colors.yellow);
            }
            resolve(false);
          }
      } else {
          if (!silent) {
        log('HEALTH', `API server responded with status: ${res.statusCode}`, colors.yellow);
      }
          resolve(false);
        }
      });
    });
    
    req.on('error', (error) => {
      if (!silent) {
      log('HEALTH', `API server health check failed: ${error.message}`, colors.red);
      log('HEALTH', 'The frontend may not be able to communicate with the backend!', colors.red);
      }
      resolve(false);
    });
    
    req.on('timeout', () => {
      if (!silent) {
      log('HEALTH', 'API server health check timed out!', colors.red);
      }
      req.destroy();
      resolve(false);
    });
    
    req.end();
  });
}

// Check frontend health
function checkFrontendHealth(port = 3000) {
  log('HEALTH', 'Checking frontend server health...', colors.blue);
  
  const options = {
    hostname: 'localhost',
    port: port,
    path: '/',
    method: 'GET',
    timeout: 3000
  };
  
  const req = http.request(options, (res) => {
    if (res.statusCode === 200) {
      log('HEALTH', 'Frontend server is healthy and responding!', colors.green);
    } else {
      log('HEALTH', `Frontend server responded with status: ${res.statusCode}`, colors.yellow);
    }
  });
  
  req.on('error', (error) => {
    log('HEALTH', `Frontend server health check failed: ${error.message}`, colors.red);
  });
  
  req.on('timeout', () => {
    log('HEALTH', 'Frontend server health check timed out!', colors.red);
    req.destroy();
  });
  
  req.end();
}

// Check for CSV data files
function checkDataFiles() {
  log('DATA', 'Checking data files...', colors.blue);
  
  const requiredFiles = [
    'buy_signals.csv',
    'short_signals.csv',
    'backtest_results.csv'
  ];
  
  let allFilesExist = true;
  
  requiredFiles.forEach(file => {
    // Check in root directory
    const rootFilePath = path.join(process.cwd(), file);
    // Check in data directory
    const dataFilePath = path.join(process.cwd(), 'data', file);
    
    if (fs.existsSync(rootFilePath)) {
      const stats = fs.statSync(rootFilePath);
      const fileSizeKB = (stats.size / 1024).toFixed(2);
      log('DATA', `✓ ${file} found in root directory (${fileSizeKB} KB)`, colors.green);
    } else if (fs.existsSync(dataFilePath)) {
      const stats = fs.statSync(dataFilePath);
      const fileSizeKB = (stats.size / 1024).toFixed(2);
      log('DATA', `✓ ${file} found in data directory (${fileSizeKB} KB)`, colors.green);
    } else {
      log('DATA', `✗ ${file} not found in root or data directory`, colors.red);
      allFilesExist = false;
    }
  });
  
  if (!allFilesExist) {
    log('DATA', 'Some data files are missing. The app will use mock data.', colors.yellow);
  }
  
  return allFilesExist;
}

// Check for environment variables
function checkEnvironmentVariables() {
  log('ENV', 'Checking environment variables...', colors.blue);
  
  const requiredVars = {
    APP_ENV: 'Application environment',
    UNUSUAL_WHALES_API_KEY: 'Unusual Whales API key',
    HUME_API_KEY: 'Hume AI API key',
  };
  
  const dotenvPath = path.join(process.cwd(), '.env');
  if (fs.existsSync(dotenvPath)) {
    log('ENV', `Found .env file at ${dotenvPath}`, colors.green);
    
    // Load and check environment variables
    const dotenvContent = fs.readFileSync(dotenvPath, 'utf8');
    const dotenvLines = dotenvContent.split('\n');
    
    Object.keys(requiredVars).forEach(varName => {
      const varLine = dotenvLines.find(line => line.startsWith(`${varName}=`));
      if (varLine) {
        const value = varLine.split('=')[1].trim();
        if (value && value !== '') {
          log('ENV', `✓ ${varName} is set`, colors.green);
        } else {
          log('ENV', `✗ ${varName} is empty`, colors.yellow);
        }
      } else {
        log('ENV', `✗ ${varName} is not defined`, colors.red);
      }
    });
    
    // Check if APP_ENV is set to production
    const appEnvLine = dotenvLines.find(line => line.startsWith('APP_ENV='));
    if (appEnvLine) {
      const value = appEnvLine.split('=')[1].trim();
      if (value === 'production') {
        log('ENV', 'APP_ENV is set to production - will use real data sources', colors.green);
      } else {
        log('ENV', `APP_ENV is set to ${value} - will use mock data`, colors.yellow);
      }
    }
  } else {
    log('ENV', '.env file not found, using environment variables from system', colors.yellow);
    
    // Check system environment variables
    Object.keys(requiredVars).forEach(varName => {
      if (process.env[varName]) {
        log('ENV', `✓ ${varName} is set in system environment`, colors.green);
      } else {
        log('ENV', `✗ ${varName} is not set in system environment`, colors.red);
      }
    });
  }
}

// Add this new function
function startCronScheduler() {
  log('CRON', 'Starting Cron Job Scheduler...', colors.blue);
  
  // Check if node-cron and other required packages are installed
  try {
    require.resolve('node-cron');
    require.resolve('axios');
    require.resolve('date-fns');
    require.resolve('express');
    log('CRON', 'Required packages are installed', colors.green);
  } catch (err) {
    log('CRON', `Missing required packages: ${err.message}`, colors.red);
    log('CRON', 'Installing missing packages...', colors.yellow);
    
    try {
      const { execSync } = require('child_process');
      execSync('npm install node-cron axios date-fns express --no-save', { stdio: 'inherit' });
      log('CRON', 'Packages installed successfully', colors.green);
    } catch (installErr) {
      log('CRON', `Failed to install packages: ${installErr.message}`, colors.red);
      log('CRON', 'Please run: npm install node-cron axios date-fns express', colors.yellow);
      return false;
    }
  }
  
  // Start the cron scheduler
  const cronProcess = spawn('node', ['cron-scheduler.js'], {
    stdio: 'pipe',
    detached: false
  });
  
  cronProcess.stdout.on('data', (data) => {
    data.toString().split('\n').forEach(line => {
      if (line.trim() !== '') {
        log('CRON', line.trim(), colors.blue);
      }
    });
  });
  
  cronProcess.stderr.on('data', (data) => {
    data.toString().split('\n').forEach(line => {
      if (line.trim() !== '') {
        log('CRON', line.trim(), colors.red);
      }
    });
  });
  
  cronProcess.on('error', (error) => {
    log('CRON', `Failed to start cron scheduler: ${error.message}`, colors.red);
    return false;
  });
  
  cronProcess.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      log('CRON', `Cron scheduler exited with code ${code}`, colors.red);
    } else {
      log('CRON', 'Cron scheduler stopped', colors.yellow);
    }
  });
  
  log('CRON', 'Cron scheduler started successfully', colors.green);
  return true;
}

// Main function
function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  const includeCron = args.includes('--with-cron') || args.includes('-c');
  const cronOnly = args.includes('--cron-only');
  
  log('MAIN', '='.repeat(60), colors.bright);
  log('MAIN', 'Starting AI Trading Bot Server', colors.bright);
  log('MAIN', '='.repeat(60), colors.bright);
  
  if (cronOnly) {
    // Only start the cron scheduler
    startCronScheduler();
    log('MAIN', 'Running in cron-only mode. Press Ctrl+C to stop.', colors.bright);
    return;
  }
  
  // Check Python installation
  checkPythonInstallation();
  
  // Check Python packages
  checkPythonPackages();
  
  // Check environment variables
  checkEnvironmentVariables();
  
  // Check data files
  checkDataFiles();
  
  // Start backend first
  startBackend();
  
  // Then start frontend after a delay
  setTimeout(() => {
    startFrontend();
    
    // Initial health check
    setTimeout(() => {
      checkBackendHealth();
      
      // Start cron scheduler if requested
      if (includeCron) {
        setTimeout(() => {
          startCronScheduler();
        }, 2000);
      }
    }, 8000);
  }, 5000);
  
  log('MAIN', `Press Ctrl+C to stop all servers${includeCron ? ' and schedulers' : ''}.`, colors.bright);
  
  if (!includeCron && !cronOnly) {
    log('MAIN', 'To start with cron scheduler: node start-servers.js --with-cron', colors.yellow);
    log('MAIN', 'To start only the cron scheduler: node start-servers.js --cron-only', colors.yellow);
  }
}

// Run the main function
main(); 