"""
Factory module for broker integration.
Responsible for creating and returning broker instances based on configuration.
"""

import logging
from typing import Dict, Any, Optional, Type

from .base import BrokerBase
from .mock import MockBroker
from .alpaca import AlpacaBroker
from .config import load_config, get_active_broker_config

# Configure logging
logger = logging.getLogger(__name__)

# Registry of broker implementations
BROKER_REGISTRY = {
    "mock": MockBroker,
    "alpaca": AlpacaBroker
}

def register_broker(name: str, broker_class: Type[BrokerBase]) -> None:
    """
    Register a broker implementation.
    
    Args:
        name: Unique name for the broker
        broker_class: Broker class that implements BrokerBase
    """
    if name in BROKER_REGISTRY:
        logger.warning(f"Overriding existing broker implementation for '{name}'")
    
    BROKER_REGISTRY[name] = broker_class
    logger.info(f"Registered broker implementation '{name}'")

def get_broker(broker_name: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> BrokerBase:
    """
    Get a broker instance based on the configuration.
    
    Args:
        broker_name: Name of the broker to use. If None, uses the active broker from config.
        config: Configuration dictionary. If None, loads configuration from file.
        
    Returns:
        Instance of BrokerBase implementation
        
    Raises:
        ValueError: If the requested broker is not registered
    """
    if config is None:
        config = load_config()
    
    if broker_name is None:
        # Use active broker from config
        broker_name = config.get("active_broker", "mock")
    
    if broker_name not in BROKER_REGISTRY:
        logger.error(f"Broker '{broker_name}' not registered. Available brokers: {list(BROKER_REGISTRY.keys())}")
        raise ValueError(f"Broker '{broker_name}' not registered")
    
    # Get broker-specific config
    broker_config = config.get("brokers", {}).get(broker_name, {})
    
    # If broker is disabled, default to mock
    if broker_name != "mock" and not broker_config.get("enabled", False):
        logger.warning(f"Broker '{broker_name}' is disabled. Using mock broker instead.")
        broker_name = "mock"
        broker_config = config.get("brokers", {}).get("mock", {})
    
    # Create instance
    broker_class = BROKER_REGISTRY[broker_name]
    broker = broker_class(broker_config)
    
    logger.info(f"Created broker instance of type '{broker_name}'")
    return broker

def get_active_broker(config: Optional[Dict[str, Any]] = None) -> BrokerBase:
    """
    Get the active broker instance.
    
    Args:
        config: Configuration dictionary. If None, loads configuration from file.
        
    Returns:
        Instance of the active broker
    """
    if config is None:
        config = load_config()
    
    active_broker = config.get("active_broker", "mock")
    return get_broker(active_broker, config) 