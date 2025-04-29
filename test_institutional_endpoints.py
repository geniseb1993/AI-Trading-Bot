import requests
import json

BASE_URL = "http://localhost:5001"

def test_basic_institutional_flow():
    """Test the basic institutional flow endpoint"""
    url = f"{BASE_URL}/api/institutional-flow"
    print(f"Testing GET {url}")
    response = requests.get(url)
    if response.status_code == 200:
        print("✅ Basic institutional flow endpoint is working")
        data = response.json()
        print(f"Returned {len(data.get('data', []))} items")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def test_filtered_institutional_flow():
    """Test the filtered institutional flow endpoint"""
    url = f"{BASE_URL}/api/institutional-flow/get-data"
    payload = {
        "type": "options-flow",
        "timeframe": "today",
        "sector": "technology"
    }
    print(f"Testing POST {url}")
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Filtered institutional flow endpoint is working")
        data = response.json()
        print(f"Returned {len(data.get('data', []))} items")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def test_enhanced_analysis():
    """Test the enhanced analysis endpoint"""
    url = f"{BASE_URL}/api/institutional-flow/enhanced-analysis"
    payload = {
        "symbols": ["AAPL", "MSFT"],
        "days_back": 30
    }
    print(f"Testing POST {url}")
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Enhanced analysis endpoint is working")
        data = response.json()
        print(f"Analyzed {len(data.get('flow_analysis', {}))} symbols")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def test_13f_filings():
    """Test the 13F filings endpoint"""
    url = f"{BASE_URL}/api/13f-filings"
    print(f"Testing GET {url}")
    response = requests.get(url)
    if response.status_code == 200:
        print("✅ 13F filings endpoint is working")
        data = response.json()
        print(f"Returned {len(data.get('data', []))} items")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def test_insider_trading():
    """Test the insider trading endpoint"""
    url = f"{BASE_URL}/api/insider-trading"
    print(f"Testing GET {url}")
    response = requests.get(url)
    if response.status_code == 200:
        print("✅ Insider trading endpoint is working")
        data = response.json()
        print(f"Returned {len(data.get('data', []))} items")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Testing institutional flow endpoints...")
    test_basic_institutional_flow()
    print("\n")
    test_filtered_institutional_flow()
    print("\n")
    test_enhanced_analysis()
    print("\n")
    test_13f_filings()
    print("\n")
    test_insider_trading() 