# test_connection.py

# Import the necessary library
import alpaca_trade_api as tradeapi

# Your API Key, Secret, and Endpoint
API_KEY = "AK24VRQSSSMJJ11KWUPL"
API_SECRET = "4KemAIFEvfudDCcWHuDsKnpmwJzxKaWiEqvkBtWN"
BASE_URL = "https://api.alpaca.markets"  # This is the live trading endpoint

# Print to confirm the script has started
print("Starting Alpaca API connection test...")

try:
    # Initialize the Alpaca API connection
    api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

    # Fetch account information to verify the connection
    account = api.get_account()

    # If the connection is successful, print account status
    print(f"Connection successful! Account status: {account.status}")
    
except Exception as e:
    # If an error occurs, print the error message
    print(f"Error occurred while connecting to Alpaca API: {e}")

