#!/usr/bin/env python
"""
Start the Bot Management System

This script starts the Flask API server and ensures all necessary components
are properly initialized.
"""
import os
import subprocess
import logging
import sys
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set"""
    load_dotenv()
    required_vars = [
        'ALPACA_API_KEY',
        'ALPACA_API_SECRET',
        'POLYGON_API_KEY'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please check your .env file at the project root")
        return False
    
    return True

def create_data_directories():
    """Create necessary data directories"""
    dirs = [
        'data',
        'data/logs',
        'data/signals',
        'data/dashboard'
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")
    
    return True

def update_credentials():
    """Update API credentials in files"""
    try:
        # Run the update_credentials.py script
        subprocess.run([sys.executable, 'update_credentials.py'], check=True)
        logger.info("Updated API credentials in all necessary files")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to update credentials: {str(e)}")
        return False

def start_api_server():
    """Start the Flask API server"""
    try:
        logger.info("Starting API server...")
        
        # Start the API server as a subprocess
        api_process = subprocess.Popen(
            [sys.executable, 'run_api.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for the server to start
        time.sleep(2)
        
        # Check if the process is still running
        if api_process.poll() is not None:
            # Process has terminated
            stdout, stderr = api_process.communicate()
            logger.error(f"API server failed to start:\nSTDOUT: {stdout}\nSTDERR: {stderr}")
            return False
        
        logger.info("API server started successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error starting API server: {str(e)}")
        return False

def main():
    """Main entry point"""
    logger.info("Starting Bot Management System...")
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed. Exiting.")
        return False
    
    # Create data directories
    if not create_data_directories():
        logger.error("Failed to create data directories. Exiting.")
        return False
    
    # Update credentials
    if not update_credentials():
        logger.error("Failed to update credentials. Exiting.")
        return False
    
    # Start API server
    if not start_api_server():
        logger.error("Failed to start API server. Exiting.")
        return False
    
    logger.info("Bot Management System started successfully!")
    logger.info("API server is running at http://localhost:5000")
    logger.info("Press Ctrl+C to stop")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down Bot Management System...")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 