import requests
import json
from datetime import datetime

# API endpoints
API_BASE_URL = "http://localhost:5000"
BOT_STATUS_ENDPOINT = f"{API_BASE_URL}/api/bot/status"

def test_bot_status():
    """
    Test the bot status endpoint to verify if it's working correctly
    """
    print(f"\n===== Testing Bot Status API at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")
    
    try:
        # Make the request to the bot status endpoint
        print(f"GET {BOT_STATUS_ENDPOINT}")
        response = requests.get(BOT_STATUS_ENDPOINT)
        
        # Print the response status code
        print(f"Status Code: {response.status_code}")
        
        # If the request was successful, print the bot statuses
        if response.status_code == 200:
            data = response.json()
            print("\nBot Status Summary:")
            
            # Print status for each bot
            for bot_type in ['autonomous_bot', 'rsi_bot', 'dual_bot']:
                if bot_type in data:
                    bot_data = data[bot_type]
                    status_text = "Running" if bot_data.get('status') == 'active' else "Inactive"
                    print(f"\n{bot_type.replace('_', ' ').title()}:")
                    print(f"  Status: {status_text}")
                    print(f"  Last Active: {bot_data.get('last_active', 'N/A')}")
                    print(f"  Trades Executed: {bot_data.get('trades_executed', 'N/A')}")
                    print(f"  Success Rate: {bot_data.get('success_rate', 'N/A')}")
                    print(f"  Current Positions: {bot_data.get('current_positions', 'N/A')}")
                    
                    if 'error' in bot_data:
                        print(f"  Error: {bot_data['error']}")
            
            return data
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error connecting to API: {str(e)}")
        return None

if __name__ == "__main__":
    print("Simple Bot Status Test Tool")
    print("==========================")
    print("This tool checks if the bot management server is running and returns the current status of all bots.")
    
    # Run the test
    test_bot_status()
    
    print("\nTest complete!") 