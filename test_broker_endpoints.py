import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}/{endpoint}"
    print(f"\nTesting {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"Method {method} not supported")
            return False
            
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(json.dumps(result, indent=2))
                return True
            except json.JSONDecodeError:
                print("Error decoding JSON response")
                print(response.text)
                return False
        else:
            print(f"Error: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"Error: {e}")
        return False

def main():
    # Test broker endpoints
    print("\n=== TESTING BROKER ENDPOINTS ===")
    
    # Test get available brokers
    test_endpoint("broker/available")
    
    # Test broker info
    test_endpoint("broker/info")
    
    # Test broker config
    test_endpoint("broker/config")
    
    # Test broker account
    test_endpoint("broker/account")
    
    # Test broker positions
    test_endpoint("broker/positions")
    
    # Test broker orders
    test_endpoint("broker/orders")
    
    # Test broker market data
    test_endpoint("broker/market-data?symbol=SPY")
    
    # Test broker test connection
    test_endpoint("broker/test-connection", method="POST", data={"broker": "mock"})
    
    print("\n=== TESTS COMPLETED ===")

if __name__ == "__main__":
    main() 