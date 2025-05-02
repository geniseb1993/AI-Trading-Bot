"""
Market Condition Analyzer Module

This module analyzes market conditions to determine if the current market
is in a trend day, choppy day, or no-trade day condition.
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, time

logger = logging.getLogger(__name__)

class MarketConditionAnalyzer:
    """
    Analyzes market data to determine the current market condition
    
    Market conditions:
    - TREND: Strong directional movement, good for trend-following strategies
    - CHOPPY: Range-bound, good for mean-reversion strategies
    - NO_TRADE: Conditions unfavorable for trading
    """
    
    def __init__(self, config):
        """
        Initialize with configuration
        
        Args:
            config: ExecutionModelConfig instance
        """
        self.config = config
        self.indicators = {}
        
    def analyze_market_condition(self, market_data):
        """
        Determine the current market condition
        
        Args:
            market_data: Dictionary or DataFrame containing market data
                Required fields: 'open', 'high', 'low', 'close', 'volume', 'timestamp'
                
        Returns:
            str: 'TREND', 'CHOPPY', or 'NO_TRADE'
        """
        try:
            # Convert to DataFrame if dictionary
            if isinstance(market_data, dict):
                df = pd.DataFrame(market_data)
            else:
                df = market_data.copy()
                
            # Calculate indicators
            self._calculate_indicators(df)
            
            # Check for no-trade condition first
            if self.detect_no_trade_day(df):
                logger.info("Market condition analysis: NO_TRADE")
                return "NO_TRADE"
                
            # Check for trend day
            if self.detect_trend_day(df):
                logger.info("Market condition analysis: TREND")
                return "TREND"
                
            # Default to choppy
            logger.info("Market condition analysis: CHOPPY")
            return "CHOPPY"
            
        except Exception as e:
            logger.error(f"Error analyzing market condition: {str(e)}")
            # Default to NO_TRADE on error
            return "NO_TRADE"
            
    def _calculate_indicators(self, df):
        """
        Calculate technical indicators for analysis
        
        Args:
            df: DataFrame with market data
        """
        # Get config values
        trend_config = self.config.get("market_analyzer", {}).get("trend_detection", {})
        ma_lookback = trend_config.get("ma_lookback", 20)
        
        # Calculate ADX if we have enough data
        if len(df) >= 14:
            self.indicators["adx"] = self._calculate_adx(df, 14)
        else:
            self.indicators["adx"] = 0
            
        # Calculate moving averages if we have enough data
        if len(df) >= ma_lookback:
            self.indicators["sma"] = df['close'].rolling(window=ma_lookback).mean().iloc[-1]
            
        # Calculate RSI
        if len(df) >= 14:
            self.indicators["rsi"] = self._calculate_rsi(df, 14)
        else:
            self.indicators["rsi"] = 50
            
        # Calculate daily range as percentage
        if len(df) > 0:
            self.indicators["range_pct"] = (df['high'].iloc[-1] - df['low'].iloc[-1]) / df['low'].iloc[-1]
            
        # Calculate volume relative to average
        if len(df) >= 20:
            avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
            self.indicators["rel_volume"] = df['volume'].iloc[-1] / avg_volume if avg_volume > 0 else 0
        else:
            self.indicators["rel_volume"] = 1
            
    def detect_trend_day(self, df):
        """
        Detect if current market is in a trend day condition
        
        Args:
            df: DataFrame with market data
            
        Returns:
            bool: True if trend day, False otherwise
        """
        # Get config values
        trend_config = self.config.get("market_analyzer", {}).get("trend_detection", {})
        adx_threshold = trend_config.get("adx_threshold", 25)
        directional_threshold = trend_config.get("directional_threshold", 0.6)
        
        # Check if ADX indicates a trend
        adx_trend = self.indicators.get("adx", 0) >= adx_threshold
        
        # Check if close is near high/low indicating trend direction
        if len(df) > 0:
            latest = df.iloc[-1]
            high_close_diff = abs(latest['high'] - latest['close'])
            low_close_diff = abs(latest['low'] - latest['close'])
            range_size = latest['high'] - latest['low']
            
            # Check if close is near high (uptrend) or near low (downtrend)
            if range_size > 0:
                near_extreme = max(
                    (range_size - high_close_diff) / range_size,  # Near high (uptrend)
                    (range_size - low_close_diff) / range_size     # Near low (downtrend)
                )
                directional = near_extreme >= directional_threshold
            else:
                directional = False
        else:
            directional = False
            
        # Check volume confirmation
        volume_confirms = self.indicators.get("rel_volume", 0) >= 1.0
        
        return adx_trend and directional and volume_confirms
        
    def detect_choppy_day(self, df):
        """
        Detect if current market is in a choppy day condition
        
        Args:
            df: DataFrame with market data
            
        Returns:
            bool: True if choppy day, False otherwise
        """
        # Get config values
        choppy_config = self.config.get("market_analyzer", {}).get("choppy_detection", {})
        rsi_range = choppy_config.get("rsi_range", [40, 60])
        range_threshold = choppy_config.get("range_threshold", 0.005)
        
        # Check if RSI is in middle range
        rsi_middle = rsi_range[0] <= self.indicators.get("rsi", 50) <= rsi_range[1]
        
        # Check if price range is small
        small_range = self.indicators.get("range_pct", 0) <= range_threshold
        
        # Not a trend day
        not_trend = not self.detect_trend_day(df)
        
        return rsi_middle and small_range and not_trend
        
    def detect_no_trade_day(self, df):
        """
        Detect if current market should be a no-trade day
        
        Args:
            df: DataFrame with market data
            
        Returns:
            bool: True if no-trade day, False otherwise
        """
        # Get config values
        no_trade_config = self.config.get("market_analyzer", {}).get("no_trade_detection", {})
        volume_threshold = no_trade_config.get("volume_threshold", 0.7)
        volatility_threshold = no_trade_config.get("volatility_threshold", 0.5)
        
        # Check for low volume
        low_volume = self.indicators.get("rel_volume", 1) < volume_threshold
        
        # Check for low volatility
        low_volatility = self.indicators.get("range_pct", 0) < volatility_threshold
        
        # Check for market hours (avoid pre/post market)
        current_time = datetime.now().time()
        outside_market_hours = (current_time < time(9, 30)) or (current_time > time(16, 0))
        
        # Could add calendar check for holidays, major economic events, etc.
        
        return low_volume or low_volatility or outside_market_hours
        
    def _calculate_adx(self, df, period=14):
        """
        Calculate Average Directional Index (ADX)
        
        Args:
            df: DataFrame with market data
            period: Period for calculation
            
        Returns:
            float: ADX value
        """
        # Calculate True Range
        df = df.copy()
        df['tr1'] = abs(df['high'] - df['low'])
        df['tr2'] = abs(df['high'] - df['close'].shift(1))
        df['tr3'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        
        # Calculate Directional Movement
        df['up_move'] = df['high'] - df['high'].shift(1)
        df['down_move'] = df['low'].shift(1) - df['low']
        
        df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
        df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)
        
        # Calculate Smoothed Moving Averages
        df['tr_sma'] = df['tr'].rolling(window=period).mean()
        df['plus_dm_sma'] = df['plus_dm'].rolling(window=period).mean()
        df['minus_dm_sma'] = df['minus_dm'].rolling(window=period).mean()
        
        # Calculate Directional Indicators
        df['plus_di'] = 100 * (df['plus_dm_sma'] / df['tr_sma'])
        df['minus_di'] = 100 * (df['minus_dm_sma'] / df['tr_sma'])
        
        # Calculate Directional Index
        df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
        
        # Calculate ADX
        df['adx'] = df['dx'].rolling(window=period).mean()
        
        # Return latest ADX value
        return df['adx'].iloc[-1] if not pd.isna(df['adx'].iloc[-1]) else 0
        
    def _calculate_rsi(self, df, period=14):
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            df: DataFrame with market data
            period: Period for calculation
            
        Returns:
            float: RSI value
        """
        df = df.copy()
        df['change'] = df['close'].diff()
        df['gain'] = np.where(df['change'] > 0, df['change'], 0)
        df['loss'] = np.where(df['change'] < 0, -df['change'], 0)
        
        df['avg_gain'] = df['gain'].rolling(window=period).mean()
        df['avg_loss'] = df['loss'].rolling(window=period).mean()
        
        df['rs'] = df['avg_gain'] / df['avg_loss']
        df['rsi'] = 100 - (100 / (1 + df['rs']))
        
        return df['rsi'].iloc[-1] if not pd.isna(df['rsi'].iloc[-1]) else 50 