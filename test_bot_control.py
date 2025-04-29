import requests
import json
import time
from datetime import datetime

# API endpoints
API_BASE_URL = "http://localhost:5000"
START_BOT_ENDPOINT = lambda bot_type: f"{API_BASE_URL}/api/bot/{bot_type}/start"
STOP_BOT_ENDPOINT = lambda bot_type: f"{API_BASE_URL}/api/bot/{bot_type}/stop"
STATUS_ENDPOINT = f"{API_BASE_URL}/api/bot/status"

def get_bot_status(bot_type=None):
    """Get the current status of all bots or a specific bot"""
    try:
        response = requests.get(STATUS_ENDPOINT)
        if response.status_code == 200:
            data = response.json()
            if bot_type:
                return data.get(bot_type, {})
            return data
        return {}
    except Exception as e:
        print(f"Error getting bot status: {str(e)}")
        return {}

def start_bot(bot_type):
    """Start a specific bot"""
    print(f"\nStarting {bot_type}...")
    try:
        response = requests.post(START_BOT_ENDPOINT(bot_type))
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error starting bot: {str(e)}")
        return False

def stop_bot(bot_type):
    """Stop a specific bot"""
    print(f"\nStopping {bot_type}...")
    try:
        response = requests.post(STOP_BOT_ENDPOINT(bot_type))
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error stopping bot: {str(e)}")
        return False

def test_bot_control(bot_type):
    """Test starting and stopping a bot"""
    print(f"\n===== Testing Bot Control for {bot_type} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")
    
    # Get initial status
    initial_status = get_bot_status(bot_type)
    initial_state = initial_status.get('status', 'unknown')
    print(f"\nInitial status of {bot_type}: {initial_state}")
    
    # Test sequence based on initial state
    if initial_state == 'active':
        # If bot is active, test stop then start
        print(f"{bot_type} is already running. Testing stop then start...")
        
        # Stop the bot
        if stop_bot(bot_type):
            # Wait a moment for status to update
            time.sleep(2)
            
            # Check if it stopped
            current_status = get_bot_status(bot_type)
            current_state = current_status.get('status', 'unknown')
            print(f"\nStatus after stopping: {current_state}")
            
            if current_state != 'inactive':
                print(f"ERROR: Failed to stop {bot_type}!")
            
            # Start the bot again (restore original state)
            if start_bot(bot_type):
                # Wait a moment for status to update
                time.sleep(2)
                
                # Check if it started
                current_status = get_bot_status(bot_type)
                current_state = current_status.get('status', 'unknown')
                print(f"\nStatus after restarting: {current_state}")
                
                if current_state != 'active':
                    print(f"ERROR: Failed to restart {bot_type}!")
    else:
        # If bot is inactive, test start then stop
        print(f"{bot_type} is not running. Testing start then stop...")
        
        # Start the bot
        if start_bot(bot_type):
            # Wait a moment for status to update
            time.sleep(2)
            
            # Check if it started
            current_status = get_bot_status(bot_type)
            current_state = current_status.get('status', 'unknown')
            print(f"\nStatus after starting: {current_state}")
            
            if current_state != 'active':
                print(f"ERROR: Failed to start {bot_type}!")
            
            # Stop the bot again (restore original state)
            if stop_bot(bot_type):
                # Wait a moment for status to update
                time.sleep(2)
                
                # Check if it stopped
                current_status = get_bot_status(bot_type)
                current_state = current_status.get('status', 'unknown')
                print(f"\nStatus after stopping: {current_state}")
                
                if current_state != 'inactive':
                    print(f"ERROR: Failed to stop {bot_type}!")

if __name__ == "__main__":
    print("Bot Control Test Tool")
    print("====================")
    print("This tool tests starting and stopping bots via the API.")
    print("Available bot types: autonomous_bot, rsi_bot, dual_bot")
    
    # Ask user which bot to test
    bot_type = input("\nWhich bot would you like to test? ")
    
    # Validate input
    valid_bots = ['autonomous_bot', 'rsi_bot', 'dual_bot']
    if bot_type not in valid_bots:
        print(f"Invalid bot type. Please choose from: {', '.join(valid_bots)}")
    else:
        # Run the test for the specified bot
        test_bot_control(bot_type)
    
    print("\nTest complete!") 