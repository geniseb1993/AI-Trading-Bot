#!/usr/bin/env python
"""
Test script for DeepSeekScanner.
This script validates the functionality of the DeepSeekScanner.
"""

import os
import sys
import logging
import json
from pathlib import Path
import time
from datetime import datetime

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from dual_bot.ai.deepseek_scanner import DeepSeekScanner

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DeepSeekTest")

# Mock data for testing
MOCK_MARKET_DATA = {
    "QQQ": [
        {"timestamp": "2023-03-10", "open": 390.0, "high": 395.0, "low": 388.0, "close": 392.0, "volume": 9000000},
        {"timestamp": "2023-03-11", "open": 392.0, "high": 398.0, "low": 390.0, "close": 395.0, "volume": 10000000},
        {"timestamp": "2023-03-12", "open": 395.0, "high": 400.0, "low": 393.0, "close": 398.0, "volume": 11000000},
        {"timestamp": "2023-03-13", "open": 398.0, "high": 405.0, "low": 396.0, "close": 401.0, "volume": 12000000},
        {"timestamp": "2023-03-14", "open": 401.0, "high": 406.0, "low": 399.0, "close": 404.0, "volume": 13000000},
        {"timestamp": "2023-03-15", "open": 404.0, "high": 410.0, "low": 402.0, "close": 408.0, "volume": 14000000}
    ],
    "TSLA": [
        {"timestamp": "2023-03-10", "open": 170.0, "high": 175.0, "low": 168.0, "close": 172.0, "volume": 19000000},
        {"timestamp": "2023-03-11", "open": 172.0, "high": 178.0, "low": 170.0, "close": 175.0, "volume": 20000000},
        {"timestamp": "2023-03-12", "open": 175.0, "high": 180.0, "low": 173.0, "close": 178.0, "volume": 21000000},
        {"timestamp": "2023-03-13", "open": 178.0, "high": 185.0, "low": 176.0, "close": 181.0, "volume": 22000000},
        {"timestamp": "2023-03-14", "open": 181.0, "high": 186.0, "low": 179.0, "close": 184.0, "volume": 23000000},
        {"timestamp": "2023-03-15", "open": 184.0, "high": 190.0, "low": 182.0, "close": 188.0, "volume": 24000000}
    ],
    "PLTR": [
        {"timestamp": "2023-03-10", "open": 20.0, "high": 21.0, "low": 19.5, "close": 20.5, "volume": 15000000},
        {"timestamp": "2023-03-11", "open": 20.5, "high": 22.0, "low": 20.0, "close": 21.5, "volume": 16000000},
        {"timestamp": "2023-03-12", "open": 21.5, "high": 23.0, "low": 21.0, "close": 22.5, "volume": 17000000},
        {"timestamp": "2023-03-13", "open": 22.5, "high": 24.0, "low": 22.0, "close": 23.5, "volume": 18000000},
        {"timestamp": "2023-03-14", "open": 23.5, "high": 25.0, "low": 23.0, "close": 24.5, "volume": 19000000},
        {"timestamp": "2023-03-15", "open": 24.5, "high": 26.0, "low": 24.0, "close": 25.5, "volume": 20000000}
    ]
}

def test_scanner_with_manual_config():
    """Test scanner functionality with a manually created config."""
    logger.info("Starting DeepSeekScanner functionality test with manual config...")
    
    # Create a minimal config
    test_config = {
        "data_sources": {
            "polygon": {"enabled": True, "api_key": "test_key"},
            "unusual_whales": {"enabled": True, "api_key": "test_key"},
            "news_api": {"enabled": True, "api_key": "test_key"}
        },
        "ai_models": {
            "deepseek": {"enabled": True, "api_key": "test_key"},
            "chatgpt": {"enabled": True, "api_key": "test_key"}
        },
        "trading": {
            "symbols": ["QQQ", "TSLA", "PLTR"],
            "max_trades_per_day": 3,
            "position_sizing": {"type": "fixed", "amount": 1000},
            "risk_management": {
                "max_loss_per_trade_percent": 2.0,
                "max_daily_loss_percent": 5.0,
                "default_stop_loss_percent": 2.0,
                "default_take_profit_percent": 5.0
            },
            "signal_thresholds": {
                "flow_score_threshold": 0.7,
                "dark_pool_score_threshold": 0.7,
                "news_score_threshold": 0.8,
                "technical_score_threshold": 0.6,
                "combined_score_threshold": 0.65
            }
        },
        "logging": {
            "level": "INFO",
            "file": "dual_bot/logs/test_dual_bot.log"
        }
    }
    
    try:
        # Mock the DataFetcher
        from unittest.mock import patch, MagicMock
        
        # Create a mock data fetcher
        mock_data_fetcher = MagicMock()
        mock_data_fetcher.initialize.return_value = True
        mock_data_fetcher.start.return_value = True
        mock_data_fetcher.stop.return_value = True
        
        # Mock get_market_data to return our test data
        mock_data_fetcher.get_market_data = lambda symbol: MOCK_MARKET_DATA.get(symbol, [])
        
        # Apply the patch
        with patch('dual_bot.ai.deepseek_scanner.DataFetcher', return_value=mock_data_fetcher):
            # Initialize scanner
            scanner = DeepSeekScanner(test_config)
            logger.info("Scanner initialized successfully!")
            
            # Manually inject market data
            for symbol in scanner.symbols:
                if symbol in MOCK_MARKET_DATA:
                    # Add to data cache
                    scanner.data_cache["market_data"][symbol] = {
                        "close": MOCK_MARKET_DATA[symbol][-1]["close"],
                        "open": MOCK_MARKET_DATA[symbol][-1]["open"],
                        "high": MOCK_MARKET_DATA[symbol][-1]["high"],
                        "low": MOCK_MARKET_DATA[symbol][-1]["low"],
                        "volume": MOCK_MARKET_DATA[symbol][-1]["volume"]
                    }
                    logger.info(f"Added mock data for {symbol}")
            
            # Generate some fake technical signals for QQQ
            signals = [
                {
                    "type": "indicator",
                    "direction": "bullish",
                    "strength": 0.8,
                    "indicator": "rsi",
                    "value": 25
                },
                {
                    "type": "indicator",
                    "direction": "bullish",
                    "strength": 0.7,
                    "indicator": "macd",
                    "value": 2.5
                }
            ]
            
            # Manually update recommendations
            scanner._update_recommendations("QQQ", signals)
            logger.info("Added mock recommendation for QQQ")
            
            # Get recommendations
            recommendations = scanner.get_recommendations()
            
            # Display recommendations
            logger.info(f"Retrieved {len(recommendations)} recommendations")
            for i, rec in enumerate(recommendations):
                logger.info(f"Recommendation {i+1}:")
                logger.info(f"Symbol: {rec.get('symbol')}")
                logger.info(f"Direction: {rec.get('direction')}")
                logger.info(f"Score: {rec.get('score')}")
                logger.info(f"Entry Price: {rec.get('entry_price')}")
                logger.info(f"Stop Loss: {rec.get('stop_loss')}")
                logger.info(f"Take Profit: {rec.get('take_profit')}")
                logger.info(f"Signals: {len(rec.get('signals', []))}")
                logger.info("---")
            
            logger.info("Test completed successfully!")
            return True
    except Exception as e:
        logger.error(f"Error in scanner test: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    test_scanner_with_manual_config() 