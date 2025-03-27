import alpaca_trade_api as tradeapi
from config import API_KEY, API_SECRET, BASE_URL

# Initialize the Alpaca API connection
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

try:
    # Check account info to verify the connection
    account = api.get_account()
    print(f"Connection successful! Account status: {account.status}")
except Exception as e:
    print(f"Error: {e}")
