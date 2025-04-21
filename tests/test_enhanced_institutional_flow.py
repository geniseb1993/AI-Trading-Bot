"""
Unit tests for the Enhanced Institutional Flow Analyzer

This module contains tests to verify the functionality of the
Enhanced Institutional Flow Analyzer implementation.
"""

import unittest
import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the analyzer
from execution_model.enhanced_institutional_flow import EnhancedInstitutionalFlowAnalyzer

class TestEnhancedInstitutionalFlowAnalyzer(unittest.TestCase):
    """Test cases for the EnhancedInstitutionalFlowAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "institutional_flow": {
                "unusual_options_weight": 0.65,
                "dark_pool_weight": 0.75,
                "block_trade_weight": 0.6,
                "min_flow_signal": 0.55,
                "correlation_window": 20,
                "volatility_adjustment": True
            },
            "data_directory": "data"
        }
        
        self.analyzer = EnhancedInstitutionalFlowAnalyzer(self.config)
        
        # Create mock flow data
        self.flow_data = self._create_mock_flow_data()
        
        # Create mock market data
        self.market_data = self._create_mock_market_data()
    
    def test_initialization(self):
        """Test that the analyzer initializes correctly"""
        self.assertEqual(self.analyzer.unusual_options_weight, 0.65)
        self.assertEqual(self.analyzer.dark_pool_weight, 0.75)
        self.assertEqual(self.analyzer.block_trade_weight, 0.6)
        self.assertEqual(self.analyzer.min_flow_signal, 0.55)
        self.assertEqual(self.analyzer.correlation_window, 20)
        self.assertTrue(self.analyzer.volatility_adjustment)
        self.assertIsInstance(self.analyzer.flow_cache, dict)
    
    def test_filter_symbol_data(self):
        """Test filtering data by symbol"""
        options_data = [
            {"symbol": "AAPL", "type": "CALL", "volume": 100},
            {"symbol": "MSFT", "type": "PUT", "volume": 200},
            {"symbol": "AAPL", "type": "PUT", "volume": 300}
        ]
        
        filtered = self.analyzer._filter_symbol_data(options_data, "AAPL")
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["symbol"], "AAPL")
        self.assertEqual(filtered[1]["symbol"], "AAPL")
    
    def test_options_flow_analysis(self):
        """Test options flow analysis with bullish data"""
        # Create bullish options flow data
        options_flow = [
            {
                "symbol": "AAPL",
                "type": "CALL",
                "volume": 500,
                "premium": 150000,
                "strike": 180,
                "expiration": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "sweep": True,
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "AAPL",
                "type": "CALL",
                "volume": 300,
                "premium": 90000,
                "strike": 185,
                "expiration": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
                "sweep": False,
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "AAPL",
                "type": "PUT",
                "volume": 200,
                "premium": 40000,
                "strike": 160,
                "expiration": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "sweep": False,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        signal, details = self.analyzer.analyze_options_flow(options_flow)
        
        # Should be bullish signal (positive)
        self.assertGreater(signal, 0)
        self.assertEqual(details["call_volume"], 800)
        self.assertEqual(details["put_volume"], 200)
        self.assertEqual(details["call_premium"], 240000)
        self.assertEqual(details["put_premium"], 40000)
    
    def test_dark_pool_analysis(self):
        """Test dark pool analysis with bearish data"""
        # Create bearish dark pool data
        dark_pool = [
            {
                "symbol": "AAPL",
                "side": "SELL",
                "volume": 50000,
                "price": 175.50,
                "value": 8775000,
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "AAPL",
                "side": "SELL",
                "volume": 30000,
                "price": 175.25,
                "value": 5257500,
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "AAPL",
                "side": "BUY",
                "volume": 20000,
                "price": 175.00,
                "value": 3500000,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        signal, details = self.analyzer.analyze_dark_pool(dark_pool)
        
        # Should be bearish signal (negative)
        self.assertLess(signal, 0)
        self.assertEqual(details["buy_volume"], 20000)
        self.assertEqual(details["sell_volume"], 80000)
    
    def test_block_trades_analysis(self):
        """Test block trades analysis"""
        # Create block trade data
        block_trades = [
            {
                "symbol": "AAPL",
                "side": "BUY",
                "volume": 100000,
                "price": 175.50,
                "value": 17550000,
                "institution": "BlackRock",
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "AAPL",
                "side": "SELL",
                "volume": 50000,
                "price": 175.25,
                "value": 8762500,
                "institution": "Citadel",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        signal, details = self.analyzer.analyze_block_trades(block_trades)
        
        # Should be bullish since buy blocks have more value
        self.assertGreater(signal, 0)
        self.assertEqual(details["buy_blocks"], 1)
        self.assertEqual(details["sell_blocks"], 1)
        self.assertEqual(details["buy_notional"], 17550000)
        self.assertEqual(details["sell_notional"], 8762500)
    
    def test_overall_flow_analysis(self):
        """Test the complete flow analysis process"""
        symbol = "AAPL"
        
        # Analyze flow
        result = self.analyzer.analyze_flow(self.flow_data, self.market_data, symbol)
        
        # Check result structure
        self.assertEqual(result["symbol"], symbol)
        self.assertIn("signal", result)
        self.assertIn("options_signal", result)
        self.assertIn("dark_pool_signal", result)
        self.assertIn("block_trade_signal", result)
        self.assertIn("confidence", result)
        self.assertIn("details", result)
        self.assertIn("has_significant_flow", result)
        
        # Verify signal calculation
        self.assertIsInstance(result["signal"], float)
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)
    
    def test_volatility_adjustment(self):
        """Test volatility adjustment calculation"""
        # Create market data with high volatility
        high_vol_data = self._create_mock_market_data(volatility=0.03)  # 3% daily vol = ~48% annual
        
        # Calculate adjustment
        adjustment = self.analyzer.calculate_volatility_adjustment(high_vol_data)
        
        # Should reduce signal for high volatility
        self.assertLess(adjustment, 1.0)
        
        # Create market data with low volatility
        low_vol_data = self._create_mock_market_data(volatility=0.005)  # 0.5% daily vol = ~8% annual
        
        # Calculate adjustment
        adjustment = self.analyzer.calculate_volatility_adjustment(low_vol_data)
        
        # Should amplify signal for low volatility
        self.assertGreater(adjustment, 1.0)
    
    def test_smart_money_moves(self):
        """Test detection of smart money moves"""
        # Get smart money moves
        moves = self.analyzer.get_smart_money_moves(self.flow_data, min_confidence=0.7)
        
        # Verify structure
        for move in moves:
            self.assertIn("type", move)
            self.assertIn("symbol", move)
            self.assertIn("sentiment", move)
            self.assertIn("confidence", move)
            self.assertIn("description", move)
            self.assertGreaterEqual(move["confidence"], 0.7)
    
    def test_price_correlations(self):
        """Test price correlation calculations"""
        symbol = "AAPL"
        
        # Calculate correlations
        correlations = self.analyzer.calculate_price_correlations(self.flow_data, self.market_data, symbol)
        
        # Verify structure
        self.assertIn("short_term", correlations)
        self.assertIn("medium_term", correlations)
        self.assertIn("long_term", correlations)
        
        # Values should be between -1 and 1
        self.assertGreaterEqual(correlations["short_term"], -1.0)
        self.assertLessEqual(correlations["short_term"], 1.0)
    
    def _create_mock_flow_data(self):
        """Create mock flow data for testing"""
        symbols = ["AAPL", "MSFT", "GOOGL"]
        now = datetime.now()
        
        options_flow = []
        dark_pool = []
        block_trades = []
        
        # Generate options flow data
        for symbol in symbols:
            for _ in range(5):
                option_type = "CALL" if np.random.random() > 0.4 else "PUT"
                hours_back = np.random.randint(1, 48)
                timestamp = now - timedelta(hours=hours_back)
                
                options_flow.append({
                    "symbol": symbol,
                    "type": option_type,
                    "volume": np.random.randint(50, 500),
                    "premium": np.random.randint(10000, 500000),
                    "strike": 100 + np.random.randint(-20, 20),
                    "expiration": (now + timedelta(days=np.random.randint(7, 90))).strftime("%Y-%m-%d"),
                    "sweep": np.random.random() > 0.7,
                    "block": np.random.random() > 0.8,
                    "timestamp": timestamp.isoformat()
                })
        
        # Generate dark pool data
        for symbol in symbols:
            for _ in range(5):
                side = "BUY" if np.random.random() > 0.4 else "SELL"
                hours_back = np.random.randint(1, 48)
                timestamp = now - timedelta(hours=hours_back)
                
                dark_pool.append({
                    "symbol": symbol,
                    "side": side,
                    "volume": np.random.randint(1000, 50000),
                    "price": 100 + np.random.randint(-5, 5),
                    "value": np.random.randint(100000, 5000000),
                    "timestamp": timestamp.isoformat(),
                    "off_hours": np.random.random() > 0.7
                })
        
        # Generate block trade data
        institutions = ["BlackRock", "Vanguard", "Fidelity", "Citadel", "Renaissance"]
        for symbol in symbols:
            for _ in range(3):
                side = "BUY" if np.random.random() > 0.4 else "SELL"
                hours_back = np.random.randint(1, 48)
                timestamp = now - timedelta(hours=hours_back)
                
                block_trades.append({
                    "symbol": symbol,
                    "side": side,
                    "volume": np.random.randint(10000, 100000),
                    "price": 100 + np.random.randint(-5, 5),
                    "value": np.random.randint(1000000, 10000000),
                    "institution": np.random.choice(institutions),
                    "timestamp": timestamp.isoformat()
                })
        
        return {
            "options_flow": options_flow,
            "dark_pool": dark_pool,
            "block_trades": block_trades
        }
    
    def _create_mock_market_data(self, days=30, volatility=0.01):
        """Create mock market data for testing"""
        dates = pd.date_range(end=datetime.now(), periods=days)
        price = 100.0
        prices = []
        
        for _ in range(days):
            daily_return = np.random.normal(0.0005, volatility)  # Slight upward drift
            price *= (1 + daily_return)
            
            high = price * (1 + abs(np.random.normal(0, volatility / 2)))
            low = price * (1 - abs(np.random.normal(0, volatility / 2)))
            open_price = price * (1 + np.random.normal(0, volatility / 4))
            close = price
            volume = int(1000000 * (1 + np.random.normal(0, 0.3)))
            
            prices.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(prices, index=dates)
        return df

if __name__ == '__main__':
    unittest.main() 