#!/usr/bin/env python
"""
Configuration file setup script for the AI Trading Bot project.
This script ensures that all required configuration files are in place
and creates any missing directories needed for the application to run.
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('config_setup')

# Dictionary of required config files and their default locations
CONFIG_FILES = {
    'config.json': {
        'source': 'config.json',
        'destinations': [
            'config.json',
            'api/config.json',
            'backend/config.json',
        ]
    },
    'broker_config.json': {
        'source': 'broker_config.json',
        'destinations': [
            'broker_config.json',
            'api/broker_config.json',
            'backend/broker_config.json',
        ]
    },
    'execution_model_config.json': {
        'source': 'execution_model_config.json',
        'destinations': [
            'execution_model_config.json',
            'api/execution_model_config.json',
            'backend/execution_model_config.json',
        ]
    },
    'market_data_config.json': {
        'source': 'config/environments/market_data_config.json',
        'destinations': [
            'config/environments/market_data_config.json',
            'api/config/environments/market_data_config.json',
            'backend/config/environments/market_data_config.json',
        ]
    }
}

# Required directories to ensure they exist
REQUIRED_DIRS = [
    'data',
    'data/logs',
    'data/broker',
    'data/market_data',
    'data/signals',
    'api/data',
    'api/data/logs',
    'api/data/broker',
    'api/config/environments',
    'backend/config/environments',
    'static',
    'static/css',
    'static/js',
    'static/static',
    'static/static/css',
    'static/static/js',
]

def ensure_directory(directory):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory (str): The directory path to ensure exists
        
    Returns:
        bool: True if the directory exists or was created, False otherwise
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False

def create_config_file(path, content):
    """
    Create a configuration file at the specified path if it doesn't exist.
    
    Args:
        path (str): The path to the configuration file
        content (dict): The content to write to the file
        
    Returns:
        bool: True if the file exists or was created, False otherwise
    """
    try:
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump(content, f, indent=2)
            logger.info(f"Created configuration file: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create configuration file {path}: {e}")
        return False

def copy_file(src, dst):
    """
    Copy a file from source to destination, creating any necessary directories.
    
    Args:
        src (str): The source file path
        dst (str): The destination file path
        
    Returns:
        bool: True if the file was copied or already exists, False on error
    """
    try:
        if not os.path.exists(src):
            logger.warning(f"Source file does not exist: {src}")
            return False
            
        # Create destination directory if it doesn't exist
        dst_dir = os.path.dirname(dst)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir, exist_ok=True)
            
        # Only copy if destination doesn't exist or source is newer
        if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
            shutil.copy2(src, dst)
            logger.info(f"Copied {src} to {dst}")
        return True
    except Exception as e:
        logger.error(f"Failed to copy {src} to {dst}: {e}")
        return False

def copy_config_files():
    """
    Copy all configuration files to their required locations
    and create any necessary directories.
    
    Returns:
        bool: True if all operations succeeded, False otherwise
    """
    success = True
    
    # Ensure all required directories exist
    for directory in REQUIRED_DIRS:
        if not ensure_directory(directory):
            success = False
    
    # Copy all config files to their destinations
    for config_file, config_info in CONFIG_FILES.items():
        source = config_info['source']
        
        # Check if source exists
        if not os.path.exists(source):
            logger.warning(f"Source configuration file not found: {source}")
            continue
            
        # Copy to all destinations
        for destination in config_info['destinations']:
            if not copy_file(source, destination):
                success = False
    
    return success

def main():
    """Main entry point for the script"""
    logger.info("Starting configuration file setup")
    success = copy_config_files()
    
    if success:
        logger.info("Configuration setup completed successfully")
        return 0
    else:
        logger.warning("Configuration setup completed with some issues")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 