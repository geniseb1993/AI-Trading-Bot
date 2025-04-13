#!/usr/bin/env python
"""
Test script for the AI Trading Bot Execution Model

This script tests the execution model components including:
- Market Condition Analyzer
- Institutional Flow Analyzer
- Trade Setup Generator
- Risk Manager
- Execution Algorithm
- Data Adapter

Usage:
    python test_execution_model.py
"""

import os
import sys
import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import execution model components
try:
    from execution_model import (
        MarketConditionAnalyzer,
        InstitutionalFlowAnalyzer,
        TradeSetupGenerator,
        RiskManager,
        ExecutionAlgorithm,
        ExecutionModelDataAdapter
    )
    from execution_model.config import get_config
    logger.info("Successfully imported execution model components")
except ImportError as e:
    logger.error(f"Error importing execution model components: {e}")
    logger.error("Make sure you're running this script from the project root directory")
    sys.exit(1)

def test_market_condition_analyzer():
    """Test the market condition analyzer"""
    logger.info("Testing MarketConditionAnalyzer...")
    
    # Load configuration
    config = get_config()
    
    # Create analyzer instance
    analyzer = MarketConditionAnalyzer(config)
    
    # Create sample market data
    sample_data = {
        "SPY": create_sample_market_data("uptrend"),  # Uptrend
        "QQQ": create_sample_market_data("downtrend"),  # Downtrend
        "IWM": create_sample_market_data("choppy"),  # Choppy
        "DIA": create_sample_market_data("volatile")  # Volatile
    }
    
    # Test market condition analysis
    try:
        results = analyzer.analyze_market_conditions(sample_data)
        logger.info(f"Market condition analysis results: {json.dumps(results, indent=2)}")
        logger.info("✅ MarketConditionAnalyzer test passed")
        return results
    except Exception as e:
        logger.error(f"❌ MarketConditionAnalyzer test failed: {str(e)}")
        return None

def test_institutional_flow_analyzer(market_data=None):
    """Test the institutional flow analyzer"""
    logger.info("Testing InstitutionalFlowAnalyzer...")
    
    # Load configuration
    config = get_config()
    
    # Create analyzer instance
    analyzer = InstitutionalFlowAnalyzer(config)
    
    # Create sample flow data
    flow_data = create_sample_flow_data()
    
    # If no market data provided, create sample
    if market_data is None:
        market_data = {
            "SPY": create_sample_market_data("uptrend"),
            "AAPL": create_sample_market_data("uptrend"),
            "MSFT": create_sample_market_data("downtrend")
        }
    
    # Test flow analysis
    try:
        results = {}
        for symbol in flow_data["options_flow"]:
            symbol_flow = {
                "options_flow": [item for item in flow_data["options_flow"] if item["symbol"] == symbol],
                "dark_pool": [item for item in flow_data["dark_pool"] if item["symbol"] == symbol]
            }
            
            if symbol in market_data:
                symbol_market_data = market_data[symbol]
                analysis = analyzer.analyze_flow(symbol_flow, symbol_market_data, symbol)
                results[symbol] = analysis
                logger.info(f"Flow analysis for {symbol}: {json.dumps(analysis, indent=2)}")
        
        logger.info("✅ InstitutionalFlowAnalyzer test passed")
        return results
    except Exception as e:
        logger.error(f"❌ InstitutionalFlowAnalyzer test failed: {str(e)}")
        return None

def test_risk_manager():
    """Test the risk manager"""
    logger.info("Testing RiskManager...")
    
    # Load configuration
    config = get_config()
    
    # Create risk manager instance
    risk_manager = RiskManager(config)
    
    # Set up test parameters
    account_value = 100000.0
    position_value = 5000.0
    symbol = "AAPL"
    entry_price = 150.0
    stop_loss_price = 145.0
    
    # Test position sizing
    try:
        # Update portfolio value
        risk_manager.update_portfolio_value(account_value)
        
        # Calculate position size
        position_size = risk_manager.calculate_position_size(
            symbol, 
            entry_price, 
            stop_loss_price,
            market_condition="TREND",
            setup_quality=0.8
        )
        logger.info(f"Position size calculation: {position_size}")
        
        # Check portfolio exposure
        positions = [
            {"symbol": "MSFT", "value": 4000.0, "sector": "Technology"},
            {"symbol": "GOOGL", "value": 5000.0, "sector": "Technology"}
        ]
        risk_manager.update_positions(positions)
        
        exposure = risk_manager.check_portfolio_exposure(symbol, position_value)
        logger.info(f"Portfolio exposure check: {exposure}")
        
        # Get portfolio statistics
        stats = risk_manager.get_portfolio_statistics()
        logger.info(f"Portfolio statistics: {json.dumps(stats, indent=2)}")
        
        logger.info("✅ RiskManager test passed")
        return {
            "position_size": position_size,
            "exposure": exposure,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"❌ RiskManager test failed: {str(e)}")
        return None

def test_trade_setup_generator(market_data=None, flow_analysis=None):
    """Test the trade setup generator"""
    logger.info("Testing TradeSetupGenerator...")
    
    # Load configuration
    config = get_config()
    
    # Create instances of required components
    market_analyzer = MarketConditionAnalyzer(config)
    risk_manager = RiskManager(config)
    flow_analyzer = InstitutionalFlowAnalyzer(config)
    
    # Create trade setup generator instance
    setup_generator = TradeSetupGenerator(
        market_analyzer, 
        risk_manager, 
        flow_analyzer, 
        config
    )
    
    # If no market data provided, create sample
    if market_data is None:
        market_data = {
            "SPY": create_sample_market_data("uptrend"),
            "AAPL": create_sample_market_data("uptrend"),
            "MSFT": create_sample_market_data("downtrend")
        }
    
    # If no flow analysis provided, create it
    if flow_analysis is None:
        flow_data = create_sample_flow_data()
        flow_analysis = {}
        
        for symbol in market_data.keys():
            symbol_flow = {
                "options_flow": [item for item in flow_data["options_flow"] if item["symbol"] == symbol],
                "dark_pool": [item for item in flow_data["dark_pool"] if item["symbol"] == symbol]
            }
            
            analysis = flow_analyzer.analyze_flow(symbol_flow, market_data[symbol], symbol)
            flow_analysis[symbol] = analysis
    
    # Create sample account info
    account_info = {
        "balance": 100000.0,
        "buying_power": 200000.0,
        "equity": 105000.0,
        "currency": "USD"
    }
    
    # Test trade setup generation
    try:
        setups = setup_generator.generate_trade_setups(market_data, flow_analysis, account_info)
        logger.info(f"Generated {len(setups)} trade setups:")
        for i, setup in enumerate(setups):
            logger.info(f"Setup {i+1}: {json.dumps(setup, indent=2)}")
        
        logger.info("✅ TradeSetupGenerator test passed")
        return setups
    except Exception as e:
        logger.error(f"❌ TradeSetupGenerator test failed: {str(e)}")
        return None

def test_execution_algorithm(trade_setups=None):
    """Test the execution algorithm"""
    logger.info("Testing ExecutionAlgorithm...")
    
    # Load configuration
    config = get_config()
    
    # Create risk manager instance
    risk_manager = RiskManager(config)
    
    # Create execution algorithm instance
    execution_algo = ExecutionAlgorithm(risk_manager, config)
    
    # If no trade setups provided, create a sample
    if trade_setups is None or len(trade_setups) == 0:
        trade_setups = [
            {
                "symbol": "AAPL",
                "direction": "LONG",
                "entry_price": 150.0,
                "stop_loss": 145.0,
                "target_price": 160.0,
                "quantity": 10,
                "setup_type": "TREND_FOLLOWING",
                "market_condition": "TREND",
                "confidence": 0.85,
                "reason": "Strong uptrend with institutional buying"
            }
        ]
    
    # Create sample market data for each setup
    market_data = {}
    for setup in trade_setups:
        symbol = setup["symbol"]
        if symbol not in market_data:
            market_data[symbol] = create_sample_market_data("uptrend" if setup["direction"] == "LONG" else "downtrend")
    
    # Create sample account info
    account_info = {
        "balance": 100000.0,
        "buying_power": 200000.0,
        "equity": 105000.0,
        "currency": "USD"
    }
    
    # Test trade execution
    try:
        # Execute trades
        executed_trades = []
        for setup in trade_setups:
            trade = execution_algo.execute_trade(setup, market_data, account_info)
            if trade:
                executed_trades.append(trade)
                logger.info(f"Executed trade: {json.dumps(trade, indent=2)}")
            else:
                logger.info(f"Trade not executed for setup: {setup['symbol']}")
        
        # Update trades
        if executed_trades:
            # Simulate price movement
            for symbol in market_data:
                last_price = market_data[symbol]["close"].iloc[-1]
                # Simulate 1% move up
                market_data[symbol]["close"].iloc[-1] = last_price * 1.01
            
            updated_trades = execution_algo.update_trades(market_data, account_info)
            logger.info(f"Updated trades: {json.dumps(updated_trades, indent=2)}")
            
            # Close a trade
            if updated_trades:
                symbol_to_close = updated_trades[0]["symbol"]
                close_price = market_data[symbol_to_close]["close"].iloc[-1]
                closed_trade = execution_algo.close_trade(symbol_to_close, close_price, "TEST_CLOSE")
                logger.info(f"Closed trade: {json.dumps(closed_trade, indent=2)}")
        
        logger.info("✅ ExecutionAlgorithm test passed")
        return {
            "executed": executed_trades,
            "active": execution_algo.get_active_trades(),
            "completed": execution_algo.get_completed_trades()
        }
    except Exception as e:
        logger.error(f"❌ ExecutionAlgorithm test failed: {str(e)}")
        return None

def test_data_adapter():
    """Test the data adapter"""
    logger.info("Testing ExecutionModelDataAdapter...")
    
    # Create data adapter instance
    data_adapter = ExecutionModelDataAdapter()
    
    # Test with no market data manager (should return defaults)
    try:
        account_info = data_adapter.get_account_info()
        logger.info(f"Default account info: {json.dumps(account_info, indent=2)}")
        
        flow_data = data_adapter.get_institutional_flow_data()
        logger.info(f"Default flow data: {json.dumps(flow_data, indent=2)}")
        
        # Create sample market data
        symbols = ["SPY", "AAPL", "MSFT"]
        market_data = {}
        for symbol in symbols:
            market_data[symbol] = create_sample_market_data("uptrend")
        
        # Test formatting function by setting a dummy "_fetch_raw_data" method
        data_adapter._fetch_raw_data = lambda s, dt, tf, l: {"bars": market_data[s]} if s in market_data else {}
        
        # Set a mock market data manager
        class MockMarketDataManager:
            def get_bars(self, symbol, timeframe, limit):
                if symbol in market_data:
                    return market_data[symbol]
                return None
        
        data_adapter.set_market_data_manager(MockMarketDataManager())
        
        # Test getting market data
        formatted_data = data_adapter.get_market_data_for_execution(symbols)
        logger.info(f"Formatted market data: {formatted_data.keys()}")
        
        logger.info("✅ ExecutionModelDataAdapter test passed")
        return {
            "account_info": account_info,
            "flow_data": flow_data,
            "market_data": {symbol: data.shape for symbol, data in formatted_data.items()}
        }
    except Exception as e:
        logger.error(f"❌ ExecutionModelDataAdapter test failed: {str(e)}")
        return None

def create_sample_market_data(data_type="uptrend"):
    """
    Create sample market data for testing
    
    Args:
        data_type: Type of data to create (uptrend, downtrend, choppy, volatile)
        
    Returns:
        DataFrame with OHLCV data
    """
    # Create base DataFrame
    n = 100  # 100 days of data
    dates = pd.date_range(end=datetime.now(), periods=n, freq='D')
    
    # Base price series
    base_price = 100.0
    
    if data_type == "uptrend":
        # Create an uptrend
        trend = np.linspace(0, 0.3, n)  # 30% increase over the period
        noise = np.random.normal(0, 0.01, n)  # Small random noise
        close = base_price * (1 + trend + noise)
    elif data_type == "downtrend":
        # Create a downtrend
        trend = np.linspace(0, -0.25, n)  # 25% decrease over the period
        noise = np.random.normal(0, 0.01, n)  # Small random noise
        close = base_price * (1 + trend + noise)
    elif data_type == "choppy":
        # Create a choppy market
        noise = np.random.normal(0, 0.02, n)  # Larger random noise
        close = base_price * (1 + noise)
    elif data_type == "volatile":
        # Create a volatile market
        trend = np.linspace(0, 0.1, n)  # Slight uptrend
        volatility = np.random.normal(0, 0.03, n)  # Large random moves
        close = base_price * (1 + trend + volatility)
    else:
        # Default to random walk
        changes = np.random.normal(0.0005, 0.01, n)  # Small upward drift
        close = base_price * np.cumprod(1 + changes)
    
    # Create OHLC based on close prices
    daily_volatility = 0.015  # 1.5% daily volatility
    high = close * (1 + np.random.uniform(0, daily_volatility, n))
    low = close * (1 - np.random.uniform(0, daily_volatility, n))
    open_prices = close * (1 + np.random.normal(0, daily_volatility/2, n))
    
    # Create volume
    base_volume = 1000000  # Base volume
    volume = base_volume * (1 + np.random.uniform(-0.5, 1.0, n))  # Volume varies from 50% to 200% of base
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': dates,
        'open': open_prices,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    
    return df

def create_sample_flow_data():
    """
    Create sample institutional flow data for testing
    
    Returns:
        Dictionary with options flow and dark pool data
    """
    # Sample symbols
    symbols = ["SPY", "AAPL", "MSFT", "GOOGL", "AMZN"]
    
    # Create options flow data
    options_flow = []
    for symbol in symbols:
        # Add multiple options flow items for each symbol
        for _ in range(5):
            is_call = np.random.choice([True, False])
            is_buy = np.random.choice([True, False])
            
            options_flow.append({
                "symbol": symbol,
                "timestamp": (datetime.now() - timedelta(days=np.random.randint(0, 7))).isoformat(),
                "contract": f"{symbol} {np.random.randint(1, 30):02d}/{np.random.randint(1, 12):02d} ${np.random.randint(50, 500)}{'C' if is_call else 'P'}",
                "strike": np.random.randint(50, 500),
                "expiration": (datetime.now() + timedelta(days=np.random.randint(1, 365))).isoformat(),
                "type": "CALL" if is_call else "PUT",
                "side": "BUY" if is_buy else "SELL",
                "premium": np.random.randint(10000, 1000000) / 100,
                "size": np.random.randint(10, 1000),
                "open_interest": np.random.randint(100, 10000),
                "implied_volatility": np.random.uniform(0.2, 0.8),
                "underlying_price": np.random.randint(50, 500),
                "unusual_score": np.random.uniform(0.5, 1.0)
            })
    
    # Create dark pool data
    dark_pool = []
    for symbol in symbols:
        # Add multiple dark pool transactions for each symbol
        for _ in range(3):
            is_buy = np.random.choice([True, False])
            
            dark_pool.append({
                "symbol": symbol,
                "timestamp": (datetime.now() - timedelta(days=np.random.randint(0, 7))).isoformat(),
                "price": np.random.randint(50, 500),
                "size": np.random.randint(10000, 1000000),
                "side": "BUY" if is_buy else "SELL",
                "exchange": np.random.choice(["NYSE", "NASDAQ", "CBOE", "IEX"]),
                "premium": np.random.randint(1000000, 100000000) / 100,
                "percentage_of_daily_volume": np.random.uniform(0.01, 0.2)
            })
    
    return {
        "options_flow": options_flow,
        "dark_pool": dark_pool
    }

def run_all_tests():
    """Run all execution model tests"""
    logger.info("Running all execution model tests...")
    
    # Test market condition analyzer
    market_analysis = test_market_condition_analyzer()
    
    # Test institutional flow analyzer
    flow_analysis = test_institutional_flow_analyzer()
    
    # Test risk manager
    risk_results = test_risk_manager()
    
    # Test trade setup generator
    trade_setups = test_trade_setup_generator()
    
    # Test execution algorithm
    execution_results = test_execution_algorithm(trade_setups)
    
    # Test data adapter
    adapter_results = test_data_adapter()
    
    # Print summary
    logger.info("\n===== Execution Model Test Summary =====")
    logger.info(f"Market Condition Analyzer: {'✅ PASSED' if market_analysis else '❌ FAILED'}")
    logger.info(f"Institutional Flow Analyzer: {'✅ PASSED' if flow_analysis else '❌ FAILED'}")
    logger.info(f"Risk Manager: {'✅ PASSED' if risk_results else '❌ FAILED'}")
    logger.info(f"Trade Setup Generator: {'✅ PASSED' if trade_setups else '❌ FAILED'}")
    logger.info(f"Execution Algorithm: {'✅ PASSED' if execution_results else '❌ FAILED'}")
    logger.info(f"Data Adapter: {'✅ PASSED' if adapter_results else '❌ FAILED'}")
    
    return {
        "market_analysis": market_analysis,
        "flow_analysis": flow_analysis,
        "risk_results": risk_results,
        "trade_setups": trade_setups,
        "execution_results": execution_results,
        "adapter_results": adapter_results
    }

if __name__ == "__main__":
    run_all_tests() 