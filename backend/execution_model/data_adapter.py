"""
Execution Model Data Adapter Module

This module adapts market data from the sources implemented in Stage 1
to the format expected by the execution model components.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ExecutionModelDataAdapter:
    """
    Adapts market data from various sources to the execution model
    
    This class serves as a bridge between the market data sources implemented
    in Stage 1 and the execution model components, ensuring consistent data format.
    """
    
    def __init__(self, market_data_manager=None):
        """
        Initialize with optional market data manager
        
        Args:
            market_data_manager: MarketDataSourceManager instance from Stage 1
        """
        self.market_data_manager = market_data_manager
        
    def set_market_data_manager(self, market_data_manager):
        """
        Set the market data manager
        
        Args:
            market_data_manager: MarketDataSourceManager instance
        """
        self.market_data_manager = market_data_manager
        
    def get_market_data_for_execution(self, symbols, data_types=None, timeframe="1d", limit=100):
        """
        Get market data formatted for the execution model
        
        Args:
            symbols: List of symbols to fetch data for
            data_types: Optional list of data types to fetch ('bars', 'quotes', 'trades')
            timeframe: Timeframe for bar data (e.g. '1d', '1h', '15m')
            limit: Maximum number of data points to fetch
            
        Returns:
            dict: Dictionary with market data for each symbol
                Format: {'SYMBOL': DataFrame with OHLCV data, ...}
        """
        if self.market_data_manager is None:
            logger.warning("Market data manager not set")
            return {}
            
        # Default to bars if no data types specified
        if data_types is None:
            data_types = ["bars"]
            
        result = {}
        
        for symbol in symbols:
            try:
                # Fetch raw data from the market data manager
                raw_data = self._fetch_raw_data(symbol, data_types, timeframe, limit)
                
                # Format the data for the execution model
                formatted_data = self._format_for_execution_model(raw_data, symbol)
                
                if formatted_data is not None and len(formatted_data) > 0:
                    result[symbol] = formatted_data
                    logger.debug(f"Got {len(formatted_data)} data points for {symbol}")
                else:
                    logger.warning(f"No data available for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error getting market data for {symbol}: {str(e)}")
                continue
                
        return result
    
    def get_account_info(self):
        """
        Get account information from the market data manager
        
        Returns:
            dict: Account information, or default account info if not available
        """
        if self.market_data_manager is None:
            logger.warning("Market data manager not set, returning default account info")
            return self._get_default_account_info()
            
        try:
            # Try to get account info from the market data manager
            # This assumes that the market data manager has a get_account_info method
            # If not, we'll catch the exception and return default account info
            if hasattr(self.market_data_manager, 'get_account_info'):
                account_info = self.market_data_manager.get_account_info()
                return account_info
            else:
                logger.warning("Market data manager does not have get_account_info method")
                return self._get_default_account_info()
                
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return self._get_default_account_info()
    
    def get_institutional_flow_data(self, symbols=None, days_back=7):
        """
        Get institutional flow data from the market data manager
        
        Args:
            symbols: Optional list of symbols to filter by
            days_back: Number of days of historical data to fetch
            
        Returns:
            dict: Institutional flow data, or empty dict if not available
        """
        if self.market_data_manager is None:
            logger.warning("Market data manager not set")
            return {'options_flow': [], 'dark_pool': []}
            
        try:
            # Try to get unusual options flow and dark pool data
            flow_data = {'options_flow': [], 'dark_pool': []}
            
            # Check if we have access to Unusual Whales API
            if hasattr(self.market_data_manager, 'get_unusual_options_flow'):
                # Get unusual options flow data
                since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
                options_flow = self.market_data_manager.get_unusual_options_flow(since_date=since_date)
                
                # Filter by symbols if provided
                if symbols is not None:
                    options_flow = [flow for flow in options_flow if flow.get('symbol') in symbols]
                    
                flow_data['options_flow'] = options_flow
                logger.debug(f"Got {len(options_flow)} unusual options flow entries")
            
            # Check if we have access to dark pool data
            if hasattr(self.market_data_manager, 'get_dark_pool_data'):
                # Get dark pool data
                since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
                dark_pool = self.market_data_manager.get_dark_pool_data(since_date=since_date)
                
                # Filter by symbols if provided
                if symbols is not None:
                    dark_pool = [dp for dp in dark_pool if dp.get('symbol') in symbols]
                    
                flow_data['dark_pool'] = dark_pool
                logger.debug(f"Got {len(dark_pool)} dark pool entries")
            
            return flow_data
            
        except Exception as e:
            logger.error(f"Error getting institutional flow data: {str(e)}")
            return {'options_flow': [], 'dark_pool': []}
    
    def _fetch_raw_data(self, symbol, data_types, timeframe, limit):
        """
        Fetch raw data from the market data manager
        
        Args:
            symbol: Symbol to fetch data for
            data_types: List of data types to fetch
            timeframe: Timeframe for bar data
            limit: Maximum number of data points
            
        Returns:
            dict: Raw data from the market data manager
        """
        raw_data = {}
        
        for data_type in data_types:
            try:
                if data_type == "bars":
                    # Get bar data
                    data = self.market_data_manager.get_bars(
                        symbol, timeframe=timeframe, limit=limit
                    )
                    raw_data["bars"] = data
                    
                elif data_type == "quotes":
                    # Get quote data
                    data = self.market_data_manager.get_quotes(
                        symbol, limit=min(limit, 100)  # Usually need fewer quotes
                    )
                    raw_data["quotes"] = data
                    
                elif data_type == "trades":
                    # Get trade data
                    data = self.market_data_manager.get_trades(
                        symbol, limit=min(limit, 100)  # Usually need fewer trades
                    )
                    raw_data["trades"] = data
                    
            except Exception as e:
                logger.error(f"Error fetching {data_type} data for {symbol}: {str(e)}")
                continue
                
        return raw_data
    
    def _format_for_execution_model(self, raw_data, symbol):
        """
        Format raw data for the execution model
        
        Args:
            raw_data: Raw data from the market data manager
            symbol: Symbol the data is for
            
        Returns:
            DataFrame: Formatted data for the execution model
        """
        # Start with bar data if available
        if "bars" in raw_data and raw_data["bars"] is not None:
            # Convert to DataFrame if it's not already
            if isinstance(raw_data["bars"], dict):
                bars_df = pd.DataFrame([raw_data["bars"]])
            elif isinstance(raw_data["bars"], list):
                bars_df = pd.DataFrame(raw_data["bars"])
            else:
                bars_df = raw_data["bars"]
                
            # Ensure we have the required columns
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            # Check if we need to rename any columns
            if not all(col in bars_df.columns for col in required_columns):
                # Try some common column mappings
                column_mappings = {
                    't': 'timestamp',
                    'time': 'timestamp',
                    'o': 'open',
                    'h': 'high',
                    'l': 'low',
                    'c': 'close',
                    'v': 'volume'
                }
                
                # Rename columns if needed
                for old_col, new_col in column_mappings.items():
                    if old_col in bars_df.columns and new_col not in bars_df.columns:
                        bars_df = bars_df.rename(columns={old_col: new_col})
            
            # Check if we still have all required columns
            if not all(col in bars_df.columns for col in required_columns):
                logger.warning(f"Missing required columns for {symbol}")
                return None
                
            # Sort by timestamp
            if 'timestamp' in bars_df.columns:
                # Convert timestamp to datetime if it's not already
                if not pd.api.types.is_datetime64_any_dtype(bars_df['timestamp']):
                    try:
                        bars_df['timestamp'] = pd.to_datetime(bars_df['timestamp'])
                    except:
                        # If conversion fails, create a dummy timestamp
                        logger.warning(f"Could not convert timestamp for {symbol}, creating dummy timestamps")
                        bars_df['timestamp'] = pd.date_range(
                            start=datetime.now() - timedelta(days=len(bars_df)), 
                            periods=len(bars_df), 
                            freq='D'
                        )
                        
                bars_df = bars_df.sort_values('timestamp')
                
            # Set the bar data as the base DataFrame
            result_df = bars_df
            
            # Add quote data if available
            if "quotes" in raw_data and raw_data["quotes"] is not None:
                # Convert to DataFrame if needed
                if isinstance(raw_data["quotes"], dict):
                    quotes_df = pd.DataFrame([raw_data["quotes"]])
                elif isinstance(raw_data["quotes"], list):
                    quotes_df = pd.DataFrame(raw_data["quotes"])
                else:
                    quotes_df = raw_data["quotes"]
                    
                # Extract bid/ask from latest quote
                if not quotes_df.empty:
                    latest_quote = quotes_df.iloc[-1]
                    result_df['bid'] = latest_quote.get('bid_price', latest_quote.get('bid', 0))
                    result_df['ask'] = latest_quote.get('ask_price', latest_quote.get('ask', 0))
                    result_df['bid_size'] = latest_quote.get('bid_size', 0)
                    result_df['ask_size'] = latest_quote.get('ask_size', 0)
            
            return result_df
            
        # If no bar data but we have quotes, construct a simple DataFrame
        elif "quotes" in raw_data and raw_data["quotes"] is not None:
            # Convert to DataFrame
            if isinstance(raw_data["quotes"], dict):
                quotes_df = pd.DataFrame([raw_data["quotes"]])
            elif isinstance(raw_data["quotes"], list):
                quotes_df = pd.DataFrame(raw_data["quotes"])
            else:
                quotes_df = raw_data["quotes"]
                
            # Create a simple DataFrame with required columns
            result_df = pd.DataFrame()
            result_df['timestamp'] = quotes_df.get('timestamp', pd.date_range(
                start=datetime.now() - timedelta(minutes=len(quotes_df)), 
                periods=len(quotes_df), 
                freq='T'
            ))
            
            # Use midpoint as OHLC prices
            bid = quotes_df.get('bid_price', quotes_df.get('bid', 0))
            ask = quotes_df.get('ask_price', quotes_df.get('ask', 0))
            midpoint = (bid + ask) / 2 if bid is not None and ask is not None else 0
            
            result_df['open'] = midpoint
            result_df['high'] = midpoint
            result_df['low'] = midpoint
            result_df['close'] = midpoint
            result_df['volume'] = 0
            result_df['bid'] = bid
            result_df['ask'] = ask
            
            return result_df
            
        # If no useful data available
        logger.warning(f"No useful data available for {symbol}")
        return None
    
    def _get_default_account_info(self):
        """
        Get default account information
        
        Returns:
            dict: Default account information
        """
        return {
            'balance': 100000.0,  # $100,000 default balance
            'buying_power': 200000.0,  # $200,000 default buying power (2x margin)
            'equity': 100000.0,
            'currency': 'USD',
            'is_dummy_account': True
        } 