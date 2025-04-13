#!/usr/bin/env python3
"""
Test signal generator for the AutoTrader module.
This script generates random trade signals and submits them to the auto trader API.
"""

import argparse
import json
import random
import requests
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default symbols to use for test signals
DEFAULT_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'SPY', 'QQQ', 'XLF']

def generate_signal(symbols=None, position_type=None):
    """
    Generate a random trade signal
    
    Args:
        symbols: List of symbols to choose from (optional)
        position_type: Force a specific position type (LONG or SHORT) (optional)
    
    Returns:
        dict: Trade signal dictionary
    """
    if symbols is None:
        symbols = DEFAULT_SYMBOLS
    
    # Select a random symbol
    symbol = random.choice(symbols)
    
    # Determine base price for the symbol
    base_prices = {
        'AAPL': 180.0, 'MSFT': 380.0, 'GOOGL': 140.0, 'AMZN': 140.0, 
        'TSLA': 230.0, 'META': 470.0, 'NVDA': 950.0, 'SPY': 458.0, 
        'QQQ': 390.0, 'XLF': 39.0
    }
    
    base_price = base_prices.get(symbol, 100.0)
    
    # Add some random variation
    current_price = round(base_price * (1 + random.uniform(-0.02, 0.02)), 2)
    
    # Determine position type
    if position_type is None:
        position_type = random.choice(['LONG', 'SHORT'])
    
    # Calculate entry, stop loss, and take profit prices
    if position_type == 'LONG':
        entry_price = round(current_price * 0.9995, 2)  # Slightly below current
        stop_loss_pct = random.uniform(0.01, 0.03)  # 1-3% stop loss
        take_profit_pct = random.uniform(0.02, 0.05)  # 2-5% take profit
        
        stop_loss = round(entry_price * (1 - stop_loss_pct), 2)
        take_profit = round(entry_price * (1 + take_profit_pct), 2)
    else:  # SHORT
        entry_price = round(current_price * 1.0005, 2)  # Slightly above current
        stop_loss_pct = random.uniform(0.01, 0.03)  # 1-3% stop loss
        take_profit_pct = random.uniform(0.02, 0.05)  # 2-5% take profit
        
        stop_loss = round(entry_price * (1 + stop_loss_pct), 2)
        take_profit = round(entry_price * (1 - take_profit_pct), 2)
    
    # Generate signal score (0-10)
    signal_score = round(random.uniform(5.0, 9.5), 1)
    
    # Create the signal
    signal = {
        'symbol': symbol,
        'position_type': position_type,
        'entry_price': entry_price,
        'current_price': current_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'signal_score': signal_score,
        'timestamp': datetime.now().isoformat(),
        'use_market': random.random() < 0.3  # 30% chance of using market order
    }
    
    return signal

def submit_signal(signal, api_url="http://localhost:5000/api/auto-trade/signal"):
    """
    Submit a signal to the auto trader API
    
    Args:
        signal: Trade signal dictionary
        api_url: URL of the API endpoint
    
    Returns:
        dict: API response
    """
    try:
        response = requests.post(
            api_url,
            json=signal,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        return response.json()
    except Exception as e:
        logger.error(f"Error submitting signal: {e}")
        return {'success': False, 'error': str(e)}

def enable_auto_trader(api_url="http://localhost:5000/api/auto-trade/enable"):
    """
    Enable the auto trader
    
    Args:
        api_url: URL of the API endpoint
    
    Returns:
        dict: API response
    """
    try:
        response = requests.post(api_url, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Error enabling auto trader: {e}")
        return {'success': False, 'error': str(e)}

def get_auto_trader_status(api_url="http://localhost:5000/api/auto-trade/status"):
    """
    Get auto trader status
    
    Args:
        api_url: URL of the API endpoint
    
    Returns:
        dict: API response
    """
    try:
        response = requests.get(api_url, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Error getting auto trader status: {e}")
        return {'success': False, 'error': str(e)}

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate and submit test trade signals")
    parser.add_argument('-n', '--num-signals', type=int, default=1,
                      help='Number of signals to generate (default: 1)')
    parser.add_argument('-i', '--interval', type=float, default=5.0,
                      help='Interval between signals in seconds (default: 5.0)')
    parser.add_argument('-s', '--symbols', type=str,
                      help='Comma-separated list of symbols to use')
    parser.add_argument('-t', '--type', choices=['LONG', 'SHORT'],
                      help='Force specific position type (LONG or SHORT)')
    parser.add_argument('-u', '--api-url', type=str, default="http://localhost:5000",
                      help='Base URL of the API (default: http://localhost:5000)')
    parser.add_argument('-e', '--enable', action='store_true',
                      help='Enable auto trader before submitting signals')
    parser.add_argument('-m', '--market', action='store_true',
                      help='Force all signals to use market orders')
    parser.add_argument('-d', '--dry-run', action='store_true',
                      help='Print signals without submitting them')
    
    args = parser.parse_args()
    
    # Process symbols if provided
    symbols = DEFAULT_SYMBOLS
    if args.symbols:
        symbols = [s.strip() for s in args.symbols.split(',')]
    
    # Check if auto trader is running and enabled
    if not args.dry_run:
        status_response = get_auto_trader_status(f"{args.api_url}/api/auto-trade/status")
        
        if not status_response.get('success', False):
            logger.error("Failed to get auto trader status. Is the API server running?")
            return
        
        status = status_response.get('status', {})
        logger.info(f"Auto trader status: running={status.get('running', False)}, enabled={status.get('enabled', False)}")
        
        # Enable auto trader if requested
        if args.enable and not status.get('enabled', False):
            enable_response = enable_auto_trader(f"{args.api_url}/api/auto-trade/enable")
            if enable_response.get('success', False):
                logger.info("Auto trader enabled successfully")
            else:
                logger.error(f"Failed to enable auto trader: {enable_response.get('error', 'Unknown error')}")
    
    # Generate and submit signals
    logger.info(f"Generating {args.num_signals} test trade signals...")
    
    for i in range(args.num_signals):
        # Generate a signal
        signal = generate_signal(symbols, args.type)
        
        # Force market order if requested
        if args.market:
            signal['use_market'] = True
        
        # Print the signal
        logger.info(f"Signal {i+1}/{args.num_signals}: {json.dumps(signal, indent=2)}")
        
        # Submit the signal if not dry run
        if not args.dry_run:
            response = submit_signal(signal, f"{args.api_url}/api/auto-trade/signal")
            if response.get('success', False):
                logger.info(f"Signal submitted successfully: {response.get('message', '')}")
            else:
                logger.error(f"Failed to submit signal: {response.get('error', 'Unknown error')}")
        
        # Sleep between signals
        if i < args.num_signals - 1:
            time.sleep(args.interval)
    
    logger.info("Done generating signals")

if __name__ == "__main__":
    main() 