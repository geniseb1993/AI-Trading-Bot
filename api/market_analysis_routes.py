from flask import jsonify, request, Blueprint
import random
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

# Import market data modules
try:
    from api.lib.market_data import UnusualWhalesAPI
    from api.lib.sec_api_integration import SecApiIntegration
except ImportError:
    # Try importing without api prefix for compatibility
    try:
        from lib.market_data import UnusualWhalesAPI
        from lib.sec_api_integration import SecApiIntegration
    except ImportError:
        UnusualWhalesAPI = None
        SecApiIntegration = None

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

# Initialize SEC API if available
sec_api = None
try:
    api_key = os.environ.get('SEC_API_KEY')
    if api_key and SecApiIntegration:
        sec_api = SecApiIntegration(api_key=api_key)
        logger.info("SEC API initialized for market analysis routes")
    else:
        logger.warning("SEC API not initialized - missing API key or module not available")
except Exception as e:
    logger.error(f"Error initializing SEC API: {str(e)}")

@bp.route('/market-data/<symbol>', methods=['GET'])
def api_get_market_data(symbol):
    """
    Get comprehensive market data for a specific symbol
    
    Args:
        symbol: Stock symbol to get data for
    
    Query parameters:
        timeframe: Timeframe for data (1m, 5m, 15m, 30m, 1h, 1d)
        days: Number of days of data to return
    
    Returns:
        JSON response with market data
    """
    timeframe = request.args.get('timeframe', '1d')
    days = int(request.args.get('days', 30))
    
    logger.info(f"Market data requested for {symbol}, timeframe: {timeframe}, days: {days}")
    
    try:
        # Generate bars data (timestamps and OHLC values)
        bars = generate_market_bars(symbol, timeframe, days)
        
        # Generate market overview data to complement live market view
        market_overview = {
            # Key statistics
            "stats": {
                "52_week_high": round(calculate_52_week_high(bars), 2),
                "52_week_low": round(calculate_52_week_low(bars), 2),
                "avg_volume": calculate_avg_volume(bars),
                "volatility": round(calculate_volatility(bars), 2),
                "performance_ytd": round(random.uniform(-15, 30), 2),
                "performance_1m": round(random.uniform(-8, 8), 2),
                "performance_3m": round(random.uniform(-15, 15), 2),
                "performance_1y": round(random.uniform(-25, 45), 2),
            },
            
            # Technical indicators
            "technical_indicators": {
                "rsi": round(random.uniform(30, 70), 2),
                "macd": {
                    "value": round(random.uniform(-5, 5), 2),
                    "signal": round(random.uniform(-3, 3), 2),
                    "histogram": round(random.uniform(-2, 2), 2)
                },
                "bollinger_bands": {
                    "upper": round(bars[-1]["close"] * (1 + random.uniform(0.01, 0.05)), 2),
                    "middle": round(bars[-1]["close"], 2),
                    "lower": round(bars[-1]["close"] * (1 - random.uniform(0.01, 0.05)), 2)
                },
                "moving_averages": {
                    "sma_20": round(calculate_sma(bars, 20), 2),
                    "sma_50": round(calculate_sma(bars, 50), 2),
                    "sma_200": round(calculate_sma(bars, 200), 2),
                    "ema_12": round(calculate_ema(bars, 12), 2),
                    "ema_26": round(calculate_ema(bars, 26), 2)
                }
            },
            
            # Market sentiment
            "market_sentiment": {
                "analysts_rating": random.choice(["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"]),
                "analyst_count": random.randint(5, 30),
                "price_target": {
                    "low": round(bars[-1]["close"] * (1 - random.uniform(0.05, 0.2)), 2),
                    "average": round(bars[-1]["close"] * (1 + random.uniform(0.05, 0.15)), 2),
                    "high": round(bars[-1]["close"] * (1 + random.uniform(0.1, 0.3)), 2)
                },
                "social_sentiment": round(random.uniform(-100, 100), 2),
                "institutional_ownership": round(random.uniform(0, 100), 2),
                "short_interest": round(random.uniform(0, 30), 2)
            },
            
            # Related sectors performance
            "sector_performance": generate_sector_performance(),
            
            # Upcoming events
            "upcoming_events": generate_upcoming_events(symbol)
        }
        
        return jsonify({
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "days": days,
            "bars": bars,
            "market_overview": market_overview,
            "isRealData": False,
            "source": "mock",
            "message": "Market data retrieved successfully"
        })
        
    except Exception as e:
        logger.error(f"Error generating market data for {symbol}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/market/ai_signals/<symbol>', methods=['GET'])
def api_get_market_ai_signals(symbol):
    """
    Get AI-generated signals for a specific symbol.
    
    Args:
        symbol: Stock symbol to get signals for
        
    Returns:
        JSON response with AI signals data
    """
    try:
        # Generate mock AI signal data for demo purposes
        mock_signals = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "signals": [
                {
                    "type": "bullish",
                    "timeframe": "1d",
                    "confidence": round(random.uniform(0.65, 0.95), 2),
                    "description": f"Bullish signal detected for {symbol} on daily chart",
                    "indicators": [
                        {"name": "RSI", "value": random.randint(30, 40), "threshold": 30, "signal": "oversold"},
                        {"name": "MACD", "value": random.uniform(-1, 0), "threshold": 0, "signal": "crossover soon"},
                        {"name": "Moving Average", "value": f"Price near {random.randint(10, 50)} day MA support"}
                    ]
                },
                {
                    "type": "consolidation",
                    "timeframe": "4h",
                    "confidence": round(random.uniform(0.7, 0.9), 2),
                    "description": f"{symbol} is consolidating in a tight range on 4h chart",
                    "indicators": [
                        {"name": "Bollinger Bands", "value": "Narrowing", "signal": "low volatility"},
                        {"name": "Volume", "value": "Decreasing", "signal": "consolidation phase"}
                    ]
                }
            ],
            "ai_analysis": f"AI analysis indicates {symbol} is showing signs of potential upward movement based on technical pattern recognition and sentiment analysis. Key support at previous resistance level with positive momentum building.",
            "risk_level": random.choice(["low", "medium", "high"]),
            "opportunity_score": round(random.uniform(1, 10), 1)
        }
        
        return jsonify({
            "success": True,
            "data": mock_signals
        })
        
    except Exception as e:
        logger.error(f"Error generating AI signals for {symbol}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

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
    data_source = "mock"
    flow_data = []
    
    if unusual_whales_api and unusual_whales_api.token:
        try:
            # Try to get dark pool data
            dark_pool_data = unusual_whales_api.get_dark_pool_recent()
            if dark_pool_data and len(dark_pool_data) > 0:
                is_real_data = True
                data_source = "Unusual Whales API"
                flow_data.extend(dark_pool_data)
                logger.info(f"Retrieved {len(dark_pool_data)} dark pool entries")
            else:
                logger.warning("No dark pool data received from API")
                
            # Try to get options flow data
            options_data = unusual_whales_api.get_options_flow()
            if options_data and len(options_data) > 0:
                is_real_data = True
                data_source = "Unusual Whales API"
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
        is_real_data = False
        data_source = "mock"
        
    return jsonify({
        'success': True,
        'isRealData': is_real_data,
        'source': data_source,
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
    data_source = "mock"
    flow_data = []
    
    if unusual_whales_api and unusual_whales_api.token:
        try:
            # Get appropriate data based on flow type
            if flow_type.lower() == 'darkpool':
                data_list = unusual_whales_api.get_dark_pool_recent()
                if data_list and len(data_list) > 0:
                    is_real_data = True
                    data_source = "Unusual Whales API"
                    flow_data = data_list
                    logger.info(f"Retrieved {len(data_list)} dark pool entries for filtering")
            elif flow_type.lower() == 'options':
                data_list = unusual_whales_api.get_options_flow()
                if data_list and len(data_list) > 0:
                    is_real_data = True
                    data_source = "Unusual Whales API"
                    flow_data = data_list
                    logger.info(f"Retrieved {len(data_list)} options flow entries for filtering")
            else:
                # If no specific type, try to get both
                dark_pool = unusual_whales_api.get_dark_pool_recent() or []
                options = unusual_whales_api.get_options_flow() or []
                
                if (len(dark_pool) > 0 or len(options) > 0):
                    is_real_data = True
                    data_source = "Unusual Whales API"
                    flow_data = dark_pool + options
                    logger.info(f"Retrieved {len(dark_pool)} dark pool and {len(options)} options entries for filtering")
            
        except Exception as e:
            logger.error(f"Error fetching institutional flow data for filtering: {str(e)}")
    
    # If no data or API not available, use mock data
    if not is_real_data or len(flow_data) == 0:
        logger.info("Using mock institutional flow data for filtering")
        flow_data = generate_mock_institutional_flow_data()
        is_real_data = False
        data_source = "mock"
    
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
        'source': data_source,
        'data': filtered_data,
        'message': 'Filtered institutional flow data retrieved successfully'
    })

@bp.route('/13f-filings', methods=['GET'])
def get_13f_filings():
    """
    Get 13F filings data from SEC.
    
    Query parameters:
        limit: Maximum number of results to return
        offset: Offset for pagination
        cik: CIK number to filter by specific institution
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        JSON response with 13F filings data
    """
    logger.info("Fetching 13F filings data")
    
    # Get query parameters
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    cik = request.args.get('cik')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Check if SEC API is available
    is_real_data = False
    data_source = "mock"
    filings_data = []
    
    if sec_api and sec_api.api_key:
        try:
            # Fetch 13F filings data from SEC API
            filings_data = sec_api.get_13f_filings(
                cik=cik, 
                limit=limit, 
                offset=offset, 
                start_date=start_date, 
                end_date=end_date
            )
            
            if isinstance(filings_data, list) and len(filings_data) > 0:
                is_real_data = True
                data_source = "SEC API"
                logger.info(f"Retrieved {len(filings_data)} 13F filings from SEC API")
            elif isinstance(filings_data, dict) and "error" in filings_data:
                logger.error(f"Error from SEC API: {filings_data['error']}")
        except Exception as e:
            logger.error(f"Error fetching 13F filings data: {str(e)}")
    
    # If no data or API not available, use mock data
    if not is_real_data or len(filings_data) == 0:
        logger.info("Using mock 13F filings data")
        filings_data = generate_mock_13f_filings(limit=limit)
        is_real_data = False
        data_source = "mock"
        
    return jsonify({
        'success': True,
        'isRealData': is_real_data,
        'source': data_source,
        'data': filings_data,
        'message': '13F filings data retrieved successfully'
    })

@bp.route('/insider-trading', methods=['GET'])
def get_insider_trading():
    """
    Get insider trading data from SEC.
    
    Query parameters:
        symbol: Stock symbol to filter by
        limit: Maximum number of results to return
        offset: Offset for pagination
        cik: CIK number to filter by specific insider
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        JSON response with insider trading data
    """
    logger.info("Fetching insider trading data")
    
    # Get query parameters
    symbol = request.args.get('symbol')
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    cik = request.args.get('cik')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Check if SEC API is available
    is_real_data = False
    data_source = "mock"
    insider_data = []
    
    if sec_api and sec_api.api_key:
        try:
            # Fetch insider trading data from SEC API
            insider_data = sec_api.get_insider_trading(
                symbol=symbol,
                cik=cik, 
                limit=limit, 
                offset=offset, 
                start_date=start_date, 
                end_date=end_date
            )
            
            if isinstance(insider_data, list) and len(insider_data) > 0:
                is_real_data = True
                data_source = "SEC API"
                logger.info(f"Retrieved {len(insider_data)} insider trading records from SEC API")
            elif isinstance(insider_data, dict) and "error" in insider_data:
                logger.error(f"Error from SEC API: {insider_data['error']}")
        except Exception as e:
            logger.error(f"Error fetching insider trading data: {str(e)}")
    
    # If no data or API not available, use mock data
    if not is_real_data or len(insider_data) == 0:
        logger.info("Using mock insider trading data")
        insider_data = generate_mock_insider_trading(symbol=symbol, limit=limit)
        is_real_data = False
        data_source = "mock"
        
    return jsonify({
        'success': True,
        'isRealData': is_real_data,
        'source': data_source,
        'data': insider_data,
        'message': 'Insider trading data retrieved successfully'
    })

def register_routes(app):
    """Register routes with the Flask app - added for backward compatibility"""
    app.register_blueprint(bp)
    logger.info("Market analysis routes registered")

# Helper function to generate market data bars
def generate_market_bars(symbol, timeframe, days=30):
    """
    Generate market data bars for a given symbol and timeframe
    
    Args:
        symbol: Stock ticker symbol
        timeframe: Data timeframe (1m, 5m, 15m, 30m, 1h, 1d)
        days: Number of days of data to return
        
    Returns:
        List of bar data with date, open, high, low, close, volume and change
    """
    # Base price and volatility for the symbol
    base_prices = {
        "SPY": 475, "QQQ": 425, "AAPL": 175, "MSFT": 415, "TSLA": 175, 
        "NVDA": 900, "AMD": 155, "AMZN": 175, "GOOGL": 170, "META": 485
    }
    
    base_price = base_prices.get(symbol, random.uniform(50, 500))
    volatility = random.uniform(0.005, 0.02)  # Daily volatility
    
    # Determine number of bars based on timeframe and days
    bars_per_day = {
        "1m": 390,  # 6.5 hours × 60 minutes
        "5m": 78,   # 6.5 hours × 12 periods per hour
        "15m": 26,  # 6.5 hours × 4 periods per hour
        "30m": 13,  # 6.5 hours × 2 periods per hour
        "1h": 7,    # ~7 hours in a trading day
        "1d": 1     # 1 bar per day
    }
    
    periods = min(bars_per_day.get(timeframe, 1) * days, 1000)  # Cap at 1000 bars
    
    # Generate bars
    bars = []
    last_price = base_price
    end_date = datetime.now()
    
    # Set start date based on timeframe
    if timeframe == "1d":
        delta = timedelta(days=1)
    elif timeframe == "1h":
        delta = timedelta(hours=1)
    elif timeframe == "30m":
        delta = timedelta(minutes=30)
    elif timeframe == "15m":
        delta = timedelta(minutes=15)
    elif timeframe == "5m":
        delta = timedelta(minutes=5)
    else:  # 1m
        delta = timedelta(minutes=1)
    
    # Generate bars from newest to oldest
    for i in range(periods):
        date = end_date - (delta * i)
        
        # Skip weekends for daily data
        if timeframe == "1d" and date.weekday() >= 5:
            continue
        
        # More volatility for shorter timeframes
        tf_volatility = volatility
        if timeframe in ["1m", "5m"]:
            tf_volatility = volatility * 0.5
        
        # Random price movement
        change = random.uniform(-tf_volatility, tf_volatility)
        close_price = last_price * (1 + change)
        
        # Generate OHLC
        high_price = close_price * (1 + random.uniform(0, tf_volatility))
        low_price = close_price * (1 - random.uniform(0, tf_volatility))
        open_price = last_price
        
        # Ensure high is the highest and low is the lowest
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        # Random volume - higher on bigger price moves
        volume_base = abs(change) * 1000000 * (random.uniform(0.5, 1.5))
        volume = int(max(volume_base, 10000))
        
        bars.append({
            'date': date.strftime("%Y-%m-%d %H:%M:%S"),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume,
            'change': round(((close_price - open_price) / open_price) * 100, 2)
        })
        
        last_price = close_price
    
    # Reverse to get oldest to newest
    bars.reverse()
    return bars

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

# Helper functions for market data calculations
def calculate_52_week_high(bars):
    """Calculate 52-week high from bar data"""
    if not bars:
        return 0
    return max([bar["high"] for bar in bars])

def calculate_52_week_low(bars):
    """Calculate 52-week low from bar data"""
    if not bars:
        return 0
    return min([bar["low"] for bar in bars])

def calculate_avg_volume(bars):
    """Calculate average volume from bar data"""
    if not bars:
        return 0
    return int(sum([bar["volume"] for bar in bars]) / len(bars))

def calculate_volatility(bars):
    """Calculate volatility (standard deviation) from bar data"""
    if not bars or len(bars) < 2:
        return 0
    
    # Calculate daily returns
    returns = []
    for i in range(1, len(bars)):
        prev_close = bars[i-1]["close"]
        curr_close = bars[i]["close"]
        daily_return = (curr_close - prev_close) / prev_close
        returns.append(daily_return)
    
    # Calculate standard deviation
    mean_return = sum(returns) / len(returns)
    variance = sum([(r - mean_return) ** 2 for r in returns]) / len(returns)
    return (variance ** 0.5) * 100  # Convert to percentage

def calculate_sma(bars, period):
    """Calculate Simple Moving Average for the given period"""
    if not bars or len(bars) < period:
        return bars[-1]["close"] if bars else 0
    
    closes = [bar["close"] for bar in bars[-period:]]
    return sum(closes) / period

def calculate_ema(bars, period):
    """Calculate Exponential Moving Average for the given period"""
    if not bars:
        return 0
    
    # For simplicity, we'll use a smoothing factor based on the period
    alpha = 2 / (period + 1)
    
    # Start with SMA for the first EMA value
    ema = calculate_sma(bars[:period], period)
    
    # Calculate EMA for the rest of the data
    for i in range(period, len(bars)):
        ema = (bars[i]["close"] * alpha) + (ema * (1 - alpha))
    
    return ema

def generate_sector_performance():
    """Generate mock sector performance data"""
    sectors = [
        "Technology", "Healthcare", "Financials", "Consumer Discretionary", 
        "Industrials", "Communication Services", "Consumer Staples", 
        "Energy", "Utilities", "Materials", "Real Estate"
    ]
    
    return [{
        "name": sector,
        "performance_1d": round(random.uniform(-3, 3), 2),
        "performance_1m": round(random.uniform(-10, 10), 2),
        "performance_ytd": round(random.uniform(-20, 30), 2),
    } for sector in sectors]

def generate_upcoming_events(symbol):
    """Generate mock upcoming events for a symbol"""
    # Current date
    now = datetime.now()
    
    # Generate a random future date within the next 3 months
    def random_future_date():
        days_ahead = random.randint(1, 90)
        future_date = now + timedelta(days=days_ahead)
        return future_date.strftime("%Y-%m-%d")
    
    # List of possible event types
    event_types = [
        "Earnings Report", "Dividend Payment", "Ex-Dividend Date",
        "Conference Call", "Investor Day", "Product Launch",
        "Industry Conference", "Analyst Meeting"
    ]
    
    # Generate 0-3 upcoming events
    num_events = random.randint(0, 3)
    return [{
        "date": random_future_date(),
        "type": random.choice(event_types),
        "description": f"{symbol} {random.choice(event_types).lower()} scheduled"
    } for _ in range(num_events)]

def generate_mock_13f_filings(limit=20, cik=None):
    """Generate mock 13F filings data for testing purposes"""
    institutions = [
        {"name": "BlackRock Inc.", "cik": "1364742"},
        {"name": "Vanguard Group Inc.", "cik": "102909"},
        {"name": "State Street Corporation", "cik": "93751"},
        {"name": "Fidelity Management & Research", "cik": "315066"},
        {"name": "JPMorgan Chase & Co.", "cik": "19617"},
        {"name": "Invesco Ltd.", "cik": "914208"},
        {"name": "Capital Research Global Investors", "cik": "1736291"},
        {"name": "Bank of America Corporation", "cik": "70858"},
        {"name": "Goldman Sachs Group Inc.", "cik": "886982"},
        {"name": "Morgan Stanley", "cik": "895421"}
    ]
    
    symbols = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "BRK.B", "UNH", "JPM"]
    
    filings = []
    end_date = datetime.now()
    
    for i in range(limit):
        # Random institution
        institution = random.choice(institutions)
        
        # Random filing date
        filing_date = end_date - timedelta(days=random.randint(1, 90))
        
        # Random holdings for the filing
        holdings = []
        for _ in range(random.randint(5, 20)):
            symbol = random.choice(symbols)
            holdings.append({
                "name": symbol,
                "value": random.randint(1000000, 1000000000),
                "shares": random.randint(10000, 10000000),
                "percentage": round(random.uniform(0.01, 10.0), 2)
            })
        
        # Create filing
        filing = {
            "id": str(i+1),
            "accessionNo": f"0001{random.randint(100000, 999999)}-{random.randint(10, 99)}-{random.randint(100000, 999999)}",
            "symbol": "",  # Not applicable for 13F (it's about the institution, not a specific stock)
            "companyName": institution["name"],
            "cik": institution["cik"],
            "filedAt": filing_date.strftime("%Y-%m-%d"),
            "reportDate": (filing_date - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
            "form": "13F-HR",
            "holdings": holdings,
            "url": f"https://www.sec.gov/Archives/edgar/data/{institution['cik']}/000{random.randint(100000000, 999999999)}/form13f.html",
            "dataSource": "mock"
        }
        
        # Filter by CIK if provided
        if cik is None or institution["cik"] == cik:
            filings.append(filing)
    
    return filings

def generate_mock_insider_trading(symbol=None, limit=20):
    """Generate mock insider trading data for testing purposes"""
    if not symbol:
        symbols = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "BRK.B", "UNH", "JPM"]
    else:
        symbols = [symbol]
    
    # Executive positions
    positions = ["CEO", "CFO", "CTO", "COO", "Director", "VP", "SVP", "President", "Chairman", "Board Member"]
    
    # Transaction types
    transaction_types = [
        {"code": "P", "description": "Open market or private purchase"},
        {"code": "S", "description": "Open market or private sale"},
        {"code": "A", "description": "Grant or award"},
        {"code": "D", "description": "Sale back to issuer"},
        {"code": "F", "description": "Payment of exercise price or tax liability by delivering securities"}
    ]
    
    # Generate insider names
    first_names = ["John", "Jane", "Robert", "Mary", "William", "Patricia", "James", "Jennifer", "Michael", "Linda"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
    
    transactions = []
    end_date = datetime.now()
    
    for i in range(limit):
        # Random symbol if not provided
        stock_symbol = random.choice(symbols)
        
        # Random company name based on symbol
        company_names = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "AMZN": "Amazon.com Inc.",
            "GOOGL": "Alphabet Inc.",
            "META": "Meta Platforms Inc.",
            "TSLA": "Tesla Inc.",
            "NVDA": "NVIDIA Corporation",
            "BRK.B": "Berkshire Hathaway Inc.",
            "UNH": "UnitedHealth Group Inc.",
            "JPM": "JPMorgan Chase & Co."
        }
        company_name = company_names.get(stock_symbol, f"{stock_symbol} Inc.")
        
        # Random insider name
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        insider_name = f"{first_name} {last_name}"
        
        # Random position
        position = random.choice(positions)
        
        # Random transaction details
        transaction_type = random.choice(transaction_types)
        is_buy = transaction_type["code"] in ["P", "A"]
        direction = "buy" if is_buy else "sell"
        
        # Random dates
        filing_date = end_date - timedelta(days=random.randint(1, 30))
        transaction_date = filing_date - timedelta(days=random.randint(1, 5))
        
        # Random price and shares
        base_prices = {
            "AAPL": 170, "MSFT": 350, "AMZN": 180, "GOOGL": 170, 
            "META": 480, "TSLA": 200, "NVDA": 850, "BRK.B": 350,
            "UNH": 500, "JPM": 180
        }
        price = round(base_prices.get(stock_symbol, 100) * random.uniform(0.9, 1.1), 2)
        shares = random.randint(1000, 50000)
        value = round(price * shares, 2)
        
        transaction = {
            "id": str(i+1),
            "symbol": stock_symbol,
            "companyName": company_name,
            "insider_name": insider_name,
            "position": position,
            "transaction_date": transaction_date.strftime("%Y-%m-%d"),
            "filing_date": filing_date.strftime("%Y-%m-%d"),
            "transaction_type": transaction_type["code"],
            "transaction_description": transaction_type["description"],
            "direction": direction,
            "shares": shares,
            "price": price,
            "value": value,
            "url": f"https://www.sec.gov/Archives/edgar/data/000{random.randint(100000, 999999)}/form4.html",
            "dataSource": "mock"
        }
        
        transactions.append(transaction)
    
    return transactions 