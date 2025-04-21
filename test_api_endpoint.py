import requests
import sys

try:
    print("Testing API server...")
    response = requests.get("http://localhost:5000/api/health", timeout=5)
    print(f"Health endpoint status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    print("\nTesting bot status endpoint...")
    bot_response = requests.get("http://localhost:5000/api/bot/status", timeout=5)
    print(f"Bot status endpoint status code: {bot_response.status_code}")
    
    if bot_response.status_code == 200:
        data = bot_response.json()
        print("Bot status data received:")
        print(f"Autonomous bot: {'Running' if data.get('autonomous_bot', {}).get('status', False) else 'Stopped'}")
        print(f"RSI bot: {'Running' if data.get('rsi_bot', {}).get('status', False) else 'Stopped'}")
        print(f"Dual bot: {'Running' if data.get('dual_bot', {}).get('status', False) else 'Stopped'}")
    else:
        print(f"Error response: {bot_response.text}")
    
except Exception as e:
    print(f"Error connecting to API: {e}")
    sys.exit(1) 