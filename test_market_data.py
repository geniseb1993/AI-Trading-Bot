#!/usr/bin/env python

"""
Market Data API Integration Test Script

This script tests the market data API integrations by:
1. Loading the market data configuration
2. Initializing the MarketDataSourceManager
3. Testing each data source that is configured
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the market data modules
from api.lib.market_data import MarketDataSourceManager
from api.lib.market_data_config import load_market_data_config

def print_separator(title):
    """Print a separator with a title"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def test_alpaca_api(manager):
    """Test the Alpaca API"""
    print_separator("Testing Alpaca API")
    
    # Check if Alpaca is available
    if 'alpaca' not in manager.sources:
        print("Alpaca API not configured.")
        return False
    
    # Set the active source to Alpaca
    manager.set_active_source('alpaca')
    
    # Test getting market data
    symbols = ['SPY', 'QQQ', 'AAPL']
    print(f"Getting market data for {symbols}...")
    
    # Try bars, quotes, and trades
    for data_type in ['bars', 'quotes', 'trades']:
        print(f"\nTesting data type: {data_type}")
        data = manager.get_market_data(symbols, data_type=data_type)
        
        if isinstance(data, dict) and 'error' in data:
            print(f"Error: {data['error']}")
        else:
            print(f"Successfully retrieved {data_type} data:")
            print(json.dumps(data, indent=2)[:1000] + "..." if len(json.dumps(data)) > 1000 else json.dumps(data, indent=2))
    
    return True

def test_interactive_brokers_api(manager):
    """Test the Interactive Brokers API"""
    print_separator("Testing Interactive Brokers API")
    
    # Check if Interactive Brokers is available
    if 'interactive_brokers' not in manager.sources:
        print("Interactive Brokers API not configured.")
        return False
    
    # Set the active source to Interactive Brokers
    manager.set_active_source('interactive_brokers')
    
    # Test getting market data
    symbols = ['SPY', 'QQQ', 'AAPL']
    print(f"Getting market data for {symbols}...")
    
    data = manager.get_market_data(symbols)
    
    if isinstance(data, dict) and 'error' in data:
        print(f"Error: {data['error']}")
    else:
        print(f"Successfully retrieved data:")
        print(json.dumps(data, indent=2)[:1000] + "..." if len(json.dumps(data)) > 1000 else json.dumps(data, indent=2))
    
    return True

def test_unusual_whales_api(manager):
    """Test the Unusual Whales API"""
    print_separator("Testing Unusual Whales API")
    
    # Check if Unusual Whales is available
    if 'unusual_whales' not in manager.sources:
        print("Unusual Whales API not configured.")
        return False
    
    # Get the Unusual Whales source
    unusual_whales = manager.sources['unusual_whales']
    
    # Test getting options flow data
    symbols = ['SPY', 'QQQ', 'AAPL']
    print(f"Getting options flow data for {symbols}...")
    
    options_flow = unusual_whales.get_options_flow(symbols)
    
    if isinstance(options_flow, dict) and 'error' in options_flow:
        print(f"Error getting options flow: {options_flow['error']}")
    else:
        print(f"Successfully retrieved options flow data:")
        print(json.dumps(options_flow, indent=2)[:1000] + "..." if len(json.dumps(options_flow)) > 1000 else json.dumps(options_flow, indent=2))
    
    # Test getting dark pool data
    print(f"\nGetting dark pool data for {symbols}...")
    
    dark_pool = unusual_whales.get_dark_pool_data(symbols)
    
    if isinstance(dark_pool, dict) and 'error' in dark_pool:
        print(f"Error getting dark pool data: {dark_pool['error']}")
    else:
        print(f"Successfully retrieved dark pool data:")
        print(json.dumps(dark_pool, indent=2)[:1000] + "..." if len(json.dumps(dark_pool)) > 1000 else json.dumps(dark_pool, indent=2))
    
    return True

def test_tradingview_webhooks(manager):
    """Test the TradingView Webhooks"""
    print_separator("Testing TradingView Webhooks")
    
    # Check if TradingView is available
    if 'tradingview' not in manager.sources:
        print("TradingView Webhooks not configured.")
        return False
    
    # Get the TradingView source
    tradingview = manager.sources['tradingview']
    
    # Start the webhook server
    print("Starting TradingView webhook server...")
    tradingview.start_webhook_server()
    
    # Check if the server is running
    if tradingview.server_running:
        print(f"TradingView webhook server running on port {tradingview.webhook_port}")
        print(f"Use the following URL in TradingView alerts:")
        print(f"http://YOUR_SERVER_IP:{tradingview.webhook_port}{tradingview.webhook_path}")
        print("\nExample alert payload:")
        print(json.dumps({
            "symbol": "AAPL",
            "action": "BUY",
            "price": 150.0,
            "time": datetime.now().isoformat()
        }, indent=2))
    else:
        print("Error starting TradingView webhook server.")
        return False
    
    # Get any existing alerts
    alerts = tradingview.get_alerts()
    
    if alerts:
        print(f"\nFound {len(alerts)} existing alerts:")
        print(json.dumps(alerts, indent=2)[:1000] + "..." if len(json.dumps(alerts)) > 1000 else json.dumps(alerts, indent=2))
    else:
        print("\nNo existing alerts found.")
    
    return True

def main():
    """Main function"""
    print_separator("Market Data API Integration Test")
    
    print("Loading market data configuration...")
    config = load_market_data_config()
    
    print("Initializing MarketDataSourceManager...")
    manager = MarketDataSourceManager(config)
    
    # Print available sources
    sources = list(manager.sources.keys())
    print(f"Available sources: {sources}")
    print(f"Active source: {manager.active_source}")
    
    # Test each source
    test_alpaca_api(manager)
    test_interactive_brokers_api(manager)
    test_unusual_whales_api(manager)
    test_tradingview_webhooks(manager)
    
    print_separator("Test Complete")

if __name__ == "__main__":
    main() 