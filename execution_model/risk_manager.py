"""
Risk Manager Module

This module handles risk management for trading operations,
including position sizing, risk per trade, and portfolio exposure management.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from .ai_risk_manager import AIRiskManager

logger = logging.getLogger(__name__)

class RiskManager:
    """
    Manages risk for trading operations
    
    This class is responsible for determining appropriate position sizes,
    monitoring portfolio risk, and enforcing risk limits.
    """
    
    def __init__(self, config=None):
        """
        Initialize with optional configuration
        
        Args:
            config: Optional configuration dictionary with risk parameters
        """
        self.config = config or {}
        
        # Set default risk parameters
        self.max_position_size_percent = self.config.get('max_position_size_percent', 5.0)
        self.max_portfolio_risk_percent = self.config.get('max_portfolio_risk_percent', 2.0)
        self.max_single_trade_risk_percent = self.config.get('max_single_trade_risk_percent', 1.0)
        self.max_sector_exposure_percent = self.config.get('max_sector_exposure_percent', 20.0)
        self.max_correlated_exposure_percent = self.config.get('max_correlated_exposure_percent', 15.0)
        self.default_stop_loss_percent = self.config.get('default_stop_loss_percent', 2.0)
        self.max_trades_per_day = self.config.get('max_trades_per_day', 5)
        self.position_scaling_factors = self.config.get('position_scaling_factors', {
            'high_volatility': 0.7,
            'low_volatility': 1.2,
            'strong_trend': 1.2,
            'weak_trend': 0.8,
            'oversold': 1.1,
            'overbought': 0.9
        })
        
        # Initialize state
        self.portfolio_value = self.config.get('initial_portfolio_value', 100000.0)
        self.current_positions = {}
        self.trade_history = []
        self.daily_trade_count = 0
        self.last_trade_date = None
        
        # Initialize AI Risk Manager if enabled
        self.use_ai_risk_management = self.config.get('use_ai_risk_management', False)
        if self.use_ai_risk_management:
            self.ai_risk_manager = AIRiskManager(config, self)
            logger.info("AI Risk Manager initialized")
        else:
            self.ai_risk_manager = None
        
        logger.info("Risk Manager initialized with max portfolio risk: {}%".format(
            self.max_portfolio_risk_percent))
        
    def update_config(self, config):
        """
        Update the configuration
        
        Args:
            config: New configuration dictionary
        """
        self.config.update(config)
        
        # Update risk parameters
        self.max_position_size_percent = self.config.get('max_position_size_percent', 5.0)
        self.max_portfolio_risk_percent = self.config.get('max_portfolio_risk_percent', 2.0)
        self.max_single_trade_risk_percent = self.config.get('max_single_trade_risk_percent', 1.0)
        self.max_sector_exposure_percent = self.config.get('max_sector_exposure_percent', 20.0)
        self.max_correlated_exposure_percent = self.config.get('max_correlated_exposure_percent', 15.0)
        self.default_stop_loss_percent = self.config.get('default_stop_loss_percent', 2.0)
        self.max_trades_per_day = self.config.get('max_trades_per_day', 5)
        self.position_scaling_factors = self.config.get('position_scaling_factors', {
            'high_volatility': 0.7,
            'low_volatility': 1.2,
            'strong_trend': 1.2,
            'weak_trend': 0.8,
            'oversold': 1.1,
            'overbought': 0.9
        })
        
        # Update AI Risk Manager settings
        self.use_ai_risk_management = self.config.get('use_ai_risk_management', False)
        if self.use_ai_risk_management:
            if self.ai_risk_manager:
                # Update existing AI Risk Manager
                self.ai_risk_manager.update_config(config)
            else:
                # Create new AI Risk Manager
                self.ai_risk_manager = AIRiskManager(config, self)
                logger.info("AI Risk Manager initialized")
        
        logger.info("Risk Manager configuration updated")
        
    def update_portfolio_value(self, new_value):
        """
        Update the portfolio value
        
        Args:
            new_value: New portfolio value
        """
        self.portfolio_value = new_value
        logger.info(f"Portfolio value updated to {new_value}")
        
    def update_positions(self, positions):
        """
        Update current positions
        
        Args:
            positions: Dictionary of current positions
                Format: {'SYMBOL': {'quantity': 100, 'avg_price': 150.0, ...}, ...}
        """
        self.current_positions = positions
        logger.debug(f"Positions updated: {len(positions)} active positions")
        
    def calculate_position_size(self, symbol, entry_price, stop_loss_price=None, 
                                market_condition=None, setup_quality=None):
        """
        Calculate the appropriate position size for a trade
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price for the trade
            stop_loss_price: Optional stop loss price (if None, uses default_stop_loss_percent)
            market_condition: Optional market condition analysis for the symbol
            setup_quality: Optional setup quality score (0-1)
            
        Returns:
            dict: Position sizing information with details
        """
        try:
            # Check if we've reached the maximum number of trades for the day
            current_date = datetime.now().date()
            if self.last_trade_date != current_date:
                self.last_trade_date = current_date
                self.daily_trade_count = 0
            
            if self.daily_trade_count >= self.max_trades_per_day:
                logger.warning(f"Maximum trades per day ({self.max_trades_per_day}) reached")
                return {
                    'shares': 0,
                    'position_value': 0,
                    'risk_amount': 0,
                    'risk_percent': 0,
                    'stop_loss_price': stop_loss_price,
                    'reason': 'Max daily trades reached',
                    'can_trade': False
                }
            
            # If AI Risk Management is enabled, use it for position sizing
            if self.use_ai_risk_management and self.ai_risk_manager and market_condition is not None:
                # Get market data from market condition if available
                market_data = market_condition.get('market_data', None)
                risk_profile = self.config.get('risk_profile', 'moderate')
                
                # Determine risk profile from setup quality if available
                if setup_quality is not None:
                    if setup_quality > 0.8:
                        risk_profile = 'aggressive'
                    elif setup_quality < 0.4:
                        risk_profile = 'conservative'
                
                # If we have market data, use AI position sizing
                if market_data is not None:
                    # Get AI-calculated position size
                    shares = self.ai_risk_manager.calculate_position_size(
                        self.portfolio_value, 
                        entry_price, 
                        stop_loss_price, 
                        symbol, 
                        market_data, 
                        risk_profile
                    )
                    
                    # Calculate position value
                    position_value = shares * entry_price
                    
                    # Calculate risk amount
                    risk_per_share = abs(entry_price - stop_loss_price)
                    risk_amount = shares * risk_per_share
                    risk_percent = (risk_amount / self.portfolio_value) * 100
                    
                    # Determine if we can trade
                    can_trade = (shares > 0 and position_value > 0)
                    
                    # Return result
                    result = {
                        'shares': shares,
                        'position_value': position_value,
                        'risk_amount': risk_amount,
                        'risk_percent': risk_percent,
                        'stop_loss_price': stop_loss_price,
                        'scaling_factor': 1.0,  # AI Risk Manager handles scaling internally
                        'can_trade': can_trade,
                        'ai_enhanced': True
                    }
                    
                    # If we can trade, increment daily trade count
                    if can_trade:
                        self.daily_trade_count += 1
                        
                    return result
                    
            # Traditional position sizing logic if AI is not used
            
            # Calculate risk amount based on portfolio value
            max_risk_amount = self.portfolio_value * (self.max_single_trade_risk_percent / 100)
            
            # Calculate risk per share
            if stop_loss_price is None:
                # Use default stop loss percentage
                stop_loss_percent = self.default_stop_loss_percent
                stop_loss_price = entry_price * (1 - stop_loss_percent / 100)
                
            risk_per_share = abs(entry_price - stop_loss_price)
            
            # Basic position size calculation based on risk
            if risk_per_share > 0:
                shares = max_risk_amount / risk_per_share
            else:
                logger.warning(f"Invalid risk per share for {symbol}: {risk_per_share}")
                shares = 0
                
            # Apply position scaling based on market conditions
            scaling_factor = 1.0
            
            if market_condition is not None:
                # Adjust based on volatility
                if market_condition.get('volatility', {}).get('is_high_volatility', False):
                    scaling_factor *= self.position_scaling_factors.get('high_volatility', 0.7)
                elif market_condition.get('volatility', {}).get('is_low_volatility', False):
                    scaling_factor *= self.position_scaling_factors.get('low_volatility', 1.2)
                    
                # Adjust based on trend strength
                if market_condition.get('trend', {}).get('is_trending', False):
                    trend_strength = market_condition.get('trend', {}).get('strength', 0)
                    if trend_strength > 0.7:  # Strong trend
                        scaling_factor *= self.position_scaling_factors.get('strong_trend', 1.2)
                    elif trend_strength < 0.3:  # Weak trend
                        scaling_factor *= self.position_scaling_factors.get('weak_trend', 0.8)
                        
                # Adjust based on momentum (RSI)
                rsi = market_condition.get('momentum', {}).get('rsi', 50)
                if rsi < 30:  # Oversold
                    scaling_factor *= self.position_scaling_factors.get('oversold', 1.1)
                elif rsi > 70:  # Overbought
                    scaling_factor *= self.position_scaling_factors.get('overbought', 0.9)
            
            # Adjust based on setup quality if provided
            if setup_quality is not None:
                scaling_factor *= (0.5 + setup_quality / 2)  # Scale from 0.5x to 1.0x based on quality
                
            # Apply scaling factor
            shares = shares * scaling_factor
            
            # Round down to whole shares
            shares = int(shares)
            
            # Calculate position value
            position_value = shares * entry_price
            
            # Check if position size exceeds max percentage of portfolio
            max_position_value = self.portfolio_value * (self.max_position_size_percent / 100)
            if position_value > max_position_value:
                shares = int(max_position_value / entry_price)
                position_value = shares * entry_price
                
            # Check current portfolio exposure and risk
            current_risk = self.calculate_current_portfolio_risk()
            available_risk = (self.max_portfolio_risk_percent / 100) - current_risk
            
            # Calculate risk for this trade
            trade_risk_percent = (shares * risk_per_share) / self.portfolio_value
            
            # Check if this trade would exceed max portfolio risk
            if trade_risk_percent > available_risk:
                # Reduce position size to fit within available risk
                adjusted_shares = int(available_risk * self.portfolio_value / risk_per_share)
                shares = adjusted_shares
                position_value = shares * entry_price
                trade_risk_percent = (shares * risk_per_share) / self.portfolio_value
                
            # Final risk amount
            risk_amount = shares * risk_per_share
            
            # Determine if we can trade
            can_trade = (shares > 0 and position_value > 0)
            
            # Prepare position size result
            result = {
                'shares': shares,
                'position_value': position_value,
                'risk_amount': risk_amount,
                'risk_percent': trade_risk_percent * 100,  # Convert to percentage
                'stop_loss_price': stop_loss_price,
                'scaling_factor': scaling_factor,
                'can_trade': can_trade,
                'ai_enhanced': False
            }
            
            # If we can trade, increment daily trade count
            if can_trade:
                self.daily_trade_count += 1
                
            return result
            
        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {str(e)}")
            return {
                'shares': 0,
                'position_value': 0,
                'risk_amount': 0,
                'risk_percent': 0,
                'stop_loss_price': stop_loss_price if stop_loss_price else 0,
                'reason': f'Error: {str(e)}',
                'can_trade': False,
                'ai_enhanced': False
            }
    
    def calculate_current_portfolio_risk(self):
        """
        Calculate the current portfolio risk based on open positions
        
        Returns:
            float: Current portfolio risk as a decimal (e.g., 0.05 for 5%)
        """
        total_risk = 0.0
        
        for symbol, position in self.current_positions.items():
            # If the position has stop loss information, use it
            if 'stop_loss' in position and position.get('quantity', 0) > 0:
                current_price = position.get('current_price', position.get('avg_price', 0))
                stop_loss = position.get('stop_loss')
                risk_per_share = abs(current_price - stop_loss)
                position_risk = position.get('quantity', 0) * risk_per_share
                position_risk_percent = position_risk / self.portfolio_value
                total_risk += position_risk_percent
                
        return total_risk
        
    def check_portfolio_exposure(self, symbol, position_value):
        """
        Check if adding a new position would exceed portfolio exposure limits
        
        Args:
            symbol: Symbol to check
            position_value: Value of the position to add
            
        Returns:
            dict: Exposure check results
        """
        try:
            # Calculate total portfolio exposure
            total_exposure = sum(
                pos.get('market_value', pos.get('quantity', 0) * pos.get('current_price', pos.get('avg_price', 0)))
                for pos in self.current_positions.values()
            )
            
            current_exposure_percent = (total_exposure / self.portfolio_value) * 100
            new_exposure_percent = ((total_exposure + position_value) / self.portfolio_value) * 100
            
            # Get sector information for the symbol (would need sector data integration)
            sector = self.get_symbol_sector(symbol)
            
            # Calculate sector exposure
            sector_exposure = sum(
                pos.get('market_value', pos.get('quantity', 0) * pos.get('current_price', pos.get('avg_price', 0)))
                for sym, pos in self.current_positions.items()
                if self.get_symbol_sector(sym) == sector
            )
            
            sector_exposure_percent = (sector_exposure / self.portfolio_value) * 100
            new_sector_exposure_percent = ((sector_exposure + position_value) / self.portfolio_value) * 100
            
            # Check exposure limits
            exposure_limit_exceeded = new_exposure_percent > self.config.get('max_portfolio_exposure_percent', 80)
            sector_limit_exceeded = new_sector_exposure_percent > self.max_sector_exposure_percent
            
            return {
                'current_exposure_percent': current_exposure_percent,
                'new_exposure_percent': new_exposure_percent,
                'sector': sector,
                'current_sector_exposure_percent': sector_exposure_percent,
                'new_sector_exposure_percent': new_sector_exposure_percent,
                'exposure_limit_exceeded': exposure_limit_exceeded,
                'sector_limit_exceeded': sector_limit_exceeded,
                'can_add_position': not (exposure_limit_exceeded or sector_limit_exceeded)
            }
            
        except Exception as e:
            logger.error(f"Error checking portfolio exposure for {symbol}: {str(e)}")
            return {
                'error': str(e),
                'can_add_position': False
            }
    
    def get_symbol_sector(self, symbol):
        """
        Get sector for a symbol
        
        This would typically integrate with a data source that provides sector information.
        For now, we'll return a placeholder.
        
        Args:
            symbol: Symbol to get sector for
            
        Returns:
            str: Sector name
        """
        # This would be replaced with actual sector data lookup
        # Placeholder implementation
        sectors = self.config.get('symbol_sectors', {})
        return sectors.get(symbol, 'Unknown')
    
    def calculate_correlation_exposure(self, symbol, correlation_matrix=None):
        """
        Calculate exposure to correlated assets
        
        Args:
            symbol: Symbol to check correlation exposure for
            correlation_matrix: Optional correlation matrix for symbols
            
        Returns:
            float: Exposure to assets correlated with the given symbol
        """
        if correlation_matrix is None or symbol not in correlation_matrix:
            return 0.0
            
        correlated_exposure = 0.0
        
        for pos_symbol, position in self.current_positions.items():
            if pos_symbol in correlation_matrix[symbol]:
                correlation = correlation_matrix[symbol][pos_symbol]
                if abs(correlation) > 0.7:  # High correlation threshold
                    pos_value = position.get('market_value', 
                                          position.get('quantity', 0) * 
                                          position.get('current_price', position.get('avg_price', 0)))
                    correlated_exposure += pos_value
                    
        return correlated_exposure / self.portfolio_value if self.portfolio_value > 0 else 0.0
    
    def get_portfolio_statistics(self):
        """
        Get portfolio risk statistics
        
        Returns:
            dict: Portfolio statistics
        """
        try:
            # Calculate total exposure
            total_value = sum(
                pos.get('market_value', pos.get('quantity', 0) * pos.get('current_price', pos.get('avg_price', 0)))
                for pos in self.current_positions.values()
            )
            
            # Calculate exposure percentage
            exposure_percent = (total_value / self.portfolio_value) * 100 if self.portfolio_value > 0 else 0
            
            # Calculate total risk
            total_risk = self.calculate_current_portfolio_risk() * 100  # Convert to percentage
            
            # Get sector exposure
            sector_exposure = {}
            for symbol, position in self.current_positions.items():
                sector = self.get_symbol_sector(symbol)
                position_value = position.get('market_value', 
                                           position.get('quantity', 0) * 
                                           position.get('current_price', position.get('avg_price', 0)))
                
                if sector in sector_exposure:
                    sector_exposure[sector] += position_value
                else:
                    sector_exposure[sector] = position_value
                    
            # Convert sector exposure to percentages
            sector_exposure_percent = {
                sector: (value / self.portfolio_value) * 100 if self.portfolio_value > 0 else 0
                for sector, value in sector_exposure.items()
            }
            
            return {
                'portfolio_value': self.portfolio_value,
                'total_exposure': total_value,
                'exposure_percent': exposure_percent,
                'total_risk_percent': total_risk,
                'max_risk_percent': self.max_portfolio_risk_percent,
                'available_risk_percent': self.max_portfolio_risk_percent - total_risk,
                'num_positions': len(self.current_positions),
                'sector_exposure_percent': sector_exposure_percent,
                'daily_trades': self.daily_trade_count,
                'max_daily_trades': self.max_trades_per_day
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio statistics: {str(e)}")
            return {
                'error': str(e),
                'portfolio_value': self.portfolio_value
            }
    
    def record_trade(self, trade_data):
        """
        Record a trade in the trade history
        
        Args:
            trade_data: Trade data to record
        """
        # Add timestamp if not present
        if 'timestamp' not in trade_data:
            trade_data['timestamp'] = datetime.now().isoformat()
            
        self.trade_history.append(trade_data)
        logger.debug(f"Trade recorded for {trade_data.get('symbol')}")
        
    def calculate_stop_loss(self, symbol, entry_price, direction, market_condition=None, atr_multiplier=2.0):
        """
        Calculate an appropriate stop loss price based on volatility and market conditions
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price for the trade
            direction: Trade direction ('long' or 'short')
            market_condition: Optional market condition analysis for the symbol
            atr_multiplier: ATR multiplier for stop loss calculation
            
        Returns:
            float: Calculated stop loss price
        """
        try:
            # Check if AI Risk Management is enabled
            if self.use_ai_risk_management and self.ai_risk_manager and market_condition is not None:
                # Get market data from market condition if available
                market_data = market_condition.get('market_data', None)
                
                # If market data is available, use AI-enhanced stop loss
                if market_data is not None:
                    logger.debug(f"Using AI-enhanced stop loss calculation for {symbol}")
                    
                    # Normalize direction format (LONG/long/SHORT/short)
                    normalized_direction = direction.upper() if isinstance(direction, str) else direction
                    
                    return self.ai_risk_manager.calculate_adaptive_stop_loss(
                        symbol, entry_price, normalized_direction, market_data
                    )
            
            # Default stop loss using percent
            default_stop_loss_price = (
                entry_price * (1 - self.default_stop_loss_percent / 100) 
                if direction.lower() == 'long' 
                else entry_price * (1 + self.default_stop_loss_percent / 100)
            )
            
            # If no market condition data available, use default
            if market_condition is None:
                return default_stop_loss_price
                
            # Calculate stop loss based on ATR if available
            atr = market_condition.get('volatility', {}).get('atr', 0)
            
            if atr > 0:
                # Use ATR-based stop loss
                stop_loss_distance = atr * atr_multiplier
                stop_loss_price = (
                    entry_price - stop_loss_distance 
                    if direction.lower() == 'long' 
                    else entry_price + stop_loss_distance
                )
                
                # Use the tighter of ATR-based and percent-based stop losses
                if direction.lower() == 'long':
                    return max(stop_loss_price, default_stop_loss_price)
                else:
                    return min(stop_loss_price, default_stop_loss_price)
            else:
                # Fallback to default stop loss
                return default_stop_loss_price
                
        except Exception as e:
            logger.error(f"Error calculating stop loss for {symbol}: {str(e)}")
            # Fallback to default stop loss
            return entry_price * (1 - self.default_stop_loss_percent / 100) if direction.lower() == 'long' else entry_price * (1 + self.default_stop_loss_percent / 100)
    
    def adjust_stop_loss(self, symbol, current_price, direction, current_stop_loss, market_condition=None):
        """
        Adjust stop loss for an existing position (e.g., trailing stop)
        
        Args:
            symbol: Trading symbol
            current_price: Current price
            direction: Trade direction ('long' or 'short')
            current_stop_loss: Current stop loss price
            market_condition: Optional market condition analysis for the symbol
            
        Returns:
            float: Adjusted stop loss price
        """
        try:
            # Get ATR if available
            atr = 0
            if market_condition is not None:
                atr = market_condition.get('volatility', {}).get('atr', 0)
                
            # Set trailing stop distance based on ATR or default percentage
            if atr > 0:
                # Use ATR-based trailing distance
                trailing_distance = atr * self.config.get('trailing_stop_atr_multiplier', 2.0)
            else:
                # Use percent-based trailing distance
                trailing_percent = self.config.get('trailing_stop_percent', 1.0)
                trailing_distance = current_price * (trailing_percent / 100)
                
            # Calculate new stop loss price based on trailing distance
            if direction.lower() == 'long':
                new_stop_loss = current_price - trailing_distance
                # Only move stop loss up, never down
                return max(new_stop_loss, current_stop_loss)
            else:
                new_stop_loss = current_price + trailing_distance
                # Only move stop loss down, never up
                return min(new_stop_loss, current_stop_loss)
                
        except Exception as e:
            logger.error(f"Error adjusting stop loss for {symbol}: {str(e)}")
            return current_stop_loss  # Keep current stop loss if error 

    def evaluate_trade_risk(self, trade_setup, market_data=None):
        """
        Evaluate the risk for a potential trade
        
        Args:
            trade_setup: Trade setup dictionary
            market_data: Optional market data for the symbol
            
        Returns:
            dict: Risk evaluation results
        """
        try:
            # If AI Risk Management is enabled, use it for risk evaluation
            if self.use_ai_risk_management and self.ai_risk_manager:
                if market_data is not None:
                    logger.debug(f"Using AI risk evaluation for {trade_setup.get('symbol')}")
                    return self.ai_risk_manager.evaluate_trade_risk(
                        trade_setup, market_data, self.portfolio_value
                    )
            
            # Simple risk evaluation if AI is not available
            symbol = trade_setup.get('symbol')
            entry_price = trade_setup.get('entry_price')
            direction = trade_setup.get('direction')
            stop_loss = trade_setup.get('stop_loss')
            profit_target = trade_setup.get('profit_target')
            
            # Validate required fields
            if not all([symbol, entry_price, direction]):
                return {
                    'risk_score': 0,
                    'recommendation': 'REJECT',
                    'reason': 'Incomplete trade setup'
                }
            
            # Calculate position size
            position_result = self.calculate_position_size(
                symbol, entry_price, stop_loss, 
                market_condition={'market_data': market_data} if market_data is not None else None
            )
            
            # Calculate risk-reward ratio
            if stop_loss and profit_target:
                risk = abs(entry_price - stop_loss)
                reward = abs(profit_target - entry_price)
                risk_reward_ratio = reward / risk if risk > 0 else 0
            else:
                risk_reward_ratio = 0
            
            # Simple risk score (0-100)
            risk_score = 0
            
            # Factor 1: Position size viability
            if position_result.get('can_trade', False):
                risk_score += 40
            
            # Factor 2: Risk-reward ratio
            if risk_reward_ratio >= 2:
                risk_score += 40
            elif risk_reward_ratio >= 1.5:
                risk_score += 30
            elif risk_reward_ratio >= 1:
                risk_score += 20
            
            # Factor 3: Market condition (if available)
            if market_data is not None and len(market_data) > 0:
                # Simple trend check (last 10 periods)
                if len(market_data) >= 10:
                    prices = market_data['close'].values[-10:]
                    if (direction.lower() == 'long' and prices[-1] > prices[0]) or \
                       (direction.lower() == 'short' and prices[-1] < prices[0]):
                        risk_score += 20
                else:
                    risk_score += 10  # Not enough data for trend check
            
            # Determine recommendation
            recommendation = 'ACCEPT'
            reason = 'Trade meets basic risk criteria'
            
            if risk_score < 40:
                recommendation = 'REJECT'
                reason = 'Risk score too low'
            elif risk_score < 60:
                recommendation = 'CAUTION'
                reason = 'Moderate risk, proceed with caution'
            
            return {
                'risk_score': risk_score,
                'recommendation': recommendation,
                'reason': reason,
                'position_size': position_result.get('shares', 0),
                'risk_amount': position_result.get('risk_amount', 0),
                'risk_percent': position_result.get('risk_percent', 0),
                'risk_reward_ratio': risk_reward_ratio,
                'ai_enhanced': False
            }
            
        except Exception as e:
            logger.error(f"Error evaluating trade risk: {str(e)}")
            return {
                'risk_score': 0,
                'recommendation': 'REJECT',
                'reason': f'Error in risk evaluation: {str(e)}'
            } 