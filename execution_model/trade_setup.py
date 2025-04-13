"""
Trade Setup Generator Module

This module generates trade setups based on market conditions, technical indicators,
and institutional flow data.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class TradeSetupGenerator:
    """
    Generates trade setups based on market conditions and indicators
    
    This class evaluates market conditions and generates appropriate trade
    setups based on the current market type (trend, choppy, no-trade).
    """
    
    def __init__(self, market_analyzer, risk_manager, institutional_flow_analyzer, config):
        """
        Initialize with dependencies
        
        Args:
            market_analyzer: MarketConditionAnalyzer instance
            risk_manager: RiskManager instance
            institutional_flow_analyzer: InstitutionalFlowAnalyzer instance
            config: ExecutionModelConfig instance
        """
        self.market_analyzer = market_analyzer
        self.risk_manager = risk_manager
        self.flow_analyzer = institutional_flow_analyzer
        self.config = config
        
    def generate_trade_setups(self, market_data, flow_data, account_info):
        """
        Generate potential trade setups based on market conditions
        
        Args:
            market_data: Dictionary with market data for multiple symbols
                Format: {'SYMBOL': DataFrame with OHLCV data, ...}
            flow_data: Dictionary with institutional flow data
            account_info: Dictionary with account information
                Required keys: 'balance'
                
        Returns:
            list: List of trade setup dictionaries
        """
        trade_setups = []
        
        for symbol, data in market_data.items():
            try:
                # Analyze market condition for this symbol
                market_condition = self.market_analyzer.analyze_market_condition(data)
                
                # Skip if no-trade day
                if market_condition == "NO_TRADE":
                    logger.info(f"No-trade condition for {symbol}, skipping setup generation")
                    continue
                
                # Analyze institutional flow if available
                flow_analysis = None
                if flow_data:
                    flow_analysis = self.flow_analyzer.analyze_flow(flow_data, data, symbol)
                
                # Generate setups based on market condition
                symbol_setups = []
                
                if market_condition == "TREND":
                    symbol_setups = self.generate_trend_setups(symbol, data, flow_analysis, account_info)
                elif market_condition == "CHOPPY":
                    symbol_setups = self.generate_mean_reversion_setups(symbol, data, flow_analysis, account_info)
                
                # Add setups with necessary metadata
                for setup in symbol_setups:
                    setup.update({
                        'symbol': symbol,
                        'market_condition': market_condition,
                        'timestamp': datetime.now().isoformat(),
                        'flow_analysis': flow_analysis
                    })
                    trade_setups.append(setup)
                
                logger.info(f"Generated {len(symbol_setups)} trade setups for {symbol}")
                
            except Exception as e:
                logger.error(f"Error generating trade setups for {symbol}: {str(e)}")
                continue
        
        return trade_setups
    
    def generate_trend_setups(self, symbol, market_data, flow_analysis, account_info):
        """
        Generate trend-following trade setups
        
        Args:
            symbol: Trading symbol
            market_data: DataFrame with OHLCV data
            flow_analysis: Flow analysis result or None
            account_info: Account information dictionary
            
        Returns:
            list: List of trend-following trade setups
        """
        setups = []
        
        # Determine trend direction
        trend_direction = self._determine_trend_direction(market_data)
        
        # Skip if no clear trend
        if trend_direction == "NEUTRAL":
            return []
        
        # Check if institutional flow contradicts the trend
        if flow_analysis and abs(flow_analysis['signal']) > 0.7:
            flow_direction = "LONG" if flow_analysis['signal'] > 0 else "SHORT"
            if ((trend_direction == "LONG" and flow_direction == "SHORT") or 
                (trend_direction == "SHORT" and flow_direction == "LONG")):
                logger.info(f"Institutional flow contradicts trend for {symbol}, avoiding setup")
                return []
        
        # Get current price
        current_price = market_data['close'].iloc[-1]
        
        # Calculate entry price (use limit order slightly away from current price)
        if trend_direction == "LONG":
            entry_price = current_price * 0.9995  # Slightly below current price
            trade_direction = "LONG"
        else:
            entry_price = current_price * 1.0005  # Slightly above current price
            trade_direction = "SHORT"
        
        # Calculate stop loss using RiskManager
        stop_loss = self.risk_manager.calculate_stop_loss(
            entry_price, trade_direction, market_data, volatility_factor=1.5
        )
        
        # Calculate profit target
        profit_target = self.risk_manager.calculate_profit_target(
            entry_price, stop_loss, trade_direction
        )
        
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            account_info['balance'], entry_price, stop_loss, symbol
        )
        
        # Skip if position size is too small
        if position_size <= 0:
            logger.info(f"Position size too small for {symbol}, skipping setup")
            return []
        
        # Create setup
        setup = {
            'type': 'TREND_FOLLOWING',
            'direction': trade_direction,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'profit_target': profit_target,
            'position_size': position_size,
            'risk_reward': round(abs(profit_target - entry_price) / abs(entry_price - stop_loss), 2),
            'confidence': self._calculate_setup_confidence(
                market_data, flow_analysis, trade_direction, "TREND"
            ),
            'indicators': self._get_indicator_values(market_data),
            'setup_reason': self._generate_setup_reason(
                symbol, trade_direction, "TREND", market_data, flow_analysis
            )
        }
        
        setups.append(setup)
        return setups
    
    def generate_mean_reversion_setups(self, symbol, market_data, flow_analysis, account_info):
        """
        Generate mean-reversion trade setups
        
        Args:
            symbol: Trading symbol
            market_data: DataFrame with OHLCV data
            flow_analysis: Flow analysis result or None
            account_info: Account information dictionary
            
        Returns:
            list: List of mean-reversion trade setups
        """
        setups = []
        
        # Calculate if price is extended from moving average
        ma_period = 20
        if len(market_data) < ma_period:
            return []
            
        ma = market_data['close'].rolling(window=ma_period).mean().iloc[-1]
        current_price = market_data['close'].iloc[-1]
        
        # Calculate deviation from MA
        deviation = (current_price - ma) / ma
        
        # Skip if not enough deviation
        if abs(deviation) < 0.02:  # 2% deviation threshold
            return []
        
        # Determine trade direction (opposite of deviation)
        if deviation > 0:
            trade_direction = "SHORT"  # Price above MA, expect reversion down
        else:
            trade_direction = "LONG"   # Price below MA, expect reversion up
        
        # Check if institutional flow contradicts the mean-reversion
        if flow_analysis and abs(flow_analysis['signal']) > 0.7:
            flow_direction = "LONG" if flow_analysis['signal'] > 0 else "SHORT"
            if flow_direction != trade_direction:
                logger.info(f"Institutional flow contradicts mean-reversion for {symbol}, reducing confidence")
                # We'll still generate the setup but with lower confidence
        
        # Calculate entry price
        if trade_direction == "LONG":
            entry_price = current_price * 0.9995  # Slightly below current price
        else:
            entry_price = current_price * 1.0005  # Slightly above current price
        
        # Calculate stop loss
        # For mean-reversion, use tighter stops as we expect immediate reversion
        volatility_factor = 1.0
        stop_loss = self.risk_manager.calculate_stop_loss(
            entry_price, trade_direction, market_data, volatility_factor
        )
        
        # Calculate profit target (usually the moving average)
        risk = abs(entry_price - stop_loss)
        reward = risk * 1.5  # Lower reward expectation for mean-reversion
        
        if trade_direction == "LONG":
            profit_target = entry_price + reward
            # Cap profit target at MA if it's closer
            if ma < profit_target and ma > entry_price:
                profit_target = ma
        else:
            profit_target = entry_price - reward
            # Cap profit target at MA if it's closer
            if ma > profit_target and ma < entry_price:
                profit_target = ma
        
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            account_info['balance'], entry_price, stop_loss, symbol
        )
        
        # Skip if position size is too small
        if position_size <= 0:
            return []
        
        # Create setup
        setup = {
            'type': 'MEAN_REVERSION',
            'direction': trade_direction,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'profit_target': profit_target,
            'position_size': position_size,
            'risk_reward': round(abs(profit_target - entry_price) / abs(entry_price - stop_loss), 2),
            'confidence': self._calculate_setup_confidence(
                market_data, flow_analysis, trade_direction, "CHOPPY"
            ),
            'indicators': self._get_indicator_values(market_data),
            'setup_reason': self._generate_setup_reason(
                symbol, trade_direction, "MEAN_REVERSION", market_data, flow_analysis
            )
        }
        
        setups.append(setup)
        return setups
    
    def _determine_trend_direction(self, market_data):
        """
        Determine the trend direction from market data
        
        Args:
            market_data: DataFrame with OHLCV data
            
        Returns:
            str: 'LONG', 'SHORT', or 'NEUTRAL'
        """
        # Use simple moving averages for trend direction
        short_period = 10
        long_period = 50
        
        # Skip if not enough data
        if len(market_data) < long_period:
            return "NEUTRAL"
        
        # Calculate moving averages
        short_ma = market_data['close'].rolling(window=short_period).mean().iloc[-1]
        long_ma = market_data['close'].rolling(window=long_period).mean().iloc[-1]
        
        # Determine direction based on MA crossover
        if short_ma > long_ma * 1.005:  # Add small buffer (0.5%)
            return "LONG"
        elif short_ma < long_ma * 0.995:  # Add small buffer (0.5%)
            return "SHORT"
        else:
            return "NEUTRAL"
    
    def _calculate_setup_confidence(self, market_data, flow_analysis, direction, market_type):
        """
        Calculate confidence level for a trade setup
        
        Args:
            market_data: DataFrame with OHLCV data
            flow_analysis: Flow analysis result or None
            direction: Trade direction ('LONG' or 'SHORT')
            market_type: Market condition type ('TREND' or 'CHOPPY')
            
        Returns:
            float: Confidence level (0.0 to 1.0)
        """
        confidence = 0.5  # Start with neutral confidence
        
        # Adjust based on volatility
        if len(market_data) >= 20:
            # Calculate normalized volatility
            returns = market_data['close'].pct_change().dropna()
            vol = returns.std() * np.sqrt(252)  # Annualized volatility
            
            # Higher vol = lower confidence
            if vol > 0.4:  # Very high volatility
                confidence -= 0.1
            elif vol < 0.15:  # Low volatility
                confidence += 0.1
        
        # Adjust based on market type and direction
        if market_type == "TREND":
            confidence += 0.1  # Trend setups generally more reliable
            
        # Adjust based on institutional flow if available
        if flow_analysis:
            flow_signal = flow_analysis['signal']
            flow_confidence = flow_analysis['confidence']
            
            # Flow agrees with direction
            if (direction == "LONG" and flow_signal > 0) or (direction == "SHORT" and flow_signal < 0):
                # Weight by flow strength and confidence
                confidence += 0.2 * abs(flow_signal) * flow_confidence
            # Flow disagrees with direction
            elif (direction == "LONG" and flow_signal < 0) or (direction == "SHORT" and flow_signal > 0):
                confidence -= 0.2 * abs(flow_signal) * flow_confidence
        
        # Ensure confidence is in [0, 1] range
        return min(max(confidence, 0.0), 1.0)
    
    def _get_indicator_values(self, market_data):
        """
        Get values for technical indicators
        
        Args:
            market_data: DataFrame with OHLCV data
            
        Returns:
            dict: Dictionary of indicator values
        """
        indicators = {}
        
        # Calculate indicators if we have enough data
        if len(market_data) >= 14:
            # RSI
            delta = market_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))
            
            # MACD (12, 26, 9)
            ema12 = market_data['close'].ewm(span=12).mean()
            ema26 = market_data['close'].ewm(span=26).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9).mean()
            
            indicators['macd'] = macd_line.iloc[-1]
            indicators['macd_signal'] = signal_line.iloc[-1]
            indicators['macd_histogram'] = macd_line.iloc[-1] - signal_line.iloc[-1]
        
        # Add basic indicators
        if len(market_data) > 0:
            current_price = market_data['close'].iloc[-1]
            indicators['current_price'] = current_price
            
            # Add moving averages if we have enough data
            for period in [10, 20, 50, 200]:
                if len(market_data) >= period:
                    indicators[f'ma_{period}'] = market_data['close'].rolling(window=period).mean().iloc[-1]
        
        return indicators
    
    def _generate_setup_reason(self, symbol, direction, setup_type, market_data, flow_analysis):
        """
        Generate a human-readable explanation for the trade setup
        
        Args:
            symbol: Trading symbol
            direction: Trade direction ('LONG' or 'SHORT')
            setup_type: Type of setup ('TREND' or 'MEAN_REVERSION')
            market_data: DataFrame with OHLCV data
            flow_analysis: Flow analysis result or None
            
        Returns:
            str: Setup reason explanation
        """
        reasons = []
        indicators = self._get_indicator_values(market_data)
        
        # Basic setup type explanation
        if setup_type == "TREND":
            reasons.append(f"{symbol} is in a strong {direction.lower()} trend")
            
            # Add MA information if available
            if 'ma_50' in indicators and 'ma_200' in indicators:
                ma50 = indicators['ma_50']
                ma200 = indicators['ma_200']
                if direction == "LONG" and ma50 > ma200:
                    reasons.append(f"The 50-day MA (${ma50:.2f}) is above the 200-day MA (${ma200:.2f})")
                elif direction == "SHORT" and ma50 < ma200:
                    reasons.append(f"The 50-day MA (${ma50:.2f}) is below the 200-day MA (${ma200:.2f})")
                    
        elif setup_type == "MEAN_REVERSION":
            if direction == "LONG":
                reasons.append(f"{symbol} is oversold and likely to revert to the mean")
            else:
                reasons.append(f"{symbol} is overbought and likely to revert to the mean")
            
            # Add RSI information if available
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if direction == "LONG" and rsi < 30:
                    reasons.append(f"RSI is oversold at {rsi:.1f}")
                elif direction == "SHORT" and rsi > 70:
                    reasons.append(f"RSI is overbought at {rsi:.1f}")
        
        # Add flow analysis information if available
        if flow_analysis and abs(flow_analysis['signal']) > 0.3:
            flow_direction = "bullish" if flow_analysis['signal'] > 0 else "bearish"
            flow_strength = "strong" if abs(flow_analysis['signal']) > 0.7 else "moderate"
            
            if (direction == "LONG" and flow_analysis['signal'] > 0) or (direction == "SHORT" and flow_analysis['signal'] < 0):
                reasons.append(f"Institutional flow is {flow_strength} {flow_direction}, supporting this trade")
                
                # Add specific flow details if significant
                if flow_analysis.get('options_signal', 0) > 0.5 and direction == "LONG":
                    reasons.append("Heavy call option buying detected")
                elif flow_analysis.get('options_signal', 0) < -0.5 and direction == "SHORT":
                    reasons.append("Heavy put option buying detected")
                    
                if flow_analysis.get('dark_pool_signal', 0) > 0.5 and direction == "LONG":
                    reasons.append("Dark pool buying detected")
                elif flow_analysis.get('dark_pool_signal', 0) < -0.5 and direction == "SHORT":
                    reasons.append("Dark pool selling detected")
            
        return " | ".join(reasons) 