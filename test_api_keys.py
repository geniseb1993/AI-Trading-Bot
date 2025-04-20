import os
import sys
import logging
import requests
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("API_Test")

def test_alpaca_api():
    """Test Alpaca API connection and functionality"""
    try:
        import alpaca_trade_api as tradeapi
        
        api_key = os.getenv('ALPACA_API_KEY')
        api_secret = os.getenv('ALPACA_API_SECRET')
        base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not (api_key and api_secret):
            return False, "Alpaca API credentials not found in environment variables"
        
        api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
        
        # Test account info
        account = api.get_account()
        
        # Test market data
        aapl_bars = api.get_bars('AAPL', '1Day', limit=1)
        
        return True, f"Alpaca API working. Account status: {account.status}"
    except Exception as e:
        return False, f"Alpaca API error: {str(e)}"

def test_unusual_whales_api():
    """Test Unusual Whales API connection"""
    try:
        api_key = os.getenv('UNUSUAL_WHALES_API_KEY')
        
        if not api_key:
            return False, "Unusual Whales API key not found in environment variables"
        
        # Test endpoint (adjust based on actual API endpoint)
        response = requests.get(
            'https://api.unusualwhales.com/api/flow',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "Unusual Whales API working"
        else:
            return False, f"Unusual Whales API error: Status {response.status_code}"
    except Exception as e:
        return False, f"Unusual Whales API error: {str(e)}"

def test_news_api():
    """Test NewsAPI connection"""
    try:
        api_key = os.getenv('NEWS_API_KEY')
        
        if not api_key:
            return False, "NewsAPI key not found in environment variables"
        
        response = requests.get(
            f'https://newsapi.org/v2/everything?q=stock+market&apiKey={api_key}',
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "NewsAPI working"
        else:
            return False, f"NewsAPI error: Status {response.status_code}"
    except Exception as e:
        return False, f"NewsAPI error: {str(e)}"

def test_polygon_ws():
    """Test Polygon WebSocket connection"""
    try:
        api_key = os.getenv('POLYGON_API_KEY')
        
        if not api_key:
            return False, "Polygon API key not found in environment variables"
        
        # Test REST endpoint first
        response = requests.get(
            f'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2023-01-09/2024-01-09?apiKey={api_key}',
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "Polygon API working"
        else:
            return False, f"Polygon API error: Status {response.status_code}"
    except Exception as e:
        return False, f"Polygon API error: {str(e)}"

def test_signal_generation():
    """Test signal generation functionality"""
    try:
        # Import signal generation function
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app_starter import generate_signals
        
        # Try to generate signals
        generate_signals()
        
        # Check if signal files were created
        buy_signals_path = 'data/buy_signals.csv'
        short_signals_path = 'data/short_signals.csv'
        
        if os.path.exists(buy_signals_path) and os.path.exists(short_signals_path):
            buy_df = pd.read_csv(buy_signals_path)
            short_df = pd.read_csv(short_signals_path)
            return True, f"Signals generated successfully. Buy signals: {len(buy_df)}, Short signals: {len(short_df)}"
        else:
            return False, "Signal files not created"
    except Exception as e:
        return False, f"Signal generation error: {str(e)}"

def main():
    """Run all API tests and report results"""
    logger.info("Starting API tests...")
    
    # Load environment variables
    load_dotenv()
    
    # Run tests
    tests = {
        "Alpaca API": test_alpaca_api(),
        "Unusual Whales API": test_unusual_whales_api(),
        "NewsAPI": test_news_api(),
        "Polygon WebSocket": test_polygon_ws(),
        "Signal Generation": test_signal_generation()
    }
    
    # Print results
    logger.info("\n=== API Test Results ===")
    all_passed = True
    for test_name, (passed, message) in tests.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {message}")
        if not passed:
            all_passed = False
    
    logger.info("\n=== Summary ===")
    logger.info("All tests passed!" if all_passed else "Some tests failed. Please check the logs above.")
    
    return all_passed

if __name__ == "__main__":
    main() 