#!/usr/bin/env python
"""
Simplified script to start both API server and frontend
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
        logging.FileHandler("server_startup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("server_startup")

# Constants
BASE_DIR = Path(__file__).resolve().parent
API_PORT = 5001
FRONTEND_PORT = 3001

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

def start_api_server():
    """Start the API server."""
    logger.info(f"Starting API server on port {API_PORT}...")
    
    # Create required directories
    create_required_directories()
    
    # Set environment variables
    env = os.environ.copy()
    env["FLASK_APP"] = "simple_api_server.py"
    env["FLASK_ENV"] = "development"
    env["FLASK_DEBUG"] = "1"
    
    # Start the server
    cmd = [sys.executable, "simple_api_server.py"]
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        logger.info(f"API server process started with PID: {process.pid}")
        
        # Wait a bit to see if the server starts correctly
        time.sleep(5)
        
        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            logger.error(f"API server process terminated with code: {process.returncode}")
            logger.error(f"STDOUT: {stdout.decode('utf-8')}")
            logger.error(f"STDERR: {stderr.decode('utf-8')}")
            return None
        
        logger.info("API server is running!")
        return process
    
    except Exception as e:
        logger.error(f"Error starting API server: {e}")
        return None

def start_frontend():
    """Start the frontend application."""
    logger.info(f"Starting frontend on port {FRONTEND_PORT}...")
    
    frontend_dir = os.path.join(BASE_DIR, "frontend")
    
    if not os.path.exists(frontend_dir):
        logger.error(f"Frontend directory not found: {frontend_dir}")
        return None
    
    if not os.path.exists(os.path.join(frontend_dir, "package.json")):
        logger.error(f"package.json not found in frontend directory")
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
            shell=True
        )
        
        # Change back to original directory
        os.chdir(BASE_DIR)
        
        logger.info(f"Frontend process started with PID: {process.pid}")
        
        # Wait a bit to see if the frontend starts correctly
        time.sleep(5)
        
        if process.poll() is not None:
            # Process has terminated
            logger.error(f"Frontend process terminated with code: {process.returncode}")
            return None
        
        logger.info("Frontend is running!")
        return process
    
    except Exception as e:
        logger.error(f"Error starting frontend: {e}")
        # Change back to original directory
        os.chdir(BASE_DIR)
        return None

def main():
    """Main function."""
    print("\n" + "="*50)
    print("      SIMPLIFIED SERVER STARTER")
    print("="*50 + "\n")
    
    # Start API server
    api_process = start_api_server()
    
    if api_process is None:
        logger.error("Failed to start API server")
        return False
    
    # Start frontend
    frontend_process = start_frontend()
    
    if frontend_process is None:
        logger.warning("Failed to start frontend")
        # Continue even if frontend fails
    
    # Print summary
    print("\n" + "="*50)
    print("      STARTUP SUMMARY")
    print("="*50)
    print(f"API server running at: http://localhost:{API_PORT}")
    if frontend_process is not None:
        print(f"Frontend running at: http://localhost:{FRONTEND_PORT}")
    print("\nPress Ctrl+C to stop all servers")
    print("="*50 + "\n")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        
        # Terminate processes
        if api_process is not None:
            api_process.terminate()
        
        if frontend_process is not None:
            frontend_process.terminate()
    
    return True

if __name__ == "__main__":
    main() 