"""
Institutional Flow Analyzer Module

This module analyzes institutional order flow data such as unusual options activity
and dark pool transactions to identify potential smart money moves.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class InstitutionalFlowAnalyzer:
    """
    Analyzes institutional order flow data for trade signals
    
    Capabilities:
    - Detect unusual options activity
    - Analyze dark pool transactions
    - Correlate institutional flow with price action
    - Identify potential smart money moves
    """
    
    def __init__(self, config):
        """
        Initialize with configuration
        
        Args:
            config: ExecutionModelConfig instance
        """
        self.config = config
        self.flow_config = config.get("institutional_flow", {})
        
        # Get parameters from config with defaults
        self.unusual_options_weight = self.flow_config.get("unusual_options_weight", 0.7)
        self.dark_pool_weight = self.flow_config.get("dark_pool_weight", 0.8)
        self.min_flow_signal = self.flow_config.get("min_flow_signal", 0.6)
        self.correlation_window = self.flow_config.get("correlation_window", 20)
        
        # Cache for analyzed data
        self.flow_cache = {}
        
    def analyze_flow(self, flow_data, market_data, symbol):
        """
        Analyze institutional flow data for the specified symbol
        
        Args:
            flow_data: Dictionary containing flow data with keys:
                - 'options_flow': List of unusual options activity
                - 'dark_pool': List of dark pool transactions
            market_data: DataFrame containing market price data
            symbol: Symbol to analyze
            
        Returns:
            dict: Analysis results with keys:
                - 'signal': Overall signal strength (-1.0 to 1.0, negative for bearish)
                - 'options_signal': Options flow signal (-1.0 to 1.0)
                - 'dark_pool_signal': Dark pool signal (-1.0 to 1.0)
                - 'confidence': Confidence level (0.0 to 1.0)
                - 'details': Detailed analysis explanation
        """
        try:
            # Check cache first (avoid re-analyzing recent data)
            cache_key = f"{symbol}_{datetime.now().strftime('%Y-%m-%d_%H')}"
            if cache_key in self.flow_cache:
                logger.debug(f"Using cached flow analysis for {symbol}")
                return self.flow_cache[cache_key]
            
            # Extract data for the symbol
            options_flow = self._filter_symbol_data(flow_data.get('options_flow', []), symbol)
            dark_pool = self._filter_symbol_data(flow_data.get('dark_pool', []), symbol)
            
            # Analyze each flow component
            options_signal = self.analyze_options_flow(options_flow)
            dark_pool_signal = self.analyze_dark_pool(dark_pool)
            
            # Correlate with price movements if we have market data
            price_correlation = 0
            if market_data is not None and len(market_data) > 0:
                price_correlation = self.correlate_with_price_action(flow_data, market_data, symbol)
            
            # Calculate overall signal
            overall_signal = (
                options_signal * self.unusual_options_weight +
                dark_pool_signal * self.dark_pool_weight +
                price_correlation * 0.5  # Lower weight for price correlation
            ) / (self.unusual_options_weight + self.dark_pool_weight + 0.5)
            
            # Calculate confidence level
            confidence = self._calculate_confidence(options_flow, dark_pool, price_correlation)
            
            # Generate detailed analysis
            details = self._generate_analysis_details(
                options_flow, dark_pool, 
                options_signal, dark_pool_signal,
                price_correlation, overall_signal, confidence
            )
            
            # Create result
            result = {
                'symbol': symbol,
                'signal': overall_signal,
                'options_signal': options_signal,
                'dark_pool_signal': dark_pool_signal,
                'price_correlation': price_correlation,
                'confidence': confidence,
                'details': details,
                'has_significant_flow': abs(overall_signal) >= self.min_flow_signal,
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache the result
            self.flow_cache[cache_key] = result
            
            logger.info(f"Flow analysis for {symbol}: Signal={overall_signal:.2f}, Confidence={confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing flow data for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'signal': 0,
                'options_signal': 0,
                'dark_pool_signal': 0,
                'price_correlation': 0,
                'confidence': 0,
                'details': f"Error analyzing flow: {str(e)}",
                'has_significant_flow': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_options_flow(self, options_flow):
        """
        Analyze unusual options activity
        
        Args:
            options_flow: List of unusual options activity
            
        Returns:
            float: Signal strength (-1.0 to 1.0)
        """
        if not options_flow:
            return 0
            
        # Extract relevant data
        call_volume = 0
        put_volume = 0
        call_premium = 0
        put_premium = 0
        
        for option in options_flow:
            option_type = option.get('type', '').upper()
            volume = option.get('volume', 0)
            premium = option.get('premium', 0)
            
            if option_type == 'CALL':
                call_volume += volume
                call_premium += premium
            elif option_type == 'PUT':
                put_volume += volume
                put_premium += premium
        
        # Calculate put/call ratio by volume
        total_volume = call_volume + put_volume
        if total_volume > 0:
            put_call_ratio_volume = put_volume / total_volume
        else:
            put_call_ratio_volume = 0.5  # Neutral
            
        # Calculate put/call ratio by premium
        total_premium = call_premium + put_premium
        if total_premium > 0:
            put_call_ratio_premium = put_premium / total_premium
        else:
            put_call_ratio_premium = 0.5  # Neutral
            
        # Combine the signals, giving more weight to premium
        combined_put_call_ratio = (
            put_call_ratio_volume * 0.4 +
            put_call_ratio_premium * 0.6
        )
        
        # Convert to signal (-1 to +1)
        # A high put/call ratio (>0.7) is bearish (negative signal)
        # A low put/call ratio (<0.3) is bullish (positive signal)
        if combined_put_call_ratio > 0.5:
            # Bearish signal (negative)
            signal = -2 * (combined_put_call_ratio - 0.5)
        else:
            # Bullish signal (positive)
            signal = 2 * (0.5 - combined_put_call_ratio)
            
        logger.debug(f"Options flow signal: {signal:.2f} (P/C Ratio: {combined_put_call_ratio:.2f})")
        return signal
    
    def analyze_dark_pool(self, dark_pool):
        """
        Analyze dark pool transactions
        
        Args:
            dark_pool: List of dark pool transactions
            
        Returns:
            float: Signal strength (-1.0 to 1.0)
        """
        if not dark_pool:
            return 0
            
        # Extract buy/sell information
        buy_volume = 0
        sell_volume = 0
        
        for trade in dark_pool:
            side = trade.get('side', '').upper()
            volume = trade.get('volume', 0)
            
            if side == 'BUY':
                buy_volume += volume
            elif side == 'SELL':
                sell_volume += volume
        
        # Calculate buy/sell ratio
        total_volume = buy_volume + sell_volume
        if total_volume > 0:
            buy_ratio = buy_volume / total_volume
        else:
            buy_ratio = 0.5  # Neutral
            
        # Convert to signal (-1 to +1)
        signal = 2 * (buy_ratio - 0.5)
        
        logger.debug(f"Dark pool signal: {signal:.2f} (Buy Ratio: {buy_ratio:.2f})")
        return signal
    
    def correlate_with_price_action(self, flow_data, market_data, symbol):
        """
        Find correlations between flow and price movements
        
        Args:
            flow_data: Flow data dictionary
            market_data: Market price data DataFrame
            symbol: Symbol to analyze
            
        Returns:
            float: Correlation strength (-1.0 to 1.0)
        """
        # This is a simplified version, a real implementation would:
        # 1. Align flow data with price data by timestamp
        # 2. Calculate lagged correlations
        # 3. Detect if institutional flow precedes price movements
        
        # For now, we'll return a simple placeholder value
        # based on recent price action
        if len(market_data) < 2:
            return 0
            
        # Calculate recent price direction
        latest_close = market_data['close'].iloc[-1]
        prev_close = market_data['close'].iloc[-2]
        price_change = (latest_close - prev_close) / prev_close
        
        # Normalize to -1 to +1 range
        price_signal = min(max(price_change * 20, -1), 1)
        
        logger.debug(f"Price correlation signal: {price_signal:.2f}")
        return price_signal
    
    def detect_smart_money_moves(self, flow_data, min_confidence=0.7):
        """
        Identify significant institutional activity
        
        Args:
            flow_data: Dictionary containing flow data
            min_confidence: Minimum confidence threshold
            
        Returns:
            list: List of detected smart money moves
        """
        smart_money_moves = []
        
        # Process options flow
        options_flow = flow_data.get('options_flow', [])
        for option in options_flow:
            # Look for large premium transactions
            if option.get('premium', 0) > 1000000:  # $1M+ premium
                smart_money_moves.append({
                    'type': 'OPTIONS',
                    'symbol': option.get('symbol'),
                    'side': 'BUY' if option.get('type') == 'CALL' else 'SELL',
                    'confidence': 0.8,
                    'description': f"Large {option.get('type')} order with ${option.get('premium')/1000000:.2f}M premium"
                })
        
        # Process dark pool
        dark_pool = flow_data.get('dark_pool', [])
        for trade in dark_pool:
            # Look for large dark pool transactions
            if trade.get('volume', 0) * trade.get('price', 0) > 5000000:  # $5M+ transaction
                smart_money_moves.append({
                    'type': 'DARK_POOL',
                    'symbol': trade.get('symbol'),
                    'side': trade.get('side'),
                    'confidence': 0.75,
                    'description': f"Large dark pool {trade.get('side')} of {trade.get('volume')} shares"
                })
        
        # Filter by confidence
        smart_money_moves = [move for move in smart_money_moves if move['confidence'] >= min_confidence]
        
        return smart_money_moves
    
    def _filter_symbol_data(self, data_list, symbol):
        """
        Filter data list to include only items for the specified symbol
        
        Args:
            data_list: List of data items (options or dark pool)
            symbol: Symbol to filter by
            
        Returns:
            list: Filtered data
        """
        return [item for item in data_list if item.get('symbol') == symbol]
    
    def _calculate_confidence(self, options_flow, dark_pool, price_correlation):
        """
        Calculate confidence level for the analysis
        
        Args:
            options_flow: Options flow data
            dark_pool: Dark pool data
            price_correlation: Price correlation value
            
        Returns:
            float: Confidence level (0.0 to 1.0)
        """
        # Base confidence on quantity and quality of data
        confidence = 0.5  # Start with neutral confidence
        
        # More data = higher confidence
        if options_flow:
            confidence += 0.1 + (min(len(options_flow), 10) / 50)
        
        if dark_pool:
            confidence += 0.1 + (min(len(dark_pool), 20) / 100)
            
        # Strong price correlation increases confidence
        if abs(price_correlation) > 0.5:
            confidence += 0.1
            
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _generate_analysis_details(self, options_flow, dark_pool, 
                                  options_signal, dark_pool_signal,
                                  price_correlation, overall_signal, confidence):
        """
        Generate detailed analysis text
        
        Args:
            options_flow: Options flow data
            dark_pool: Dark pool data
            options_signal: Options signal value
            dark_pool_signal: Dark pool signal value
            price_correlation: Price correlation value
            overall_signal: Overall signal value
            confidence: Confidence level
            
        Returns:
            str: Detailed analysis
        """
        details = []
        
        # Options flow details
        options_count = len(options_flow)
        if options_count > 0:
            direction = "bullish" if options_signal > 0 else "bearish"
            strength = "strong" if abs(options_signal) > 0.7 else "moderate" if abs(options_signal) > 0.3 else "weak"
            details.append(f"Found {options_count} unusual options transactions indicating {strength} {direction} sentiment.")
            
        # Dark pool details
        dark_pool_count = len(dark_pool)
        if dark_pool_count > 0:
            direction = "buying" if dark_pool_signal > 0 else "selling"
            strength = "heavy" if abs(dark_pool_signal) > 0.7 else "moderate" if abs(dark_pool_signal) > 0.3 else "light"
            details.append(f"Detected {dark_pool_count} dark pool transactions showing {strength} institutional {direction}.")
            
        # Price correlation details
        if abs(price_correlation) > 0.3:
            correlation_direction = "aligned with" if price_correlation * overall_signal > 0 else "contrary to"
            details.append(f"Recent price action is {correlation_direction} institutional flow signals.")
            
        # Overall signal details
        signal_direction = "bullish" if overall_signal > 0 else "bearish" if overall_signal < 0 else "neutral"
        signal_strength = "strong" if abs(overall_signal) > 0.7 else "moderate" if abs(overall_signal) > 0.3 else "weak"
        
        details.append(f"Overall institutional flow is {signal_strength} {signal_direction} with {confidence:.0%} confidence.")
        
        return "\n".join(details) 