"""
Alpaca API Client

Provides a robust interface to the Alpaca API with error handling,
automatic retries, rate limit handling, and caching.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
import pandas as pd
import requests
from alpaca_trade_api.rest import REST, APIError
from alpaca_trade_api.entity import Account, Position, Order

from api.auth.key_manager import get_key_manager

# Configure logging
logger = logging.getLogger(__name__)

class AlpacaClient:
    """
    A robust Alpaca API client that handles errors, retries, and rate limits.
    """
    
    # Default parameters
    DEFAULT_RETRY_COUNT = 3
    DEFAULT_RETRY_DELAY = 1.0  # seconds
    DEFAULT_RATE_LIMIT_DELAY = 60.0  # seconds
    DEFAULT_CACHE_TTL = 5  # seconds
    
    def __init__(
        self,
        paper: bool = True,
        max_retries: int = DEFAULT_RETRY_COUNT,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        rate_limit_delay: float = DEFAULT_RATE_LIMIT_DELAY,
        cache_ttl: int = DEFAULT_CACHE_TTL
    ):
        """
        Initialize the Alpaca API client.
        
        Args:
            paper: If True, use the paper trading API. Default is True.
            max_retries: Maximum number of retry attempts for API calls.
            retry_delay: Initial delay between retries in seconds.
            rate_limit_delay: Delay when rate limit is hit.
            cache_ttl: Time-to-live for cached data in seconds.
        """
        self.paper = paper
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        self.cache_ttl = cache_ttl
        
        # Cache for API responses
        self._cache = {
            'account': {'data': None, 'timestamp': 0},
            'positions': {'data': None, 'timestamp': 0},
            'orders': {'data': None, 'timestamp': 0}
        }
        
        # Initialize the API client
        self.api = None
        self._initialize_client()
    
    def _has_credentials(self) -> bool:
        """
        Check if Alpaca API credentials are available.
        
        Returns:
            True if credentials are available, False otherwise.
        """
        key_manager = get_key_manager()
        keys = key_manager.get_key("alpaca")
        return keys is not None and 'api_key' in keys and 'api_secret' in keys
    
    def _initialize_client(self) -> None:
        """Initialize the Alpaca API client with credentials."""
        if not self._has_credentials():
            logger.error("Alpaca API credentials not found")
            raise ValueError("Alpaca API credentials not found in key manager")
        
        try:
            key_manager = get_key_manager()
            keys = key_manager.get_key("alpaca")
            api_key = keys['api_key']
            api_secret = keys['api_secret']
            
            base_url = 'https://paper-api.alpaca.markets' if self.paper else 'https://api.alpaca.markets'
            
            self.api = REST(
                key_id=api_key,
                secret_key=api_secret,
                base_url=base_url
            )
            logger.info(f"Alpaca API client initialized (paper: {self.paper})")
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca API client: {e}")
            raise
    
    def _get_cached_data(self, cache_key: str) -> Tuple[bool, Any]:
        """
        Get data from cache if available and not expired.
        
        Args:
            cache_key: The cache key to retrieve data for.
            
        Returns:
            Tuple of (is_valid, data), where is_valid is True if cached data exists
            and is not expired, and data is the cached data (or None if not valid).
        """
        cache_entry = self._cache.get(cache_key)
        if not cache_entry:
            return False, None
        
        # Check if cache has expired
        current_time = time.time()
        if (current_time - cache_entry['timestamp']) > self.cache_ttl:
            return False, None
        
        return True, cache_entry['data']
    
    def _update_cache(self, cache_key: str, data: Any) -> None:
        """
        Update cached data.
        
        Args:
            cache_key: The cache key to update.
            data: The data to cache.
        """
        self._cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_account(self, use_cache: bool = True) -> Account:
        """
        Get account information from Alpaca.
        
        Args:
            use_cache: If True, use cached data if available.
            
        Returns:
            Account information.
            
        Raises:
            ValueError: If API credentials are not available.
            APIError: If the Alpaca API returns an error.
        """
        if not self.api:
            self._initialize_client()
        
        # Check cache first if requested
        if use_cache:
            is_valid, cached_data = self._get_cached_data('account')
            if is_valid:
                return cached_data
        
        # Call API with retry logic
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                account = self.api.get_account()
                # Update cache
                self._update_cache('account', account)
                return account
            except APIError as e:
                if e.status_code == 429:  # Rate limit exceeded
                    logger.warning(f"Alpaca API rate limit exceeded. Waiting {self.rate_limit_delay} seconds...")
                    time.sleep(self.rate_limit_delay)
                    retry_count += 1
                    continue
                elif retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)  # Exponential backoff
                    logger.warning(f"Alpaca API error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to get account information: {e}")
                raise
            except Exception as e:
                if retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Unexpected error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to get account information: {e}")
                raise
    
    def get_positions(self, use_cache: bool = True) -> List[Position]:
        """
        Get positions from Alpaca.
        
        Args:
            use_cache: If True, use cached data if available.
            
        Returns:
            List of positions.
            
        Raises:
            ValueError: If API credentials are not available.
            APIError: If the Alpaca API returns an error.
        """
        if not self.api:
            self._initialize_client()
        
        # Check cache first if requested
        if use_cache:
            is_valid, cached_data = self._get_cached_data('positions')
            if is_valid:
                return cached_data
        
        # Call API with retry logic
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                positions = self.api.list_positions()
                # Update cache
                self._update_cache('positions', positions)
                return positions
            except APIError as e:
                if e.status_code == 429:  # Rate limit exceeded
                    logger.warning(f"Alpaca API rate limit exceeded. Waiting {self.rate_limit_delay} seconds...")
                    time.sleep(self.rate_limit_delay)
                    retry_count += 1
                    continue
                elif retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Alpaca API error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to get positions: {e}")
                raise
            except Exception as e:
                if retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Unexpected error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to get positions: {e}")
                raise
    
    def get_orders(self, status: str = "open", use_cache: bool = True) -> List[Order]:
        """
        Get orders from Alpaca.
        
        Args:
            status: Order status filter. Default is "open".
            use_cache: If True, use cached data if available.
            
        Returns:
            List of orders.
            
        Raises:
            ValueError: If API credentials are not available.
            APIError: If the Alpaca API returns an error.
        """
        if not self.api:
            self._initialize_client()
        
        # Check cache first if requested and status is "open" (cache only applies to open orders)
        if use_cache and status == "open":
            is_valid, cached_data = self._get_cached_data('orders')
            if is_valid:
                return cached_data
        
        # Call API with retry logic
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                orders = self.api.list_orders(status=status)
                # Update cache if status is "open"
                if status == "open":
                    self._update_cache('orders', orders)
                return orders
            except APIError as e:
                if e.status_code == 429:  # Rate limit exceeded
                    logger.warning(f"Alpaca API rate limit exceeded. Waiting {self.rate_limit_delay} seconds...")
                    time.sleep(self.rate_limit_delay)
                    retry_count += 1
                    continue
                elif retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Alpaca API error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to get orders: {e}")
                raise
            except Exception as e:
                if retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Unexpected error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to get orders: {e}")
                raise
    
    def get_bars(
        self,
        symbol: str,
        timeframe: str = "1Day",
        start: Optional[Union[str, datetime]] = None,
        end: Optional[Union[str, datetime]] = None,
        limit: int = 100,
        adjustment: str = 'raw'
    ) -> pd.DataFrame:
        """
        Get historical bar data from Alpaca.
        
        Args:
            symbol: Stock symbol to get data for.
            timeframe: Bar timeframe (e.g., "1Min", "1Hour", "1Day").
            start: Start date/time. If None, calculated based on limit and timeframe.
            end: End date/time. If None, current time is used.
            limit: Maximum number of bars to return.
            adjustment: Adjustment type ("raw", "split", "dividend", "all").
            
        Returns:
            DataFrame with bar data.
            
        Raises:
            ValueError: If API credentials are not available or parameters are invalid.
            APIError: If the Alpaca API returns an error.
        """
        if not self.api:
            self._initialize_client()
        
        # Set default end time to now if not provided
        if end is None:
            end = datetime.now()
        elif isinstance(end, str):
            end = pd.Timestamp(end).to_pydatetime()
        
        # Set default start time based on limit and timeframe if not provided
        if start is None:
            if timeframe.endswith('Min'):
                minutes = int(timeframe.replace('Min', ''))
                start = end - timedelta(minutes=minutes * limit)
            elif timeframe.endswith('Hour'):
                hours = int(timeframe.replace('Hour', ''))
                start = end - timedelta(hours=hours * limit)
            elif timeframe.endswith('Day'):
                days = int(timeframe.replace('Day', ''))
                start = end - timedelta(days=days * limit)
            else:
                # Default to 100 days if timeframe is not recognized
                start = end - timedelta(days=100)
        elif isinstance(start, str):
            start = pd.Timestamp(start).to_pydatetime()
        
        # Call API with retry logic
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                bars = self.api.get_bars(
                    symbol=symbol,
                    timeframe=timeframe,
                    start=start,
                    end=end,
                    limit=limit,
                    adjustment=adjustment
                ).df
                
                # If DataFrame is empty, log warning
                if bars.empty:
                    logger.warning(f"No bar data returned for {symbol} ({timeframe})")
                
                return bars
            except APIError as e:
                if e.status_code == 429:  # Rate limit exceeded
                    logger.warning(f"Alpaca API rate limit exceeded. Waiting {self.rate_limit_delay} seconds...")
                    time.sleep(self.rate_limit_delay)
                    retry_count += 1
                    continue
                elif retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Alpaca API error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to get bar data for {symbol}: {e}")
                raise
            except Exception as e:
                if retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Unexpected error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to get bar data for {symbol}: {e}")
                raise
    
    def submit_order(
        self,
        symbol: str,
        qty: Optional[float] = None,
        side: str = "buy",
        type: str = "market",
        time_in_force: str = "day",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        notional: Optional[float] = None,
        client_order_id: Optional[str] = None,
        order_class: Optional[str] = None,
        take_profit: Optional[Dict[str, float]] = None,
        stop_loss: Optional[Dict[str, float]] = None
    ) -> Order:
        """
        Submit an order to Alpaca.
        
        Args:
            symbol: Stock symbol to submit order for.
            qty: Quantity of shares to trade. Set to None if using notional amount.
            side: Order side ("buy" or "sell").
            type: Order type ("market", "limit", "stop", "stop_limit").
            time_in_force: Time in force ("day", "gtc", "opg", "cls", "ioc", "fok").
            limit_price: Limit price for limit orders.
            stop_price: Stop price for stop or stop_limit orders.
            notional: Notional amount (dollar value) instead of quantity.
            client_order_id: Custom client order ID.
            order_class: Order class ("simple", "bracket", "oco", "oto").
            take_profit: Take profit configuration for bracket orders.
            stop_loss: Stop loss configuration for bracket orders.
            
        Returns:
            Submitted order information.
            
        Raises:
            ValueError: If API credentials are not available or parameters are invalid.
            APIError: If the Alpaca API returns an error.
        """
        if not self.api:
            self._initialize_client()
        
        # Validate parameters
        if qty is None and notional is None:
            raise ValueError("Either qty or notional must be specified")
        
        if qty is not None and notional is not None:
            raise ValueError("Only one of qty or notional can be specified")
        
        if type in ["limit", "stop_limit"] and limit_price is None:
            raise ValueError(f"limit_price must be specified for {type} orders")
        
        if type in ["stop", "stop_limit"] and stop_price is None:
            raise ValueError(f"stop_price must be specified for {type} orders")
        
        order_params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "time_in_force": time_in_force
        }
        
        if qty is not None:
            order_params["qty"] = str(qty)
        
        if notional is not None:
            order_params["notional"] = str(notional)
        
        if limit_price is not None:
            order_params["limit_price"] = str(limit_price)
        
        if stop_price is not None:
            order_params["stop_price"] = str(stop_price)
        
        if client_order_id is not None:
            order_params["client_order_id"] = client_order_id
        
        if order_class is not None:
            order_params["order_class"] = order_class
        
        if take_profit is not None:
            order_params["take_profit"] = take_profit
        
        if stop_loss is not None:
            order_params["stop_loss"] = stop_loss
        
        # Call API with retry logic
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                order = self.api.submit_order(**order_params)
                
                # Invalidate orders cache since we've submitted a new order
                self._cache['orders']['timestamp'] = 0
                
                return order
            except APIError as e:
                if e.status_code == 429:  # Rate limit exceeded
                    logger.warning(f"Alpaca API rate limit exceeded. Waiting {self.rate_limit_delay} seconds...")
                    time.sleep(self.rate_limit_delay)
                    retry_count += 1
                    continue
                elif retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Alpaca API error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to submit order for {symbol}: {e}")
                raise
            except Exception as e:
                if retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Unexpected error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to submit order for {symbol}: {e}")
                raise
    
    def cancel_order(self, order_id: str) -> None:
        """
        Cancel an open order.
        
        Args:
            order_id: Order ID to cancel.
            
        Raises:
            ValueError: If API credentials are not available.
            APIError: If the Alpaca API returns an error.
        """
        if not self.api:
            self._initialize_client()
        
        # Call API with retry logic
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                self.api.cancel_order(order_id)
                
                # Invalidate orders cache since we've canceled an order
                self._cache['orders']['timestamp'] = 0
                
                return
            except APIError as e:
                # If the order is not found or already canceled, consider it a success
                if e.status_code == 404 and "404 Not Found" in str(e):
                    logger.warning(f"Order {order_id} not found. It may have already been filled or canceled.")
                    return
                
                if e.status_code == 429:  # Rate limit exceeded
                    logger.warning(f"Alpaca API rate limit exceeded. Waiting {self.rate_limit_delay} seconds...")
                    time.sleep(self.rate_limit_delay)
                    retry_count += 1
                    continue
                elif retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Alpaca API error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to cancel order {order_id}: {e}")
                raise
            except Exception as e:
                if retry_count < self.max_retries:
                    retry_count += 1
                    delay = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Unexpected error: {e}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Failed to cancel order {order_id}: {e}")
                raise

# Global instance for convenience
alpaca_client = AlpacaClient()

def get_alpaca_client() -> AlpacaClient:
    """Get the global AlpacaClient instance."""
    return alpaca_client 