import requests
import json

API_BASE_URL = "http://localhost:5000"

def test_connection():
    """Test the API connection and bot components availability"""
    print("\n======= Testing API Connection =======")
    
    # Test 1: Health endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        print(f"Health Check: Status Code {response.status_code}")
        if response.status_code == 200:
            print("API is responding to health checks")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to API: {str(e)}")
        return
    
    # Test 2: Bot connection check
    try:
        response = requests.get(f"{API_BASE_URL}/api/bot/connection-check")
        print(f"Bot Connection Check: Status Code {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("\nComponents Status:")
            if 'components' in data:
                for comp, status in data['components'].items():
                    print(f"  - {comp}: {'Available' if status else 'Not Available'}")
            else:
                print("No component information returned")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error checking bot connection: {str(e)}")
    
    # Test 3: Bot status endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/api/bot/status")
        print(f"\nBot Status: Status Code {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("\nBots Status:")
            # Check if autonomous_bot key exists
            if 'autonomous_bot' in data:
                print(f"  - Autonomous Bot: {'Running' if data['autonomous_bot'].get('status', False) else 'Stopped'}")
            else:
                print("  - Autonomous Bot: Not Found in Response")
                
            # Check if rsi_bot key exists
            if 'rsi_bot' in data:
                print(f"  - RSI Bot: {'Running' if data['rsi_bot'].get('status', False) else 'Stopped'}")
            else:
                print("  - RSI Bot: Not Found in Response")
                
            # Check if dual_bot key exists
            if 'dual_bot' in data:
                print(f"  - Dual Bot: {'Running' if data['dual_bot'].get('status', False) else 'Stopped'}")
            else:
                print("  - Dual Bot: Not Found in Response")
                
            # Print entire response for debugging
            print("\nFull Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error getting bot status: {str(e)}")

if __name__ == "__main__":
    test_connection() 