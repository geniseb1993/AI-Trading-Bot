import requests
import json
import sys

def test_endpoints():
    BASE_URL = "http://localhost:5001/api"
    
    endpoints = [
        "/cors-test",
        "/dual-bot/status",
        "/dual-bot/signals",
        "/config"
    ]
    
    print("\n=== Testing Dual Bot API Endpoints ===\n")
    
    for endpoint in endpoints:
        try:
            print(f"Testing {endpoint}...")
            response = requests.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS - Status code: {response.status_code}")
                data = response.json()
                
                # Print just a summary of the response to keep output clean
                if isinstance(data, dict):
                    keys = list(data.keys())
                    print(f"Response contains keys: {keys}")
                else:
                    print(f"Response type: {type(data)}")
            else:
                print(f"❌ FAILED - Status code: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR - {endpoint}: {str(e)}")
        
        print("")  # Add empty line between endpoint tests
    
    print("=== All tests completed ===")

if __name__ == "__main__":
    test_endpoints() 