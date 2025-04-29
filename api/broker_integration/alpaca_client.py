"""
Alpaca API Client

Provides a high-level interface to the Alpaca trading API.
Handles authentication, rate limiting, error handling, and request retries.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from requests.exceptions import RequestException

# Import key manager
from api.utils.key_manager import get_key_manager

# Configure logging
logger = logging.getLogger(__name__)

class AlpacaAPIError(Exception):
    """Base exception for Alpaca API related errors."""
    pass

class AlpacaClient:
    """
    Client for interacting with the Alpaca trading API.
    
    Features:
    - Authentication with API keys
    - Rate limiting and request throttling
    - Error handling and request retries
    - Paper/live trading mode
    """
    
    # API base URLs
    PAPER_API_URL = "https://paper-api.alpaca.markets"
    LIVE_API_URL = "https://api.alpaca.markets"
    DATA_API_URL = "https://data.alpaca.markets"
    
    # Request timeouts and retry settings
    DEFAULT_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    def __init__(self, 
        paper_trading: bool = True,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None
    ):
        """
        Initialize Alpaca client.
        
        Args:
            paper_trading: Whether to use paper trading mode.
            api_key: Alpaca API key (optional, will load from key manager if not provided).
            api_secret: Alpaca API secret (optional, will load from key manager if not provided).
        """
        self.paper_trading = paper_trading
        self.base_url = self.PAPER_API_URL if paper_trading else self.LIVE_API_URL
        
        # Load API keys from key manager if not provided
        if not api_key or not api_secret:
            key_manager = get_key_manager()
            service = "alpaca_paper" if paper_trading else "alpaca_live"
            
            api_key = api_key or key_manager.get_key(service, "api_key")
            api_secret = api_secret or key_manager.get_key(service, "api_secret")
        
        # Store API keys
        self.api_key = api_key
        self.api_secret = api_secret
        
        if not self.api_key or not self.api_secret:
            logger.warning("Alpaca API keys not provided and not found in key manager")
        
        # Request tracking
        self.last_request_time = 0
        self.request_count = 0
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for API requests.
        
        Returns:
            Dictionary of HTTP headers.
        """
        return {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
            "Content-Type": "application/json"
        }
    
    def _handle_rate_limit(self) -> None:
        """
        Handle API rate limiting.
        
        Implements a simple rate limiting mechanism to avoid exceeding API limits.
        """
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        # Simple rate limiting: maximum 200 requests per minute
        if elapsed < 0.3 and self.request_count > 0:  # 200 requests per minute = 1 request per 0.3 seconds
            sleep_time = 0.3 - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _request(self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        api_version: str = "v2",
        use_data_api: bool = False
    ) -> Dict[str, Any]:
        """
        Make API request with retries and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint.
            data: Request data.
            params: Query parameters.
            timeout: Request timeout in seconds.
            api_version: API version.
            use_data_api: Whether to use the data API URL.
            
        Returns:
            API response data.
            
        Raises:
            AlpacaAPIError: If the API request fails.
        """
        # Set base URL
        if use_data_api:
            base_url = self.DATA_API_URL
        else:
            base_url = self.base_url
        
        # Build URL
        url = f"{base_url}/{api_version}/{endpoint}"
        
        # Set timeout
        timeout = timeout or self.DEFAULT_TIMEOUT
        
        # Initialize retry count
        retry_count = 0
        
        while retry_count <= self.MAX_RETRIES:
            try:
                # Handle rate limiting
                self._handle_rate_limit()
                
                # Make request
                logger.debug(f"Making {method} request to {url}")
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=self._get_headers(),
                    timeout=timeout
                )
                
                # Check for HTTP errors
                response.raise_for_status()
                
                # Parse response
                if response.content:
                    return response.json()
                else:
                    return {}
                
            except RequestException as e:
                logger.warning(f"API request failed: {str(e)}")
                
                # Handle specific error cases
                if hasattr(e, "response") and e.response is not None:
                    status_code = e.response.status_code
                    
                    # Handle rate limiting
                    if status_code == 429:
                        retry_after = int(e.response.headers.get("Retry-After", "60"))
                        logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                        time.sleep(retry_after)
                        retry_count += 1
                        continue
                    
                    # Handle server errors
                    if status_code >= 500:
                        retry_count += 1
                        sleep_time = self.RETRY_DELAY * (2 ** retry_count)  # Exponential backoff
                        logger.warning(f"Server error, retrying in {sleep_time} seconds")
                        time.sleep(sleep_time)
                        continue
                    
                    # Handle client errors
                    try:
                        error_data = e.response.json()
                        error_message = error_data.get("message", str(e))
                        raise AlpacaAPIError(f"API error: {error_message} (status: {status_code})")
                    except (ValueError, KeyError):
                        # Failed to parse error response
                        error_message = e.response.text or str(e)
                        raise AlpacaAPIError(f"API error: {error_message} (status: {status_code})")
                
                # Handle connection errors
                retry_count += 1
                if retry_count <= self.MAX_RETRIES:
                    sleep_time = self.RETRY_DELAY * (2 ** retry_count)  # Exponential backoff
                    logger.warning(f"Connection error, retrying in {sleep_time} seconds")
                    time.sleep(sleep_time)
                else:
                    raise AlpacaAPIError(f"API request failed after {self.MAX_RETRIES} retries: {str(e)}")
    
    # Account endpoints
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Account information.
        """
        return self._request("GET", "account")
    
    def get_account_configurations(self) -> Dict[str, Any]:
        """
        Get account configurations.
        
        Returns:
            Account configurations.
        """
        return self._request("GET", "account/configurations")
    
    def update_account_configurations(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update account configurations.
        
        Args:
            config: Account configurations.
            
        Returns:
            Updated account configurations.
        """
        return self._request("PATCH", "account/configurations", data=config)
    
    # Order endpoints
    
    def submit_order(self, 
        symbol: str,
        qty: Optional[float] = None,
        notional: Optional[float] = None,
        side: str = "buy",
        type: str = "market",
        time_in_force: str = "day",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        client_order_id: Optional[str] = None,
        order_class: Optional[str] = None,
        take_profit: Optional[Dict[str, Any]] = None,
        stop_loss: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit a new order.
        
        Args:
            symbol: Asset symbol.
            qty: Order quantity.
            notional: Order notional value (alternative to qty).
            side: Order side (buy, sell).
            type: Order type (market, limit, stop, stop_limit).
            time_in_force: Time in force (day, gtc, ioc, fok).
            limit_price: Limit price for limit orders.
            stop_price: Stop price for stop orders.
            client_order_id: Client order ID.
            order_class: Order class (simple, bracket, oco, oto).
            take_profit: Take profit settings.
            stop_loss: Stop loss settings.
            
        Returns:
            Order information.
        """
        # Validate parameters
        if qty is None and notional is None:
            raise ValueError("Either qty or notional must be specified")
        
        if qty is not None and notional is not None:
            raise ValueError("Only one of qty or notional can be specified")
        
        # Build order data
        data = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "time_in_force": time_in_force
        }
        
        # Set quantity or notional
        if qty is not None:
            data["qty"] = str(qty)
        elif notional is not None:
            data["notional"] = str(notional)
        
        # Add optional parameters
        if limit_price is not None:
            data["limit_price"] = str(limit_price)
        
        if stop_price is not None:
            data["stop_price"] = str(stop_price)
        
        if client_order_id is not None:
            data["client_order_id"] = client_order_id
        
        if order_class is not None:
            data["order_class"] = order_class
        
        if take_profit is not None:
            data["take_profit"] = take_profit
        
        if stop_loss is not None:
            data["stop_loss"] = stop_loss
        
        return self._request("POST", "orders", data=data)
    
    def get_orders(self, 
        status: Optional[str] = None,
        limit: int = 100,
        after: Optional[str] = None,
        until: Optional[str] = None,
        direction: str = "desc",
        nested: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get orders.
        
        Args:
            status: Order status (open, closed, all).
            limit: Maximum number of orders to return.
            after: Filter orders after this timestamp.
            until: Filter orders until this timestamp.
            direction: Sort direction (asc, desc).
            nested: Whether to include nested orders.
            
        Returns:
            List of orders.
        """
        params = {"limit": limit, "direction": direction, "nested": nested}
        
        if status is not None:
            params["status"] = status
        
        if after is not None:
            params["after"] = after
        
        if until is not None:
            params["until"] = until
        
        return self._request("GET", "orders", params=params)
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get order by ID.
        
        Args:
            order_id: Order ID.
            
        Returns:
            Order information.
        """
        return self._request("GET", f"orders/{order_id}")
    
    def get_order_by_client_id(self, client_order_id: str) -> Dict[str, Any]:
        """
        Get order by client order ID.
        
        Args:
            client_order_id: Client order ID.
            
        Returns:
            Order information.
        """
        return self._request("GET", f"orders:by_client_order_id", params={"client_order_id": client_order_id})
    
    def cancel_order(self, order_id: str) -> None:
        """
        Cancel order.
        
        Args:
            order_id: Order ID.
        """
        return self._request("DELETE", f"orders/{order_id}")
    
    def cancel_all_orders(self) -> List[Dict[str, Any]]:
        """
        Cancel all orders.
        
        Returns:
            List of canceled orders.
        """
        return self._request("DELETE", "orders")
    
    # Position endpoints
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all positions.
        
        Returns:
            List of positions.
        """
        return self._request("GET", "positions")
    
    def get_position(self, symbol: str) -> Dict[str, Any]:
        """
        Get position by symbol.
        
        Args:
            symbol: Asset symbol.
            
        Returns:
            Position information.
        """
        return self._request("GET", f"positions/{symbol}")
    
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """
        Close position.
        
        Args:
            symbol: Asset symbol.
            
        Returns:
            Position information.
        """
        return self._request("DELETE", f"positions/{symbol}")
    
    def close_all_positions(self) -> List[Dict[str, Any]]:
        """
        Close all positions.
        
        Returns:
            List of closed positions.
        """
        return self._request("DELETE", "positions")
    
    # Asset endpoints
    
    def get_assets(self, status: str = "active", asset_class: str = "us_equity") -> List[Dict[str, Any]]:
        """
        Get assets.
        
        Args:
            status: Asset status (active, inactive).
            asset_class: Asset class (us_equity, crypto).
            
        Returns:
            List of assets.
        """
        params = {"status": status, "asset_class": asset_class}
        return self._request("GET", "assets", params=params)
    
    def get_asset(self, symbol: str) -> Dict[str, Any]:
        """
        Get asset by symbol.
        
        Args:
            symbol: Asset symbol.
            
        Returns:
            Asset information.
        """
        return self._request("GET", f"assets/{symbol}")
    
    # Market data endpoints
    
    def get_bars(self, 
        symbol: str,
        timeframe: str = "1D",
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 100,
        adjustment: str = "raw"
    ) -> List[Dict[str, Any]]:
        """
        Get bars (OHLC) data.
        
        Args:
            symbol: Asset symbol.
            timeframe: Bar timeframe (1Min, 5Min, 15Min, 1H, 1D).
            start: Start date/time (ISO 8601 format).
            end: End date/time (ISO 8601 format).
            limit: Maximum number of bars to return.
            adjustment: Price adjustment (raw, split, dividend, all).
            
        Returns:
            List of bars.
        """
        params = {
            "symbols": symbol,
            "timeframe": timeframe,
            "limit": limit,
            "adjustment": adjustment
        }
        
        if start is not None:
            params["start"] = start
        
        if end is not None:
            params["end"] = end
        
        response = self._request("GET", "bars", params=params, use_data_api=True)
        return response.get("bars", {}).get(symbol, [])
    
    def get_last_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get last quote.
        
        Args:
            symbol: Asset symbol.
            
        Returns:
            Quote information.
        """
        params = {"symbols": symbol}
        response = self._request("GET", "quotes/latest", params=params, use_data_api=True)
        return response.get("quotes", {}).get(symbol, {})
    
    def get_last_trade(self, symbol: str) -> Dict[str, Any]:
        """
        Get last trade.
        
        Args:
            symbol: Asset symbol.
            
        Returns:
            Trade information.
        """
        params = {"symbols": symbol}
        response = self._request("GET", "trades/latest", params=params, use_data_api=True)
        return response.get("trades", {}).get(symbol, {})
    
    # Calendar and clock endpoints
    
    def get_calendar(self, 
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get market calendar.
        
        Args:
            start: Start date (YYYY-MM-DD).
            end: End date (YYYY-MM-DD).
            
        Returns:
            List of market calendar days.
        """
        params = {}
        
        if start is not None:
            params["start"] = start
        
        if end is not None:
            params["end"] = end
        
        return self._request("GET", "calendar", params=params)
    
    def get_clock(self) -> Dict[str, Any]:
        """
        Get market clock.
        
        Returns:
            Market clock information.
        """
        return self._request("GET", "clock")
    
    def is_market_open(self) -> bool:
        """
        Check if market is open.
        
        Returns:
            True if market is open, False otherwise.
        """
        clock = self.get_clock()
        return clock.get("is_open", False)
    
    # Watchlist endpoints
    
    def get_watchlists(self) -> List[Dict[str, Any]]:
        """
        Get all watchlists.
        
        Returns:
            List of watchlists.
        """
        return self._request("GET", "watchlists")
    
    def get_watchlist(self, watchlist_id: str) -> Dict[str, Any]:
        """
        Get watchlist by ID.
        
        Args:
            watchlist_id: Watchlist ID.
            
        Returns:
            Watchlist information.
        """
        return self._request("GET", f"watchlists/{watchlist_id}")
    
    def create_watchlist(self, name: str, symbols: List[str]) -> Dict[str, Any]:
        """
        Create watchlist.
        
        Args:
            name: Watchlist name.
            symbols: List of asset symbols.
            
        Returns:
            Watchlist information.
        """
        data = {"name": name, "symbols": symbols}
        return self._request("POST", "watchlists", data=data)
    
    def update_watchlist(self, watchlist_id: str, name: Optional[str] = None, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Update watchlist.
        
        Args:
            watchlist_id: Watchlist ID.
            name: Watchlist name.
            symbols: List of asset symbols.
            
        Returns:
            Watchlist information.
        """
        data = {}
        
        if name is not None:
            data["name"] = name
        
        if symbols is not None:
            data["symbols"] = symbols
        
        return self._request("PUT", f"watchlists/{watchlist_id}", data=data)
    
    def add_to_watchlist(self, watchlist_id: str, symbol: str) -> Dict[str, Any]:
        """
        Add asset to watchlist.
        
        Args:
            watchlist_id: Watchlist ID.
            symbol: Asset symbol.
            
        Returns:
            Watchlist information.
        """
        data = {"symbol": symbol}
        return self._request("POST", f"watchlists/{watchlist_id}", data=data)
    
    def remove_from_watchlist(self, watchlist_id: str, symbol: str) -> Dict[str, Any]:
        """
        Remove asset from watchlist.
        
        Args:
            watchlist_id: Watchlist ID.
            symbol: Asset symbol.
            
        Returns:
            Watchlist information.
        """
        return self._request("DELETE", f"watchlists/{watchlist_id}/{symbol}")
    
    def delete_watchlist(self, watchlist_id: str) -> None:
        """
        Delete watchlist.
        
        Args:
            watchlist_id: Watchlist ID.
        """
        return self._request("DELETE", f"watchlists/{watchlist_id}")
    
    # Helper methods
    
    def get_buying_power(self) -> float:
        """
        Get account buying power.
        
        Returns:
            Buying power.
        """
        account = self.get_account()
        return float(account.get("buying_power", 0))
    
    def get_portfolio_value(self) -> float:
        """
        Get portfolio value.
        
        Returns:
            Portfolio value.
        """
        account = self.get_account()
        return float(account.get("portfolio_value", 0))
    
    def get_cash(self) -> float:
        """
        Get cash balance.
        
        Returns:
            Cash balance.
        """
        account = self.get_account()
        return float(account.get("cash", 0))
    
    def get_asset_price(self, symbol: str) -> float:
        """
        Get current asset price.
        
        Args:
            symbol: Asset symbol.
            
        Returns:
            Current price.
        """
        trade = self.get_last_trade(symbol)
        return float(trade.get("p", 0))
    
    def calculate_order_quantity(self, symbol: str, cash_amount: float) -> float:
        """
        Calculate order quantity based on cash amount.
        
        Args:
            symbol: Asset symbol.
            cash_amount: Cash amount to use for the order.
            
        Returns:
            Order quantity.
        """
        price = self.get_asset_price(symbol)
        
        if price == 0:
            raise AlpacaAPIError(f"Failed to get price for {symbol}")
        
        return round(cash_amount / price, 6)  # Round to 6 decimal places
    
    def place_market_order(self, symbol: str, side: str, qty: Optional[float] = None, notional: Optional[float] = None) -> Dict[str, Any]:
        """
        Place market order.
        
        Args:
            symbol: Asset symbol.
            side: Order side (buy, sell).
            qty: Order quantity.
            notional: Order notional value (alternative to qty).
            
        Returns:
            Order information.
        """
        return self.submit_order(
            symbol=symbol,
            qty=qty,
            notional=notional,
            side=side,
            type="market",
            time_in_force="day"
        )
    
    def place_limit_order(self, symbol: str, side: str, limit_price: float, qty: Optional[float] = None, notional: Optional[float] = None) -> Dict[str, Any]:
        """
        Place limit order.
        
        Args:
            symbol: Asset symbol.
            side: Order side (buy, sell).
            limit_price: Limit price.
            qty: Order quantity.
            notional: Order notional value (alternative to qty).
            
        Returns:
            Order information.
        """
        return self.submit_order(
            symbol=symbol,
            qty=qty,
            notional=notional,
            side=side,
            type="limit",
            limit_price=limit_price,
            time_in_force="day"
        )
    
    def place_stop_order(self, symbol: str, side: str, stop_price: float, qty: Optional[float] = None, notional: Optional[float] = None) -> Dict[str, Any]:
        """
        Place stop order.
        
        Args:
            symbol: Asset symbol.
            side: Order side (buy, sell).
            stop_price: Stop price.
            qty: Order quantity.
            notional: Order notional value (alternative to qty).
            
        Returns:
            Order information.
        """
        return self.submit_order(
            symbol=symbol,
            qty=qty,
            notional=notional,
            side=side,
            type="stop",
            stop_price=stop_price,
            time_in_force="day"
        )
    
    def place_bracket_order(self, 
        symbol: str, 
        side: str, 
        qty: Optional[float] = None,
        notional: Optional[float] = None,
        take_profit_limit_price: float = 0,
        stop_loss_stop_price: float = 0,
        stop_loss_limit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place bracket order (entry order with take profit and stop loss).
        
        Args:
            symbol: Asset symbol.
            side: Order side (buy, sell).
            qty: Order quantity.
            notional: Order notional value (alternative to qty).
            take_profit_limit_price: Take profit limit price.
            stop_loss_stop_price: Stop loss stop price.
            stop_loss_limit_price: Stop loss limit price (optional).
            
        Returns:
            Order information.
        """
        # Build take profit settings
        take_profit = {
            "limit_price": str(take_profit_limit_price)
        }
        
        # Build stop loss settings
        stop_loss = {
            "stop_price": str(stop_loss_stop_price)
        }
        
        if stop_loss_limit_price is not None:
            stop_loss["limit_price"] = str(stop_loss_limit_price)
        
        return self.submit_order(
            symbol=symbol,
            qty=qty,
            notional=notional,
            side=side,
            type="market",
            time_in_force="day",
            order_class="bracket",
            take_profit=take_profit,
            stop_loss=stop_loss
        )

# Factory function to create Alpaca client instance
def get_alpaca_client(paper_trading: bool = True) -> AlpacaClient:
    """
    Get Alpaca client instance.
    
    Args:
        paper_trading: Whether to use paper trading mode.
        
    Returns:
        AlpacaClient instance.
    """
    return AlpacaClient(paper_trading=paper_trading) 