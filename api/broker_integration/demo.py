"""
Broker Integration Demo

This script demonstrates the usage of the broker integration module.
It performs basic operations with the mock broker for demonstration purposes.
"""

import logging
import json
import os
import sys
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import modules
from api.broker_integration.broker_adapter import BrokerAdapter
from api.broker_integration.broker_utils import (
    format_order_for_response,
    format_position_for_response,
    format_account_for_response
)

def print_separator(title: str = None):
    """Print a separator line with optional title"""
    width = 80
    if title:
        print(f"\n{'-' * 3} {title} {'-' * (width - len(title) - 6)}\n")
    else:
        print(f"\n{'-' * width}\n")

def print_json(data):
    """Print data as formatted JSON"""
    print(json.dumps(data, indent=2))

def run_demo():
    """Run the broker integration demo"""
    print_separator("BROKER INTEGRATION DEMO")
    
    # Create broker adapter (defaults to mock broker)
    broker = BrokerAdapter()
    
    # Connect to broker
    print_separator("CONNECTING TO BROKER")
    connected = broker.connect()
    print(f"Connected: {connected}")
    
    # Get account info
    print_separator("ACCOUNT INFORMATION")
    account_info = broker.get_account_info()
    formatted_account = format_account_for_response(account_info)
    print_json(formatted_account)
    
    # Get available brokers
    print_separator("AVAILABLE BROKERS")
    brokers = broker.get_available_brokers()
    print_json(brokers)
    
    # Place market order
    print_separator("PLACING MARKET ORDER")
    market_order = broker.place_order(
        symbol="AAPL",
        qty=10,
        side="buy",
        order_type="market"
    )
    formatted_order = format_order_for_response(market_order)
    print_json(formatted_order)
    
    # Wait for order to process
    print("Waiting for order to process...")
    time.sleep(2)
    
    # Get order status
    print_separator("ORDER STATUS")
    order = broker.get_order(formatted_order["id"])
    updated_order = format_order_for_response(order)
    print_json(updated_order)
    
    # Place limit order
    print_separator("PLACING LIMIT ORDER")
    limit_order = broker.place_order(
        symbol="MSFT",
        qty=5,
        side="buy",
        order_type="limit",
        limit_price=300.00
    )
    formatted_limit_order = format_order_for_response(limit_order)
    print_json(formatted_limit_order)
    
    # Get positions
    print_separator("POSITIONS")
    positions = broker.get_positions()
    formatted_positions = [format_position_for_response(p) for p in positions]
    print_json(formatted_positions)
    
    # Get market data
    print_separator("MARKET DATA")
    market_data = broker.get_market_data("AAPL")
    print_json(market_data)
    
    # Get all orders
    print_separator("ALL ORDERS")
    orders = broker.get_orders()
    formatted_orders = [format_order_for_response(o) for o in orders]
    print_json(formatted_orders)
    
    # Cancel limit order
    print_separator("CANCELLING LIMIT ORDER")
    cancel_result = broker.cancel_order(formatted_limit_order["id"])
    print(f"Order cancelled: {cancel_result}")
    
    # Get account info again
    print_separator("UPDATED ACCOUNT INFORMATION")
    account_info = broker.get_account_info()
    formatted_account = format_account_for_response(account_info)
    print_json(formatted_account)
    
    # Disconnect
    print_separator("DISCONNECTING FROM BROKER")
    disconnected = broker.disconnect()
    print(f"Disconnected: {disconnected}")
    
    print_separator("DEMO COMPLETED")

if __name__ == "__main__":
    run_demo() 