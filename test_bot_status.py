import requests
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:5000"

def test_bot_status():
    """Test the bot status endpoint"""
    print("\n======= Testing Bot Status API =======")
    
    url = f"{API_BASE_URL}/api/bot/status"
    print(f"GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse Summary:")
            
            # Print autonomous bot status
            auto_bot = data.get("autonomous_bot", {})
            print(f"\nAutonomous Bot:")
            print(f"  Status: {'Running' if auto_bot.get('status', False) else 'Stopped'}")
            print(f"  Last Update: {auto_bot.get('last_update', 'N/A')}")
            print(f"  Active Trades: {len(auto_bot.get('active_trades', []))}")
            if 'error' in auto_bot:
                print(f"  Error: {auto_bot['error']}")
            
            # Print RSI bot status
            rsi_bot = data.get("rsi_bot", {})
            print(f"\nRSI Bot:")
            print(f"  Status: {'Running' if rsi_bot.get('status', False) else 'Stopped'}")
            print(f"  Last Update: {rsi_bot.get('last_update', 'N/A')}")
            print(f"  Active Signals: {len(rsi_bot.get('active_signals', []))}")
            if 'error' in rsi_bot:
                print(f"  Error: {rsi_bot['error']}")
            
            # Print dual bot status
            dual_bot = data.get("dual_bot", {})
            print(f"\nDual Bot:")
            print(f"  Status: {'Running' if dual_bot.get('status', False) else 'Stopped'}")
            print(f"  Last Update: {dual_bot.get('last_update', 'N/A')}")
            print(f"  Active Positions: {len(dual_bot.get('active_positions', []))}")
            if 'error' in dual_bot:
                print(f"  Error: {dual_bot['error']}")
            
            return data
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error connecting to API: {str(e)}")
        return None

def test_start_stop_bot(bot_type):
    """Test starting and stopping a specific bot"""
    print(f"\n======= Testing Start/Stop for {bot_type} Bot =======")
    
    # Get current status
    current_status = test_bot_status()
    if not current_status:
        print("Could not get current status, aborting test")
        return
    
    # Determine current bot status
    bot_key = f"{bot_type}_bot"
    is_running = current_status.get(bot_key, {}).get("status", False)
    
    # First test: If running, stop it
    if is_running:
        print(f"\nTesting STOP for {bot_type} bot...")
        url = f"{API_BASE_URL}/api/bot/stop/{bot_type}"
        try:
            response = requests.post(url, json={})
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # Wait a few seconds
            print("Waiting 3 seconds...")
            time.sleep(3)
            
            # Check status again
            print(f"\nChecking status after stopping...")
            after_stop = test_bot_status()
            new_status = after_stop.get(bot_key, {}).get("status", False)
            if new_status:
                print(f"ERROR: {bot_type} bot is still running after stop request")
            else:
                print(f"SUCCESS: {bot_type} bot stopped successfully")
        
        except Exception as e:
            print(f"Error testing stop: {str(e)}")
    
    # Second test: Start the bot
    print(f"\nTesting START for {bot_type} bot...")
    url = f"{API_BASE_URL}/api/bot/start/{bot_type}"
    try:
        response = requests.post(url, json={})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Wait a few seconds
        print("Waiting 3 seconds...")
        time.sleep(3)
        
        # Check status again
        print(f"\nChecking status after starting...")
        after_start = test_bot_status()
        new_status = after_start.get(bot_key, {}).get("status", False)
        if not new_status:
            print(f"ERROR: {bot_type} bot is not running after start request")
        else:
            print(f"SUCCESS: {bot_type} bot started successfully")
    
    except Exception as e:
        print(f"Error testing start: {str(e)}")
    
    # If we started it but it was originally stopped, let's stop it again
    if not is_running:
        print(f"\nRestoring original state (stopping {bot_type} bot)...")
        url = f"{API_BASE_URL}/api/bot/stop/{bot_type}"
        try:
            response = requests.post(url, json={})
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error restoring state: {str(e)}")

if __name__ == "__main__":
    print(f"Bot Status Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test 1: Get bot status
    status_data = test_bot_status()
    
    if status_data:
        print("\nChoose a bot to test start/stop functionality:")
        print("1. Autonomous Bot")
        print("2. RSI Bot")
        print("3. Dual Bot")
        print("4. Test All Bots")
        print("5. Skip Start/Stop Tests")
        
        choice = input("\nEnter choice (1-5): ")
        
        if choice == "1":
            test_start_stop_bot("autonomous")
        elif choice == "2":
            test_start_stop_bot("rsi")
        elif choice == "3":
            test_start_stop_bot("dual")
        elif choice == "4":
            test_start_stop_bot("autonomous")
            test_start_stop_bot("rsi")
            test_start_stop_bot("dual")
        
    print("\nTest complete!") 