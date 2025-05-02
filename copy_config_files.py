#!/usr/bin/env python
"""
Copy Config Files Script

This script copies configuration files to all necessary locations in the project structure
to ensure consistent configuration across all services.
"""

import os
import shutil
import json
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("config_copier")

# Primary configuration files
CONFIG_FILES = {
    "config.json": [
        "api/config/config.json",
        "backend/config/config.json",
        "server/config/config.json"
    ],
    "broker_config.json": [
        "api/config/broker_config.json",
        "backend/config/broker_config.json",
        "server/config/broker_config.json"
    ],
    "execution_model_config.json": [
        "api/config/execution_model_config.json",
        "backend/config/execution_model_config.json",
        "server/config/execution_model_config.json"
    ]
}

# Environment-specific config files
ENV_CONFIG_FILES = {
    "config/environments/market_data_config.json": [
        "api/config/environments/market_data_config.json",
        "backend/config/environments/market_data_config.json",
        "server/config/environments/market_data_config.json"
    ]
}

def ensure_directory_exists(directory_path):
    """
    Make sure the directory exists, creating it if necessary
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path.exists()

def copy_file(source, destination):
    """
    Copy a file from source to destination, creating directories if needed
    """
    try:
        # Make sure target directory exists
        dest_dir = os.path.dirname(destination)
        ensure_directory_exists(dest_dir)
        
        # Copy the file
        shutil.copy2(source, destination)
        logger.info(f"Copied {source} to {destination}")
        return True
    except FileNotFoundError:
        logger.warning(f"Source file {source} not found. Skipping.")
        return False
    except Exception as e:
        logger.error(f"Error copying {source} to {destination}: {str(e)}")
        return False

def create_default_config(template, destination):
    """
    Create default config file if the source doesn't exist
    """
    try:
        # Make sure template exists
        if not os.path.exists(template):
            logger.warning(f"Template {template} not found. Cannot create default.")
            return False
            
        # Make sure target directory exists
        dest_dir = os.path.dirname(destination)
        ensure_directory_exists(dest_dir)
        
        # Copy the file
        shutil.copy2(template, destination)
        logger.info(f"Created default config at {destination} from {template}")
        return True
    except Exception as e:
        logger.error(f"Error creating default config at {destination}: {str(e)}")
        return False

def copy_api_lib_configs():
    """Copy config files to the lib directories for api and other modules"""
    try:
        market_data_config = "config/environments/market_data_config.json"
        if os.path.exists(market_data_config):
            # Copy to api/lib
            dest = "api/lib/market_data_config.json"
            copy_file(market_data_config, dest)
            
            # Copy to backend/lib
            dest = "backend/lib/market_data_config.json"
            copy_file(market_data_config, dest)
            
            # Copy to other potential locations
            dest = "lib/market_data_config.json"
            copy_file(market_data_config, dest)
    except Exception as e:
        logger.error(f"Error copying lib configs: {str(e)}")

def main():
    """
    Main entry point: copy all configuration files to their respective locations
    """
    logger.info("Starting configuration file deployment")
    
    # Create necessary directories
    ensure_directory_exists("api/config/environments")
    ensure_directory_exists("backend/config/environments")
    ensure_directory_exists("server/config/environments")
    ensure_directory_exists("config/environments")
    
    # Copy primary config files
    for source, destinations in CONFIG_FILES.items():
        if os.path.exists(source):
            for dest in destinations:
                copy_file(source, dest)
        else:
            logger.warning(f"Source file {source} not found")
    
    # Copy environment-specific config files
    for source, destinations in ENV_CONFIG_FILES.items():
        if os.path.exists(source):
            for dest in destinations:
                copy_file(source, dest)
        else:
            logger.warning(f"Source file {source} not found")
    
    # Special handling for API lib configs
    copy_api_lib_configs()
    
    logger.info("Configuration file deployment completed")

if __name__ == "__main__":
    main() 