"""
Alpaca broker implementation.
Integrates with the Alpaca trading API for real or paper trading.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple

from .base import BrokerBase

# Configure logging
logger = logging.getLogger(__name__)

try:
    import alpaca_trade_api as tradeapi
    from alpaca_trade_api.rest import REST, APIError
    HAS_ALPACA = True
except ImportError:
    logger.warning("alpaca-trade-api package not found. Install with 'pip install alpaca-trade-api'")
    HAS_ALPACA = False

class AlpacaBroker(BrokerBase):
    """
    Alpaca broker implementation.
    Uses the alpaca-trade-api package to interact with Alpaca's trading API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Alpaca broker with configuration.
        
        Args:
            config: Dictionary with Alpaca API configuration
        """
        super().__init__(config)
        self.name = "alpaca"
        self.connected = False
        
        if not HAS_ALPACA:
            logger.error("Cannot initialize AlpacaBroker: alpaca-trade-api package not installed")
            return
        
        self.api_key = config.get("api_key", "")
        self.api_secret = config.get("api_secret", "")
        self.base_url = config.get("base_url", "https://paper-api.alpaca.markets")
        self.data_feed = config.get("data_feed", "iex")
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)  # seconds
        
        # Will be initialized in connect()
        self.api = None
    
    def connect(self) -> bool:
        """
        Connect to the Alpaca API.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not HAS_ALPACA:
            logger.error("Cannot connect to Alpaca: alpaca-trade-api package not installed")
            return False
        
        if not self.api_key or not self.api_secret:
            logger.error("Cannot connect to Alpaca: API credentials not provided")
            return False
        
        try:
            self.api = REST(
                key_id=self.api_key,
                secret_key=self.api_secret,
                base_url=self.base_url,
                api_version='v2'
            )
            
            # Test connection
            account = self.api.get_account()
            self.connected = True
            logger.info(f"Connected to Alpaca API ({self.base_url})")
            logger.info(f"Account ID: {account.id}, Status: {account.status}")
            return True
            
        except APIError as e:
            logger.error(f"Alpaca API error: {str(e)}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Error connecting to Alpaca: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from the Alpaca API.
        
        Returns:
            bool: True if disconnection successful
        """
        self.api = None
        self.connected = False
        logger.info("Disconnected from Alpaca API")
        return True
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information from Alpaca.
        
        Returns:
            Dict containing account information
        """
        self._check_connection()
        
        account = self._execute_with_retry(self.api.get_account)
        
        # Convert to a regular dict
        result = {
            "id": account.id,
            "cash": float(account.cash),
            "equity": float(account.equity),
            "buying_power": float(account.buying_power),
            "currency": "USD",
            "status": account.status,
            "created_at": account.created_at.isoformat() if account.created_at else None,
            "leverage": float(account.multiplier),
            "pattern_day_trader": account.pattern_day_trader,
            "trading_blocked": account.trading_blocked,
            "trades_blocked": account.trades_blocked,
            "transfers_blocked": account.transfers_blocked,
            "account_blocked": account.account_blocked,
            "daytrading_buying_power": float(account.daytrading_buying_power),
            "regt_buying_power": float(account.regt_buying_power),
            "non_marginable_buying_power": float(account.non_marginable_buying_power)
        }
        
        return result
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions from Alpaca.
        
        Returns:
            List of dictionaries containing position information
        """
        self._check_connection()
        
        positions = self._execute_with_retry(self.api.list_positions)
        
        result = []
        for position in positions:
            result.append({
                "symbol": position.symbol,
                "quantity": float(position.qty),
                "average_price": float(position.avg_entry_price),
                "cost_basis": float(position.cost_basis),
                "current_price": float(position.current_price),
                "market_value": float(position.market_value),
                "profit_loss": float(position.unrealized_pl),
                "profit_loss_pct": float(position.unrealized_plpc) * 100,
                "side": position.side,
                "exchange": position.exchange,
                "asset_id": position.asset_id,
                "asset_marginable": position.asset_marginable,
                "created_at": datetime.now().isoformat()  # Alpaca doesn't provide creation time
            })
        
        return result
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders from Alpaca with optional filtering by status.
        
        Args:
            status: Filter orders by status ('open', 'closed', 'all')
            
        Returns:
            List of dictionaries containing order information
        """
        self._check_connection()
        
        # Map our status values to Alpaca's
        if status is None or status.lower() == "all":
            status = "all"
        elif status.lower() == "open":
            status = "open"
        elif status.lower() in ["filled", "closed", "canceled"]:
            status = "closed"
        
        orders = self._execute_with_retry(
            self.api.list_orders,
            status=status,
            limit=100,
            nested=True  # Get nested order information
        )
        
        result = []
        for order in orders:
            # Convert to our standard order format
            result.append({
                "id": order.id,
                "client_order_id": order.client_order_id,
                "symbol": order.symbol,
                "quantity": float(order.qty),
                "filled_quantity": float(order.filled_qty),
                "side": order.side,
                "type": order.type,
                "time_in_force": order.time_in_force,
                "limit_price": float(order.limit_price) if order.limit_price else None,
                "stop_price": float(order.stop_price) if order.stop_price else None,
                "status": order.status,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "updated_at": order.updated_at.isoformat() if order.updated_at else None,
                "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                "expired_at": order.expired_at.isoformat() if order.expired_at else None,
                "canceled_at": order.canceled_at.isoformat() if order.canceled_at else None,
                "failed_at": order.failed_at.isoformat() if order.failed_at else None,
                "fill_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                "average_price": float(order.filled_avg_price) if order.filled_avg_price else None
            })
        
        return result
    
    def place_order(self,
                   symbol: str,
                   quantity: float,
                   side: str,
                   order_type: str = "market",
                   limit_price: Optional[float] = None,
                   stop_price: Optional[float] = None,
                   time_in_force: str = "day") -> Dict[str, Any]:
        """
        Place an order with Alpaca.
        
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
            
        Raises:
            ValueError: If order parameters are invalid
            RuntimeError: If order placement fails
        """
        self._check_connection()
        
        # Validate inputs
        symbol = symbol.upper()
        side = side.lower()
        order_type = order_type.lower()
        time_in_force = time_in_force.lower()
        
        if side not in ["buy", "sell"]:
            raise ValueError(f"Invalid order side: {side}. Must be 'buy' or 'sell'")
            
        # Map our order types to Alpaca's
        alpaca_order_type = order_type
        if order_type == "stop":
            alpaca_order_type = "stop"
        elif order_type == "stop_limit":
            alpaca_order_type = "stop_limit"
        elif order_type not in ["market", "limit"]:
            raise ValueError(f"Invalid order type: {order_type}")
        
        # Check required parameters for specific order types
        if order_type in ["limit", "stop_limit"] and limit_price is None:
            raise ValueError(f"Limit price required for {order_type} orders")
            
        if order_type in ["stop", "stop_limit"] and stop_price is None:
            raise ValueError(f"Stop price required for {order_type} orders")
        
        # Place the order
        try:
            order = self._execute_with_retry(
                self.api.submit_order,
                symbol=symbol,
                qty=quantity,
                side=side,
                type=alpaca_order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price
            )
            
            # Convert to our standard order format
            result = {
                "id": order.id,
                "client_order_id": order.client_order_id,
                "symbol": order.symbol,
                "quantity": float(order.qty),
                "filled_quantity": float(order.filled_qty),
                "side": order.side,
                "type": order.type,
                "time_in_force": order.time_in_force,
                "limit_price": float(order.limit_price) if order.limit_price else None,
                "stop_price": float(order.stop_price) if order.stop_price else None,
                "status": order.status,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "updated_at": order.updated_at.isoformat() if order.updated_at else None,
                "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                "expired_at": order.expired_at.isoformat() if order.expired_at else None,
                "canceled_at": order.canceled_at.isoformat() if order.canceled_at else None,
                "failed_at": order.failed_at.isoformat() if order.failed_at else None,
                "fill_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                "average_price": float(order.filled_avg_price) if order.filled_avg_price else None
            }
            
            logger.info(f"Placed {order_type} {side} order for {quantity} {symbol}")
            return result
            
        except APIError as e:
            logger.error(f"Alpaca API error placing order: {str(e)}")
            raise RuntimeError(f"Failed to place order: {str(e)}")
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            raise RuntimeError(f"Failed to place order: {str(e)}")
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order with Alpaca.
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            bool: True if cancellation successful, False otherwise
        """
        self._check_connection()
        
        try:
            self._execute_with_retry(self.api.cancel_order, order_id=order_id)
            logger.info(f"Canceled order {order_id}")
            return True
        except APIError as e:
            if "404" in str(e):
                logger.warning(f"Order {order_id} not found")
                return False
            elif "cannot be canceled" in str(e).lower():
                logger.warning(f"Order {order_id} cannot be canceled: {str(e)}")
                return False
            else:
                logger.error(f"Alpaca API error canceling order: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Error canceling order: {str(e)}")
            return False
    
    def get_asset(self, symbol: str) -> Dict[str, Any]:
        """
        Get information about an asset from Alpaca.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Dict containing asset information
            
        Raises:
            ValueError: If asset not found
        """
        self._check_connection()
        
        symbol = symbol.upper()
        
        try:
            asset = self._execute_with_retry(self.api.get_asset, symbol=symbol)
            
            result = {
                "symbol": asset.symbol,
                "name": asset.name,
                "exchange": asset.exchange,
                "tradable": asset.tradable,
                "marginable": asset.marginable,
                "shortable": asset.shortable,
                "fractionable": asset.fractionable,
                "easy_to_borrow": asset.easy_to_borrow,
                "status": asset.status,
                "asset_class": asset.asset_class,
                "asset_id": asset.id
            }
            
            return result
            
        except APIError as e:
            if "404" in str(e):
                logger.warning(f"Asset {symbol} not found")
                raise ValueError(f"Asset {symbol} not found")
            else:
                logger.error(f"Alpaca API error getting asset: {str(e)}")
                raise RuntimeError(f"Failed to get asset information: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting asset: {str(e)}")
            raise RuntimeError(f"Failed to get asset information: {str(e)}")
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get current quote for an asset from Alpaca.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Dict containing quote information
            
        Raises:
            ValueError: If asset not found
        """
        self._check_connection()
        
        symbol = symbol.upper()
        
        try:
            quote = self._execute_with_retry(self.api.get_latest_quote, symbol=symbol)
            
            result = {
                "symbol": symbol,
                "bid_price": float(quote.bp),
                "bid_size": int(quote.bs),
                "ask_price": float(quote.ap),
                "ask_size": int(quote.as_),
                "last_price": float(quote.p if hasattr(quote, 'p') else quote.ap),
                "last_size": int(quote.s if hasattr(quote, 's') else 0),
                "last_trade_time": quote.t.isoformat() if hasattr(quote, 't') and quote.t else datetime.now().isoformat(),
                "quote_time": datetime.now().isoformat()
            }
            
            return result
            
        except APIError as e:
            if "404" in str(e):
                logger.warning(f"Quote for {symbol} not found")
                raise ValueError(f"Quote for {symbol} not found")
            else:
                logger.error(f"Alpaca API error getting quote: {str(e)}")
                raise RuntimeError(f"Failed to get quote: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting quote: {str(e)}")
            raise RuntimeError(f"Failed to get quote: {str(e)}")
    
    def get_bars(self,
                symbol: str,
                timeframe: str = "1Day",
                start: Optional[datetime] = None,
                end: Optional[datetime] = None,
                limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get historical price bars for an asset from Alpaca.
        
        Args:
            symbol: Asset symbol
            timeframe: Bar timeframe ('1Min', '5Min', '15Min', '1Hour', '1Day', etc.)
            start: Start datetime
            end: End datetime
            limit: Maximum number of bars to return
            
        Returns:
            List of dictionaries containing bar data
            
        Raises:
            ValueError: If timeframe is invalid or asset not found
        """
        self._check_connection()
        
        symbol = symbol.upper()
        
        # Map our timeframes to Alpaca's
        if timeframe == "1Min":
            alpaca_timeframe = "1Min"
        elif timeframe == "5Min":
            alpaca_timeframe = "5Min"
        elif timeframe == "15Min":
            alpaca_timeframe = "15Min"
        elif timeframe == "1Hour":
            alpaca_timeframe = "1Hour"
        elif timeframe == "1Day":
            alpaca_timeframe = "1Day"
        else:
            try:
                # Try to parse the timeframe as Alpaca expects it
                alpaca_timeframe = timeframe
            except:
                raise ValueError(f"Invalid timeframe: {timeframe}")
                
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
                
        try:
            bars = self._execute_with_retry(
                self.api.get_bars,
                symbol=symbol,
                timeframe=alpaca_timeframe,
                start=start,
                end=end,
                limit=limit
            )
            
            result = []
            for bar in bars:
                result.append({
                    "symbol": symbol,
                    "timestamp": bar.t.isoformat(),
                    "open": float(bar.o),
                    "high": float(bar.h),
                    "low": float(bar.l),
                    "close": float(bar.c),
                    "volume": int(bar.v)
                })
            
            return result
            
        except APIError as e:
            logger.error(f"Alpaca API error getting bars: {str(e)}")
            raise RuntimeError(f"Failed to get bars: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting bars: {str(e)}")
            raise RuntimeError(f"Failed to get bars: {str(e)}")
    
    # Helper methods
    def _check_connection(self):
        """Check if broker is connected and raise exception if not."""
        if not self.connected or not self.api:
            raise RuntimeError("Not connected to Alpaca API. Call connect() first.")
    
    def _execute_with_retry(self, func, *args, **kwargs):
        """Execute a function with retry logic on API errors."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except APIError as e:
                # Check if it's a rate limit error
                if "429" in str(e) and attempt < self.max_retries - 1:
                    # Rate limited, sleep and retry
                    sleep_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limited by Alpaca API. Retrying in {sleep_time:.2f}s (attempt {attempt+1}/{self.max_retries})")
                    time.sleep(sleep_time)
                    continue
                # For other API errors, or on the last retry attempt, re-raise
                raise
            except Exception as e:
                # For non-API errors, re-raise immediately
                raise 