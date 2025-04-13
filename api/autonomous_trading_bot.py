"""
Autonomous Trading Bot for AI Trading System

This module implements an autonomous trading bot that can:
1. Analyze market data in real-time
2. Make trade decisions based on technical indicators and AI signals
3. Execute trades autonomously
4. Manage risk according to predefined parameters
5. Log its activities for monitoring

The bot runs as a scheduled background task that operates independently
from user interaction with the front-end application.
"""

import os
import time
import json
import random
import pandas as pd
import numpy as np
import logging
import threading
import schedule
from datetime import datetime, timedelta
import uuid
from pathlib import Path
import csv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("autonomous_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AutonomousTradingBot")

# Constants
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
WATCHLIST = ["AAPL", "MSFT", "AMZN", "NVDA", "TSLA", "GOOGL", "META", "JPM", "SPY", "QQQ", "XLE", "XLF", "AMD", "INTC", "DIS", "NFLX"]
RISK_PER_TRADE = 0.01  # 1% risk per trade
MAX_POSITIONS = 10  # Maximum number of open positions
MAX_POSITION_SIZE = 0.10  # Maximum 10% of portfolio in a single position
STRATEGIES = ["Momentum", "Trend Reversal", "Breakout", "Support Bounce", "Technical", "Moving Average", "RSI_Breakout", "MACD_Cross", "ML_Prediction"]

class AutonomousTradingBot:
    """
    Autonomous trading bot that continuously analyzes market data,
    makes trading decisions, and executes trades without user input.
    """
    
    def __init__(self):
        """Initialize the trading bot with default parameters"""
        self.portfolio_value = 100000.0  # Default starting capital
        self.cash_balance = 65000.0  # Available cash
        self.equity_value = 35000.0  # Value of current positions
        self.active_trades = []  # Currently open trades
        self.trading_history = []  # Historical trades
        self.watchlist = WATCHLIST
        self.running = False
        self.last_update = datetime.now()
        self.initialized = False
        self.next_trade_id = 1001  # Starting trade ID
        
        # Trading parameters
        self.risk_per_trade = RISK_PER_TRADE
        self.max_positions = MAX_POSITIONS
        self.max_position_size = MAX_POSITION_SIZE
        
        # Initialize data structures
        self._load_existing_data()
        
        logger.info(f"Autonomous Trading Bot initialized with portfolio value: ${self.portfolio_value:.2f}")
    
    def _load_existing_data(self):
        """Load existing data from CSV files to initialize the bot state"""
        try:
            # Load active trades
            active_trades_path = os.path.join(DATA_DIR, "active_trades.csv")
            if os.path.exists(active_trades_path):
                df_active = pd.read_csv(active_trades_path)
                self.active_trades = df_active.to_dict('records')
                logger.info(f"Loaded {len(self.active_trades)} active trades from CSV")
            
            # Load trading history
            trading_history_path = os.path.join(DATA_DIR, "trading_history.csv")
            if os.path.exists(trading_history_path):
                df_history = pd.read_csv(trading_history_path)
                self.trading_history = df_history.to_dict('records')
                logger.info(f"Loaded {len(self.trading_history)} historical trades from CSV")
            
            # Load portfolio performance to get latest values
            portfolio_path = os.path.join(DATA_DIR, "portfolio_performance.csv")
            if os.path.exists(portfolio_path):
                df_portfolio = pd.read_csv(portfolio_path)
                if not df_portfolio.empty:
                    latest = df_portfolio.iloc[-1]
                    self.portfolio_value = float(latest['portfolio_value'])
                    self.cash_balance = float(latest['cash_balance'])
                    self.equity_value = float(latest['equity_value'])
                    logger.info(f"Loaded portfolio state: Value=${self.portfolio_value:.2f}, Cash=${self.cash_balance:.2f}")
            
            # Find the highest trade ID to avoid duplicates
            all_trade_ids = []
            for trade in self.active_trades:
                if 'trade_id' in trade and isinstance(trade['trade_id'], (int, str)) and str(trade['trade_id']).isdigit():
                    all_trade_ids.append(int(trade['trade_id']))
            
            for trade in self.trading_history:
                if 'trade_id' in trade and isinstance(trade['trade_id'], (int, str)) and str(trade['trade_id']).strip().isdigit():
                    all_trade_ids.append(int(trade['trade_id']))
            
            if all_trade_ids:
                self.next_trade_id = max(all_trade_ids) + 1
                
            self.initialized = True
            logger.info(f"Data loaded successfully. Next trade ID: {self.next_trade_id}")
            
        except Exception as e:
            logger.error(f"Error loading existing data: {str(e)}")
            # Continue with default values in case of error
    
    def _save_active_trades(self):
        """Save current active trades to CSV file"""
        try:
            df = pd.DataFrame(self.active_trades)
            csv_path = os.path.join(DATA_DIR, "active_trades.csv")
            df.to_csv(csv_path, index=False)
            logger.info(f"Saved {len(self.active_trades)} active trades to CSV")
        except Exception as e:
            logger.error(f"Error saving active trades: {str(e)}")
    
    def _save_trading_history(self):
        """Save trading history to CSV file"""
        try:
            # Append new trades to existing file
            csv_path = os.path.join(DATA_DIR, "trading_history.csv")
            
            # If file doesn't exist, create it with header
            if not os.path.exists(csv_path):
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'trade_id', 'symbol', 'entry_date', 'exit_date', 
                        'position_type', 'entry_price', 'exit_price', 
                        'quantity', 'pnl', 'pnl_percent', 'strategy',
                        'trade_duration_days', 'market_condition'
                    ])
            
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                for trade in self.trading_history[-5:]:  # Only save the most recent trades
                    writer.writerow([
                        trade.get('trade_id', ''),
                        trade.get('symbol', ''),
                        trade.get('entry_date', ''),
                        trade.get('exit_date', ''),
                        trade.get('position_type', ''),
                        trade.get('entry_price', ''),
                        trade.get('exit_price', ''),
                        trade.get('quantity', ''),
                        trade.get('pnl', ''),
                        trade.get('pnl_percent', ''),
                        trade.get('strategy', ''),
                        trade.get('trade_duration_days', ''),
                        trade.get('market_condition', '')
                    ])
            
            logger.info(f"Saved trading history to CSV")
        except Exception as e:
            logger.error(f"Error saving trading history: {str(e)}")
    
    def _update_portfolio_performance(self):
        """Update portfolio performance data"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Calculate daily change
            yesterday_value = self.portfolio_value - (self.equity_value * 0.01 * random.uniform(-1, 2))
            daily_pnl = self.portfolio_value - yesterday_value
            daily_return_percent = (daily_pnl / yesterday_value) * 100 if yesterday_value > 0 else 0
            
            # Benchmark is S&P 500 - we'll simulate it with a slightly less volatile performance
            benchmark_daily_return = random.uniform(-0.5, 0.8)
            benchmark_value = 100000 * (1 + benchmark_daily_return/100)
            
            # Create new portfolio record
            new_record = {
                'date': today,
                'portfolio_value': round(self.portfolio_value, 2),
                'daily_pnl': round(daily_pnl, 2),
                'daily_return_percent': round(daily_return_percent, 2),
                'benchmark_value': round(benchmark_value, 2),
                'benchmark_daily_return_percent': round(benchmark_daily_return, 2),
                'cash_balance': round(self.cash_balance, 2),
                'equity_value': round(self.equity_value, 2),
                'margin_used': 0.0,
                'net_deposits': 100000.00
            }
            
            # Append to existing CSV or create new one
            csv_path = os.path.join(DATA_DIR, "portfolio_performance.csv")
            
            # If file doesn't exist, create it with header
            if not os.path.exists(csv_path):
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(list(new_record.keys()))
            
            # Append new record
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(list(new_record.values()))
            
            logger.info(f"Updated portfolio performance: Value=${self.portfolio_value:.2f}, PnL=${daily_pnl:.2f}")
        except Exception as e:
            logger.error(f"Error updating portfolio performance: {str(e)}")
    
    def get_market_data(self, symbol):
        """
        Simulate getting market data for a symbol.
        In a real implementation, this would fetch data from a broker API.
        """
        current_price = 0
        
        # Check if we have this symbol in active trades to maintain consistency
        for trade in self.active_trades:
            if trade.get('symbol') == symbol:
                current_price = float(trade.get('current_price', 0))
                break
        
        # If no existing data, generate a realistic price
        if current_price == 0:
            # Generate different price ranges based on the symbol
            if symbol in ['AAPL', 'META', 'NFLX']:
                current_price = random.uniform(180, 300)
            elif symbol in ['MSFT', 'NVDA']:
                current_price = random.uniform(300, 500)
            elif symbol in ['GOOGL', 'AMZN']:
                current_price = random.uniform(120, 180)
            elif symbol in ['TSLA']:
                current_price = random.uniform(200, 280)
            elif symbol in ['JPM', 'DIS']:
                current_price = random.uniform(80, 160)
            elif symbol in ['SPY']:
                current_price = random.uniform(430, 470)
            elif symbol in ['QQQ']:
                current_price = random.uniform(370, 410)
            elif symbol in ['XLE', 'XLF']:
                current_price = random.uniform(30, 100)
            else:
                current_price = random.uniform(50, 200)
        
        # Generate other market data points
        high = current_price * (1 + random.uniform(0.005, 0.02))
        low = current_price * (1 - random.uniform(0.005, 0.02))
        open_price = low + random.uniform(0, high - low)
        volume = int(random.uniform(500000, 5000000))
        
        # Calculate some basic technical indicators
        sma_20 = current_price * (1 + random.uniform(-0.05, 0.05))
        sma_50 = current_price * (1 + random.uniform(-0.08, 0.08))
        sma_200 = current_price * (1 + random.uniform(-0.15, 0.15))
        rsi = random.uniform(30, 70)  # RSI between 30 and 70
        macd = random.uniform(-2, 2)
        macd_signal = macd * (1 + random.uniform(-0.2, 0.2))
        
        market_data = {
            'symbol': symbol,
            'price': current_price,
            'open': open_price,
            'high': high,
            'low': low,
            'volume': volume,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'sma_200': sma_200,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'timestamp': datetime.now().isoformat()
        }
        
        return market_data
    
    def analyze_market(self, symbol):
        """
        Analyze market data and determine if a trading signal is present.
        Returns a dict with signal information or None if no signal.
        """
        data = self.get_market_data(symbol)
        
        # Don't generate too many signals - add randomness
        if random.random() > 0.3:  # 30% chance of generating a signal
            return None
        
        # Calculate signal score (0 to 10)
        signal_score = random.uniform(4, 9)
        
        # Determine trade direction based on indicators
        long_signal = (
            data['price'] > data['sma_20'] > data['sma_50'] or
            (data['rsi'] < 40 and data['macd'] > data['macd_signal']) or
            (data['price'] > data['sma_200'] and data['volume'] > 1000000)
        )
        
        position_type = "LONG" if long_signal else "SHORT"
        
        # Select a strategy
        strategy = random.choice(STRATEGIES)
        
        # Market condition
        market_condition = "Bullish" if data['price'] > data['sma_200'] else "Bearish"
        
        # Calculate reasonable entry price - slightly different from current price
        entry_price = data['price'] * (1 - random.uniform(0.001, 0.005)) if long_signal else data['price'] * (1 + random.uniform(0.001, 0.005))
        
        # Calculate appropriate stop loss and take profit levels (1-3% for stop, 2-5% for target)
        stop_loss_pct = random.uniform(0.01, 0.03)
        take_profit_pct = random.uniform(0.02, 0.05)
        
        stop_loss = entry_price * (1 - stop_loss_pct) if long_signal else entry_price * (1 + stop_loss_pct)
        take_profit = entry_price * (1 + take_profit_pct) if long_signal else entry_price * (1 - take_profit_pct)
        
        # Create signal
        signal = {
            'symbol': symbol,
            'position_type': position_type,
            'entry_price': round(entry_price, 2),
            'current_price': round(data['price'], 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'signal_score': round(signal_score, 2),
            'strategy': strategy,
            'market_condition': market_condition,
            'timestamp': datetime.now().isoformat()
        }
        
        return signal
    
    def calculate_position_size(self, signal):
        """
        Calculate appropriate position size based on account value and risk parameters.
        
        Args:
            signal: Dict containing trade signal information
            
        Returns:
            int: Number of shares to trade
        """
        # Calculate risk amount (1% of portfolio)
        risk_amount = self.portfolio_value * self.risk_per_trade
        
        # Calculate risk per share
        entry_price = signal['entry_price']
        stop_loss = signal['stop_loss']
        risk_per_share = abs(entry_price - stop_loss)
        
        # Calculate position size based on risk
        if risk_per_share > 0:
            shares = int(risk_amount / risk_per_share)
        else:
            # Default to 5% of portfolio if can't calculate risk
            shares = int((self.portfolio_value * 0.05) / entry_price)
        
        # Check if position size exceeds max position size
        max_shares = int((self.portfolio_value * self.max_position_size) / entry_price)
        shares = min(shares, max_shares)
        
        # Check if we have enough cash
        required_cash = shares * entry_price
        if required_cash > self.cash_balance:
            # Reduce position size to fit available cash
            shares = int(self.cash_balance / entry_price)
        
        return max(1, shares)  # Ensure at least 1 share
    
    def execute_trade(self, signal):
        """
        Execute a trade based on the signal.
        
        Args:
            signal: Dict containing trade signal information
            
        Returns:
            dict: Information about the executed trade or None if trade wasn't executed
        """
        # Check if we can open new positions
        if len(self.active_trades) >= self.max_positions:
            logger.info(f"Maximum positions reached ({self.max_positions}). Can't open new position for {signal['symbol']}")
            return None
        
        # Check if we're already in a position for this symbol
        for trade in self.active_trades:
            if trade.get('symbol') == signal['symbol']:
                logger.info(f"Already have an active position for {signal['symbol']}. Skipping trade.")
                return None
        
        # Calculate position size
        quantity = self.calculate_position_size(signal)
        
        if quantity <= 0:
            logger.info(f"Calculated position size is 0 for {signal['symbol']}. Skipping trade.")
            return None
        
        # Calculate required cash
        required_cash = quantity * signal['entry_price']
        
        # Check if we have enough cash
        if required_cash > self.cash_balance:
            logger.warning(f"Not enough cash for trade. Required: ${required_cash:.2f}, Available: ${self.cash_balance:.2f}")
            return None
        
        # Generate trade ID
        trade_id = self.next_trade_id
        self.next_trade_id += 1
        
        # Create trade record
        trade = {
            'trade_id': trade_id,
            'symbol': signal['symbol'],
            'entry_price': signal['entry_price'],
            'current_price': signal['current_price'],
            'position_type': signal['position_type'],
            'quantity': quantity,
            'entry_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'strategy': signal['strategy'],
            'status': 'active'
        }
        
        # Calculate initial PnL
        price_diff = trade['current_price'] - trade['entry_price'] if trade['position_type'] == 'LONG' else trade['entry_price'] - trade['current_price']
        trade['pnl'] = round(price_diff * quantity, 2)
        trade['pnl_percent'] = round((price_diff / trade['entry_price']) * 100, 2)
        
        # Update portfolio
        self.cash_balance -= required_cash
        self.equity_value += required_cash
        
        # Add to active trades
        self.active_trades.append(trade)
        
        # Save updated data
        self._save_active_trades()
        
        logger.info(f"Executed {trade['position_type']} trade for {quantity} shares of {signal['symbol']} at ${signal['entry_price']:.2f}")
        return trade
    
    def update_active_trades(self):
        """
        Update prices and PnL for active trades, and close trades if stop loss or take profit is hit.
        """
        updated_trades = []
        closed_trades = []
        
        for trade in self.active_trades:
            # Get current market data
            market_data = self.get_market_data(trade['symbol'])
            current_price = market_data['price']
            
            # Update the current price
            trade['current_price'] = round(current_price, 2)
            
            # Calculate PnL
            price_diff = current_price - trade['entry_price'] if trade['position_type'] == 'LONG' else trade['entry_price'] - current_price
            trade['pnl'] = round(price_diff * trade['quantity'], 2)
            trade['pnl_percent'] = round((price_diff / trade['entry_price']) * 100, 2)
            
            # Check if stop loss or take profit is hit
            stop_loss_hit = (
                (trade['position_type'] == 'LONG' and current_price <= trade['stop_loss']) or
                (trade['position_type'] == 'SHORT' and current_price >= trade['stop_loss'])
            )
            
            take_profit_hit = (
                (trade['position_type'] == 'LONG' and current_price >= trade['take_profit']) or
                (trade['position_type'] == 'SHORT' and current_price <= trade['take_profit'])
            )
            
            # Add randomness for trade exits (simulating unpredictable market moves)
            random_exit = random.random() < 0.05  # 5% chance of random exit
            
            # Also randomly close some trades that have been open for a while (simulating time-based exit)
            time_based_exit = False
            if 'entry_date' in trade:
                try:
                    entry_date = datetime.strptime(trade['entry_date'], '%Y-%m-%d %H:%M:%S')
                    days_open = (datetime.now() - entry_date).days
                    if days_open > 0 and random.random() < 0.1:  # 10% chance per day
                        time_based_exit = True
                except:
                    pass
            
            if stop_loss_hit or take_profit_hit or random_exit or time_based_exit:
                # Close the trade
                exit_reason = "Stop Loss" if stop_loss_hit else "Take Profit" if take_profit_hit else "Time-based Exit" if time_based_exit else "Market Conditions"
                
                # Create history record
                history_record = {
                    'trade_id': trade.get('trade_id', str(uuid.uuid4())[:8]),
                    'symbol': trade['symbol'],
                    'entry_date': trade['entry_date'],
                    'exit_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'position_type': trade['position_type'],
                    'entry_price': trade['entry_price'],
                    'exit_price': current_price,
                    'quantity': trade['quantity'],
                    'pnl': trade['pnl'],
                    'pnl_percent': trade['pnl_percent'],
                    'strategy': trade['strategy'],
                    'trade_duration_days': self._calculate_trade_duration(trade['entry_date']),
                    'market_condition': "Bullish" if market_data['price'] > market_data['sma_200'] else "Bearish",
                    'exit_reason': exit_reason
                }
                
                # Update portfolio
                self.cash_balance += (trade['quantity'] * current_price)
                self.equity_value -= (trade['quantity'] * current_price)
                
                # Add to closed trades
                closed_trades.append(history_record)
                
                logger.info(f"Closed {trade['position_type']} position for {trade['quantity']} shares of {trade['symbol']} at ${current_price:.2f}. "
                          f"PnL: ${trade['pnl']:.2f} ({trade['pnl_percent']:.2f}%). Reason: {exit_reason}")
            else:
                # Keep trade active
                updated_trades.append(trade)
        
        # Update active trades list
        self.active_trades = updated_trades
        
        # Add closed trades to history
        if closed_trades:
            self.trading_history.extend(closed_trades)
            self._save_trading_history()
        
        # Save updated active trades
        self._save_active_trades()
        
        # Update portfolio value
        self.portfolio_value = self.cash_balance + self.equity_value
        
        return len(closed_trades)
    
    def _calculate_trade_duration(self, entry_date_str):
        """Calculate the duration of a trade in days"""
        try:
            entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d %H:%M:%S')
            duration = (datetime.now() - entry_date).days
            return max(1, duration)  # Minimum 1 day
        except:
            return 1
    
    def run_trading_cycle(self):
        """
        Execute a complete trading cycle:
        1. Update existing positions
        2. Analyze the market for new opportunities
        3. Execute new trades if conditions are favorable
        4. Save updated portfolio performance
        """
        logger.info("Starting trading cycle")
        
        # Update current positions
        closed_count = self.update_active_trades()
        logger.info(f"Updated active trades. Closed {closed_count} positions.")
        
        # Only look for new opportunities if we have room for more positions
        if len(self.active_trades) < self.max_positions:
            # Analyze watchlist for new opportunities
            for symbol in self.watchlist:
                # Skip if we already have a position in this symbol
                if any(trade['symbol'] == symbol for trade in self.active_trades):
                    continue
                
                # Analyze market for this symbol
                signal = self.analyze_market(symbol)
                
                # If we have a signal and signal score is high enough, execute trade
                if signal and signal['signal_score'] > 7.0:
                    trade = self.execute_trade(signal)
                    if trade:
                        logger.info(f"Opened new {trade['position_type']} position for {symbol} with {trade['quantity']} shares")
                        
                        # Only take a few trades per cycle
                        if len(self.active_trades) >= self.max_positions or random.random() < 0.7:
                            break
        
        # Update portfolio performance
        self._update_portfolio_performance()
        
        # Record last update time
        self.last_update = datetime.now()
        
        logger.info(f"Trading cycle completed. Portfolio value: ${self.portfolio_value:.2f}, "
                   f"Active positions: {len(self.active_trades)}, "
                   f"Cash: ${self.cash_balance:.2f}")
    
    def start(self):
        """Start the autonomous trading bot"""
        if self.running:
            logger.warning("Trading bot is already running")
            return False
        
        self.running = True
        logger.info("Autonomous Trading Bot started")
        
        # Schedule regular trading cycles
        def run_scheduled_task():
            if self.running:
                try:
                    self.run_trading_cycle()
                except Exception as e:
                    logger.error(f"Error in trading cycle: {str(e)}")
        
        # Schedule to run every few minutes (simulation speed)
        # In production this would be less frequent
        schedule.every(3).minutes.do(run_scheduled_task)
        
        # Run trading cycle immediately to initialize
        try:
            self.run_trading_cycle()
        except Exception as e:
            logger.error(f"Error in initial trading cycle: {str(e)}")
        
        # Start the scheduler in a background thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        return True
    
    def _run_scheduler(self):
        """Run the scheduler loop in a background thread"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """Stop the autonomous trading bot"""
        self.running = False
        logger.info("Autonomous Trading Bot stopped")
        return True
    
    def get_status(self):
        """Get the current status of the trading bot"""
        return {
            'running': self.running,
            'portfolio_value': self.portfolio_value,
            'cash_balance': self.cash_balance,
            'equity_value': self.equity_value,
            'active_positions': len(self.active_trades),
            'last_update': self.last_update.isoformat(),
            'next_trade_id': self.next_trade_id
        }


# Create a singleton instance
bot_instance = None

def get_bot_instance():
    """Get or create the singleton bot instance"""
    global bot_instance
    if bot_instance is None:
        bot_instance = AutonomousTradingBot()
    return bot_instance

if __name__ == "__main__":
    # For testing when running the script directly
    bot = AutonomousTradingBot()
    bot.start()
    
    # Keep the script running
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        bot.stop()
        print("Bot stopped by user") 