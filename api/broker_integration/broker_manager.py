import os
import logging
from typing import Dict, Optional, Any
import json

from .broker_interface import BrokerInterface
from .mock_broker import MockBroker
from .alpaca_broker import AlpacaBroker

logger = logging.getLogger(__name__)

class BrokerManager:
    """Manages different broker implementations and provides a unified interface"""
    
    def __init__(self, config_file: str = "broker_config.json"):
        """Initialize the broker manager with the broker configuration."""
        self.config_file = config_file
        self.config = self._load_config()
        self.active_broker_name = self.config.get("active_broker", "mock")
        self.brokers: Dict[str, BrokerInterface] = {}
        
        # Initialize brokers
        self._initialize_brokers()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load broker configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading broker config: {e}")
        
        # Return default config if file doesn't exist or there was an error
        return {
            "active_broker": "mock",
            "brokers": {
                "mock": {
                    "type": "mock",
                    "initial_balance": 100000.0
                },
                "alpaca": {
                    "type": "alpaca",
                    "api_key": os.environ.get("ALPACA_API_KEY", ""),
                    "api_secret": os.environ.get("ALPACA_API_SECRET", ""),
                    "is_paper": True
                }
            }
        }
    
    def _save_config(self):
        """Save broker configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving broker config: {e}")
    
    def _initialize_brokers(self):
        """Initialize broker instances based on configuration."""
        broker_configs = self.config.get("brokers", {})
        
        # Initialize mock broker
        mock_config = broker_configs.get("mock", {"type": "mock", "initial_balance": 100000.0})
        self.brokers["mock"] = MockBroker(initial_balance=mock_config.get("initial_balance", 100000.0))
        
        # Initialize Alpaca broker
        alpaca_config = broker_configs.get("alpaca", {
            "type": "alpaca",
            "api_key": os.environ.get("ALPACA_API_KEY", ""),
            "api_secret": os.environ.get("ALPACA_API_SECRET", ""),
            "is_paper": True
        })
        self.brokers["alpaca"] = AlpacaBroker(
            api_key=alpaca_config.get("api_key"),
            api_secret=alpaca_config.get("api_secret"),
            is_paper=alpaca_config.get("is_paper", True)
        )
    
    def get_broker(self, broker_name: Optional[str] = None) -> BrokerInterface:
        """Get the specified broker or the active broker if none specified."""
        name = broker_name or self.active_broker_name
        
        # Return the requested broker or fall back to mock if not found
        if name in self.brokers:
            return self.brokers[name]
        else:
            logger.warning(f"Broker '{name}' not found, falling back to mock")
            return self.brokers["mock"]
    
    def set_active_broker(self, broker_name: str) -> bool:
        """Set the active broker."""
        if broker_name not in self.brokers:
            logger.error(f"Broker '{broker_name}' not found")
            return False
        
        self.active_broker_name = broker_name
        self.config["active_broker"] = broker_name
        self._save_config()
        logger.info(f"Active broker set to '{broker_name}'")
        return True
    
    def get_available_brokers(self) -> Dict[str, str]:
        """Get a dictionary of available broker names and their types."""
        return {
            broker_name: broker.__class__.__name__
            for broker_name, broker in self.brokers.items()
        }
    
    def update_broker_config(self, broker_name: str, config: Dict[str, Any]) -> bool:
        """Update the configuration for a specific broker."""
        if broker_name not in self.config.get("brokers", {}):
            logger.error(f"Broker '{broker_name}' not found in config")
            return False
        
        # Update config
        self.config["brokers"][broker_name].update(config)
        self._save_config()
        
        # Reinitialize the broker
        if broker_name == "mock":
            self.brokers["mock"] = MockBroker(initial_balance=config.get("initial_balance", 100000.0))
        elif broker_name == "alpaca":
            self.brokers["alpaca"] = AlpacaBroker(
                api_key=config.get("api_key"),
                api_secret=config.get("api_secret"),
                is_paper=config.get("is_paper", True)
            )
        
        logger.info(f"Updated configuration for broker '{broker_name}'")
        return True 