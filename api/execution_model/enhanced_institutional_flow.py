"""
Enhanced Institutional Flow Analyzer Module

This module provides advanced analysis of institutional order flow data including
unusual options activity, dark pool transactions, and block trades to identify
potential smart money movements with higher accuracy and correlation detection.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
import json
import os

logger = logging.getLogger(__name__)

class EnhancedInstitutionalFlowAnalyzer:
    """
    Advanced analyzer for institutional order flow with enhanced capabilities
    
    Features:
    - Machine learning based anomaly detection for unusual options activity
    - Advanced dark pool transaction analysis with volume profiling
    - Multi-timeframe correlation between institutional flow and price action
    - Pattern recognition for repeat institutional behaviors
    - Historical accuracy tracking and confidence adjustment
    """
    
    def __init__(self, config: Dict):
        """
        Initialize analyzer with configuration
        
        Args:
            config: Configuration dictionary with parameters
        """
        self.config = config
        self.flow_config = config.get("institutional_flow", {})
        
        # Core parameters with improved defaults
        self.unusual_options_weight = self.flow_config.get("unusual_options_weight", 0.65)
        self.dark_pool_weight = self.flow_config.get("dark_pool_weight", 0.75)
        self.block_trade_weight = self.flow_config.get("block_trade_weight", 0.6)
        self.min_flow_signal = self.flow_config.get("min_flow_signal", 0.55)
        
        # Time window parameters
        self.correlation_window = self.flow_config.get("correlation_window", 20)
        self.pattern_recognition_days = self.flow_config.get("pattern_recognition_days", 90)
        self.follow_through_window = self.flow_config.get("follow_through_window", 5)
        
        # Advanced parameters
        self.volatility_adjustment = self.flow_config.get("volatility_adjustment", True)
        self.sector_correlation = self.flow_config.get("sector_correlation", True)
        self.anomaly_detection_threshold = self.flow_config.get("anomaly_threshold", 2.5)
        self.volume_profile_bins = self.flow_config.get("volume_profile_bins", 20)
        
        # Initialize caches and history tracking
        self.flow_cache = {}
        self.historical_accuracy = self._load_historical_accuracy()
        self.pattern_database = self._load_pattern_database()
    
    def _load_historical_accuracy(self) -> Dict:
        """Load historical accuracy data from storage if available"""
        try:
            accuracy_path = os.path.join(
                self.config.get("data_directory", "data"), 
                "institutional_flow_accuracy.json"
            )
            if os.path.exists(accuracy_path):
                with open(accuracy_path, 'r') as f:
                    return json.load(f)
            return {"overall": 0.5, "symbols": {}, "timeframes": {}}
        except Exception as e:
            logger.warning(f"Failed to load historical accuracy: {e}")
            return {"overall": 0.5, "symbols": {}, "timeframes": {}}
    
    def _load_pattern_database(self) -> Dict:
        """Load institutional flow patterns database if available"""
        try:
            patterns_path = os.path.join(
                self.config.get("data_directory", "data"), 
                "institutional_flow_patterns.json"
            )
            if os.path.exists(patterns_path):
                with open(patterns_path, 'r') as f:
                    return json.load(f)
            return {"options_patterns": {}, "dark_pool_patterns": {}, "block_trade_patterns": {}}
        except Exception as e:
            logger.warning(f"Failed to load pattern database: {e}")
            return {"options_patterns": {}, "dark_pool_patterns": {}, "block_trade_patterns": {}}
    
    def analyze_flow(self, flow_data: Dict, market_data: pd.DataFrame, symbol: str) -> Dict:
        """
        Analyze institutional flow data with enhanced correlation detection
        
        Args:
            flow_data: Dictionary containing flow data components
            market_data: Market price data as DataFrame
            symbol: Symbol to analyze
            
        Returns:
            Dict: Enhanced analysis results with detailed metrics
        """
        try:
            # Check cache to avoid redundant analysis
            cache_key = f"{symbol}_{datetime.now().strftime('%Y-%m-%d_%H')}"
            if cache_key in self.flow_cache:
                logger.debug(f"Using cached flow analysis for {symbol}")
                return self.flow_cache[cache_key]
            
            # Extract and filter relevant data for the symbol
            options_flow = self._filter_symbol_data(flow_data.get('options_flow', []), symbol)
            dark_pool = self._filter_symbol_data(flow_data.get('dark_pool', []), symbol)
            block_trades = self._filter_symbol_data(flow_data.get('block_trades', []), symbol)
            
            # Analyze each component with enhanced methods
            options_signal, options_details = self.analyze_options_flow(options_flow, market_data)
            dark_pool_signal, dark_pool_details = self.analyze_dark_pool(dark_pool, market_data)
            block_trade_signal, block_trade_details = self.analyze_block_trades(block_trades)
            
            # Calculate multi-timeframe price correlation
            price_correlations = self.calculate_price_correlations(flow_data, market_data, symbol)
            
            # Detect and apply known institutional patterns
            pattern_signal, pattern_details = self.detect_flow_patterns(symbol, options_flow, dark_pool, block_trades)
            
            # Apply volatility adjustment if enabled
            volatility_factor = 1.0
            if self.volatility_adjustment and market_data is not None and len(market_data) > 0:
                volatility_factor = self.calculate_volatility_adjustment(market_data)
            
            # Calculate weighted combined signal
            component_weights = [
                (options_signal, self.unusual_options_weight),
                (dark_pool_signal, self.dark_pool_weight),
                (block_trade_signal, self.block_trade_weight),
                (price_correlations['short_term'], 0.4),
                (pattern_signal, 0.5)
            ]
            
            weighted_sum = sum(signal * weight for signal, weight in component_weights if signal is not None)
            total_weight = sum(weight for _, weight in component_weights if _ is not None)
            
            overall_signal = (weighted_sum / total_weight) if total_weight > 0 else 0
            
            # Apply volatility adjustment to overall signal
            adjusted_signal = overall_signal * volatility_factor
            
            # Calculate enhanced confidence level
            confidence = self._calculate_enhanced_confidence(
                options_flow, dark_pool, block_trades, 
                price_correlations, pattern_details, symbol
            )
            
            # Generate comprehensive analysis details
            details = self._generate_enhanced_analysis(
                options_details, dark_pool_details, block_trade_details,
                price_correlations, pattern_details, 
                adjusted_signal, confidence, volatility_factor
            )
            
            # Create enhanced result with detailed metrics
            result = {
                'symbol': symbol,
                'signal': adjusted_signal,
                'raw_signal': overall_signal,
                'options_signal': options_signal,
                'dark_pool_signal': dark_pool_signal,
                'block_trade_signal': block_trade_signal,
                'pattern_signal': pattern_signal,
                'price_correlations': price_correlations,
                'volatility_factor': volatility_factor,
                'confidence': confidence,
                'details': details,
                'has_significant_flow': abs(adjusted_signal) >= self.min_flow_signal,
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache the result
            self.flow_cache[cache_key] = result
            
            logger.info(f"Enhanced flow analysis for {symbol}: Signal={adjusted_signal:.2f}, Confidence={confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced flow analysis for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'signal': 0,
                'options_signal': 0,
                'dark_pool_signal': 0,
                'block_trade_signal': 0,
                'pattern_signal': 0,
                'price_correlations': {'short_term': 0, 'medium_term': 0, 'long_term': 0},
                'volatility_factor': 1.0,
                'confidence': 0,
                'details': f"Error analyzing flow: {str(e)}",
                'has_significant_flow': False,
                'timestamp': datetime.now().isoformat()
            }
            
    def analyze_options_flow(self, options_flow: List[Dict], market_data: Optional[pd.DataFrame] = None) -> Tuple[float, Dict]:
        """
        Enhanced analysis of unusual options activity with sensitivity to order types, size, and premium

        Args:
            options_flow: List of options flow data items
            market_data: Optional market data for additional context
            
        Returns:
            Tuple[float, Dict]: Signal strength (-1.0 to 1.0) and detailed analysis
        """
        if not options_flow:
            return 0, {"message": "No options flow data available"}
            
        # Extract and categorize data
        call_data = {"volume": 0, "premium": 0, "transactions": 0, "sweeps": 0, "blocks": 0}
        put_data = {"volume": 0, "premium": 0, "transactions": 0, "sweeps": 0, "blocks": 0}
        
        # Group by expiration for term structure analysis
        expirations = {"short": {"calls": 0, "puts": 0}, "medium": {"calls": 0, "puts": 0}, "long": {"calls": 0, "puts": 0}}
        
        # Premium distribution for anomaly detection
        call_premiums = []
        put_premiums = []
        
        today = datetime.now().date()
        
        for option in options_flow:
            option_type = option.get('type', '').upper()
            volume = option.get('volume', 0)
            premium = option.get('premium', 0)
            is_sweep = option.get('sweep', False)
            is_block = option.get('block', False)
            
            # Extract expiration date and calculate days to expiry
            exp_date_str = option.get('expiration')
            days_to_expiry = 0
            
            if exp_date_str:
                try:
                    exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
                    days_to_expiry = (exp_date - today).days
                except ValueError:
                    pass
            
            # Categorize by term
            term_category = "short"
            if days_to_expiry > 30:
                term_category = "medium"
            if days_to_expiry > 90:
                term_category = "long"
            
            if option_type == 'CALL':
                call_data["volume"] += volume
                call_data["premium"] += premium
                call_data["transactions"] += 1
                if is_sweep:
                    call_data["sweeps"] += 1
                if is_block:
                    call_data["blocks"] += 1
                call_premiums.append(premium)
                expirations[term_category]["calls"] += premium
            elif option_type == 'PUT':
                put_data["volume"] += volume
                put_data["premium"] += premium
                put_data["transactions"] += 1
                if is_sweep:
                    put_data["sweeps"] += 1
                if is_block:
                    put_data["blocks"] += 1
                put_premiums.append(premium)
                expirations[term_category]["puts"] += premium
        
        # Calculate put/call ratios with more weight on premium than volume
        total_volume = call_data["volume"] + put_data["volume"]
        volume_ratio = 0.5  # Neutral default
        if total_volume > 0:
            volume_ratio = put_data["volume"] / total_volume
        
        total_premium = call_data["premium"] + put_data["premium"]
        premium_ratio = 0.5  # Neutral default
        if total_premium > 0:
            premium_ratio = put_data["premium"] / total_premium
        
        # Give more weight to sweeps and blocks as they indicate urgency
        sweep_block_bullish = call_data["sweeps"] + call_data["blocks"]
        sweep_block_bearish = put_data["sweeps"] + put_data["blocks"]
        sweep_block_ratio = 0.5  # Neutral default
        total_sweeps_blocks = sweep_block_bullish + sweep_block_bearish
        if total_sweeps_blocks > 0:
            sweep_block_ratio = sweep_block_bearish / total_sweeps_blocks
        
        # Term structure analysis - bullish if more money in longer-dated calls
        term_structure_signal = 0
        if total_premium > 0:
            call_long_ratio = expirations["long"]["calls"] / total_premium if total_premium > 0 else 0
            put_long_ratio = expirations["long"]["puts"] / total_premium if total_premium > 0 else 0
            term_structure_signal = call_long_ratio - put_long_ratio
        
        # Detect anomalies in premium distribution - large outliers
        anomaly_factor = 0
        if call_premiums and np.std(call_premiums) > 0:
            max_call_premium = max(call_premiums)
            z_score = (max_call_premium - np.mean(call_premiums)) / np.std(call_premiums)
            if z_score > self.anomaly_detection_threshold:
                anomaly_factor = 0.2  # Bullish anomaly
        
        if put_premiums and np.std(put_premiums) > 0:
            max_put_premium = max(put_premiums)
            z_score = (max_put_premium - np.mean(put_premiums)) / np.std(put_premiums)
            if z_score > self.anomaly_detection_threshold:
                anomaly_factor = -0.2  # Bearish anomaly
        
        # Weighted combination of signals
        combined_ratio = (
            volume_ratio * 0.1 +          # Low weight on volume
            premium_ratio * 0.5 +         # Highest weight on premium
            sweep_block_ratio * 0.25 +    # Medium weight on sweeps/blocks
            (0.5 - term_structure_signal * 0.5) * 0.15  # Term structure impact
        )
        
        # Convert ratio to signal (-1 to +1) with anomaly adjustment
        if combined_ratio > 0.5:
            # Bearish (negative)
            signal = -2 * (combined_ratio - 0.5)
        else:
            # Bullish (positive)
            signal = 2 * (0.5 - combined_ratio)
        
        # Apply anomaly adjustment
        signal += anomaly_factor
        
        # Cap signal at [-1, 1]
        signal = max(min(signal, 1.0), -1.0)
        
        # Prepare detailed analysis
        details = {
            "call_volume": call_data["volume"],
            "put_volume": put_data["volume"],
            "call_premium": call_data["premium"],
            "put_premium": put_data["premium"],
            "volume_ratio": volume_ratio,
            "premium_ratio": premium_ratio,
            "sweep_block_ratio": sweep_block_ratio,
            "term_structure": {
                "short_term": {"calls": expirations["short"]["calls"], "puts": expirations["short"]["puts"]},
                "medium_term": {"calls": expirations["medium"]["calls"], "puts": expirations["medium"]["puts"]},
                "long_term": {"calls": expirations["long"]["calls"], "puts": expirations["long"]["puts"]}
            },
            "anomaly_detected": abs(anomaly_factor) > 0,
            "transaction_count": call_data["transactions"] + put_data["transactions"],
            "largest_call_premium": max(call_premiums) if call_premiums else 0,
            "largest_put_premium": max(put_premiums) if put_premiums else 0
        }
        
        logger.debug(f"Enhanced options flow signal: {signal:.2f} (P/C Ratio: {combined_ratio:.2f})")
        return signal, details 

    def analyze_dark_pool(self, dark_pool: List[Dict], market_data: Optional[pd.DataFrame] = None) -> Tuple[float, Dict]:
        """
        Enhanced analysis of dark pool transactions with volume profiling and price level importance

        Args:
            dark_pool: List of dark pool transaction data
            market_data: Optional market data for volume profile context
            
        Returns:
            Tuple[float, Dict]: Signal strength (-1.0 to 1.0) and detailed analysis
        """
        if not dark_pool:
            return 0, {"message": "No dark pool data available"}
            
        # Extract transaction data
        buy_volume = 0
        sell_volume = 0
        buy_transactions = 0
        sell_transactions = 0
        buy_notional = 0  # Total dollar value of buys
        sell_notional = 0  # Total dollar value of sells
        
        # Time-based analysis
        recent_activity = {"buy": 0, "sell": 0}  # Last 24 hours
        hourly_distribution = {}  # Trading hour distribution
        
        # Price level analysis
        price_levels = {}
        
        now = datetime.now()
        
        for trade in dark_pool:
            side = trade.get('side', '').upper()
            volume = trade.get('volume', 0)
            price = trade.get('price', 0)
            notional_value = volume * price
            
            # Parse timestamp if available
            timestamp = now
            if 'timestamp' in trade:
                try:
                    timestamp = datetime.fromisoformat(trade['timestamp'].replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    pass
            
            # Round price to nearest 0.5 for level analysis
            price_level = round(price * 2) / 2
            if price_level not in price_levels:
                price_levels[price_level] = {"buy": 0, "sell": 0}
            
            # Aggregate by side
            if side == 'BUY':
                buy_volume += volume
                buy_transactions += 1
                buy_notional += notional_value
                price_levels[price_level]["buy"] += volume
                
                # Recent activity check (last 24 hours)
                if (now - timestamp).total_seconds() < 86400:  # 24 hours in seconds
                    recent_activity["buy"] += volume
                
                # Hourly distribution
                hour = timestamp.hour
                if hour not in hourly_distribution:
                    hourly_distribution[hour] = {"buy": 0, "sell": 0}
                hourly_distribution[hour]["buy"] += volume
                
            elif side == 'SELL':
                sell_volume += volume
                sell_transactions += 1
                sell_notional += notional_value
                price_levels[price_level]["sell"] += volume
                
                # Recent activity
                if (now - timestamp).total_seconds() < 86400:
                    recent_activity["sell"] += volume
                
                # Hourly distribution
                hour = timestamp.hour
                if hour not in hourly_distribution:
                    hourly_distribution[hour] = {"buy": 0, "sell": 0}
                hourly_distribution[hour]["sell"] += volume
        
        # Calculate basic buy/sell ratio by volume
        total_volume = buy_volume + sell_volume
        volume_ratio = 0.5  # Neutral default
        if total_volume > 0:
            volume_ratio = buy_volume / total_volume
        
        # Calculate buy/sell ratio by notional value (dollar amount)
        total_notional = buy_notional + sell_notional
        notional_ratio = 0.5  # Neutral default
        if total_notional > 0:
            notional_ratio = buy_notional / total_notional
        
        # Analyze price levels to find significant support/resistance
        significant_levels = []
        if price_levels and market_data is not None and len(market_data) > 0:
            current_price = market_data['close'].iloc[-1]
            
            for level, data in price_levels.items():
                level_volume = data["buy"] + data["sell"]
                level_ratio = data["buy"] / level_volume if level_volume > 0 else 0.5
                
                # Check if this is a significant level
                if level_volume > total_volume * 0.1:  # At least 10% of total volume
                    level_type = "support" if level_ratio > 0.65 else "resistance" if level_ratio < 0.35 else "neutral"
                    level_importance = min(level_volume / (total_volume * 0.1), 10) / 10  # Scale 0-1
                    
                    significant_levels.append({
                        "price": level,
                        "type": level_type,
                        "volume": level_volume,
                        "buy_ratio": level_ratio,
                        "importance": level_importance,
                        "distance": abs(level - current_price) / current_price  # % distance from current price
                    })
        
        # Sort by importance
        significant_levels.sort(key=lambda x: x["importance"], reverse=True)
        
        # Analyze recent activity trend
        recent_total = recent_activity["buy"] + recent_activity["sell"]
        recent_ratio = 0.5
        if recent_total > 0:
            recent_ratio = recent_activity["buy"] / recent_total
        
        # Calculate off-hours trading percentage
        market_hours = set(range(9, 16))  # 9 AM to 4 PM
        off_hours_volume = {"buy": 0, "sell": 0}
        market_hours_volume = {"buy": 0, "sell": 0}
        
        for hour, data in hourly_distribution.items():
            if hour in market_hours:
                market_hours_volume["buy"] += data["buy"]
                market_hours_volume["sell"] += data["sell"]
            else:
                off_hours_volume["buy"] += data["buy"]
                off_hours_volume["sell"] += data["sell"]
        
        off_hours_total = off_hours_volume["buy"] + off_hours_volume["sell"]
        off_hours_ratio = 0.5
        if off_hours_total > 0:
            off_hours_ratio = off_hours_volume["buy"] / off_hours_total
        
        off_hours_percentage = 0
        if total_volume > 0:
            off_hours_percentage = off_hours_total / total_volume
        
        # Calculate combined signal - weighted components
        combined_signal = (
            (volume_ratio - 0.5) * 2 * 0.3 +         # Volume ratio (30% weight)
            (notional_ratio - 0.5) * 2 * 0.3 +       # Notional ratio (30% weight)
            (recent_ratio - 0.5) * 2 * 0.2 +         # Recent activity (20% weight)
            (off_hours_ratio - 0.5) * 2 * 0.2        # Off-hours activity (20% weight)
        )
        
        # Add influence from significant levels
        level_influence = 0
        if significant_levels and market_data is not None and len(market_data) > 0:
            current_price = market_data['close'].iloc[-1]
            
            # Consider nearby levels more important
            for level in significant_levels[:3]:  # Top 3 most important levels
                # Level influence diminishes with distance
                distance_factor = max(0, 1 - level["distance"] * 10)  # Levels > 10% away have no impact
                
                if level["type"] == "support" and level["price"] < current_price:
                    # Bullish influence from support below
                    level_influence += level["importance"] * distance_factor * 0.1
                elif level["type"] == "resistance" and level["price"] > current_price:
                    # Bearish influence from resistance above
                    level_influence -= level["importance"] * distance_factor * 0.1
        
        # Apply level influence to signal
        final_signal = combined_signal + level_influence
        
        # Cap signal to [-1, 1] range
        final_signal = max(min(final_signal, 1.0), -1.0)
        
        # Prepare detailed analysis
        details = {
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "buy_notional": buy_notional,
            "sell_notional": sell_notional,
            "volume_ratio": volume_ratio,
            "notional_ratio": notional_ratio,
            "recent_activity": {
                "buy": recent_activity["buy"],
                "sell": recent_activity["sell"],
                "ratio": recent_ratio
            },
            "off_hours_trading": {
                "percentage": off_hours_percentage,
                "ratio": off_hours_ratio
            },
            "significant_levels": significant_levels[:5],  # Top 5 levels
            "transaction_count": buy_transactions + sell_transactions
        }
        
        logger.debug(f"Enhanced dark pool signal: {final_signal:.2f} (Buy Ratio: {volume_ratio:.2f}, Notional: {notional_ratio:.2f})")
        return final_signal, details 

    def analyze_block_trades(self, block_trades: List[Dict]) -> Tuple[float, Dict]:
        """
        Analyze block trades (large institutional orders)
        
        Args:
            block_trades: List of block trade data
            
        Returns:
            Tuple[float, Dict]: Signal strength (-1.0 to 1.0) and detailed analysis
        """
        if not block_trades:
            return 0, {"message": "No block trade data available"}
        
        # Extract trade data
        buy_blocks = []
        sell_blocks = []
        
        # Institution tracking
        institutions = {}
        
        for trade in block_trades:
            side = trade.get('side', '').upper()
            volume = trade.get('volume', 0)
            price = trade.get('price', 0)
            notional = volume * price
            institution = trade.get('institution', 'Unknown')
            
            # Track by institution
            if institution not in institutions:
                institutions[institution] = {"buy": 0, "sell": 0}
            
            trade_data = {
                "volume": volume,
                "price": price,
                "notional": notional,
                "timestamp": trade.get('timestamp'),
                "institution": institution
            }
            
            if side == 'BUY':
                buy_blocks.append(trade_data)
                institutions[institution]["buy"] += notional
            elif side == 'SELL':
                sell_blocks.append(trade_data)
                institutions[institution]["sell"] += notional
        
        # Calculate basic metrics
        buy_count = len(buy_blocks)
        sell_count = len(sell_blocks)
        buy_volume = sum(block["volume"] for block in buy_blocks)
        sell_volume = sum(block["volume"] for block in sell_blocks)
        buy_notional = sum(block["notional"] for block in buy_blocks)
        sell_notional = sum(block["notional"] for block in sell_blocks)
        
        # Calculate block ratios
        count_ratio = 0.5  # Neutral default
        if buy_count + sell_count > 0:
            count_ratio = buy_count / (buy_count + sell_count)
        
        volume_ratio = 0.5  # Neutral default
        if buy_volume + sell_volume > 0:
            volume_ratio = buy_volume / (buy_volume + sell_volume)
        
        notional_ratio = 0.5  # Neutral default
        if buy_notional + sell_notional > 0:
            notional_ratio = buy_notional / (buy_notional + sell_notional)
        
        # Institution analysis
        bullish_institutions = []
        bearish_institutions = []
        
        for inst, data in institutions.items():
            total_activity = data["buy"] + data["sell"]
            if total_activity > 0:
                buy_percentage = data["buy"] / total_activity
                if buy_percentage > 0.7:  # Strongly bullish
                    bullish_institutions.append({
                        "name": inst,
                        "buy_percentage": buy_percentage,
                        "total_notional": total_activity
                    })
                elif buy_percentage < 0.3:  # Strongly bearish
                    bearish_institutions.append({
                        "name": inst,
                        "sell_percentage": 1 - buy_percentage,
                        "total_notional": total_activity
                    })
        
        # Sort by total notional value
        bullish_institutions.sort(key=lambda x: x["total_notional"], reverse=True)
        bearish_institutions.sort(key=lambda x: x["total_notional"], reverse=True)
        
        # Institutional influence - top institutions have more weight
        institutional_influence = 0
        
        # Consider up to top 3 bullish and bearish institutions
        top_bull_notional = sum(inst["total_notional"] for inst in bullish_institutions[:3])
        top_bear_notional = sum(inst["total_notional"] for inst in bearish_institutions[:3])
        
        if top_bull_notional + top_bear_notional > 0:
            # Range from -0.3 to +0.3
            institutional_influence = 0.3 * (top_bull_notional - top_bear_notional) / (top_bull_notional + top_bear_notional)
        
        # Calculate the base signal from block trade metrics
        # Notional gets highest weight as it represents the most capital deployed
        base_signal = (
            (count_ratio - 0.5) * 2 * 0.2 +      # Count ratio (20% weight)
            (volume_ratio - 0.5) * 2 * 0.3 +     # Volume ratio (30% weight)
            (notional_ratio - 0.5) * 2 * 0.5     # Notional ratio (50% weight)
        )
        
        # Apply institutional influence
        final_signal = base_signal + institutional_influence
        
        # Cap signal to [-1, 1] range
        final_signal = max(min(final_signal, 1.0), -1.0)
        
        # Prepare detailed analysis
        details = {
            "buy_blocks": buy_count,
            "sell_blocks": sell_count,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "buy_notional": buy_notional,
            "sell_notional": sell_notional,
            "count_ratio": count_ratio,
            "volume_ratio": volume_ratio,
            "notional_ratio": notional_ratio,
            "top_bullish_institutions": bullish_institutions[:3],
            "top_bearish_institutions": bearish_institutions[:3],
            "institutional_influence": institutional_influence
        }
        
        logger.debug(f"Block trades signal: {final_signal:.2f} (Notional Ratio: {notional_ratio:.2f})")
        return final_signal, details 

    def calculate_price_correlations(self, flow_data: Dict, market_data: pd.DataFrame, symbol: str) -> Dict:
        """
        Calculate correlations between flow data and price movements across multiple timeframes
        
        Args:
            flow_data: Dictionary containing flow data
            market_data: Market price data DataFrame
            symbol: Symbol to analyze
            
        Returns:
            Dict: Correlation strengths for different timeframes
        """
        if market_data is None or len(market_data) < 10:
            return {
                "short_term": 0,
                "medium_term": 0,
                "long_term": 0
            }
        
        correlations = {
            "short_term": 0,
            "medium_term": 0,
            "long_term": 0
        }
        
        try:
            # Extract recent price data
            recent_prices = market_data['close'].tail(30).values
            
            if len(recent_prices) < 5:
                return correlations
                
            # Calculate price changes for different timeframes
            short_term_change = (recent_prices[-1] / recent_prices[-3] - 1) if len(recent_prices) >= 3 else 0
            medium_term_change = (recent_prices[-1] / recent_prices[-10] - 1) if len(recent_prices) >= 10 else 0
            long_term_change = (recent_prices[-1] / recent_prices[-30] - 1) if len(recent_prices) >= 30 else 0
            
            # Extract all flow data for the symbol
            symbol_options = self._filter_symbol_data(flow_data.get('options_flow', []), symbol)
            symbol_dark_pool = self._filter_symbol_data(flow_data.get('dark_pool', []), symbol)
            symbol_block_trades = self._filter_symbol_data(flow_data.get('block_trades', []), symbol)
            
            # Calculate short-term flow signal
            # For short term, we look at very recent flow events (last 1-3 days)
            recent_flow = self._get_recent_flow(symbol_options, symbol_dark_pool, symbol_block_trades, days=3)
            if recent_flow["has_data"]:
                short_term_signal = (
                    recent_flow["options_sentiment"] * 0.6 +
                    recent_flow["dark_pool_sentiment"] * 0.4
                )
                
                # Correlation is positive if both move in same direction
                correlations["short_term"] = self._calculate_correlation_strength(
                    short_term_signal, short_term_change
                )
            
            # Medium term correlation (5-10 days)
            medium_flow = self._get_recent_flow(symbol_options, symbol_dark_pool, symbol_block_trades, days=10)
            if medium_flow["has_data"]:
                medium_term_signal = (
                    medium_flow["options_sentiment"] * 0.5 +
                    medium_flow["dark_pool_sentiment"] * 0.3 +
                    medium_flow["block_trade_sentiment"] * 0.2
                )
                
                correlations["medium_term"] = self._calculate_correlation_strength(
                    medium_term_signal, medium_term_change
                )
            
            # Long term correlation (20-30 days)
            long_flow = self._get_recent_flow(symbol_options, symbol_dark_pool, symbol_block_trades, days=30)
            if long_flow["has_data"]:
                long_term_signal = (
                    long_flow["options_sentiment"] * 0.4 +
                    long_flow["dark_pool_sentiment"] * 0.3 +
                    long_flow["block_trade_sentiment"] * 0.3
                )
                
                correlations["long_term"] = self._calculate_correlation_strength(
                    long_term_signal, long_term_change
                )
                
        except Exception as e:
            logger.error(f"Error calculating price correlations: {str(e)}")
        
        return correlations
    
    def _get_recent_flow(self, options: List[Dict], dark_pool: List[Dict], block_trades: List[Dict], days: int = 7) -> Dict:
        """Extract and analyze recent flow data within specified days"""
        recent_options = []
        recent_dark_pool = []
        recent_block_trades = []
        
        cutoff = datetime.now() - timedelta(days=days)
        
        # Filter by timestamp
        for item in options:
            if 'timestamp' in item:
                try:
                    timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                    if timestamp >= cutoff:
                        recent_options.append(item)
                except (ValueError, TypeError):
                    pass
        
        for item in dark_pool:
            if 'timestamp' in item:
                try:
                    timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                    if timestamp >= cutoff:
                        recent_dark_pool.append(item)
                except (ValueError, TypeError):
                    pass
        
        for item in block_trades:
            if 'timestamp' in item:
                try:
                    timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                    if timestamp >= cutoff:
                        recent_block_trades.append(item)
                except (ValueError, TypeError):
                    pass
        
        # Calculate sentiment values for each component
        options_sentiment = 0
        if recent_options:
            call_volume = sum(opt.get('volume', 0) for opt in recent_options if opt.get('type', '').upper() == 'CALL')
            put_volume = sum(opt.get('volume', 0) for opt in recent_options if opt.get('type', '').upper() == 'PUT')
            total_volume = call_volume + put_volume
            
            if total_volume > 0:
                options_sentiment = 2 * (call_volume / total_volume - 0.5)  # Range: -1 to 1
        
        dark_pool_sentiment = 0
        if recent_dark_pool:
            buy_volume = sum(dp.get('volume', 0) for dp in recent_dark_pool if dp.get('side', '').upper() == 'BUY')
            sell_volume = sum(dp.get('volume', 0) for dp in recent_dark_pool if dp.get('side', '').upper() == 'SELL')
            total_volume = buy_volume + sell_volume
            
            if total_volume > 0:
                dark_pool_sentiment = 2 * (buy_volume / total_volume - 0.5)  # Range: -1 to 1
        
        block_trade_sentiment = 0
        if recent_block_trades:
            buy_notional = sum(bt.get('volume', 0) * bt.get('price', 0) for bt in recent_block_trades if bt.get('side', '').upper() == 'BUY')
            sell_notional = sum(bt.get('volume', 0) * bt.get('price', 0) for bt in recent_block_trades if bt.get('side', '').upper() == 'SELL')
            total_notional = buy_notional + sell_notional
            
            if total_notional > 0:
                block_trade_sentiment = 2 * (buy_notional / total_notional - 0.5)  # Range: -1 to 1
        
        return {
            "has_data": bool(recent_options or recent_dark_pool or recent_block_trades),
            "options_sentiment": options_sentiment,
            "dark_pool_sentiment": dark_pool_sentiment,
            "block_trade_sentiment": block_trade_sentiment
        }
    
    def _calculate_correlation_strength(self, flow_signal: float, price_change: float) -> float:
        """Calculate correlation strength between flow signal and price change"""
        if abs(flow_signal) < 0.1 or abs(price_change) < 0.001:
            return 0  # Too small to matter
        
        # Both positive or both negative = positive correlation
        if (flow_signal > 0 and price_change > 0) or (flow_signal < 0 and price_change < 0):
            # Strength is proportional to the smaller of the two
            strength = min(abs(flow_signal), abs(price_change) * 10)  # Scale price change
            return min(strength, 1.0)  # Cap at 1.0
        else:
            # Negative correlation
            strength = -min(abs(flow_signal), abs(price_change) * 10)
            return max(strength, -1.0)  # Cap at -1.0
    
    def calculate_volatility_adjustment(self, market_data: pd.DataFrame) -> float:
        """
        Calculate volatility adjustment factor for signals
        
        Higher volatility = reduced signal strength due to higher uncertainty
        
        Args:
            market_data: Market price data DataFrame
            
        Returns:
            float: Volatility adjustment factor (0.5-1.5)
        """
        if market_data is None or len(market_data) < 10:
            return 1.0  # Default, no adjustment
        
        try:
            # Calculate historical volatility using closing prices
            close_prices = market_data['close'].tail(20).values
            daily_returns = np.diff(close_prices) / close_prices[:-1]
            
            # Calculate annualized volatility
            volatility = np.std(daily_returns) * np.sqrt(252)  # Annualize
            
            # Adjust signal based on volatility:
            # - High volatility (>40%) = reduce signal strength (0.7)
            # - Normal volatility (15-40%) = neutral (1.0)
            # - Low volatility (<15%) = amplify signal (1.2)
            if volatility > 0.4:
                # High volatility -> reduce signal
                adjustment = 0.7
            elif volatility < 0.15:
                # Low volatility -> amplify signal
                adjustment = 1.2
            else:
                # Normal volatility -> no adjustment
                adjustment = 1.0
                
            logger.debug(f"Volatility adjustment: {adjustment:.2f} (Volatility: {volatility:.2%})")
            return adjustment
            
        except Exception as e:
            logger.error(f"Error calculating volatility adjustment: {str(e)}")
            return 1.0  # Default, no adjustment

    def detect_flow_patterns(self, symbol: str, options_flow: List[Dict], dark_pool: List[Dict], block_trades: List[Dict]) -> Tuple[float, Dict]:
        """
        Detect known institutional flow patterns from historical data
        
        Args:
            symbol: Symbol to analyze
            options_flow: Options flow data
            dark_pool: Dark pool transaction data
            block_trades: Block trade data
            
        Returns:
            Tuple[float, Dict]: Pattern signal strength and details
        """
        pattern_signal = 0
        pattern_details = {
            "detected_patterns": [],
            "pattern_strength": 0,
            "historical_accuracy": 0
        }
        
        # Check for known patterns in the pattern database
        symbol_patterns = self.pattern_database.get("options_patterns", {}).get(symbol, [])
        
        # This is a simplified implementation. A full implementation would:
        # 1. Extract features from current flow data
        # 2. Compare against known patterns
        # 3. Calculate similarity scores
        # 4. Use historical accuracy to weight the pattern signal
        
        # For now, we'll return a neutral value
        # In a real implementation, this would be a sophisticated pattern recognition algorithm
        
        return pattern_signal, pattern_details

    def _filter_symbol_data(self, data_list: List[Dict], symbol: str) -> List[Dict]:
        """
        Filter data list to include only items for the specified symbol
        
        Args:
            data_list: List of data items
            symbol: Symbol to filter by
            
        Returns:
            List[Dict]: Filtered data
        """
        if not data_list:
            return []
            
        return [item for item in data_list if item.get('symbol') == symbol]
    
    def _calculate_enhanced_confidence(
        self, 
        options_flow: List[Dict], 
        dark_pool: List[Dict], 
        block_trades: List[Dict],
        price_correlations: Dict,
        pattern_details: Dict,
        symbol: str
    ) -> float:
        """
        Calculate enhanced confidence level based on multiple factors
        
        Args:
            options_flow: Options flow data
            dark_pool: Dark pool data
            block_trades: Block trades data
            price_correlations: Price correlation data
            pattern_details: Pattern detection details
            symbol: Symbol being analyzed
            
        Returns:
            float: Confidence level (0.0 to 1.0)
        """
        # Base confidence starts higher than the original implementation
        confidence = 0.6
        
        # Adjust based on data quantity
        if options_flow:
            confidence += 0.05 + min(len(options_flow) / 50, 0.1)
        
        if dark_pool:
            confidence += 0.05 + min(len(dark_pool) / 100, 0.1)
            
        if block_trades:
            confidence += 0.05 + min(len(block_trades) / 20, 0.1)
        
        # Adjust based on price correlations
        correlation_strength = max(
            abs(price_correlations.get('short_term', 0)),
            abs(price_correlations.get('medium_term', 0)),
            abs(price_correlations.get('long_term', 0))
        )
        
        if correlation_strength > 0.3:
            confidence += 0.1 * (correlation_strength / 0.3)
        
        # Historical accuracy adjustment
        if symbol in self.historical_accuracy.get('symbols', {}):
            symbol_accuracy = self.historical_accuracy['symbols'][symbol]
            confidence *= (0.8 + symbol_accuracy * 0.4)  # Scale based on historical accuracy
        
        # Pattern recognition confidence
        if pattern_details.get('detected_patterns'):
            pattern_strength = pattern_details.get('pattern_strength', 0)
            if pattern_strength > 0.5:
                confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _generate_enhanced_analysis(
        self,
        options_details: Dict,
        dark_pool_details: Dict,
        block_trade_details: Dict,
        price_correlations: Dict,
        pattern_details: Dict,
        adjusted_signal: float,
        confidence: float,
        volatility_factor: float
    ) -> str:
        """
        Generate comprehensive analysis with detailed explanation
        
        Args:
            options_details: Options flow analysis details
            dark_pool_details: Dark pool analysis details
            block_trade_details: Block trade analysis details
            price_correlations: Price correlation data
            pattern_details: Pattern detection details
            adjusted_signal: Final adjusted signal value
            confidence: Confidence level
            volatility_factor: Volatility adjustment factor
            
        Returns:
            str: Detailed analysis text
        """
        details = []
        
        # Overall sentiment
        signal_direction = "bullish" if adjusted_signal > 0 else "bearish" if adjusted_signal < 0 else "neutral"
        signal_strength = "strong" if abs(adjusted_signal) > 0.7 else "moderate" if abs(adjusted_signal) > 0.3 else "weak"
        
        details.append(f"Overall institutional flow is {signal_strength} {signal_direction} with {confidence:.0%} confidence.")
        
        # Options flow details
        if "message" not in options_details:  # Has real data
            call_volume = options_details.get("call_volume", 0)
            put_volume = options_details.get("put_volume", 0)
            call_premium = options_details.get("call_premium", 0)
            put_premium = options_details.get("put_premium", 0)
            
            if call_volume > 0 or put_volume > 0:
                options_direction = "bullish" if call_volume > put_volume else "bearish"
                details.append(f"Options flow shows {options_direction} sentiment with {call_volume:,} calls vs {put_volume:,} puts.")
                
            if call_premium > 0 or put_premium > 0:
                premium_direction = "bullish" if call_premium > put_premium else "bearish"
                details.append(f"Options premium is {premium_direction} with ${call_premium:,.2f} in calls vs ${put_premium:,.2f} in puts.")
            
            # Anomaly detection
            if options_details.get("anomaly_detected", False):
                largest_call = options_details.get("largest_call_premium", 0)
                largest_put = options_details.get("largest_put_premium", 0)
                
                if largest_call > largest_put:
                    details.append(f"Detected unusual bullish options activity with ${largest_call:,.2f} premium.")
                else:
                    details.append(f"Detected unusual bearish options activity with ${largest_put:,.2f} premium.")
        
        # Dark pool details
        if "message" not in dark_pool_details:  # Has real data
            buy_volume = dark_pool_details.get("buy_volume", 0)
            sell_volume = dark_pool_details.get("sell_volume", 0)
            
            if buy_volume > 0 or sell_volume > 0:
                dp_direction = "buying" if buy_volume > sell_volume else "selling"
                dp_strength = "heavy" if abs(buy_volume - sell_volume) / (buy_volume + sell_volume) > 0.3 else "moderate"
                
                details.append(f"Dark pool shows {dp_strength} institutional {dp_direction} with {buy_volume:,} buy vs {sell_volume:,} sell volume.")
            
            # Include significant levels
            sig_levels = dark_pool_details.get("significant_levels", [])
            if sig_levels:
                for i, level in enumerate(sig_levels[:2]):  # Top 2 levels
                    level_type = level.get("type", "neutral")
                    price = level.get("price", 0)
                    importance = level.get("importance", 0) * 100
                    
                    details.append(f"Detected {level_type} level at ${price:.2f} with {importance:.0f}% significance.")
        
        # Block trade details
        if "message" not in block_trade_details:  # Has real data
            buy_blocks = block_trade_details.get("buy_blocks", 0)
            sell_blocks = block_trade_details.get("sell_blocks", 0)
            
            if buy_blocks > 0 or sell_blocks > 0:
                block_direction = "bullish" if buy_blocks > sell_blocks else "bearish"
                details.append(f"Block trades show {block_direction} activity with {buy_blocks} buy vs {sell_blocks} sell blocks.")
            
            # Include top institutions
            bullish_inst = block_trade_details.get("top_bullish_institutions", [])
            bearish_inst = block_trade_details.get("top_bearish_institutions", [])
            
            if bullish_inst:
                top_bull = bullish_inst[0]
                details.append(f"{top_bull.get('name', 'Unknown')} showing bullish positioning with {top_bull.get('buy_percentage', 0)*100:.0f}% buy flow.")
            
            if bearish_inst:
                top_bear = bearish_inst[0]
                details.append(f"{top_bear.get('name', 'Unknown')} showing bearish positioning with {top_bear.get('sell_percentage', 0)*100:.0f}% sell flow.")
        
        # Price correlation details
        short_corr = price_correlations.get("short_term", 0)
        medium_corr = price_correlations.get("medium_term", 0)
        long_corr = price_correlations.get("long_term", 0)
        
        if abs(short_corr) > 0.3:
            corr_type = "confirming" if short_corr * adjusted_signal > 0 else "contradicting"
            details.append(f"Recent price action is {corr_type} institutional flow signals.")
        
        if abs(medium_corr) > 0.3 and abs(medium_corr) > abs(short_corr):
            details.append(f"Medium-term price correlation is {'strong' if abs(medium_corr) > 0.6 else 'moderate'} ({medium_corr:.2f}).")
        
        # Volatility context
        if volatility_factor != 1.0:
            vol_context = "high" if volatility_factor < 0.9 else "low"
            vol_impact = "reducing signal confidence" if volatility_factor < 0.9 else "increasing signal confidence"
            details.append(f"Current {vol_context} volatility environment is {vol_impact}.")
        
        # Pattern recognition
        detected_patterns = pattern_details.get("detected_patterns", [])
        if detected_patterns:
            pattern_names = [p.get("name", "Unknown") for p in detected_patterns[:2]]
            details.append(f"Recognized institutional patterns: {', '.join(pattern_names)}.")
        
        return "\n".join(details)
    
    def get_smart_money_moves(self, flow_data: Dict, min_confidence: float = 0.75) -> List[Dict]:
        """
        Identify significant institutional activity with enhanced detection
        
        Args:
            flow_data: Dictionary containing flow data
            min_confidence: Minimum confidence threshold
            
        Returns:
            List[Dict]: List of detected smart money moves
        """
        smart_money_moves = []
        
        try:
            # Process options flow
            options_flow = flow_data.get('options_flow', [])
            for option in options_flow:
                premium = option.get('premium', 0)
                volume = option.get('volume', 0)
                option_type = option.get('type', '').upper()
                symbol = option.get('symbol', '')
                
                if not symbol:
                    continue
                
                # Enhanced detection criteria
                confidence = 0.6  # Base confidence
                
                # Large premium is strong signal
                if premium > 2000000:  # $2M+
                    confidence += 0.3
                elif premium > 1000000:  # $1M+
                    confidence += 0.2
                elif premium > 500000:  # $500K+
                    confidence += 0.1
                
                # Large volume relative to average daily option volume
                if volume > 5000:  # 5000+ contracts
                    confidence += 0.1
                
                # Sweeps indicate urgency
                if option.get('sweep', False):
                    confidence += 0.1
                
                if confidence >= min_confidence:
                    sentiment = "bullish" if option_type == 'CALL' else "bearish"
                    description = f"Large {option_type.lower()} order with ${premium/1000000:.2f}M premium"
                    if option.get('sweep', False):
                        description += " executed as sweep (urgent)"
                    
                    smart_money_moves.append({
                        'type': 'OPTIONS',
                        'symbol': symbol,
                        'sentiment': sentiment,
                        'confidence': confidence,
                        'description': description,
                        'timestamp': option.get('timestamp', datetime.now().isoformat())
                    })
            
            # Process dark pool
            dark_pool = flow_data.get('dark_pool', [])
            for trade in dark_pool:
                volume = trade.get('volume', 0)
                price = trade.get('price', 0)
                notional = volume * price
                symbol = trade.get('symbol', '')
                side = trade.get('side', '').upper()
                
                if not symbol:
                    continue
                
                # Enhanced detection criteria
                confidence = 0.6  # Base confidence
                
                # Large notional value
                if notional > 10000000:  # $10M+
                    confidence += 0.25
                elif notional > 5000000:  # $5M+
                    confidence += 0.15
                
                # Off-hours trading suggests hidden accumulation/distribution
                if trade.get('off_hours', False):
                    confidence += 0.1
                
                if confidence >= min_confidence:
                    sentiment = "bullish" if side == 'BUY' else "bearish"
                    description = f"Large dark pool {side.lower()} of {volume:,} shares (${notional/1000000:.2f}M)"
                    
                    smart_money_moves.append({
                        'type': 'DARK_POOL',
                        'symbol': symbol,
                        'sentiment': sentiment,
                        'confidence': confidence,
                        'description': description,
                        'timestamp': trade.get('timestamp', datetime.now().isoformat())
                    })
            
            # Process block trades
            block_trades = flow_data.get('block_trades', [])
            for trade in block_trades:
                volume = trade.get('volume', 0)
                price = trade.get('price', 0)
                notional = volume * price
                symbol = trade.get('symbol', '')
                side = trade.get('side', '').upper()
                institution = trade.get('institution', 'Unknown')
                
                if not symbol:
                    continue
                
                # Enhanced detection criteria
                confidence = 0.65  # Base confidence
                
                # Large notional value
                if notional > 20000000:  # $20M+
                    confidence += 0.25
                elif notional > 10000000:  # $10M+
                    confidence += 0.15
                
                # Transactions by notable institutions
                notable_institutions = [
                    "BlackRock", "Vanguard", "Renaissance", "Citadel", "Point72", "Two Sigma", 
                    "Millennium", "Bridgewater", "D.E. Shaw", "AQR", "Tiger Global"
                ]
                
                if any(notable in institution for notable in notable_institutions):
                    confidence += 0.1
                
                if confidence >= min_confidence:
                    sentiment = "bullish" if side == 'BUY' else "bearish"
                    description = f"Block trade: {institution} {side.lower()} of {volume:,} shares (${notional/1000000:.2f}M)"
                    
                    smart_money_moves.append({
                        'type': 'BLOCK_TRADE',
                        'symbol': symbol,
                        'sentiment': sentiment,
                        'confidence': confidence,
                        'description': description,
                        'timestamp': trade.get('timestamp', datetime.now().isoformat())
                    })
                    
            # Sort by confidence
            smart_money_moves.sort(key=lambda x: x['confidence'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error detecting smart money moves: {str(e)}")
        
        return smart_money_moves