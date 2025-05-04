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

def create_required_directories():
    """Create required directories for the application."""
    directories = [
        "data",
        "data/dashboard",
        "data/broker",
        "data/logs",
        "instance"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    return True

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

def start_api_server():
    """Start the API server."""
    logger.info(f"Starting API server on port {API_PORT}...")
    
    # On Render, we don't need to start the API server separately
    if IS_RENDER:
        logger.info("Running on Render - API server will be started by Render itself")
        return None
    
    # Check if port is available
    if not check_port_available(API_PORT):
        logger.warning(f"Port {API_PORT} is already in use")
        user_input = input(f"Do you want to kill the process using port {API_PORT}? (y/n): ")
        if user_input.lower() == 'y':
            kill_process_on_port(API_PORT)
        else:
            logger.error(f"Cannot start API server on port {API_PORT}")
            return None
    
    # Create required directories
    create_required_directories()
    
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
        
        # Wait a bit to see if the server starts correctly
        time.sleep(5)
        
        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            logger.error(f"API server process terminated with code: {process.returncode}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return None
        
        logger.info("API server is running!")
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

def handle_interrupt(signum, frame):
    """Handle interrupt signal (Ctrl+C)."""
    logger.info("\nShutting down servers...")
    
    # Terminate all processes
    for name, process in running_processes.items():
        logger.info(f"Stopping {name}...")
        terminate_process(process)
    
    logger.info("All servers stopped")
    print("\nThank you for using AI Trading Bot!")
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
    """Main function."""
    # Check if running on Render
    if IS_RENDER:
        # For Render, just set up the environment
        return start_render_deployment()
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, handle_interrupt)
    
    print("\n" + "="*60)
    print("        AI TRADING BOT - UNIFIED SERVER STARTER")
    print("="*60 + "\n")
    
    logger.info("Starting all servers...")
    
    # Start API server
    api_process = start_api_server()
    if api_process:
        running_processes["api_server"] = api_process
    else:
        logger.error("Failed to start API server")
        return False
    
    # Start Bot Management Server
    bot_mgmt_process = start_bot_management_server()
    if bot_mgmt_process:
        running_processes["bot_management_server"] = bot_mgmt_process
    
    # Start TradingView Server
    tv_process = start_tradingview_server()
    if tv_process:
        running_processes["tradingview_server"] = tv_process
    
    # Start Frontend
    frontend_process = start_frontend()
    if frontend_process:
        running_processes["frontend"] = frontend_process
    else:
        logger.warning("Failed to start frontend")
    
    # Print summary
    print("\n" + "="*60)
    print("        SERVER STARTUP SUMMARY")
    print("="*60)
    print(f"API Server:            http://localhost:{API_PORT}/api/health")
    
    if "bot_management_server" in running_processes:
        print(f"Bot Management Server: http://localhost:{BOT_MANAGEMENT_PORT}/api/health")
    
    if "tradingview_server" in running_processes:
        print(f"TradingView Server:    http://localhost:{TRADINGVIEW_PORT}/api/test")
    
    if "frontend" in running_processes:
        print(f"Frontend:              http://localhost:{FRONTEND_PORT}")
    
    print("\nPress Ctrl+C to stop all servers")
    print("="*60 + "\n")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # This should be caught by our signal handler
        pass
    
    return True

if __name__ == "__main__":
    main() 