"""
Broker Integration Configuration Module

This module handles loading and saving broker integration configurations.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default configuration paths
DEFAULT_CONFIG_PATH = "broker_config.json"
BACKUP_CONFIG_PATH = "config/secrets/broker_config.json"

# Default configuration for brokers
DEFAULT_CONFIG = {
    "active_broker": "mock",
    "mock": {
        "use_real_data": False,
        "simulated_slippage": 0.01,
        "simulated_latency": 500
    },
    "alpaca": {
        "api_key": "YOUR_ALPACA_API_KEY",
        "api_secret": "YOUR_ALPACA_API_SECRET",
        "paper_trading": True,
        "base_url": "https://paper-api.alpaca.markets"
    },
    "interactive_brokers": {
        "tws_port": 7497,
        "client_id": 1,
        "host": "localhost",
        "read_only": True
    },
    "td_ameritrade": {
        "api_key": "",
        "refresh_token": "",
        "callback_url": "http://localhost:5000/callback"
    }
}

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load broker configuration from a file.
    
    Args:
        config_path: Path to the configuration file. If None, tries default paths.
        
    Returns:
        Dict containing broker configuration.
    """
    # If no path specified, try default paths
    if not config_path:
        # Try the default path first
        if os.path.exists(DEFAULT_CONFIG_PATH):
            config_path = DEFAULT_CONFIG_PATH
        # Try the backup path
        elif os.path.exists(BACKUP_CONFIG_PATH):
            config_path = BACKUP_CONFIG_PATH
        # If no file exists, return default configuration
        else:
            logger.warning("No broker configuration file found. Using default configuration.")
            return DEFAULT_CONFIG
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            logger.info(f"Successfully loaded broker configuration from {config_path}")
            return config
    except FileNotFoundError:
        logger.warning(f"Configuration file {config_path} not found. Using default configuration.")
        return DEFAULT_CONFIG
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {config_path}: {str(e)}. Using default configuration.")
        return DEFAULT_CONFIG
    except Exception as e:
        logger.error(f"Unexpected error loading configuration from {config_path}: {str(e)}. Using default configuration.")
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any], config_path: str = DEFAULT_CONFIG_PATH) -> bool:
    """
    Save broker configuration to a file.
    
    Args:
        config: Dictionary containing broker configuration.
        config_path: Path to save the configuration file.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(config_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"Successfully saved broker configuration to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving broker configuration to {config_path}: {str(e)}")
        return False

def get_active_broker_config() -> Dict[str, Any]:
    """
    Get the configuration for the currently active broker.
    
    Returns:
        Dict containing active broker configuration.
    """
    config = load_config()
    active_broker = config.get('active_broker', 'mock')
    
    # Get the configuration for the active broker
    if active_broker in config:
        broker_config = config[active_broker]
        return {
            "broker": active_broker,
            "config": broker_config
        }
    else:
        logger.warning(f"Active broker '{active_broker}' not found in configuration. Using mock broker.")
        return {
            "broker": "mock",
            "config": config.get("mock", {})
        } 