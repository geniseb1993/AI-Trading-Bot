import requests
import json
from datetime import datetime
import time
import traceback

def test_endpoint(endpoint, method='GET', data=None, timeout=10):
    """Test an API endpoint and print the response"""
    base_url = 'http://localhost:5000/api/dual-bot'
    url = f'{base_url}/{endpoint}'
    
    print(f"\n🔄 Testing {method} {url}")
    start_time = time.time()
    try:
        if method == 'GET':
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, json=data, timeout=timeout)
        
        elapsed = time.time() - start_time
        print(f"Status Code: {response.status_code} (took {elapsed:.2f}s)")
        if response.status_code == 200:
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {str(e)}")
        print("Make sure the Flask server is running and accessible")
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error after {timeout}s: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())

def main():
    print("🤖 Testing Dual Bot API Endpoints")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait a bit for server to fully start
    print("Waiting 2 seconds for server to initialize...")
    time.sleep(2)
    
    # Test status endpoint
    test_endpoint('status')
    
    # Test signals endpoint
    test_endpoint('signals')
    
    # Test generate-signals endpoint
    test_endpoint('generate-signals', method='POST')

if __name__ == "__main__":
    main() 