import requests
import json

BASE_URL = "http://localhost:5001"

def test_13f_filings():
    """Test the 13F filings endpoint"""
    url = f"{BASE_URL}/api/13f-filings"
    print(f"Testing GET {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ 13F filings endpoint is working")
            data = response.json()
            print(f"Returned {len(data.get('data', []))} items")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")

if __name__ == "__main__":
    print("Testing 13F filings endpoint...")
    test_13f_filings() 