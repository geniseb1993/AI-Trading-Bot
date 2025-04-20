#!/usr/bin/env python
"""
update_dashboard.py - Update dashboard data and start development server

This script runs the trading pipeline to generate up-to-date data,
then starts the development server.
"""

import os
import sys
import subprocess
import time
import logging
import shutil
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to update dashboard data and start server"""
    try:
        # Step 1: Run the update_backtest_data.py script to generate fresh data
        logger.info("Running update_backtest_data.py to generate fresh data...")
        
        # Import and run update_backtest_data function
        from update_backtest_data import update_backtest_data
        success = update_backtest_data()
        
        if success:
            logger.info("✅ Successfully updated backtest data")
        else:
            logger.error("❌ Failed to update backtest data")
            return False
        
        # Step 2: Make sure data files are copied to the frontend/public directory
        ensure_data_available_for_frontend()
        
        # Step 3: Start the backend Flask server if not already running
        logger.info("Checking if backend server is running...")
        
        # Try to connect to the server
        import requests
        backend_running = False
        try:
            response = requests.get("http://localhost:5000/api/test", timeout=2)
            if response.status_code == 200:
                logger.info("Backend server is already running")
                backend_running = True
        except requests.exceptions.RequestException:
            logger.info("Backend server is not running")
        
        if not backend_running:
            logger.info("Starting backend server...")
            # Start backend in a new process
            backend_process = subprocess.Popen(
                ["python", "api/app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for the server to start
            time.sleep(3)
            logger.info("Backend server started")
        
        # Step 4: Check if frontend is running
        logger.info("Checking if frontend server is running...")
        
        frontend_running = False
        try:
            response = requests.get("http://localhost:3000", timeout=2)
            if response.status_code == 200:
                logger.info("Frontend server is already running")
                frontend_running = True
        except requests.exceptions.RequestException:
            logger.info("Frontend server is not running")
        
        if not frontend_running:
            logger.info("Starting frontend development server...")
            
            # Navigate to the frontend directory
            os.chdir("frontend")
            
            # Start frontend in a new process
            frontend_process = subprocess.Popen(
                ["npm", "start"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for the server to start
            time.sleep(5)
            logger.info("Frontend server started")
            
            # Return to the original directory
            os.chdir("..")
        
        logger.info("✅ Dashboard is now running with real data")
        logger.info("- Backend URL: http://localhost:5000")
        logger.info("- Frontend URL: http://localhost:3000")
        
        print("\n✅ Trading dashboard is now running with real pipeline data!")
        print("📊 Open http://localhost:3000 in your browser to view it")
        print("\nPress Ctrl+C to stop the servers\n")
        
        # Keep the script running to allow the user to view logs and Ctrl+C to exit
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        return True
    except Exception as e:
        logger.error(f"Error updating dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def ensure_data_available_for_frontend():
    """
    Make sure all the necessary data files are available for the frontend
    by copying them to the frontend/public/data directory
    """
    logger.info("Ensuring data files are available for frontend...")
    
    # Create the frontend data directory if it doesn't exist
    frontend_data_dir = os.path.join("frontend", "public", "data")
    os.makedirs(frontend_data_dir, exist_ok=True)
    
    frontend_dashboard_dir = os.path.join(frontend_data_dir, "dashboard")
    os.makedirs(frontend_dashboard_dir, exist_ok=True)
    
    # Copy individual dashboard data files
    src_dashboard_dir = os.path.join("data", "dashboard")
    if os.path.exists(src_dashboard_dir):
        for file in os.listdir(src_dashboard_dir):
            src_file = os.path.join(src_dashboard_dir, file)
            dst_file = os.path.join(frontend_dashboard_dir, file)
            try:
                shutil.copy2(src_file, dst_file)
                logger.info(f"Copied {src_file} to {dst_file}")
            except Exception as e:
                logger.error(f"Error copying {src_file}: {str(e)}")
    
    # Also copy data files from the project root
    data_files = [
        "backtest_results.csv",
        "buy_signals.csv",
        "short_signals.csv"
    ]
    
    for file in data_files:
        if os.path.exists(file):
            dst_file = os.path.join(frontend_data_dir, file)
            try:
                shutil.copy2(file, dst_file)
                logger.info(f"Copied {file} to {dst_file}")
            except Exception as e:
                logger.error(f"Error copying {file}: {str(e)}")
    
    # Disable the backtest chart figure by creating a file with config
    config = {
        "showBacktestChart": False,
        "useRealData": True
    }
    
    config_file = os.path.join(frontend_data_dir, "config.json")
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f)
        logger.info(f"Created config file at {config_file}")
    except Exception as e:
        logger.error(f"Error creating config file: {str(e)}")
    
    logger.info("✅ Data files prepared for frontend")
    
if __name__ == "__main__":
    main() 