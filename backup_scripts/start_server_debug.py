#!/usr/bin/env python
"""
Debug script to start the Dual Bot API Server with detailed logs
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug_server_start.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("server_debug")

def create_required_directories():
    """Create any required directories for the server."""
    dirs = [
        "data",
        "data/dashboard",
        "data/broker",
        "data/logs"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        logger.info(f"Created directory: {d}")
    
    return True

def check_database_file():
    """Check if database file exists and create it if necessary."""
    db_path = os.path.join("instance", "trading_bot.db")
    os.makedirs("instance", exist_ok=True)
    
    if not os.path.exists(db_path):
        logger.info(f"Database file not found at {db_path}. Creating empty file.")
        # Create an empty file
        with open(db_path, 'w') as f:
            pass
    else:
        logger.info(f"Database file found at {db_path}")
    
    return True

def start_server():
    """Start the Dual Bot API Server with debug logs."""
    logger.info("Starting Dual Bot API Server in debug mode...")
    
    # Create required directories
    create_required_directories()
    
    # Check database file
    check_database_file()
    
    # Get Python executable
    python_exe = os.path.join(".venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable
        logger.warning(f"Using system Python interpreter: {python_exe}")
    else:
        logger.info(f"Using virtual environment Python: {python_exe}")
    
    # Check if server script exists
    server_script = "dual_bot_api_server.py"
    if not os.path.exists(server_script):
        logger.error(f"Server script not found: {server_script}")
        return False
    
    # Set environment variables
    env = os.environ.copy()
    env["FLASK_APP"] = server_script
    env["FLASK_ENV"] = "development"
    env["FLASK_DEBUG"] = "1"
    env["LOG_LEVEL"] = "DEBUG"
    
    # Print all environment variables (without secret values)
    logger.info("Environment variables:")
    for key, value in env.items():
        if "KEY" in key or "SECRET" in key or "TOKEN" in key:
            logger.info(f"  {key}=****")
        else:
            logger.info(f"  {key}={value}")
    
    # Start the server process
    cmd = [python_exe, server_script]
    logger.info(f"Starting server with command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        logger.info(f"Server process started with PID: {process.pid}")
        
        # Monitor the process for a short time to see if it crashes immediately
        for i in range(10):
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                logger.error(f"Server exited immediately with code: {process.returncode}")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
            
            logger.info(f"Waiting for server to start ({i+1}/10)...")
            time.sleep(1)
        
        # If we get here, the server is at least running
        logger.info("Server started and running.")
        return True
    
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return False

def main():
    """Main function."""
    logger.info("=" * 40)
    logger.info("STARTING SERVER IN DEBUG MODE")
    logger.info("=" * 40)
    
    # Start the server
    success = start_server()
    
    if success:
        logger.info("Server startup appears successful.")
        logger.info("Server should be available at: http://localhost:5001")
        logger.info("Health check endpoint: http://localhost:5001/api/health")
        logger.info("Press Ctrl+C to stop the server")
        
        # Keep the script running so we can see logs
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
    else:
        logger.error("Failed to start server.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 