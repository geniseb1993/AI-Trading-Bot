import requests
import json
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dual_bot_api_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_endpoint(base_url, endpoint, method="GET", data=None, expected_status=200):
    """
    Test a specific API endpoint
    
    Args:
        base_url: Base URL of the API
        endpoint: Endpoint to test
        method: HTTP method (GET or POST)
        data: Data to send for POST requests
        expected_status: Expected HTTP status code
        
    Returns:
        tuple: (success, response_data)
    """
    url = f"{base_url}{endpoint}"
    
    try:
        logger.info(f"Testing {method} {endpoint}...")
        
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        else:
            logger.error(f"Unsupported method: {method}")
            return False, None
        
        if response.status_code == expected_status:
            logger.info(f"✅ SUCCESS - Status code: {response.status_code}")
            
            try:
                response_data = response.json()
                
                # Print summary of response
                if isinstance(response_data, dict):
                    keys = list(response_data.keys())
                    logger.info(f"Response contains keys: {keys}")
                elif isinstance(response_data, list):
                    logger.info(f"Response is a list with {len(response_data)} items")
                else:
                    logger.info(f"Response type: {type(response_data)}")
                
                return True, response_data
            except json.JSONDecodeError:
                logger.warning(f"Response is not JSON: {response.text}")
                return True, response.text
        else:
            logger.error(f"❌ FAILED - Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        logger.error(f"❌ ERROR - {endpoint}: {str(e)}")
        return False, None

def test_all_endpoints():
    """Test all available endpoints in the dual bot API"""
    BASE_URL = "http://localhost:5001/api"
    
    # Map of endpoints to test with their configuration
    endpoints = [
        # Basic endpoints
        {"endpoint": "/health", "method": "GET"},
        {"endpoint": "/status", "method": "GET"},
        {"endpoint": "/config", "method": "GET"},
        {"endpoint": "/cors-test", "method": "GET"},
        {"endpoint": "/test-frontend-cors", "method": "GET"},
        
        # Dual bot specific endpoints
        {"endpoint": "/dual-bot/status", "method": "GET"},
        {"endpoint": "/dual-bot/signals", "method": "GET"},
        
        # Market data endpoints
        {"endpoint": "/market-data/QQQ", "method": "GET"},
        {"endpoint": "/market-data/TSLA", "method": "GET"},
        {"endpoint": "/options-data/SPY", "method": "GET"},
        {"endpoint": "/news/AAPL", "method": "GET"},
        
        # POST endpoints with sample data
        {
            "endpoint": "/scan", 
            "method": "POST",
            "data": {"symbol": "MSFT"}
        },
        {
            "endpoint": "/assess-risk", 
            "method": "POST",
            "data": {
                "recommendation": {
                    "symbol": "NVDA",
                    "trade_type": "BUY_CALL",
                    "confidence": 0.85
                },
                "market_context": {
                    "volatility": "medium",
                    "trend": "bullish"
                }
            }
        },
        {
            "endpoint": "/check-position", 
            "method": "POST",
            "data": {"symbol": "PLTR"}
        }
    ]
    
    print("\n" + "="*50)
    print(f"DUAL BOT API TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")
    
    # Track results
    results = {
        "total": len(endpoints),
        "success": 0,
        "failed": 0,
        "errors": []
    }
    
    # Test each endpoint
    for config in endpoints:
        endpoint = config["endpoint"]
        method = config["method"]
        data = config.get("data")
        
        print(f"\n--- Testing {method} {endpoint} ---")
        success, response = test_endpoint(BASE_URL, endpoint, method, data)
        
        if success:
            results["success"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(f"{method} {endpoint}")
        
        print("-" * 40)
    
    # Print summary
    print("\n" + "="*50)
    print(f"TEST SUMMARY: {results['success']}/{results['total']} tests passed")
    
    if results["failed"] > 0:
        print(f"\nFailed endpoints ({results['failed']}):")
        for error in results["errors"]:
            print(f"- {error}")
    
    print("="*50 + "\n")
    
    return results["failed"] == 0

if __name__ == "__main__":
    success = test_all_endpoints()
    sys.exit(0 if success else 1) 