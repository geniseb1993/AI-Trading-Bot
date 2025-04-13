"""
Market Condition Analyzer Module

This module analyzes market conditions to inform trading decisions,
including volatility analysis, trend detection, and liquidity assessment.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """Market regime classification"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    VOLATILE = "volatile"
    CALM = "calm"
    UNKNOWN = "unknown"

class MarketConditionAnalyzer:
    """
    Analyzes market conditions to inform trading decisions
    
    This class provides tools to analyze current market conditions,
    including volatility analysis, trend detection, liquidity assessment,
    and correlation analysis.
    """
    
    def __init__(self, config=None):
        """
        Initialize with optional configuration
        
        Args:
            config: Optional configuration dictionary with parameters
        """
        self.config = config or {}
        
        # Set default parameters
        self.volatility_lookback = self.config.get('volatility_lookback', 20)
        self.trend_lookback = self.config.get('trend_lookback', 50)
        self.volume_lookback = self.config.get('volume_lookback', 20)
        self.rsi_period = self.config.get('rsi_period', 14)
        self.correlation_lookback = self.config.get('correlation_lookback', 30)
        
        # Set thresholds
        self.high_volatility_threshold = self.config.get('high_volatility_threshold', 0.20)
        self.low_volatility_threshold = self.config.get('low_volatility_threshold', 0.10)
        self.trend_strength_threshold = self.config.get('trend_strength_threshold', 0.6)
        self.high_volume_threshold = self.config.get('high_volume_threshold', 1.5)
        self.low_volume_threshold = self.config.get('low_volume_threshold', 0.5)
        
        logger.info("Market Condition Analyzer initialized")
        
    def update_config(self, config):
        """
        Update the configuration
        
        Args:
            config: New configuration dictionary
        """
        self.config.update(config)
        
        # Update parameters
        self.volatility_lookback = self.config.get('volatility_lookback', 20)
        self.trend_lookback = self.config.get('trend_lookback', 50)
        self.volume_lookback = self.config.get('volume_lookback', 20)
        self.rsi_period = self.config.get('rsi_period', 14)
        self.correlation_lookback = self.config.get('correlation_lookback', 30)
        
        # Update thresholds
        self.high_volatility_threshold = self.config.get('high_volatility_threshold', 0.20)
        self.low_volatility_threshold = self.config.get('low_volatility_threshold', 0.10)
        self.trend_strength_threshold = self.config.get('trend_strength_threshold', 0.6)
        self.high_volume_threshold = self.config.get('high_volume_threshold', 1.5)
        self.low_volume_threshold = self.config.get('low_volume_threshold', 0.5)
        
        logger.info("Market Condition Analyzer configuration updated")
        
    def analyze_market_conditions(self, market_data_dict, index_data=None):
        """
        Analyze market conditions for multiple symbols
        
        Args:
            market_data_dict: Dictionary of market data for each symbol
                Format: {'SYMBOL': DataFrame with OHLCV data, ...}
            index_data: Optional DataFrame with index data (e.g. S&P 500)
            
        Returns:
            dict: Market conditions for each symbol
        """
        result = {}
        
        # Analyze each symbol
        for symbol, data in market_data_dict.items():
            try:
                # Check if we have enough data
                if data is None or len(data) < max(self.volatility_lookback, self.trend_lookback):
                    logger.warning(f"Not enough data for {symbol}")
                    result[symbol] = self._get_default_analysis(symbol)
                    continue
                
                # Analyze market conditions
                analysis = self.analyze_single_symbol(symbol, data)
                
                # Add to result
                result[symbol] = analysis
                
            except Exception as e:
                logger.error(f"Error analyzing market conditions for {symbol}: {str(e)}")
                result[symbol] = self._get_default_analysis(symbol)
                
        # Add market-wide analysis if index data is provided
        if index_data is not None:
            try:
                market_wide = self.analyze_single_symbol("MARKET", index_data)
                result["MARKET"] = market_wide
            except Exception as e:
                logger.error(f"Error analyzing market-wide conditions: {str(e)}")
                result["MARKET"] = self._get_default_analysis("MARKET")
                
        return result
    
    def analyze_single_symbol(self, symbol, data):
        """
        Analyze market conditions for a single symbol
        
        Args:
            symbol: Symbol to analyze
            data: DataFrame with OHLCV data
            
        Returns:
            dict: Market condition analysis
        """
        # Ensure data is a DataFrame
        if not isinstance(data, pd.DataFrame):
            logger.error(f"Expected DataFrame for {symbol}, got {type(data)}")
            return self._get_default_analysis(symbol)
            
        # Make sure we have required columns
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            logger.error(f"Missing required columns for {symbol}")
            return self._get_default_analysis(symbol)
            
        # Calculate volatility
        atr = self._calculate_atr(data)
        hist_volatility = self._calculate_historical_volatility(data)
        
        # Calculate trend
        trend_direction, trend_strength = self._analyze_trend(data)
        
        # Calculate volume profile
        volume_profile = self._analyze_volume(data)
        
        # Calculate momentum
        rsi = self._calculate_rsi(data)
        macd, macd_signal, macd_hist = self._calculate_macd(data)
        
        # Determine market regime
        regime = self._determine_market_regime(
            data, trend_direction, trend_strength, hist_volatility
        )
        
        # Build result
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'volatility': {
                'atr': float(atr),
                'historical_volatility': float(hist_volatility),
                'is_high_volatility': hist_volatility > self.high_volatility_threshold,
                'is_low_volatility': hist_volatility < self.low_volatility_threshold
            },
            'trend': {
                'direction': trend_direction,
                'strength': float(trend_strength),
                'is_trending': trend_strength > self.trend_strength_threshold
            },
            'volume': {
                'profile': volume_profile,
                'is_high_volume': volume_profile > self.high_volume_threshold,
                'is_low_volume': volume_profile < self.low_volume_threshold
            },
            'momentum': {
                'rsi': float(rsi),
                'macd': float(macd),
                'macd_signal': float(macd_signal),
                'macd_histogram': float(macd_hist),
                'is_overbought': rsi > 70,
                'is_oversold': rsi < 30
            },
            'market_regime': regime.value,
            'support_resistance': {
                'support_levels': self._find_support_levels(data),
                'resistance_levels': self._find_resistance_levels(data)
            }
        }
        
        # Add any extra analysis based on config
        if self.config.get('include_moving_averages', False):
            result['moving_averages'] = self._calculate_moving_averages(data)
            
        if self.config.get('include_bollinger_bands', False):
            result['bollinger_bands'] = self._calculate_bollinger_bands(data)
            
        return result
    
    def _calculate_atr(self, data, period=14):
        """
        Calculate Average True Range (ATR)
        
        Args:
            data: DataFrame with OHLCV data
            period: Period for ATR calculation
            
        Returns:
            float: ATR value
        """
        try:
            # Make a copy to avoid modifying original data
            df = data.copy()
            
            # Calculate true range
            df['tr0'] = df['high'] - df['low']
            df['tr1'] = abs(df['high'] - df['close'].shift())
            df['tr2'] = abs(df['low'] - df['close'].shift())
            df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
            
            # Calculate ATR
            df['atr'] = df['tr'].rolling(period).mean()
            
            # Return the latest ATR value
            atr = df['atr'].iloc[-1]
            return atr if not np.isnan(atr) else 0
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {str(e)}")
            return 0
    
    def _calculate_historical_volatility(self, data, period=None):
        """
        Calculate historical volatility (standard deviation of returns)
        
        Args:
            data: DataFrame with OHLCV data
            period: Optional period for volatility calculation
            
        Returns:
            float: Historical volatility value
        """
        if period is None:
            period = self.volatility_lookback
            
        try:
            # Calculate daily returns
            returns = data['close'].pct_change().dropna()
            
            # Calculate volatility
            volatility = returns.tail(period).std() * np.sqrt(252)  # Annualized
            return volatility if not np.isnan(volatility) else 0
            
        except Exception as e:
            logger.error(f"Error calculating historical volatility: {str(e)}")
            return 0
    
    def _analyze_trend(self, data):
        """
        Analyze trend direction and strength
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            tuple: (trend_direction, trend_strength)
        """
        try:
            # Calculate simple moving averages
            short_ma = data['close'].rolling(20).mean()
            long_ma = data['close'].rolling(50).mean()
            
            # Determine trend direction
            if short_ma.iloc[-1] > long_ma.iloc[-1]:
                trend_direction = 1  # Uptrend
            elif short_ma.iloc[-1] < long_ma.iloc[-1]:
                trend_direction = -1  # Downtrend
            else:
                trend_direction = 0  # Neutral
                
            # Calculate trend strength using ADX
            trend_strength = self._calculate_adx(data)
            
            return trend_direction, trend_strength
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {str(e)}")
            return 0, 0
    
    def _calculate_adx(self, data, period=14):
        """
        Calculate Average Directional Index (ADX)
        
        Args:
            data: DataFrame with OHLCV data
            period: Period for ADX calculation
            
        Returns:
            float: ADX value (0-100, higher means stronger trend)
        """
        try:
            # Make a copy to avoid modifying original data
            df = data.copy()
            
            # Calculate +DM, -DM, +DI, -DI
            df['h_diff'] = df['high'] - df['high'].shift(1)
            df['l_diff'] = df['low'].shift(1) - df['low']
            
            df['plus_dm'] = np.where(
                (df['h_diff'] > df['l_diff']) & (df['h_diff'] > 0),
                df['h_diff'],
                0
            )
            df['minus_dm'] = np.where(
                (df['l_diff'] > df['h_diff']) & (df['l_diff'] > 0),
                df['l_diff'],
                0
            )
            
            # Calculate true range
            df['tr'] = np.maximum(
                df['high'] - df['low'],
                np.maximum(
                    abs(df['high'] - df['close'].shift(1)),
                    abs(df['low'] - df['close'].shift(1))
                )
            )
            
            # Calculate smoothed values
            df['tr_smoothed'] = df['tr'].rolling(period).mean()
            df['plus_di'] = 100 * (df['plus_dm'].rolling(period).mean() / df['tr_smoothed'])
            df['minus_di'] = 100 * (df['minus_dm'].rolling(period).mean() / df['tr_smoothed'])
            
            # Calculate directional index
            df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
            
            # Calculate ADX
            df['adx'] = df['dx'].rolling(period).mean()
            
            # Return the latest ADX value
            adx = df['adx'].iloc[-1]
            return adx / 100 if not np.isnan(adx) else 0  # Normalize to 0-1
            
        except Exception as e:
            logger.error(f"Error calculating ADX: {str(e)}")
            return 0
    
    def _analyze_volume(self, data):
        """
        Analyze volume profile
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            float: Volume profile (ratio to average)
        """
        try:
            # Calculate average volume
            avg_volume = data['volume'].tail(self.volume_lookback).mean()
            
            # Calculate volume profile
            volume_profile = data['volume'].iloc[-1] / avg_volume if avg_volume > 0 else 1
            
            return volume_profile
            
        except Exception as e:
            logger.error(f"Error analyzing volume: {str(e)}")
            return 1  # Default to neutral
    
    def _calculate_rsi(self, data, period=None):
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            data: DataFrame with OHLCV data
            period: Optional period for RSI calculation
            
        Returns:
            float: RSI value (0-100)
        """
        if period is None:
            period = self.rsi_period
            
        try:
            # Calculate price changes
            delta = data['close'].diff()
            
            # Calculate gains and losses
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # Calculate average gain and loss
            avg_gain = gain.rolling(period).mean()
            avg_loss = loss.rolling(period).mean()
            
            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            # Return the latest RSI value
            latest_rsi = rsi.iloc[-1]
            return latest_rsi if not np.isnan(latest_rsi) else 50
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return 50  # Default to neutral
    
    def _calculate_macd(self, data, fast_period=12, slow_period=26, signal_period=9):
        """
        Calculate Moving Average Convergence Divergence (MACD)
        
        Args:
            data: DataFrame with OHLCV data
            fast_period: Period for fast EMA
            slow_period: Period for slow EMA
            signal_period: Period for signal line
            
        Returns:
            tuple: (macd, signal, histogram)
        """
        try:
            # Calculate EMAs
            ema_fast = data['close'].ewm(span=fast_period).mean()
            ema_slow = data['close'].ewm(span=slow_period).mean()
            
            # Calculate MACD and signal
            macd = ema_fast - ema_slow
            signal = macd.ewm(span=signal_period).mean()
            
            # Calculate histogram
            histogram = macd - signal
            
            # Return latest values
            return (
                macd.iloc[-1] if not np.isnan(macd.iloc[-1]) else 0,
                signal.iloc[-1] if not np.isnan(signal.iloc[-1]) else 0,
                histogram.iloc[-1] if not np.isnan(histogram.iloc[-1]) else 0
            )
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            return 0, 0, 0
    
    def _determine_market_regime(self, data, trend_direction, trend_strength, volatility):
        """
        Determine market regime based on trend and volatility
        
        Args:
            data: DataFrame with OHLCV data
            trend_direction: Direction of the trend (1=up, -1=down, 0=neutral)
            trend_strength: Strength of the trend (0-1)
            volatility: Historical volatility
            
        Returns:
            MarketRegime: Market regime
        """
        try:
            # Check if trending
            if trend_strength > self.trend_strength_threshold:
                if trend_direction > 0:
                    regime = MarketRegime.TRENDING_UP
                elif trend_direction < 0:
                    regime = MarketRegime.TRENDING_DOWN
                else:
                    regime = MarketRegime.RANGING
            else:
                # Check volatility
                if volatility > self.high_volatility_threshold:
                    regime = MarketRegime.VOLATILE
                elif volatility < self.low_volatility_threshold:
                    regime = MarketRegime.CALM
                else:
                    regime = MarketRegime.RANGING
                    
            return regime
            
        except Exception as e:
            logger.error(f"Error determining market regime: {str(e)}")
            return MarketRegime.UNKNOWN
    
    def _find_support_levels(self, data, n_levels=3):
        """
        Find support levels
        
        Args:
            data: DataFrame with OHLCV data
            n_levels: Number of support levels to find
            
        Returns:
            list: Support levels
        """
        try:
            # Identify local minima
            minima = []
            for i in range(2, len(data) - 2):
                if (data['low'].iloc[i] < data['low'].iloc[i-1] and 
                    data['low'].iloc[i] < data['low'].iloc[i-2] and
                    data['low'].iloc[i] < data['low'].iloc[i+1] and
                    data['low'].iloc[i] < data['low'].iloc[i+2]):
                    minima.append(data['low'].iloc[i])
            
            # Get the most recent n_levels
            minima.sort(reverse=True)
            support_levels = minima[:n_levels]
            
            # If we don't have enough support levels, add recent lows
            if len(support_levels) < n_levels:
                recent_lows = data['low'].tail(20).nsmallest(n_levels).tolist()
                support_levels.extend(recent_lows)
                
                # Remove duplicates and keep only n_levels
                support_levels = sorted(list(set(support_levels)), reverse=True)[:n_levels]
            
            return support_levels
            
        except Exception as e:
            logger.error(f"Error finding support levels: {str(e)}")
            return []
    
    def _find_resistance_levels(self, data, n_levels=3):
        """
        Find resistance levels
        
        Args:
            data: DataFrame with OHLCV data
            n_levels: Number of resistance levels to find
            
        Returns:
            list: Resistance levels
        """
        try:
            # Identify local maxima
            maxima = []
            for i in range(2, len(data) - 2):
                if (data['high'].iloc[i] > data['high'].iloc[i-1] and 
                    data['high'].iloc[i] > data['high'].iloc[i-2] and
                    data['high'].iloc[i] > data['high'].iloc[i+1] and
                    data['high'].iloc[i] > data['high'].iloc[i+2]):
                    maxima.append(data['high'].iloc[i])
            
            # Get the most recent n_levels
            maxima.sort()
            resistance_levels = maxima[:n_levels]
            
            # If we don't have enough resistance levels, add recent highs
            if len(resistance_levels) < n_levels:
                recent_highs = data['high'].tail(20).nlargest(n_levels).tolist()
                resistance_levels.extend(recent_highs)
                
                # Remove duplicates and keep only n_levels
                resistance_levels = sorted(list(set(resistance_levels)))[:n_levels]
            
            return resistance_levels
            
        except Exception as e:
            logger.error(f"Error finding resistance levels: {str(e)}")
            return []
    
    def _calculate_moving_averages(self, data):
        """
        Calculate various moving averages
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            dict: Moving averages
        """
        try:
            result = {}
            
            # Calculate SMAs
            for period in [20, 50, 100, 200]:
                ma = data['close'].rolling(period).mean().iloc[-1]
                result[f'sma_{period}'] = float(ma) if not np.isnan(ma) else None
                
            # Calculate EMAs
            for period in [12, 26, 50]:
                ema = data['close'].ewm(span=period).mean().iloc[-1]
                result[f'ema_{period}'] = float(ema) if not np.isnan(ema) else None
                
            return result
            
        except Exception as e:
            logger.error(f"Error calculating moving averages: {str(e)}")
            return {}
    
    def _calculate_bollinger_bands(self, data, period=20, std_dev=2):
        """
        Calculate Bollinger Bands
        
        Args:
            data: DataFrame with OHLCV data
            period: Period for moving average
            std_dev: Number of standard deviations
            
        Returns:
            dict: Bollinger Bands
        """
        try:
            # Calculate middle band (SMA)
            middle = data['close'].rolling(period).mean()
            
            # Calculate standard deviation
            std = data['close'].rolling(period).std()
            
            # Calculate upper and lower bands
            upper = middle + (std * std_dev)
            lower = middle - (std * std_dev)
            
            # Get latest values
            return {
                'upper': float(upper.iloc[-1]) if not np.isnan(upper.iloc[-1]) else None,
                'middle': float(middle.iloc[-1]) if not np.isnan(middle.iloc[-1]) else None,
                'lower': float(lower.iloc[-1]) if not np.isnan(lower.iloc[-1]) else None,
                'width': float((upper.iloc[-1] - lower.iloc[-1]) / middle.iloc[-1]) if not np.isnan(middle.iloc[-1]) and middle.iloc[-1] > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return {}
    
    def _get_default_analysis(self, symbol):
        """
        Get default analysis for a symbol
        
        Args:
            symbol: Symbol to get default analysis for
            
        Returns:
            dict: Default market condition analysis
        """
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'volatility': {
                'atr': 0,
                'historical_volatility': 0,
                'is_high_volatility': False,
                'is_low_volatility': False
            },
            'trend': {
                'direction': 0,
                'strength': 0,
                'is_trending': False
            },
            'volume': {
                'profile': 1,
                'is_high_volume': False,
                'is_low_volume': False
            },
            'momentum': {
                'rsi': 50,
                'macd': 0,
                'macd_signal': 0,
                'macd_histogram': 0,
                'is_overbought': False,
                'is_oversold': False
            },
            'market_regime': MarketRegime.UNKNOWN.value,
            'support_resistance': {
                'support_levels': [],
                'resistance_levels': []
            }
        } 