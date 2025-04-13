#!/usr/bin/env python
"""
Test script for the PnL logging functionality

This script tests the PnL logging system with sample trade data.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add parent directory to path to import execution_model
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from execution_model.pnl_logger import PnLLogger
from execution_model.config import get_config

def create_sample_trade(symbol, positive_pnl=None):
    """Create a sample trade with random values for testing"""
    
    # Random entry and exit times
    now = datetime.now()
    entry_time = now - timedelta(hours=random.randint(1, 8))
    exit_time = entry_time + timedelta(minutes=random.randint(15, 240))
    
    # Random direction
    direction = 'LONG' if random.random() > 0.5 else 'SHORT'
    
    # Random prices
    entry_price = round(random.uniform(100, 500), 2)
    
    # Control if the trade is winning or losing
    if positive_pnl is None:
        positive_pnl = random.random() > 0.4  # 60% winning trades by default
        
    price_change_pct = random.uniform(0.01, 0.05) if positive_pnl else random.uniform(0.01, 0.05)
    
    if direction == 'LONG':
        exit_price = entry_price * (1 + price_change_pct if positive_pnl else 1 - price_change_pct)
    else:
        exit_price = entry_price * (1 - price_change_pct if positive_pnl else 1 + price_change_pct)
    
    exit_price = round(exit_price, 2)
    
    # Calculate PnL
    position_size = random.randint(1, 10) * 10  # 10, 20, ..., 100 shares
    
    if direction == 'LONG':
        pnl = (exit_price - entry_price) * position_size
        pnl_pct = ((exit_price / entry_price) - 1) * 100
    else:
        pnl = (entry_price - exit_price) * position_size
        pnl_pct = ((entry_price / exit_price) - 1) * 100
    
    # Create the trade dictionary similar to what ExecutionAlgorithm would create
    trade = {
        'symbol': symbol,
        'direction': direction,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'position_size': position_size,
        'entry_time': entry_time.isoformat(),
        'exit_time': exit_time.isoformat(),
        'pnl': pnl,
        'pnl_pct': pnl_pct,
        'reason': 'TEST_TRADE',
        'setup_type': random.choice(['BREAKOUT', 'REVERSAL', 'TREND_FOLLOWING', 'MEAN_REVERSION']),
        'risk_reward': random.uniform(0.5, 3.0),
        'market_condition': random.choice(['BULL', 'BEAR', 'SIDEWAYS', 'VOLATILE'])
    }
    
    return trade

def create_sample_trades_for_today(symbols, num_trades=10):
    """Create sample trades for today's date"""
    trades = []
    
    # Create random trades
    for _ in range(num_trades):
        symbol = random.choice(symbols)
        positive_pnl = random.random() > 0.4  # 60% winning trades
        trade = create_sample_trade(symbol, positive_pnl)
        trades.append(trade)
        
    return trades

def create_sample_trades_for_past_days(symbols, days=5, trades_per_day=10):
    """Create sample trades for past days"""
    all_trades = []
    
    for day_offset in range(1, days + 1):
        # Create trades with dates in the past
        day_trades = []
        for _ in range(trades_per_day):
            symbol = random.choice(symbols)
            positive_pnl = random.random() > 0.4  # 60% winning trades
            trade = create_sample_trade(symbol, positive_pnl)
            
            # Adjust dates to be in the past
            past_day = datetime.now() - timedelta(days=day_offset)
            entry_time = datetime.fromisoformat(trade['entry_time'])
            exit_time = datetime.fromisoformat(trade['exit_time'])
            
            # Adjust to past day but keep the time component
            entry_time = datetime.combine(past_day.date(), entry_time.time())
            exit_time = datetime.combine(past_day.date(), exit_time.time())
            
            # Ensure exit_time is not before entry_time
            if exit_time <= entry_time:
                exit_time = entry_time + timedelta(minutes=random.randint(15, 240))
                
            trade['entry_time'] = entry_time.isoformat()
            trade['exit_time'] = exit_time.isoformat()
            
            day_trades.append(trade)
            
        all_trades.extend(day_trades)
        
    return all_trades

def main():
    """Main test function"""
    config = get_config()
    pnl_logger = PnLLogger(config)
    
    # Test symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 'JPM', 'V']
    
    # Create and log sample trades for today
    print("\n=== Logging today's sample trades ===", flush=True)
    today_trades = create_sample_trades_for_today(symbols, num_trades=15)
    
    for trade in today_trades:
        pnl_logger.log_trade(trade)
        print(f"Logged {trade['direction']} trade for {trade['symbol']} with PnL: ${trade['pnl']:.2f}", flush=True)
    
    # Calculate daily metrics for today
    today_stats = pnl_logger.calculate_daily_metrics(force_update=True)
    
    if today_stats:
        print(f"\nToday's stats: {today_stats['total_trades']} trades, "
              f"{today_stats['win_rate']}% win rate, ${today_stats['total_pnl']} total PnL", flush=True)
    
    # Create and log sample trades for past days
    print("\n=== Logging past days' sample trades ===", flush=True)
    past_trades = create_sample_trades_for_past_days(symbols, days=5, trades_per_day=10)
    
    for trade in past_trades:
        pnl_logger.log_trade(trade)
        exit_time = datetime.fromisoformat(trade['exit_time'])
        print(f"Logged {trade['direction']} trade for {trade['symbol']} on "
              f"{exit_time.strftime('%Y-%m-%d')} with PnL: ${trade['pnl']:.2f}", flush=True)
    
    # Retrieve daily statistics
    print("\n=== Retrieving daily stats for the last week ===", flush=True)
    from datetime import date
    start_date = date.today() - timedelta(days=7)
    daily_stats = pnl_logger.get_daily_stats(start_date=start_date)
    
    if not daily_stats.empty:
        print(f"Found stats for {len(daily_stats)} days:", flush=True)
        print(daily_stats.to_string(index=False), flush=True)
    else:
        print("No daily stats found for the specified date range", flush=True)
    
    # Retrieve trade history with filtering
    print("\n=== Retrieving filtered trade history ===", flush=True)
    apple_trades = pnl_logger.get_trade_history(symbol='AAPL', limit=5)
    if not apple_trades.empty:
        print(f"Found {len(apple_trades)} AAPL trades:", flush=True)
        print(apple_trades[['timestamp', 'side', 'entry_price', 'exit_price', 'pnl']].to_string(index=False), flush=True)
    else:
        print("No AAPL trades found", flush=True)
    
    print("\n=== PnL Logging Test Complete ===", flush=True)

if __name__ == "__main__":
    main() 