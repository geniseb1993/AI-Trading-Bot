"""
Enhanced minimal Flask server that attempts to use real data from APIs.
Provides real data when possible with mock data as fallback.
"""

from flask import Flask, jsonify, request
import random
import requests
import json
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the Flask app with CORS support
app = Flask(__name__)

# Enable CORS
try:
    from flask_cors import CORS
    CORS(app)
    logger.info("CORS enabled successfully")
except ImportError:
    logger.warning("flask_cors not installed, CORS will not be enabled")

# Get API keys from environment variables
UNUSUAL_WHALES_API_KEY = os.environ.get('UNUSUAL_WHALES_API_KEY')
ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY')
ALPACA_API_SECRET = os.environ.get('ALPACA_API_SECRET')
ALPACA_BASE_URL = os.environ.get('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
USE_REAL_DATA = os.environ.get('USE_REAL_DATA', 'false').lower() == 'true'

# Log API key presence (not the actual keys)
logger.info(f"Unusual Whales API Key present: {bool(UNUSUAL_WHALES_API_KEY)}")
logger.info(f"Alpaca API Key present: {bool(ALPACA_API_KEY)}")
logger.info(f"APP_ENV: {os.environ.get('APP_ENV', 'development')}")
logger.info(f"Using real data: {USE_REAL_DATA}")

# Real data client for Unusual Whales API
class UnusualWhalesAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.unusualwhales.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        })
        logger.info("UnusualWhalesAPI client initialized")
        
    def get_dark_pool_recent(self, limit=20):
        """Get recent dark pool data"""
        try:
            endpoint = f"{self.base_url}/api/darkpool/recent"
            params = {'limit': limit}
            
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Format the data for frontend display
            formatted_data = []
            records = data.get("data", [])
            
            # Check if we got valid data
            if not isinstance(records, list) or len(records) == 0:
                logger.warning(f"Unexpected or empty data from Unusual Whales API: {type(records)}")
                return []
                
            for i, record in enumerate(records):
                formatted_record = {
                    "id": i + 1,
                    "symbol": record.get("ticker", ""),
                    "type": "block",
                    "direction": "call" if record.get("direction", "").lower() == "buy" else "put",
                    "premium": record.get("size", 0) * record.get("price", 0),
                    "strike": record.get("price", 0),
                    "expiry": None,
                    "timestamp": record.get("executed_at", datetime.now().isoformat()),
                    "sentiment": "bullish" if record.get("direction", "").lower() == "buy" else "bearish",
                    "flow_score": 80,
                    "unusual_score": 85
                }
                formatted_data.append(formatted_record)
                
            logger.info(f"Successfully retrieved {len(formatted_data)} dark pool records from Unusual Whales API")
            return formatted_data
        except Exception as e:
            logger.error(f"Error in Unusual Whales API get_dark_pool_recent: {str(e)}")
            return []
    
    def get_dark_pool_symbol(self, symbol):
        """Get dark pool data for a specific symbol"""
        try:
            endpoint = f"{self.base_url}/api/darkpool/ticker/{symbol.upper()}"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            data = response.json()
            
            # Format the data for frontend display
            formatted_data = []
            records = data.get("data", [])
            
            if not isinstance(records, list):
                logger.warning(f"Unexpected data format from Unusual Whales API for {symbol}: {type(records)}")
                return []
                
            for i, record in enumerate(records):
                formatted_record = {
                    "id": i + 1,
                    "symbol": symbol,
                    "type": "block",
                    "direction": "call" if record.get("direction", "").lower() == "buy" else "put",
                    "premium": record.get("size", 0) * record.get("price", 0),
                    "strike": record.get("price", 0),
                    "expiry": None,
                    "timestamp": record.get("executed_at", datetime.now().isoformat()),
                    "sentiment": "bullish" if record.get("direction", "").lower() == "buy" else "bearish",
                    "flow_score": 80,
                    "unusual_score": 85
                }
                formatted_data.append(formatted_record)
                
            logger.info(f"Successfully retrieved {len(formatted_data)} dark pool records for {symbol}")
            return formatted_data
        except Exception as e:
            logger.error(f"Error in Unusual Whales API get_dark_pool_symbol for {symbol}: {str(e)}")
            return []

# Initialize the APIs
unusual_whales_api = None
if UNUSUAL_WHALES_API_KEY:
    try:
        unusual_whales_api = UnusualWhalesAPI(UNUSUAL_WHALES_API_KEY)
        logger.info("Successfully initialized Unusual Whales API client")
    except Exception as e:
        logger.error(f"Failed to initialize Unusual Whales API client: {str(e)}")

# Try importing the blueprint from market_analysis_routes
try:
    # Import the blueprint from market_analysis_routes
    from api.market_analysis_routes import bp as market_analysis_bp
    
    # Share the API clients with the blueprint
    # We need to modify the blueprint to access our API instances
    import api.market_analysis_routes as market_routes
    market_routes.unusual_whales_api = unusual_whales_api
    
    # Register the blueprint with the Flask app
    app.register_blueprint(market_analysis_bp)
    logger.info("Successfully registered market analysis blueprint")
except Exception as e:
    logger.error(f"Failed to register market analysis blueprint: {str(e)}")

# Import and register CEO dashboard routes
try:
    # Make sure current directory is in the path
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Now try to import
    from api.routes.ceo_dashboard_routes import ceo_dashboard_bp
    app.register_blueprint(ceo_dashboard_bp)
    logger.info("Successfully registered CEO dashboard routes in minimal server")
except Exception as e:
    logger.error(f"Error registering CEO dashboard routes in minimal server: {e}")

# Import and register TradingView routes
try:
    # First try importing directly
    try:
        print("Importing TradingView routes for minimal server...")
        from api.routes.tradingview_integration import tradingview_bp
        has_tradingview = True
    except ImportError:
        # Try alternative path
        print("Trying alternative path for TradingView routes...")
        from routes.tradingview_integration import tradingview_bp
        has_tradingview = True
    
    # Register the blueprint
    if has_tradingview:
        print("Registering TradingView blueprint in minimal server...")
        app.register_blueprint(tradingview_bp)
        print("✅ Successfully registered TradingView blueprint in minimal server")
        
        # Add a direct test route to verify registration
        @app.route('/api/tradingview-minimal-test', methods=['GET'])
        def tradingview_minimal_test():
            print("TradingView minimal test route called")
            return jsonify({
                'success': True,
                'message': 'TradingView minimal test route is working',
                'timestamp': datetime.now().isoformat()
            })
except Exception as e:
    print(f"❌ Error registering TradingView routes in minimal server: {e}")
    import traceback
    traceback.print_exc()
    logger.error(f"Failed to register TradingView routes: {str(e)}")

@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint to verify the server is running"""
    app_env = os.environ.get('APP_ENV', 'development')
    return jsonify({
        'success': True,
        'message': 'Enhanced Flask server is running',
        'timestamp': datetime.now().isoformat(),
        'version': 'enhanced-1.0',
        'environment': app_env,
        'unusual_whales_api': bool(unusual_whales_api),
        'alpaca_api': bool(ALPACA_API_KEY and ALPACA_API_SECRET)
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to provide connection status information"""
    try:
        # Check if required APIs are available
        alpaca_connected = bool(ALPACA_API_KEY and ALPACA_API_SECRET)
        unusual_whales_connected = bool(unusual_whales_api)
        
        # Check if using real data
        using_real_data = USE_REAL_DATA
        
        # Log the status
        logger.info(f"Health check: Alpaca connected: {alpaca_connected}, Unusual Whales connected: {unusual_whales_connected}, Using real data: {using_real_data}")
        
        # Return status information
        return jsonify({
            'status': 'ok',
            'message': 'API is running',
            'timestamp': datetime.now().isoformat(),
            'alpaca_connected': alpaca_connected,
            'unusual_whales_connected': unusual_whales_connected,
            'using_real_data': using_real_data,
            'app_env': os.environ.get('APP_ENV', 'development')
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# NOTE: These routes are commented out as they are now handled by the market_analysis_routes blueprint
# Keeping them here for reference and as a fallback if the blueprint registration fails
"""
@app.route('/api/institutional-flow', methods=['GET'])
def get_institutional_flow():
    # Get institutional flow data including dark pool and options activity.
    # Now handled by the market_analysis_routes blueprint
    pass

@app.route('/api/institutional-flow/get-data', methods=['POST'])
def get_filtered_institutional_flow():
    # Get filtered institutional flow data based on user criteria.
    # Now handled by the market_analysis_routes blueprint
    pass
"""

# Function to generate mock institutional flow data for testing
def generate_mock_institutional_flow_data(limit=20, symbols=None, flow_type=None, direction=None):
    """Generate mock institutional flow data for development/testing"""
    if not symbols:
        symbols = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOG", "META", "AMD", "INTC", "SPY", "QQQ"]
    
    # If symbols is provided as a string, convert to list
    if isinstance(symbols, str):
        symbols = [symbols]
    
    flow_data = []
    
    for i in range(limit):
        # Pick a random symbol or from the provided list
        symbol = random.choice(symbols) if symbols else random.choice(["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"])
        
        # Generate timestamp within last 24 hours
        timestamp = datetime.now() - timedelta(hours=random.randint(0, 24))
        
        # Base price for the symbol
        base_price = {
            "AAPL": 170, "MSFT": 350, "NVDA": 850, "TSLA": 200, "AMZN": 180,
            "GOOG": 170, "META": 480, "AMD": 160, "INTC": 30, "SPY": 500, "QQQ": 430
        }.get(symbol, random.uniform(100, 500))
        
        # Randomize price within +/- 5% of base
        price = round(base_price * random.uniform(0.95, 1.05), 2)
        
        # Generate data based on flow type
        if flow_type == "options" or (flow_type is None and random.random() > 0.5):
            # Generate options flow data
            option_type = "call" if direction == "bullish" or (direction is None and random.random() > 0.5) else "put"
            exp_date = (datetime.now() + timedelta(days=random.randint(7, 180))).strftime("%Y-%m-%d")
            strike = round(price * random.uniform(0.9, 1.1), 1)
            
            flow_item = {
                "id": i + 1,
                "symbol": symbol,
                "type": "options",
                "direction": option_type,
                "size": random.randint(10, 500) * 100,
                "price": round(random.uniform(1, 20), 2),
                "strike": strike,
                "expiration": exp_date,
                "timestamp": timestamp.isoformat(),
                "premium": random.randint(50000, 5000000) / 100,
                "sentiment": "bullish" if option_type == "call" else "bearish",
                "flow_score": random.randint(65, 95),
                "unusual_score": random.randint(70, 98)
            }
        else:
            # Generate dark pool data
            flow_item = {
                "id": i + 1,
                "symbol": symbol,
                "type": "darkpool",
                "direction": "call" if random.random() > 0.5 else "put",
                "premium": price * random.randint(1000, 50000),
                "strike": price,
                "expiry": None,
                "timestamp": timestamp.isoformat(),
                "sentiment": "bullish" if random.random() > 0.5 else "bearish",
                "size": random.randint(1000, 50000),
                "price": price,
                "value": round(price * random.randint(1000, 50000), 2),
                "exchange": random.choice(["NYSE", "NASDAQ", "IEX", "CBOE"]),
                "flow_score": random.randint(65, 95),
                "unusual_score": random.randint(70, 98)
            }
        
        flow_data.append(flow_item)
    
    return flow_data

@app.route('/api/get-saved-signals', methods=['GET'])
def get_saved_signals():
    """Get saved buy and short signals"""
    try:
        # Check both the current directory and data directory
        data_dir = os.path.join(os.getcwd(), 'data')
        buy_file = os.path.join(data_dir, 'buy_signals.csv')
        short_file = os.path.join(data_dir, 'short_signals.csv')
        
        print(f"Looking for signal files at:")
        print(f" - Buy signals: {buy_file}")
        print(f" - Short signals: {short_file}")
        
        if os.path.exists(buy_file) and os.path.exists(short_file):
            print(f"Signal files found! Reading data...")
            
            # Check file sizes to ensure they're not empty
            buy_size = os.path.getsize(buy_file)
            short_size = os.path.getsize(short_file)
            print(f"File sizes - Buy: {buy_size} bytes, Short: {short_size} bytes")
            
            if buy_size == 0 or short_size == 0:
                print("Warning: One or both signal files are empty!")
                return jsonify({
                    'success': False,
                    'error': 'Signal files exist but are empty',
                    'buy_signals': [],
                    'short_signals': []
                })
                
            try:
                buy_signals = pd.read_csv(buy_file)
                short_signals = pd.read_csv(short_file)
                
                # Verify we have valid dataframes
                print(f"Read {len(buy_signals)} buy signals and {len(short_signals)} short signals")
                
                # Convert to records format for JSON serialization
                buy_records = buy_signals.to_dict('records')
                short_records = short_signals.to_dict('records')
                
                return jsonify({
                    'success': True,
                    'buy_signals': buy_records,
                    'short_signals': short_records
                })
            except pd.errors.EmptyDataError:
                print("Error: CSV files contain no data")
                return jsonify({
                    'success': False,
                    'error': 'CSV files contain no data',
                    'buy_signals': [],
                    'short_signals': []
                })
            except pd.errors.ParserError as e:
                print(f"Error parsing CSV files: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Error parsing CSV files: {str(e)}',
                    'buy_signals': [],
                    'short_signals': []
                })
        else:
            # Return mock data as fallback
            print("Signal files not found, using mock data")
            missing_files = []
            if not os.path.exists(buy_file):
                missing_files.append("buy_signals.csv")
            if not os.path.exists(short_file):
                missing_files.append("short_signals.csv")
                
            print(f"Missing files: {', '.join(missing_files)}")
            
            buy_signals = pd.DataFrame({
                'date': [datetime.now().strftime('%Y-%m-%d')],
                'symbol': ['AAPL'],
                'signal_score': [8.5],
                'close': [180.0],
                'ema_9': [175.0],
                'ema_21': [170.0],
                'volume': [50000000]
            })
            short_signals = pd.DataFrame({
                'date': [datetime.now().strftime('%Y-%m-%d')],
                'symbol': ['TSLA'],
                'signal_score': [-8.2],
                'close': [220.0],
                'ema_9': [225.0],
                'ema_21': [230.0],
                'volume': [60000000]
            })
            
            return jsonify({
                'success': True,
                'buy_signals': buy_signals.to_dict('records'),
                'short_signals': short_signals.to_dict('records'),
                'is_mock': True,
                'message': f"Using mock data. Missing files: {', '.join(missing_files)}"
            })
    except Exception as e:
        logger.error(f"Error in get-saved-signals: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'buy_signals': [],
            'short_signals': []
        }), 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        print("Starting enhanced Flask server...")
        print(f"Server running at: http://localhost:{port}")
        print(f"Test endpoint: http://localhost:{port}/api/test")
        print(f"API connection status: Unusual Whales API:{bool(unusual_whales_api)}, Alpaca API:{bool(ALPACA_API_KEY and ALPACA_API_SECRET)}")
        print("If you're still seeing mock data, check your environment variables in the .env file")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"Error starting Flask server: {str(e)}")
        import traceback
        traceback.print_exc() 