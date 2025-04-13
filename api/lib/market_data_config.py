"""
Market Data Configuration Module

This module contains the configuration for the market data sources.
Default values are loaded from environment variables or set to None.
"""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

def get_market_data_config() -> Dict[str, Any]:
    """
    Get the market data configuration from environment variables.
    
    Returns:
        Dict: Configuration for market data sources
    """
    # Read APP_ENV to determine if we should use production or test data
    app_env = os.environ.get('APP_ENV', 'development')
    logger.info(f"Application environment: {app_env}")
    
    # Read Unusual Whales API key
    unusual_whales_api_key = os.environ.get('UNUSUAL_WHALES_API_KEY')
    if unusual_whales_api_key:
        logger.info("Unusual Whales API key found in environment")
    else:
        logger.warning("Unusual Whales API key not found in environment")
    
    # Read Alpaca API credentials
    alpaca_api_key = os.environ.get('ALPACA_API_KEY')
    alpaca_api_secret = os.environ.get('ALPACA_API_SECRET')
    
    if alpaca_api_key and alpaca_api_secret:
        logger.info("Alpaca API credentials found in environment")
    else:
        logger.warning("Alpaca API credentials not found in environment")
    
    # Check if we should use real data based on environment
    use_real_data = app_env == 'production'
    
    config = {
        # Use Unusual Whales as the default active source if the API key is available,
        # otherwise fall back to alpaca or mock data
        'active_source': 'unusual_whales' if unusual_whales_api_key and use_real_data else 
                       ('alpaca' if alpaca_api_key and use_real_data else 'mock'),
        
        # Alpaca API configuration
        'alpaca': {
            'api_key': alpaca_api_key,
            'api_secret': alpaca_api_secret,
            'base_url': os.environ.get('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets'),
            'use_real_data': use_real_data
        },
        
        # Interactive Brokers configuration
        'interactive_brokers': {
            'port': int(os.environ.get('IB_PORT', '7496')),
            'client_id': int(os.environ.get('IB_CLIENT_ID', '0')),
            'use_real_data': use_real_data
        },
        
        # Unusual Whales API configuration
        'unusual_whales': {
            'token': unusual_whales_api_key,
            'use_real_data': use_real_data
        },
        
        # TradingView webhooks configuration
        'tradingview': {
            'webhook_port': int(os.environ.get('TRADINGVIEW_WEBHOOK_PORT', '5001')),
            'webhook_path': os.environ.get('TRADINGVIEW_WEBHOOK_PATH', '/tradingview-webhook'),
            'use_real_data': use_real_data
        },
        
        # Mock data configuration (for development and testing)
        'mock': {
            'use_csv_data': True,  # Use CSV files if available
            'csv_directory': 'data/market_data'  # Directory containing CSV files
        }
    }
    
    logger.info(f"Active market data source: {config['active_source']}")
    logger.info(f"Using real data: {use_real_data}")
    
    return config

def save_market_data_config(config: Dict[str, Any]) -> bool:
    """
    Save the market data configuration to a file.
    
    Args:
        config: Configuration for market data sources
        
    Returns:
        bool: True if successful, False otherwise
    """
    import json
    
    try:
        config_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(config_dir, 'market_data_config.json')
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
            
        logger.info(f"Market data configuration saved to {config_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving market data configuration: {e}")
        return False

def load_market_data_config() -> Dict[str, Any]:
    """
    Load the market data configuration from a file.
    If the file doesn't exist, use the default configuration.
    
    Returns:
        Dict: Configuration for market data sources
    """
    import json
    
    try:
        config_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(config_dir, 'market_data_config.json')
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                logger.info(f"Market data configuration loaded from {config_file}")
                
                # Always check if APP_ENV has changed since the config was saved
                app_env = os.environ.get('APP_ENV', 'development')
                logger.info(f"Current application environment: {app_env}")
                
                # Update the use_real_data flags based on current APP_ENV
                use_real_data = app_env == 'production'
                
                for source in config:
                    if isinstance(config[source], dict) and 'use_real_data' in config[source]:
                        config[source]['use_real_data'] = use_real_data
                
                logger.info(f"Using real data (based on APP_ENV): {use_real_data}")
                return config
        else:
            logger.warning(f"Configuration file {config_file} not found, using default configuration")
            return get_market_data_config()
    except Exception as e:
        logger.error(f"Error loading market data configuration: {e}")
        return get_market_data_config() 