#!/usr/bin/env python
"""
Simplified script to start the AI Trading Bot application
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_start.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app_starter")

# Constants
BASE_DIR = Path(__file__).resolve().parent
VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
DUAL_BOT_SERVER = os.path.join(BASE_DIR, "simple_api_server.py")
PORT = 5001

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

def start_server():
    """Start the API server."""
    logger.info(f"Starting API server on port {PORT}...")
    
    # Create required directories
    create_required_directories()
    
    # Set environment variables
    env = os.environ.copy()
    env["FLASK_APP"] = DUAL_BOT_SERVER
    env["FLASK_ENV"] = "development"
    env["FLASK_DEBUG"] = "1"
    
    # Start the server
    cmd = [VENV_PYTHON, DUAL_BOT_SERVER]
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        logger.info(f"Server process started with PID: {process.pid}")
        
        # Wait a bit to see if the server starts correctly
        for i in range(10):
            if process.poll() is not None:
                # Process has terminated
                stdout, stderr = process.communicate()
                logger.error(f"Server process terminated with code: {process.returncode}")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
            
            time.sleep(1)
            logger.info(f"Waiting for server to start ({i+1}/10)...")
        
        # Process is still running, assume it's working
        logger.info("Server is running!")
        return True
    
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return False

def main():
    """Main function."""
    logger.info("=" * 50)
    logger.info("STARTING AI TRADING BOT APPLICATION")
    logger.info("=" * 50)
    
    if not os.path.exists(VENV_PYTHON):
        logger.error(f"Virtual environment Python not found at: {VENV_PYTHON}")
        logger.info("Make sure the virtual environment is set up correctly.")
        return False
    
    if not os.path.exists(DUAL_BOT_SERVER):
        logger.error(f"API server script not found at: {DUAL_BOT_SERVER}")
        return False
    
    # Start the API server
    if start_server():
        logger.info(f"API server started successfully on port {PORT}")
        logger.info(f"You can access the API at: http://localhost:{PORT}/api/health")
        logger.info("Press Ctrl+C to stop the server")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
    else:
        logger.error("Failed to start the API server")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 