from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import datetime


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class TimeInForce(str, Enum):
    DAY = "day"
    GTC = "gtc"  # Good Till Canceled
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill


class OrderStatus(str, Enum):
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    PENDING = "pending"


class Position:
    def __init__(
        self,
        symbol: str,
        qty: float,
        avg_entry_price: float,
        current_price: float,
        side: OrderSide,
    ):
        self.symbol = symbol
        self.qty = qty
        self.avg_entry_price = avg_entry_price
        self.current_price = current_price
        self.side = side
        self.market_value = qty * current_price
        self.cost_basis = qty * avg_entry_price
        self.unrealized_pl = self.market_value - self.cost_basis if side == OrderSide.BUY else self.cost_basis - self.market_value
        self.unrealized_pl_pct = (self.unrealized_pl / self.cost_basis) * 100 if self.cost_basis != 0 else 0


class Order:
    def __init__(
        self,
        id: str,
        symbol: str,
        qty: float,
        side: OrderSide,
        type: OrderType,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.DAY,
        status: OrderStatus = OrderStatus.NEW,
        created_at: Optional[datetime.datetime] = None,
        filled_at: Optional[datetime.datetime] = None,
        filled_qty: float = 0,
        filled_avg_price: Optional[float] = None,
        trail_percent: Optional[float] = None,
        trail_price: Optional[float] = None,
    ):
        self.id = id
        self.symbol = symbol
        self.qty = qty
        self.side = side
        self.type = type
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.time_in_force = time_in_force
        self.status = status
        self.created_at = created_at or datetime.datetime.now()
        self.filled_at = filled_at
        self.filled_qty = filled_qty
        self.filled_avg_price = filled_avg_price
        self.trail_percent = trail_percent
        self.trail_price = trail_price

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "qty": self.qty,
            "side": self.side,
            "type": self.type,
            "limit_price": self.limit_price,
            "stop_price": self.stop_price,
            "time_in_force": self.time_in_force,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
            "filled_qty": self.filled_qty,
            "filled_avg_price": self.filled_avg_price,
            "trail_percent": self.trail_percent,
            "trail_price": self.trail_price
        }


class Account:
    def __init__(
        self,
        id: str,
        cash: float,
        portfolio_value: float,
        buying_power: float,
        equity: float,
        currency: str = "USD",
    ):
        self.id = id
        self.cash = cash
        self.portfolio_value = portfolio_value
        self.buying_power = buying_power
        self.equity = equity
        self.currency = currency
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "cash": self.cash,
            "portfolio_value": self.portfolio_value,
            "buying_power": self.buying_power,
            "equity": self.equity,
            "currency": self.currency
        }


class BrokerInterface(ABC):
    """Abstract base class defining the interface for broker integrations"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection with the broker API"""
        pass
    
    @abstractmethod
    def get_account(self) -> Account:
        """Get account information"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Get current positions"""
        pass
    
    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a specific symbol"""
        pass
    
    @abstractmethod
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get list of orders with optional status filter"""
        pass
    
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get a specific order by ID"""
        pass
    
    @abstractmethod
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
        """Submit a new order"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        pass
    
    @abstractmethod
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        pass
    
    @abstractmethod
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a symbol"""
        pass 