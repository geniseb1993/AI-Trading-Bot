const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

// Configuration
const config = {
    isProduction: process.env.NODE_ENV === 'production' || process.env.APP_ENV === 'production',
    useVirtualEnv: true,
    pythonCommand: process.env.PYTHON_COMMAND || 'python3',
    venvPath: process.env.VENV_PATH || './.venv',
    requiredPackages: ['flask', 'flask_cors', 'pandas'],
    port: process.env.PORT || 10000
};

// Logger setup
const logger = {
    timestamp: () => {
        const now = new Date();
        return `[${now.toLocaleTimeString()}]`;
    },
    log: (tag, message) => {
        console.log(`${logger.timestamp()} [${tag}] ${message}`);
    },
    error: (tag, message) => {
        console.error(`${logger.timestamp()} [${tag}] ${message}`);
    }
};

// Helper function to check if a package is installed
const checkPackage = (packageName) => {
    return new Promise((resolve) => {
        const pythonCmd = config.useVirtualEnv ? getVenvPythonPath() : config.pythonCommand;
        const cmd = `${pythonCmd} -c "import ${packageName}; print('ok')"`;
        
        exec(cmd, (error) => {
            resolve(!error);
        });
    });
};

// Helper to get the Python path in the virtual environment
function getVenvPythonPath() {
    if (os.platform() === 'win32') {
        return path.join(config.venvPath, 'Scripts', 'python');
    } else {
        return path.join(config.venvPath, 'bin', 'python');
    }
}

// Helper to run a command in the virtual environment
function runInVenv(command) {
    if (config.useVirtualEnv) {
        if (os.platform() === 'win32') {
            // Windows
            return `${path.join(config.venvPath, 'Scripts', 'activate')} && ${command}`;
        } else {
            // Linux/Mac
            return `source ${path.join(config.venvPath, 'bin', 'activate')} && ${command}`;
        }
    }
    return command;
}

// Check required Python packages
async function checkRequiredPackages() {
    logger.log('MAIN', 'Checking required Python packages...');
    
    let missingPackages = [];
    
    for (const pkg of config.requiredPackages) {
        const isInstalled = await checkPackage(pkg);
        if (!isInstalled) {
            missingPackages.push(pkg);
        }
    }
    
    if (missingPackages.length > 0) {
        logger.log('MAIN', `Missing packages: ${missingPackages.join(', ')}`);
        
        if (config.isProduction) {
            logger.error('MAIN', 'Missing required packages in production environment!');
            process.exit(1);
        }
        
        // Install missing packages
        const installCmd = `pip install ${missingPackages.join(' ')}`;
        const fullCmd = config.useVirtualEnv ? runInVenv(installCmd) : installCmd;
        
        logger.log('MAIN', `Installing missing packages: ${fullCmd}`);
        exec(fullCmd, (error, stdout, stderr) => {
            if (error) {
                logger.error('MAIN', `Error installing packages: ${error.message}`);
                logger.error('MAIN', stderr);
            } else {
                logger.log('MAIN', 'Packages installed successfully');
            }
        });
    } else {
        logger.log('MAIN', 'All required Python packages are installed');
    }
}

// Start the API server
function startAPIServer() {
    logger.log('BACKEND', 'Starting Flask API server...');
    
    // Determine the correct command to start the API server
    let startCommand;
    
    if (config.isProduction) {
        // In production, use gunicorn
        startCommand = runInVenv(`gunicorn wsgi:app --bind=0.0.0.0:${config.port}`);
    } else {
        // In development, use Flask's built-in server
        const pythonScript = 'wsgi.py';
        startCommand = runInVenv(`${config.pythonCommand} ${pythonScript}`);
    }
    
    // Use exec to start the server without a child process
    if (os.platform() === 'win32') {
        // On Windows, we use a different approach
        const apiServer = spawn('cmd.exe', ['/c', startCommand], {
            stdio: 'inherit',
            shell: true
        });
        
        apiServer.on('error', (err) => {
            logger.error('BACKEND', `Failed to start API server: ${err}`);
        });
    } else {
        // On Linux/Mac, we can use exec directly
        exec(startCommand, (error, stdout, stderr) => {
            if (error) {
                logger.error('BACKEND', `API server error: ${error.message}`);
                return;
            }
            logger.log('BACKEND', stdout);
            if (stderr) logger.error('BACKEND', stderr);
        });
    }
}

// Main function to start all servers
async function main() {
    logger.log('MAIN', '============================================================');
    logger.log('MAIN', 'Starting AI Trading Bot Server');
    logger.log('MAIN', '============================================================');
    
    // Check for Python
    exec(`${config.pythonCommand} --version`, (error, stdout) => {
        if (error) {
            logger.error('MAIN', `Error detecting Python: ${error.message}`);
        } else {
            logger.log('MAIN', `Python detected: ${stdout.trim()}`);
        }
    });

    // Check required packages
    await checkRequiredPackages();
    
    // Start the API server
    startAPIServer();
    
    logger.log('MAIN', 'Press Ctrl+C to stop all servers.');
}

// Run the main function
main().catch(err => {
    logger.error('MAIN', `Error in main function: ${err.message}`);
    process.exit(1);
}); 