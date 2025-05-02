import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from enum import Enum, auto
import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class OrderSide(Enum):
    """Order side enum"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type enum"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class OrderStatus(Enum):
    """Order status enum"""
    NEW = "new"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    DONE_FOR_DAY = "done_for_day"
    REPLACED = "replaced"
    PENDING_CANCEL = "pending_cancel"
    PENDING_REPLACE = "pending_replace"
    HELD = "held"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"


class TimeInForce(Enum):
    """Time in force enum"""
    DAY = "day"
    GTC = "gtc"  # Good till cancelled
    OPG = "opg"  # Market on open
    CLS = "cls"  # Market on close
    IOC = "ioc"  # Immediate or cancel
    FOK = "fok"  # Fill or kill


@dataclass
class Account:
    """
    Account information
    """
    id: str
    cash: float
    portfolio_value: float
    buying_power: float
    equity: float
    currency: str = "USD"
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "cash": self.cash,
            "portfolio_value": self.portfolio_value,
            "buying_power": self.buying_power,
            "equity": self.equity,
            "currency": self.currency,
            **self.extra_data
        }


@dataclass
class Position:
    """
    Position information
    """
    symbol: str
    qty: float
    avg_entry_price: float
    current_price: float
    side: OrderSide = OrderSide.BUY
    extra_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def market_value(self) -> float:
        """
        Calculate market value of the position
        """
        return self.qty * self.current_price

    @property
    def unrealized_pl(self) -> float:
        """
        Calculate unrealized profit/loss
        """
        if self.side == OrderSide.BUY:
            return (self.current_price - self.avg_entry_price) * self.qty
        else:
            return (self.avg_entry_price - self.current_price) * self.qty

    @property
    def unrealized_pl_percent(self) -> float:
        """
        Calculate unrealized profit/loss percentage
        """
        if self.avg_entry_price == 0:
            return 0
        return (self.unrealized_pl / (self.avg_entry_price * self.qty)) * 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "qty": self.qty,
            "avg_entry_price": self.avg_entry_price,
            "current_price": self.current_price,
            "side": self.side.value,
            "market_value": self.market_value,
            "unrealized_pl": self.unrealized_pl,
            "unrealized_pl_percent": self.unrealized_pl_percent,
            **self.extra_data
        }


@dataclass
class Order:
    """
    Order information
    """
    id: str
    symbol: str
    qty: float
    side: OrderSide
    type: OrderType
    status: OrderStatus = OrderStatus.NEW
    time_in_force: TimeInForce = TimeInForce.DAY
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    trail_percent: Optional[float] = None
    filled_qty: float = 0
    filled_avg_price: Optional[float] = None
    created_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_filled(self) -> bool:
        """
        Check if order is filled
        """
        return self.status == OrderStatus.FILLED

    @property
    def is_active(self) -> bool:
        """
        Check if order is still active
        """
        active_statuses = [
            OrderStatus.NEW,
            OrderStatus.PARTIALLY_FILLED,
            OrderStatus.HELD,
            OrderStatus.PENDING_CANCEL,
            OrderStatus.PENDING_REPLACE
        ]
        return self.status in active_statuses

    @property
    def notional_value(self) -> float:
        """
        Calculate notional value of the order
        """
        if self.filled_avg_price and self.filled_qty > 0:
            return self.filled_avg_price * self.filled_qty
        elif self.limit_price:
            return self.limit_price * self.qty
        else:
            # For market orders without filled price, we can't calculate exact value
            return 0

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "symbol": self.symbol,
            "qty": self.qty,
            "side": self.side.value,
            "type": self.type.value,
            "time_in_force": self.time_in_force.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "filled_qty": self.filled_qty
        }
        
        if self.limit_price is not None:
            result["limit_price"] = self.limit_price
        
        if self.stop_price is not None:
            result["stop_price"] = self.stop_price
        
        if self.filled_at is not None:
            result["filled_at"] = self.filled_at.isoformat()
        
        if self.filled_avg_price is not None:
            result["filled_avg_price"] = self.filled_avg_price
        
        if self.trail_percent is not None:
            result["trail_percent"] = self.trail_percent
        
        result.update(self.extra_data)
        
        return result


class BrokerInterface(ABC):
    """
    Abstract base class defining the interface for all broker implementations.
    Any broker integration must implement these methods.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the broker's API or service.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the broker's API or service.
        
        Returns:
            bool: True if disconnection is successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if currently connected to the broker.
        
        Returns:
            bool: True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information from the broker.
        
        Returns:
            dict: Account information (balance, equity, etc.)
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all current positions.
        
        Returns:
            list: List of position dictionaries
        """
        pass
    
    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific position by symbol.
        
        Args:
            symbol: The ticker symbol to query
            
        Returns:
            dict: Position information or None if position doesn't exist
        """
        pass
    
    @abstractmethod
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all orders, optionally filtered by status.
        
        Args:
            status: Optional filter for order status (open, filled, canceled, etc.)
            
        Returns:
            list: List of order dictionaries
        """
        pass
    
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific order by ID.
        
        Args:
            order_id: The ID of the order to retrieve
            
        Returns:
            dict: Order information or None if order doesn't exist
        """
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, qty: float, side: str, type: str = "market", 
                   limit_price: Optional[float] = None, stop_price: Optional[float] = None,
                   time_in_force: str = "day") -> Dict[str, Any]:
        """
        Place an order with the broker.
        
        Args:
            symbol: The ticker symbol
            qty: Quantity of shares/contracts
            side: 'buy' or 'sell'
            type: Order type (market, limit, stop, etc.)
            limit_price: Price for limit orders
            stop_price: Price for stop orders
            time_in_force: Time in force (day, gtc, etc.)
            
        Returns:
            dict: Information about the placed order
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a specific order.
        
        Args:
            order_id: The ID of the order to cancel
            
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cancel_all_orders(self) -> bool:
        """
        Cancel all open orders.
        
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market data for a symbol.
        
        Args:
            symbol: The ticker symbol
            
        Returns:
            dict: Market data including price, volume, etc.
        """
        pass 