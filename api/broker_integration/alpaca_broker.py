import os
import logging
import datetime
from typing import Dict, List, Optional, Any, Union
import json

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
from .mock_broker import MockBroker

logger = logging.getLogger(__name__)

class AlpacaBroker(BrokerInterface):
    """Alpaca API implementation with fallback to mock broker"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, is_paper: bool = True):
        self.api_key = api_key or os.environ.get("ALPACA_API_KEY")
        self.api_secret = api_secret or os.environ.get("ALPACA_API_SECRET")
        self.is_paper = is_paper
        self.connected = False
        self.alpaca_client = None
        
        # Initialize fallback broker
        self.mock_broker = MockBroker()
        self.using_mock = False
        
        # Try to import alpaca-trade-api
        try:
            import alpaca_trade_api as tradeapi
            self.tradeapi = tradeapi
            logger.info("Successfully imported alpaca-trade-api")
        except ImportError:
            logger.warning("alpaca-trade-api not installed, using mock broker")
            self.tradeapi = None
            self.using_mock = True
    
    def connect(self) -> bool:
        """Connect to Alpaca API or fallback to mock broker"""
        if self.using_mock or not self.api_key or not self.api_secret:
            logger.warning("Using mock broker for Alpaca integration")
            self.using_mock = True
            self.mock_broker.connect()
            self.connected = True
            return True
        
        try:
            base_url = "https://paper-api.alpaca.markets" if self.is_paper else "https://api.alpaca.markets"
            self.alpaca_client = self.tradeapi.REST(
                self.api_key,
                self.api_secret,
                base_url=base_url,
                api_version="v2"
            )
            # Test connection
            account_info = self.alpaca_client.get_account()
            logger.info(f"Connected to Alpaca API: {account_info.id}")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca API: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            self.mock_broker.connect()
            self.connected = True
            return True
    
    def _ensure_connected(self):
        """Ensure we're connected to the broker"""
        if not self.connected:
            self.connect()
    
    def get_account(self) -> Account:
        """Get account information from Alpaca or mock"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_account()
        
        try:
            account = self.alpaca_client.get_account()
            return Account(
                id=account.id,
                cash=float(account.cash),
                portfolio_value=float(account.portfolio_value),
                buying_power=float(account.buying_power),
                equity=float(account.equity),
                currency=account.currency
            )
        except Exception as e:
            logger.error(f"Error getting account from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_account()
    
    def get_positions(self) -> List[Position]:
        """Get all current positions"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_positions()
        
        try:
            alpaca_positions = self.alpaca_client.list_positions()
            positions = []
            
            for pos in alpaca_positions:
                side = OrderSide.BUY if float(pos.qty) > 0 else OrderSide.SELL
                positions.append(Position(
                    symbol=pos.symbol,
                    qty=abs(float(pos.qty)),
                    avg_entry_price=float(pos.avg_entry_price),
                    current_price=float(pos.current_price),
                    side=side
                ))
            
            return positions
        except Exception as e:
            logger.error(f"Error getting positions from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_positions()
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a specific symbol"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_position(symbol)
        
        try:
            pos = self.alpaca_client.get_position(symbol)
            side = OrderSide.BUY if float(pos.qty) > 0 else OrderSide.SELL
            return Position(
                symbol=pos.symbol,
                qty=abs(float(pos.qty)),
                avg_entry_price=float(pos.avg_entry_price),
                current_price=float(pos.current_price),
                side=side
            )
        except Exception as e:
            # If position not found, return None
            if "position not found" in str(e).lower():
                return None
            
            logger.error(f"Error getting position for {symbol} from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_position(symbol)
    
    def _convert_alpaca_order_to_interface(self, alpaca_order) -> Order:
        """Convert Alpaca order to our interface Order object"""
        # Map Alpaca order side to our OrderSide
        side = OrderSide.BUY if alpaca_order.side.lower() == "buy" else OrderSide.SELL
        
        # Map Alpaca order type to our OrderType
        order_type_map = {
            "market": OrderType.MARKET,
            "limit": OrderType.LIMIT,
            "stop": OrderType.STOP,
            "stop_limit": OrderType.STOP_LIMIT,
            "trailing_stop": OrderType.TRAILING_STOP
        }
        order_type = order_type_map.get(alpaca_order.type.lower(), OrderType.MARKET)
        
        # Map Alpaca order status to our OrderStatus
        status_map = {
            "new": OrderStatus.NEW,
            "partially_filled": OrderStatus.PARTIALLY_FILLED,
            "filled": OrderStatus.FILLED,
            "done_for_day": OrderStatus.FILLED,
            "canceled": OrderStatus.CANCELED,
            "expired": OrderStatus.CANCELED,
            "replaced": OrderStatus.NEW,
            "pending_cancel": OrderStatus.PENDING,
            "pending_replace": OrderStatus.PENDING,
            "accepted": OrderStatus.NEW,
            "pending_new": OrderStatus.PENDING,
            "accepted_for_bidding": OrderStatus.NEW,
            "stopped": OrderStatus.FILLED,
            "rejected": OrderStatus.REJECTED,
            "suspended": OrderStatus.PENDING,
            "calculated": OrderStatus.NEW
        }
        status = status_map.get(alpaca_order.status.lower(), OrderStatus.NEW)
        
        # Map Alpaca time in force to our TimeInForce
        tif_map = {
            "day": TimeInForce.DAY,
            "gtc": TimeInForce.GTC,
            "opg": TimeInForce.DAY,
            "cls": TimeInForce.DAY,
            "ioc": TimeInForce.IOC,
            "fok": TimeInForce.FOK
        }
        time_in_force = tif_map.get(alpaca_order.time_in_force.lower(), TimeInForce.DAY)
        
        # Parse dates
        created_at = datetime.datetime.fromisoformat(alpaca_order.created_at.replace('Z', '+00:00'))
        filled_at = None
        if alpaca_order.filled_at and alpaca_order.filled_at != "None":
            filled_at = datetime.datetime.fromisoformat(alpaca_order.filled_at.replace('Z', '+00:00'))
        
        # Create our Order object
        return Order(
            id=alpaca_order.id,
            symbol=alpaca_order.symbol,
            qty=float(alpaca_order.qty),
            side=side,
            type=order_type,
            limit_price=float(alpaca_order.limit_price) if alpaca_order.limit_price else None,
            stop_price=float(alpaca_order.stop_price) if alpaca_order.stop_price else None,
            time_in_force=time_in_force,
            status=status,
            created_at=created_at,
            filled_at=filled_at,
            filled_qty=float(alpaca_order.filled_qty) if alpaca_order.filled_qty else 0,
            filled_avg_price=float(alpaca_order.filled_avg_price) if alpaca_order.filled_avg_price else None,
            trail_percent=float(alpaca_order.trail_percent) if hasattr(alpaca_order, 'trail_percent') and alpaca_order.trail_percent else None,
            trail_price=float(alpaca_order.trail_price) if hasattr(alpaca_order, 'trail_price') and alpaca_order.trail_price else None
        )
    
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get list of orders with optional status filter"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_orders(status)
        
        try:
            # Convert our status to Alpaca status
            alpaca_status = None
            if status:
                status_map = {
                    OrderStatus.NEW: "open",
                    OrderStatus.PARTIALLY_FILLED: "open",
                    OrderStatus.FILLED: "closed",
                    OrderStatus.CANCELED: "closed",
                    OrderStatus.REJECTED: "closed",
                    OrderStatus.PENDING: "open"
                }
                alpaca_status = status_map.get(status)
            
            # Get orders from Alpaca
            if alpaca_status:
                alpaca_orders = self.alpaca_client.list_orders(status=alpaca_status)
            else:
                # Get both open and closed orders
                alpaca_orders = []
                alpaca_orders.extend(self.alpaca_client.list_orders(status="open"))
                alpaca_orders.extend(self.alpaca_client.list_orders(status="closed", limit=100))
            
            # Convert to our Order objects
            orders = [self._convert_alpaca_order_to_interface(order) for order in alpaca_orders]
            
            # Filter by our status if needed
            if status:
                orders = [order for order in orders if order.status == status]
            
            return orders
        except Exception as e:
            logger.error(f"Error getting orders from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_orders(status)
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get a specific order by ID"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_order(order_id)
        
        try:
            alpaca_order = self.alpaca_client.get_order(order_id)
            return self._convert_alpaca_order_to_interface(alpaca_order)
        except Exception as e:
            logger.error(f"Error getting order {order_id} from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_order(order_id)
    
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
        """Submit an order to Alpaca"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price,
                trail_percent=trail_percent
            )
        
        try:
            # Convert our enums to Alpaca format
            alpaca_side = "buy" if side == OrderSide.BUY else "sell"
            
            alpaca_type_map = {
                OrderType.MARKET: "market",
                OrderType.LIMIT: "limit",
                OrderType.STOP: "stop",
                OrderType.STOP_LIMIT: "stop_limit",
                OrderType.TRAILING_STOP: "trailing_stop"
            }
            alpaca_type = alpaca_type_map.get(type, "market")
            
            alpaca_tif_map = {
                TimeInForce.DAY: "day",
                TimeInForce.GTC: "gtc",
                TimeInForce.IOC: "ioc",
                TimeInForce.FOK: "fok"
            }
            alpaca_tif = alpaca_tif_map.get(time_in_force, "day")
            
            # Submit order to Alpaca
            alpaca_order = self.alpaca_client.submit_order(
                symbol=symbol,
                qty=qty,
                side=alpaca_side,
                type=alpaca_type,
                time_in_force=alpaca_tif,
                limit_price=limit_price,
                stop_price=stop_price,
                trail_percent=trail_percent
            )
            
            return self._convert_alpaca_order_to_interface(alpaca_order)
        except Exception as e:
            logger.error(f"Error submitting order to Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price,
                trail_percent=trail_percent
            )
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.cancel_order(order_id)
        
        try:
            self.alpaca_client.cancel_order(order_id)
            return True
        except Exception as e:
            logger.error(f"Error canceling order {order_id} on Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.cancel_order(order_id)
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.cancel_all_orders()
        
        try:
            self.alpaca_client.cancel_all_orders()
            return True
        except Exception as e:
            logger.error(f"Error canceling all orders on Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.cancel_all_orders()
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a symbol"""
        self._ensure_connected()
        
        if self.using_mock:
            return self.mock_broker.get_market_data(symbol)
        
        try:
            # Get latest bar
            bars = self.alpaca_client.get_barset(symbol, "minute", limit=1)
            bar = bars[symbol][0]
            
            # Get latest quote
            quote = self.alpaca_client.get_last_quote(symbol)
            
            return {
                "symbol": symbol,
                "bid": float(quote.bidprice),
                "ask": float(quote.askprice),
                "last": float(bar.c),
                "high": float(bar.h),
                "low": float(bar.l),
                "volume": int(bar.v),
                "timestamp": bar.t.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting market data for {symbol} from Alpaca: {e}")
            logger.warning("Falling back to mock broker")
            self.using_mock = True
            return self.mock_broker.get_market_data(symbol) 