"""
AI Risk Manager Module

This module provides AI-driven risk management capabilities:
- Adaptive stop-loss and profit target calculation based on market volatility
- AI-powered position sizing based on account balance and risk tolerance
- Dynamic risk assessment for trading opportunities
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AIRiskManager:
    """
    Provides AI-powered risk management capabilities
    
    This class:
    - Calculates adaptive stop-loss levels based on market volatility
    - Determines position sizing based on risk tolerance and market conditions
    - Evaluates overall portfolio risk
    """
    
    def __init__(self, config, risk_manager=None):
        """
        Initialize with configuration
        
        Args:
            config: Configuration dictionary or object
            risk_manager: Optional RiskManager instance for integration
        """
        self.config = config
        self.risk_manager = risk_manager
        
        # Get AI risk config
        if hasattr(config, 'get'):
            # It's a config object
            self.ai_risk_config = config.get("ai_risk_management", {})
        else:
            # It's a dictionary
            self.ai_risk_config = config.get("ai_risk_management", {}) if isinstance(config, dict) else {}
        
        # Initialize parameters
        self.volatility_multiplier = self.ai_risk_config.get("volatility_multiplier", 2.0)
        self.risk_tolerance_factor = self.ai_risk_config.get("risk_tolerance_factor", 1.0)
        self.max_position_size_percent = self.ai_risk_config.get("max_position_size_percent", 5.0)
        self.risk_per_trade_percent = self.ai_risk_config.get("risk_per_trade_percent", 1.0)
        self.use_gpt_for_risk = self.ai_risk_config.get("use_gpt_for_risk", True)
        
        # GPT API setup
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if self.use_gpt_for_risk and not self.openrouter_api_key:
            logger.warning("OpenRouter API key not found. GPT risk analysis will not be available.")
            self.use_gpt_for_risk = False
        
        # Initialize OpenAI client if API key is available
        if self.use_gpt_for_risk and self.openrouter_api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_api_key,
            )
        else:
            self.client = None
        
        logger.info("AI Risk Manager initialized")
    
    def calculate_adaptive_stop_loss(self, symbol, entry_price, direction, market_data):
        """
        Calculate adaptive stop loss based on market volatility
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price for the trade
            direction: Trade direction ('LONG' or 'SHORT')
            market_data: Market data DataFrame
            
        Returns:
            float: Calculated stop loss price
        """
        try:
            # Calculate ATR for volatility measurement
            atr = self._calculate_atr(market_data)
            
            # Default stop loss (1% of entry price)
            default_stop = entry_price * 0.99 if direction == 'LONG' else entry_price * 1.01
            
            if atr == 0:
                logger.warning(f"Could not calculate ATR for {symbol}, using default stop")
                return default_stop
            
            # Calculate adaptive stop loss based on volatility
            stop_distance = atr * self.volatility_multiplier
            
            # Apply direction-specific calculation
            if direction == 'LONG':
                stop_loss = entry_price - stop_distance
            else:
                stop_loss = entry_price + stop_distance
            
            logger.debug(f"Calculated adaptive stop loss for {symbol}: {stop_loss:.4f} (ATR: {atr:.4f})")
            return stop_loss
            
        except Exception as e:
            logger.error(f"Error calculating adaptive stop loss for {symbol}: {str(e)}")
            # Fallback to default
            return entry_price * 0.99 if direction == 'LONG' else entry_price * 1.01
    
    def calculate_profit_target(self, symbol, entry_price, stop_loss, direction, market_data, target_risk_reward=2.0):
        """
        Calculate profit target based on risk-reward ratio and support/resistance levels
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price for the trade
            stop_loss: Stop loss price
            direction: Trade direction ('LONG' or 'SHORT')
            market_data: Market data DataFrame
            target_risk_reward: Target risk-reward ratio
            
        Returns:
            float: Calculated profit target price
        """
        try:
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            
            # Calculate target based on risk-reward ratio
            if direction == 'LONG':
                base_target = entry_price + (risk_per_share * target_risk_reward)
            else:
                base_target = entry_price - (risk_per_share * target_risk_reward)
            
            # If GPT insights are enabled, we could enhance with support/resistance levels
            if self.use_gpt_for_risk and self.client:
                try:
                    key_levels = self._get_key_price_levels(symbol, market_data)
                    
                    if key_levels and 'resistance' in key_levels and 'support' in key_levels:
                        if direction == 'LONG':
                            # Find the nearest resistance level above entry
                            resistance_levels = [r for r in key_levels['resistance'] if r > entry_price]
                            if resistance_levels:
                                nearest_resistance = min(resistance_levels)
                                # Use either the base target or resistance, whichever is closer
                                if nearest_resistance < base_target:
                                    logger.info(f"Adjusting profit target to resistance level: {nearest_resistance:.4f}")
                                    return nearest_resistance
                        else:
                            # Find the nearest support level below entry
                            support_levels = [s for s in key_levels['support'] if s < entry_price]
                            if support_levels:
                                nearest_support = max(support_levels)
                                # Use either the base target or support, whichever is closer
                                if nearest_support > base_target:
                                    logger.info(f"Adjusting profit target to support level: {nearest_support:.4f}")
                                    return nearest_support
                except Exception as gpt_error:
                    logger.error(f"Error getting key levels for profit target: {str(gpt_error)}")
            
            return base_target
            
        except Exception as e:
            logger.error(f"Error calculating profit target for {symbol}: {str(e)}")
            # Fallback to default 2:1 reward-risk ratio
            if direction == 'LONG':
                return entry_price * 1.02
            else:
                return entry_price * 0.98
    
    def calculate_position_size(self, account_balance, entry_price, stop_loss, symbol, market_data=None, risk_profile='moderate'):
        """
        Calculate optimal position size based on account balance and risk tolerance
        
        Args:
            account_balance: Available account balance
            entry_price: Entry price for the trade
            stop_loss: Stop loss price
            symbol: Trading symbol
            market_data: Optional market data for volatility assessment
            risk_profile: Risk profile ('conservative', 'moderate', 'aggressive')
            
        Returns:
            int: Recommended position size in shares
        """
        try:
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            if risk_per_share == 0:
                logger.warning(f"Invalid risk (stop loss too close to entry) for {symbol}")
                return 0
            
            # Adjust risk percentage based on risk profile
            risk_factor = 0.5  # Conservative
            if risk_profile == 'moderate':
                risk_factor = 1.0
            elif risk_profile == 'aggressive':
                risk_factor = 1.5
            
            # Calculate base risk amount
            risk_percent = self.risk_per_trade_percent * risk_factor * self.risk_tolerance_factor
            risk_amount = account_balance * (risk_percent / 100)
            
            # Calculate base position size
            base_position_size = int(risk_amount / risk_per_share)
            
            # Apply volatility adjustment if market data is available
            volatility_adjustment = 1.0
            if market_data is not None:
                volatility = self._calculate_volatility(market_data)
                
                # Adjust position size based on volatility
                if volatility > 0.03:  # High volatility
                    volatility_adjustment = 0.7
                elif volatility < 0.01:  # Low volatility
                    volatility_adjustment = 1.2
                
                logger.debug(f"Volatility adjustment for {symbol}: {volatility_adjustment:.2f} (volatility: {volatility:.4f})")
            
            # Apply adjustment
            adjusted_position_size = int(base_position_size * volatility_adjustment)
            
            # Check against maximum position size
            max_position_value = account_balance * (self.max_position_size_percent / 100)
            max_shares = int(max_position_value / entry_price)
            
            if adjusted_position_size > max_shares:
                logger.info(f"Position size reduced from {adjusted_position_size} to {max_shares} shares due to max position limit")
                adjusted_position_size = max_shares
            
            return adjusted_position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {str(e)}")
            return 0
    
    def evaluate_trade_risk(self, trade_setup, market_data, account_balance):
        """
        Provide comprehensive risk evaluation for a trade setup
        
        Args:
            trade_setup: Trade setup dictionary
            market_data: Market data DataFrame
            account_balance: Current account balance
            
        Returns:
            dict: Risk assessment with various metrics
        """
        try:
            symbol = trade_setup.get('symbol')
            entry_price = trade_setup.get('entry_price')
            direction = trade_setup.get('direction')
            
            if not all([symbol, entry_price, direction]):
                logger.error("Trade setup missing required fields")
                return {'risk_score': 0, 'recommendation': 'REJECT', 'reason': 'Incomplete trade setup'}
            
            # Calculate adaptive stop loss if not provided
            stop_loss = trade_setup.get('stop_loss')
            if not stop_loss:
                stop_loss = self.calculate_adaptive_stop_loss(symbol, entry_price, direction, market_data)
            
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            
            # Calculate position size
            position_size = self.calculate_position_size(
                account_balance, entry_price, stop_loss, symbol, market_data
            )
            
            # Calculate total risk amount
            risk_amount = position_size * risk_per_share
            risk_percent = (risk_amount / account_balance) * 100
            
            # Calculate profit target if not provided
            profit_target = trade_setup.get('profit_target')
            if not profit_target:
                profit_target = self.calculate_profit_target(
                    symbol, entry_price, stop_loss, direction, market_data
                )
            
            # Calculate reward per share and risk-reward ratio
            reward_per_share = abs(profit_target - entry_price)
            risk_reward_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0
            
            # Assess market volatility
            volatility = self._calculate_volatility(market_data)
            volatility_assessment = 'NORMAL'
            if volatility > 0.03:
                volatility_assessment = 'HIGH'
            elif volatility < 0.01:
                volatility_assessment = 'LOW'
            
            # Calculate base risk score (0-100)
            risk_score = 0
            
            # Factor 1: Risk-reward ratio (0-40 points)
            if risk_reward_ratio >= 3:
                risk_score += 40
            elif risk_reward_ratio >= 2:
                risk_score += 30
            elif risk_reward_ratio >= 1.5:
                risk_score += 20
            elif risk_reward_ratio >= 1:
                risk_score += 10
            
            # Factor 2: Risk percent of account (0-30 points)
            if risk_percent <= 0.5:
                risk_score += 30
            elif risk_percent <= 1.0:
                risk_score += 20
            elif risk_percent <= 2.0:
                risk_score += 10
            
            # Factor 3: Volatility (0-20 points)
            if volatility_assessment == 'NORMAL':
                risk_score += 20
            elif volatility_assessment == 'LOW':
                risk_score += 15
            else:  # HIGH
                risk_score += 5
            
            # Factor 4: Setup quality (0-10 points) - if available
            setup_quality = trade_setup.get('ai_setup_quality', 0.5)
            risk_score += int(setup_quality * 10)
            
            # Determine recommendation
            recommendation = 'ACCEPT'
            reason = 'Trade meets risk criteria'
            
            if risk_score < 40:
                recommendation = 'REJECT'
                reason = 'Risk score too low'
            elif risk_score < 60:
                recommendation = 'CAUTION'
                reason = 'Moderate risk, proceed with caution'
            
            # Check if risk percent exceeds maximum
            if risk_percent > self.risk_per_trade_percent * 2:
                recommendation = 'REJECT'
                reason = f'Risk percent too high: {risk_percent:.2f}%'
            
            # Check if risk-reward ratio is acceptable
            if risk_reward_ratio < 1.0:
                recommendation = 'REJECT'
                reason = f'Risk-reward ratio too low: {risk_reward_ratio:.2f}'
            
            # Complete assessment
            assessment = {
                'risk_score': risk_score,
                'recommendation': recommendation,
                'reason': reason,
                'risk_amount': risk_amount,
                'risk_percent': risk_percent,
                'risk_reward_ratio': risk_reward_ratio,
                'position_size': position_size,
                'stop_loss': stop_loss,
                'profit_target': profit_target,
                'volatility_assessment': volatility_assessment,
                'current_volatility': volatility
            }
            
            logger.info(f"Risk assessment for {symbol}: score={risk_score}, recommendation={recommendation}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error evaluating trade risk: {str(e)}")
            return {
                'risk_score': 0,
                'recommendation': 'REJECT',
                'reason': f'Error in risk assessment: {str(e)}',
                'error': str(e)
            }
    
    def _calculate_atr(self, market_data, period=14):
        """Calculate Average True Range from market data"""
        try:
            if len(market_data) < period + 1:
                return 0
                
            high = market_data['high'].values
            low = market_data['low'].values
            close = market_data['close'].values
            
            # Calculate true range
            tr1 = np.abs(high[1:] - low[1:])
            tr2 = np.abs(high[1:] - close[:-1])
            tr3 = np.abs(low[1:] - close[:-1])
            
            tr = np.maximum(np.maximum(tr1, tr2), tr3)
            
            # Calculate ATR
            atr = np.mean(tr[-period:])
            return atr
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {str(e)}")
            return 0
    
    def _calculate_volatility(self, market_data, period=20):
        """Calculate price volatility from market data"""
        try:
            if len(market_data) < period:
                return 0
                
            # Use close prices for volatility calculation
            close = market_data['close'].values[-period:]
            
            # Calculate returns
            returns = np.diff(close) / close[:-1]
            
            # Calculate volatility (standard deviation of returns)
            volatility = np.std(returns)
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating volatility: {str(e)}")
            return 0
    
    def _get_key_price_levels(self, symbol, market_data):
        """Get key support and resistance levels using GPT"""
        if not self.client:
            return None
            
        try:
            # Prepare market data for the prompt
            recent_data = market_data.tail(20).reset_index()
            
            data_summary = f"Market data for {symbol}:\n"
            for _, row in recent_data.iterrows():
                data_summary += f"Date: {row['timestamp']} | Open: {row['open']:.2f} | High: {row['high']:.2f} | Low: {row['low']:.2f} | Close: {row['close']:.2f} | Volume: {row['volume']}\n"
            
            # Create prompt for key levels analysis
            prompt = f"""
            You are a professional market analysis assistant with expertise in price action analysis.
            
            Analyze the following market data for {symbol} and identify the 3 most important support and resistance levels:
            
            {data_summary}
            
            Return only a JSON object with the following structure:
            {{
                "support": [price_level1, price_level2, price_level3],
                "resistance": [price_level1, price_level2, price_level3]
            }}
            
            The support levels should be sorted from lowest to highest price.
            The resistance levels should be sorted from lowest to highest price.
            Only include the numeric values (no explanations) and ensure all values are numbers, not strings.
            """
            
            # Call GPT API
            response = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "ai-trading-bot.app",
                    "X-Title": "AI Trading Bot",
                },
                model="anthropic/claude-3.7-sonnet",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                insight_text = response.choices[0].message.content
                
                # Parse JSON response
                try:
                    # Extract JSON content
                    if '```json' in insight_text and '```' in insight_text:
                        json_text = insight_text.split('```json')[1].split('```')[0].strip()
                    elif '```' in insight_text:
                        json_text = insight_text.split('```')[1].split('```')[0].strip()
                    else:
                        json_text = insight_text
                        
                    return json.loads(json_text)
                except Exception as parse_error:
                    logger.error(f"Error parsing GPT response for key levels: {str(parse_error)}")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting key price levels: {str(e)}")
            return None
    
    def update_config(self, new_config):
        """Update configuration parameters"""
        if isinstance(new_config, dict):
            if 'ai_risk_management' in new_config:
                self.ai_risk_config.update(new_config['ai_risk_management'])
            else:
                self.ai_risk_config.update(new_config)
                
            # Update parameters
            self.volatility_multiplier = self.ai_risk_config.get("volatility_multiplier", 2.0)
            self.risk_tolerance_factor = self.ai_risk_config.get("risk_tolerance_factor", 1.0)
            self.max_position_size_percent = self.ai_risk_config.get("max_position_size_percent", 5.0)
            self.risk_per_trade_percent = self.ai_risk_config.get("risk_per_trade_percent", 1.0)
            self.use_gpt_for_risk = self.ai_risk_config.get("use_gpt_for_risk", True)
            
            logger.info("AI Risk Manager configuration updated") 