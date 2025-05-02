"""
Base module for broker integration.
Defines the base class and interfaces that all broker implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

class BrokerBase(ABC):
    """
    Abstract base class that defines the interface for all broker implementations.
    Any broker integration must inherit from this class and implement its methods.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the broker with configuration parameters.
        
        Args:
            config: Dictionary containing broker-specific configuration
        """
        self.config = config
        self.name = "base"
        self.connected = False
        logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the broker's API.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the broker's API.
        
        Returns:
            bool: True if disconnection is successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Dict containing account information (balance, positions, etc.)
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions.
        
        Returns:
            List of dictionaries containing position information
        """
        pass
    
    @abstractmethod
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders with optional filtering by status.
        
        Args:
            status: Filter orders by status (open, closed, etc.)
            
        Returns:
            List of dictionaries containing order information
        """
        pass
    
    @abstractmethod
    def place_order(self, 
                   symbol: str, 
                   quantity: float, 
                   side: str, 
                   order_type: str = "market",
                   limit_price: Optional[float] = None,
                   stop_price: Optional[float] = None,
                   time_in_force: str = "day") -> Dict[str, Any]:
        """
        Place an order with the broker.
        
        Args:
            symbol: Asset symbol
            quantity: Order quantity
            side: Order side ('buy' or 'sell')
            order_type: Order type ('market', 'limit', 'stop', 'stop_limit')
            limit_price: Limit price for limit and stop-limit orders
            stop_price: Stop price for stop and stop-limit orders
            time_in_force: Time in force ('day', 'gtc', 'ioc', 'fok')
            
        Returns:
            Dict containing order information
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            bool: True if cancellation is successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_asset(self, symbol: str) -> Dict[str, Any]:
        """
        Get information about an asset.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Dict containing asset information
        """
        pass
    
    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get current quote for an asset.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Dict containing quote information (bid, ask, etc.)
        """
        pass
    
    @abstractmethod
    def get_bars(self, 
                symbol: str, 
                timeframe: str = "1Day", 
                start: Optional[datetime] = None, 
                end: Optional[datetime] = None,
                limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get historical price bars for an asset.
        
        Args:
            symbol: Asset symbol
            timeframe: Bar timeframe ('1Min', '5Min', '15Min', '1Hour', '1Day', etc.)
            start: Start datetime
            end: End datetime
            limit: Maximum number of bars to return
            
        Returns:
            List of dictionaries containing bar data
        """
        pass
    
    def is_connected(self) -> bool:
        """
        Check if the broker is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.connected
    
    def get_name(self) -> str:
        """
        Get the broker's name.
        
        Returns:
            str: Broker name
        """
        return self.name 