from alpaca_trade_api.rest import REST, TimeFrame

API_KEY = PKFYIQKN2WHT06H9XGVU
API_SECRET = hetakpN3nq0Qm8AzRFlA8k6wmq3BSuO8RRdcHWwv
BASE_URL = https://alpaca.markets/

# Initialize API connection
api = REST(API_KEY, API_SECRET, BASE_URL)

# Fetch recent QQQ prices
barset = api.get_bars("QQQ", TimeFrame.Day, limit=5)
print(barset)
