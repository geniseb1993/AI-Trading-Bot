import requests
import json
import logging
import sys
from datetime import datetime

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('api_test.log')
        ]
    )

def test_health():
    """Test the health check endpoint."""
    try:
        response = requests.get('http://localhost:5000/api/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        logging.info("Health check test passed")
        return True
    except Exception as e:
        logging.error(f"Health check test failed: {str(e)}")
        return False

def test_market_data():
    """Test the market data endpoint."""
    try:
        symbol = 'QQQ'
        response = requests.get(f'http://localhost:5000/api/market-data/{symbol}')
        assert response.status_code == 200
        data = response.json()
        assert 'price' in data
        assert 'volume' in data
        logging.info(f"Market data test passed for {symbol}")
        return True
    except Exception as e:
        logging.error(f"Market data test failed: {str(e)}")
        return False

def test_options_data():
    """Test the options data endpoint."""
    try:
        symbol = 'QQQ'
        response = requests.get(f'http://localhost:5000/api/options-data/{symbol}')
        assert response.status_code == 200
        data = response.json()
        assert 'calls' in data
        assert 'puts' in data
        logging.info(f"Options data test passed for {symbol}")
        return True
    except Exception as e:
        logging.error(f"Options data test failed: {str(e)}")
        return False

def test_news():
    """Test the news endpoint."""
    try:
        symbol = 'QQQ'
        response = requests.get(f'http://localhost:5000/api/news/{symbol}')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        logging.info(f"News test passed for {symbol}")
        return True
    except Exception as e:
        logging.error(f"News test failed: {str(e)}")
        return False

def test_scan():
    """Test the scan endpoint."""
    try:
        response = requests.get('http://localhost:5000/api/scan')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        logging.info("Scan test passed")
        return True
    except Exception as e:
        logging.error(f"Scan test failed: {str(e)}")
        return False

def test_assess_risk():
    """Test the risk assessment endpoint."""
    try:
        test_data = {
            'symbol': 'QQQ',
            'direction': 'bullish',
            'confidence': 0.85,
            'market_context': {
                'market_hours': True,
                'market_conditions': 'normal',
                'vix': 15.5,
                'sector_performance': {'technology': 0.02}
            }
        }
        response = requests.post(
            'http://localhost:5000/api/assess-risk',
            json=test_data
        )
        assert response.status_code == 200
        data = response.json()
        assert 'risk_score' in data
        assert 'recommendation' in data
        logging.info("Risk assessment test passed")
        return True
    except Exception as e:
        logging.error(f"Risk assessment test failed: {str(e)}")
        return False

def test_check_position():
    """Test the position check endpoint."""
    try:
        test_data = {
            'symbol': 'QQQ',
            'entry_price': 400.0,
            'current_price': 405.0,
            'position_size': 100,
            'entry_time': datetime.now().isoformat()
        }
        response = requests.post(
            'http://localhost:5000/api/check-position',
            json=test_data
        )
        assert response.status_code == 200
        data = response.json()
        assert 'should_close' in data
        assert 'reason' in data
        logging.info("Position check test passed")
        return True
    except Exception as e:
        logging.error(f"Position check test failed: {str(e)}")
        return False

def test_config():
    """Test the config endpoint."""
    try:
        response = requests.get('http://localhost:5000/api/config')
        assert response.status_code == 200
        data = response.json()
        assert 'data_sources' in data
        assert 'ai_models' in data
        logging.info("Config test passed")
        return True
    except Exception as e:
        logging.error(f"Config test failed: {str(e)}")
        return False

def main():
    """Run all API tests."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting API tests...")
    
    tests = [
        ('Health Check', test_health),
        ('Market Data', test_market_data),
        ('Options Data', test_options_data),
        ('News', test_news),
        ('Scan', test_scan),
        ('Risk Assessment', test_assess_risk),
        ('Position Check', test_check_position),
        ('Config', test_config)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"Running {test_name} test...")
        success = test_func()
        results.append((test_name, success))
    
    logger.info("\nTest Results:")
    for test_name, success in results:
        status = "PASSED" if success else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    total_tests = len(tests)
    passed_tests = sum(1 for _, success in results if success)
    logger.info(f"\nTotal Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")

if __name__ == '__main__':
    main() 