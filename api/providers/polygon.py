"""
Polygon API Client

A robust client for interacting with the Polygon.io API.
Provides market data services with error handling, automatic
retries, and caching capabilities.
"""

import logging
import time
import json
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Any, Union, Tuple

import pandas as pd
import requests

from api.auth.key_manager import get_key_manager

# Configure logger
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 2  # seconds
DEFAULT_CACHE_TTL = 300  # 5 minutes in seconds
MAX_RETRY_DELAY = 30  # maximum delay between retries in seconds

class PolygonClient:
    """
    Client for the Polygon.io API with caching and error handling.
    
    This client provides methods to access various Polygon API endpoints
    with built-in error handling, automatic retries for failed requests,
    and caching to minimize API usage.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.polygon.io",
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_delay: int = DEFAULT_RETRY_DELAY,
        cache_ttl: int = DEFAULT_CACHE_TTL,
    ):
        """
        Initialize the Polygon API client.
        
        Args:
            api_key: Polygon API key. If None, will attempt to load from key manager.
            base_url: Base URL for the Polygon API.
            retry_count: Maximum number of retry attempts for failed requests.
            retry_delay: Initial delay between retries in seconds (doubles after each retry).
            cache_ttl: Cache time-to-live in seconds.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.cache_ttl = cache_ttl
        
        # In-memory cache
        self._cache = {}
        self._cache_timestamps = {}
        
        # Check credentials
        if not self.api_key:
            self._load_credentials()
        
        if not self.api_key:
            logger.warning("No Polygon API key provided or found in key manager")
            
    def _load_credentials(self) -> None:
        """
        Load Polygon API credentials from the key manager.
        """
        key_manager = get_key_manager()
        polygon_keys = key_manager.get_key("polygon")
        
        if polygon_keys and "api_key" in polygon_keys:
            self.api_key = polygon_keys["api_key"]
            logger.info("Loaded Polygon API key from key manager")
        else:
            logger.warning("No Polygon API key found in key manager")
    
    def _check_credentials(self) -> bool:
        """
        Check if valid API credentials are available.
        
        Returns:
            bool: True if API key is available, False otherwise.
        """
        if not self.api_key:
            logger.error("Polygon API key is required")
            return False
        return True
    
    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """
        Generate a cache key for an API request.
        
        Args:
            endpoint: API endpoint path.
            params: Request parameters.
            
        Returns:
            Cache key string.
        """
        # Sort params to ensure consistent caching
        sorted_params = sorted(params.items())
        return f"{endpoint}:{json.dumps(sorted_params)}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """
        Try to get a cached response.
        
        Args:
            cache_key: Cache key to lookup.
            
        Returns:
            Cached response or None if not found or expired.
        """
        if cache_key not in self._cache:
            return None
            
        timestamp = self._cache_timestamps.get(cache_key)
        if not timestamp or (time.time() - timestamp) > self.cache_ttl:
            # Cache expired
            del self._cache[cache_key]
            if cache_key in self._cache_timestamps:
                del self._cache_timestamps[cache_key]
            return None
            
        return self._cache[cache_key]
    
    def _cache_response(self, cache_key: str, response: Any) -> None:
        """
        Cache an API response.
        
        Args:
            cache_key: Cache key to use.
            response: Response data to cache.
        """
        self._cache[cache_key] = response
        self._cache_timestamps[cache_key] = time.time()
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Make a request to the Polygon API with retry logic.
        
        Args:
            endpoint: API endpoint path.
            params: Query parameters.
            use_cache: Whether to use the cache.
            
        Returns:
            API response data.
            
        Raises:
            requests.RequestException: If all retry attempts fail.
        """
        if not self._check_credentials():
            raise ValueError("Missing Polygon API key")
            
        # Prepare request
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Add API key to params
        if params is None:
            params = {}
        
        params = params.copy()  # Don't modify the original
        params["apiKey"] = self.api_key
        
        # Generate cache key and check cache
        cache_key = self._get_cache_key(endpoint, params)
        if use_cache:
            cached_response = self._get_from_cache(cache_key)
            if cached_response is not None:
                logger.debug(f"Cache hit for {endpoint}")
                return cached_response
        
        # Make request with retry logic
        retry_count = 0
        delay = self.retry_delay
        
        while True:
            try:
                logger.debug(f"Making request to {endpoint}")
                response = requests.get(url, params=params)
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(f"Rate limit exceeded for {endpoint}, retrying after delay")
                    retry_count += 1
                    
                    # Check if max retries exceeded
                    if retry_count > self.retry_count:
                        raise requests.RequestException(
                            f"Max retries exceeded for {endpoint}: Rate limit error"
                        )
                        
                    # Get retry-after header if available, otherwise use exponential backoff
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        delay = int(retry_after)
                    else:
                        # Exponential backoff with jitter
                        delay = min(delay * 2, MAX_RETRY_DELAY)
                        
                    logger.info(f"Retrying after {delay}s (attempt {retry_count}/{self.retry_count})")
                    time.sleep(delay)
                    continue
                
                # Handle other errors
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                # Check for API errors
                if "error" in data:
                    error_message = data.get("error", "Unknown API error")
                    logger.error(f"API error for {endpoint}: {error_message}")
                    raise requests.RequestException(f"API error: {error_message}")
                
                # Cache response
                if use_cache:
                    self._cache_response(cache_key, data)
                
                return data
                
            except (requests.RequestException, json.JSONDecodeError) as e:
                logger.warning(f"Error requesting {endpoint}: {str(e)}")
                
                # Don't retry on client errors (400-level), except for rate limiting (429)
                if isinstance(e, requests.HTTPError) and 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    logger.error(f"Client error {e.response.status_code} for {endpoint}, not retrying")
                    raise
                
                retry_count += 1
                if retry_count > self.retry_count:
                    logger.error(f"Max retries exceeded for {endpoint}")
                    raise
                
                # Exponential backoff with jitter
                delay = min(delay * 2, MAX_RETRY_DELAY)
                logger.info(f"Retrying after {delay}s (attempt {retry_count}/{self.retry_count})")
                time.sleep(delay)
    
    def get_ticker_details(self, ticker: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get ticker details from Polygon.
        
        Args:
            ticker: The ticker symbol to look up.
            use_cache: Whether to use cached responses.
            
        Returns:
            Ticker details.
            
        Raises:
            requests.RequestException: If the request fails.
        """
        endpoint = f"v3/reference/tickers/{ticker}"
        
        try:
            return self._make_request(endpoint, use_cache=use_cache)
        except Exception as e:
            logger.error(f"Error fetching ticker details for {ticker}: {str(e)}")
            raise
    
    def get_aggs(
        self,
        ticker: str,
        multiplier: int = 1,
        timespan: str = "day",
        from_date: Union[str, datetime] = None,
        to_date: Union[str, datetime] = None,
        limit: int = 100,
        adjusted: bool = True,
        sort: str = "desc",
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Get aggregated bars for a ticker.
        
        Args:
            ticker: The ticker symbol.
            multiplier: The multiplier for the timespan.
            timespan: The timespan unit (minute, hour, day, week, month, quarter, year).
            from_date: The start date (YYYY-MM-DD) or datetime object.
            to_date: The end date (YYYY-MM-DD) or datetime object.
            limit: The maximum number of results to return.
            adjusted: Whether to return adjusted data.
            sort: The sort order for results (asc or desc).
            use_cache: Whether to use cached responses.
            
        Returns:
            Aggregated bar data.
            
        Raises:
            requests.RequestException: If the request fails.
        """
        # Format dates if provided
        params = {
            "adjusted": str(adjusted).lower(),
            "sort": sort,
            "limit": limit,
        }
        
        if from_date:
            if isinstance(from_date, datetime):
                from_date = from_date.strftime("%Y-%m-%d")
            params["from"] = from_date
            
        if to_date:
            if isinstance(to_date, datetime):
                to_date = to_date.strftime("%Y-%m-%d")
            params["to"] = to_date
        
        endpoint = f"v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}"
        
        try:
            return self._make_request(endpoint, params, use_cache=use_cache)
        except Exception as e:
            logger.error(f"Error fetching aggregated bars for {ticker}: {str(e)}")
            raise
    
    def get_previous_close(self, ticker: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get the previous day's close price for a ticker.
        
        Args:
            ticker: The ticker symbol.
            use_cache: Whether to use cached responses.
            
        Returns:
            Previous close data.
            
        Raises:
            requests.RequestException: If the request fails.
        """
        endpoint = f"v2/aggs/ticker/{ticker}/prev"
        
        try:
            return self._make_request(endpoint, use_cache=use_cache)
        except Exception as e:
            logger.error(f"Error fetching previous close for {ticker}: {str(e)}")
            raise
    
    def get_daily_open_close(
        self,
        ticker: str,
        date: Union[str, datetime],
        adjusted: bool = True,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Get daily open/close data for a ticker.
        
        Args:
            ticker: The ticker symbol.
            date: The date (YYYY-MM-DD) or datetime object.
            adjusted: Whether to return adjusted data.
            use_cache: Whether to use cached responses.
            
        Returns:
            Daily open/close data.
            
        Raises:
            requests.RequestException: If the request fails.
        """
        # Format date
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
            
        params = {
            "adjusted": str(adjusted).lower(),
        }
        
        endpoint = f"v1/open-close/{ticker}/{date}"
        
        try:
            return self._make_request(endpoint, params, use_cache=use_cache)
        except Exception as e:
            logger.error(f"Error fetching daily open/close for {ticker} on {date}: {str(e)}")
            raise
    
    def get_ticker_news(
        self,
        ticker: str = None,
        limit: int = 10,
        order: str = "desc",
        sort: str = "published_utc",
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Get news articles for a ticker.
        
        Args:
            ticker: The ticker symbol (optional).
            limit: The maximum number of results to return.
            order: The sort order (asc or desc).
            sort: The field to sort by.
            use_cache: Whether to use cached responses.
            
        Returns:
            News articles.
            
        Raises:
            requests.RequestException: If the request fails.
        """
        params = {
            "limit": limit,
            "order": order,
            "sort": sort,
        }
        
        if ticker:
            params["ticker"] = ticker
            
        endpoint = "v2/reference/news"
        
        try:
            return self._make_request(endpoint, params, use_cache=use_cache)
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {str(e)}")
            raise
    
    def get_market_status(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get current market status.
        
        Args:
            use_cache: Whether to use cached responses.
            
        Returns:
            Market status.
            
        Raises:
            requests.RequestException: If the request fails.
        """
        endpoint = "v1/marketstatus/now"
        
        try:
            return self._make_request(endpoint, use_cache=use_cache)
        except Exception as e:
            logger.error(f"Error fetching market status: {str(e)}")
            raise
    
    def clear_cache(self) -> None:
        """
        Clear the response cache.
        """
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Polygon API cache cleared")
    
    def get_tickers(
        self,
        ticker_type: str = "cs",  # Common stock
        market: str = "stocks",
        exchange: str = "XNYS",  # NYSE
        limit: int = 100,
        active: bool = True,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Get a list of tickers.
        
        Args:
            ticker_type: The type of ticker (cs = Common Stock, etc.)
            market: The market (stocks, crypto, fx, otc)
            exchange: The exchange code
            limit: The maximum number of results to return
            active: Whether to return only active tickers
            use_cache: Whether to use cached responses
            
        Returns:
            List of tickers
            
        Raises:
            requests.RequestException: If the request fails
        """
        params = {
            "type": ticker_type,
            "market": market,
            "exchange": exchange,
            "limit": limit,
            "active": str(active).lower(),
        }
        
        endpoint = "v3/reference/tickers"
        
        try:
            return self._make_request(endpoint, params, use_cache=use_cache)
        except Exception as e:
            logger.error(f"Error fetching tickers: {str(e)}")
            raise
    
    def get_ticker_types(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get available ticker types.
        
        Args:
            use_cache: Whether to use cached responses
            
        Returns:
            List of ticker types
            
        Raises:
            requests.RequestException: If the request fails
        """
        endpoint = "v3/reference/tickers/types"
        
        try:
            return self._make_request(endpoint, use_cache=use_cache)
        except Exception as e:
            logger.error(f"Error fetching ticker types: {str(e)}")
            raise
    
    def get_exchanges(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get a list of exchanges.
        
        Args:
            use_cache: Whether to use cached responses
            
        Returns:
            List of exchanges
            
        Raises:
            requests.RequestException: If the request fails
        """
        endpoint = "v3/reference/exchanges"
        
        try:
            return self._make_request(endpoint, use_cache=use_cache)
        except Exception as e:
            logger.error(f"Error fetching exchanges: {str(e)}")
            raise

# Global client instance
_polygon_client_instance = None

def get_polygon_client() -> PolygonClient:
    """
    Get the global PolygonClient instance.
    
    Returns:
        PolygonClient instance.
    """
    global _polygon_client_instance
    
    if _polygon_client_instance is None:
        _polygon_client_instance = PolygonClient()
    
    return _polygon_client_instance

def init_polygon_client(
    api_key: Optional[str] = None,
    base_url: str = "https://api.polygon.io",
    retry_count: int = DEFAULT_RETRY_COUNT,
    retry_delay: int = DEFAULT_RETRY_DELAY,
    cache_ttl: int = DEFAULT_CACHE_TTL,
) -> PolygonClient:
    """
    Initialize the global PolygonClient instance.
    
    Args:
        api_key: Polygon API key. If None, will attempt to load from key manager.
        base_url: Base URL for the Polygon API.
        retry_count: Maximum number of retry attempts for failed requests.
        retry_delay: Initial delay between retries in seconds (doubles after each retry).
        cache_ttl: Cache time-to-live in seconds.
        
    Returns:
        PolygonClient instance.
    """
    global _polygon_client_instance
    
    _polygon_client_instance = PolygonClient(
        api_key=api_key,
        base_url=base_url,
        retry_count=retry_count,
        retry_delay=retry_delay,
        cache_ttl=cache_ttl,
    )
    
    return _polygon_client_instance 