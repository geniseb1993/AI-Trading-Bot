import requests
import json
import sys
import time

def test_bot_management_server():
    """
    Test the functionality of the simplified bot management server
    """
    BASE_URL = "http://localhost:5002/api"
    
    # List of endpoints to test
    endpoints = [
        {"url": "/health", "method": "GET", "name": "Health Check"},
        {"url": "/bot/status", "method": "GET", "name": "Bot Status"},
        {"url": "/status", "method": "GET", "name": "Standard Status"},
        {"url": "/dual-bot/status", "method": "GET", "name": "Dual Bot Status"},
        {"url": "/ai-activity/logs?limit=5", "method": "GET", "name": "AI Activity Logs"},
        {"url": "/ai-activity/activity-types", "method": "GET", "name": "AI Activity Types"}
    ]
    
    # Bot operations to test
    bot_operations = [
        {"url": "/bot/start/autonomous-bot", "method": "POST", "name": "Start Autonomous Bot"},
        {"url": "/bot/start/rsi-bot", "method": "POST", "name": "Start RSI Bot"},
        {"url": "/bot/start/dual-bot", "method": "POST", "name": "Start Dual Bot"},
        {"url": "/bot/status", "method": "GET", "name": "Verify Bots Started"},
        {"url": "/bot/stop/autonomous-bot", "method": "POST", "name": "Stop Autonomous Bot"},
        {"url": "/bot/stop/rsi-bot", "method": "POST", "name": "Stop RSI Bot"},
        {"url": "/bot/stop/dual-bot", "method": "POST", "name": "Stop Dual Bot"},
        {"url": "/bot/status", "method": "GET", "name": "Verify Bots Stopped"}
    ]
    
    print("\n=== Testing Bot Management Server ===\n")
    
    # Test endpoints
    print("Testing basic endpoints:")
    for endpoint in endpoints:
        try:
            print(f"  Testing {endpoint['name']} ({endpoint['url']})...", end="")
            url = f"{BASE_URL}{endpoint['url']}"
            
            if endpoint['method'] == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, timeout=5)
                
            if response.status_code == 200:
                print(f" SUCCESS ({response.status_code})")
                
                # Print a summary of the response for some endpoints
                if "/status" in endpoint['url']:
                    data = response.json()
                    if "status" in data:
                        bot_statuses = data["status"]
                        for bot_name, bot_info in bot_statuses.items():
                            print(f"    - {bot_name}: {bot_info.get('status', 'unknown')}")
            else:
                print(f" FAILED ({response.status_code})")
                print(f"    Response: {response.text}")
                
        except Exception as e:
            print(f" ERROR: {str(e)}")
    
    # Test bot operations
    print("\nTesting bot operations:")
    for operation in bot_operations:
        try:
            print(f"  {operation['name']} ({operation['url']})...", end="")
            url = f"{BASE_URL}{operation['url']}"
            
            if operation['method'] == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, timeout=5)
                
            if response.status_code == 200:
                print(f" SUCCESS ({response.status_code})")
                
                # Print response summary for status checks
                if "/status" in operation['url']:
                    data = response.json()
                    if "status" in data:
                        bot_statuses = data["status"]
                        for bot_name, bot_info in bot_statuses.items():
                            print(f"    - {bot_name}: {bot_info.get('status', 'unknown')}")
                            
                # Add a small delay between operations to see status changes
                if operation['method'] == "POST":
                    time.sleep(1)
            else:
                print(f" FAILED ({response.status_code})")
                print(f"    Response: {response.text}")
                
        except Exception as e:
            print(f" ERROR: {str(e)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    try:
        # Check if server is running first
        print("Checking if bot management server is running...")
        try:
            response = requests.get("http://localhost:5002/api/health", timeout=2)
            if response.status_code == 200:
                print("Server is running - proceeding with tests")
                test_bot_management_server()
            else:
                print(f"Server returned status code {response.status_code}")
                print("Please make sure the server is running (run start_bot_management_server.bat)")
                sys.exit(1)
        except requests.exceptions.ConnectionError:
            print("Connection error - server is not running")
            print("Please start the server first with start_bot_management_server.bat")
            sys.exit(1)
        except Exception as e:
            print(f"Error checking server status: {str(e)}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(0) 