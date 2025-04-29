import logging
from typing import Dict, Any, Optional

# Import broker implementations
from api.broker_integration.broker_interface import BrokerInterface
from api.broker_integration.brokers.mock_broker import MockBroker
from api.broker_integration.brokers.alpaca_broker import AlpacaBroker

# Configure logging
logger = logging.getLogger(__name__)

# Map of broker types to their implementation classes
BROKER_CLASSES = {
    "mock": MockBroker,
    "alpaca": AlpacaBroker,
    # Add more brokers as they are implemented
}

def create_broker(broker_type: str, config: Dict[str, Any]) -> Optional[BrokerInterface]:
    """
    Create and return a broker instance of the specified type with the given configuration.
    
    Args:
        broker_type: The type of broker to create (e.g., 'mock', 'alpaca')
        config: The configuration dictionary for the broker
        
    Returns:
        An instance of the appropriate broker implementation, or None if the broker type is invalid
    """
    # Sanitize broker type
    broker_type = broker_type.lower()
    
    # Check if the broker type is supported
    if broker_type not in BROKER_CLASSES:
        logger.error(f"Unsupported broker type: {broker_type}")
        # Return a mock broker as fallback
        return MockBroker({})
    
    try:
        # Create an instance of the appropriate broker class
        broker_class = BROKER_CLASSES[broker_type]
        broker = broker_class(config)
        logger.info(f"Created broker of type: {broker_type}")
        return broker
    except Exception as e:
        logger.error(f"Error creating broker of type {broker_type}: {str(e)}")
        # Return a mock broker as fallback
        return MockBroker({}) 