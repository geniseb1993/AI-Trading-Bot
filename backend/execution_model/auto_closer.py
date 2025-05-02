"""
Auto-Closer Module

This module is responsible for automatically closing trades based on predefined rules
such as stop-loss, take-profit, trailing stops, and other risk management parameters.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import time
import threading

logger = logging.getLogger(__name__)

class AutoCloser:
    """
    Manages automatic trade exits based on predefined rules
    """
    
    def __init__(self, config=None, broker_api=None):
        """
        Initialize the Auto-Closer
        
        Args:
            config: Configuration dictionary with parameters
            broker_api: Broker API client instance (Alpaca, etc.)
        """
        self.config = config or {}
        self.broker_api = broker_api
        
        # Default configuration
        self.check_interval = self.config.get('check_interval', 60)  # seconds
        self.stop_loss_percent = self.config.get('stop_loss_percent', 2.0)  # %
        self.take_profit_percent = self.config.get('take_profit_percent', 5.0)  # %
        self.trailing_stop_percent = self.config.get('trailing_stop_percent', 1.5)  # %
        self.time_based_exit = self.config.get('time_based_exit', False)  # Enable time-based exits
        self.max_hold_time = self.config.get('max_hold_time', 60)  # minutes
        self.enable_partial_exits = self.config.get('enable_partial_exits', True)  # Enable partial exits
        self.partial_exit_levels = self.config.get('partial_exit_levels', [
            {'profit_percent': 2.0, 'exit_percent': 25.0},
            {'profit_percent': 4.0, 'exit_percent': 25.0},
            {'profit_percent': 7.0, 'exit_percent': 25.0}
        ])
        
        # Initialize state
        self.active_trades = {}
        self.closed_trades = []
        self.running = False
        self.monitor_thread = None
        self.last_check_time = None
        
        logger.info(f"Auto-Closer initialized with stop loss: {self.stop_loss_percent}%, take profit: {self.take_profit_percent}%")
        
    def update_config(self, config):
        """
        Update configuration
        
        Args:
            config: New configuration dictionary
        """
        self.config.update(config)
        self.check_interval = self.config.get('check_interval', 60)
        self.stop_loss_percent = self.config.get('stop_loss_percent', 2.0)
        self.take_profit_percent = self.config.get('take_profit_percent', 5.0)
        self.trailing_stop_percent = self.config.get('trailing_stop_percent', 1.5)
        self.time_based_exit = self.config.get('time_based_exit', False)
        self.max_hold_time = self.config.get('max_hold_time', 60)
        self.enable_partial_exits = self.config.get('enable_partial_exits', True)
        self.partial_exit_levels = self.config.get('partial_exit_levels', [
            {'profit_percent': 2.0, 'exit_percent': 25.0},
            {'profit_percent': 4.0, 'exit_percent': 25.0},
            {'profit_percent': 7.0, 'exit_percent': 25.0}
        ])
        
        logger.info("Auto-Closer configuration updated")
        
    def start_monitoring(self):
        """
        Start the monitoring thread
        """
        if self.running:
            logger.warning("Auto-Closer is already running")
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Auto-Closer monitoring started")
        
    def stop_monitoring(self):
        """
        Stop the monitoring thread
        """
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            
        logger.info("Auto-Closer monitoring stopped")
        
    def _monitor_loop(self):
        """
        Main monitoring loop
        """
        while self.running:
            try:
                self.check_all_trades()
                self.last_check_time = datetime.now()
            except Exception as e:
                logger.error(f"Error in monitor loop: {str(e)}")
                
            time.sleep(self.check_interval)
            
    def add_trade(self, trade):
        """
        Add a trade to be monitored
        
        Args:
            trade: Dictionary with trade details
        """
        if 'id' not in trade:
            trade['id'] = f"trade_{int(time.time() * 1000)}"
            
        if 'symbol' not in trade:
            logger.error("Trade must include 'symbol'")
            return
            
        if 'entry_price' not in trade:
            logger.error("Trade must include 'entry_price'")
            return
            
        if 'side' not in trade and 'direction' not in trade:
            logger.error("Trade must include 'side' or 'direction'")
            return
            
        # Normalize side/direction to 'long' or 'short'
        if 'side' in trade and 'direction' not in trade:
            side = trade['side'].lower()
            if side in ['buy', 'long']:
                trade['direction'] = 'long'
            elif side in ['sell', 'short']:
                trade['direction'] = 'short'
            else:
                logger.error(f"Invalid side: {side}")
                return
                
        # Add required fields if missing
        if 'entry_time' not in trade:
            trade['entry_time'] = datetime.now().isoformat()
            
        if 'quantity' not in trade and 'size' in trade:
            trade['quantity'] = trade['size']
            
        if 'stop_loss' not in trade:
            # Calculate default stop loss
            entry_price = trade['entry_price']
            if trade['direction'] == 'long':
                trade['stop_loss'] = entry_price * (1 - self.stop_loss_percent / 100)
            else:
                trade['stop_loss'] = entry_price * (1 + self.stop_loss_percent / 100)
                
        if 'take_profit' not in trade:
            # Calculate default take profit
            entry_price = trade['entry_price']
            if trade['direction'] == 'long':
                trade['take_profit'] = entry_price * (1 + self.take_profit_percent / 100)
            else:
                trade['take_profit'] = entry_price * (1 - self.take_profit_percent / 100)
                
        if 'trailing_stop' not in trade:
            trade['trailing_stop'] = None  # Will be set when price moves in favor
                
        if 'max_hold_time' not in trade:
            trade['max_hold_time'] = self.max_hold_time
            
        if 'partial_exits' not in trade and self.enable_partial_exits:
            trade['partial_exits'] = self.partial_exit_levels.copy()
            trade['executed_partial_exits'] = []
            
        # Add to active trades
        self.active_trades[trade['id']] = trade
        
        logger.info(f"Added trade {trade['id']}: {trade['symbol']} {trade['direction']} at {trade['entry_price']}")
        
        return trade['id']
        
    def remove_trade(self, trade_id):
        """
        Remove a trade from monitoring
        
        Args:
            trade_id: ID of the trade to remove
        """
        if trade_id in self.active_trades:
            del self.active_trades[trade_id]
            logger.info(f"Removed trade {trade_id}")
            
    def update_trade(self, trade_id, updates):
        """
        Update an existing trade
        
        Args:
            trade_id: ID of the trade to update
            updates: Dictionary with updated values
        """
        if trade_id not in self.active_trades:
            logger.error(f"Trade {trade_id} not found")
            return
            
        self.active_trades[trade_id].update(updates)
        logger.info(f"Updated trade {trade_id}")
        
    def check_all_trades(self):
        """
        Check all active trades for exit conditions
        """
        if not self.active_trades:
            return
            
        logger.debug(f"Checking {len(self.active_trades)} active trades")
        
        # Get current market data (could be optimized to batch)
        current_prices = self._get_current_prices()
        
        # Check each trade
        for trade_id, trade in list(self.active_trades.items()):
            symbol = trade['symbol']
            
            if symbol not in current_prices:
                logger.warning(f"No price data for {symbol}")
                continue
                
            current_price = current_prices[symbol]
            
            # Check if we should exit
            exit_signal = self._check_exit_conditions(trade, current_price)
            
            if exit_signal['should_exit']:
                # Close the trade
                self._close_trade(trade, current_price, exit_signal['reason'])
                
    def _get_current_prices(self):
        """
        Get current prices for all symbols in active trades
        
        Returns:
            Dictionary of current prices by symbol
        """
        current_prices = {}
        
        # Get unique symbols
        symbols = set(trade['symbol'] for trade in self.active_trades.values())
        
        # Use the broker API if available
        if self.broker_api:
            try:
                # This implementation depends on the broker API
                # For Alpaca, might use something like:
                # for symbol in symbols:
                #     current_prices[symbol] = self.broker_api.get_latest_trade(symbol).price
                pass
            except Exception as e:
                logger.error(f"Error getting prices from broker API: {str(e)}")
        else:
            # For testing or when no broker API is available
            # Just use the last known price with a small random change
            for symbol in symbols:
                # Find the last known price for this symbol
                for trade in self.active_trades.values():
                    if trade['symbol'] == symbol and 'last_price' in trade:
                        current_prices[symbol] = trade['last_price']
                        break
                        
                # If we don't have a price, use the entry price
                if symbol not in current_prices:
                    for trade in self.active_trades.values():
                        if trade['symbol'] == symbol:
                            current_prices[symbol] = trade['entry_price']
                            break
                
                # Apply a small random change for testing
                if symbol in current_prices:
                    change = (np.random.random() - 0.45) * 0.01  # -0.45% to +0.55%
                    current_prices[symbol] *= (1 + change)
                    
        return current_prices
        
    def _check_exit_conditions(self, trade, current_price):
        """
        Check if a trade should be exited
        
        Args:
            trade: Trade dictionary
            current_price: Current price of the symbol
            
        Returns:
            Dictionary with exit decision and reason
        """
        entry_price = trade['entry_price']
        direction = trade['direction']
        
        # Calculate profit/loss
        if direction == 'long':
            pnl_percent = (current_price - entry_price) / entry_price * 100
        else:
            pnl_percent = (entry_price - current_price) / entry_price * 100
            
        # Update last known price
        trade['last_price'] = current_price
        
        # Check if we need to update the trailing stop
        if direction == 'long' and current_price > entry_price and (trade['trailing_stop'] is None or current_price > trade['trailing_stop'] * (1 + self.trailing_stop_percent / 100)):
            # Set or update trailing stop for long
            trade['trailing_stop'] = current_price * (1 - self.trailing_stop_percent / 100)
            logger.debug(f"Updated trailing stop for {trade['id']} to {trade['trailing_stop']}")
        elif direction == 'short' and current_price < entry_price and (trade['trailing_stop'] is None or current_price < trade['trailing_stop'] * (1 - self.trailing_stop_percent / 100)):
            # Set or update trailing stop for short
            trade['trailing_stop'] = current_price * (1 + self.trailing_stop_percent / 100)
            logger.debug(f"Updated trailing stop for {trade['id']} to {trade['trailing_stop']}")
            
        # Check for partial exits
        if self.enable_partial_exits and 'partial_exits' in trade:
            for i, level in enumerate(trade['partial_exits']):
                if level['profit_percent'] <= pnl_percent and i not in trade['executed_partial_exits']:
                    # Execute partial exit
                    exit_percent = level['exit_percent']
                    self._execute_partial_exit(trade, current_price, exit_percent, f"Partial exit at {level['profit_percent']}% profit")
                    trade['executed_partial_exits'].append(i)
        
        # Check stop loss condition
        if direction == 'long' and current_price <= trade['stop_loss']:
            return {'should_exit': True, 'reason': 'Stop loss triggered'}
        elif direction == 'short' and current_price >= trade['stop_loss']:
            return {'should_exit': True, 'reason': 'Stop loss triggered'}
            
        # Check take profit condition
        if direction == 'long' and current_price >= trade['take_profit']:
            return {'should_exit': True, 'reason': 'Take profit reached'}
        elif direction == 'short' and current_price <= trade['take_profit']:
            return {'should_exit': True, 'reason': 'Take profit reached'}
            
        # Check trailing stop condition
        if trade['trailing_stop'] is not None:
            if direction == 'long' and current_price <= trade['trailing_stop']:
                return {'should_exit': True, 'reason': 'Trailing stop triggered'}
            elif direction == 'short' and current_price >= trade['trailing_stop']:
                return {'should_exit': True, 'reason': 'Trailing stop triggered'}
                
        # Check time-based exit
        if self.time_based_exit and 'entry_time' in trade:
            entry_time = datetime.fromisoformat(trade['entry_time'])
            elapsed_minutes = (datetime.now() - entry_time).total_seconds() / 60
            
            if elapsed_minutes >= trade['max_hold_time']:
                return {'should_exit': True, 'reason': f"Max hold time reached ({trade['max_hold_time']} minutes)"}
        
        # No exit condition triggered
        return {'should_exit': False, 'reason': None}
    
    def _execute_partial_exit(self, trade, current_price, exit_percent, reason):
        """
        Execute a partial exit on a trade
        
        Args:
            trade: Trade dictionary
            current_price: Current price of the symbol
            exit_percent: Percentage of position to exit
            reason: Reason for the partial exit
        """
        logger.info(f"Executing partial exit for {trade['id']}: {exit_percent}% at {current_price}")
        
        # Calculate exit quantity
        exit_quantity = trade['quantity'] * exit_percent / 100
        
        # Update remaining quantity
        remaining_quantity = trade['quantity'] - exit_quantity
        trade['quantity'] = remaining_quantity
        
        # Create exit record
        exit_record = {
            'trade_id': trade['id'],
            'symbol': trade['symbol'],
            'exit_price': current_price,
            'exit_quantity': exit_quantity,
            'exit_time': datetime.now().isoformat(),
            'reason': reason,
            'is_partial': True
        }
        
        # Record the partial exit
        if 'partial_exit_records' not in trade:
            trade['partial_exit_records'] = []
            
        trade['partial_exit_records'].append(exit_record)
        
        # Execute the actual order if broker API is available
        if self.broker_api:
            try:
                # This implementation depends on the broker API
                # For Alpaca, might use something like:
                # side = 'sell' if trade['direction'] == 'long' else 'buy'
                # self.broker_api.submit_order(
                #     symbol=trade['symbol'],
                #     qty=exit_quantity,
                #     side=side,
                #     type='market',
                #     time_in_force='gtc'
                # )
                pass
            except Exception as e:
                logger.error(f"Error executing partial exit: {str(e)}")
        
    def _close_trade(self, trade, exit_price, reason):
        """
        Close a trade
        
        Args:
            trade: Trade dictionary
            exit_price: Exit price
            reason: Reason for exit
        """
        trade_id = trade['id']
        symbol = trade['symbol']
        entry_price = trade['entry_price']
        direction = trade['direction']
        
        # Calculate P&L
        if direction == 'long':
            pnl_percent = (exit_price - entry_price) / entry_price * 100
        else:
            pnl_percent = (entry_price - exit_price) / entry_price * 100
            
        logger.info(f"Closing trade {trade_id}: {symbol} {direction} at {exit_price}, P&L: {pnl_percent:.2f}%, Reason: {reason}")
        
        # Create exit record
        exit_time = datetime.now()
        exit_record = {
            'trade_id': trade_id,
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'entry_time': trade.get('entry_time', 'unknown'),
            'exit_time': exit_time.isoformat(),
            'direction': direction,
            'quantity': trade.get('quantity', 0),
            'pnl_percent': pnl_percent,
            'reason': reason,
            'partial_exits': trade.get('partial_exit_records', [])
        }
        
        # Add to closed trades
        self.closed_trades.append(exit_record)
        
        # Remove from active trades
        del self.active_trades[trade_id]
        
        # Execute the actual order if broker API is available
        if self.broker_api:
            try:
                # This implementation depends on the broker API
                # For Alpaca, might use something like:
                # side = 'sell' if direction == 'long' else 'buy'
                # self.broker_api.submit_order(
                #     symbol=symbol,
                #     qty=trade['quantity'],
                #     side=side,
                #     type='market',
                #     time_in_force='gtc'
                # )
                pass
            except Exception as e:
                logger.error(f"Error executing exit order: {str(e)}")
                
        return exit_record
    
    def get_active_trades(self):
        """
        Get all active trades
        
        Returns:
            Dictionary of active trades by ID
        """
        return self.active_trades
    
    def get_closed_trades(self):
        """
        Get all closed trades
        
        Returns:
            List of closed trade records
        """
        return self.closed_trades
    
    def get_pnl_summary(self):
        """
        Get a summary of P&L from closed trades
        
        Returns:
            Dictionary with P&L summary
        """
        if not self.closed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'total_pnl': 0,
                'max_win': 0,
                'max_loss': 0
            }
            
        # Calculate stats
        total_trades = len(self.closed_trades)
        winning_trades = sum(1 for t in self.closed_trades if t['pnl_percent'] > 0)
        losing_trades = sum(1 for t in self.closed_trades if t['pnl_percent'] <= 0)
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        winning_pnls = [t['pnl_percent'] for t in self.closed_trades if t['pnl_percent'] > 0]
        losing_pnls = [t['pnl_percent'] for t in self.closed_trades if t['pnl_percent'] <= 0]
        
        avg_win = sum(winning_pnls) / len(winning_pnls) if winning_pnls else 0
        avg_loss = sum(losing_pnls) / len(losing_pnls) if losing_pnls else 0
        
        total_pnl = sum(t['pnl_percent'] for t in self.closed_trades)
        max_win = max(winning_pnls) if winning_pnls else 0
        max_loss = min(losing_pnls) if losing_pnls else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'total_pnl': total_pnl,
            'max_win': max_win,
            'max_loss': max_loss
        }


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create auto-closer
    auto_closer = AutoCloser()
    
    # Add some test trades
    auto_closer.add_trade({
        'symbol': 'SPY',
        'direction': 'long',
        'entry_price': 450.0,
        'quantity': 100,
        'stop_loss': 445.0,
        'take_profit': 460.0
    })
    
    auto_closer.add_trade({
        'symbol': 'QQQ',
        'direction': 'short',
        'entry_price': 380.0,
        'quantity': 50,
        'stop_loss': 385.0,
        'take_profit': 370.0
    })
    
    # Start monitoring
    auto_closer.start_monitoring()
    
    try:
        # Run for a while
        print("Auto-Closer running...")
        time.sleep(300)  # 5 minutes
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # Stop monitoring
        auto_closer.stop_monitoring()
        
        # Print results
        print("\nActive Trades:")
        for trade_id, trade in auto_closer.get_active_trades().items():
            print(f"{trade_id}: {trade['symbol']} {trade['direction']} at {trade['entry_price']}")
            
        print("\nClosed Trades:")
        for trade in auto_closer.get_closed_trades():
            print(f"{trade['symbol']} {trade['direction']}: {trade['pnl_percent']:.2f}% - {trade['reason']}")
            
        print("\nP&L Summary:")
        summary = auto_closer.get_pnl_summary()
        print(f"Total Trades: {summary['total_trades']}")
        print(f"Win Rate: {summary['win_rate']:.2f}")
        print(f"Total P&L: {summary['total_pnl']:.2f}%") 