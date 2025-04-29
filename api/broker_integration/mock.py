"""
Mock broker implementation for testing and development.
Simulates a broker API without making actual API calls.
"""

import logging
import random
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from .base import BrokerBase

# Configure logging
logger = logging.getLogger(__name__)

class MockBroker(BrokerBase):
    """
    Mock broker implementation for testing and development.
    Simulates a broker API with in-memory storage.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the mock broker with configuration.
        
        Args:
            config: Dictionary with mock broker configuration
        """
        super().__init__(config)
        self.name = "mock"
        self.connected = False
        
        # Initialize mock data structures
        self.account = {
            "id": "mock-account-" + str(uuid.uuid4()),
            "cash": config.get("initial_balance", 100000.0),
            "equity": config.get("initial_balance", 100000.0),
            "buying_power": config.get("initial_balance", 100000.0) * 2,  # 2x margin
            "currency": "USD",
            "status": "ACTIVE",
            "created_at": datetime.now().isoformat()
        }
        
        self.positions = {}  # symbol -> position
        self.orders = {}     # order_id -> order
        self.assets = self._initialize_assets()
        
        # Simulated latency
        self.simulate_latency = config.get("simulate_latency", True)
        self.latency_ms = config.get("latency_ms", 500)
        
        logger.info(f"Initialized {self.__class__.__name__} with balance: ${self.account['cash']}")
    
    def connect(self) -> bool:
        """
        Simulate connecting to the broker API.
        
        Returns:
            bool: True if connection successful
        """
        # Simulate connection delay
        self._apply_latency()
        
        self.connected = True
        logger.info("Connected to mock broker API")
        return True
    
    def disconnect(self) -> bool:
        """
        Simulate disconnecting from the broker API.
        
        Returns:
            bool: True if disconnection successful
        """
        # Simulate disconnection delay
        self._apply_latency()
        
        self.connected = False
        logger.info("Disconnected from mock broker API")
        return True
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get mock account information.
        
        Returns:
            Dict with account information
        """
        self._check_connection()
        self._apply_latency()
        
        # Update equity based on positions
        total_position_value = sum(
            position["quantity"] * self._get_current_price(position["symbol"])
            for position in self.positions.values()
        )
        
        self.account["equity"] = self.account["cash"] + total_position_value
        self.account["buying_power"] = self.account["cash"] * 2  # 2x margin
        
        return self.account
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions.
        
        Returns:
            List of position dictionaries
        """
        self._check_connection()
        self._apply_latency()
        
        # Update market values of positions
        for symbol, position in self.positions.items():
            current_price = self._get_current_price(symbol)
            position["current_price"] = current_price
            position["market_value"] = position["quantity"] * current_price
            position["profit_loss"] = position["market_value"] - position["cost_basis"]
            position["profit_loss_pct"] = (
                (position["profit_loss"] / position["cost_basis"]) * 100 
                if position["cost_basis"] > 0 else 0
            )
            
        return list(self.positions.values())
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders with optional status filtering.
        
        Args:
            status: Filter by order status ('open', 'filled', 'canceled', etc.)
            
        Returns:
            List of order dictionaries
        """
        self._check_connection()
        self._apply_latency()
        
        if status:
            return [
                order for order in self.orders.values() 
                if order["status"].lower() == status.lower()
            ]
        
        return list(self.orders.values())
    
    def place_order(self,
                   symbol: str,
                   quantity: float,
                   side: str,
                   order_type: str = "market",
                   limit_price: Optional[float] = None,
                   stop_price: Optional[float] = None,
                   time_in_force: str = "day") -> Dict[str, Any]:
        """
        Place a mock order.
        
        Args:
            symbol: Asset symbol
            quantity: Order quantity
            side: Order side ('buy' or 'sell')
            order_type: Order type ('market', 'limit', 'stop', 'stop_limit')
            limit_price: Limit price for limit orders
            stop_price: Stop price for stop orders
            time_in_force: Time in force ('day', 'gtc', 'ioc', 'fok')
            
        Returns:
            Dict with order information
        """
        self._check_connection()
        self._apply_latency()
        
        # Validate inputs
        symbol = symbol.upper()
        side = side.lower()
        order_type = order_type.lower()
        time_in_force = time_in_force.lower()
        
        if side not in ["buy", "sell"]:
            raise ValueError(f"Invalid order side: {side}. Must be 'buy' or 'sell'")
            
        if order_type not in ["market", "limit", "stop", "stop_limit"]:
            raise ValueError(f"Invalid order type: {order_type}")
            
        if order_type in ["limit", "stop_limit"] and limit_price is None:
            raise ValueError(f"Limit price required for {order_type} orders")
            
        if order_type in ["stop", "stop_limit"] and stop_price is None:
            raise ValueError(f"Stop price required for {order_type} orders")
            
        if time_in_force not in ["day", "gtc", "ioc", "fok"]:
            raise ValueError(f"Invalid time in force: {time_in_force}")
            
        # Create order
        current_price = self._get_current_price(symbol)
        order_id = f"mock-order-{str(uuid.uuid4())}"
        
        order = {
            "id": order_id,
            "client_order_id": f"client-{order_id}",
            "symbol": symbol,
            "quantity": quantity,
            "filled_quantity": 0,
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
            "limit_price": limit_price,
            "stop_price": stop_price,
            "status": "new",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "filled_at": None,
            "expired_at": None,
            "canceled_at": None,
            "failed_at": None,
            "fill_price": None,
            "average_price": None
        }
        
        self.orders[order_id] = order
        
        # Process market orders immediately
        if order_type == "market":
            self._process_order(order_id)
        
        logger.info(f"Placed {order_type} {side} order for {quantity} {symbol}")
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a mock order.
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        self._check_connection()
        self._apply_latency()
        
        if order_id not in self.orders:
            logger.warning(f"Order {order_id} not found")
            return False
            
        order = self.orders[order_id]
        
        if order["status"] in ["filled", "canceled", "expired", "failed"]:
            logger.warning(f"Cannot cancel order {order_id} with status: {order['status']}")
            return False
            
        order["status"] = "canceled"
        order["canceled_at"] = datetime.now().isoformat()
        order["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Canceled order {order_id}")
        return True
    
    def get_asset(self, symbol: str) -> Dict[str, Any]:
        """
        Get information about a mock asset.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Dict with asset information
        """
        self._check_connection()
        self._apply_latency()
        
        symbol = symbol.upper()
        
        if symbol not in self.assets:
            logger.warning(f"Asset {symbol} not found")
            raise ValueError(f"Asset {symbol} not found")
            
        return self.assets[symbol]
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get current quote for a mock asset.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Dict with quote information
        """
        self._check_connection()
        self._apply_latency()
        
        symbol = symbol.upper()
        
        if symbol not in self.assets:
            logger.warning(f"Asset {symbol} not found")
            raise ValueError(f"Asset {symbol} not found")
            
        current_price = self._get_current_price(symbol)
        bid_price = current_price * (1 - random.uniform(0.0001, 0.0005))
        ask_price = current_price * (1 + random.uniform(0.0001, 0.0005))
        
        quote = {
            "symbol": symbol,
            "bid_price": round(bid_price, 2),
            "bid_size": random.randint(100, 10000),
            "ask_price": round(ask_price, 2),
            "ask_size": random.randint(100, 10000),
            "last_price": round(current_price, 2),
            "last_size": random.randint(1, 100),
            "last_trade_time": datetime.now().isoformat(),
            "quote_time": datetime.now().isoformat()
        }
        
        return quote
    
    def get_bars(self,
                symbol: str,
                timeframe: str = "1Day",
                start: Optional[datetime] = None,
                end: Optional[datetime] = None,
                limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get historical price bars for a mock asset.
        
        Args:
            symbol: Asset symbol
            timeframe: Bar timeframe ('1Min', '5Min', '15Min', '1Hour', '1Day', etc.)
            start: Start datetime
            end: End datetime
            limit: Maximum number of bars to return
            
        Returns:
            List of dictionaries with bar data
        """
        self._check_connection()
        self._apply_latency()
        
        symbol = symbol.upper()
        
        if symbol not in self.assets:
            logger.warning(f"Asset {symbol} not found")
            raise ValueError(f"Asset {symbol} not found")
            
        if end is None:
            end = datetime.now()
            
        if start is None:
            # Calculate start based on timeframe and limit
            if timeframe == "1Min":
                start = end - timedelta(minutes=limit)
            elif timeframe == "5Min":
                start = end - timedelta(minutes=5*limit)
            elif timeframe == "15Min":
                start = end - timedelta(minutes=15*limit)
            elif timeframe == "1Hour":
                start = end - timedelta(hours=limit)
            elif timeframe == "1Day":
                start = end - timedelta(days=limit)
            else:
                # Default to 100 days
                start = end - timedelta(days=limit)
                
        # Generate mock bars
        bars = []
        current_time = start
        base_price = self.assets[symbol]["price"]
        volatility = self.assets[symbol].get("volatility", 0.02)  # Default 2% volatility
        
        while current_time < end and len(bars) < limit:
            # Generate random price movement
            price_change = base_price * volatility * (random.random() - 0.5)
            open_price = base_price + price_change
            high_price = open_price * (1 + random.uniform(0, 0.01))
            low_price = open_price * (1 - random.uniform(0, 0.01))
            close_price = (open_price + high_price + low_price) / 3  # Random close
            volume = random.randint(1000, 1000000)
            
            bar = {
                "symbol": symbol,
                "timestamp": current_time.isoformat(),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            }
            
            bars.append(bar)
            
            # Update base price for next bar
            base_price = close_price
            
            # Increment time based on timeframe
            if timeframe == "1Min":
                current_time += timedelta(minutes=1)
            elif timeframe == "5Min":
                current_time += timedelta(minutes=5)
            elif timeframe == "15Min":
                current_time += timedelta(minutes=15)
            elif timeframe == "1Hour":
                current_time += timedelta(hours=1)
            elif timeframe == "1Day":
                current_time += timedelta(days=1)
            else:
                current_time += timedelta(days=1)
                
        return bars
    
    # Helper methods
    def _check_connection(self):
        """Check if broker is connected and raise exception if not."""
        if not self.connected:
            raise RuntimeError("Not connected to mock broker API. Call connect() first.")
    
    def _apply_latency(self):
        """Simulate API latency if enabled."""
        if self.simulate_latency:
            latency = random.uniform(0, self.latency_ms / 1000)  # Convert to seconds
            time.sleep(latency)
    
    def _process_order(self, order_id: str):
        """Process a pending order (simulated execution)."""
        if order_id not in self.orders:
            return
            
        order = self.orders[order_id]
        
        # Only process orders that are new/pending
        if order["status"] not in ["new", "pending"]:
            return
            
        symbol = order["symbol"]
        side = order["side"]
        quantity = order["quantity"]
        order_type = order["type"]
        
        current_price = self._get_current_price(symbol)
        
        # Check if limit/stop conditions are met
        execute_order = False
        
        if order_type == "market":
            execute_order = True
        elif order_type == "limit":
            if side == "buy" and current_price <= order["limit_price"]:
                execute_order = True
            elif side == "sell" and current_price >= order["limit_price"]:
                execute_order = True
        elif order_type == "stop":
            if side == "buy" and current_price >= order["stop_price"]:
                execute_order = True
            elif side == "sell" and current_price <= order["stop_price"]:
                execute_order = True
        elif order_type == "stop_limit":
            # First check if stop is triggered
            if side == "buy" and current_price >= order["stop_price"]:
                # Then check limit condition
                if current_price <= order["limit_price"]:
                    execute_order = True
            elif side == "sell" and current_price <= order["stop_price"]:
                # Then check limit condition
                if current_price >= order["limit_price"]:
                    execute_order = True
                    
        if not execute_order:
            # Update order status to pending if it was new
            if order["status"] == "new":
                order["status"] = "pending"
                order["updated_at"] = datetime.now().isoformat()
            return
            
        # Add small price improvement/slippage
        slippage = current_price * random.uniform(-0.001, 0.001)
        fill_price = current_price + slippage
        
        # Execute the order
        order["status"] = "filled"
        order["filled_quantity"] = quantity
        order["fill_price"] = round(fill_price, 2)
        order["average_price"] = round(fill_price, 2)
        order["filled_at"] = datetime.now().isoformat()
        order["updated_at"] = datetime.now().isoformat()
        
        # Update account and positions
        order_value = quantity * fill_price
        
        if side == "buy":
            # Deduct cash for buy orders
            self.account["cash"] -= order_value
            
            # Update position
            if symbol in self.positions:
                position = self.positions[symbol]
                # Calculate weighted average cost basis
                total_shares = position["quantity"] + quantity
                total_cost = (position["quantity"] * position["average_price"]) + order_value
                position["quantity"] = total_shares
                position["average_price"] = total_cost / total_shares
                position["cost_basis"] = total_cost
                position["updated_at"] = datetime.now().isoformat()
            else:
                # Create new position
                self.positions[symbol] = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "average_price": fill_price,
                    "cost_basis": order_value,
                    "current_price": fill_price,
                    "market_value": order_value,
                    "profit_loss": 0,
                    "profit_loss_pct": 0,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
        elif side == "sell":
            # Add cash for sell orders
            self.account["cash"] += order_value
            
            # Update position
            if symbol in self.positions:
                position = self.positions[symbol]
                
                if quantity >= position["quantity"]:
                    # Selling entire position
                    del self.positions[symbol]
                else:
                    # Partial sell
                    position["quantity"] -= quantity
                    position["cost_basis"] = position["average_price"] * position["quantity"]
                    position["updated_at"] = datetime.now().isoformat()
            else:
                logger.warning(f"Attempted to sell {symbol} but no position exists")
                
        logger.info(f"Executed {side} order for {quantity} {symbol} at ${fill_price}")
    
    def _get_current_price(self, symbol: str) -> float:
        """Get simulated current price for a symbol."""
        symbol = symbol.upper()
        
        if symbol not in self.assets:
            return 0.0
            
        base_price = self.assets[symbol]["price"]
        volatility = self.assets[symbol].get("volatility", 0.02)  # Default 2% volatility
        
        # Add small random movement to simulate price changes
        price_change = base_price * volatility * (random.random() - 0.5)
        current_price = base_price + price_change
        
        # Update the asset price for next time
        self.assets[symbol]["price"] = current_price
        
        return current_price
    
    def _initialize_assets(self) -> Dict[str, Dict[str, Any]]:
        """Initialize a set of mock assets."""
        assets = {
            "AAPL": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "exchange": "NASDAQ",
                "price": 150.0,
                "volatility": 0.015,
                "tradable": True,
                "marginable": True,
                "shortable": True,
                "fractionable": True,
                "easy_to_borrow": True
            },
            "MSFT": {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "exchange": "NASDAQ",
                "price": 300.0,
                "volatility": 0.012,
                "tradable": True,
                "marginable": True,
                "shortable": True,
                "fractionable": True,
                "easy_to_borrow": True
            },
            "GOOGL": {
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "exchange": "NASDAQ",
                "price": 120.0,
                "volatility": 0.018,
                "tradable": True,
                "marginable": True,
                "shortable": True,
                "fractionable": True,
                "easy_to_borrow": True
            },
            "AMZN": {
                "symbol": "AMZN",
                "name": "Amazon.com Inc.",
                "exchange": "NASDAQ",
                "price": 140.0,
                "volatility": 0.02,
                "tradable": True,
                "marginable": True,
                "shortable": True,
                "fractionable": True,
                "easy_to_borrow": True
            },
            "TSLA": {
                "symbol": "TSLA",
                "name": "Tesla Inc.",
                "exchange": "NASDAQ",
                "price": 240.0,
                "volatility": 0.035,
                "tradable": True,
                "marginable": True,
                "shortable": True,
                "fractionable": True,
                "easy_to_borrow": True
            },
            "SPY": {
                "symbol": "SPY",
                "name": "SPDR S&P 500 ETF Trust",
                "exchange": "NYSE",
                "price": 440.0,
                "volatility": 0.008,
                "tradable": True,
                "marginable": True,
                "shortable": True,
                "fractionable": True,
                "easy_to_borrow": True
            }
        }
        
        return assets 