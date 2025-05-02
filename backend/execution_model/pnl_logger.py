"""
PnL Logging Module

This module handles the logging of trade PnL data to CSV files, including:
- Per-trade PnL logging
- Daily aggregated PnL metrics
"""

import os
import pandas as pd
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class PnLLogger:
    """
    Handles logging of trade profit and loss data to CSV files
    
    This class provides methods to:
    - Log individual trade details
    - Calculate and log daily performance metrics
    """
    
    def __init__(self, config):
        """
        Initialize the PnL logger
        
        Args:
            config: Configuration dictionary with logging settings
        """
        self.config = config
        
        # Set up file paths
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'logs')
        self.trades_file = os.path.join(self.base_dir, 'trades.csv')
        self.daily_pnl_file = os.path.join(self.base_dir, 'daily_pnl.csv')
        
        # Ensure log directory exists
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Initialize CSV files if they don't exist
        self._init_trades_file()
        self._init_daily_pnl_file()
        
        # Cache for today's trades (used for calculating daily metrics)
        self.todays_trades = []
        self.last_daily_update = None
        
    def _init_trades_file(self):
        """Initialize the trades CSV file if it doesn't exist"""
        if not os.path.exists(self.trades_file) or os.path.getsize(self.trades_file) == 0:
            columns = [
                'timestamp', 'symbol', 'side', 'entry_price', 'exit_price', 
                'quantity', 'pnl', 'pnl_percentage', 'trade_duration', 
                'strategy_name', 'notes'
            ]
            pd.DataFrame(columns=columns).to_csv(self.trades_file, index=False)
            logger.info(f"Created trades log file at {self.trades_file}")
            
    def _init_daily_pnl_file(self):
        """Initialize the daily PnL CSV file if it doesn't exist"""
        if not os.path.exists(self.daily_pnl_file) or os.path.getsize(self.daily_pnl_file) == 0:
            columns = [
                'date', 'total_trades', 'winning_trades', 'losing_trades', 
                'win_rate', 'total_pnl', 'average_pnl', 'max_drawdown', 
                'profit_factor', 'notes'
            ]
            pd.DataFrame(columns=columns).to_csv(self.daily_pnl_file, index=False)
            logger.info(f"Created daily PnL log file at {self.daily_pnl_file}")
    
    def log_trade(self, trade):
        """
        Log a completed trade to the trades CSV file
        
        Args:
            trade: Dictionary containing trade details
        """
        try:
            # Extract needed data and format for CSV
            entry_time = datetime.fromisoformat(trade['entry_time'])
            exit_time = datetime.fromisoformat(trade['exit_time'])
            trade_duration = (exit_time - entry_time).total_seconds() / 60  # in minutes
            
            trade_record = {
                'timestamp': exit_time.strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': trade['symbol'],
                'side': trade['direction'],
                'entry_price': trade['entry_price'],
                'exit_price': trade['exit_price'],
                'quantity': trade['position_size'],
                'pnl': trade['pnl'],
                'pnl_percentage': trade['pnl_pct'],
                'trade_duration': round(trade_duration, 2),
                'strategy_name': trade.get('setup_type', 'UNKNOWN'),
                'notes': trade.get('reason', '')
            }
            
            # Append to trades CSV
            df = pd.DataFrame([trade_record])
            df.to_csv(self.trades_file, mode='a', header=False, index=False)
            
            # Store in today's trades cache for daily metrics
            self.todays_trades.append(trade_record)
            
            # Update daily metrics if needed
            today = date.today()
            if self.last_daily_update != today:
                self.calculate_daily_metrics(force_update=True)
                
            logger.info(f"Logged trade for {trade['symbol']} with PnL: ${trade['pnl']:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging trade: {str(e)}")
            return False
    
    def calculate_daily_metrics(self, specific_date=None, force_update=False):
        """
        Calculate daily performance metrics and log them
        
        Args:
            specific_date: Optional date to calculate metrics for
            force_update: Whether to force an update even if already done today
        """
        try:
            today = date.today()
            target_date = specific_date if specific_date else today
            
            # Skip if already updated today unless forced
            if self.last_daily_update == target_date and not force_update:
                return
                
            # If calculating for a different day, reload from CSV
            if target_date != today or not self.todays_trades:
                # Load trades for the target date from CSV
                all_trades = pd.read_csv(self.trades_file)
                date_str = target_date.strftime('%Y-%m-%d')
                day_trades = all_trades[all_trades['timestamp'].str.startswith(date_str)]
                
                if len(day_trades) == 0:
                    logger.info(f"No trades found for {date_str}, skipping daily metrics calculation")
                    return
                    
                trades_list = day_trades.to_dict('records')
            else:
                trades_list = self.todays_trades
                
            # Calculate metrics
            total_trades = len(trades_list)
            winning_trades = sum(1 for t in trades_list if t['pnl'] > 0)
            losing_trades = sum(1 for t in trades_list if t['pnl'] <= 0)
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            total_pnl = sum(t['pnl'] for t in trades_list)
            average_pnl = total_pnl / total_trades if total_trades > 0 else 0
            
            # Calculate drawdown and profit factor
            gross_profit = sum(t['pnl'] for t in trades_list if t['pnl'] > 0)
            gross_loss = abs(sum(t['pnl'] for t in trades_list if t['pnl'] < 0))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else (float('inf') if gross_profit > 0 else 0)
            
            # Calculate max drawdown (simplified)
            cumulative_pnl = 0
            max_pnl = 0
            max_drawdown = 0
            
            for trade in trades_list:
                cumulative_pnl += trade['pnl']
                max_pnl = max(max_pnl, cumulative_pnl)
                drawdown = max_pnl - cumulative_pnl
                max_drawdown = max(max_drawdown, drawdown)
            
            # Create daily record
            date_str = target_date.strftime('%Y-%m-%d')
            daily_record = {
                'date': date_str,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 2),
                'total_pnl': round(total_pnl, 2),
                'average_pnl': round(average_pnl, 2),
                'max_drawdown': round(max_drawdown, 2),
                'profit_factor': round(profit_factor, 2),
                'notes': ''
            }
            
            # Check if this date already exists in the file
            if os.path.exists(self.daily_pnl_file) and os.path.getsize(self.daily_pnl_file) > 0:
                daily_df = pd.read_csv(self.daily_pnl_file)
                if date_str in daily_df['date'].values:
                    # Update existing record - fix the error here
                    daily_df.loc[daily_df['date'] == date_str, daily_record.keys()] = list(daily_record.values())
                    daily_df.to_csv(self.daily_pnl_file, index=False)
                else:
                    # Append new record
                    pd.DataFrame([daily_record]).to_csv(self.daily_pnl_file, mode='a', header=False, index=False)
            else:
                # Create new file with this record
                pd.DataFrame([daily_record]).to_csv(self.daily_pnl_file, index=False)
            
            # Update last update timestamp
            self.last_daily_update = target_date
            
            logger.info(f"Updated daily PnL metrics for {date_str}: Win rate: {win_rate:.1f}%, Total PnL: ${total_pnl:.2f}")
            
            # Reset today's trades if calculating for today
            if target_date == today:
                self.todays_trades = []
                
            return daily_record
                
        except Exception as e:
            logger.error(f"Error calculating daily metrics: {str(e)}")
            return None
            
    def get_daily_stats(self, start_date=None, end_date=None):
        """
        Retrieve daily statistics for a date range
        
        Args:
            start_date: Optional start date for the range
            end_date: Optional end date for the range
            
        Returns:
            DataFrame with daily stats
        """
        try:
            if not os.path.exists(self.daily_pnl_file) or os.path.getsize(self.daily_pnl_file) == 0:
                logger.warning("Daily PnL file is empty or doesn't exist")
                return pd.DataFrame()
                
            daily_df = pd.read_csv(self.daily_pnl_file)
            
            if start_date:
                daily_df = daily_df[daily_df['date'] >= start_date.strftime('%Y-%m-%d')]
                
            if end_date:
                daily_df = daily_df[daily_df['date'] <= end_date.strftime('%Y-%m-%d')]
                
            return daily_df
            
        except Exception as e:
            logger.error(f"Error retrieving daily stats: {str(e)}")
            return pd.DataFrame()
            
    def get_trade_history(self, symbol=None, start_date=None, end_date=None, limit=None):
        """
        Retrieve trade history with optional filtering
        
        Args:
            symbol: Optional symbol to filter by
            start_date: Optional start date for the range
            end_date: Optional end date for the range
            limit: Optional limit on number of records
            
        Returns:
            DataFrame with trade history
        """
        try:
            if not os.path.exists(self.trades_file) or os.path.getsize(self.trades_file) == 0:
                logger.warning("Trades file is empty or doesn't exist")
                return pd.DataFrame()
                
            trades_df = pd.read_csv(self.trades_file)
            
            # Apply filters
            if symbol:
                trades_df = trades_df[trades_df['symbol'] == symbol]
                
            if start_date:
                start_str = start_date.strftime('%Y-%m-%d')
                trades_df = trades_df[trades_df['timestamp'] >= start_str]
                
            if end_date:
                end_str = end_date.strftime('%Y-%m-%d')
                trades_df = trades_df[trades_df['timestamp'] <= end_str + " 23:59:59"]
                
            # Sort by timestamp descending and apply limit
            trades_df = trades_df.sort_values('timestamp', ascending=False)
            
            if limit:
                trades_df = trades_df.head(limit)
                
            return trades_df
            
        except Exception as e:
            logger.error(f"Error retrieving trade history: {str(e)}")
            return pd.DataFrame() 