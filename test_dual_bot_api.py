import requests
import json
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = "http://localhost:5001/api"

def format_json(data):
    """Format JSON data for display"""
    return json.dumps(data, indent=2, sort_keys=True)

def test_health():
    """Test the health endpoint."""
    try:
        endpoint = f"{API_BASE_URL}/health"
        logger.info(f"Testing health endpoint: {endpoint}")
        
        response = requests.get(endpoint, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Health endpoint response: {format_json(data)}")
        
        # Verify health data
        assert response.status_code == 200
        assert 'status' in data
        assert data['status'] == 'healthy'
        
        logger.info("✅ Health endpoint test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Health endpoint test FAILED: {str(e)}")
        return False

def test_status():
    """Test the status endpoint."""
    try:
        endpoint = f"{API_BASE_URL}/status"
        logger.info(f"Testing status endpoint: {endpoint}")
        
        response = requests.get(endpoint, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Status endpoint response: {format_json(data)}")
        
        # Verify status data
        assert response.status_code == 200
        assert 'dual_bot' in data
        assert 'status' in data['dual_bot']
        assert 'last_active' in data['dual_bot']
        
        logger.info("✅ Status endpoint test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Status endpoint test FAILED: {str(e)}")
        return False

def test_dual_bot_status():
    """Test the dedicated dual bot status endpoint."""
    try:
        endpoint = f"{API_BASE_URL}/dual-bot/status"
        logger.info(f"Testing dual bot status endpoint: {endpoint}")
        
        response = requests.get(endpoint, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Dual bot status endpoint response: {format_json(data)}")
        
        # Verify dual bot status data
        assert response.status_code == 200
        assert 'dual_bot' in data
        assert 'status' in data['dual_bot']
        assert 'last_active' in data['dual_bot']
        
        logger.info("✅ Dual bot status endpoint test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Dual bot status endpoint test FAILED: {str(e)}")
        return False

def test_market_data(symbol="QQQ"):
    """Test the market data endpoint."""
    try:
        endpoint = f"{API_BASE_URL}/market-data/{symbol}"
        logger.info(f"Testing market data endpoint: {endpoint}")
        
        response = requests.get(endpoint, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Market data for {symbol}: {format_json(data)}")
        
        # Verify market data
        assert response.status_code == 200
        assert 'symbol' in data
        assert data['symbol'] == symbol
        assert 'price' in data
        assert 'volume' in data
        
        logger.info(f"✅ Market data endpoint test for {symbol} PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Market data endpoint test for {symbol} FAILED: {str(e)}")
        return False

def test_options_data(symbol="QQQ"):
    """Test the options data endpoint."""
    try:
        endpoint = f"{API_BASE_URL}/options-data/{symbol}"
        logger.info(f"Testing options data endpoint: {endpoint}")
        
        response = requests.get(endpoint, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Options data summary for {symbol}: {len(data.get('options', []))} options available")
        
        # Verify options data
        assert response.status_code == 200
        assert 'symbol' in data
        assert data['symbol'] == symbol
        assert 'underlying_price' in data
        assert 'options' in data
        assert isinstance(data['options'], list)
        assert len(data['options']) > 0
        
        logger.info(f"✅ Options data endpoint test for {symbol} PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Options data endpoint test for {symbol} FAILED: {str(e)}")
        return False

def test_news(symbol="QQQ"):
    """Test the news endpoint."""
    try:
        endpoint = f"{API_BASE_URL}/news/{symbol}"
        logger.info(f"Testing news endpoint: {endpoint}")
        
        response = requests.get(endpoint, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"News summary for {symbol}: {len(data.get('news', []))} news items available")
        
        # Verify news data
        assert response.status_code == 200
        assert 'symbol' in data
        assert data['symbol'] == symbol
        assert 'news' in data
        assert isinstance(data['news'], list)
        assert len(data['news']) > 0
        
        logger.info(f"✅ News endpoint test for {symbol} PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ News endpoint test for {symbol} FAILED: {str(e)}")
        return False

def test_signals():
    """Test the dual bot signals endpoint."""
    try:
        endpoint = f"{API_BASE_URL}/dual-bot/signals"
        logger.info(f"Testing signals endpoint: {endpoint}")
        
        response = requests.get(endpoint, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Signals summary: {len(data.get('signals', []))} signals available")
        
        # Verify signals data
        assert response.status_code == 200
        assert 'success' in data
        assert data['success'] == True
        assert 'signals' in data
        assert isinstance(data['signals'], list)
        assert len(data['signals']) > 0
        
        # Check if first signal has required fields
        if len(data['signals']) > 0:
            signal = data['signals'][0]
            required_fields = ['symbol', 'type', 'signal_score', 'price_target', 'stop_loss']
            for field in required_fields:
                assert field in signal, f"Signal missing required field: {field}"
        
        logger.info("✅ Signals endpoint test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Signals endpoint test FAILED: {str(e)}")
        return False

def test_assess_risk():
    """Test the assess-risk endpoint."""
    try:
        endpoint = f"{API_BASE_URL}/assess-risk"
        logger.info(f"Testing assess-risk endpoint: {endpoint}")
        
        # Test payload
        payload = {
            "recommendation": {
                "symbol": "QQQ",
                "trade_type": "BUY",
                "strike": 450,
                "expiration": "2025-01-15",
                "entry_price": 3.25,
                "target_price": 5.50,
                "stop_loss": 1.75,
                "confidence": 0.85
            },
            "market_context": {
                "price": 450.75,
                "volatility": "medium",
                "market_condition": "bullish"
            }
        }
        
        response = requests.post(endpoint, json=payload, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Assess risk endpoint response: {format_json(data)}")
        
        # Verify risk assessment data
        assert response.status_code == 200
        assert 'success' in data
        assert data['success'] == True
        assert 'approved' in data
        assert 'risk_score' in data
        assert 'concerns' in data
        
        logger.info("✅ Assess risk endpoint test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Assess risk endpoint test FAILED: {str(e)}")
        return False

def run_all_tests():
    """Run all API tests"""
    logger.info(f"Starting API tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    # Test health endpoint first (critical)
    test_results['health'] = test_health()
    
    if not test_results['health']:
        logger.error("Health endpoint test failed, aborting further tests.")
        return test_results
    
    # Test other endpoints
    test_results['status'] = test_status()
    test_results['dual_bot_status'] = test_dual_bot_status()
    test_results['market_data'] = test_market_data()
    test_results['options_data'] = test_options_data()
    test_results['news'] = test_news()
    test_results['signals'] = test_signals()
    test_results['assess_risk'] = test_assess_risk()
    
    # Print summary
    logger.info("\n=== TEST SUMMARY ===")
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    # Overall result
    all_passed = all(test_results.values())
    logger.info(f"\nOVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return test_results

if __name__ == "__main__":
    run_all_tests() 