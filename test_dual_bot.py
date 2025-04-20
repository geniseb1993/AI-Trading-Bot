import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000/api/dual-bot'

def test_endpoint(endpoint, method='GET', data=None):
    """Test an endpoint and print the response"""
    url = f"{BASE_URL}/{endpoint}"
    print(f"\nTesting {method} {url}")
    
    try:
        if method == 'GET':
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    # Test status endpoint
    test_endpoint('status')
    
    # Test signals endpoint
    test_endpoint('signals')
    
    # Test generate-signals endpoint
    test_endpoint('generate-signals', method='POST')

if __name__ == '__main__':
    main() 