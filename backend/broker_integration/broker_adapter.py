"""
Broker Adapter Module

This module provides a unified interface to interact with different broker implementations.
It serves as a bridge between the application and the specific broker APIs.
"""

import logging
from typing import Dict, List, Optional, Any, Union
import os
import json

from .broker_interface import BrokerInterface, Order, Position, Account, OrderSide, OrderType, TimeInForce, OrderStatus
from .broker_manager import BrokerManager
from .config import load_config, get_active_broker_config

logger = logging.getLogger(__name__)

class BrokerAdapter:
    """
    Adapter class that provides a unified interface for interacting with different brokers.
    This class manages the connection to the broker and handles all trading operations.
    """
    
    def __init__(self, broker_name: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the broker adapter.
        
        Args:
            broker_name: Name of the broker to use. If None, uses the active broker from config.
            config_path: Path to the broker configuration file. If None, uses default.
        """
        self.config = load_config(config_path)
        self.broker_manager = BrokerManager(config_file=config_path or "broker_config.json")
        
        if broker_name:
            self.broker = self.broker_manager.get_broker(broker_name)
        else:
            self.broker = self.broker_manager.get_broker()
        
        # Connect to the broker
        self.connect()
    
    def connect(self) -> bool:
        """
        Connect to the broker's API.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            result = self.broker.connect()
            if result:
                logger.info(f"Successfully connected to broker: {self.broker.__class__.__name__}")
            else:
                logger.error(f"Failed to connect to broker: {self.broker.__class__.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error connecting to broker: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from the broker's API.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            result = self.broker.disconnect()
            if result:
                logger.info(f"Successfully disconnected from broker: {self.broker.__class__.__name__}")
            else:
                logger.error(f"Failed to disconnect from broker: {self.broker.__class__.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error disconnecting from broker: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if the broker is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            return self.broker.is_connected()
        except Exception as e:
            logger.error(f"Error checking connection status: {str(e)}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information from the broker.
        
        Returns:
            Dict containing account information
        """
        try:
            return self.broker.get_account_info()
        except Exception as e:
            logger.error(f"Error retrieving account info: {str(e)}")
            return {
                "error": str(e),
                "status": "error",
                "cash": 0.0,
                "portfolio_value": 0.0,
                "buying_power": 0.0
            }
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all positions from the broker.
        
        Returns:
            List of dictionaries containing position information
        """
        try:
            return self.broker.get_positions()
        except Exception as e:
            logger.error(f"Error retrieving positions: {str(e)}")
            return []
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get position for a specific symbol.
        
        Args:
            symbol: Symbol to get position for
            
        Returns:
            Dictionary containing position information or None if position not found
        """
        try:
            return self.broker.get_position(symbol)
        except Exception as e:
            logger.error(f"Error retrieving position for {symbol}: {str(e)}")
            return None
    
    def place_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        order_type: str = "market",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "day"
    ) -> Dict[str, Any]:
        """
        Place an order with the broker.
        
        Args:
            symbol: Symbol to trade
            qty: Quantity to trade
            side: Order side ("buy" or "sell")
            order_type: Order type ("market", "limit", "stop", "stop_limit")
            limit_price: Limit price for limit orders
            stop_price: Stop price for stop orders
            time_in_force: Time in force ("day", "gtc", "ioc", "fok")
            
        Returns:
            Dictionary containing order information
        """
        try:
            return self.broker.place_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                limit_price=limit_price,
                stop_price=stop_price,
                time_in_force=time_in_force
            )
        except Exception as e:
            logger.error(f"Error placing order for {symbol}: {str(e)}")
            return {
                "error": str(e),
                "status": "error",
                "id": None,
                "symbol": symbol,
                "qty": qty,
                "side": side
            }
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order with the broker.
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        try:
            return self.broker.cancel_order(order_id)
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {str(e)}")
            return False
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders from the broker.
        
        Args:
            status: Filter by order status
            
        Returns:
            List of dictionaries containing order information
        """
        try:
            return self.broker.get_orders(status)
        except Exception as e:
            logger.error(f"Error retrieving orders: {str(e)}")
            return []
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific order from the broker.
        
        Args:
            order_id: ID of the order to retrieve
            
        Returns:
            Dictionary containing order information or None if order not found
        """
        try:
            return self.broker.get_order(order_id)
        except Exception as e:
            logger.error(f"Error retrieving order {order_id}: {str(e)}")
            return None
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get market data for a specific symbol.
        
        Args:
            symbol: Symbol to get market data for
            
        Returns:
            Dictionary containing market data
        """
        try:
            return self.broker.get_market_data(symbol)
        except Exception as e:
            logger.error(f"Error retrieving market data for {symbol}: {str(e)}")
            return {
                "error": str(e),
                "symbol": symbol,
                "last_price": None,
                "bid": None,
                "ask": None
            }
    
    def switch_broker(self, broker_name: str) -> bool:
        """
        Switch to a different broker.
        
        Args:
            broker_name: Name of the broker to switch to
            
        Returns:
            bool: True if switch successful, False otherwise
        """
        try:
            # Disconnect from current broker
            self.disconnect()
            
            # Get new broker and connect
            self.broker = self.broker_manager.get_broker(broker_name)
            result = self.connect()
            
            if result:
                # Update active broker in config
                self.broker_manager.set_active_broker(broker_name)
                logger.info(f"Successfully switched to broker: {broker_name}")
            else:
                logger.error(f"Failed to connect to broker: {broker_name}")
            
            return result
        except Exception as e:
            logger.error(f"Error switching to broker {broker_name}: {str(e)}")
            return False
    
    def get_available_brokers(self) -> Dict[str, str]:
        """
        Get a list of available brokers.
        
        Returns:
            Dictionary mapping broker names to their types
        """
        return self.broker_manager.get_available_brokers() 