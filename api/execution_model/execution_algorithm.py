"""
Execution Algorithm Module

This module handles the execution of trade setups, including:
- Volume confirmation before entry
- Order creation and management
- Tracking of active trades
- Risk management during trade execution
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from .pnl_logger import PnLLogger
from .ai_signal_ranking import AISignalRanking

logger = logging.getLogger(__name__)

class ExecutionAlgorithm:
    """
    Executes trades based on trade setups and market conditions
    
    This class handles the actual execution of trades, including:
    - Validating setups before execution
    - Checking for volume confirmation
    - Creating and managing orders
    - Tracking active trades
    """
    
    def __init__(self, risk_manager, config):
        """
        Initialize with risk manager and configuration
        
        Args:
            risk_manager: RiskManager instance
            config: ExecutionModelConfig instance
        """
        self.risk_manager = risk_manager
        self.config = config
        self.execution_config = config.get("execution", {})
        
        # Get execution parameters from config
        self.use_volume_confirmation = self.execution_config.get("volume_confirmation", True)
        self.volume_threshold = self.execution_config.get("volume_threshold", 1.5)
        self.use_time_based_rules = self.execution_config.get("time_based_rules", True)
        self.avoid_high_spread = self.execution_config.get("avoid_high_spread", True)
        
        # Initialize cooldown timer parameters
        self.cooldown_enabled = self.execution_config.get("cooldown_enabled", True)
        self.max_trades_per_hour = self.execution_config.get("max_trades_per_hour", 3)
        self.max_trades_per_day = self.execution_config.get("max_trades_per_day", 10)
        self.cooldown_minutes = self.execution_config.get("cooldown_minutes", 20)
        self.cooldown_adaptive = self.execution_config.get("cooldown_adaptive", True)
        
        # Initialize trade tracking for cooldown
        self.trade_timestamps = []
        self.hourly_trade_count = 0
        self.daily_trade_count = 0
        self.last_hourly_reset = datetime.now()
        self.last_daily_reset = datetime.now().date()
        self.next_available_trade_time = None
        
        # Track active and completed trades
        self.active_trades = {}
        self.completed_trades = []
        
        # Initialize PnL logger
        self.pnl_logger = PnLLogger(config)
        
        # Initialize AI signal ranking
        self.ai_config = config.get("ai_signal_ranking", {})
        self.use_ai_ranking = self.ai_config.get("enabled", True)
        self.min_ai_confidence = self.ai_config.get("min_confidence_threshold", 0.65)
        self.optimize_setups = self.ai_config.get("optimize_trade_setups", True)
        
        if self.use_ai_ranking:
            self.ai_signal_ranking = AISignalRanking(config, self.pnl_logger)
            logger.info("AI signal ranking initialized")
        else:
            self.ai_signal_ranking = None
            logger.info("AI signal ranking disabled")

    def execute_trade(self, trade_setup, market_data, account_info):
        """
        Execute a trade based on a trade setup
        
        Args:
            trade_setup: Dictionary with trade setup details
            market_data: DataFrame with market data
            account_info: Dictionary with account information
            
        Returns:
            dict: Trade order details if executed, None if not executed
        """
        symbol = trade_setup['symbol']
        
        try:
            # Apply AI ranking if enabled
            if self.use_ai_ranking and self.ai_signal_ranking:
                # Get symbol-specific market data
                symbol_market_data = {symbol: market_data}
                
                # Rank the signal
                ranked_signals = self.ai_signal_ranking.rank_signals([trade_setup], symbol_market_data)
                if ranked_signals:
                    trade_setup = ranked_signals[0]  # Get the ranked signal
                    
                    # Check confidence threshold
                    ai_confidence = trade_setup.get('ai_confidence', 0)
                    if ai_confidence < self.min_ai_confidence:
                        logger.info(f"AI confidence too low for {symbol}: {ai_confidence:.2f} < {self.min_ai_confidence:.2f}")
                        return None
                    
                    # Log AI confidence and ranking factors
                    logger.info(f"AI confidence for {symbol}: {ai_confidence:.2f}")
                    ranking_factors = trade_setup.get('ranking_factors', {})
                    for factor, score in ranking_factors.items():
                        logger.debug(f"  {factor}: {score:.2f}")
                    
                    # Optimize trade setup with GPT insights if enabled
                    if self.optimize_setups:
                        trade_setup = self.ai_signal_ranking.optimize_trade_setup(trade_setup, market_data)
            
            # Validate setup
            if not self._validate_setup(trade_setup):
                logger.warning(f"Trade setup validation failed for {symbol}")
                return None
            
            # Check if symbol already has an active trade
            if symbol in self.active_trades:
                logger.warning(f"Already have an active trade for {symbol}, skipping execution")
                return None
            
            # Check cooldown timer if enabled
            if self.cooldown_enabled and not self._check_cooldown_timer(trade_setup):
                logger.info(f"Cooldown timer prevented trade execution for {symbol}")
                return None
            
            # Check time-based rules if enabled
            if self.use_time_based_rules and not self._check_time_rules():
                logger.info(f"Time-based rules prevented trade execution for {symbol}")
                return None
            
            # Check volume confirmation if enabled
            if self.use_volume_confirmation and not self._confirm_volume(trade_setup, market_data):
                logger.info(f"Volume confirmation failed for {symbol}, skipping execution")
                return None
            
            # Check spread if enabled
            if self.avoid_high_spread and self._has_high_spread(trade_setup, market_data):
                logger.info(f"High spread detected for {symbol}, skipping execution")
                return None
            
            # Create trade order
            trade_order = self._create_trade_order(trade_setup, market_data, account_info)
            
            if trade_order:
                # Update cooldown timer
                self._update_trade_cooldown(trade_setup)
                
                # Add to active trades
                self.active_trades[symbol] = trade_order
                logger.info(f"Trade executed for {symbol}: {trade_order['direction']} {trade_order['position_size']} @ {trade_order['entry_price']:.4f}")
            
            return trade_order
            
        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {str(e)}")
            return None
    
    def update_trades(self, market_data, account_info):
        """
        Update active trades based on current market data
        
        Args:
            market_data: Dictionary with market data for multiple symbols
            account_info: Dictionary with account information
            
        Returns:
            list: List of trades that were updated or closed
        """
        updated_trades = []
        
        # Update cooldown counters
        self._update_cooldown_counters()
        
        for symbol, trade in list(self.active_trades.items()):
            if symbol not in market_data:
                continue
                
            current_data = market_data[symbol]
            
            if len(current_data) == 0:
                continue
                
            # Get current price
            current_price = current_data['close'].iloc[-1]
            
            # Update trade with current price
            trade['current_price'] = current_price
            
            # Calculate unrealized P&L
            entry_price = trade['entry_price']
            position_size = trade['position_size']
            direction = trade['direction']
            
            if direction == 'LONG':
                price_change = current_price - entry_price
            else:  # SHORT
                price_change = entry_price - current_price
                
            trade['unrealized_pnl'] = price_change * position_size
            trade['unrealized_pnl_pct'] = price_change / entry_price
            
            # Check if stop loss or profit target hit
            if self._should_close_trade(trade, current_price):
                # Close the trade
                closed_trade = self._close_trade(trade, current_price, "TARGET_OR_STOP_HIT")
                updated_trades.append(closed_trade)
            else:
                # Just update the trade
                updated_trades.append(trade)
                
        return updated_trades
    
    def close_trade(self, symbol, close_price=None, reason="MANUAL_CLOSE"):
        """
        Close a specific trade
        
        Args:
            symbol: Symbol of the trade to close
            close_price: Optional closing price, if None will use latest price
            reason: Reason for closing the trade
            
        Returns:
            dict: Closed trade details, or None if trade not found
        """
        if symbol not in self.active_trades:
            logger.warning(f"No active trade found for {symbol}")
            return None
            
        trade = self.active_trades[symbol]
        
        # If no close price provided, use the current price in the trade
        if close_price is None:
            close_price = trade.get('current_price')
            
            if close_price is None:
                logger.warning(f"No close price provided and no current price in trade for {symbol}")
                return None
                
        return self._close_trade(trade, close_price, reason)
    
    def get_active_trades(self):
        """
        Get all active trades
        
        Returns:
            dict: Active trades by symbol
        """
        return self.active_trades
    
    def get_completed_trades(self):
        """
        Get all completed trades
        
        Returns:
            list: Completed trades
        """
        return self.completed_trades
    
    def _update_cooldown_counters(self):
        """
        Update the cooldown counters based on current time
        """
        current_time = datetime.now()
        current_date = current_time.date()
        
        # Reset daily counter if date changed
        if current_date != self.last_daily_reset:
            self.daily_trade_count = 0
            self.last_daily_reset = current_date
            logger.debug("Daily trade counter reset")
            
        # Reset hourly counter if hour changed
        hour_diff = (current_time - self.last_hourly_reset).total_seconds() / 3600
        if hour_diff >= 1:
            self.hourly_trade_count = 0
            self.last_hourly_reset = current_time
            logger.debug("Hourly trade counter reset")
    
    def _check_cooldown_timer(self, trade_setup):
        """
        Check if a trade can be executed based on cooldown timer
        
        Args:
            trade_setup: Trade setup dictionary
            
        Returns:
            bool: True if a trade can be executed, False otherwise
        """
        current_time = datetime.now()
        
        # Update counters before checking
        self._update_cooldown_counters()
        
        # Check if we've reached the maximum trades per day
        if self.daily_trade_count >= self.max_trades_per_day:
            logger.info(f"Maximum trades per day ({self.max_trades_per_day}) reached")
            return False
            
        # Check if we've reached the maximum trades per hour
        if self.hourly_trade_count >= self.max_trades_per_hour:
            logger.info(f"Maximum trades per hour ({self.max_trades_per_hour}) reached")
            return False
            
        # Check if we need to wait for the cooldown period
        if self.next_available_trade_time and current_time < self.next_available_trade_time:
            time_remaining = (self.next_available_trade_time - current_time).total_seconds() / 60
            logger.info(f"Cooldown period still active, {time_remaining:.1f} minutes remaining")
            return False
            
        # If we got here, cooldown checks passed
        return True
        
    def _update_trade_cooldown(self, trade_setup):
        """
        Update trade cooldown timers after a successful trade execution
        
        Args:
            trade_setup: Trade setup that was executed
        """
        current_time = datetime.now()
        
        # Record trade timestamp
        self.trade_timestamps.append(current_time)
        
        # Increment counters
        self.hourly_trade_count += 1
        self.daily_trade_count += 1
        
        # Calculate cooldown period
        cooldown_period = self.cooldown_minutes
        
        # Adjust cooldown based on market conditions if adaptive mode is enabled
        if self.cooldown_adaptive and 'market_condition' in trade_setup:
            market_condition = trade_setup['market_condition']
            
            # Reduce cooldown for trending markets
            if market_condition == 'TREND':
                cooldown_period *= 0.8
            
            # Increase cooldown for choppy markets
            elif market_condition == 'CHOPPY':
                cooldown_period *= 1.5
                
            # Add extra cooldown for high confidence setups
            if trade_setup.get('confidence', 0) > 0.8:
                cooldown_period *= 0.9
            
            # Add extra cooldown for low confidence setups
            elif trade_setup.get('confidence', 0) < 0.4:
                cooldown_period *= 1.5
        
        # Set next available trade time
        self.next_available_trade_time = current_time + timedelta(minutes=cooldown_period)
        
        logger.info(f"Cooldown timer set: next trade available at {self.next_available_trade_time.strftime('%H:%M:%S')}")
        logger.info(f"Daily trade count: {self.daily_trade_count}/{self.max_trades_per_day}, " +
                   f"Hourly trade count: {self.hourly_trade_count}/{self.max_trades_per_hour}")
    
    def _validate_setup(self, trade_setup):
        """
        Validate a trade setup before execution
        
        Args:
            trade_setup: Trade setup dictionary
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = [
            'symbol', 'direction', 'entry_price', 
            'stop_loss', 'profit_target', 'position_size'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in trade_setup:
                logger.warning(f"Missing required field: {field}")
                return False
                
        # Check position size
        if trade_setup['position_size'] <= 0:
            logger.warning(f"Invalid position size: {trade_setup['position_size']}")
            return False
            
        # Check direction
        if trade_setup['direction'] not in ['LONG', 'SHORT']:
            logger.warning(f"Invalid direction: {trade_setup['direction']}")
            return False
            
        # Check risk-reward ratio
        risk = abs(trade_setup['entry_price'] - trade_setup['stop_loss'])
        reward = abs(trade_setup['profit_target'] - trade_setup['entry_price'])
        risk_reward = reward / risk if risk > 0 else 0
        
        min_risk_reward = 1.5  # Minimum R:R ratio
        if risk_reward < min_risk_reward:
            logger.warning(f"Insufficient risk-reward ratio: {risk_reward:.2f} < {min_risk_reward}")
            return False
            
        return True
    
    def _confirm_volume(self, trade_setup, market_data):
        """
        Check if volume confirms the trade setup
        
        Args:
            trade_setup: Trade setup dictionary
            market_data: Market data DataFrame
            
        Returns:
            bool: True if volume confirms, False otherwise
        """
        if len(market_data) < 20:  # Need some history for volume comparison
            return True  # Not enough data to check, assume it's OK
            
        # Get current volume
        current_volume = market_data['volume'].iloc[-1]
        
        # Calculate average volume over last 20 periods
        avg_volume = market_data['volume'].iloc[-20:-1].mean()
        
        if avg_volume == 0:
            return True  # Avoid division by zero
            
        # Calculate volume ratio
        volume_ratio = current_volume / avg_volume
        
        # Check if volume is high enough
        return volume_ratio >= self.volume_threshold
    
    def _has_high_spread(self, trade_setup, market_data):
        """
        Check if the spread is too high
        
        Args:
            trade_setup: Trade setup dictionary
            market_data: Market data DataFrame
            
        Returns:
            bool: True if spread is high, False otherwise
        """
        if 'ask' not in market_data.columns or 'bid' not in market_data.columns:
            return False  # No bid/ask data, assume it's OK
            
        # Get latest bid/ask
        latest = market_data.iloc[-1]
        bid = latest['bid']
        ask = latest['ask']
        
        if bid == 0:
            return True  # Avoid division by zero and invalid data
            
        # Calculate spread percentage
        spread_pct = (ask - bid) / bid
        
        # Define high spread threshold
        high_spread_threshold = 0.005  # 0.5%
        
        return spread_pct > high_spread_threshold
    
    def _check_time_rules(self):
        """
        Check time-based rules for trade execution
        
        Returns:
            bool: True if time rules allow execution, False otherwise
        """
        # Get current time
        now = datetime.now()
        current_time = now.time()
        
        # Avoid trading in first 15 minutes of market open
        market_open = datetime.strptime("09:30", "%H:%M").time()
        early_market = datetime.strptime("09:45", "%H:%M").time()
        if market_open <= current_time <= early_market:
            logger.info("Avoiding trade during first 15 minutes of market open")
            return False
            
        # Avoid trading in last 15 minutes of market close
        pre_close = datetime.strptime("15:45", "%H:%M").time()
        market_close = datetime.strptime("16:00", "%H:%M").time()
        if pre_close <= current_time <= market_close:
            logger.info("Avoiding trade during last 15 minutes before market close")
            return False
            
        return True
    
    def _create_trade_order(self, trade_setup, market_data, account_info):
        """
        Create a trade order from a validated setup
        
        Args:
            trade_setup: Trade setup dictionary
            market_data: Market data DataFrame
            account_info: Account information dictionary
            
        Returns:
            dict: Trade order dictionary
        """
        symbol = trade_setup['symbol']
        direction = trade_setup['direction']
        entry_price = trade_setup['entry_price']
        stop_loss = trade_setup['stop_loss']
        profit_target = trade_setup['profit_target']
        position_size = trade_setup['position_size']
        
        # Calculate risk amount
        risk_per_share = abs(entry_price - stop_loss)
        risk_amount = risk_per_share * position_size
        
        # Create the order
        order = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'profit_target': profit_target,
            'position_size': position_size,
            'risk_amount': risk_amount,
            'entry_time': datetime.now().isoformat(),
            'status': 'ACTIVE',
            'setup_type': trade_setup.get('type', 'UNKNOWN'),
            'risk_reward': trade_setup.get('risk_reward', 0),
            'confidence': trade_setup.get('confidence', 0),
            'setup_reason': trade_setup.get('setup_reason', ''),
            'market_condition': trade_setup.get('market_condition', 'UNKNOWN')
        }
        
        # Add AI confidence if available
        if 'ai_confidence' in trade_setup:
            order['ai_confidence'] = trade_setup['ai_confidence']
            
        # Add AI insights if available
        if 'ai_insights' in trade_setup:
            order['ai_insights'] = trade_setup['ai_insights']
        
        # Calculate true trade parameters based on latest data
        latest_price = market_data['close'].iloc[-1]
        
        # Adjust entry price if market has moved
        # For live trading, you'd use actual execution price
        order['entry_price'] = latest_price
        
        # Recalculate position size with the actual entry price
        actual_position_size = self.risk_manager.calculate_position_size(
            account_info['balance'], latest_price, stop_loss, symbol
        )
        
        # Only update if we got a valid position size
        if actual_position_size > 0:
            order['position_size'] = actual_position_size
            
            # Apply position size boost based on AI confidence if available
            if self.use_ai_ranking and 'ai_confidence' in trade_setup:
                ai_confidence = trade_setup['ai_confidence']
                confidence_boost_threshold = self.ai_config.get("confidence_boost_threshold", 0.8)
                
                if ai_confidence >= confidence_boost_threshold:
                    # Boost position size by up to 20% for high confidence signals
                    confidence_boost = 1.0 + ((ai_confidence - confidence_boost_threshold) / (1.0 - confidence_boost_threshold)) * 0.2
                    boosted_size = order['position_size'] * confidence_boost
                    order['position_size'] = min(boosted_size, actual_position_size * 1.2)  # Cap at 20% boost
                    order['size_boosted_by_ai'] = True
                    logger.info(f"Position size boosted by AI confidence: {confidence_boost:.2f}x")
        
        # Recalculate risk amount
        order['risk_amount'] = abs(latest_price - stop_loss) * order['position_size']
        
        # Add the order to risk manager for tracking
        self.risk_manager.add_position({
            'symbol': symbol,
            'direction': direction,
            'size': order['position_size'],
            'entry_price': order['entry_price'],
            'stop_loss': stop_loss,
            'risk_amount': order['risk_amount']
        })
        
        return order
    
    def _should_close_trade(self, trade, current_price):
        """
        Check if a trade should be closed based on current price
        
        Args:
            trade: Trade dictionary
            current_price: Current market price
            
        Returns:
            bool: True if trade should be closed, False otherwise
        """
        direction = trade['direction']
        stop_loss = trade['stop_loss']
        profit_target = trade['profit_target']
        
        # Check if stop loss hit
        if direction == 'LONG' and current_price <= stop_loss:
            logger.info(f"Stop loss hit for {trade['symbol']} LONG at {current_price:.4f}")
            return True
        elif direction == 'SHORT' and current_price >= stop_loss:
            logger.info(f"Stop loss hit for {trade['symbol']} SHORT at {current_price:.4f}")
            return True
            
        # Check if profit target hit
        if direction == 'LONG' and current_price >= profit_target:
            logger.info(f"Profit target hit for {trade['symbol']} LONG at {current_price:.4f}")
            return True
        elif direction == 'SHORT' and current_price <= profit_target:
            logger.info(f"Profit target hit for {trade['symbol']} SHORT at {current_price:.4f}")
            return True
            
        return False
    
    def _close_trade(self, trade, close_price, reason):
        """
        Close a trade and update records
        
        Args:
            trade: Trade dictionary
            close_price: Closing price
            reason: Reason for closing
            
        Returns:
            dict: Closed trade dictionary
        """
        symbol = trade['symbol']
        direction = trade['direction']
        entry_price = trade['entry_price']
        position_size = trade['position_size']
        entry_time = trade['entry_time']
        
        # Calculate P&L
        if direction == 'LONG':
            pnl = (close_price - entry_price) * position_size
        else:  # SHORT
            pnl = (entry_price - close_price) * position_size
            
        pnl_pct = ((close_price / entry_price) - 1) * 100
        if direction == 'SHORT':
            pnl_pct = -pnl_pct
            
        # Create closed trade record
        closed_trade = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': close_price,
            'position_size': position_size,
            'entry_time': entry_time,
            'exit_time': datetime.now().isoformat(),
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason,
            'setup_type': trade.get('setup_type', 'UNKNOWN'),
            'risk_reward': trade.get('risk_reward', 0),
            'market_condition': trade.get('market_condition', 'UNKNOWN')
        }
        
        # Remove from active trades
        if symbol in self.active_trades:
            del self.active_trades[symbol]
            
        # Add to completed trades
        self.completed_trades.append(closed_trade)
        
        # Log trade to CSV
        self.pnl_logger.log_trade(closed_trade)
        
        # Log trade result
        logger.info(f"Closed {direction} trade for {symbol} at {close_price:.4f} with P&L: ${pnl:.2f} ({pnl_pct:.2f}%)")
        
        return closed_trade
    
    def get_cooldown_status(self):
        """
        Get the current status of the cooldown timer
        
        Returns:
            dict: Cooldown status
        """
        current_time = datetime.now()
        
        # Update counters to ensure they're current
        self._update_cooldown_counters()
        
        remaining_time = 0
        if self.next_available_trade_time and current_time < self.next_available_trade_time:
            remaining_time = (self.next_available_trade_time - current_time).total_seconds() / 60
            
        return {
            'cooldown_enabled': self.cooldown_enabled,
            'hourly_trade_count': self.hourly_trade_count,
            'max_trades_per_hour': self.max_trades_per_hour,
            'daily_trade_count': self.daily_trade_count, 
            'max_trades_per_day': self.max_trades_per_day,
            'next_available_trade_time': self.next_available_trade_time.isoformat() if self.next_available_trade_time else None,
            'cooldown_minutes': self.cooldown_minutes,
            'cooldown_remaining_minutes': round(remaining_time, 1),
            'cooldown_active': remaining_time > 0 or 
                              self.hourly_trade_count >= self.max_trades_per_hour or 
                              self.daily_trade_count >= self.max_trades_per_day
        } 