#!/usr/bin/env python
"""
Unified Server Startup Script for AI Trading Bot
==============================================

This script starts all necessary components:
1. API Server (simple_api_server.py)
2. Bot Management Server (simple_bot_management_server.py) - if available
3. TradingView Server (tradingview_server.py) - if available
4. Frontend Application

Features:
- Single command to start all components
- Automatic directory creation
- Error handling with detailed logs
- Health checks for server components
- Graceful shutdown with Ctrl+C
- Render deployment support
"""

import os
import sys
import subprocess
import time
import logging
import signal
import socket
import platform
import importlib
import json
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server_startup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("server_startup")

# Constants
BASE_DIR = Path(__file__).resolve().parent
API_PORT = int(os.environ.get("PORT", 5001))  # Use PORT env var if set (for Render)
BOT_MANAGEMENT_PORT = 5002
TRADINGVIEW_PORT = 5003
FRONTEND_PORT = 3001
IS_WINDOWS = platform.system() == "Windows"
IS_RENDER = os.environ.get("RENDER_DEPLOYMENT", "false").lower() == "true"

# Dictionary to track running processes
running_processes = {}

def check_and_install_dependencies():
    """Check and install critical dependencies."""
    logger.info("Checking critical dependencies...")
    
    # Required packages and their compatibility versions
    required_packages = {
        "flask": "2.0.1",  # Specific version for compatibility
        "flask-cors": "3.0.10",
        "werkzeug": "2.0.1",  # Must match Flask version
        "markupsafe": "2.0.1",
        "jinja2": "3.0.3",
        "itsdangerous": "2.0.1",
        "python-dotenv": "1.0.0"
    }
    
    # Check if python-dotenv is installed for loading .env files
    try:
        import dotenv
        logger.info("Loading environment variables from .env file")
        dotenv.load_dotenv()
    except ImportError:
        logger.warning("python-dotenv is not installed. Will install it now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv==1.0.0"])
            import dotenv
            dotenv.load_dotenv()
            logger.info("Successfully installed python-dotenv and loaded .env file")
        except Exception as e:
            logger.error(f"Failed to install python-dotenv: {e}")
    
    # Collect missing packages
    missing_packages = []
    
    for package, version in required_packages.items():
        package_module = package.replace('-', '_')
        try:
            importlib.import_module(package_module)
        except ImportError:
            missing_packages.append(f"{package}=={version}")
    
    # Install missing packages
    if missing_packages:
        logger.warning(f"Missing Python packages: {', '.join(p.split('==')[0] for p in missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            logger.info("Successfully installed missing Python packages")
        except Exception as e:
            logger.error(f"Failed to install missing packages: {e}")
            return False
    
    return True

def create_required_directories():
    """Create required directories for the application."""
    directories = [
        "data",
        "data/dashboard",
        "data/broker",
        "data/logs",
        "data/signals",
        "data/market_data",
        "instance"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    return True

def create_sample_data():
    """Create sample data files if they don't exist."""
    # Create bot status file
    if not os.path.exists('bot_status.json'):
        bot_status = {
            "status": "ready",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "active_strategies": 3,
            "trades_today": 0
        }
        with open('bot_status.json', 'w') as f:
            json.dump(bot_status, f, indent=2)
        logger.info("Created sample bot_status.json")
    
    # Create signals file directory
    signals_dir = os.path.join('data', 'signals')
    os.makedirs(signals_dir, exist_ok=True)
    
    # Create latest signals file if it doesn't exist
    signals_file = os.path.join(signals_dir, 'latest_signals.json')
    if not os.path.exists(signals_file):
        signals = {
            "signals": [
                {
                    "id": "sig_001",
                    "symbol": "AAPL",
                    "signal_type": "buy",
                    "confidence": 0.85,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            ]
        }
        with open(signals_file, 'w') as f:
            json.dump(signals, f, indent=2)
        logger.info(f"Created sample signals file: {signals_file}")

def check_port_available(port):
    """Check if a port is available (not in use)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except socket.error:
            return False

def kill_process_on_port(port):
    """Kill any process using the specified port."""
    try:
        if IS_WINDOWS:
            # On Windows
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
            for line in output.split('\n'):
                if 'LISTENING' in line:
                    pid = line.strip().split()[-1]
                    logger.info(f"Killing process {pid} using port {port}")
                    subprocess.check_output(f"taskkill /F /PID {pid}", shell=True)
                    return True
        else:
            # On Unix-like systems
            output = subprocess.check_output(f"lsof -i :{port} -t", shell=True).decode()
            pid = output.strip()
            if pid:
                logger.info(f"Killing process {pid} using port {port}")
                subprocess.check_output(f"kill -9 {pid}", shell=True)
                return True
    except subprocess.CalledProcessError:
        # No process found using this port
        pass
    return False

def check_server_health(url, max_attempts=3, wait_time=5):
    """Check if a server is healthy by making requests to its health endpoint."""
    import requests
    from urllib3.exceptions import MaxRetryError
    
    for attempt in range(1, max_attempts + 1):
        logger.info(f"Health check attempt {attempt}/{max_attempts} for {url}")
        try:
            response = requests.get(url, timeout=4)
            if response.status_code == 200:
                logger.info(f"Health check successful: {url}")
                return True
            else:
                logger.warning(f"Health check returned status code {response.status_code}: {url}")
        except (requests.RequestException, MaxRetryError) as e:
            logger.warning(f"Health check failed: {e}")
        
        if attempt < max_attempts:
            logger.info(f"Waiting {wait_time} seconds before next attempt...")
            time.sleep(wait_time)
    
    logger.error(f"Health check failed after {max_attempts} attempts for {url}")
    return False

def start_api_server():
    """Start the API server."""
    logger.info(f"Starting API server on port {API_PORT}...")
    
    # On Render, we don't need to start the API server separately
    if IS_RENDER:
        logger.info("Running on Render - API server will be started by Render itself")
        return None
    
    # Check if port is available, kill process if needed
    if not check_port_available(API_PORT):
        logger.warning(f"Port {API_PORT} is already in use")
        user_input = input(f"Do you want to kill the process using port {API_PORT}? (y/n): ")
        if user_input.lower() == 'y':
            kill_process_on_port(API_PORT)
            time.sleep(2)  # Wait for the process to terminate
        else:
            logger.error(f"Cannot start API server on port {API_PORT}")
            return None
    
    # Create required directories
    create_required_directories()
    
    # Ensure sample data exists
    create_sample_data()
    
    # First, try using the fix-dual-bot-api.py if available
    if os.path.exists("fix-dual-bot-api.py"):
        logger.info("Using fix-dual-bot-api.py to start the Dual Bot API Server")
        try:
            subprocess.run(
                [sys.executable, "fix-dual-bot-api.py"],
                check=True,
                timeout=180  # Allow longer timeout
            )
            
            # Check if the server is running
            health_url = f"http://localhost:{API_PORT}/api/health"
            if check_server_health(health_url):
                logger.info("Dual Bot API Server started successfully")
                # Return a placeholder process since the actual process is managed by fix-dual-bot-api.py
                running_processes['dual_bot_api'] = True
                return {'pid': 'managed_externally'}
            else:
                logger.error("Failed to start Dual Bot API Server")
        except (subprocess.SubprocessError, Exception) as e:
            logger.error(f"Fix script error: {e}")
    
    # If the fix script failed or doesn't exist, try direct approach
    logger.warning("Fix script didn't start the server properly. Attempting direct start...")
    
    # Choose the API server script
    api_script = "simple_api_server.py"
    if not os.path.exists(api_script):
        logger.warning(f"{api_script} not found, trying alternative scripts...")
        alternatives = ["dual_bot_api_server.py", "minimal_flask_server.py"]
        for alt in alternatives:
            if os.path.exists(alt):
                api_script = alt
                logger.info(f"Using alternative API script: {api_script}")
                break
        else:
            logger.error("No suitable API server script found")
            return None
    
    logger.info(f"Starting Dual Bot API Server directly")
    
    # Set environment variables
    env = os.environ.copy()
    env["FLASK_APP"] = api_script
    env["FLASK_ENV"] = "development"
    env["FLASK_DEBUG"] = "1"
    
    # Start the server
    cmd = [sys.executable, api_script]
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"API server process started with PID: {process.pid}")
        logger.info("Waiting for Dual Bot API Server to start...")
        
        # Wait a bit to see if the server starts correctly
        time.sleep(10)
        
        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            logger.error(f"API server process terminated with code: {process.returncode}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return None
        
        # Check if the server is accessible
        health_url = f"http://localhost:{API_PORT}/api/health"
        if check_server_health(health_url):
            logger.info("API server is running and healthy!")
        else:
            logger.warning("API server is running but health check failed!")
            
        return process
    
    except Exception as e:
        logger.error(f"Error starting API server: {e}")
        return None

def start_bot_management_server():
    """Start the Bot Management Server if available."""
    logger.info(f"Starting Bot Management Server on port {BOT_MANAGEMENT_PORT}...")
    
    # Skip on Render deployment
    if IS_RENDER:
        logger.info("Running on Render - skipping Bot Management Server")
        return None
    
    bot_mgmt_script = "simple_bot_management_server.py"
    if not os.path.exists(bot_mgmt_script):
        logger.warning(f"{bot_mgmt_script} not found, skipping Bot Management Server")
        return None
    
    # Check if port is available
    if not check_port_available(BOT_MANAGEMENT_PORT):
        logger.warning(f"Port {BOT_MANAGEMENT_PORT} is already in use")
        user_input = input(f"Do you want to kill the process using port {BOT_MANAGEMENT_PORT}? (y/n): ")
        if user_input.lower() == 'y':
            kill_process_on_port(BOT_MANAGEMENT_PORT)
        else:
            logger.error(f"Cannot start Bot Management Server on port {BOT_MANAGEMENT_PORT}")
            return None
    
    # Set environment variables
    env = os.environ.copy()
    env["BOT_MANAGEMENT_PORT"] = str(BOT_MANAGEMENT_PORT)
    
    # Start the server
    cmd = [sys.executable, bot_mgmt_script]
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"Bot Management Server process started with PID: {process.pid}")
        
        # Wait a bit to see if the server starts correctly
        time.sleep(5)
        
        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            logger.error(f"Bot Management Server process terminated with code: {process.returncode}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return None
        
        logger.info("Bot Management Server is running!")
        return process
    
    except Exception as e:
        logger.error(f"Error starting Bot Management Server: {e}")
        return None

def start_tradingview_server():
    """Start the TradingView Server if available."""
    logger.info(f"Starting TradingView Server on port {TRADINGVIEW_PORT}...")
    
    # Skip on Render deployment
    if IS_RENDER:
        logger.info("Running on Render - skipping TradingView Server")
        return None
    
    tv_script = "tradingview_server.py"
    if not os.path.exists(tv_script):
        logger.warning(f"{tv_script} not found, skipping TradingView Server")
        return None
    
    # Check if port is available
    if not check_port_available(TRADINGVIEW_PORT):
        logger.warning(f"Port {TRADINGVIEW_PORT} is already in use")
        user_input = input(f"Do you want to kill the process using port {TRADINGVIEW_PORT}? (y/n): ")
        if user_input.lower() == 'y':
            kill_process_on_port(TRADINGVIEW_PORT)
        else:
            logger.error(f"Cannot start TradingView Server on port {TRADINGVIEW_PORT}")
            return None
    
    # Set environment variables
    env = os.environ.copy()
    env["TRADINGVIEW_PORT"] = str(TRADINGVIEW_PORT)
    
    # Start the server
    cmd = [sys.executable, tv_script]
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"TradingView Server process started with PID: {process.pid}")
        
        # Wait a bit to see if the server starts correctly
        time.sleep(5)
        
        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            logger.error(f"TradingView Server process terminated with code: {process.returncode}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return None
        
        logger.info("TradingView Server is running!")
        return process
    
    except Exception as e:
        logger.error(f"Error starting TradingView Server: {e}")
        return None

def start_frontend():
    """Start the frontend application."""
    logger.info(f"Starting frontend on port {FRONTEND_PORT}...")
    
    # Skip on Render deployment
    if IS_RENDER:
        logger.info("Running on Render - skipping frontend startup")
        return None
    
    frontend_dir = os.path.join(BASE_DIR, "frontend")
    
    if not os.path.exists(frontend_dir):
        logger.error(f"Frontend directory not found: {frontend_dir}")
        return None
    
    if not os.path.exists(os.path.join(frontend_dir, "package.json")):
        logger.error(f"package.json not found in frontend directory")
        return None
    
    # Check if port is available
    if not check_port_available(FRONTEND_PORT):
        logger.warning(f"Port {FRONTEND_PORT} is already in use")
        user_input = input(f"Do you want to kill the process using port {FRONTEND_PORT}? (y/n): ")
        if user_input.lower() == 'y':
            kill_process_on_port(FRONTEND_PORT)
        else:
            logger.error(f"Cannot start frontend on port {FRONTEND_PORT}")
            return None
    
    try:
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Set environment variables
        env = os.environ.copy()
        env["PORT"] = str(FRONTEND_PORT)
        
        # Start the frontend
        cmd = ["npm", "start"]
        logger.info(f"Running command: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            env=env,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Change back to original directory
        os.chdir(BASE_DIR)
        
        logger.info(f"Frontend process started with PID: {process.pid}")
        
        # Wait a bit to see if the frontend starts correctly
        time.sleep(10)
        
        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            logger.error(f"Frontend process terminated with code: {process.returncode}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return None
        
        logger.info("Frontend is running!")
        return process
    
    except Exception as e:
        logger.error(f"Error starting frontend: {e}")
        # Change back to original directory
        os.chdir(BASE_DIR)
        return None

def terminate_process(process):
    """Terminate a process gracefully."""
    if process is None:
        return
    
    try:
        logger.info(f"Terminating process with PID: {process.pid}")
        process.terminate()
        
        # Wait for process to terminate gracefully
        for _ in range(5):
            if process.poll() is not None:
                logger.info(f"Process terminated with code: {process.returncode}")
                return
            time.sleep(1)
        
        # If process is still running, kill it
        logger.warning(f"Process with PID {process.pid} didn't terminate gracefully, killing it...")
        if IS_WINDOWS:
            process.kill()
        else:
            os.kill(process.pid, signal.SIGKILL)
        
        logger.info(f"Process killed")
    except Exception as e:
        logger.error(f"Error terminating process: {e}")

def cleanup_processes():
    """Clean up all running processes."""
    logger.info("Cleaning up processes...")
    
    for name, process in running_processes.items():
        if process:
            logger.info(f"Terminating {name}...")
            if isinstance(process, dict) and process.get('pid') == 'managed_externally':
                # This is a process managed by another script, try to kill by port
                if name == 'dual_bot_api':
                    kill_process_on_port(API_PORT)
                elif name == 'bot_management':
                    kill_process_on_port(BOT_MANAGEMENT_PORT)
                elif name == 'tradingview':
                    kill_process_on_port(TRADINGVIEW_PORT)
                elif name == 'frontend':
                    kill_process_on_port(FRONTEND_PORT)
            elif hasattr(process, 'terminate'):
                try:
                    # Normal process object
                    process.terminate()
                    process.wait(timeout=5)
                except (subprocess.TimeoutExpired, Exception) as e:
                    logger.warning(f"Error terminating {name}: {e}")
                    try:
                        # Force kill if terminate doesn't work
                        if hasattr(process, 'kill'):
                            process.kill()
                    except Exception:
                        pass
    
    # Additional cleanup: Check and kill processes on the ports we use
    ports_to_check = [API_PORT, BOT_MANAGEMENT_PORT, TRADINGVIEW_PORT, FRONTEND_PORT]
    for port in ports_to_check:
        kill_process_on_port(port)
    
    running_processes.clear()

def handle_interrupt(signum, frame):
    """Handle interrupt signal (Ctrl+C)."""
    print("\n")
    logger.info("Interrupt received, shutting down...")
    
    cleanup_processes()
    
    logger.info("All servers have been stopped. Exiting.")
    sys.exit(0)

def start_render_deployment():
    """Configure the application for Render deployment."""
    logger.info("Starting in Render deployment mode")
    
    # Create required directories
    create_required_directories()
    
    # For Render, we don't start services ourselves
    # We just ensure directories exist and configs are correct
    logger.info("Setting up Render deployment environment")
    
    # Copy frontend build to static directory if it exists
    frontend_build = os.path.join(BASE_DIR, "frontend", "build")
    static_dir = os.path.join(BASE_DIR, "static")
    
    if os.path.exists(frontend_build) and os.path.isdir(static_dir):
        logger.info("Copying frontend build to static directory...")
        subprocess.run(f"cp -r {frontend_build}/* {static_dir}/", shell=True)
    
    logger.info("Render deployment setup complete")
    return True

def main():
    """Main function to start all components."""
    try:
        logger.info("Starting AI Trading Bot...")
        
        # Check if .env file exists and load it
        if os.path.exists(".env"):
            logger.info("Loading environment variables from %s", os.path.abspath(".env"))
            try:
                import dotenv
                dotenv.load_dotenv()
            except ImportError:
                logger.warning("python-dotenv is not installed, environment variables from .env won't be loaded")
        
        # Check and install dependencies
        if not check_and_install_dependencies():
            logger.error("Failed to install required dependencies. Please fix manually.")
            return
        
        # Check if Node.js is installed
        node_installed = False
        try:
            node_version = subprocess.check_output(["node", "--version"], text=True).strip()
            logger.info(f"Node.js version: {node_version}")
            node_installed = True
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("Node.js is not installed or not in PATH")
        
        # Check if npm is installed (needed for frontend)
        npm_installed = False
        if node_installed:
            try:
                subprocess.check_output(["npm", "--version"], text=True)
                npm_installed = True
            except (subprocess.SubprocessError, FileNotFoundError):
                logger.error("npm is not installed or not in PATH")
        
        if not node_installed or not npm_installed:
            logger.warning("Issues with Node.js dependencies. Frontend may not work properly.")
        
        # For Render deployments, use special handling
        if IS_RENDER:
            logger.info("Starting Render deployment...")
            start_render_deployment()
            return
        
        # Kill existing processes on ports if needed (automated for non-interactive use)
        ports_to_check = [API_PORT, BOT_MANAGEMENT_PORT, TRADINGVIEW_PORT, FRONTEND_PORT]
        for port in ports_to_check:
            if not check_port_available(port):
                logger.info(f"Automatically killing process on port {port}")
                kill_process_on_port(port)
                time.sleep(1)
        
        # Create directories
        create_required_directories()
        
        # Create sample data
        create_sample_data()
        
        # First, try starting the Dual Bot API Server using fix-dual-bot-api.py
        dual_bot_started = False
        if os.path.exists("fix-dual-bot-api.py") and os.path.exists("dual_bot_api_server.py"):
            logger.info("Starting Dual Bot API Server...")
            try:
                subprocess.run(
                    [sys.executable, "fix-dual-bot-api.py"],
                    check=True,
                    timeout=180  # Allow longer timeout
                )
                
                # Check if the server is running
                health_url = f"http://localhost:{API_PORT}/api/health"
                if check_server_health(health_url):
                    logger.info("Dual Bot API Server started successfully")
                    dual_bot_started = True
                else:
                    logger.warning("Dual Bot API Server health check failed")
            except (subprocess.SubprocessError, Exception) as e:
                logger.error(f"Failed to start Dual Bot API Server using fix script: {e}")
                
        # If Dual Bot API Server didn't start, try traditional API server
        if not dual_bot_started:
            running_processes['api_server'] = start_api_server()
            if not running_processes['api_server']:
                logger.error("Failed to start API server. Exiting.")
                return
        
        # Start Bot Management Server
        running_processes['bot_management'] = start_bot_management_server()
        if running_processes['bot_management']:
            logger.info("Bot Management Server started successfully")
        
        # Start TradingView Integration Server
        running_processes['tradingview'] = start_tradingview_server()
        if running_processes['tradingview']:
            logger.info("TradingView Integration Server started successfully")
        
        # Start Frontend Application
        running_processes['frontend'] = start_frontend()
        if running_processes['frontend']:
            logger.info(f"Frontend should be available at http://localhost:{FRONTEND_PORT}")
        
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, handle_interrupt)
        signal.signal(signal.SIGTERM, handle_interrupt)
        
        logger.info("All components started successfully.")
        logger.info("Press Ctrl+C to stop all servers and exit.")
        
        # Keep the process running - cross-platform solution
        # Instead of signal.pause() which only works on Unix
        print("\nAll servers are now running! Press Ctrl+C to stop...\n")
        try:
            # Simple loop that keeps the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # This will be caught by our signal handler
            pass
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        # Clean up processes on error
        cleanup_processes()

if __name__ == "__main__":
    main() 