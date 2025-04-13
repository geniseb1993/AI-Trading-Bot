import uuid
import random
import datetime
import logging
from typing import Dict, List, Optional, Any, Union
from .broker_interface import (
    BrokerInterface,
    Account,
    Position,
    Order,
    OrderSide,
    OrderType,
    OrderStatus,
    TimeInForce,
)

logger = logging.getLogger(__name__)

class MockBroker(BrokerInterface):
    """Mock implementation of a broker for testing and development"""
    
    def __init__(self, initial_balance: float = 100000.0):
        self.connected = False
        self.account_id = f"mock-account-{uuid.uuid4()}"
        self.initial_balance = initial_balance
        self.cash = initial_balance
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.market_data: Dict[str, Dict[str, Any]] = {}
        
        # Initialize with some random market data
        self._initialize_market_data()
        
        logger.info(f"MockBroker initialized with ${initial_balance} balance")
    
    def _initialize_market_data(self):
        """Initialize mock market data for common symbols"""
        symbols = ["AAPL", "MSFT", "AMZN", "TSLA", "GOOGL", "META", "SPY", "QQQ"]
        
        for symbol in symbols:
            base_price = random.uniform(100, 500)
            self.market_data[symbol] = {
                "symbol": symbol,
                "bid": round(base_price * 0.999, 2),
                "ask": round(base_price * 1.001, 2),
                "last": round(base_price, 2),
                "high": round(base_price * 1.02, 2),
                "low": round(base_price * 0.98, 2),
                "volume": random.randint(100000, 1000000),
                "timestamp": datetime.datetime.now().isoformat(),
            }
    
    def _update_market_data(self):
        """Simulate market data changes"""
        for symbol, data in self.market_data.items():
            # Simulate price movement
            price_change_pct = random.uniform(-0.002, 0.002)  # 0.2% max movement
            base_price = data["last"]
            new_price = round(base_price * (1 + price_change_pct), 2)
            
            self.market_data[symbol] = {
                "symbol": symbol,
                "bid": round(new_price * 0.999, 2),
                "ask": round(new_price * 1.001, 2),
                "last": new_price,
                "high": max(data["high"], new_price),
                "low": min(data["low"], new_price),
                "volume": data["volume"] + random.randint(100, 1000),
                "timestamp": datetime.datetime.now().isoformat(),
            }
            
            # Update positions with new prices
            if symbol in self.positions:
                pos = self.positions[symbol]
                pos.current_price = new_price
                pos.market_value = pos.qty * new_price
                pos.unrealized_pl = pos.market_value - pos.cost_basis if pos.side == OrderSide.BUY else pos.cost_basis - pos.market_value
                pos.unrealized_pl_pct = (pos.unrealized_pl / pos.cost_basis) * 100 if pos.cost_basis != 0 else 0
    
    def connect(self) -> bool:
        """Simulate connecting to broker API"""
        self.connected = True
        logger.info("Connected to mock broker")
        return True
    
    def get_account(self) -> Account:
        """Get mock account information"""
        if not self.connected:
            self.connect()
        
        self._update_market_data()
        
        # Calculate portfolio value as cash + positions value
        portfolio_value = self.cash
        for symbol, position in self.positions.items():
            portfolio_value += position.market_value
        
        return Account(
            id=self.account_id,
            cash=self.cash,
            portfolio_value=portfolio_value,
            buying_power=self.cash * 2,  # Simulate 2x margin
            equity=portfolio_value,
            currency="USD"
        )
    
    def get_positions(self) -> List[Position]:
        """Get all current positions"""
        if not self.connected:
            self.connect()
        
        self._update_market_data()
        return list(self.positions.values())
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a specific symbol"""
        if not self.connected:
            self.connect()
        
        self._update_market_data()
        return self.positions.get(symbol)
    
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get list of orders with optional status filter"""
        if not self.connected:
            self.connect()
        
        if status is None:
            return list(self.orders.values())
        return [order for order in self.orders.values() if order.status == status]
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get a specific order by ID"""
        if not self.connected:
            self.connect()
        
        return self.orders.get(order_id)
    
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
        """Submit a mock order"""
        if not self.connected:
            self.connect()
        
        self._update_market_data()
        
        # Validate the order
        if symbol not in self.market_data:
            logger.error(f"Symbol {symbol} not found in market data")
            return None
        
        if qty <= 0:
            logger.error(f"Invalid quantity: {qty}")
            return None
        
        if type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and limit_price is None:
            logger.error(f"Limit price required for {type} orders")
            return None
        
        if type in [OrderType.STOP, OrderType.STOP_LIMIT] and stop_price is None:
            logger.error(f"Stop price required for {type} orders")
            return None
        
        if type == OrderType.TRAILING_STOP and trail_percent is None:
            logger.error("Trail percent required for trailing stop orders")
            return None
        
        # Create the order
        order_id = f"mock-order-{uuid.uuid4()}"
        now = datetime.datetime.now()
        
        order = Order(
            id=order_id,
            symbol=symbol,
            qty=qty,
            side=side,
            type=type,
            limit_price=limit_price,
            stop_price=stop_price,
            time_in_force=time_in_force,
            status=OrderStatus.NEW,
            created_at=now,
            trail_percent=trail_percent,
        )
        
        self.orders[order_id] = order
        logger.info(f"Submitted order: {order_id} for {qty} {symbol} {side} {type}")
        
        # Simulate execution - immediately for market orders
        if type == OrderType.MARKET:
            self._execute_order(order)
        
        return order
    
    def _execute_order(self, order: Order):
        """Simulate order execution"""
        symbol = order.symbol
        current_data = self.market_data[symbol]
        
        # Determine execution price
        if order.side == OrderSide.BUY:
            exec_price = current_data["ask"]
        else:
            exec_price = current_data["bid"]
        
        # Apply small random slippage to simulate real market
        slippage = random.uniform(-0.001, 0.001)  # 0.1% max slippage
        exec_price = round(exec_price * (1 + slippage), 2)
        
        # Update order
        order.status = OrderStatus.FILLED
        order.filled_qty = order.qty
        order.filled_avg_price = exec_price
        order.filled_at = datetime.datetime.now()
        
        # Update account
        cost = order.qty * exec_price
        
        if order.side == OrderSide.BUY:
            # Deduct cash
            self.cash -= cost
            
            # Update or create position
            if symbol in self.positions:
                pos = self.positions[symbol]
                # Update average entry
                new_qty = pos.qty + order.qty
                new_cost_basis = pos.cost_basis + cost
                pos.avg_entry_price = new_cost_basis / new_qty
                pos.qty = new_qty
                pos.cost_basis = new_cost_basis
                pos.market_value = new_qty * pos.current_price
                pos.unrealized_pl = pos.market_value - pos.cost_basis
                pos.unrealized_pl_pct = (pos.unrealized_pl / pos.cost_basis) * 100 if pos.cost_basis != 0 else 0
            else:
                # Create new position
                self.positions[symbol] = Position(
                    symbol=symbol,
                    qty=order.qty,
                    avg_entry_price=exec_price,
                    current_price=exec_price,
                    side=OrderSide.BUY
                )
        else:  # SELL
            # Add to cash
            self.cash += cost
            
            # Update position
            if symbol in self.positions:
                pos = self.positions[symbol]
                pos.qty -= order.qty
                
                # Remove position if qty becomes 0
                if pos.qty <= 0:
                    del self.positions[symbol]
                else:
                    # No need to update avg_entry_price on sell
                    pos.market_value = pos.qty * pos.current_price
                    pos.unrealized_pl = pos.market_value - pos.cost_basis
                    pos.unrealized_pl_pct = (pos.unrealized_pl / pos.cost_basis) * 100 if pos.cost_basis != 0 else 0
            
        logger.info(f"Executed order: {order.id} at ${exec_price} for {order.qty} {symbol}")
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        if not self.connected:
            self.connect()
        
        if order_id not in self.orders:
            logger.error(f"Order {order_id} not found")
            return False
        
        order = self.orders[order_id]
        
        if order.status not in [OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED]:
            logger.error(f"Cannot cancel order with status: {order.status}")
            return False
        
        order.status = OrderStatus.CANCELED
        logger.info(f"Canceled order: {order_id}")
        
        return True
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        if not self.connected:
            self.connect()
        
        cancellable_orders = [
            order for order in self.orders.values() 
            if order.status in [OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED]
        ]
        
        for order in cancellable_orders:
            order.status = OrderStatus.CANCELED
        
        logger.info(f"Canceled {len(cancellable_orders)} orders")
        
        return True
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a symbol"""
        if not self.connected:
            self.connect()
        
        self._update_market_data()
        
        if symbol not in self.market_data:
            logger.error(f"Symbol {symbol} not found in market data")
            return {}
        
        return self.market_data[symbol] 