#!/usr/bin/env python
"""
Test script for the broker integration module.
This script connects to the broker integration module, tests basic operations,
and verifies that the mock broker is working correctly.
"""

import json
import logging
import sys
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import broker integration module
try:
    from api.broker_integration import (
        BrokerManager, MockBroker, AlpacaBroker, 
        TradeExecutor, PortfolioTracker,
        OrderSide, OrderType
    )
    logger.info("Successfully imported broker integration module")
except ImportError:
    try:
        # Try alternative import path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from api.broker_integration import (
            BrokerManager, MockBroker, AlpacaBroker, 
            TradeExecutor, PortfolioTracker,
            OrderSide, OrderType
        )
        logger.info("Successfully imported broker integration module from alternative path")
    except ImportError as e:
        logger.error(f"Failed to import broker integration module: {e}")
        sys.exit(1)

def test_broker_manager():
    """Test the broker manager functionality"""
    logger.info("Testing broker manager...")
    
    # Initialize broker manager
    config_file = "api/broker_integration/broker_config.json"
    broker_manager = BrokerManager(config_file=config_file)
    
    # Get available brokers
    available_brokers = broker_manager.get_available_brokers()
    logger.info(f"Available brokers: {available_brokers}")
    
    # Get active broker
    active_broker_name = broker_manager.active_broker_name
    logger.info(f"Active broker: {active_broker_name}")
    
    # Test switching brokers
    if "mock" in available_brokers:
        result = broker_manager.set_active_broker("mock")
        logger.info(f"Set active broker to mock: {result}")
    
    # Get broker
    broker = broker_manager.get_broker()
    logger.info(f"Got broker: {broker.__class__.__name__}")
    
    return broker_manager

def test_mock_broker(broker_manager):
    """Test the mock broker functionality"""
    logger.info("Testing mock broker...")
    
    # Get mock broker
    broker = broker_manager.get_broker("mock")
    
    # Connect to broker
    broker.connect()
    
    # Get account info
    account = broker.get_account()
    logger.info(f"Account: {account.to_dict()}")
    
    # Get market data
    market_data = broker.get_market_data("AAPL")
    logger.info(f"Market data for AAPL: {market_data}")
    
    # Get positions
    positions = broker.get_positions()
    logger.info(f"Number of positions: {len(positions)}")
    
    # Get orders
    orders = broker.get_orders()
    logger.info(f"Number of orders: {len(orders)}")
    
    return broker

def test_trade_executor(broker_manager):
    """Test the trade executor functionality"""
    logger.info("Testing trade executor...")
    
    # Initialize trade executor
    trade_executor = TradeExecutor(broker_manager)
    
    # Execute a market order
    order = trade_executor.market_order("AAPL", 10, "buy")
    if order:
        logger.info(f"Market order executed: {order.to_dict()}")
    
    # Execute a limit order
    # First get current price
    broker = broker_manager.get_broker()
    market_data = broker.get_market_data("MSFT")
    limit_price = market_data["last"] * 0.99  # 1% below last price
    
    order = trade_executor.limit_order("MSFT", 5, "buy", limit_price)
    if order:
        logger.info(f"Limit order placed: {order.to_dict()}")
    
    # Execute a bracket order
    entry_price = None  # Use market order for entry
    stop_loss_percent = 2.0  # 2% below entry
    take_profit_percent = 5.0  # 5% above entry
    
    entry_order, tp_order, sl_order = trade_executor.place_bracket_order(
        symbol="GOOGL",
        qty=2,
        side="buy",
        entry_price=entry_price,
        take_profit_percent=take_profit_percent,
        stop_loss_percent=stop_loss_percent
    )
    
    if entry_order:
        logger.info(f"Bracket order placed: Entry={entry_order.id}")
        if tp_order:
            logger.info(f"Take profit order placed: {tp_order.id}")
        if sl_order:
            logger.info(f"Stop loss order placed: {sl_order.id}")
    
    return trade_executor

def test_portfolio_tracker(broker_manager):
    """Test the portfolio tracker functionality"""
    logger.info("Testing portfolio tracker...")
    
    # Initialize portfolio tracker
    trades_file = "api/broker_integration/data/test_trade_history.json"
    portfolio_tracker = PortfolioTracker(broker_manager, trades_file=trades_file)
    
    # Open a trade
    trade = portfolio_tracker.open_trade(
        symbol="AAPL",
        quantity=10,
        entry_price=180.50,
        side="long",
        strategy="test",
        stop_loss=175.00,
        take_profit=190.00,
        notes="Test trade",
        tags=["test", "demo"]
    )
    
    logger.info(f"Opened trade: {trade.to_dict()}")
    
    # Open another trade
    trade2 = portfolio_tracker.open_trade(
        symbol="MSFT",
        quantity=5,
        entry_price=350.25,
        side="long",
        strategy="test",
        stop_loss=340.00,
        take_profit=370.00,
        notes="Test trade 2",
        tags=["test", "demo"]
    )
    
    logger.info(f"Opened trade 2: {trade2.to_dict()}")
    
    # Close the first trade
    closed_trade = portfolio_tracker.close_trade(
        trade_id=trade.id,
        exit_price=185.75,
        notes="Test close"
    )
    
    if closed_trade:
        logger.info(f"Closed trade: {closed_trade.to_dict()}")
    
    # Get performance metrics
    metrics = portfolio_tracker.get_performance_metrics()
    logger.info(f"Performance metrics: {metrics.to_dict()}")
    
    return portfolio_tracker

def main():
    """Main test function"""
    try:
        logger.info("Starting broker integration tests...")
        
        # Test broker manager
        broker_manager = test_broker_manager()
        
        # Test mock broker
        broker = test_mock_broker(broker_manager)
        
        # Test trade executor
        trade_executor = test_trade_executor(broker_manager)
        
        # Test portfolio tracker
        portfolio_tracker = test_portfolio_tracker(broker_manager)
        
        logger.info("All tests completed successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 