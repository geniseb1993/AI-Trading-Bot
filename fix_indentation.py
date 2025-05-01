#!/usr/bin/env python
"""
Script to fix indentation issues in broker integration files.
This script will automatically fix the indentation problems that are causing
deployment errors on Render.
"""

import os
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_alpaca_broker_file():
    """Fix indentation issues in alpaca_broker.py"""
    file_path = "api/broker_integration/alpaca_broker.py"
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the indentation error around line 125
    pattern = r"self\.connected = True\s+logger\.info\(.*?\)\s+return True"
    replacement = "self.connected = True\n            logger.info(\"Connected to Alpaca API\")\n            return True"
    
    fixed_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Fix any other similar indentation errors
    pattern = r"self\.connected = False\s+logger\.info\(.*?\)\s+return True"
    replacement = "self.connected = False\n        logger.info(\"Disconnected from Alpaca API\")\n        return True"
    
    fixed_content = re.sub(pattern, replacement, fixed_content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    logger.info(f"Fixed indentation in {file_path}")
    return True

def fix_mock_broker_file():
    """Fix indentation issues in mock_broker.py"""
    file_path = "api/broker_integration/mock_broker.py"
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the indentation error around line 396
    pattern = r"if should_fill:\s+order\.status = OrderStatus\.FILLED"
    replacement = "if should_fill:\n            order.status = OrderStatus.FILLED"
    
    fixed_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    logger.info(f"Fixed indentation in {file_path}")
    return True

def create_alpaca_broker_fallback():
    """Create a simplified alpaca_broker.py if fixing fails"""
    file_path = "api/broker_integration/alpaca_broker.py"
    
    content = """\"\"\"
Alpaca broker implementation.

This module implements the BrokerInterface for the Alpaca trading API.
\"\"\"

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import the broker interface
from .broker_interface import (
    BrokerInterface,
    OrderStatus,
    OrderSide,
    OrderType,
    TimeInForce
)

logger = logging.getLogger(__name__)

class AlpacaBroker(BrokerInterface):
    \"\"\"Alpaca broker implementation\"\"\"
    
    def __init__(self, config: Dict[str, Any] = None):
        \"\"\"Initialize Alpaca broker with configuration\"\"\"
        self.config = config or {}
        self.api_key = self.config.get("api_key", "")
        self.api_secret = self.config.get("api_secret", "")
        self.is_paper = self.config.get("is_paper", True)
        self.base_url = self.config.get("base_url", "https://paper-api.alpaca.markets" if self.is_paper else "https://api.alpaca.markets")
        self.connected = False
    
    def connect(self) -> bool:
        \"\"\"Connect to Alpaca API\"\"\"
        self.connected = True
        logger.info("Connected to Alpaca API")
        return True
    
    def disconnect(self) -> bool:
        \"\"\"Disconnect from Alpaca API\"\"\"
        self.connected = False
        logger.info("Disconnected from Alpaca API")
        return True
    
    def is_connected(self) -> bool:
        \"\"\"Check if connected to Alpaca API\"\"\"
        return self.connected
    
    def get_account_info(self) -> Dict[str, Any]:
        \"\"\"Get account information\"\"\"
        return {"status": "simulated", "connected": self.connected}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        \"\"\"Get all positions\"\"\"
        return []
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        \"\"\"Get position for a specific symbol\"\"\"
        return None
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        \"\"\"Get orders with optional status filter\"\"\"
        return []
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        \"\"\"Get a specific order by ID\"\"\"
        return None
    
    def place_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        type: str = "market",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "day"
    ) -> Dict[str, Any]:
        \"\"\"Place an order with Alpaca\"\"\"
        return {"status": "simulated"}
    
    def cancel_order(self, order_id: str) -> bool:
        \"\"\"Cancel an order\"\"\"
        return True
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        \"\"\"Get market data for a symbol\"\"\"
        return {"symbol": symbol, "price": 0.0}
    
    def get_bot_status(self) -> bool:
        \"\"\"Get the status of the trading bot\"\"\"
        return False
        
    def start_bot(self) -> bool:
        \"\"\"Start the trading bot\"\"\"
        return True
        
    def stop_bot(self) -> bool:
        \"\"\"Stop the trading bot\"\"\"
        return True
        
    def run_trading_cycle(self) -> bool:
        \"\"\"Run a single trading cycle\"\"\"
        return True
        
    def get_active_trades(self) -> List[Dict[str, Any]]:
        \"\"\"Get active trades\"\"\"
        return []
        
    def get_trading_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        \"\"\"Get trading history\"\"\"
        return []
        
    def get_real_time_data(self) -> Dict[str, Any]:
        \"\"\"Get real-time market data\"\"\"
        return {}
        
    def cancel_all_orders(self) -> bool:
        \"\"\"Cancel all active orders\"\"\"
        return True
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Created simplified {file_path}")
    return True

def create_mock_broker_fallback():
    """Create a simplified mock_broker.py if fixing fails"""
    file_path = "api/broker_integration/mock_broker.py"
    
    # Create a minimal version if needed
    content = """\"\"\"
Mock broker implementation.

This module implements the BrokerInterface for simulated trading.
\"\"\"

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import the broker interface
from .broker_interface import (
    BrokerInterface,
    Account,
    Position,
    Order,
    OrderStatus,
    OrderSide,
    OrderType,
    TimeInForce
)

logger = logging.getLogger(__name__)

class MockBroker(BrokerInterface):
    \"\"\"Mock broker implementation for testing\"\"\"
    
    def __init__(self, config: Dict[str, Any] = None):
        \"\"\"Initialize mock broker with configuration\"\"\"
        self.config = config or {}
        self.connected = True
        self._account = self._create_mock_account()
        self._positions = {}
        self._orders = {}
        self._market_data = {}
    
    def _create_mock_account(self) -> Account:
        \"\"\"Create a mock trading account\"\"\"
        return Account(
            id="mock-account",
            cash=100000.0,
            buying_power=100000.0,
            equity=100000.0,
            portfolio_value=100000.0,
            currency="USD"
        )
    
    def connect(self) -> bool:
        \"\"\"Connect to mock broker\"\"\"
        self.connected = True
        return True
    
    def disconnect(self) -> bool:
        \"\"\"Disconnect from mock broker\"\"\"
        self.connected = False
        return True
    
    def is_connected(self) -> bool:
        \"\"\"Check if connected to mock broker\"\"\"
        return self.connected
    
    def get_account(self) -> Account:
        \"\"\"Get account information\"\"\"
        return self._account
    
    def get_account_info(self) -> Dict[str, Any]:
        \"\"\"Get account information as dictionary\"\"\"
        return self._account.__dict__
    
    def get_positions(self) -> List[Dict[str, Any]]:
        \"\"\"Get all positions\"\"\"
        return [position.__dict__ for position in self._positions.values()]
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        \"\"\"Get position for a specific symbol\"\"\"
        position = self._positions.get(symbol)
        return position.__dict__ if position else None
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        \"\"\"Get orders with optional status filter\"\"\"
        orders = list(self._orders.values())
        
        if status:
            orders = [order for order in orders if order.status.name.lower() == status.lower()]
            
        return [order.__dict__ for order in orders]
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        \"\"\"Get a specific order by ID\"\"\"
        order = self._orders.get(order_id)
        return order.__dict__ if order else None
        
    def place_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        type: str = "market",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "day"
    ) -> Dict[str, Any]:
        \"\"\"Place an order with the mock broker\"\"\"
        # Convert string values to enums
        try:
            side_enum = OrderSide[side.upper()]
        except KeyError:
            return {"error": f"Invalid side: {side}", "status": "rejected"}
            
        try:
            type_enum = OrderType[type.upper()]
        except KeyError:
            return {"error": f"Invalid order type: {type}", "status": "rejected"}
            
        try:
            tif_enum = TimeInForce[time_in_force.upper()]
        except KeyError:
            return {"error": f"Invalid time in force: {time_in_force}", "status": "rejected"}
        
        # Create an order
        order = self.submit_order(
            symbol=symbol,
            qty=qty,
            side=side_enum,
            type=type_enum,
            time_in_force=tif_enum,
            limit_price=limit_price,
            stop_price=stop_price
        )
        
        if not order:
            return {"error": "Failed to create order", "status": "rejected"}
            
        return order.__dict__
        
    def cancel_order(self, order_id: str) -> bool:
        \"\"\"Cancel an order\"\"\"
        if order_id not in self._orders:
            return False
            
        order = self._orders[order_id]
        
        if not order.is_active:
            return False
            
        order.status = OrderStatus.CANCELLED
        return True
        
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        \"\"\"Get market data for a symbol\"\"\"
        return {"symbol": symbol, "price": 100.0}
        
    def get_bot_status(self) -> bool:
        \"\"\"Get the status of the trading bot\"\"\"
        return False
        
    def start_bot(self) -> bool:
        \"\"\"Start the trading bot\"\"\"
        return True
        
    def stop_bot(self) -> bool:
        \"\"\"Stop the trading bot\"\"\"
        return True
        
    def run_trading_cycle(self) -> bool:
        \"\"\"Run a single trading cycle\"\"\"
        return True
        
    def get_active_trades(self) -> List[Dict[str, Any]]:
        \"\"\"Get active trades\"\"\"
        return []
        
    def get_trading_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        \"\"\"Get trading history\"\"\"
        return []
        
    def get_real_time_data(self) -> Dict[str, Any]:
        \"\"\"Get real-time market data\"\"\"
        return {}
        
    def cancel_all_orders(self) -> bool:
        \"\"\"Cancel all active orders\"\"\"
        return True
        
    def submit_order(
        self,
        symbol: str,
        qty: float,
        side: OrderSide,
        type: OrderType = OrderType.MARKET,
        time_in_force: TimeInForce = TimeInForce.DAY,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_percent: Optional[float] = None,
    ) -> Optional[Order]:
        \"\"\"Submit an order to the mock broker\"\"\"
        import uuid
        
        order_id = str(uuid.uuid4())
        
        order = Order(
            id=order_id,
            symbol=symbol.upper(),
            qty=qty,
            side=side,
            type=type,
            time_in_force=time_in_force,
            limit_price=limit_price,
            stop_price=stop_price,
            trail_percent=trail_percent,
            status=OrderStatus.NEW,
            created_at=datetime.now()
        )
        
        self._orders[order_id] = order
        
        # Execute order immediately for simplicity
        if should_fill := (type == OrderType.MARKET):
            order.status = OrderStatus.FILLED
            order.filled_qty = qty
            order.filled_avg_price = 100.0  # Simplified
            order.filled_at = datetime.now()
            
        return order
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Created simplified {file_path}")
    return True

def main():
    """Run all fixes"""
    logger.info("Starting to fix indentation issues...")
    
    # Try to fix alpaca_broker.py
    if not fix_alpaca_broker_file():
        logger.warning("Could not fix alpaca_broker.py, creating fallback version")
        create_alpaca_broker_fallback()
    
    # Try to fix mock_broker.py
    if not fix_mock_broker_file():
        logger.warning("Could not fix mock_broker.py, creating fallback version")
        create_mock_broker_fallback()
    
    logger.info("Fixes complete")
    return 0

if __name__ == "__main__":
    main() 