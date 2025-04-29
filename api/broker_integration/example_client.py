#!/usr/bin/env python
"""
Example client for the broker integration API.

This script demonstrates how to interact with the broker integration API,
making requests to various endpoints and processing the responses.
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional
import sys
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define API base URL
API_BASE_URL = "http://localhost:5000/api/broker"

def get_broker_info() -> Dict[str, Any]:
    """Get information about available brokers"""
    url = f"{API_BASE_URL}/info"
    response = requests.get(url)
    return response.json()

def set_active_broker(broker_name: str) -> Dict[str, Any]:
    """Set the active broker"""
    url = f"{API_BASE_URL}/set-active"
    data = {"broker_name": broker_name}
    response = requests.post(url, json=data)
    return response.json()

def configure_broker(broker_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Configure a broker"""
    url = f"{API_BASE_URL}/configure"
    data = {"broker_name": broker_name, "config": config}
    response = requests.post(url, json=data)
    return response.json()

def get_account_info() -> Dict[str, Any]:
    """Get account information"""
    url = f"{API_BASE_URL}/account"
    response = requests.get(url)
    return response.json()

def get_positions() -> Dict[str, Any]:
    """Get current positions"""
    url = f"{API_BASE_URL}/positions"
    response = requests.get(url)
    return response.json()

def get_orders(status: Optional[str] = None) -> Dict[str, Any]:
    """Get orders with optional status filter"""
    url = f"{API_BASE_URL}/orders"
    params = {}
    if status:
        params["status"] = status
    response = requests.get(url, params=params)
    return response.json()

def get_market_data(symbol: str) -> Dict[str, Any]:
    """Get market data for a symbol"""
    url = f"{API_BASE_URL}/market-data"
    params = {"symbol": symbol}
    response = requests.get(url, params=params)
    return response.json()

def execute_market_order(
    symbol: str, 
    qty: float, 
    side: str, 
    strategy: str = "manual",
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Execute a market order"""
    url = f"{API_BASE_URL}/execute/market"
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "strategy": strategy
    }
    
    if stop_loss:
        data["stop_loss"] = stop_loss
    
    if take_profit:
        data["take_profit"] = take_profit
    
    if notes:
        data["notes"] = notes
    
    if tags:
        data["tags"] = tags
    
    response = requests.post(url, json=data)
    return response.json()

def execute_limit_order(
    symbol: str, 
    qty: float, 
    side: str, 
    limit_price: float,
    strategy: str = "manual",
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Execute a limit order"""
    url = f"{API_BASE_URL}/execute/limit"
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "limit_price": limit_price,
        "strategy": strategy
    }
    
    if stop_loss:
        data["stop_loss"] = stop_loss
    
    if take_profit:
        data["take_profit"] = take_profit
    
    if notes:
        data["notes"] = notes
    
    if tags:
        data["tags"] = tags
    
    response = requests.post(url, json=data)
    return response.json()

def execute_bracket_order(
    symbol: str, 
    qty: float, 
    side: str,
    entry_price: Optional[float] = None,
    take_profit_price: Optional[float] = None,
    stop_loss_price: Optional[float] = None,
    take_profit_percent: Optional[float] = None,
    stop_loss_percent: Optional[float] = None,
    strategy: str = "manual",
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Execute a bracket order"""
    url = f"{API_BASE_URL}/execute/bracket"
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "strategy": strategy
    }
    
    if entry_price:
        data["entry_price"] = entry_price
    
    if take_profit_price:
        data["take_profit_price"] = take_profit_price
    
    if stop_loss_price:
        data["stop_loss_price"] = stop_loss_price
    
    if take_profit_percent:
        data["take_profit_percent"] = take_profit_percent
    
    if stop_loss_percent:
        data["stop_loss_percent"] = stop_loss_percent
    
    if notes:
        data["notes"] = notes
    
    if tags:
        data["tags"] = tags
    
    response = requests.post(url, json=data)
    return response.json()

def cancel_order(order_id: str) -> Dict[str, Any]:
    """Cancel an order"""
    url = f"{API_BASE_URL}/cancel-order/{order_id}"
    response = requests.delete(url)
    return response.json()

def cancel_all_orders() -> Dict[str, Any]:
    """Cancel all open orders"""
    url = f"{API_BASE_URL}/cancel-all-orders"
    response = requests.delete(url)
    return response.json()

def get_trades(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    strategy: Optional[str] = None
) -> Dict[str, Any]:
    """Get trades with optional filtering"""
    url = f"{API_BASE_URL}/trades"
    params = {}
    
    if status:
        params["status"] = status
    
    if symbol:
        params["symbol"] = symbol
    
    if strategy:
        params["strategy"] = strategy
    
    response = requests.get(url, params=params)
    return response.json()

def get_trade(trade_id: str) -> Dict[str, Any]:
    """Get a specific trade by ID"""
    url = f"{API_BASE_URL}/trades/{trade_id}"
    response = requests.get(url)
    return response.json()

def close_trade(
    trade_id: str,
    exit_price: float,
    exit_order_id: Optional[str] = None,
    fees: Optional[float] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Close a trade"""
    url = f"{API_BASE_URL}/trades/{trade_id}/close"
    data = {"exit_price": exit_price}
    
    if exit_order_id:
        data["exit_order_id"] = exit_order_id
    
    if fees:
        data["fees"] = fees
    
    if notes:
        data["notes"] = notes
    
    response = requests.post(url, json=data)
    return response.json()

def get_performance(starting_balance: float = 10000.0) -> Dict[str, Any]:
    """Get performance metrics"""
    url = f"{API_BASE_URL}/performance"
    params = {"starting_balance": starting_balance}
    response = requests.get(url, params=params)
    return response.json()

def sync_portfolio() -> Dict[str, Any]:
    """Synchronize portfolio with broker positions"""
    url = f"{API_BASE_URL}/sync"
    response = requests.post(url)
    return response.json()

def demo_basic_broker_operations():
    """Demonstrate basic broker operations"""
    logger.info("Demonstrating basic broker operations...")
    
    # Get broker info
    broker_info = get_broker_info()
    logger.info(f"Broker info: {json.dumps(broker_info, indent=2)}")
    
    # Set active broker to mock
    result = set_active_broker("mock")
    logger.info(f"Set active broker to mock: {json.dumps(result, indent=2)}")
    
    # Get account info
    account_info = get_account_info()
    logger.info(f"Account info: {json.dumps(account_info, indent=2)}")
    
    # Get market data for a symbol
    market_data = get_market_data("AAPL")
    logger.info(f"Market data for AAPL: {json.dumps(market_data, indent=2)}")
    
    # Get positions
    positions = get_positions()
    logger.info(f"Current positions: {json.dumps(positions, indent=2)}")
    
    # Get orders
    orders = get_orders()
    logger.info(f"Current orders: {json.dumps(orders, indent=2)}")

def demo_trading_operations():
    """Demonstrate trading operations"""
    logger.info("Demonstrating trading operations...")
    
    # Execute a market order
    result = execute_market_order(
        symbol="AAPL",
        qty=5,
        side="buy",
        strategy="demo",
        stop_loss=160.0,
        take_profit=180.0,
        notes="Demo market order",
        tags=["demo", "api-client"]
    )
    logger.info(f"Market order result: {json.dumps(result, indent=2)}")
    
    # Get market data for MSFT
    market_data = get_market_data("MSFT")
    if market_data.get("success"):
        current_price = market_data["market_data"]["last"]
        
        # Execute a limit order
        result = execute_limit_order(
            symbol="MSFT",
            qty=3,
            side="buy",
            limit_price=current_price * 0.98,  # 2% below current price
            strategy="demo",
            notes="Demo limit order",
            tags=["demo", "api-client"]
        )
        logger.info(f"Limit order result: {json.dumps(result, indent=2)}")
    
    # Execute a bracket order
    result = execute_bracket_order(
        symbol="GOOGL",
        qty=1,
        side="buy",
        entry_price=None,  # Use market order
        take_profit_percent=5.0,
        stop_loss_percent=2.0,
        strategy="demo",
        notes="Demo bracket order",
        tags=["demo", "api-client"]
    )
    logger.info(f"Bracket order result: {json.dumps(result, indent=2)}")
    
    # Get open trades
    trades = get_trades(status="open")
    logger.info(f"Open trades: {json.dumps(trades, indent=2)}")
    
    # Close the first trade if any
    if trades.get("success") and trades.get("trades"):
        trade = trades["trades"][0]
        trade_id = trade["id"]
        
        # Get current market data
        market_data = get_market_data(trade["symbol"])
        if market_data.get("success"):
            current_price = market_data["market_data"]["last"]
            
            # Close the trade
            result = close_trade(
                trade_id=trade_id,
                exit_price=current_price,
                notes="Demo trade close"
            )
            logger.info(f"Close trade result: {json.dumps(result, indent=2)}")
    
    # Get performance metrics
    performance = get_performance()
    logger.info(f"Performance metrics: {json.dumps(performance, indent=2)}")

def main():
    """Main function"""
    try:
        logger.info("Starting broker integration API client demo...")
        
        # Ensure the Flask server is running first
        try:
            response = requests.get(f"{API_BASE_URL}/info")
            if response.status_code != 200:
                logger.error(f"Failed to connect to the API server. Make sure it's running at {API_BASE_URL}")
                return 1
        except requests.RequestException:
            logger.error(f"Failed to connect to the API server. Make sure it's running at {API_BASE_URL}")
            return 1
        
        # Demo broker operations
        demo_basic_broker_operations()
        
        # Demo trading operations
        demo_trading_operations()
        
        logger.info("Demo completed successfully")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 