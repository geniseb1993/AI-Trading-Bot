#!/usr/bin/env python
import os
import sys
import subprocess
import time
import requests
import socket
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fix-dual-bot-api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Essential endpoints that the frontend expects
ESSENTIAL_ENDPOINTS = [
    '/api/health',
    '/api/status',
    '/api/dual-bot/status',
    '/api/market-data/QQQ',
    '/api/options-data/QQQ',
    '/api/news/QQQ',
    '/api/config'
]

def check_dependencies():
    """Check and install missing dependencies."""
    try:
        logger.info("Checking for dependencies...")
        
        # Try importing werkzeug
        try:
            import werkzeug
            logger.info("Werkzeug is installed")
        except ImportError:
            logger.warning("Werkzeug is not installed, installing now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "werkzeug==2.3.7"])
            logger.info("Werkzeug installed")
        
        # Check specific Flask dependencies
        try:
            import flask_cors
            logger.info("Flask-CORS is installed")
        except ImportError:
            logger.warning("Flask-CORS is not installed, installing now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask-cors==4.0.0"])
            logger.info("Flask-CORS installed")
        
        # Try importing other required packages
        packages_to_check = ["pandas", "numpy", "openai", "yfinance"]
        missing_packages = []
        
        for package in packages_to_check:
            try:
                __import__(package)
                logger.info(f"{package} is installed")
            except ImportError:
                logger.warning(f"{package} is not installed")
                missing_packages.append(package)
        
        if missing_packages:
            logger.warning(f"Installing missing packages: {', '.join(missing_packages)}")
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            logger.info("Installed missing packages")
            
        return True
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
        return False

def check_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_server_health(port=5001):
    """Check if the dual bot server is responsive."""
    try:
        response = requests.get(f"http://localhost:{port}/api/health", timeout=10)
        logger.info(f"Health check response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Health data: {data}")
            if data.get('status') == 'healthy':
                logger.info(f"Server on port {port} is healthy")
                return True
            else:
                logger.warning(f"Server on port {port} returned unexpected health status: {data}")
        else:
            logger.warning(f"Server on port {port} returned status code {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Error connecting to server on port {port}: {e}")
    return False

def kill_process_on_port(port):
    """Kill any process that's using the specified port."""
    logger.info(f"Attempting to kill existing process on port {port}...")
    
    try:
        # Find PID using port
        if sys.platform.startswith('win'):
            # Windows
            netstat_output = subprocess.check_output(
                f"netstat -ano | findstr :{port}", 
                shell=True
            ).decode().strip()
            
            if netstat_output:
                # Extract PID from netstat output
                for line in netstat_output.split('\n'):
                    if 'LISTENING' in line:
                        pid = line.strip().split()[-1]
                        logger.info(f"Found process with PID {pid} using port {port}. Killing...")
                        subprocess.call(f"taskkill /F /PID {pid}", shell=True)
                        time.sleep(2)  # Give some time for the process to terminate
                        return True
            else:
                logger.info(f"No process found using port {port}")
        else:
            # Linux/macOS
            try:
                pid_output = subprocess.check_output(
                    f"lsof -i :{port} -t", 
                    shell=True
                ).decode().strip()
                
                if pid_output:
                    pid = pid_output.split('\n')[0]
                    logger.info(f"Found process with PID {pid} using port {port}. Killing...")
                    subprocess.call(f"kill -9 {pid}", shell=True)
                    time.sleep(2)  # Give some time for the process to terminate
                    return True
                else:
                    logger.info(f"No process found using port {port}")
            except subprocess.CalledProcessError:
                logger.info(f"No process found using port {port}")
    except Exception as e:
        logger.error(f"Error killing process on port {port}: {e}")
    
    return False

def verify_dual_bot_server_file():
    """Verify that the dual_bot_api_server.py file exists."""
    if os.path.exists("dual_bot_api_server.py"):
        logger.info("dual_bot_api_server.py file found")
        return True
    else:
        logger.error("dual_bot_api_server.py file not found in the current directory")
        return False

def start_dual_bot_server_direct():
    """Start the dual bot server directly as a module import rather than subprocess."""
    logger.info("Starting dual bot server directly...")
    
    # Kill any existing process on port 5001
    if check_port_in_use(5001):
        logger.info("Port 5001 is in use. Killing existing process...")
        kill_process_on_port(5001)
        time.sleep(2)
    
    # Verify the file exists
    if not verify_dual_bot_server_file():
        return False
    
    try:
        # Create the data/dashboard directory
        os.makedirs('data/dashboard', exist_ok=True)
        logger.info("Created data/dashboard directory")
        
        # Start the server as a direct process
        # Get Python executable path (use the current interpreter)
        python_exe = sys.executable
        logger.info(f"Using Python interpreter: {python_exe}")
        
        # Run the server directly
        cmd = [python_exe, "dual_bot_api_server.py"]
        env = os.environ.copy()
        
        # Set Flask environment variables
        env["FLASK_APP"] = "dual_bot_api_server.py"
        env["FLASK_ENV"] = "development"
        env["FLASK_DEBUG"] = "1"
        
        logger.info(f"Starting dual_bot_api_server.py with command: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            env=env,
            shell=False
        )
        
        logger.info(f"Started dual bot server process with PID {process.pid}")
        
        # Wait for the server to start accepting connections
        wait_time = 15  # Wait for up to 15 seconds
        logger.info(f"Waiting {wait_time} seconds for server to start...")
        time.sleep(wait_time)
        
        # Check if the server is running
        if process.poll() is not None:
            logger.error(f"Server process exited with code {process.returncode}")
            return False
        
        logger.info("Dual bot server should now be running")
        return True
        
    except Exception as e:
        logger.error(f"Error starting dual bot server: {e}")
        return False

def test_key_endpoints():
    """Test key endpoints to verify they're working."""
    endpoints = ESSENTIAL_ENDPOINTS
    
    all_passed = True
    
    for endpoint in endpoints:
        try:
            url = f"http://localhost:5001{endpoint}"
            logger.info(f"Testing endpoint: {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"✅ Endpoint {endpoint} is working (status 200)")
            else:
                logger.warning(f"❌ Endpoint {endpoint} returned status {response.status_code}")
                all_passed = False
        except requests.RequestException as e:
            logger.error(f"❌ Error testing endpoint {endpoint}: {e}")
            all_passed = False
    
    return all_passed

def verify_frontend_api_config():
    """Verify that the frontend configuration files are using the correct API endpoints."""
    config_files = [
        'frontend/src/services/apiService.js',
        'frontend/src/services/dualBotService.js',
        'frontend/src/setupProxy.js'
    ]
    
    all_correct = True
    issues_found = []
    
    for file_path in config_files:
        if not os.path.exists(file_path):
            logger.warning(f"Frontend config file not found: {file_path}")
            issues_found.append(f"Missing file: {file_path}")
            all_correct = False
            continue
        
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                
                # Check for API URL and port
                if 'localhost:5001' not in content:
                    logger.warning(f"API server URL/port not found in {file_path}")
                    issues_found.append(f"Incorrect API URL in {file_path}")
                    all_correct = False
                
                # Check for essential endpoints in frontend config
                for endpoint in ['/api/health', '/api/status', '/api/dual-bot/status']:
                    endpoint_pattern = re.escape(endpoint)
                    if not re.search(endpoint_pattern, content):
                        logger.warning(f"Essential endpoint {endpoint} not found in {file_path}")
                        issues_found.append(f"Missing endpoint {endpoint} in {file_path}")
                        all_correct = False
        
        except Exception as e:
            logger.error(f"Error checking frontend config file {file_path}: {e}")
            issues_found.append(f"Error reading {file_path}: {str(e)}")
            all_correct = False
    
    if all_correct:
        logger.info("✅ Frontend API configuration looks correct")
    else:
        logger.warning("❌ Issues found in frontend API configuration:")
        for issue in issues_found:
            logger.warning(f"  - {issue}")
    
    return all_correct, issues_found

def main(use_new_window=False):
    """Main function to fix the dual bot API server."""
    logger.info("=" * 60)
    logger.info("Starting dual bot API server fix script")
    logger.info("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        logger.error("Failed to check and install dependencies. Please install them manually.")
        logger.error("Required packages: werkzeug==2.3.7, flask-cors, pandas, numpy, openai, yfinance")
        return False
    
    # Check if server is already running
    if check_port_in_use(5001):
        logger.info("Port 5001 is already in use. Checking server health...")
        
        # Check if the server is healthy
        if check_server_health():
            logger.info("Dual bot server is already running and healthy")
            return True
        else:
            logger.info("Dual bot server is not running or not healthy. Starting it...")
            
            # Kill any existing process on port 5001 that might be stuck
            kill_process_on_port(5001)
            time.sleep(2)  # Wait for the process to be killed
    else:
        logger.info("Dual bot server is not running or not healthy. Starting it...")
    
    # Start the dual bot server
    server_started = start_dual_bot_server_direct()
    
    if not server_started:
        logger.error("Failed to start dual bot API server.")
        return False
    
    # Verify the server is up and running
    time.sleep(5)  # Give the server some time to start up fully
    
    if check_server_health():
        logger.info("Dual bot API server has been started successfully!")
        return True
    else:
        logger.error("Server started but health check failed.")
        return False

if __name__ == "__main__":
    main() 