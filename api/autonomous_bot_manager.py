"""
Autonomous Bot Manager.

This module implements a manager for an AI-powered autonomous trading bot.
The manager provides an interface to control the bot, access its state,
and retrieve trading information.
"""

import os
import logging
import threading
import time
import json
import csv
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# Singleton instance
_bot_manager_instance = None

def get_bot_manager():
    """Get the singleton instance of the bot manager."""
    global _bot_manager_instance
    if _bot_manager_instance is None:
        _bot_manager_instance = AutonomousBotManager()
    return _bot_manager_instance

class AutonomousBotManager:
    """Manager for the autonomous trading bot."""
    
    def __init__(self):
        """Initialize the bot manager."""
        self.running = False
        self.trading_thread = None
        self.stop_event = threading.Event()
        self.cycle_interval = 300  # 5 minutes between trading cycles
        self.data_dir = Path('data')
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Initialize files if they don't exist
        self._initialize_data_files()
        
        logger.info("Autonomous Bot Manager initialized")
    
    def _initialize_data_files(self):
        """Initialize data files if they don't exist."""
        # Active trades file
        active_trades_file = self.data_dir / 'active_trades.csv'
        if not os.path.exists(active_trades_file):
            with open(active_trades_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['symbol', 'entry_date', 'entry_price', 'current_price', 
                                'quantity', 'pnl', 'pnl_percent', 'position_type', 
                                'stop_loss', 'take_profit', 'strategy'])
        
        # Trading history file
        history_file = self.data_dir / 'trading_history.csv'
        if not os.path.exists(history_file):
            with open(history_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['symbol', 'entry_date', 'exit_date', 'entry_price', 
                                'exit_price', 'quantity', 'pnl', 'pnl_percent', 
                                'position_type', 'strategy', 'exit_reason'])
        
        # Portfolio performance file
        performance_file = self.data_dir / 'portfolio_performance.csv'
        if not os.path.exists(performance_file):
            with open(performance_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['date', 'portfolio_value', 'cash_balance', 
                                'invested_amount', 'daily_pnl', 'daily_pnl_percent'])
            
            # Initialize with 30 days of mock data
            start_date = datetime.now() - timedelta(days=30)
            portfolio_value = 100000.0  # Starting value
            cash_balance = 70000.0      # Starting cash
            invested_amount = 30000.0   # Starting investment
            
            with open(performance_file, 'a', newline='') as f:
                writer = csv.writer(f)
                for i in range(30):
                    current_date = start_date + timedelta(days=i)
                    # Small random daily change (-2% to +2%)
                    daily_change = random.uniform(-0.02, 0.025) 
                    daily_pnl = invested_amount * daily_change
                    portfolio_value += daily_pnl
                    invested_amount += daily_pnl
                    
                    writer.writerow([
                        current_date.strftime('%Y-%m-%d'),
                        round(portfolio_value, 2),
                        round(cash_balance, 2),
                        round(invested_amount, 2),
                        round(daily_pnl, 2),
                        round(daily_change * 100, 2)  # Percentage
                    ])
    
    def get_bot_status(self):
        """Get the current status of the bot."""
        return {
            'running': self.running,
            'last_cycle': getattr(self, 'last_cycle_time', None),
            'next_cycle': getattr(self, 'next_cycle_time', None) if self.running else None,
            'active_trades_count': len(self.get_active_trades())
        }
    
    def start_bot(self):
        """Start the autonomous trading bot."""
        if self.running:
            return False, "Bot is already running"
        
        self.running = True
        self.stop_event.clear()
        self.trading_thread = threading.Thread(target=self._trading_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
        
        logger.info("Autonomous trading bot started")
        return True, "Bot started successfully"
    
    def stop_bot(self):
        """Stop the autonomous trading bot."""
        if not self.running:
            return False, "Bot is not running"
        
        self.running = False
        self.stop_event.set()
        if self.trading_thread:
            self.trading_thread.join(timeout=10)
        
        logger.info("Autonomous trading bot stopped")
        return True, "Bot stopped successfully"
    
    def _trading_loop(self):
        """Main trading loop that runs continuously while the bot is active."""
        while not self.stop_event.is_set():
            try:
                self.last_cycle_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.next_cycle_time = (datetime.now() + timedelta(seconds=self.cycle_interval)).strftime('%Y-%m-%d %H:%M:%S')
                
                # Run a trading cycle
                self.run_trading_cycle()
                
                # Update portfolio performance
                self._update_portfolio_performance()
                
                # Sleep until the next cycle
                for _ in range(self.cycle_interval):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
            
            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                time.sleep(10)  # Sleep briefly before retrying
    
    def run_trading_cycle(self):
        """Run a single trading cycle."""
        try:
            logger.info("Running trading cycle")
            
            # 1. Analyze market conditions
            # 2. Update active trade prices
            self._update_active_trade_prices()
            # 3. Check for exit conditions
            self._check_exit_conditions()
            # 4. Look for new trade opportunities
            self._find_new_trades()
            
            return True, "Trading cycle completed successfully"
        
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
            return False, f"Error in trading cycle: {str(e)}"
    
    def _update_active_trade_prices(self):
        """Update current prices for all active trades."""
        try:
            active_trades_file = self.data_dir / 'active_trades.csv'
            
            if not os.path.exists(active_trades_file):
                return
            
            # Read active trades
            active_trades = pd.read_csv(active_trades_file)
            
            if active_trades.empty:
                return
            
            # Update current prices and P&L
            for idx, trade in active_trades.iterrows():
                # Simulate price change (-1% to +1%)
                price_change = random.uniform(-0.01, 0.012)
                new_price = trade['current_price'] * (1 + price_change)
                
                # Calculate new P&L
                pnl = (new_price - trade['entry_price']) * trade['quantity']
                if trade['position_type'].lower() == 'short':
                    pnl = -pnl
                
                pnl_percent = (pnl / (trade['entry_price'] * trade['quantity'])) * 100
                
                # Update trade
                active_trades.loc[idx, 'current_price'] = round(new_price, 2)
                active_trades.loc[idx, 'pnl'] = round(pnl, 2)
                active_trades.loc[idx, 'pnl_percent'] = round(pnl_percent, 2)
            
            # Save updated trades
            active_trades.to_csv(active_trades_file, index=False)
            logger.info(f"Updated prices for {len(active_trades)} active trades")
            
        except Exception as e:
            logger.error(f"Error updating active trade prices: {str(e)}")
    
    def _check_exit_conditions(self):
        """Check if any active trades should be closed."""
        try:
            active_trades_file = self.data_dir / 'active_trades.csv'
            history_file = self.data_dir / 'trading_history.csv'
            
            if not os.path.exists(active_trades_file):
                return
            
            # Read active trades
            active_trades = pd.read_csv(active_trades_file)
            
            if active_trades.empty:
                return
            
            # Identify trades to close
            trades_to_close = []
            for idx, trade in active_trades.iterrows():
                # Check stop loss
                if trade['position_type'].lower() == 'long' and trade['current_price'] <= trade['stop_loss']:
                    trades_to_close.append((idx, trade, 'stop_loss'))
                elif trade['position_type'].lower() == 'short' and trade['current_price'] >= trade['stop_loss']:
                    trades_to_close.append((idx, trade, 'stop_loss'))
                
                # Check take profit
                elif trade['position_type'].lower() == 'long' and trade['current_price'] >= trade['take_profit']:
                    trades_to_close.append((idx, trade, 'take_profit'))
                elif trade['position_type'].lower() == 'short' and trade['current_price'] <= trade['take_profit']:
                    trades_to_close.append((idx, trade, 'take_profit'))
                
                # Random decision to close trade (5% chance)
                elif random.random() < 0.05:
                    trades_to_close.append((idx, trade, 'algorithm_decision'))
            
            # Close trades and update history
            if trades_to_close:
                # Read trading history
                if os.path.exists(history_file):
                    trading_history = pd.read_csv(history_file)
                else:
                    trading_history = pd.DataFrame(columns=['symbol', 'entry_date', 'exit_date', 'entry_price', 
                                                          'exit_price', 'quantity', 'pnl', 'pnl_percent', 
                                                          'position_type', 'strategy', 'exit_reason'])
                
                # Process each trade to close
                indices_to_drop = []
                for idx, trade, reason in trades_to_close:
                    # Add to history
                    history_entry = {
                        'symbol': trade['symbol'],
                        'entry_date': trade['entry_date'],
                        'exit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'entry_price': trade['entry_price'],
                        'exit_price': trade['current_price'],
                        'quantity': trade['quantity'],
                        'pnl': trade['pnl'],
                        'pnl_percent': trade['pnl_percent'],
                        'position_type': trade['position_type'],
                        'strategy': trade['strategy'],
                        'exit_reason': reason
                    }
                    trading_history = pd.concat([trading_history, pd.DataFrame([history_entry])], ignore_index=True)
                    indices_to_drop.append(idx)
                
                # Remove closed trades from active trades
                active_trades = active_trades.drop(indices_to_drop).reset_index(drop=True)
                
                # Save updated files
                active_trades.to_csv(active_trades_file, index=False)
                trading_history.to_csv(history_file, index=False)
                
                logger.info(f"Closed {len(trades_to_close)} trades")
        
        except Exception as e:
            logger.error(f"Error checking exit conditions: {str(e)}")
    
    def _find_new_trades(self):
        """Look for new trading opportunities."""
        try:
            active_trades_file = self.data_dir / 'active_trades.csv'
            
            # Read active trades
            if os.path.exists(active_trades_file):
                active_trades = pd.read_csv(active_trades_file)
            else:
                active_trades = pd.DataFrame(columns=['symbol', 'entry_date', 'entry_price', 'current_price', 
                                                    'quantity', 'pnl', 'pnl_percent', 'position_type', 
                                                    'stop_loss', 'take_profit', 'strategy'])
            
            # List of potential symbols
            potential_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 
                              'JPM', 'V', 'JNJ', 'WMT', 'PG', 'XOM', 'BAC', 'ADBE',
                              'CRM', 'PYPL', 'NFLX', 'DIS', 'INTC']
            
            # Strategies
            strategies = ['Trend Following', 'Mean Reversion', 'Breakout', 'MACD Crossover', 
                        'Volatility Expansion', 'RSI Divergence', 'Support/Resistance', 
                        'Momentum', 'Moving Average Crossover']
            
            # Active symbols
            active_symbols = set(active_trades['symbol']) if not active_trades.empty else set()
            
            # Available symbols (not already in active trades)
            available_symbols = [s for s in potential_symbols if s not in active_symbols]
            
            # Random decision to enter new trades (30% chance)
            if random.random() < 0.3 and available_symbols:
                # Number of new trades to open (1-3)
                num_new_trades = random.randint(1, min(3, len(available_symbols)))
                
                new_trades = []
                for _ in range(num_new_trades):
                    # Select random symbol
                    symbol = random.choice(available_symbols)
                    available_symbols.remove(symbol)
                    
                    # Generate random price between $50 and $500
                    entry_price = round(random.uniform(50, 500), 2)
                    
                    # Long or short (70% long, 30% short)
                    position_type = 'Long' if random.random() < 0.7 else 'Short'
                    
                    # Quantity between 10 and 100
                    quantity = random.randint(10, 100)
                    
                    # Stop loss (2-5% away from entry)
                    stop_loss_pct = random.uniform(0.02, 0.05)
                    stop_loss = round(entry_price * (1 - stop_loss_pct) if position_type == 'Long' 
                                     else entry_price * (1 + stop_loss_pct), 2)
                    
                    # Take profit (5-15% away from entry)
                    take_profit_pct = random.uniform(0.05, 0.15)
                    take_profit = round(entry_price * (1 + take_profit_pct) if position_type == 'Long' 
                                       else entry_price * (1 - take_profit_pct), 2)
                    
                    # Strategy
                    strategy = random.choice(strategies)
                    
                    # New trade
                    new_trade = {
                        'symbol': symbol,
                        'entry_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'entry_price': entry_price,
                        'current_price': entry_price,
                        'quantity': quantity,
                        'pnl': 0.0,
                        'pnl_percent': 0.0,
                        'position_type': position_type,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'strategy': strategy
                    }
                    new_trades.append(new_trade)
                
                # Add new trades to active trades
                if new_trades:
                    active_trades = pd.concat([active_trades, pd.DataFrame(new_trades)], ignore_index=True)
                    active_trades.to_csv(active_trades_file, index=False)
                    logger.info(f"Opened {len(new_trades)} new trades")
        
        except Exception as e:
            logger.error(f"Error finding new trades: {str(e)}")
    
    def _update_portfolio_performance(self):
        """Update the portfolio performance record."""
        try:
            performance_file = self.data_dir / 'portfolio_performance.csv'
            active_trades_file = self.data_dir / 'active_trades.csv'
            
            # Read performance history
            if os.path.exists(performance_file):
                performance = pd.read_csv(performance_file)
                last_record = performance.iloc[-1]
            else:
                # Initialize with base values if file doesn't exist
                performance = pd.DataFrame(columns=['date', 'portfolio_value', 'cash_balance', 
                                                   'invested_amount', 'daily_pnl', 'daily_pnl_percent'])
                last_record = {
                    'portfolio_value': 100000.0,
                    'cash_balance': 70000.0,
                    'invested_amount': 30000.0,
                    'daily_pnl': 0.0,
                    'daily_pnl_percent': 0.0
                }
            
            # Calculate current portfolio value
            current_cash = last_record['cash_balance']
            
            # Add value of active trades
            invested_amount = 0
            if os.path.exists(active_trades_file):
                active_trades = pd.read_csv(active_trades_file)
                if not active_trades.empty:
                    for _, trade in active_trades.iterrows():
                        position_value = trade['current_price'] * trade['quantity']
                        invested_amount += position_value
            
            # Calculate portfolio value and daily change
            current_portfolio_value = current_cash + invested_amount
            daily_pnl = current_portfolio_value - last_record['portfolio_value']
            daily_pnl_percent = (daily_pnl / last_record['portfolio_value']) * 100 if last_record['portfolio_value'] > 0 else 0
            
            # Create new record
            today = datetime.now().strftime('%Y-%m-%d')
            if performance.empty or performance.iloc[-1]['date'] != today:
                new_record = {
                    'date': today,
                    'portfolio_value': round(current_portfolio_value, 2),
                    'cash_balance': round(current_cash, 2),
                    'invested_amount': round(invested_amount, 2),
                    'daily_pnl': round(daily_pnl, 2),
                    'daily_pnl_percent': round(daily_pnl_percent, 2)
                }
                
                performance = pd.concat([performance, pd.DataFrame([new_record])], ignore_index=True)
                performance.to_csv(performance_file, index=False)
                logger.info(f"Updated portfolio performance for {today}")
        
        except Exception as e:
            logger.error(f"Error updating portfolio performance: {str(e)}")
    
    def get_active_trades(self):
        """Get all active trades."""
        active_trades_file = self.data_dir / 'active_trades.csv'
        
        if not os.path.exists(active_trades_file):
            return []
        
        try:
            active_trades = pd.read_csv(active_trades_file)
            return active_trades.to_dict('records')
        except Exception as e:
            logger.error(f"Error reading active trades: {str(e)}")
            return []
    
    def get_trading_history(self, limit=None):
        """Get trading history."""
        history_file = self.data_dir / 'trading_history.csv'
        
        if not os.path.exists(history_file):
            return []
        
        try:
            trading_history = pd.read_csv(history_file)
            if limit and limit > 0:
                trading_history = trading_history.tail(limit)
            return trading_history.to_dict('records')
        except Exception as e:
            logger.error(f"Error reading trading history: {str(e)}")
            return []
    
    def get_portfolio_info(self):
        """Get current portfolio information."""
        try:
            performance_file = self.data_dir / 'portfolio_performance.csv'
            active_trades_file = self.data_dir / 'active_trades.csv'
            history_file = self.data_dir / 'trading_history.csv'
            
            # Get portfolio performance
            if os.path.exists(performance_file):
                performance = pd.read_csv(performance_file)
                if not performance.empty:
                    latest = performance.iloc[-1]
                    portfolio_info = {
                        'portfolio_value': latest['portfolio_value'],
                        'cash_balance': latest['cash_balance'],
                        'invested_amount': latest['invested_amount'],
                    }
                else:
                    portfolio_info = {'portfolio_value': 0, 'cash_balance': 0, 'invested_amount': 0}
            else:
                portfolio_info = {'portfolio_value': 0, 'cash_balance': 0, 'invested_amount': 0}
            
            # Count active trades
            active_trades_count = 0
            if os.path.exists(active_trades_file):
                active_trades = pd.read_csv(active_trades_file)
                active_trades_count = len(active_trades)
            
            # Calculate total profit/loss from closed trades
            realized_pnl = 0
            if os.path.exists(history_file):
                history = pd.read_csv(history_file)
                if not history.empty:
                    realized_pnl = history['pnl'].sum()
            
            # Calculate unrealized profit/loss from active trades
            unrealized_pnl = 0
            if os.path.exists(active_trades_file):
                active_trades = pd.read_csv(active_trades_file)
                if not active_trades.empty:
                    unrealized_pnl = active_trades['pnl'].sum()
            
            # Add additional information
            portfolio_info.update({
                'active_trades_count': active_trades_count,
                'realized_pnl': round(realized_pnl, 2),
                'unrealized_pnl': round(unrealized_pnl, 2),
                'total_pnl': round(realized_pnl + unrealized_pnl, 2)
            })
            
            return portfolio_info
        
        except Exception as e:
            logger.error(f"Error getting portfolio info: {str(e)}")
            return {
                'portfolio_value': 0,
                'cash_balance': 0,
                'invested_amount': 0,
                'active_trades_count': 0,
                'realized_pnl': 0,
                'unrealized_pnl': 0,
                'total_pnl': 0
            }
    
    def get_portfolio_performance(self, days=30):
        """Get historical portfolio performance."""
        performance_file = self.data_dir / 'portfolio_performance.csv'
        
        if not os.path.exists(performance_file):
            return []
        
        try:
            performance = pd.read_csv(performance_file)
            if days and days > 0:
                performance = performance.tail(days)
            return performance.to_dict('records')
        except Exception as e:
            logger.error(f"Error reading portfolio performance: {str(e)}")
            return [] 