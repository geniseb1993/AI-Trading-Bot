"""
Broker Integration Package

This package handles integration with various brokers and provides a unified interface
for interacting with them. It supports multiple broker implementations and manages
configuration, authentication, and trading operations.
"""

import logging
import os
from typing import Dict, Any
from flask import Flask

# Configure logging
logger = logging.getLogger(__name__)

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def init_app(app: Flask) -> None:
    """
    Initialize broker integration with the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Import here to avoid circular imports
    try:
        from .routes import init_app as init_routes
        from .config import load_config
        
        # Initialize routes
        init_routes(app)
        
        logger.info("Broker integration initialized")
    except Exception as e:
        logger.error(f"Error initializing broker integration: {str(e)}")

# Register broker implementations
def register_brokers() -> None:
    """
    Register available broker implementations.
    This function imports and registers all available broker classes.
    """
    available_brokers = {}
    
    # Check if we should use mock broker
    use_mock_broker = os.environ.get('USE_MOCK_BROKER', 'false').lower() == 'true'
    
    try:
        # Import mock broker - this should always work
        from .mock_broker import MockBroker
        available_brokers["mock"] = MockBroker
        logger.info("Successfully imported mock broker")
        
        # If we're forced to use mock broker, don't even try to import Alpaca
        if use_mock_broker:
            logger.info("Using mock broker as configured by environment variables")
        else:
            # Import Alpaca broker - may fail if alpaca-trade-api is not available
            try:
                from .alpaca_broker import AlpacaBroker
                available_brokers["alpaca"] = AlpacaBroker
                logger.info("Successfully imported Alpaca broker")
            except ImportError as e:
                logger.warning(f"Could not import Alpaca broker (using mock instead): {str(e)}")
                available_brokers["alpaca"] = MockBroker  # Use mock as a fallback for alpaca
            except Exception as e:
                logger.error(f"Error importing Alpaca broker: {str(e)}")
                available_brokers["alpaca"] = MockBroker  # Use mock as a fallback for alpaca
    except Exception as e:
        logger.error(f"Error importing brokers: {str(e)}")
    
    try:
        # Import factory module and register brokers
        from .factory import register_broker
        
        # Register available brokers with the factory
        for name, broker in available_brokers.items():
            register_broker(name, broker)
        
        logger.info(f"Registered {len(available_brokers)} broker implementations")
    except Exception as e:
        logger.error(f"Error registering broker implementations: {str(e)}")

# Call register_brokers when the package is imported
try:
    register_brokers()
except Exception as e:
    logger.error(f"Failed to register brokers: {str(e)}")

# Version
__version__ = "0.1.0"