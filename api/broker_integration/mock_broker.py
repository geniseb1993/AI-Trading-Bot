import os
import json
import random
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .broker_interface import (
    BrokerInterface,
    Account,
    Position,
    Order,
    OrderStatus,
    OrderSide,
    OrderType,
    TimeInForce,
)

logger = logging.getLogger(__name__)

# Mock data for testing
MOCK_SYMBOLS = {
    "AAPL": {"price": 175.50, "name": "Apple Inc."},
    "MSFT": {"price": 345.20, "name": "Microsoft Corporation"},
    "AMZN": {"price": 145.30, "name": "Amazon.com, Inc."},
    "GOOGL": {"price": 152.80, "name": "Alphabet Inc."},
    "META": {"price": 505.40, "name": "Meta Platforms, Inc."},
    "TSLA": {"price": 205.60, "name": "Tesla, Inc."},
    "NVDA": {"price": 840.80, "name": "NVIDIA Corporation"},
    "BRK.B": {"price": 410.20, "name": "Berkshire Hathaway Inc."},
    "JPM": {"price": 198.75, "name": "JPMorgan Chase & Co."},
    "V": {"price": 278.40, "name": "Visa Inc."}
}

class MockBroker(BrokerInterface):
    """Mock broker implementation for testing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize mock broker with optional configuration"""
        self.config = config or {}
        self.connected = False
        self.data_dir = os.path.join("data", "broker", "mock")
        self._ensure_data_dir()
        
        # In-memory data storage
        self._account = self._create_mock_account()
        self._positions = {}
        self._orders = {}
        self._market_data = {}
        
        # Load saved data if available
        self._load_saved_data()
        self._generate_market_data()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _create_mock_account(self) -> Account:
        """Create mock account with default values"""
        return Account(
            id=str(uuid.uuid4()),
            cash=100000.0,
            portfolio_value=105000.0,
            buying_power=200000.0,
            equity=105000.0
        )
    
    def _load_saved_data(self):
        """Load saved mock broker data if available"""
        try:
            # Load positions
            positions_file = os.path.join(self.data_dir, "positions.json")
            if os.path.exists(positions_file):
                with open(positions_file, "r") as f:
                    positions_data = json.load(f)
                    self._positions = {
                        p["symbol"]: Position(
                            symbol=p["symbol"],
                            qty=float(p["qty"]),
                            avg_entry_price=float(p["avg_entry_price"]),
                            current_price=float(p["current_price"]),
                            side=OrderSide(p["side"])
                        )
                        for p in positions_data
                    }
            
            # Load orders
            orders_file = os.path.join(self.data_dir, "orders.json")
            if os.path.exists(orders_file):
                with open(orders_file, "r") as f:
                    orders_data = json.load(f)
                    self._orders = {
                        o["id"]: Order(
                            id=o["id"],
                            symbol=o["symbol"],
                            qty=float(o["qty"]),
                            side=OrderSide(o["side"]),
                            type=OrderType(o["type"]),
                            limit_price=float(o["limit_price"]) if o.get("limit_price") else None,
                            stop_price=float(o["stop_price"]) if o.get("stop_price") else None,
                            time_in_force=TimeInForce(o["time_in_force"]),
                            status=OrderStatus(o["status"]),
                            created_at=datetime.fromisoformat(o["created_at"]),
                            filled_at=datetime.fromisoformat(o["filled_at"]) if o.get("filled_at") else None,
                            filled_qty=float(o["filled_qty"]) if o.get("filled_qty") else 0.0,
                            filled_avg_price=float(o["filled_avg_price"]) if o.get("filled_avg_price") else None
                        )
                        for o in orders_data
                    }
            
            # Load account
            account_file = os.path.join(self.data_dir, "account.json")
            if os.path.exists(account_file):
                with open(account_file, "r") as f:
                    account_data = json.load(f)
                    self._account = Account(
                        id=account_data["id"],
                        cash=float(account_data["cash"]),
                        portfolio_value=float(account_data["portfolio_value"]),
                        buying_power=float(account_data["buying_power"]),
                        equity=float(account_data["equity"]),
                        currency=account_data.get("currency", "USD")
                    )
        except Exception as e:
            logger.error(f"Error loading saved mock broker data: {e}")
    
    def _save_data(self):
        """Save current mock broker data"""
        try:
            # Save positions
            positions_data = [
                {
                    "symbol": p.symbol,
                    "qty": p.qty,
                    "avg_entry_price": p.avg_entry_price,
                    "current_price": p.current_price,
                    "side": p.side.value
                }
                for p in self._positions.values()
            ]
            with open(os.path.join(self.data_dir, "positions.json"), "w") as f:
                json.dump(positions_data, f, indent=2)
            
            # Save orders
            orders_data = [
                {
                    "id": o.id,
                    "symbol": o.symbol,
                    "qty": o.qty,
                    "side": o.side.value,
                    "type": o.type.value,
                    "limit_price": o.limit_price,
                    "stop_price": o.stop_price,
                    "time_in_force": o.time_in_force.value,
                    "status": o.status.value,
                    "created_at": o.created_at.isoformat(),
                    "filled_at": o.filled_at.isoformat() if o.filled_at else None,
                    "filled_qty": o.filled_qty,
                    "filled_avg_price": o.filled_avg_price
                }
                for o in self._orders.values()
            ]
            with open(os.path.join(self.data_dir, "orders.json"), "w") as f:
                json.dump(orders_data, f, indent=2)
            
            # Save account
            account_data = {
                "id": self._account.id,
                "cash": self._account.cash,
                "portfolio_value": self._account.portfolio_value,
                "buying_power": self._account.buying_power,
                "equity": self._account.equity,
                "currency": self._account.currency
            }
            with open(os.path.join(self.data_dir, "account.json"), "w") as f:
                json.dump(account_data, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error saving mock broker data: {e}")
    
    def _generate_market_data(self):
        """Generate mock market data for common stocks"""
        symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", 
            "META", "NVDA", "NFLX", "AMD", "INTC"
        ]
        
        # Add symbols from positions if any
        for position in self._positions.values():
            if position.symbol not in symbols:
                symbols.append(position.symbol)
        
        for symbol in symbols:
            last_price = 100.0 + random.uniform(-50, 200)
            self._market_data[symbol] = {
                "symbol": symbol,
                "last_price": last_price,
                "bid": last_price - random.uniform(0.01, 0.5),
                "ask": last_price + random.uniform(0.01, 0.5),
                "volume": random.randint(10000, 1000000),
                "timestamp": datetime.now().isoformat(),
                "change": random.uniform(-5, 5),
                "change_percent": random.uniform(-5, 5)
            }
    
    def _update_market_data(self):
        """Update mock market data with random price movements"""
        for symbol, data in self._market_data.items():
            # Generate price movement between -2% and +2%
            price_change = data["last_price"] * random.uniform(-0.02, 0.02)
            new_price = data["last_price"] + price_change
            
            # Update market data
            data["last_price"] = new_price
            data["bid"] = new_price - random.uniform(0.01, 0.5)
            data["ask"] = new_price + random.uniform(0.01, 0.5)
            data["volume"] += random.randint(100, 10000)
            data["timestamp"] = datetime.now().isoformat()
            data["change"] = price_change
            data["change_percent"] = (price_change / (new_price - price_change)) * 100
        
        # Update position current prices
        for position in self._positions.values():
            if position.symbol in self._market_data:
                position.current_price = self._market_data[position.symbol]["last_price"]
    
    def connect(self) -> bool:
        """Connect to mock broker (always successful)"""
        self.connected = True
        logger.info("Connected to mock broker")
        return True
    
    def disconnect(self) -> bool:
        """Disconnect from mock broker"""
        self.connected = False
        logger.info("Disconnected from mock broker")
        return True
    
    def is_connected(self) -> bool:
        """Check if connected to mock broker"""
        return self.connected
    
    def get_account(self) -> Account:
        """Get account information"""
        # Update portfolio value based on positions
        positions_value = sum(p.market_value for p in self._positions.values())
        self._account.portfolio_value = self._account.cash + positions_value
        self._account.equity = self._account.portfolio_value
        return self._account
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information as dictionary"""
        account = self.get_account()
        return account.to_dict()
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions as dictionaries"""
        self._update_market_data()  # Update prices
        return [position.to_dict() for position in self._positions.values()]
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get position for a specific symbol as dictionary"""
        self._update_market_data()  # Update prices
        position = self._positions.get(symbol.upper())
        return position.to_dict() if position else None
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get orders with optional status filter as dictionaries"""
        orders = list(self._orders.values())
        
        # Filter by status if provided
        if status:
            try:
                status_enum = OrderStatus(status)
                orders = [o for o in orders if o.status == status_enum]
            except (ValueError, KeyError):
                # Invalid status, log and ignore filter
                logger.warning(f"Invalid order status filter: {status}")
        
        return [order.to_dict() for order in orders]
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific order by ID as dictionary"""
        order = self._orders.get(order_id)
        return order.to_dict() if order else None
    
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
        """
        Place an order with the mock broker.
        
        Args:
            symbol: Symbol to trade
            qty: Quantity to trade
            side: Order side ("buy" or "sell")
            type: Order type ("market", "limit", "stop", "stop_limit")
            limit_price: Limit price for limit orders
            stop_price: Stop price for stop orders
            time_in_force: Time in force ("day", "gtc", "ioc", "fok")
            
        Returns:
            Dict containing order information
        """
        # Convert string parameters to enums
        try:
            side_enum = OrderSide(side)
            type_enum = OrderType(type)
            time_in_force_enum = TimeInForce(time_in_force)
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid order parameter: {e}")
            return {
                "error": f"Invalid order parameter: {e}",
                "status": "rejected"
            }
        
        # Create and submit order
        order = self.submit_order(
            symbol=symbol.upper(),
            qty=float(qty),
            side=side_enum,
            type=type_enum,
            time_in_force=time_in_force_enum,
            limit_price=float(limit_price) if limit_price is not None else None,
            stop_price=float(stop_price) if stop_price is not None else None
        )
        
        if order:
            return order.to_dict()
        else:
            return {
                "error": "Failed to create order",
                "status": "rejected"
            }
    
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
        """Submit an order to the mock broker"""
        # Validate the symbol exists
        symbol = symbol.upper()
        if symbol not in self._market_data and symbol not in MOCK_SYMBOLS:
            logger.error(f"Symbol not found: {symbol}")
            return None
        
        # Ensure we have market data for this symbol
        if symbol not in self._market_data:
            last_price = MOCK_SYMBOLS.get(symbol, {"price": 100.0})["price"]
            self._market_data[symbol] = {
                "symbol": symbol,
                "last_price": last_price,
                "bid": last_price - random.uniform(0.01, 0.5),
                "ask": last_price + random.uniform(0.01, 0.5),
                "volume": random.randint(10000, 1000000),
                "timestamp": datetime.now().isoformat(),
                "change": 0,
                "change_percent": 0
            }
        
        # Create new order
        order_id = str(uuid.uuid4())
        order = Order(
            id=order_id,
            symbol=symbol,
            qty=qty,
            side=side,
            type=type,
            status=OrderStatus.NEW,
            time_in_force=time_in_force,
            limit_price=limit_price,
            stop_price=stop_price,
            trail_percent=trail_percent,
            created_at=datetime.now()
        )
        
        # Add to orders dictionary
        self._orders[order_id] = order
        
        # Execute order (simulate fill process)
        self._execute_order(order)
        
        # Save data
        self._save_data()
        
        return order
    
    def _execute_order(self, order: Order):
        """Execute an order (simulate fill process)"""
        # For simplicity in mock broker, execute all orders immediately
        # In a real broker, this would happen asynchronously
        
        # Update market data
        self._update_market_data()
        
        # Get current market price
        market_data = self._market_data.get(order.symbol)
        if not market_data:
            order.status = OrderStatus.REJECTED
            logger.error(f"No market data for {order.symbol}")
            return
        
        current_price = market_data["last_price"]
        
        # Check if order should be filled based on type and price
        should_fill = False
        fill_price = current_price
        
        if order.type == OrderType.MARKET:
            # Market orders always fill
            should_fill = True
            
            # Use bid for sell orders and ask for buy orders
            if order.side == OrderSide.SELL:
                fill_price = market_data["bid"]
            else:
                fill_price = market_data["ask"]
                
        elif order.type == OrderType.LIMIT:
            # Limit orders fill if price is favorable
            if order.limit_price is None:
                order.status = OrderStatus.REJECTED
                logger.error("Limit order without limit price")
                return
                
            if order.side == OrderSide.BUY and current_price <= order.limit_price:
                should_fill = True
                fill_price = min(current_price, order.limit_price)
            elif order.side == OrderSide.SELL and current_price >= order.limit_price:
                should_fill = True
                fill_price = max(current_price, order.limit_price)
                
        elif order.type == OrderType.STOP:
            # Stop orders fill if price crosses the stop
            if order.stop_price is None:
                order.status = OrderStatus.REJECTED
                logger.error("Stop order without stop price")
                return
                
            if order.side == OrderSide.BUY and current_price >= order.stop_price:
                should_fill = True
                fill_price = current_price
            elif order.side == OrderSide.SELL and current_price <= order.stop_price:
                should_fill = True
                fill_price = current_price
                
        elif order.type == OrderType.STOP_LIMIT:
            # Stop-limit orders become limit orders when stop is triggered
            if order.stop_price is None or order.limit_price is None:
                order.status = OrderStatus.REJECTED
                logger.error("Stop-limit order without stop or limit price")
                return
                
            # Check if stop is triggered
            stop_triggered = False
            if order.side == OrderSide.BUY and current_price >= order.stop_price:
                stop_triggered = True
            elif order.side == OrderSide.SELL and current_price <= order.stop_price:
                stop_triggered = True
                
            if stop_triggered:
                # Now check if limit condition is met
                if order.side == OrderSide.BUY and current_price <= order.limit_price:
                    should_fill = True
                    fill_price = min(current_price, order.limit_price)
                elif order.side == OrderSide.SELL and current_price >= order.limit_price:
                    should_fill = True
                    fill_price = max(current_price, order.limit_price)
        
        # Fill the order if conditions are met
        if should_fill:
            order.status = OrderStatus.FILLED
            order.filled_qty = order.qty
            order.filled_avg_price = fill_price
            order.filled_at = datetime.now()
            
            # Update account and positions
            self._update_account_and_positions(order, fill_price)
            
            logger.info(f"Order {order.id} filled: {order.qty} {order.symbol} @ {fill_price}")
            
            # Introduce random delay for filled orders (simulate latency)
            latency = self.config.get("latency_ms", 0)
            if latency > 0:
                delay = latency / 1000
                logger.debug(f"Simulating latency: {latency}ms")
                # In a real implementation, we'd use time.sleep(delay) here
    
    def _update_account_and_positions(self, order: Order, fill_price: float):
        """Update account and positions based on filled order"""
        symbol = order.symbol
        qty = order.qty
        side = order.side
        
        # Calculate order value
        order_value = qty * fill_price
        
        # Update account cash
        if side == OrderSide.BUY:
            self._account.cash -= order_value
        else:
            self._account.cash += order_value
        
        # Update or create position
        if symbol in self._positions:
            position = self._positions[symbol]
            
            if side == OrderSide.BUY:
                # Adding to position
                new_qty = position.qty + qty
                new_cost = (position.avg_entry_price * position.qty) + (fill_price * qty)
                position.qty = new_qty
                position.avg_entry_price = new_cost / new_qty
            else:
                # Reducing position
                position.qty -= qty
                # If position is closed, remove it
                if position.qty <= 0:
                    del self._positions[symbol]
        else:
            # New position (only for buys)
            if side == OrderSide.BUY:
                self._positions[symbol] = Position(
                    symbol=symbol,
                    qty=qty,
                    avg_entry_price=fill_price,
                    current_price=fill_price,
                    side=OrderSide.BUY
                )
        
        # Update account values
        positions_value = sum(p.market_value for p in self._positions.values())
        self._account.portfolio_value = self._account.cash + positions_value
        self._account.equity = self._account.portfolio_value
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        if order_id not in self._orders:
            logger.warning(f"Order {order_id} not found for cancellation")
            return False
        
        order = self._orders[order_id]
        
        # Can only cancel active orders
        if not order.is_active:
            logger.warning(f"Cannot cancel order {order_id} with status {order.status}")
            return False
        
        # Cancel the order
        order.status = OrderStatus.CANCELLED
        
        # Save data
        self._save_data()
        
        logger.info(f"Order {order_id} cancelled")
        return True
    
    def cancel_all_orders(self) -> bool:
        """Cancel all active orders"""
        cancelled_count = 0
        
        for order_id, order in list(self._orders.items()):
            if order.is_active:
                order.status = OrderStatus.CANCELLED
                cancelled_count += 1
        
        # Save data
        self._save_data()
        
        logger.info(f"Cancelled {cancelled_count} orders")
        return True
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data for a symbol"""
        # Update market data
        self._update_market_data()
        
        symbol = symbol.upper()
        
        # Check if we have data for this symbol
        if symbol not in self._market_data:
            # Add symbol if it's in our mock symbols
            if symbol in MOCK_SYMBOLS:
                price = MOCK_SYMBOLS[symbol]["price"]
                self._market_data[symbol] = {
                    "symbol": symbol,
                    "last_price": price,
                    "bid": price - random.uniform(0.01, 0.5),
                    "ask": price + random.uniform(0.01, 0.5),
                    "volume": random.randint(10000, 1000000),
                    "timestamp": datetime.now().isoformat(),
                    "change": 0,
                    "change_percent": 0
                }
            else:
                logger.warning(f"No market data for symbol: {symbol}")
                return {
                    "symbol": symbol,
                    "error": "Symbol not found"
                }
        
        return self._market_data[symbol] 

