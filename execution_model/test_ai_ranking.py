#!/usr/bin/env python
"""
Test script for the AI Signal Ranking module

This script demonstrates the AI Signal Ranking functionality:
- ML-based signal ranking
- GPT-powered market insights
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import random
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add parent directory to path to import execution_model
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from execution_model.ai_signal_ranking import AISignalRanking
from execution_model.config import DEFAULT_CONFIG, get_config
from execution_model.pnl_logger import PnLLogger

def create_sample_market_data(symbols, periods=100):
    """Create sample market data for testing"""
    market_data = {}
    
    # Generate timestamp index going back from current time
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=periods)
    timestamps = pd.date_range(start=start_time, end=end_time, periods=periods)
    
    for symbol in symbols:
        # Generate random price data with some trend and volatility
        base_price = random.uniform(100, 500)
        trend = random.uniform(-0.0002, 0.0002)  # Small trend factor
        volatility = random.uniform(0.005, 0.015)  # Volatility factor
        
        close_prices = []
        for i in range(periods):
            # Add some random walk with trend
            if i == 0:
                close_prices.append(base_price)
            else:
                random_change = np.random.normal(trend, volatility)
                close_prices.append(close_prices[-1] * (1 + random_change))
        
        # Generate other OHLCV data
        high_prices = [price * (1 + random.uniform(0, 0.01)) for price in close_prices]
        low_prices = [price * (1 - random.uniform(0, 0.01)) for price in close_prices]
        open_prices = [low + random.random() * (high - low) for high, low in zip(high_prices, low_prices)]
        volumes = [random.randint(10000, 1000000) for _ in range(periods)]
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes
        })
        
        # Add bid/ask prices
        df['bid'] = df['close'] * (1 - random.uniform(0.001, 0.003))
        df['ask'] = df['close'] * (1 + random.uniform(0.001, 0.003))
        
        # Add to market data dictionary
        market_data[symbol] = df.set_index('timestamp')
    
    return market_data

def create_sample_signals(symbols, count=5):
    """Create sample trade signals for testing"""
    signals = []
    
    for _ in range(count):
        symbol = random.choice(symbols)
        direction = random.choice(['LONG', 'SHORT'])
        
        # Random price points
        entry_price = random.uniform(100, 500)
        
        # Determine stop loss and target based on direction
        if direction == 'LONG':
            stop_loss = entry_price * (1 - random.uniform(0.02, 0.05))
            profit_target = entry_price * (1 + random.uniform(0.04, 0.1))
        else:  # SHORT
            stop_loss = entry_price * (1 + random.uniform(0.02, 0.05))
            profit_target = entry_price * (1 - random.uniform(0.04, 0.1))
        
        # Create signal
        signal = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2),
            'profit_target': round(profit_target, 2),
            'position_size': random.randint(1, 10) * 10,  # 10-100 shares
            'setup_type': random.choice(['BREAKOUT', 'REVERSAL', 'TREND_FOLLOWING', 'MEAN_REVERSION']),
            'confidence': random.uniform(0.5, 0.9),
            'market_condition': random.choice(['BULL', 'BEAR', 'SIDEWAYS', 'VOLATILE'])
        }
        
        signals.append(signal)
    
    return signals

def main():
    """Main test function"""
    # Get configuration directly using DEFAULT_CONFIG to avoid ExecutionModelConfig issues
    config = DEFAULT_CONFIG.copy()
    config_obj = get_config()
    pnl_logger = PnLLogger(config_obj)
    
    # Create an instance of AISignalRanking with the plain dictionary config
    ai_ranking = AISignalRanking(config, pnl_logger)
    
    # Test symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 'JPM', 'V']
    
    print("\n=== Testing AI Signal Ranking ===", flush=True)
    
    # Create sample market data
    print("\nGenerating sample market data...", flush=True)
    market_data = create_sample_market_data(symbols)
    
    # Create sample signals
    print("\nGenerating sample trade signals...", flush=True)
    signals = create_sample_signals(symbols)
    
    # Print sample signals
    print("\nSample trade signals:", flush=True)
    for i, signal in enumerate(signals):
        print(f"Signal {i+1}: {signal['direction']} {signal['symbol']} @ ${signal['entry_price']:.2f} "
              f"({signal['setup_type']})", flush=True)
    
    # Test ML-based signal ranking
    print("\n=== Testing ML-based Signal Ranking ===", flush=True)
    ranked_signals = ai_ranking.rank_signals(signals, market_data)
    
    print("\nRanked signals:", flush=True)
    for i, signal in enumerate(ranked_signals):
        confidence = signal.get('ai_confidence', 0)
        factors = signal.get('ranking_factors', {})
        factor_str = ", ".join([f"{k}: {v:.2f}" for k, v in factors.items()])
        
        print(f"Rank {i+1}: {signal['direction']} {signal['symbol']} @ ${signal['entry_price']:.2f} "
              f"- Confidence: {confidence:.2f} ({factor_str})", flush=True)
    
    # Test GPT-powered insights (if API key available)
    if ai_ranking.client:
        print("\n=== Testing GPT-Powered Insights ===", flush=True)
        
        # Select top signal for detailed analysis
        top_symbol = ranked_signals[0]['symbol'] if ranked_signals else symbols[0]
        
        print(f"\nGetting insights for {top_symbol}...", flush=True)
        insights = ai_ranking.get_gpt_insights([top_symbol], market_data)
        
        if top_symbol in insights:
            print(f"\nGPT insights for {top_symbol}:", flush=True)
            insight_data = insights[top_symbol]
            print(json.dumps(insight_data, indent=2), flush=True)
        else:
            print(f"No insights available for {top_symbol}", flush=True)
        
        # Test trade setup optimization
        if ranked_signals:
            print("\n=== Testing Trade Setup Optimization ===", flush=True)
            
            # Select top signal for optimization
            top_signal = ranked_signals[0]
            symbol = top_signal['symbol']
            
            print(f"\nOptimizing setup for {symbol}...", flush=True)
            optimized_setup = ai_ranking.optimize_trade_setup(top_signal, market_data[symbol])
            
            # Compare original vs optimized
            print("\nOriginal vs Optimized Stop Loss and Target:", flush=True)
            print(f"Original: Stop Loss ${top_signal['stop_loss']:.2f}, Target ${top_signal['profit_target']:.2f}", flush=True)
            print(f"Optimized: Stop Loss ${optimized_setup['stop_loss']:.2f}, Target ${optimized_setup['profit_target']:.2f}", flush=True)
            
            # Print AI setup quality if available
            if 'ai_setup_quality' in optimized_setup:
                print(f"AI Setup Quality: {optimized_setup['ai_setup_quality']:.2f}", flush=True)
            
            # Print AI bias if available
            if 'ai_bias' in optimized_setup:
                print(f"AI Bias: {optimized_setup['ai_bias']}", flush=True)
        
        # Test market summary
        print("\n=== Testing Market Summary ===", flush=True)
        market_summary = ai_ranking.get_market_summary(market_data)
        
        print("\nMarket Summary:", flush=True)
        print(json.dumps(market_summary, indent=2), flush=True)
    else:
        print("\nGPT-powered insights not available (no API key)", flush=True)
    
    print("\n=== AI Signal Ranking Test Complete ===", flush=True)

if __name__ == "__main__":
    main() 