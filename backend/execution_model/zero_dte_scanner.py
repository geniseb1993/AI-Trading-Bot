"""
Zero DTE Scanner Module

This module is designed to scan for high-probability 0DTE (Zero Days to Expiration) options trades,
specifically focusing on SPX and QQQ for scalping and momentum strategies.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import time

logger = logging.getLogger(__name__)

class ZeroDTEScanner:
    """
    Scanner for identifying high-probability 0DTE options trades on SPX and QQQ
    """
    
    def __init__(self, config=None):
        """
        Initialize the 0DTE Scanner
        
        Args:
            config: Configuration dictionary with parameters
        """
        self.config = config or {}
        
        # Default configuration
        self.symbols = self.config.get('symbols', ['SPX', 'QQQ', 'TSLA', 'PLTR'])
        self.time_window = self.config.get('time_window', 15)  # Minutes
        self.volume_threshold = self.config.get('volume_threshold', 100)
        self.momentum_threshold = self.config.get('momentum_threshold', 0.3)  # %
        self.max_recommendations = self.config.get('max_recommendations', 3)
        self.data_source = self.config.get('data_source', 'alpaca')
        
        # Internal state
        self.recommendations = []
        self.last_scan_time = None
        
        logger.info(f"0DTE Scanner initialized for symbols: {', '.join(self.symbols)}")
        
    def update_config(self, config):
        """
        Update scanner configuration
        
        Args:
            config: New configuration dictionary
        """
        self.config.update(config)
        self.symbols = self.config.get('symbols', ['SPX', 'QQQ', 'TSLA', 'PLTR'])
        self.time_window = self.config.get('time_window', 15)
        self.volume_threshold = self.config.get('volume_threshold', 100)
        self.momentum_threshold = self.config.get('momentum_threshold', 0.3)
        self.max_recommendations = self.config.get('max_recommendations', 3)
        self.data_source = self.config.get('data_source', 'alpaca')
        
        logger.info("0DTE Scanner configuration updated")
    
    def scan_for_opportunities(self, market_data):
        """
        Scan for 0DTE trading opportunities
        
        Args:
            market_data: Dictionary of market data by symbol
            
        Returns:
            List of trade recommendations
        """
        self.last_scan_time = datetime.now()
        self.recommendations = []
        
        logger.info("Scanning for 0DTE opportunities...")
        
        for symbol in self.symbols:
            if symbol not in market_data:
                logger.warning(f"No market data available for {symbol}")
                continue
                
            symbol_data = market_data[symbol]
            
            # Convert to DataFrame if necessary
            if not isinstance(symbol_data, pd.DataFrame):
                try:
                    symbol_data = pd.DataFrame(symbol_data)
                except:
                    logger.error(f"Could not convert {symbol} data to DataFrame")
                    continue
            
            # Check if we have enough data
            if len(symbol_data) < 30:  # Need at least 30 data points
                logger.warning(f"Insufficient data for {symbol}: {len(symbol_data)} points")
                continue
                
            # Calculate technical indicators
            symbol_data = self._calculate_indicators(symbol_data)
            
            # Find setups
            setups = self._identify_setups(symbol, symbol_data)
            
            # Add valid setups to recommendations
            for setup in setups:
                self.recommendations.append(setup)
        
        # Sort by confidence and limit to max recommendations
        self.recommendations = sorted(
            self.recommendations, 
            key=lambda x: x['confidence'], 
            reverse=True
        )[:self.max_recommendations]
        
        logger.info(f"Found {len(self.recommendations)} 0DTE opportunities")
        
        return self.recommendations
    
    def _calculate_indicators(self, df):
        """
        Calculate technical indicators for analysis
        
        Args:
            df: DataFrame with market data
            
        Returns:
            DataFrame with indicators added
        """
        # Ensure required columns exist
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                logger.warning(f"Missing required column: {col}")
                # Create dummy column if missing
                df[col] = 0
        
        # Calculate short-term moving averages for momentum
        df['ema5'] = df['close'].ewm(span=5, adjust=False).mean()
        df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
        
        # Calculate volume-based indicators
        df['volume_sma10'] = df['volume'].rolling(window=10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma10']
        
        # Calculate momentum indicators
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        df['momentum'] = (df['close'] / df['close'].shift(5) - 1) * 100  # 5-period momentum
        
        # Calculate volatility indicators
        df['atr'] = self._calculate_atr(df, 14)
        
        # Calculate trend indicators
        df['trend_strength'] = self._calculate_trend_strength(df)
        
        return df

    def _calculate_rsi(self, prices, period=14):
        """
        Calculate Relative Strength Index
        
        Args:
            prices: Series of prices
            period: RSI period
            
        Returns:
            Series with RSI values
        """
        deltas = prices.diff()
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        rs = up/down if down != 0 else 0
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100./(1. + rs)
        
        for i in range(period, len(prices)):
            delta = deltas[i]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
                
            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up/down if down != 0 else 0
            rsi[i] = 100. - 100./(1. + rs)
            
        return pd.Series(rsi, index=prices.index)
    
    def _calculate_atr(self, df, period=14):
        """
        Calculate Average True Range
        
        Args:
            df: DataFrame with OHLC data
            period: ATR period
            
        Returns:
            Series with ATR values
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True range calculation
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        
        return atr
    
    def _calculate_trend_strength(self, df):
        """
        Calculate a trend strength indicator
        
        Args:
            df: DataFrame with indicators
            
        Returns:
            Series with trend strength values
        """
        # Calculate linear regression slope over 20 periods
        y = df['close'].values
        x = np.arange(len(y))
        
        slope = np.zeros_like(y)
        
        for i in range(20, len(y)):
            x_slice = x[i-20:i]
            y_slice = y[i-20:i]
            slope[i] = np.polyfit(x_slice, y_slice, 1)[0]
        
        # Normalize slope values between -1 and 1
        max_slope = max(abs(np.nanmax(slope)), abs(np.nanmin(slope)))
        if max_slope > 0:
            normalized_slope = slope / max_slope
        else:
            normalized_slope = slope
            
        return pd.Series(normalized_slope, index=df.index)
    
    def _identify_setups(self, symbol, df):
        """
        Identify trading setups based on technical indicators
        
        Args:
            symbol: Trading symbol
            df: DataFrame with indicators
            
        Returns:
            List of trade setups
        """
        setups = []
        
        # Get the most recent data
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Define setup conditions
        
        # Bullish setup
        bullish_conditions = [
            latest['close'] > latest['ema9'],
            latest['ema9'] > latest['ema20'],
            latest['volume_ratio'] > 1.2,
            latest['momentum'] > self.momentum_threshold,
            latest['close'] > prev['close'],
            latest['rsi'] > 50,
            latest['trend_strength'] > 0.3
        ]
        
        # Bearish setup
        bearish_conditions = [
            latest['close'] < latest['ema9'],
            latest['ema9'] < latest['ema20'],
            latest['volume_ratio'] > 1.2,
            latest['momentum'] < -self.momentum_threshold,
            latest['close'] < prev['close'],
            latest['rsi'] < 50,
            latest['trend_strength'] < -0.3
        ]
        
        # Determine setup type
        bullish_score = sum(bullish_conditions) / len(bullish_conditions)
        bearish_score = sum(bearish_conditions) / len(bearish_conditions)
        
        # Calculate confidence based on the number of conditions met
        if bullish_score > 0.6 and bullish_score > bearish_score:
            # Bullish setup
            confidence = bullish_score
            setup_type = "CALL"
            
            # Create setup dictionary
            setup = {
                'symbol': symbol,
                'type': setup_type,
                'price': latest['close'],
                'timestamp': datetime.now().isoformat(),
                'confidence': confidence,
                'expiration': '0DTE',  # Zero days to expiration
                'strike': self._calculate_strike_price(symbol, latest['close'], setup_type),
                'indicators': {
                    'rsi': latest['rsi'],
                    'momentum': latest['momentum'],
                    'volume_ratio': latest['volume_ratio'],
                    'trend_strength': latest['trend_strength']
                },
                'recommendation': f"BUY {symbol} {setup_type} @ {self._calculate_strike_price(symbol, latest['close'], setup_type)}"
            }
            
            setups.append(setup)
            
        elif bearish_score > 0.6 and bearish_score > bullish_score:
            # Bearish setup
            confidence = bearish_score
            setup_type = "PUT"
            
            # Create setup dictionary
            setup = {
                'symbol': symbol,
                'type': setup_type,
                'price': latest['close'],
                'timestamp': datetime.now().isoformat(),
                'confidence': confidence,
                'expiration': '0DTE',  # Zero days to expiration
                'strike': self._calculate_strike_price(symbol, latest['close'], setup_type),
                'indicators': {
                    'rsi': latest['rsi'],
                    'momentum': latest['momentum'],
                    'volume_ratio': latest['volume_ratio'],
                    'trend_strength': latest['trend_strength']
                },
                'recommendation': f"BUY {symbol} {setup_type} @ {self._calculate_strike_price(symbol, latest['close'], setup_type)}"
            }
            
            setups.append(setup)
            
        return setups
    
    def _calculate_strike_price(self, symbol, current_price, option_type):
        """
        Calculate appropriate strike price for the option
        
        Args:
            symbol: Trading symbol
            current_price: Current price of the underlying
            option_type: Option type (CALL or PUT)
            
        Returns:
            Strike price
        """
        # Determine strike price interval based on symbol
        if symbol == 'SPX':
            interval = 5
        elif symbol in ['QQQ', 'TSLA']:
            interval = 1
        else:
            interval = 0.5
            
        # Calculate strike price
        if option_type == 'CALL':
            # For calls, round up to the nearest interval
            strike = np.ceil(current_price / interval) * interval
        else:
            # For puts, round down to the nearest interval
            strike = np.floor(current_price / interval) * interval
            
        return strike
    
    def get_recommendations(self):
        """
        Get current recommendations
        
        Returns:
            List of recommendations
        """
        return self.recommendations
    
    def save_recommendations(self, file_path=None):
        """
        Save recommendations to a JSON file
        
        Args:
            file_path: Path to save the file (optional)
        """
        if not file_path:
            # Generate a timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"data/zero_dte_recommendations_{timestamp}.json"
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save recommendations to file
        with open(file_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'recommendations': self.recommendations
            }, f, indent=2)
            
        logger.info(f"Saved {len(self.recommendations)} recommendations to {file_path}")
        
        return file_path


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create scanner
    scanner = ZeroDTEScanner()
    
    # Example market data (replace with actual data in production)
    example_data = {
        'SPX': pd.DataFrame({
            'open': np.random.normal(4500, 20, 100),
            'high': np.random.normal(4520, 20, 100),
            'low': np.random.normal(4480, 20, 100),
            'close': np.random.normal(4500, 20, 100),
            'volume': np.random.normal(1000000, 200000, 100)
        }),
        'QQQ': pd.DataFrame({
            'open': np.random.normal(380, 5, 100),
            'high': np.random.normal(385, 5, 100),
            'low': np.random.normal(375, 5, 100),
            'close': np.random.normal(380, 5, 100),
            'volume': np.random.normal(500000, 100000, 100)
        })
    }
    
    # Scan for opportunities
    recommendations = scanner.scan_for_opportunities(example_data)
    
    # Print recommendations
    for rec in recommendations:
        print(f"Symbol: {rec['symbol']}")
        print(f"Type: {rec['type']}")
        print(f"Strike: {rec['strike']}")
        print(f"Confidence: {rec['confidence']:.2f}")
        print(f"Recommendation: {rec['recommendation']}")
        print("-" * 40) 