from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import logging
import datetime
from datetime import datetime, timedelta
import random
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dual_bot_api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Sample data for demonstration
SAMPLE_DATA = {
    'symbols': ['QQQ', 'TSLA', 'PLTR', 'AAPL', 'NVDA', 'SPY', 'MSFT'],
    'active_positions': [],
    'trades_executed': 36,
    'success_rate': 0.88,
}

# In-memory storage for demo data
bot_status = {
    'status': True,
    'active_positions': SAMPLE_DATA['active_positions'],
    'last_update': datetime.now().isoformat(),
    'trades_executed': SAMPLE_DATA['trades_executed'],
    'success_rate': SAMPLE_DATA['success_rate'],
    'next_scan': (datetime.now().replace(microsecond=0, second=0) + 
                 timedelta(minutes=5)).isoformat()
}

market_data = {
    symbol: {
        'symbol': symbol,
        'price': random.uniform(100, 1000) if symbol != 'QQQ' else 456.78,
        'timestamp': datetime.now().isoformat()
    } for symbol in SAMPLE_DATA['symbols']
}

config = {
    'symbols': SAMPLE_DATA['symbols'],
    'trading_hours': {
        'start': '09:30',
        'end': '16:00'
    },
    'risk_limits': {
        'max_position_size': 5000,
        'max_daily_loss': 2000
    }
}

# Create and configure the Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With"],
        "supports_credentials": True
    }
})

# API Routes
@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint."""
    logger.info("Health check called")
    return jsonify({'status': 'healthy'})

@app.route('/api/status', methods=['GET', 'OPTIONS'])
def get_status():
    """Get the status of the Dual Bot."""
    logger.info("Status endpoint called")
    # Update the last_update time
    bot_status['last_update'] = datetime.now().isoformat()
    return jsonify(bot_status)

@app.route('/api/market-data/<symbol>', methods=['GET', 'OPTIONS'])
def get_market_data(symbol):
    """Get simplified market data for a symbol."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    logger.info(f"Market data requested for {symbol}")
    
    # Check if symbol exists in our data
    if symbol not in market_data:
        market_data[symbol] = {
            'symbol': symbol,
            'price': random.uniform(100, 1000),
            'timestamp': datetime.now().isoformat()
        }
    else:
        # Slightly change the price to simulate real-time updates
        current_price = market_data[symbol]['price']
        change = random.uniform(-0.02, 0.02) * current_price
        market_data[symbol]['price'] = current_price + change
        market_data[symbol]['timestamp'] = datetime.now().isoformat()
    
    return jsonify(market_data[symbol])

@app.route('/api/options-data/<symbol>', methods=['GET', 'OPTIONS'])
def get_options_data(symbol):
    """Get options data for a symbol."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    logger.info(f"Options data requested for {symbol}")
    
    # Generate mock options data
    base_price = market_data.get(symbol, {'price': 100.0})['price']
    
    options_data = {
        'symbol': symbol,
        'options': [
            {
                'strike': round(base_price * (1 + i * 0.01), 2),
                'callPrice': round(random.uniform(1.0, 5.0), 2),
                'putPrice': round(random.uniform(1.0, 5.0), 2),
                'expirationDate': (datetime.now() + timedelta(days=i*7)).strftime('%Y-%m-%d'),
                'iv': round(random.uniform(0.2, 0.5), 2),
                'volume': random.randint(100, 5000)
            } for i in range(-5, 6)
        ]
    }
    
    return jsonify(options_data)

@app.route('/api/news/<symbol>', methods=['GET', 'OPTIONS'])
def get_news(symbol):
    """Get news for a symbol."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    logger.info(f"News requested for {symbol}")
    
    # Generate mock news data
    news = [
        {
            'title': f"{symbol} Reaches New High on Strong Earnings",
            'source': "Financial Times",
            'url': f"https://example.com/news/{symbol.lower()}/1",
            'sentiment': "positive",
            'relevance': round(random.uniform(0.7, 0.95), 2),
            'published_at': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
        },
        {
            'title': f"Analysts Upgrade {symbol} After Product Announcement",
            'source': "Market News",
            'url': f"https://example.com/news/{symbol.lower()}/2",
            'sentiment': "positive",
            'relevance': round(random.uniform(0.7, 0.95), 2),
            'published_at': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
        }
    ]
    
    return jsonify(news)

@app.route('/api/scan', methods=['POST', 'OPTIONS'])
def scan_trades():
    """Scan for trade recommendations."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        logger.info(f"Scanning for trade recommendations for {symbol}")
        
        # Check if we have market data for this symbol
        if symbol not in market_data:
            # Create it if not
            get_market_data(symbol)
        
        price = market_data[symbol]['price']
        
        # Generate a mock trade recommendation
        is_bullish = random.random() > 0.3  # 70% chance of bullish recommendation
        
        recommendation = {
            'symbol': symbol,
            'trade_type': 'BUY_CALL' if is_bullish else 'BUY_PUT',
            'strike': round(price * (1.01 if is_bullish else 0.99), 2),
            'expiration': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'entry_price': round(random.uniform(2.0, 4.0), 2),
            'target_price': round(random.uniform(4.0, 8.0), 2),
            'stop_loss': round(random.uniform(1.0, 1.8), 2),
            'confidence': round(random.uniform(0.65, 0.95), 2),
            'rationale': (
                "Strong bullish momentum with increasing volume and positive technicals. "
                "Recent price action shows consolidation above key support, with MACD showing "
                "bullish crossover and RSI indicating room for upward movement."
            ) if is_bullish else (
                "Bearish divergence on technical indicators with weakening price momentum. "
                "Recent resistance levels holding firm with decreasing volume on rallies. "
                "Options flow shows increasing put activity and sentiment turning negative."
            )
        }
        
        logger.info(f"Generated recommendation for {symbol}: {recommendation['trade_type']}")
        return jsonify(recommendation)
    except Exception as e:
        logger.error(f"Error scanning trades: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assess-risk', methods=['POST', 'OPTIONS'])
def assess_risk():
    """Assess risk for a trade recommendation."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        data = request.get_json()
        recommendation = data.get('recommendation')
        market_context = data.get('market_context')
        
        if not recommendation or not market_context:
            return jsonify({'error': 'Recommendation and market context are required'}), 400
        
        logger.info(f"Assessing risk for {recommendation.get('symbol')} recommendation")
        
        # Generate a mock risk assessment
        confidence = recommendation.get('confidence', 0.75)
        approved = random.random() < confidence  # Higher confidence trades more likely to be approved
        
        # Calculate risk level
        risk_level = "HIGH" if random.random() < 0.3 else "MEDIUM" if random.random() < 0.6 else "LOW"
        
        # Generate risk score (1-10 scale)
        risk_score = round(random.uniform(3.0, 9.0), 1)
        
        # Enhanced risk assessment with more details
        assessment = {
            'approved': approved,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'confidence': confidence,
            'market_conditions': 'Favorable' if approved else 'Uncertain',
            'market_indicators': random.choice([
                'bullish momentum',
                'high volume',
                'consolidation pattern',
                'bearish divergence',
                'low volatility'
            ]),
            'concerns': None if approved else 'Elevated volatility and weakening technical indicators suggest caution',
            'summary': (
                "This trade has a positive risk/reward ratio with well-defined exit points. "
                "The technicals align with the trade direction and current market sentiment is supportive."
            ) if approved else (
                "While the trade setup has merit, current market conditions suggest increased risk. "
                "Consider reducing position size or waiting for confirmation before entering this trade."
            ),
            'risk_factors': {
                'volatility': random.choice(['Low', 'Moderate', 'High']),
                'liquidity': random.choice(['Good', 'Average', 'Poor']),
                'news_sentiment': random.choice(['Positive', 'Neutral', 'Negative']),
                'technical_alignment': random.choice(['Strong', 'Mixed', 'Weak'])
            },
            'position_sizing': {
                'recommended_size': f"{random.randint(1, 5)} contracts",
                'max_risk_percent': f"{round(random.uniform(0.5, 2.5), 1)}%"
            },
            'alternative_strategies': [
                "Consider a vertical spread to reduce cost basis" if random.random() > 0.5 else None,
                "Wait for pullback to key support level" if random.random() > 0.5 else None,
                "Use a smaller position size with tighter stop" if random.random() > 0.5 else None
            ]
        }
        
        # Filter out None values from alternative strategies
        assessment['alternative_strategies'] = [s for s in assessment['alternative_strategies'] if s]
        
        logger.info(f"Risk assessment for {recommendation.get('symbol')}: {'APPROVED' if approved else 'REJECTED'}")
        return jsonify(assessment)
    except Exception as e:
        logger.error(f"Error assessing risk: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-position', methods=['POST', 'OPTIONS'])
def check_position():
    """Check if a position should be closed."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        data = request.get_json()
        position = data.get('position')
        market_data_input = data.get('market_data')
        
        if not position or not market_data_input:
            return jsonify({'error': 'Position and market data are required'}), 400
        
        logger.info(f"Checking position for {position.get('symbol')}")
        
        # Randomly decide if position should be closed
        should_close = random.random() > 0.7  # 30% chance of recommending closure
        
        return jsonify({
            'should_close': should_close,
            'reason': 'Target price reached' if should_close else 'Position still valid'
        })
    except Exception as e:
        logger.error(f"Error checking position: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET', 'OPTIONS'])
def get_config():
    """Get the current configuration."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    logger.info("Config requested")
    return jsonify(config)

# Test route for CORS
@app.route('/api/cors-test', methods=['GET', 'OPTIONS'])
def cors_test():
    """Test route to verify CORS is working."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    logger.info("CORS test endpoint called")
    return jsonify({
        'success': True,
        'message': 'CORS is working properly',
        'headers_received': dict(request.headers),
        'request_method': request.method,
        'timestamp': datetime.now().isoformat()
    })

# Test route for debugging frontend CORS issues
@app.route('/api/test-frontend-cors', methods=['GET', 'OPTIONS'])
def test_frontend_cors():
    """Special test route that returns details about the request for debugging CORS issues."""
    if request.method == 'OPTIONS':
        logger.info("OPTIONS request to /test-frontend-cors")
        return _build_cors_preflight_response()
        
    logger.info("Frontend CORS test endpoint called")
    return jsonify({
        'success': True,
        'message': 'CORS is working properly from your frontend application',
        'request': {
            'headers': dict(request.headers),
            'method': request.method,
            'origin': request.headers.get('Origin'),
            'host': request.headers.get('Host')
        },
        'response': {
            'cors_headers': {
                'Access-Control-Allow-Origin': 'http://localhost:3000',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,Accept,X-Requested-With',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS,PUT,DELETE',
                'Access-Control-Allow-Credentials': 'true'
            }
        },
        'timestamp': datetime.now().isoformat()
    })

# Handle OPTIONS for all routes
@app.route('/<path:path>', methods=['OPTIONS'])
@app.route('/', methods=['OPTIONS'])
def handle_options(path=None):
    """Handle preflight requests for all routes."""
    logger.info(f"Handling OPTIONS request for {'/' + path if path else '/'}")
    return _build_cors_preflight_response()

# Helper function for OPTIONS requests
def _build_cors_preflight_response():
    response = make_response()
    
    # Use the Origin header from the request if it's from an allowed origin
    origin = request.headers.get('Origin')
    if origin and origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
        response.headers.add("Access-Control-Allow-Origin", origin)
    else:
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        
    response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,Accept,X-Requested-With")
    response.headers.add('Access-Control-Allow-Methods', "GET,POST,OPTIONS,PUT,DELETE")
    response.headers.add('Access-Control-Max-Age', "3600")  # Cache preflight response for 1 hour
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses."""
    origin = request.headers.get('Origin')
    
    # If there's an Origin header, use it instead of the wildcard
    if origin and origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
        response.headers.add('Access-Control-Allow-Origin', origin)
    elif not response.headers.get('Access-Control-Allow-Origin'):
        response.headers.add('Access-Control-Allow-Origin', "http://localhost:3000")
        
    if not response.headers.get('Access-Control-Allow-Headers'):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,X-Requested-With')
    if not response.headers.get('Access-Control-Allow-Methods'):
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS,PUT,DELETE')
    if not response.headers.get('Access-Control-Allow-Credentials'):
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Add dual-bot endpoints for compatibility with the frontend
@app.route('/api/dual-bot/signals', methods=['GET', 'OPTIONS'])
def get_dual_bot_signals():
    """Get signals from the dual bot system."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    logger.info("Dual bot signals requested")
    
    # Generate mock signals data for demonstration
    signals = {
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'signals': [
            {
                'symbol': 'QQQ',
                'type': 'BUY',
                'price': 456.78,
                'date': datetime.now().isoformat(),
                'confidence': 0.85,
                'signal_score': 8.2,
                'close': 456.78,
                'ema_9': 452.34,
                'ema_21': 448.92,
                'volume': 34562198,
                'price_target': 470.25,
                'stop_loss': 448.50
            },
            {
                'symbol': 'TSLA',
                'type': 'BUY',
                'price': 187.35,
                'date': datetime.now().isoformat(),
                'confidence': 0.76,
                'signal_score': 7.4,
                'close': 187.35,
                'ema_9': 182.45,
                'ema_21': 178.92,
                'volume': 42156789,
                'price_target': 195.50,
                'stop_loss': 180.25
            }
        ]
    }
    
    return jsonify(signals)

@app.route('/api/dual-bot/status', methods=['GET', 'OPTIONS'])
def get_dual_bot_status():
    """Get the status of the dual bot system."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    logger.info("Dual bot status requested")
    
    # Generate mock status data
    status = {
        'success': True,
        'status': {
            'status': True,
            'active_positions': [],
            'last_updated': datetime.now().isoformat(),
            'components': {
                'signal_generator': True,
                'risk_manager': True,
                'execution_engine': True,
                'market_data_provider': True
            }
        }
    }
    
    return jsonify(status)

# Run the application
if __name__ == '__main__':
    logger.info("Starting Dual Bot API server on port 5001")
    print("Starting Dual Bot API server on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True) 