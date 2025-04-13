import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class MarketDataService:
    """
    Service for fetching and managing market data
    """
    
    def __init__(self):
        """Initialize market data service"""
        self.data_cache = {}
        self.last_updated = {}
        self.cache_duration = timedelta(minutes=15)  # Cache data for 15 minutes
        
    def get_symbol_data(self, symbol, days=30):
        """
        Get market data for a specific symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days of data to retrieve
            
        Returns:
            DataFrame: Market data for the symbol
        """
        # Check cache first
        current_time = datetime.now()
        if symbol in self.data_cache and symbol in self.last_updated:
            if current_time - self.last_updated[symbol] < self.cache_duration:
                logger.info(f"Using cached data for {symbol}")
                return self.data_cache[symbol]
        
        try:
            # In a real implementation, this would call an API or database
            # For now, using mock data
            df = self._generate_mock_data(symbol, days)
            
            # Cache the data
            self.data_cache[symbol] = df
            self.last_updated[symbol] = current_time
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
            
    def get_multi_symbol_data(self, symbols, days=30):
        """
        Get market data for multiple symbols
        
        Args:
            symbols: List of stock symbols
            days: Number of days of data to retrieve
            
        Returns:
            dict: Market data for each symbol
        """
        result = {}
        for symbol in symbols:
            result[symbol] = self.get_symbol_data(symbol, days)
            
        return result
        
    def _generate_mock_data(self, symbol, days):
        """
        Generate mock market data for a symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days of data
            
        Returns:
            DataFrame: Generated market data
        """
        # Set random seed based on symbol to get consistent data for the same symbol
        random.seed(hash(symbol) % 10000)
        np.random.seed(hash(symbol) % 10000)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Generate dates
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Filter for trading days (Mon-Fri)
        dates = dates[dates.dayofweek < 5]
        
        # Base price and daily change
        base_price = 50 + random.random() * 200  # Random base price between 50 and 250
        
        # Generate price data
        data = []
        current_price = base_price
        
        for date in dates:
            # Daily change percentage - slightly biased upward for a realistic market
            daily_change = np.random.normal(0.0005, 0.015)  # Mean slightly positive with volatility
            
            # Apply change
            current_price *= (1 + daily_change)
            
            # Daily high/low/open calculation
            daily_range = current_price * (0.005 + 0.03 * random.random())  # 0.5% to 3.5% daily range
            high = current_price + random.random() * daily_range / 2
            low = current_price - random.random() * daily_range / 2
            
            # Sometimes low goes below previous day, sometimes high is new high
            if random.random() > 0.5:
                low = current_price - daily_range
            else:
                high = current_price + daily_range
                
            # Ensure high >= close >= low
            high = max(high, current_price)
            low = min(low, current_price)
            
            # Generate open within previous day's range
            if data:
                prev_close = data[-1]['close']
                open_price = prev_close * (1 + np.random.normal(0, 0.007))  # Open near previous close
            else:
                open_price = current_price * (1 + np.random.normal(0, 0.007))  # First day open
                
            # Generate volume
            volume = int(np.random.gamma(shape=2.0, scale=1000000) * (1 + abs(daily_change) * 10))
            
            # Add noise to pricing for more realistic relationships
            high = max(high, open_price, current_price)
            low = min(low, open_price, current_price)
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'symbol': symbol,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(current_price, 2),
                'volume': volume
            })
            
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Add some technical indicators
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        df['atr'] = self._calculate_atr(df, 14)
        
        return df
        
    def _calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        
        # Make two series: one for gains and one for losses
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        
        # Calculate the EWMA (Exponential Weighted Moving Average)
        roll_up = up.ewm(span=period).mean()
        roll_down = down.ewm(span=period).mean()
        
        # Calculate the RSI based on EWMA
        rs = roll_up / roll_down
        rsi = 100.0 - (100.0 / (1.0 + rs))
        
        return rsi
        
    def _calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR using Simple Moving Average
        atr = tr.rolling(window=period).mean()
        
        return atr 