#!/usr/bin/env python
"""
Ensures that all necessary directories exist for the application to run.
This is important for deployment environments like Render where the application 
may need to create directories that aren't in the git repository.
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_directories():
    """Create all necessary directories if they don't exist."""
    directories = [
        'data',
        'data/logs',
        'data/market_data',
        'data/signals',
        'data/broker',
        'data/broker/mock',
        'data/dashboard',
        'logs',
        'instance',
        'public',
        'public/images',
        'public/sounds',
        'secure_backups'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {str(e)}")
        else:
            logger.info(f"Directory already exists: {directory}")
    
    # Create empty files if needed
    empty_files = [
        'data/logs/api.log',
        'data/logs/dual_bot.log',
        'logs/server.log'
    ]
    
    for file_path in empty_files:
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(file_path)
        if not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir)
                logger.info(f"Created parent directory: {parent_dir}")
            except Exception as e:
                logger.error(f"Error creating parent directory {parent_dir}: {str(e)}")
        
        # Create empty file if it doesn't exist
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w') as f:
                    pass  # Create empty file
                logger.info(f"Created empty file: {file_path}")
            except Exception as e:
                logger.error(f"Error creating file {file_path}: {str(e)}")

if __name__ == "__main__":
    ensure_directories() 