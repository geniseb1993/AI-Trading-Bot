import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint and print the response"""
    url = f"{BASE_URL}/{endpoint}"
    print(f"\nTesting {method} {url}")
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing endpoint: {str(e)}")
    print("-" * 80)

def main():
    # Test health check
    test_endpoint("health")
    
    # Test market data endpoints
    test_endpoint("market-data/sources")
    test_endpoint("market-data/config")
    
    # Test trading signals
    test_endpoint("get-saved-signals")
    
    # Test market overview
    test_endpoint("market-overview")
    
    # Test portfolio data
    test_endpoint("user-portfolio")
    test_endpoint("active-trades")
    
    # Test AI signals for a specific symbol
    test_endpoint("market/ai_signals/AAPL")
    
    # Test generating new signals
    test_endpoint("generate-signals", method="POST", data={
        "symbols": ["AAPL", "MSFT", "GOOGL"],
        "timeframe": "1d"
    })

if __name__ == "__main__":
    main() 