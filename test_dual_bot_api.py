import requests
import json
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dual_bot_api_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API Base URL
API_BASE_URL = "http://localhost:5001/api"

def test_api_health():
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        logger.info(f"Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False

def test_bot_status():
    """Test the bot status endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=5)
        response.raise_for_status()
        logger.info(f"Bot status: {response.status_code} - {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Bot status check failed: {str(e)}")
        return False

def test_market_data(symbol="QQQ"):
    """Test the market data endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/market-data/{symbol}", timeout=5)
        response.raise_for_status()
        logger.info(f"Market data for {symbol}: {response.status_code} - {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Market data check failed for {symbol}: {str(e)}")
        return False

def test_scan_trades(symbol="QQQ"):
    """Test the scan trades endpoint."""
    try:
        payload = {"symbol": symbol}
        response = requests.post(f"{API_BASE_URL}/scan", json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Scan trades for {symbol}: {response.status_code} - {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        logger.error(f"Scan trades failed for {symbol}: {str(e)}")
        return None

def test_assess_risk(recommendation, market_context):
    """Test the risk assessment endpoint."""
    try:
        payload = {
            "recommendation": recommendation,
            "market_context": market_context
        }
        response = requests.post(f"{API_BASE_URL}/assess-risk", json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Risk assessment: {response.status_code} - {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Risk assessment failed: {str(e)}")
        return False

def test_config():
    """Test the config endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/config", timeout=5)
        response.raise_for_status()
        logger.info(f"Config: {response.status_code} - {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Config check failed: {str(e)}")
        return False

def full_test_sequence():
    """Run a full test sequence of the API."""
    logger.info("Starting full API test sequence")
    
    # Create a test summary
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test health check
    results["tests"]["health_check"] = test_api_health()
    
    # Test bot status
    results["tests"]["bot_status"] = test_bot_status()
    
    # Test market data
    results["tests"]["market_data"] = test_market_data("QQQ")
    
    # Test scan trades and risk assessment
    recommendation = test_scan_trades("QQQ")
    results["tests"]["scan_trades"] = recommendation is not None
    
    if recommendation:
        market_context = {
            "price": 450.75,  # Sample price
            "volatility": "medium",
            "market_condition": "bullish"
        }
        results["tests"]["assess_risk"] = test_assess_risk(recommendation, market_context)
    else:
        results["tests"]["assess_risk"] = False
    
    # Test config
    results["tests"]["config"] = test_config()
    
    # Calculate overall success
    total_tests = len(results["tests"])
    successful_tests = sum(1 for result in results["tests"].values() if result)
    results["summary"] = {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "success_rate": f"{(successful_tests / total_tests) * 100:.1f}%"
    }
    
    # Log the results
    logger.info(f"Test summary: {json.dumps(results['summary'], indent=2)}")
    
    # Save results to file
    with open("dual_bot_api_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    try:
        logger.info("====== DUAL BOT API TEST ======")
        results = full_test_sequence()
        
        # Print a simple summary to console
        print("\n====== TEST RESULTS ======")
        for test_name, result in results["tests"].items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nSuccess Rate: {results['summary']['success_rate']}")
        print("See dual_bot_api_test.log for detailed logs")
        
    except Exception as e:
        logger.error(f"Test script error: {str(e)}")
        print(f"Test failed with error: {str(e)}") 