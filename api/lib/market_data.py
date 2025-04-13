"""
Market Data API Integration Module

This module provides integration with various market data sources:
1. Unusual Whales API for dark pool and options flow data
2. TradingView Webhooks for real-time market alerts
3. Interactive Brokers API for live market data
4. Alpaca API for real-time stock and options pricing
"""

import os
import json
import logging
import requests
from typing import Dict, List, Union, Optional
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketDataSourceManager:
    """
    Manager class for handling different market data sources.
    Provides a unified interface for switching between different data providers.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the market data manager with a configuration dictionary.
        
        Args:
            config: Dictionary containing API keys and preferences
        """
        self.config = config
        self.active_source = config.get('active_source', 'alpaca')
        self.sources = {}
        
        # Initialize the data sources
        if 'alpaca' in config:
            self.sources['alpaca'] = AlpacaAPI(
                api_key=config['alpaca'].get('api_key'),
                api_secret=config['alpaca'].get('api_secret'),
                base_url=config['alpaca'].get('base_url', 'https://paper-api.alpaca.markets')
            )
            
        if 'interactive_brokers' in config:
            self.sources['interactive_brokers'] = InteractiveBrokersAPI(
                port=config['interactive_brokers'].get('port', 7496),
                client_id=config['interactive_brokers'].get('client_id', 0)
            )
            
        if 'unusual_whales' in config:
            self.sources['unusual_whales'] = UnusualWhalesAPI(
                token=config['unusual_whales'].get('token')
            )
            
        if 'tradingview' in config:
            self.sources['tradingview'] = TradingViewWebhooks(
                webhook_port=config['tradingview'].get('webhook_port', 5001)
            )
            
    def set_active_source(self, source_name: str) -> bool:
        """
        Set the active data source.
        
        Args:
            source_name: Name of the source to activate
            
        Returns:
            bool: True if successful, False otherwise
        """
        if source_name in self.sources:
            self.active_source = source_name
            logger.info(f"Active market data source set to: {source_name}")
            return True
        else:
            logger.error(f"Data source {source_name} not available")
            return False
    
    def get_active_source(self):
        """
        Get the currently active data source object.
        
        Returns:
            The active data source object
        """
        return self.sources.get(self.active_source)
    
    def get_market_data(self, symbols: List[str], **kwargs):
        """
        Get market data from the active source.
        
        Args:
            symbols: List of symbols to get data for
            kwargs: Additional parameters to pass to the source
            
        Returns:
            Market data from the active source
        """
        source = self.get_active_source()
        if source:
            return source.get_market_data(symbols, **kwargs)
        else:
            logger.error(f"No active data source available")
            return None


class AlpacaAPI:
    """
    Integration with Alpaca API for stock and options data.
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None, 
                 base_url: str = 'https://paper-api.alpaca.markets'):
        """
        Initialize the Alpaca API connection.
        
        Args:
            api_key: Alpaca API key
            api_secret: Alpaca API secret
            base_url: Base URL for the API
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()
        
        if api_key and api_secret:
            self.session.headers.update({
                'APCA-API-KEY-ID': api_key,
                'APCA-API-SECRET-KEY': api_secret,
                'Content-Type': 'application/json'
            })
            logger.info("AlpacaAPI initialized with credentials")
        else:
            logger.warning("AlpacaAPI initialized without credentials")
    
    def get_market_data(self, symbols: List[str], data_type: str = 'bars', 
                        timeframe: str = '1Min', limit: int = 100) -> Dict:
        """
        Get market data from Alpaca.
        
        Args:
            symbols: List of symbols to get data for
            data_type: Type of data to get (bars, quotes, trades)
            timeframe: Timeframe for bars
            limit: Number of bars to get
            
        Returns:
            Dict: JSON response from Alpaca
        """
        if not self.api_key or not self.api_secret:
            logger.error("Alpaca API credentials not provided")
            return {"error": "API credentials not provided"}
        
        endpoint = ""
        if data_type == 'bars':
            endpoint = f"{self.base_url}/v2/stocks/bars"
            params = {
                'symbols': ','.join(symbols),
                'timeframe': timeframe,
                'limit': limit
            }
        elif data_type == 'quotes':
            endpoint = f"{self.base_url}/v2/stocks/quotes/latest"
            params = {
                'symbols': ','.join(symbols)
            }
        elif data_type == 'trades':
            endpoint = f"{self.base_url}/v2/stocks/trades/latest"
            params = {
                'symbols': ','.join(symbols)
            }
        else:
            return {"error": f"Unsupported data type: {data_type}"}
            
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Alpaca: {e}")
            return {"error": str(e)}


class InteractiveBrokersAPI:
    """
    Integration with Interactive Brokers API for stock and options data.
    Note: This requires the IB TWS or Gateway application to be running.
    """
    
    def __init__(self, port: int = 7496, client_id: int = 0):
        """
        Initialize the Interactive Brokers API connection.
        
        Args:
            port: Port number for the TWS/Gateway connection
            client_id: Client ID for the TWS/Gateway connection
        """
        self.port = port
        self.client_id = client_id
        self.connected = False
        
        # This will be initialized when connect() is called
        self.ib_client = None
        
        logger.info(f"InteractiveBrokersAPI initialized (port: {port}, client_id: {client_id})")
        
    def connect(self) -> bool:
        """
        Connect to the Interactive Brokers TWS/Gateway application.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Dynamically import the IB API to avoid requiring it for all users
            # Users who don't use IB don't need to install the IB API package
            from ibapi.client import EClient
            from ibapi.wrapper import EWrapper
            
            class IBWrapper(EWrapper, EClient):
                def __init__(self):
                    EClient.__init__(self, self)
                    self.data = {}
                    
                def error(self, reqId, errorCode, errorString):
                    logger.error(f"IB Error {errorCode}: {errorString}")
                    
                def historicalData(self, reqId, bar):
                    if reqId not in self.data:
                        self.data[reqId] = []
                    self.data[reqId].append({
                        'time': bar.date,
                        'open': bar.open,
                        'high': bar.high,
                        'low': bar.low,
                        'close': bar.close,
                        'volume': bar.volume
                    })
            
            self.ib_client = IBWrapper()
            self.ib_client.connect('127.0.0.1', self.port, self.client_id)
            
            # Start the client thread
            import threading
            api_thread = threading.Thread(target=self.ib_client.run)
            api_thread.start()
            
            self.connected = True
            logger.info("Connected to Interactive Brokers")
            return True
            
        except ImportError:
            logger.error("ibapi package not found. Cannot connect to Interactive Brokers.")
            return False
        except Exception as e:
            logger.error(f"Error connecting to Interactive Brokers: {e}")
            return False
    
    def disconnect(self):
        """
        Disconnect from the Interactive Brokers TWS/Gateway application.
        """
        if self.ib_client and self.connected:
            self.ib_client.disconnect()
            self.connected = False
            logger.info("Disconnected from Interactive Brokers")
    
    def get_market_data(self, symbols: List[str], data_type: str = 'bars',
                       bar_size: str = '1 min', duration: str = '1 D') -> Dict:
        """
        Get market data from Interactive Brokers.
        
        Args:
            symbols: List of symbols to get data for
            data_type: Type of data to get (bars, quotes, trades)
            bar_size: Bar size for historical data
            duration: Duration for historical data
            
        Returns:
            Dict: Market data
        """
        if not self.connected:
            success = self.connect()
            if not success:
                return {"error": "Could not connect to Interactive Brokers"}
        
        # Implementation depends on the specific TWS API methods required
        # This is a placeholder for the actual implementation
        logger.info(f"Getting {data_type} data for {symbols} from Interactive Brokers")
        return {"message": "Interactive Brokers API integration requires TWS/Gateway running"}


class UnusualWhalesAPI:
    """
    Integration with Unusual Whales API for dark pool and options flow data.
    """
    
    def __init__(self, token: str = None):
        """
        Initialize the Unusual Whales API connection.
        
        Args:
            token: Unusual Whales API token
        """
        self.token = token
        self.base_url = "https://api.unusualwhales.com"
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({
                'Authorization': f"Bearer {token}",
                'Content-Type': 'application/json'
            })
            logger.info("UnusualWhalesAPI initialized with token")
        else:
            logger.warning("UnusualWhalesAPI initialized without token")
    
    def get_options_flow(self, symbols: Optional[List[str]] = None, 
                         limit: int = 100, 
                         side: Optional[str] = None,
                         option_type: Optional[str] = None) -> Dict:
        """
        Get options flow data from Unusual Whales.
        
        Args:
            symbols: Optional list of symbols to filter by
            limit: Maximum number of results to return (default 100)
            side: Filter by side ('BUY' or 'SELL')
            option_type: Filter by option type ('CALL' or 'PUT')
            
        Returns:
            Dict: JSON response with options flow data
        """
        if not self.token:
            logger.error("Unusual Whales API token not provided")
            return {"error": "API token not provided"}
        
        endpoint = f"{self.base_url}/api/options/flow/recent"
        params = {'limit': limit}
        
        if symbols:
            params['symbols'] = ','.join(symbols)
        
        if side:
            params['side'] = side
            
        if option_type:
            params['type'] = option_type
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Unusual Whales: {e}")
            return {"error": str(e)}
    
    def get_dark_pool_data(self, symbols: Optional[List[str]] = None, 
                           limit: int = 100,
                           date: Optional[str] = None) -> Dict:
        """
        Get recent dark pool data from Unusual Whales.
        
        Args:
            symbols: Optional list of symbols to filter by
            limit: Maximum number of results to return (default 100)
            date: Optional specific date in YYYY-MM-DD format
            
        Returns:
            Dict: JSON response with dark pool data
        """
        if not self.token:
            logger.error("Unusual Whales API token not provided")
            return {"error": "API token not provided"}
        
        endpoint = f"{self.base_url}/api/darkpool/recent"
        params = {'limit': limit}
        
        if symbols:
            params['symbols'] = ','.join(symbols)
            
        if date:
            params['date'] = date
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching dark pool data from Unusual Whales: {e}")
            return {"error": str(e)}
    
    def get_dark_pool_by_ticker(self, symbol: str, 
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> Dict:
        """
        Get dark pool data for a specific ticker from Unusual Whales.
        
        Args:
            symbol: Symbol to get data for (required)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict: JSON response with dark pool data for the ticker
        """
        if not self.token:
            logger.error("Unusual Whales API token not provided")
            return {"error": "API token not provided"}
            
        if not symbol:
            logger.error("Symbol is required for get_dark_pool_by_ticker")
            return {"error": "Symbol is required"}
        
        endpoint = f"{self.base_url}/api/darkpool/ticker/{symbol.upper()}"
        params = {}
        
        if start_date:
            params['startDate'] = start_date
            
        if end_date:
            params['endDate'] = end_date
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ticker dark pool data from Unusual Whales: {e}")
            return {"error": str(e)}
            
    def get_dark_pool_aggregate(self, symbols: Optional[List[str]] = None,
                               limit: int = 100,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> Dict:
        """
        Get aggregated dark pool data from Unusual Whales.
        
        Args:
            symbols: Optional list of symbols to filter by
            limit: Maximum number of results to return (default 100)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict: JSON response with aggregated dark pool data
        """
        if not self.token:
            logger.error("Unusual Whales API token not provided")
            return {"error": "API token not provided"}
        
        endpoint = f"{self.base_url}/api/darkpool/aggregate"
        params = {'limit': limit}
        
        if symbols:
            params['symbols'] = ','.join(symbols)
            
        if start_date:
            params['startDate'] = start_date
            
        if end_date:
            params['endDate'] = end_date
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching aggregated dark pool data from Unusual Whales: {e}")
            return {"error": str(e)}
    
    def get_market_data(self, symbols: List[str], data_type: str = 'dark_pool', **kwargs) -> Dict:
        """
        General method to get market data from Unusual Whales.
        
        Args:
            symbols: List of symbols to get data for
            data_type: Type of data to get (dark_pool, options_flow, dark_pool_ticker, dark_pool_aggregate)
            **kwargs: Additional parameters to pass to the specific data request
            
        Returns:
            Dict: JSON response with requested data
        """
        if data_type == 'dark_pool':
            return self.get_dark_pool_data(symbols, **kwargs)
        elif data_type == 'options_flow':
            return self.get_options_flow(symbols, **kwargs)
        elif data_type == 'dark_pool_ticker' and len(symbols) > 0:
            return self.get_dark_pool_by_ticker(symbols[0], **kwargs)
        elif data_type == 'dark_pool_aggregate':
            return self.get_dark_pool_aggregate(symbols, **kwargs)
        else:
            return {"error": f"Unsupported data type: {data_type}"}


class TradingViewWebhooks:
    """
    Integration with TradingView Webhooks for receiving alerts.
    This requires a server that can receive webhook requests from TradingView.
    """
    
    def __init__(self, webhook_port: int = 5001, webhook_path: str = '/tradingview-webhook'):
        """
        Initialize the TradingView Webhooks integration.
        
        Args:
            webhook_port: Port to listen on for webhooks
            webhook_path: URL path for webhook endpoints
        """
        self.webhook_port = webhook_port
        self.webhook_path = webhook_path
        self.server_running = False
        self.alerts = []
        
        logger.info(f"TradingViewWebhooks initialized (port: {webhook_port}, path: {webhook_path})")
    
    def start_webhook_server(self):
        """
        Start a webhook server to receive TradingView alerts.
        This runs in a separate thread.
        """
        if self.server_running:
            logger.warning("Webhook server is already running")
            return
        
        try:
            from flask import Flask, request
            import threading
            
            app = Flask(__name__)
            
            @app.route(self.webhook_path, methods=['POST'])
            def webhook():
                try:
                    alert_data = request.json
                    self.alerts.append({
                        'timestamp': datetime.now().isoformat(),
                        'data': alert_data
                    })
                    logger.info(f"Received TradingView alert: {alert_data}")
                    return json.dumps({"success": True}), 200
                except Exception as e:
                    logger.error(f"Error processing webhook: {e}")
                    return json.dumps({"success": False, "error": str(e)}), 400
            
            def run_server():
                app.run(host='0.0.0.0', port=self.webhook_port)
            
            server_thread = threading.Thread(target=run_server)
            server_thread.daemon = True
            server_thread.start()
            
            self.server_running = True
            logger.info(f"Webhook server started on port {self.webhook_port}")
        
        except ImportError:
            logger.error("Flask not installed. Cannot start webhook server.")
        except Exception as e:
            logger.error(f"Error starting webhook server: {e}")
    
    def get_alerts(self, max_count: int = 100):
        """
        Get the most recent TradingView alerts.
        
        Args:
            max_count: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return self.alerts[-max_count:] if self.alerts else []
    
    def clear_alerts(self):
        """
        Clear all stored alerts.
        """
        self.alerts = []
        logger.info("TradingView alerts cleared")
    
    def get_market_data(self, symbols: List[str], **kwargs):
        """
        TradingView Webhooks don't directly provide market data, so this
        returns the most recent alerts filtered by the requested symbols.
        
        Args:
            symbols: List of symbols to filter alerts by
            
        Returns:
            List of filtered alerts
        """
        if not self.server_running:
            self.start_webhook_server()
            
        # Filter alerts by the requested symbols if possible
        filtered_alerts = []
        for alert in self.alerts:
            data = alert.get('data', {})
            alert_symbol = data.get('symbol')
            
            if alert_symbol and alert_symbol in symbols:
                filtered_alerts.append(alert)
        
        return filtered_alerts 