import requests
import json
import sys

def test_endpoint(url, method='GET', data=None):
    """Test an API endpoint and print the response"""
    print(f"Testing {method} {url}")
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        else:
            print(f"Unsupported method: {method}")
            return
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("-" * 50)
    except Exception as e:
        print(f"Error: {str(e)}")
        print("-" * 50)

def main():
    base_url = "http://localhost:5000/api/dual-bot"
    
    # Test status endpoint
    test_endpoint(f"{base_url}/status")
    
    # Test signals endpoint
    test_endpoint(f"{base_url}/signals")
    
    # Test generate-signals endpoint
    test_endpoint(f"{base_url}/generate-signals", method='POST')

if __name__ == "__main__":
    main() 