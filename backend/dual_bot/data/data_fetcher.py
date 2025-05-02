"""
Data fetcher module for Dual Bot.
Handles connections to Polygon WebSocket and Unusual Whales API.
"""

import os
import json
import time
import logging
import threading
import websocket
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional, Callable

from ..config.config_loader import load_config

# Initialize logger
logger = logging.getLogger(__name__)

class PolygonWebSocket:
    """Handles real-time market data from Polygon WebSocket."""
    
    def __init__(self, api_key: str, symbols: List[str], callback: Callable):
        """
        Initialize Polygon WebSocket client.
        
        Args:
            api_key: Polygon API key
            symbols: List of symbols to subscribe to
            callback: Function to call when data is received
        """
        self.api_key = api_key
        self.symbols = symbols
        self.callback = callback
        self.ws = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5  # seconds
        
        # Format symbols for subscription
        self.formatted_symbols = [f"T.{symbol}" for symbol in symbols]
    
    def connect(self):
        """Connect to Polygon WebSocket."""
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            f"wss://delayed.polygon.io/stocks",
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        
        # Start WebSocket connection in a separate thread
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
        # Wait for connection to be established
        timeout = 10
        start_time = time.time()
        while not self.connected and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        if not self.connected:
            logger.error("Failed to connect to Polygon WebSocket")
            return False
        
        return True
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            self.callback(data)
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors."""
        logger.error(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close."""
        logger.info("WebSocket connection closed")
        self.connected = False
        
        # Attempt to reconnect
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            logger.info(f"Attempting to reconnect (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
            time.sleep(self.reconnect_delay)
            self.connect()
        else:
            logger.error("Max reconnection attempts reached")
    
    def _on_open(self, ws):
        """Handle WebSocket connection open."""
        logger.info("WebSocket connection established")
        self.connected = True
        
        # Subscribe to symbols
        auth_message = {
            "action": "auth",
            "params": self.api_key
        }
        ws.send(json.dumps(auth_message))
        
        subscribe_message = {
            "action": "subscribe",
            "params": ",".join(self.formatted_symbols)
        }
        ws.send(json.dumps(subscribe_message))
    
    def disconnect(self):
        """Disconnect from Polygon WebSocket."""
        if self.ws:
            self.ws.close()
            self.connected = False

class UnusualWhalesAPI:
    """Handles interactions with Unusual Whales API."""
    
    def __init__(self, api_key: str):
        """
        Initialize Unusual Whales API client.
        
        Args:
            api_key: Unusual Whales API key
        """
        self.api_key = api_key
        self.base_url = "https://api.unusualwhales.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_dark_pool_recent(self, limit: int = 20) -> List[Dict]:
        """
        Get recent dark pool activity.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of dark pool trades
        """
        try:
            response = requests.get(
                f"{self.base_url}/dark_pool/recent",
                headers=self.headers,
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching dark pool data: {e}")
            return []
    
    def get_dark_pool_symbol(self, symbol: str) -> List[Dict]:
        """
        Get dark pool activity for a specific symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of dark pool trades for the symbol
        """
        try:
            response = requests.get(
                f"{self.base_url}/dark_pool/{symbol}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching dark pool data for {symbol}: {e}")
            return []
    
    def get_options_flow(self, symbol: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """
        Get options flow data.
        
        Args:
            symbol: Optional stock symbol to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of options trades
        """
        try:
            url = f"{self.base_url}/options_flow"
            params = {"limit": limit}
            if symbol:
                params["symbol"] = symbol
                
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching options flow data: {e}")
            return []

class NewsAPI:
    """Handles interactions with News API."""
    
    def __init__(self, api_key: str):
        """
        Initialize News API client.
        
        Args:
            api_key: News API key
        """
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
    
    def get_market_news(self, symbols: List[str], days: int = 1) -> List[Dict]:
        """
        Get market news for specific symbols.
        
        Args:
            symbols: List of stock symbols
            days: Number of days to look back
            
        Returns:
            List of news articles
        """
        try:
            # Format date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Build query
            query = " OR ".join(symbols)
            
            response = requests.get(
                f"{self.base_url}/everything",
                params={
                    "q": query,
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d"),
                    "sortBy": "publishedAt",
                    "language": "en",
                    "apiKey": self.api_key
                }
            )
            response.raise_for_status()
            return response.json().get("articles", [])
        except Exception as e:
            logger.error(f"Error fetching news data: {e}")
            return []

class DataFetcher:
    """Main class for fetching and managing market data."""
    
    def __init__(self):
        """Initialize DataFetcher with configuration."""
        self.config = load_config()
        self.polygon_ws = None
        self.unusual_whales = None
        self.news_api = None
        
        # Callbacks
        self.market_data_callback = None
        self.options_flow_callback = None
        self.dark_pool_callback = None
        self.news_callback = None
        
        # Data storage
        self.market_data = {}
        self.options_flow = []
        self.dark_pool_data = []
        self.news_data = []
        
        # Threads
        self.periodic_fetch_thread = None
        self.running = False
    
    def initialize(self):
        """Initialize all data sources."""
        try:
            # Initialize Polygon WebSocket
            if self.config["data_sources"]["polygon"]["enabled"]:
                self.polygon_ws = PolygonWebSocket(
                    api_key=self.config["data_sources"]["polygon"]["api_key"],
                    symbols=self.config["trading"]["symbols"],
                    callback=self._handle_market_data
                )
            
            # Initialize Unusual Whales API
            if self.config["data_sources"]["unusual_whales"]["enabled"]:
                self.unusual_whales = UnusualWhalesAPI(
                    api_key=self.config["data_sources"]["unusual_whales"]["api_key"]
                )
            
            # Initialize News API
            if self.config["data_sources"]["news_api"]["enabled"]:
                self.news_api = NewsAPI(
                    api_key=self.config["data_sources"]["news_api"]["api_key"]
                )
            
            return True
        except Exception as e:
            logger.error(f"Error initializing data sources: {e}")
            return False
    
    def start(self):
        """Start all data sources."""
        if not self.running:
            self.running = True
            
            # Connect to Polygon WebSocket
            if self.polygon_ws:
                self.polygon_ws.connect()
            
            # Start periodic fetching
            self._start_periodic_fetching()
            
            logger.info("Data fetcher started")
    
    def stop(self):
        """Stop all data sources."""
        if self.running:
            self.running = False
            
            # Disconnect from Polygon WebSocket
            if self.polygon_ws:
                self.polygon_ws.disconnect()
            
            # Stop periodic fetching thread
            if self.periodic_fetch_thread:
                self.periodic_fetch_thread.join()
            
            logger.info("Data fetcher stopped")
    
    def _start_periodic_fetching(self):
        """Start periodic data fetching in a separate thread."""
        def periodic_fetch():
            while self.running:
                # Fetch options flow
                self._fetch_options_flow_periodically()
                
                # Fetch dark pool data
                self._fetch_dark_pool_periodically()
                
                # Fetch news
                self._fetch_news_periodically()
                
                # Sleep for a short interval
                time.sleep(60)
        
        self.periodic_fetch_thread = threading.Thread(target=periodic_fetch)
        self.periodic_fetch_thread.daemon = True
        self.periodic_fetch_thread.start()
    
    def _fetch_options_flow_periodically(self, interval: int = 300):
        """Fetch options flow data periodically."""
        if self.unusual_whales and self.options_flow_callback:
            try:
                data = self.unusual_whales.get_options_flow()
                self.options_flow = data
                self.options_flow_callback(data)
            except Exception as e:
                logger.error(f"Error fetching options flow data: {e}")
    
    def _fetch_dark_pool_periodically(self, interval: int = 600):
        """Fetch dark pool data periodically."""
        if self.unusual_whales and self.dark_pool_callback:
            try:
                data = self.unusual_whales.get_dark_pool_recent()
                self.dark_pool_data = data
                self.dark_pool_callback(data)
            except Exception as e:
                logger.error(f"Error fetching dark pool data: {e}")
    
    def _fetch_news_periodically(self, interval: int = 1800):
        """Fetch news data periodically."""
        if self.news_api and self.news_callback:
            try:
                data = self.news_api.get_market_news(self.config["trading"]["symbols"])
                self.news_data = data
                self.news_callback(data)
            except Exception as e:
                logger.error(f"Error fetching news data: {e}")
    
    def _handle_market_data(self, data: Dict):
        """Handle incoming market data from WebSocket."""
        try:
            symbol = data.get("sym")
            if symbol:
                if symbol not in self.market_data:
                    self.market_data[symbol] = []
                self.market_data[symbol].append(data)
                
                # Keep only the last 1000 data points
                if len(self.market_data[symbol]) > 1000:
                    self.market_data[symbol] = self.market_data[symbol][-1000:]
                
                # Call callback if set
                if self.market_data_callback:
                    self.market_data_callback(symbol, data)
        except Exception as e:
            logger.error(f"Error handling market data: {e}")
    
    def set_market_data_callback(self, callback: Callable):
        """Set callback for market data updates."""
        self.market_data_callback = callback
    
    def set_options_flow_callback(self, callback: Callable):
        """Set callback for options flow updates."""
        self.options_flow_callback = callback
    
    def set_dark_pool_callback(self, callback: Callable):
        """Set callback for dark pool updates."""
        self.dark_pool_callback = callback
    
    def set_news_callback(self, callback: Callable):
        """Set callback for news updates."""
        self.news_callback = callback
    
    def get_market_data(self, symbol: str) -> List[Dict]:
        """Get stored market data for a symbol."""
        return self.market_data.get(symbol, [])
    
    def get_options_flow(self) -> List[Dict]:
        """Get stored options flow data."""
        return self.options_flow
    
    def get_dark_pool_data(self) -> List[Dict]:
        """Get stored dark pool data."""
        return self.dark_pool_data
    
    def get_news_data(self) -> List[Dict]:
        """Get stored news data."""
        return self.news_data 