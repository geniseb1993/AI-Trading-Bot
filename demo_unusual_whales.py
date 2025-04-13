#!/usr/bin/env python
"""
Unusual Whales API Demonstration Script

This script demonstrates how to use the Unusual Whales API to retrieve dark pool data,
which provides insight into institutional trading activity.

Usage:
    python demo_unusual_whales.py
"""

import os
import json
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Import the UnusualWhalesAPI class
from api.lib.market_data import UnusualWhalesAPI

def pretty_print_json(data):
    """
    Print JSON data in a more readable format.
    """
    print(json.dumps(data, indent=2))

def demo_unusual_whales_api():
    """
    Demonstrate how to use the Unusual Whales API.
    """
    print("\n" + "="*50)
    print("    UNUSUAL WHALES API DEMONSTRATION")
    print("="*50 + "\n")
    
    # Get the API key from the environment
    api_key = os.environ.get('UNUSUAL_WHALES_API_KEY')
    
    if not api_key:
        logger.error("Unusual Whales API key not found in environment variables")
        logger.error("Make sure you've added UNUSUAL_WHALES_API_KEY to the .env file")
        return
    
    # Initialize the API client
    print("Initializing Unusual Whales API client...")
    client = UnusualWhalesAPI(token=api_key)
    
    # Demonstrate retrieving recent dark pool data
    print("\n1. RETRIEVING RECENT DARK POOL TRANSACTIONS")
    print("------------------------------------------")
    print("Dark pool transactions are large block trades executed off public exchanges.")
    print("They often represent institutional buying or selling activity.\n")
    
    dark_pool_data = client.get_dark_pool_data(limit=5)
    
    if "error" in dark_pool_data:
        print(f"Error: {dark_pool_data['error']}")
    else:
        records = dark_pool_data.get("data", [])
        print(f"Successfully retrieved {len(records)} dark pool transactions:")
        
        for i, record in enumerate(records):
            print(f"\nTransaction #{i+1}:")
            print(f"  Symbol: {record.get('ticker')}")
            print(f"  Time: {record.get('executed_at')}")
            print(f"  Price: ${record.get('price')}")
            print(f"  Size: {record.get('size')} shares")
            print(f"  Value: ${float(record.get('premium', 0)):,.2f}")
            
            # Add some analysis
            volume = int(record.get('volume', 0))
            size = int(record.get('size', 0))
            if volume > 0:
                percentage = (size / volume) * 100
                print(f"  % of Daily Volume: {percentage:.2f}%")
    
    # Demonstrate filtering by symbols
    print("\n\n2. FILTERING DARK POOL DATA BY SYMBOLS")
    print("-------------------------------------")
    print("You can filter dark pool data to focus on specific stocks of interest.\n")
    
    symbols = ["AAPL", "MSFT", "TSLA"]
    print(f"Getting dark pool data for: {', '.join(symbols)}")
    
    filtered_data = client.get_dark_pool_data(symbols=symbols, limit=3)
    
    if "error" in filtered_data:
        print(f"Error: {filtered_data['error']}")
    else:
        records = filtered_data.get("data", [])
        print(f"Found {len(records)} dark pool transactions for these symbols:")
        
        for i, record in enumerate(records):
            ticker = record.get('ticker')
            premium = float(record.get('premium', 0))
            print(f"\n{ticker}: ${premium:,.2f} ({record.get('size')} shares at ${record.get('price')})")
    
    print("\n" + "="*50)
    print("    DEMONSTRATION COMPLETE")
    print("="*50 + "\n")
    print("You can now integrate this dark pool data into your trading algorithms")
    print("to gain insights into institutional trading activity.")
    print("\nFor more details, refer to the Unusual Whales API documentation.")

if __name__ == "__main__":
    demo_unusual_whales_api() 