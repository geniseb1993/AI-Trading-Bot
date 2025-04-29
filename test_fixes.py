import requests
import json

def test_endpoints():
    """Test all fixed endpoints and print results"""
    
    # Test main API server
    print("Testing main API server (port 5000)...")
    try:
        response = requests.get("http://localhost:5000/api")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Main API server is running")
        else:
            print("❌ Main API server returned an error")
    except Exception as e:
        print(f"❌ Failed to connect to main API server: {str(e)}")
    
    # Test dual bot API server
    print("\nTesting dual bot API server (port 5001)...")
    try:
        response = requests.get("http://localhost:5001/api/dual-bot/status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Dual bot API server is running")
        else:
            print("❌ Dual bot API server returned an error")
    except Exception as e:
        print(f"❌ Failed to connect to dual bot API server: {str(e)}")
    
    # Test bot management server
    print("\nTesting bot management server (port 5002)...")
    try:
        response = requests.get("http://localhost:5002/api/bot/status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Bot management server is running")
        else:
            print("❌ Bot management server returned an error")
    except Exception as e:
        print(f"❌ Failed to connect to bot management server: {str(e)}")
    
    # Test dashboard data endpoint
    print("\nTesting dashboard data endpoint...")
    try:
        response = requests.get("http://localhost:5001/data/dashboard/ceo_dashboard.json")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Dashboard data endpoint is working")
        else:
            print("❌ Dashboard data endpoint returned an error")
    except Exception as e:
        print(f"❌ Failed to fetch dashboard data: {str(e)}")
    
    # Test image endpoint
    print("\nTesting image endpoint...")
    try:
        response = requests.get("http://localhost:5001/images/vicky.png")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Image endpoint is working")
        else:
            print("❌ Image endpoint returned an error:", response.text)
    except Exception as e:
        print(f"❌ Failed to fetch image: {str(e)}")
    
    # Test backtest results endpoint
    print("\nTesting backtest results endpoint...")
    try:
        response = requests.get("http://localhost:5001/get-backtest-results")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Backtest results endpoint is working")
        else:
            print("❌ Backtest results endpoint returned an error")
    except Exception as e:
        print(f"❌ Failed to fetch backtest results: {str(e)}")

if __name__ == "__main__":
    test_endpoints() 