#!/usr/bin/env python
"""
Unified Server Startup Script for AI Trading Bot
=============================================

This script orchestrates the startup of all required services for the trading bot system:
1. Dual Bot API Server (main backend API)
2. Bot Management Server (for trading bot status and control)
3. TradingView Integration Server (for TradingView webhook alerts)
4. Frontend Application (React)

Features:
- Environment variable loading
- Dependency checks
- Health checks for all services
- Proper startup order based on dependencies
- Error handling and logging
"""

import os
import sys
import subprocess
import time
import logging
import signal
import json
import platform
import threading
import requests
from pathlib import Path
from datetime import datetime
import importlib
import shutil
from typing import Dict, List, Optional, Union, Tuple, Any

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

# Global variables
running_processes = {}
IS_WINDOWS = platform.system() == "Windows"
BASE_DIR = Path(__file__).resolve().parent

# PORT CONFIGURATION
DUAL_BOT_API_PORT = 5001
BOT_MANAGEMENT_PORT = 5002
TRADINGVIEW_PORT = 5003
FRONTEND_PORT = 3001

# HEALTH CHECK ENDPOINTS
DUAL_BOT_API_HEALTH = f"http://localhost:{DUAL_BOT_API_PORT}/api/health"
BOT_MANAGEMENT_HEALTH = f"http://localhost:{BOT_MANAGEMENT_PORT}/api/health"
TRADINGVIEW_HEALTH = f"http://localhost:{TRADINGVIEW_PORT}/api/test"
FRONTEND_HEALTH = f"http://localhost:{FRONTEND_PORT}"

# Required Python packages
REQUIRED_PACKAGES = [
    "flask",
    "flask-cors",
    "requests",
    "python-dotenv",
    "datetime",
    "pandas",
    "numpy",
    "yfinance"
]

# Required Node packages
REQUIRED_NODE_PACKAGES = [
    "react",
    "react-dom",
    "axios",
    "react-router-dom",
    "@mui/material",
    "@mui/icons-material"
]

def load_environment_variables():
    """Load environment variables from .env file"""
    try:
        from dotenv import load_dotenv
        env_file = os.path.join(BASE_DIR, '.env')
        
        if os.path.exists(env_file):
            logger.info(f"Loading environment variables from {env_file}")
            load_dotenv(env_file)
            return True
        else:
            # Try to copy the .env.example to .env if it exists
            env_example = os.path.join(BASE_DIR, '.env.example')
            if os.path.exists(env_example):
                logger.warning(f".env file not found. Creating from .env.example")
                shutil.copy(env_example, env_file)
                load_dotenv(env_file)
                logger.info(f"Created .env file from example. Please edit it with your actual API keys.")
                return True
            else:
                logger.error("No .env or .env.example file found. Environment variables not loaded.")
                return False
    except ImportError:
        logger.error("python-dotenv package not installed. Environment variables not loaded.")
        return False
    except Exception as e:
        logger.error(f"Error loading environment variables: {str(e)}")
        return False

def check_python_dependencies():
    """Check if required Python packages are installed"""
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package.split('==')[0])
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"Missing Python packages: {', '.join(missing_packages)}")
        
        # Ask user if they want to install missing packages
        user_input = input(f"Would you like to install missing packages? (y/n): ")
        if user_input.lower() in ['y', 'yes']:
            try:
                install_cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
                subprocess.run(install_cmd, check=True)
                logger.info("Successfully installed missing Python packages")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Error installing packages: {str(e)}")
                return False
        else:
            logger.warning("Missing packages not installed. Some features may not work.")
            return False
    
    return True

def check_node_dependencies():
    """Check if Node.js and npm are installed and frontend dependencies exist"""
    # Check if Node.js is installed
    try:
        node_version = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            text=True,
            check=True
        )
        logger.info(f"Node.js version: {node_version.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Node.js is not installed or not in PATH")
        return False
    
    # Check if npm is installed
    try:
        npm_version = subprocess.run(
            ["npm", "--version"], 
            capture_output=True, 
            text=True,
            check=True
        )
        logger.info(f"npm version: {npm_version.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("npm is not installed or not in PATH")
        return False
    
    # Check if frontend dependencies are installed
    frontend_dir = os.path.join(BASE_DIR, "frontend")
    node_modules = os.path.join(frontend_dir, "node_modules")
    package_json = os.path.join(frontend_dir, "package.json")
    
    if not os.path.exists(frontend_dir):
        logger.error(f"Frontend directory not found at {frontend_dir}")
        return False
    
    if not os.path.exists(package_json):
        logger.error(f"package.json not found in frontend directory")
        return False
    
    if not os.path.exists(node_modules):
        logger.warning("Node modules not installed in frontend directory")
        
        # Ask user if they want to install frontend dependencies
        user_input = input("Would you like to install frontend dependencies? (y/n): ")
        if user_input.lower() in ['y', 'yes']:
            try:
                # Change to frontend directory and run npm install
                os.chdir(frontend_dir)
                subprocess.run(["npm", "install"], check=True)
                os.chdir(BASE_DIR)  # Change back to original directory
                logger.info("Successfully installed frontend dependencies")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Error installing frontend dependencies: {str(e)}")
                os.chdir(BASE_DIR)  # Make sure we change back to original directory
                return False
        else:
            logger.warning("Frontend dependencies not installed. Frontend may not work properly.")
            return False
    
    return True

def check_port_availability(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    available = True
    
    try:
        sock.bind(('localhost', port))
    except socket.error:
        available = False
    finally:
        sock.close()
    
    return available

def health_check(url, max_retries=5, delay=2):
    """Check if a service is healthy by making a request to its health endpoint"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Health check attempt {attempt+1}/{max_retries} for {url}")
            response = requests.get(url, timeout=10)  # Increased timeout
            if response.status_code in [200, 201]:
                logger.info(f"Health check successful: {url} returned {response.status_code}")
                return True
            else:
                logger.warning(f"Health check returned status code {response.status_code} for {url}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Health check failed: {str(e)}")
        
        logger.info(f"Waiting {delay} seconds before next attempt...")
        time.sleep(delay)
    
    logger.error(f"Health check failed after {max_retries} attempts for {url}")
    return False

def start_dual_bot_api_server():
    """Start the Dual Bot API Server"""
    logger.info("Starting Dual Bot API Server...")
    
    if not check_port_availability(DUAL_BOT_API_PORT):
        logger.error(f"Port {DUAL_BOT_API_PORT} is already in use. Cannot start Dual Bot API Server.")
        return False
    
    # Check if fix script exists, use it if available
    fix_script = os.path.join(BASE_DIR, "fix-dual-bot-api.py")
    dual_bot_server = os.path.join(BASE_DIR, "dual_bot_api_server.py")
    
    if os.path.exists(fix_script):
        logger.info("Using fix-dual-bot-api.py to start the Dual Bot API Server")
        try:
            # Run the fix script and wait for it to complete
            result = subprocess.run(
                [sys.executable, fix_script],
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit code
            )
            
            # Log output from fix script
            if result.stdout:
                for line in result.stdout.splitlines():
                    logger.info(f"Fix script: {line}")
            
            if result.stderr:
                for line in result.stderr.splitlines():
                    logger.error(f"Fix script error: {line}")
            
            # Check if the process was successful
            if result.returncode != 0:
                logger.error(f"Fix script exited with code {result.returncode}")
            
            # Give the server some extra time to start fully
            time.sleep(10)
            
            # Now let's verify the server is running with a more robust check
            if health_check(DUAL_BOT_API_HEALTH, max_retries=3, delay=5):
                logger.info("Dual Bot API Server started successfully (via fix script)")
                running_processes["dual_bot_api"] = None  # We don't have a process handle when using fix script
                return True
            else:
                # Start it directly as a fallback
                logger.warning("Fix script didn't start the server properly. Attempting direct start...")
        except Exception as e:
            logger.error(f"Error running fix script: {str(e)}")
            logger.warning("Falling back to direct server start...")
    
    # Direct start as fallback or if fix script doesn't exist
    try:
        logger.info("Starting Dual Bot API Server directly")
        
        # Create directory for data/dashboard if it doesn't exist
        os.makedirs(os.path.join(BASE_DIR, 'data', 'dashboard'), exist_ok=True)
        
        # Set environment variables
        env = os.environ.copy()
        env["FLASK_APP"] = "dual_bot_api_server.py"
        env["FLASK_ENV"] = "development"
        env["FLASK_DEBUG"] = "1"
        
        # Start the server
        cmd = [sys.executable, dual_bot_server]
        
        # Start the server process
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        running_processes["dual_bot_api"] = process
        
        # Give the server some time to start
        logger.info("Waiting for Dual Bot API Server to start...")
        time.sleep(10)
        
        # Check if the server started successfully
        if health_check(DUAL_BOT_API_HEALTH, max_retries=3, delay=5):
            logger.info("Dual Bot API Server started successfully (direct start)")
            return True
        else:
            logger.error("Failed to start Dual Bot API Server")
            terminate_process(process)
            return False
            
    except Exception as e:
        logger.error(f"Error starting Dual Bot API Server: {str(e)}")
        return False

def start_bot_management_server():
    """Start the Bot Management Server"""
    logger.info("Starting Bot Management Server...")
    
    if not check_port_availability(BOT_MANAGEMENT_PORT):
        logger.error(f"Port {BOT_MANAGEMENT_PORT} is already in use. Cannot start Bot Management Server.")
        return False
    
    bot_server = os.path.join(BASE_DIR, "simple_bot_management_server.py")
    
    if not os.path.exists(bot_server):
        logger.error("Bot Management Server script not found")
        return False
    
    try:
        # Set environment variable for the port
        env = os.environ.copy()
        env["BOT_MANAGEMENT_PORT"] = str(BOT_MANAGEMENT_PORT)
        
        # Start the server
        cmd = [sys.executable, bot_server]
        
        if IS_WINDOWS:
            process = subprocess.Popen(cmd, env=env)
        else:
            process = subprocess.Popen(cmd, env=env)
        
        running_processes["bot_management"] = process
        
        # Check if the server started successfully
        if health_check(BOT_MANAGEMENT_HEALTH):
            logger.info("Bot Management Server started successfully")
            return True
        else:
            logger.error("Failed to start Bot Management Server")
            terminate_process(process)
            return False
            
    except Exception as e:
        logger.error(f"Error starting Bot Management Server: {str(e)}")
        return False

def start_tradingview_server():
    """Start the TradingView Integration Server"""
    logger.info("Starting TradingView Integration Server...")
    
    if not check_port_availability(TRADINGVIEW_PORT):
        logger.error(f"Port {TRADINGVIEW_PORT} is already in use. Cannot start TradingView Integration Server.")
        return False
    
    tradingview_server = os.path.join(BASE_DIR, "tradingview_server.py")
    
    if not os.path.exists(tradingview_server):
        logger.error("TradingView Integration Server script not found")
        return False
    
    try:
        # Set environment variable for the port
        env = os.environ.copy()
        env["TRADINGVIEW_PORT"] = str(TRADINGVIEW_PORT)
        
        # Start the server
        cmd = [sys.executable, tradingview_server]
        
        if IS_WINDOWS:
            process = subprocess.Popen(cmd, env=env)
        else:
            process = subprocess.Popen(cmd, env=env)
        
        running_processes["tradingview"] = process
        
        # Check if the server started successfully
        if health_check(TRADINGVIEW_HEALTH):
            logger.info("TradingView Integration Server started successfully")
            return True
        else:
            logger.error("Failed to start TradingView Integration Server")
            terminate_process(process)
            return False
            
    except Exception as e:
        logger.error(f"Error starting TradingView Integration Server: {str(e)}")
        return False

def start_frontend():
    """Start the Frontend Application"""
    logger.info("Starting Frontend Application...")
    
    if not check_port_availability(FRONTEND_PORT):
        logger.error(f"Port {FRONTEND_PORT} is already in use. Cannot start Frontend Application.")
        return False
    
    frontend_dir = os.path.join(BASE_DIR, "frontend")
    
    if not os.path.exists(frontend_dir):
        logger.error("Frontend directory not found")
        return False
    
    if not os.path.exists(os.path.join(frontend_dir, "package.json")):
        logger.error("package.json not found in frontend directory")
        return False
    
    try:
        # Set environment variable for the port
        env = os.environ.copy()
        env["PORT"] = str(FRONTEND_PORT)
        
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Start the frontend
        if IS_WINDOWS:
            cmd = ["npm", "start"]
            process = subprocess.Popen(cmd, env=env, shell=True)
        else:
            cmd = ["npm", "start"]
            process = subprocess.Popen(cmd, env=env)
        
        # Change back to original directory
        os.chdir(BASE_DIR)
        
        running_processes["frontend"] = process
        
        # Give it some time to start
        time.sleep(10)
        
        # Check if the frontend started successfully
        # Note: Frontend health check is not as reliable as backend health checks
        logger.info(f"Frontend should be available at http://localhost:{FRONTEND_PORT}")
        
        return True
            
    except Exception as e:
        logger.error(f"Error starting Frontend: {str(e)}")
        os.chdir(BASE_DIR)  # Make sure we change back to original directory
        return False

def terminate_process(process):
    """Terminate a process"""
    if process is None:
        return
    
    try:
        if IS_WINDOWS:
            process.terminate()
        else:
            process.terminate()
            
        # Wait for process to terminate
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        # If process doesn't terminate gracefully, kill it
        if IS_WINDOWS:
            process.kill()
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except Exception as e:
        logger.error(f"Error terminating process: {str(e)}")

def cleanup_processes():
    """Clean up all running processes"""
    logger.info("Cleaning up processes...")
    
    for name, process in running_processes.items():
        logger.info(f"Terminating {name}...")
        terminate_process(process)
    
    running_processes.clear()

def handle_interrupt(signal, frame):
    """Handle Ctrl+C by cleaning up processes and exiting"""
    logger.info("Interrupt received. Shutting down...")
    cleanup_processes()
    sys.exit(0)

def main():
    """Main function to start all servers"""
    print("\n" + "="*50)
    print("      AI TRADING BOT - UNIFIED SERVER STARTER")
    print("="*50 + "\n")
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, handle_interrupt)
    
    # Load environment variables
    if not load_environment_variables():
        logger.warning("Continuing without environment variables")
    
    # Check dependencies
    python_deps_ok = check_python_dependencies()
    node_deps_ok = check_node_dependencies()
    
    if not python_deps_ok:
        logger.error("Missing required Python dependencies. Please install them and try again.")
        sys.exit(1)
    
    if not node_deps_ok:
        logger.warning("Issues with Node.js dependencies. Frontend may not work properly.")
        user_input = input("Continue anyway? (y/n): ")
        if user_input.lower() not in ['y', 'yes']:
            sys.exit(1)
    
    # Start servers in the correct order
    servers_started = []
    
    try:
        # 1. Start Dual Bot API Server
        if start_dual_bot_api_server():
            servers_started.append("Dual Bot API Server")
        else:
            logger.error("Failed to start Dual Bot API Server. Exiting.")
            cleanup_processes()
            sys.exit(1)
        
        # 2. Start Bot Management Server
        if start_bot_management_server():
            servers_started.append("Bot Management Server")
        else:
            logger.error("Failed to start Bot Management Server.")
            # Continue even if Bot Management Server fails
        
        # 3. Start TradingView Integration Server
        if start_tradingview_server():
            servers_started.append("TradingView Integration Server")
        else:
            logger.error("Failed to start TradingView Integration Server.")
            # Continue even if TradingView Integration Server fails
        
        # 4. Start Frontend
        if start_frontend():
            servers_started.append("Frontend")
        else:
            logger.error("Failed to start Frontend.")
            # Continue even if Frontend fails
        
        print("\n" + "="*50)
        print("      STARTUP SUMMARY")
        print("="*50)
        print(f"Started servers: {', '.join(servers_started)}")
        print("\nServer URLs:")
        print(f"- Dual Bot API:      http://localhost:{DUAL_BOT_API_PORT}/api/health")
        print(f"- Bot Management:    http://localhost:{BOT_MANAGEMENT_PORT}/api/health")
        print(f"- TradingView:       http://localhost:{TRADINGVIEW_PORT}/api/test")
        print(f"- Frontend:          http://localhost:{FRONTEND_PORT}")
        print("\nPress Ctrl+C to stop all servers")
        print("="*50 + "\n")
        
        # Keep the script running to maintain the subprocesses
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_processes()

if __name__ == "__main__":
    main() 