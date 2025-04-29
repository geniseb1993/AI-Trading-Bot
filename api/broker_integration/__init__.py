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
    from .routes import init_app as init_routes
    from .config import load_config
    
    # Initialize routes
    init_routes(app)
    
    logger.info("Broker integration initialized")

# Register broker implementations
def register_brokers() -> None:
    """
    Register available broker implementations.
    This function imports and registers all available broker classes.
    """
    try:
        # Import mock broker
        from .mock_broker import MockBroker
        
        # Import Alpaca broker
        from .alpaca_broker import AlpacaBroker
        
        # Import factory module and register brokers
        from .factory import register_broker
        
        # Register brokers with the factory
        register_broker("mock", MockBroker)
        register_broker("alpaca", AlpacaBroker)
        
        logger.info("Broker implementations registered successfully")
    except ImportError as e:
        logger.warning(f"Failed to register some broker implementations: {str(e)}")
    except Exception as e:
        logger.error(f"Error registering broker implementations: {str(e)}")

# Call register_brokers when the package is imported
register_brokers()

# Import key classes and functions
from .base import BrokerBase
from .mock import MockBroker
from .alpaca import AlpacaBroker
from .factory import get_broker, get_active_broker, register_broker
from .config import load_config, save_config, get_active_broker_config

# Register built-in broker implementations
from .factory import BROKER_REGISTRY

# Ensure Alpaca broker is registered if available
try:
    BROKER_REGISTRY["alpaca"] = AlpacaBroker
except Exception as e:
    logger.warning(f"Could not register Alpaca broker: {str(e)}")

# Version
__version__ = "0.1.0"