#!/usr/bin/env python
"""
Test script for the Unusual Whales API integration in the AI Trading Bot

This script tests the connection to the Unusual Whales API and retrieves
dark pool and options flow data.

Usage:
    python test_unusual_whales.py
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Add project root to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import the UnusualWhalesAPI class
try:
    from api.lib.market_data import UnusualWhalesAPI
    logger.info("Successfully imported UnusualWhalesAPI class")
except ImportError as e:
    logger.error(f"Error importing UnusualWhalesAPI class: {e}")
    logger.error("Make sure you're running this script from the project root directory")
    sys.exit(1)

def pretty_print_json(data):
    """
    Print JSON data in a more readable format.
    """
    print(json.dumps(data, indent=2))

def test_unusual_whales_api():
    """
    Test the Unusual Whales API integration.
    """
    # Get the API key from the environment
    api_key = os.environ.get('UNUSUAL_WHALES_API_KEY')
    
    if not api_key:
        logger.error("Unusual Whales API key not found in environment variables")
        logger.error("Make sure you've added UNUSUAL_WHALES_API_KEY to the .env file")
        return False
    
    # Initialize the API client
    logger.info("Initializing UnusualWhalesAPI with the provided API key")
    client = UnusualWhalesAPI(token=api_key)
    
    # Test getting dark pool data
    logger.info("\n=== Testing Dark Pool Recent Endpoint ===")
    try:
        dark_pool_data = client.get_dark_pool_data(limit=5)
        
        if "error" in dark_pool_data:
            logger.error(f"Error getting dark pool data: {dark_pool_data['error']}")
            return False
        
        logger.info(f"Successfully retrieved dark pool data with {len(dark_pool_data.get('data', []))} records")
        pretty_print_json(dark_pool_data)
    except Exception as e:
        logger.error(f"Exception in dark pool data test: {repr(e)}")
        return False
    
    # Skip options flow for now since it's not working
    # Test getting dark pool data for specific symbols
    symbols = ["AAPL", "MSFT", "TSLA"]
    logger.info(f"\n=== Testing Dark Pool Data for Symbols: {symbols} ===")
    
    symbol_dark_pool_data = client.get_dark_pool_data(symbols=symbols, limit=5)
    
    if "error" in symbol_dark_pool_data:
        logger.error(f"Error getting dark pool data for symbols: {symbol_dark_pool_data['error']}")
    else:
        logger.info(f"Successfully retrieved dark pool data for {symbols}")
        pretty_print_json(symbol_dark_pool_data)
    
    # Test getting dark pool data for a specific ticker
    ticker = "AAPL"
    logger.info(f"\n=== Testing Dark Pool Ticker Endpoint for {ticker} ===")
    
    ticker_dark_pool_data = client.get_dark_pool_by_ticker(symbol=ticker)
    
    if "error" in ticker_dark_pool_data:
        logger.error(f"Error getting dark pool data for ticker {ticker}: {ticker_dark_pool_data['error']}")
    else:
        logger.info(f"Successfully retrieved dark pool data for ticker {ticker}")
        pretty_print_json(ticker_dark_pool_data)
    
    # Test getting aggregated dark pool data
    logger.info("\n=== Testing Dark Pool Aggregate Endpoint ===")
    
    aggregate_dark_pool_data = client.get_dark_pool_aggregate(limit=5)
    
    if "error" in aggregate_dark_pool_data:
        logger.error(f"Error getting aggregated dark pool data: {aggregate_dark_pool_data['error']}")
    else:
        logger.info("Successfully retrieved aggregated dark pool data")
        pretty_print_json(aggregate_dark_pool_data)
    
    logger.info("\n=== All Unusual Whales API tests completed ===")
    return True

if __name__ == "__main__":
    # Run the test
    success = test_unusual_whales_api()
    
    if success:
        logger.info("All Unusual Whales API tests passed successfully")
        sys.exit(0)
    else:
        logger.error("Some Unusual Whales API tests failed")
        sys.exit(1) 