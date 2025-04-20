#!/usr/bin/env python
"""
AI Trading Bot V2.0 - Application Cleanup Utility

This script helps to safely shut down all components of the application.
It terminates running processes on ports 5000 (Flask API) and 3000 (React Frontend).
"""

import os
import sys
import subprocess
import platform
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AppCleanup")

# Print directly to ensure visibility
print("=" * 50)
print("AI Trading Bot V2.0 Cleanup Utility")
print("=" * 50)

def cleanup_processes():
    """Terminate processes running on application ports"""
    print("Cleaning up application processes...")
    logger.info("Cleaning up application processes...")
    
    success = True
    
    try:
        if platform.system() == "Windows":
            # Check for running processes using the Flask port
            print("Terminating Flask API server on port 5000...")
            logger.info("Terminating Flask API server on port 5000...")
            subprocess.run('for /f "tokens=5" %a in (\'netstat -aon ^| findstr ":5000"\') do taskkill /F /PID %a', shell=True, check=False)
            
            # Check for running processes using the React port
            print("Terminating React frontend on port 3000...")
            logger.info("Terminating React frontend on port 3000...")
            subprocess.run('for /f "tokens=5" %a in (\'netstat -aon ^| findstr ":3000"\') do taskkill /F /PID %a', shell=True, check=False)
            
            # Also try to kill by process name for safety
            print("Terminating any remaining Python and Node.js processes...")
            logger.info("Terminating any remaining Python and Node.js processes...")
            subprocess.run('taskkill /F /IM python.exe /FI "WINDOWTITLE eq AI Trading Bot*"', shell=True, check=False)
            subprocess.run('taskkill /F /IM node.exe /FI "WINDOWTITLE eq AI Trading Bot*"', shell=True, check=False)
            
        else:
            # Linux/Mac version
            print("Terminating Flask API server on port 5000...")
            logger.info("Terminating Flask API server on port 5000...")
            subprocess.run("lsof -i:5000 | grep LISTEN | awk '{print $2}' | xargs -r kill -9", shell=True, check=False)
            
            print("Terminating React frontend on port 3000...")
            logger.info("Terminating React frontend on port 3000...")
            subprocess.run("lsof -i:3000 | grep LISTEN | awk '{print $2}' | xargs -r kill -9", shell=True, check=False)
            
            # Also try to kill by process name
            print("Terminating any remaining Python and Node.js processes...")
            logger.info("Terminating any remaining Python and Node.js processes...")
            subprocess.run("pkill -f 'python.*app-starter.py'", shell=True, check=False)
            subprocess.run("pkill -f 'python.*flask'", shell=True, check=False)
            subprocess.run("pkill -f 'node.*start'", shell=True, check=False)
    
    except Exception as e:
        print(f"Error during cleanup: {e}")
        logger.error(f"Error during cleanup: {e}")
        success = False
    
    # Verify cleanup was successful
    time.sleep(2)  # Wait for processes to terminate
    
    flask_running = False
    react_running = False
    
    try:
        # Check if Flask API is still running
        flask_check = subprocess.run(
            'netstat -ano | findstr ":5000"' if platform.system() == "Windows" else "lsof -i:5000",
            shell=True, 
            capture_output=True,
            text=True
        )
        
        if flask_check.stdout.strip():
            print("Flask API server is still running")
            logger.warning("Flask API server is still running")
            flask_running = True
        
        # Check if React frontend is still running
        react_check = subprocess.run(
            'netstat -ano | findstr ":3000"' if platform.system() == "Windows" else "lsof -i:3000",
            shell=True, 
            capture_output=True,
            text=True
        )
        
        if react_check.stdout.strip():
            print("React frontend is still running")
            logger.warning("React frontend is still running")
            react_running = True
            
        if not flask_running and not react_running:
            print("All application components have been terminated successfully")
            logger.info("All application components have been terminated successfully")
        else:
            print("Some application components are still running")
            logger.warning("Some application components are still running")
            success = False
            
    except Exception as e:
        print(f"Error verifying cleanup: {e}")
        logger.error(f"Error verifying cleanup: {e}")
        success = False
    
    return success

def main():
    """Main function"""
    logger.info("AI Trading Bot V2.0 Cleanup Utility")
    
    success = cleanup_processes()
    
    if success:
        print("=" * 50)
        print("Cleanup completed successfully!")
        print("=" * 50)
        logger.info("Cleanup completed successfully!")
    else:
        print("=" * 50)
        print("Cleanup completed with some issues.")
        print("You may need to manually terminate remaining processes.")
        print("=" * 50)
        logger.warning("Cleanup completed with some issues.")
        logger.warning("You may need to manually terminate remaining processes.")
    
    return success

if __name__ == "__main__":
    main() 