#!/usr/bin/env python
"""
Copy Configuration Files

This script copies configuration files to their expected locations
to fix issues with missing configuration files on Render deployment.
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ensure_directory(directory):
    """Ensure a directory exists, creating it if necessary."""
    try:
        if not os.path.exists(directory):
            logger.info(f"Creating directory: {directory}")
            os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False

def create_config_file(path, content):
    """Create a configuration file with the given content."""
    try:
        # Ensure the directory exists
        ensure_directory(os.path.dirname(path))
        
        # Write the file
        with open(path, 'w') as f:
            json.dump(content, f, indent=2)
        
        logger.info(f"Created config file: {path}")
        return True
    except Exception as e:
        logger.error(f"Error creating config file {path}: {e}")
        return False

def copy_file(src, dst):
    """Copy a file if it exists."""
    try:
        if os.path.exists(src):
            # Ensure the destination directory exists
            ensure_directory(os.path.dirname(dst))
            
            # Copy the file
            shutil.copy2(src, dst)
            logger.info(f"Copied {src} to {dst}")
            return True
        else:
            logger.warning(f"Source file not found: {src}")
            return False
    except Exception as e:
        logger.error(f"Error copying file from {src} to {dst}: {e}")
        return False

def copy_config_files():
    """Copy configuration files to their expected locations."""
    
    # Create necessary directories
    dirs = [
        os.path.join(BASE_DIR, 'config'),
        os.path.join(BASE_DIR, 'config', 'environments'),
        os.path.join(BASE_DIR, 'data'),
        os.path.join(BASE_DIR, 'data', 'logs'),
        os.path.join(BASE_DIR, 'data', 'broker'),
        os.path.join(BASE_DIR, 'data', 'market_data'),
        os.path.join(BASE_DIR, 'data', 'signals'),
        os.path.join(BASE_DIR, 'mock_modules')
    ]
    
    for directory in dirs:
        ensure_directory(directory)
    
    # List of configuration files to copy
    config_files = [
        ('config.json', os.path.join(BASE_DIR, 'config.json')),
        ('broker_config.json', os.path.join(BASE_DIR, 'broker_config.json')),
        ('execution_model_config.json', os.path.join(BASE_DIR, 'execution_model_config.json')),
        ('market_data_config.json', os.path.join(BASE_DIR, 'config', 'environments', 'market_data_config.json'))
    ]
    
    # Copy config files to expected locations
    for src_name, dst_path in config_files:
        src_path = os.path.join(BASE_DIR, src_name)
        copy_file(src_path, dst_path)
    
    # Define default configs if files don't exist
    default_configs = {
        'config.json': {
            "version": "1.0.0",
            "application_name": "AI Trading Bot",
            "environment": "production",
            "notifications": {
                "enabled": True,
                "channels": ["console"],
                "trade_notifications": True,
                "system_notifications": True,
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_email": "",
                    "to_email": ""
                },
                "discord": {
                    "enabled": False,
                    "webhook_url": ""
                },
                "voice": {
                    "enabled": False,
                    "provider": "mock"
                }
            },
            "market_data": {
                "default_source": "mock",
                "cache_enabled": True,
                "cache_duration": 3600
            },
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "console_enabled": True,
                "log_dir": "data/logs"
            }
        },
        'broker_config.json': {
            "default_broker": "mock",
            "paper_trading": True,
            "brokers": {
                "alpaca": {
                    "api_key": "",
                    "api_secret": "",
                    "base_url": "https://paper-api.alpaca.markets",
                    "data_url": "https://data.alpaca.markets",
                    "enabled": False
                },
                "mock": {
                    "enabled": True,
                    "initial_balance": 100000,
                    "commission": 0.0,
                    "delay": 0,
                    "slippage": 0.001
                }
            }
        },
        'execution_model_config.json': {
            "mode": "paper",
            "risk_level": "medium",
            "max_positions": 10,
            "position_sizing": "adaptive",
            "risk_management": {
                "stop_loss_percent": 2.0,
                "take_profit_percent": 5.0,
                "trailing_stop": False,
                "trailing_stop_percent": 1.0
            }
        },
        'market_data_config.json': {
            "active_source": "mock",
            "use_real_data": False,
            "sources": {
                "alpaca": {
                    "enabled": False,
                    "api_key": "",
                    "api_secret": "",
                    "base_url": "https://paper-api.alpaca.markets",
                    "data_url": "https://data.alpaca.markets"
                },
                "mock": {
                    "enabled": True,
                    "use_csv_data": True,
                    "csv_directory": "data/market_data"
                }
            }
        }
    }
    
    # Create default config files if they don't exist
    for config_name, content in default_configs.items():
        if config_name == 'market_data_config.json':
            path = os.path.join(BASE_DIR, 'config', 'environments', config_name)
        else:
            path = os.path.join(BASE_DIR, config_name)
            
        if not os.path.exists(path):
            create_config_file(path, content)
    
    logger.info("Config files copied successfully!")
    return True

if __name__ == "__main__":
    success = copy_config_files()
    sys.exit(0 if success else 1) 