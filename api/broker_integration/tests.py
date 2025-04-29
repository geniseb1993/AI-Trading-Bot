"""
Tests for the broker integration module.

This module contains test functions and utilities for testing the broker integration.
"""

import unittest
import logging
import json
import os
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import modules to test
from api.broker_integration.config import load_config, save_config
from api.broker_integration.broker_adapter import BrokerAdapter
from api.broker_integration.broker_utils import (
    format_order_for_response,
    format_position_for_response,
    format_account_for_response,
    check_broker_credentials
)
from api.broker_integration.broker_interface import OrderSide, OrderType

class BrokerIntegrationTests(unittest.TestCase):
    """Test cases for broker integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_config = {
            "active_broker": "mock",
            "brokers": {
                "mock": {
                    "type": "mock",
                    "initial_balance": 100000.0
                },
                "alpaca": {
                    "type": "alpaca",
                    "api_key": "test_key",
                    "api_secret": "test_secret",
                    "is_paper": True
                }
            }
        }
        
        # Save test config to temporary file
        self.test_config_path = "test_broker_config.json"
        with open(self.test_config_path, 'w') as f:
            json.dump(self.test_config, f)
        
        # Create broker adapter with test config
        self.broker_adapter = BrokerAdapter(config_path=self.test_config_path)
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove test config file
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
    
    def test_load_config(self):
        """Test loading broker configuration"""
        config = load_config(self.test_config_path)
        self.assertEqual(config["active_broker"], "mock")
        self.assertIn("mock", config["brokers"])
        self.assertIn("alpaca", config["brokers"])
    
    def test_save_config(self):
        """Test saving broker configuration"""
        # Modify config
        config = load_config(self.test_config_path)
        config["active_broker"] = "alpaca"
        
        # Save config
        result = save_config(config, self.test_config_path)
        self.assertTrue(result)
        
        # Load config again and verify changes
        config = load_config(self.test_config_path)
        self.assertEqual(config["active_broker"], "alpaca")
    
    def test_broker_adapter_init(self):
        """Test broker adapter initialization"""
        self.assertIsNotNone(self.broker_adapter)
        self.assertIsNotNone(self.broker_adapter.broker)
        self.assertEqual(self.broker_adapter.broker.__class__.__name__, "MockBroker")
    
    def test_broker_connect(self):
        """Test broker connection"""
        # Disconnect first to ensure we're testing connection
        self.broker_adapter.disconnect()
        
        # Test connect
        result = self.broker_adapter.connect()
        self.assertTrue(result)
        self.assertTrue(self.broker_adapter.is_connected())
    
    def test_get_account_info(self):
        """Test getting account information"""
        account_info = self.broker_adapter.get_account_info()
        self.assertIsNotNone(account_info)
        self.assertIn("cash", account_info)
        self.assertIn("portfolio_value", account_info)
        self.assertIn("buying_power", account_info)
    
    def test_get_positions(self):
        """Test getting positions"""
        positions = self.broker_adapter.get_positions()
        self.assertIsNotNone(positions)
        self.assertIsInstance(positions, list)
    
    def test_place_order(self):
        """Test placing an order"""
        # Place a market order
        order = self.broker_adapter.place_order(
            symbol="AAPL",
            qty=10,
            side="buy",
            order_type="market"
        )
        
        self.assertIsNotNone(order)
        self.assertIn("id", order)
        self.assertEqual(order["symbol"], "AAPL")
        self.assertEqual(order["qty"], 10)
        self.assertEqual(order["side"], "buy")
        self.assertEqual(order["type"], "market")
    
    def test_get_orders(self):
        """Test getting orders"""
        # Place an order first
        self.broker_adapter.place_order(
            symbol="AAPL",
            qty=10,
            side="buy",
            order_type="market"
        )
        
        # Get orders
        orders = self.broker_adapter.get_orders()
        self.assertIsNotNone(orders)
        self.assertIsInstance(orders, list)
        self.assertGreater(len(orders), 0)
    
    def test_format_order(self):
        """Test formatting an order for response"""
        # Create sample order
        order = {
            "id": "test-order-id",
            "symbol": "AAPL",
            "qty": 10,
            "side": "buy",
            "type": "market",
            "status": "filled",
            "filled_qty": 10,
            "filled_avg_price": 150.0,
            "created_at": "2023-01-01T12:00:00Z",
            "filled_at": "2023-01-01T12:01:00Z"
        }
        
        # Format order
        formatted = format_order_for_response(order)
        
        # Check required fields
        self.assertEqual(formatted["id"], "test-order-id")
        self.assertEqual(formatted["symbol"], "AAPL")
        self.assertEqual(formatted["qty"], 10)
        self.assertEqual(formatted["side"], "buy")
        self.assertEqual(formatted["type"], "market")
        self.assertEqual(formatted["status"], "filled")
        self.assertEqual(formatted["filled_qty"], 10)
        self.assertEqual(formatted["filled_avg_price"], 150.0)
        self.assertTrue(formatted["is_filled"])
    
    def test_check_credentials(self):
        """Test credential validation"""
        # Valid mock credentials
        result = check_broker_credentials("mock", {})
        self.assertTrue(result["is_valid"])
        
        # Valid Alpaca credentials
        result = check_broker_credentials("alpaca", {
            "api_key": "test_key",
            "api_secret": "test_secret"
        })
        self.assertTrue(result["is_valid"])
        
        # Invalid Alpaca credentials (missing fields)
        result = check_broker_credentials("alpaca", {
            "api_key": ""
        })
        self.assertFalse(result["is_valid"])
        self.assertIn("api_secret", result["missing_fields"])
        
        # Unsupported broker
        result = check_broker_credentials("unknown", {})
        self.assertFalse(result["is_valid"])
        self.assertIsNotNone(result["error"])

def run_tests():
    """Run all tests"""
    unittest.main()

if __name__ == "__main__":
    run_tests() 