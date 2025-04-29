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

def check_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_server_health(port=5001):
    """Check if the dual bot server is responsive."""
    try:
        response = requests.get(f"http://localhost:{port}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
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

def start_dual_bot_server(use_new_window=True):
    """Start the dual bot server.
    
    Args:
        use_new_window (bool): Whether to use a new window/console for the server.
                              Set to False when using in a unified script.
    """
    logger.info("Attempting to start the dual bot server...")
    
    # Check if server is already running
    if check_port_in_use(5001):
        logger.info("Port 5001 is already in use. Checking server health...")
        if check_server_health(5001):
            logger.info("Dual bot server is already running and healthy.")
            return True
        else:
            logger.warning("Port 5001 is in use but server is not responding correctly.")
            # Kill the process on port 5001
            kill_process_on_port(5001)
    
    # Verify the file exists
    if not verify_dual_bot_server_file():
        return False
    
    try:
        # Get Python executable path (use the current interpreter)
        python_exe = sys.executable
        logger.info(f"Using Python interpreter: {python_exe}")
        
        # Start the server
        if use_new_window and sys.platform.startswith('win'):
            # Start in a new console window on Windows
            process = subprocess.Popen(
                [python_exe, "dual_bot_api_server.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=os.getcwd()  # Ensure working directory is correct
            )
        elif use_new_window and sys.platform.startswith('darwin'):
            # Start in a new terminal window on macOS
            process = subprocess.Popen(
                f"osascript -e 'tell app \"Terminal\" to do script \"cd {os.getcwd()} && {python_exe} dual_bot_api_server.py\"'",
                shell=True
            )
        else:
            # Start in background for Linux or when new window is not desired
            process = subprocess.Popen(
                [python_exe, "dual_bot_api_server.py"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                cwd=os.getcwd()  # Ensure working directory is correct
            )
        
        logger.info(f"Started dual bot server process with PID {process.pid}")
        
        # Wait for server to start
        max_attempts = 10
        for attempt in range(1, max_attempts + 1):
            time.sleep(2)
            if check_port_in_use(5001):
                logger.info(f"Port 5001 is in use after {attempt * 2} seconds")
                
                # Check if the server is actually working
                if check_server_health(5001):
                    logger.info("Dual bot server started successfully!")
                    return True
            
            logger.info(f"Waiting for server to start (attempt {attempt}/{max_attempts})...")
        
        logger.error(f"Failed to confirm dual bot server is running after {max_attempts * 2} seconds")
        return False
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

def main(use_new_window=True):
    """Main function to fix the dual bot API server.
    
    Args:
        use_new_window (bool): Whether to use a new window for the server process.
                              Set to False when called from a unified script.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    logger.info("=" * 60)
    logger.info("Starting dual bot API server fix script")
    logger.info("=" * 60)
    
    # Step 1: Check if the dual bot server is running and healthy
    if check_port_in_use(5001) and check_server_health(5001):
        logger.info("Dual bot server is already running and healthy")
    else:
        # Step 2: Start or restart the server if it's not running or not healthy
        logger.info("Dual bot server is not running or not healthy. Starting it...")
        if start_dual_bot_server(use_new_window):
            logger.info("Successfully started the dual bot server")
        else:
            logger.error("Failed to start the dual bot server. Please check the logs for details.")
            return False
    
    # Step 3: Test key endpoints to make sure they're working
    logger.info("Testing key endpoints...")
    if test_key_endpoints():
        logger.info("All endpoints are working correctly!")
    else:
        logger.warning("Some endpoints failed the test. The API server is running but might have issues.")
    
    # Step 4: Verify frontend configuration
    logger.info("Verifying frontend API configuration...")
    config_correct, issues = verify_frontend_api_config()
    
    if not config_correct:
        logger.warning("Frontend configuration has issues that need to be addressed.")
    
    logger.info("Dual bot API server fix script completed")
    return True

if __name__ == "__main__":
    # Check if running as part of unified script
    use_new_window = True
    if len(sys.argv) > 1 and sys.argv[1] == "--no-window":
        use_new_window = False
    
    success = main(use_new_window)
    sys.exit(0 if success else 1) 