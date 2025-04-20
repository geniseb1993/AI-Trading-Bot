#!/usr/bin/env python
"""
Dual Bot Test Script
This script tests the functionality of the Dual Bot trading system.
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the dual_bot package
sys.path.append(str(Path(__file__).parent.parent))

# Import Dual Bot components
from dual_bot.config.config_loader import load_config
from dual_bot.deepseek_scanner import DeepSeekScanner
from dual_bot.chatgpt_risk_check import ChatGPTRiskManager
from dual_bot.auto_closer import AutoCloser
from dual_bot.data_fetcher import DataFetcher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dual_bot/logs/test_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TestBot")

def test_data_fetcher(config):
    """Test the data fetcher functionality."""
    logger.info("Testing Data Fetcher...")
    
    try:
        data_fetcher = DataFetcher(config)
        
        # Test market data fetching
        logger.info("Testing market data fetching...")
        symbol = config["trading"]["symbols"][0]
        market_data = data_fetcher.get_market_data(symbol)
        logger.info(f"Market data for {symbol}: {market_data}")
        
        # Test options data fetching
        logger.info("Testing options data fetching...")
        options_data = data_fetcher.get_options_data(symbol)
        logger.info(f"Options data for {symbol}: {options_data}")
        
        # Test news data fetching
        logger.info("Testing news data fetching...")
        news_data = data_fetcher.get_news_data(symbol)
        logger.info(f"News data for {symbol}: {news_data}")
        
        logger.info("Data Fetcher test completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Data Fetcher test failed: {e}")
        return False

def test_deepseek_scanner(config):
    """Test the DeepSeek scanner functionality."""
    logger.info("Testing DeepSeek Scanner...")
    
    try:
        scanner = DeepSeekScanner(config)
        
        # Test trade recommendation generation
        logger.info("Testing trade recommendation generation...")
        recommendations = scanner.generate_recommendations()
        logger.info(f"Trade recommendations: {recommendations}")
        
        logger.info("DeepSeek Scanner test completed successfully!")
        return True
    except Exception as e:
        logger.error(f"DeepSeek Scanner test failed: {e}")
        return False

def test_chatgpt_risk_manager(config):
    """Test the ChatGPT risk manager functionality."""
    logger.info("Testing ChatGPT Risk Manager...")
    
    try:
        risk_manager = ChatGPTRiskManager(config)
        
        # Create a sample trade recommendation
        trade_recommendation = {
            "symbol": "QQQ",
            "direction": "bullish",
            "confidence": 0.85,
            "entry_price": 450.0,
            "stop_loss": 445.0,
            "take_profit": 460.0,
            "expiry": "2023-05-19",
            "strike": 450,
            "option_type": "call",
            "reasoning": "Strong momentum and positive market sentiment"
        }
        
        # Create a sample market context
        market_context = {
            "market_hours": "open",
            "market_condition": "bullish",
            "vix": 18.5,
            "sector_performance": {
                "technology": 1.2,
                "finance": 0.8,
                "healthcare": 0.5
            },
            "recent_news": [
                "Fed signals potential rate cut",
                "Tech sector leads market gains"
            ]
        }
        
        # Test risk assessment
        logger.info("Testing risk assessment...")
        risk_assessment = risk_manager.assess_trade(trade_recommendation, market_context)
        logger.info(f"Risk assessment: {risk_assessment}")
        
        logger.info("ChatGPT Risk Manager test completed successfully!")
        return True
    except Exception as e:
        logger.error(f"ChatGPT Risk Manager test failed: {e}")
        return False

def test_auto_closer(config):
    """Test the auto closer functionality."""
    logger.info("Testing Auto Closer...")
    
    try:
        auto_closer = AutoCloser(config)
        
        # Create a sample position
        position = {
            "symbol": "QQQ",
            "side": "long",
            "entry_price": 450.0,
            "current_price": 455.0,
            "quantity": 10,
            "stop_loss": 445.0,
            "take_profit": 460.0,
            "entry_time": datetime.now() - timedelta(hours=1)
        }
        
        # Test position monitoring
        logger.info("Testing position monitoring...")
        should_close = auto_closer.should_close_position(position)
        logger.info(f"Should close position: {should_close}")
        
        logger.info("Auto Closer test completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Auto Closer test failed: {e}")
        return False

def test_integration(config):
    """Test the integration of all components."""
    logger.info("Testing integration of all components...")
    
    try:
        # Initialize components
        data_fetcher = DataFetcher(config)
        scanner = DeepSeekScanner(config)
        risk_manager = ChatGPTRiskManager(config)
        auto_closer = AutoCloser(config)
        
        # Get market data
        symbol = config["trading"]["symbols"][0]
        market_data = data_fetcher.get_market_data(symbol)
        
        # Generate trade recommendations
        recommendations = scanner.generate_recommendations()
        
        if recommendations:
            # Get the first recommendation
            recommendation = recommendations[0]
            
            # Create market context
            market_context = {
                "market_hours": "open",
                "market_condition": "bullish",
                "vix": 18.5,
                "sector_performance": {
                    "technology": 1.2,
                    "finance": 0.8,
                    "healthcare": 0.5
                },
                "recent_news": data_fetcher.get_news_data(symbol)
            }
            
            # Assess risk
            risk_assessment = risk_manager.assess_trade(recommendation, market_context)
            
            # Log the results
            logger.info(f"Trade recommendation: {recommendation}")
            logger.info(f"Risk assessment: {risk_assessment}")
            
            # If the trade is approved, simulate a position
            if risk_assessment["approved"]:
                position = {
                    "symbol": recommendation["symbol"],
                    "side": recommendation["direction"],
                    "entry_price": recommendation["entry_price"],
                    "current_price": recommendation["entry_price"],
                    "quantity": 10,
                    "stop_loss": recommendation["stop_loss"],
                    "take_profit": recommendation["take_profit"],
                    "entry_time": datetime.now()
                }
                
                # Check if the position should be closed
                should_close = auto_closer.should_close_position(position)
                logger.info(f"Should close position: {should_close}")
        
        logger.info("Integration test completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        return False

def main():
    """Main function to test the Dual Bot."""
    logger.info("Starting Dual Bot tests...")
    
    # Load configuration
    config = load_config()
    if not config:
        logger.error("Failed to load configuration.")
        return
    
    # Run individual component tests
    data_fetcher_result = test_data_fetcher(config)
    deepseek_result = test_deepseek_scanner(config)
    chatgpt_result = test_chatgpt_risk_manager(config)
    auto_closer_result = test_auto_closer(config)
    
    # Run integration test
    integration_result = test_integration(config)
    
    # Log test results
    logger.info("\n=== Test Results ===")
    logger.info(f"Data Fetcher: {'PASS' if data_fetcher_result else 'FAIL'}")
    logger.info(f"DeepSeek Scanner: {'PASS' if deepseek_result else 'FAIL'}")
    logger.info(f"ChatGPT Risk Manager: {'PASS' if chatgpt_result else 'FAIL'}")
    logger.info(f"Auto Closer: {'PASS' if auto_closer_result else 'FAIL'}")
    logger.info(f"Integration: {'PASS' if integration_result else 'FAIL'}")
    
    # Overall result
    overall_result = all([data_fetcher_result, deepseek_result, chatgpt_result, auto_closer_result, integration_result])
    logger.info(f"\nOverall Test Result: {'PASS' if overall_result else 'FAIL'}")
    
    if overall_result:
        logger.info("All tests passed successfully!")
    else:
        logger.warning("Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    main() 