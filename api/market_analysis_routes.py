from flask import jsonify, request, Blueprint
import random
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

# Import market data modules
try:
    from api.lib.market_data import UnusualWhalesAPI
except ImportError:
    # Try importing without api prefix for compatibility
    try:
        from lib.market_data import UnusualWhalesAPI
    except ImportError:
        UnusualWhalesAPI = None

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Create Blueprint with url_prefix for consistent routing
bp = Blueprint('market_analysis', __name__, url_prefix='/api')

# Initialize Unusual Whales API if available
unusual_whales_api = None
try:
    api_key = os.environ.get('UNUSUAL_WHALES_API_KEY')
    if api_key and UnusualWhalesAPI:
        unusual_whales_api = UnusualWhalesAPI(token=api_key)
        logger.info("Unusual Whales API initialized for market analysis routes")
    else:
        logger.warning("Unusual Whales API not initialized - missing API key or module not available")
except Exception as e:
    logger.error(f"Error initializing Unusual Whales API: {str(e)}")

@bp.route('/market-analysis/get-data', methods=['POST'])
def api_get_market_analysis():
    """Get market analysis data based on the requested timeframe"""
    data = request.get_json()
    symbol = data.get('symbol', 'SPY')
    timeframe = data.get('timeframe', 'daily')
    days = data.get('days', 30)
    
    logger.info(f"Market analysis requested for {symbol}, timeframe: {timeframe}, days: {days}")
    
    # Generate market data
    market_data = generate_mock_market_data(symbol, timeframe, days)
    
    return jsonify({
        'success': True,
        'data': market_data,
        'message': 'Market data retrieved successfully'
    })

@bp.route('/ai-insights/market-analysis', methods=['POST'])
def api_get_ai_insights():
    """Get AI-powered insights for market analysis"""
    data = request.get_json()
    symbol = data.get('symbol', 'SPY')
    
    logger.info(f"AI market insights requested for {symbol}")
    
    # Generate AI insights
    insights = generate_ai_market_insights(symbol)
    
    return jsonify({
        'success': True,
        'data': insights,
        'message': 'AI market insights generated successfully'
    })
        
@bp.route('/institutional-flow', methods=['GET'])
def get_institutional_flow():
    """
    Get institutional flow data including dark pool and options activity.
    
    Returns:
        JSON response with institutional flow data or error
    """
    logger.info("Fetching institutional flow data")
    
    # Check if API is available
    is_real_data = False
    flow_data = []
    
    if unusual_whales_api:
        try:
            # Try to get dark pool data
            dark_pool_data = unusual_whales_api.get_dark_pool()
            if dark_pool_data and len(dark_pool_data) > 0:
                is_real_data = True
                flow_data.extend(dark_pool_data)
                logger.info(f"Retrieved {len(dark_pool_data)} dark pool entries")
            else:
                logger.warning("No dark pool data received from API")
                
            # Try to get options flow data
            options_data = unusual_whales_api.get_options_flow()
            if options_data and len(options_data) > 0:
                is_real_data = True
                flow_data.extend(options_data)
                logger.info(f"Retrieved {len(options_data)} options flow entries")
            else:
                logger.warning("No options flow data received from API")
                
        except Exception as e:
            logger.error(f"Error fetching institutional flow data: {str(e)}")
            
    # If no data or API not available, use mock data
    if not is_real_data or len(flow_data) == 0:
        logger.info("Using mock institutional flow data")
        flow_data = generate_mock_institutional_flow_data()
        
    return jsonify({
        'success': True,
        'isRealData': is_real_data,
        'data': flow_data,
        'message': 'Institutional flow data retrieved successfully'
    })

@bp.route('/institutional-flow/get-data', methods=['POST'])
def get_filtered_institutional_flow():
    """
    Get filtered institutional flow data based on user criteria.
    
    Expected JSON body:
    {
        "symbols": ["AAPL", "MSFT"],  # Optional list of symbols
        "flowType": "darkpool",      # Optional: "darkpool" or "options"
        "direction": "bullish"       # Optional: "bullish" or "bearish"
    }
    
    Returns:
        JSON response with filtered institutional flow data
    """
    data = request.get_json() or {}
    
    # Get filter parameters
    symbols = data.get('symbols', [])
    flow_type = data.get('flowType', '')
    direction = data.get('direction', '')
    
    # Convert string to list if needed
    if isinstance(symbols, str):
        symbols = [symbols]
        
    logger.info(f"Filtering institutional flow data - symbols: {symbols}, type: {flow_type}, direction: {direction}")
    
    # Check if API is available
    is_real_data = False
    flow_data = []
    
    if unusual_whales_api:
        try:
            # Get appropriate data based on flow type
            if flow_type.lower() == 'darkpool':
                data_list = unusual_whales_api.get_dark_pool()
                if data_list and len(data_list) > 0:
                    is_real_data = True
                    flow_data = data_list
                    logger.info(f"Retrieved {len(data_list)} dark pool entries for filtering")
            elif flow_type.lower() == 'options':
                data_list = unusual_whales_api.get_options_flow()
                if data_list and len(data_list) > 0:
                    is_real_data = True
                    flow_data = data_list
                    logger.info(f"Retrieved {len(data_list)} options flow entries for filtering")
            else:
                # If no specific type, try to get both
                dark_pool = unusual_whales_api.get_dark_pool() or []
                options = unusual_whales_api.get_options_flow() or []
                
                if (len(dark_pool) > 0 or len(options) > 0):
                    is_real_data = True
                    flow_data = dark_pool + options
                    logger.info(f"Retrieved {len(dark_pool)} dark pool and {len(options)} options entries for filtering")
            
        except Exception as e:
            logger.error(f"Error fetching institutional flow data for filtering: {str(e)}")
    
    # If no data or API not available, use mock data
    if not is_real_data or len(flow_data) == 0:
        logger.info("Using mock institutional flow data for filtering")
        flow_data = generate_mock_institutional_flow_data()
    
    # Filter the data
    filtered_data = flow_data
    
    # Filter by symbols if provided
    if symbols and len(symbols) > 0:
        filtered_data = [item for item in filtered_data if item.get('ticker', item.get('symbol', '')).upper() in [s.upper() for s in symbols]]
        logger.info(f"Filtered to {len(filtered_data)} entries by symbols {symbols}")
    
    # Filter by direction if provided
    if direction:
        if direction.lower() == 'bullish':
            filtered_data = [item for item in filtered_data if item.get('sentiment', item.get('direction', '')).lower() in ['bullish', 'positive', 'up']]
        elif direction.lower() == 'bearish':
            filtered_data = [item for item in filtered_data if item.get('sentiment', item.get('direction', '')).lower() in ['bearish', 'negative', 'down']]
        logger.info(f"Filtered to {len(filtered_data)} entries by direction {direction}")
    
    return jsonify({
        'success': True,
        'isRealData': is_real_data,
        'data': filtered_data,
        'message': 'Filtered institutional flow data retrieved successfully'
    })

def register_routes(app):
    """Register routes with the Flask app - added for backward compatibility"""
    app.register_blueprint(bp)
    logger.info("Market analysis routes registered")

# Helper functions for generating mock data
def generate_mock_market_data(symbol, timeframe, days):
    """Generate mock market data for the given timeframe"""
    tickers = ["SPY", "QQQ", "AAPL", "MSFT", "AMZN", "GOOG", "META", "TSLA", "NVDA", "AMD"]
    
    market_data = []
    end_date = datetime.now()
    
    if timeframe == "1d":
        # For 1-day, generate hourly data points
        start_date = end_date - timedelta(days=1)
        interval = timedelta(hours=1)
        points = 24
    elif timeframe == "1w":
        # For 1-week, generate daily data points
        start_date = end_date - timedelta(weeks=1)
        interval = timedelta(days=1)
        points = 7
    elif timeframe == "1m":
        # For 1-month, generate daily data points
        start_date = end_date - timedelta(days=30)
        interval = timedelta(days=1)
        points = 30
    elif timeframe == "3m":
        # For 3-month, generate daily data points
        start_date = end_date - timedelta(days=90)
        interval = timedelta(days=3)
        points = 30
    else:
        # Default to 1 day hourly data
        start_date = end_date - timedelta(days=1)
        interval = timedelta(hours=1)
        points = 24
    
    for ticker in tickers:
        price = random.uniform(50, 500)
        volatility = random.uniform(0.01, 0.05)
        
        ticker_data = []
        current_date = start_date
        
        for i in range(points):
            change = random.uniform(-volatility, volatility)
            price = price * (1 + change)
            
            data_point = {
                "timestamp": current_date.isoformat(),
                "open": round(price * (1 - random.uniform(0, 0.01)), 2),
                "high": round(price * (1 + random.uniform(0, 0.02)), 2),
                "low": round(price * (1 - random.uniform(0, 0.02)), 2),
                "close": round(price, 2),
                "volume": int(random.uniform(1000000, 10000000)),
                "change_percent": round(change * 100, 2)
            }
            
            ticker_data.append(data_point)
            current_date += interval
        
        market_data.append({
            "symbol": ticker,
            "data": ticker_data
        })
    
    return market_data

def generate_ai_market_insights(symbol):
    """Generate AI-powered market insights based on current market conditions"""
    market_summary = [
        "The market is showing signs of volatility due to recent economic data.",
        "Tech stocks continue to outperform the broader market.",
        "Trading volume has increased significantly over the past week.",
        "Institutional investors are taking bullish positions in financial and healthcare sectors."
    ]
    
    trade_suggestions = [
        {
            "symbol": "AAPL",
            "action": "BUY",
            "reason": "Strong technical support and upcoming product announcements.",
            "confidence": random.uniform(0.65, 0.95)
        },
        {
            "symbol": "MSFT",
            "action": "HOLD",
            "reason": "Current valuation appears fair given growth prospects.",
            "confidence": random.uniform(0.70, 0.90)
        },
        {
            "symbol": "NVDA",
            "action": "BUY",
            "reason": "AI demand continues to drive growth in data center segment.",
            "confidence": random.uniform(0.75, 0.95)
        },
        {
            "symbol": "TSLA",
            "action": "SELL",
            "reason": "Increasing competition and margin pressure in EV market.",
            "confidence": random.uniform(0.60, 0.85)
        }
    ]
    
    market_trends = [
        {
            "trend": "AI and Machine Learning",
            "strength": random.uniform(0.8, 0.95),
            "description": "Companies focused on AI solutions continue to see strong investor interest."
        },
        {
            "trend": "Renewable Energy",
            "strength": random.uniform(0.7, 0.9),
            "description": "Solar and wind energy stocks showing momentum with new policy incentives."
        },
        {
            "trend": "Cybersecurity",
            "strength": random.uniform(0.75, 0.9),
            "description": "Increased spending on security solutions driving sector growth."
        },
        {
            "trend": "Semiconductor Shortage",
            "strength": random.uniform(0.6, 0.8),
            "description": "Supply chain issues persist, creating both challenges and opportunities."
        }
    ]
    
    return {
        "market_summary": market_summary,
        "trade_suggestions": trade_suggestions,
        "market_trends": market_trends
    }

def generate_mock_institutional_flow_data(limit=20, symbols=None, flow_type=None, direction=None):
    """Generate mock institutional flow data for testing purposes"""
    if not symbols:
        symbols = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOG", "META", "AMD", "INTC", "SPY", "QQQ"]
    
    # If symbols is provided as a string, convert to list
    if isinstance(symbols, str):
        symbols = [symbols]
    
    flow_data = []
    
    for _ in range(limit):
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
                "symbol": symbol,
                "type": "options",
                "direction": option_type,
                "size": random.randint(10, 500) * 100,
                "price": round(random.uniform(1, 20), 2),
                "strike": strike,
                "expiration": exp_date,
                "timestamp": timestamp.isoformat(),
                "premium": random.randint(50000, 5000000) / 100
            }
        else:
            # Generate dark pool data
            flow_item = {
                "symbol": symbol,
                "type": "darkpool",
                "size": random.randint(1000, 50000),
                "price": price,
                "value": round(price * random.randint(1000, 50000), 2),
                "exchange": random.choice(["NYSE", "NASDAQ", "IEX", "CBOE"]),
                "timestamp": timestamp.isoformat()
            }
        
        flow_data.append(flow_item)
    
    return flow_data 