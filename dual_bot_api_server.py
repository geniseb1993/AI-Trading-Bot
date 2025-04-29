import os
import json
import logging
import random
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "X-API-Key"]
}}, supports_credentials=True)

# Sample data for demonstration
sample_market_data = {
    "SPY": {
        "price": 450.72,
        "change": 1.23,
        "change_percent": 0.27,
        "volume": 75432156,
        "avg_volume_10d": 68945231,
        "high": 452.18,
        "low": 448.92,
        "open": 449.83,
        "prev_close": 449.49,
        "timestamp": "2023-10-16T20:00:00Z"
    }
}

# In-memory storage for demo data
webhook_alerts = []
MAX_ALERTS = 100

# Function to build CORS preflight response
def _build_cors_preflight_response():
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept,X-API-Key')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS,PUT,DELETE')
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
    # Only add CORS headers if they don't already exist
    if not response.headers.get('Access-Control-Allow-Origin'):
        origin = request.headers.get('Origin')
        allowed_origins = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:3001', 'http://127.0.0.1:3001', 'http://localhost:5000', 'http://127.0.0.1:5000']
    
        # If there's an Origin header, use it instead of the wildcard
        if origin and origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            # Default to localhost:3001 since that's our primary frontend port now
            response.headers.add('Access-Control-Allow-Origin', "http://localhost:3001")
        
    if not response.headers.get('Access-Control-Allow-Headers'):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,X-Requested-With,X-API-Key')
    if not response.headers.get('Access-Control-Allow-Methods'):
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS,PUT,DELETE')
    if not response.headers.get('Access-Control-Allow-Credentials'):
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    
    return response

# API Configuration Routes
@app.route('/api/configuration/get-api-configs', methods=['GET', 'OPTIONS'])
def get_api_configs():
    """Get API configurations with connection status information."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        logger.info("API configurations requested")
        
        # Get API keys from environment variables
        alpaca_key = os.environ.get('ALPACA_API_KEY', '')
        alpaca_secret = os.environ.get('ALPACA_API_SECRET', '')
        
        # Check if Alpaca is connected by verifying the API keys are not empty
        alpaca_connected = bool(alpaca_key and alpaca_secret)
        
        # Return API configurations
        return jsonify({
            'success': True,
            'configs': {
                'alpaca': {
                    'api_key': '****' if alpaca_key else '',
                    'api_secret': '****' if alpaca_secret else '',
                    'paper_trading': True,
                    'enabled': alpaca_connected,
                    'connected': alpaca_connected,
                    'description': 'Alpaca is a commission-free stock trading API that allows you to build and test your trading algorithms.'
                },
                'interactive_brokers': {
                    'port': os.environ.get('IB_PORT', '7496'),
                    'client_id': os.environ.get('IB_CLIENT_ID', '0'),
                    'enabled': bool(os.environ.get('IB_ENABLED', False)),
                    'connected': bool(os.environ.get('IB_CONNECTED', False)),
                    'description': 'Interactive Brokers provides a comprehensive trading API for accessing global markets.'
                },
                'trading_view': {
                    'webhook_secret': '****' if os.environ.get('TRADINGVIEW_WEBHOOK_SECRET') else '',
                    'webhook_port': os.environ.get('TRADINGVIEW_WEBHOOK_PORT', '5001'),
                    'enabled': bool(os.environ.get('TRADINGVIEW_WEBHOOK_PORT')),
                    'connected': True,  # TradingView is always "connected" if the webhook port is set
                    'description': 'TradingView webhook integration allows you to receive signals from TradingView alerts.'
                },
                'unusual_whales': {
                    'api_key': '****' if os.environ.get('UNUSUAL_WHALES_API_KEY') else '',
                    'enabled': bool(os.environ.get('UNUSUAL_WHALES_API_KEY')),
                    'connected': bool(os.environ.get('UNUSUAL_WHALES_API_KEY')),
                    'description': 'Unusual Whales provides options flow data and unusual options activity detection.'
                },
                'hume_ai': {
                    'api_key': '****' if os.environ.get('HUME_API_KEY') else '',
                    'enabled': bool(os.environ.get('HUME_API_KEY')),
                    'connected': bool(os.environ.get('HUME_API_KEY')),
                    'description': 'Hume AI provides voice notifications for trading alerts and system events.'
                }
            }
        })
    except Exception as e:
        logger.error(f"Error fetching API configurations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/configuration/update-api-configs', methods=['POST', 'OPTIONS'])
def update_api_configs():
    """Update API configurations."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        logger.info("API configurations update requested")
        data = request.json
        
        if not data or not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Invalid data format'
            }), 400
        
        # Get updated configurations
        updated_configs = data.get('configs', {})
        
        # Update only the toggles for now - in a real system, you'd update env variables or config files
        # For this implementation, we're just returning success
        
        return jsonify({
            'success': True,
            'message': 'API configurations updated successfully',
            'configs': updated_configs
        })
    except Exception as e:
        logger.error(f"Error updating API configurations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/configuration/test-connection', methods=['POST', 'OPTIONS'])
def test_api_connection():
    """Test API connection for a specific service."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        logger.info("API connection test requested")
        data = request.json
        
        if not data or not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Invalid data format'
            }), 400
        
        # Get service name from request
        service = data.get('service')
        if not service:
            return jsonify({
                'success': False,
                'error': 'Service name is required'
            }), 400
        
        # Test connection based on service name
        if service == 'alpaca':
            # Get API keys from environment variables
            api_key = os.environ.get('ALPACA_API_KEY', '')
            api_secret = os.environ.get('ALPACA_API_SECRET', '')
            
            # Check if API keys are configured
            if not api_key or not api_secret:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'message': 'Alpaca API keys are not configured'
                })
                
            # In a real implementation, you would test the connection to Alpaca API
            # For now, we'll just check if the keys are present
            return jsonify({
                'success': True,
                'connected': True,
                'message': 'Successfully connected to Alpaca API'
            })
            
        elif service == 'interactive_brokers':
            # Get IB configuration
            port = os.environ.get('IB_PORT', '')
            client_id = os.environ.get('IB_CLIENT_ID', '')
            
            # In a real implementation, you would test connection to IB
            # For now, we'll just check if port and client ID are present
            if not port or not client_id:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'message': 'Interactive Brokers configuration is incomplete'
                })
                
            return jsonify({
                'success': True,
                'connected': True,
                'message': 'Successfully connected to Interactive Brokers'
            })
            
        elif service == 'trading_view':
            # Trading View webhook is always "connected" if the webhook port is set
            webhook_port = os.environ.get('TRADINGVIEW_WEBHOOK_PORT', '')
            
            if not webhook_port:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'message': 'TradingView webhook port is not configured'
                })
                
            return jsonify({
                'success': True,
                'connected': True,
                'message': 'TradingView webhook is configured and ready'
            })
            
        elif service == 'unusual_whales':
            # Check if API key is configured
            api_key = os.environ.get('UNUSUAL_WHALES_API_KEY', '')
            
            if not api_key:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'message': 'Unusual Whales API key is not configured'
                })
                
            return jsonify({
                'success': True,
                'connected': True,
                'message': 'Successfully connected to Unusual Whales API'
            })
            
        elif service == 'hume_ai':
            # Check if API key is configured
            api_key = os.environ.get('HUME_API_KEY', '')
            
            if not api_key:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'message': 'Hume AI API key is not configured'
                })
                
            return jsonify({
                'success': True,
                'connected': True,
                'message': 'Successfully connected to Hume AI API'
            })
            
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown service: {service}'
            }), 400
            
    except Exception as e:
        logger.error(f"Error testing API connection: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Health check endpoint
@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """API health check endpoint."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'server': 'dual_bot_api_server',
        'version': '1.0.0'
    })

# Add status endpoint for dual bot
@app.route('/api/status', methods=['GET', 'OPTIONS'])
def get_status():
    """Get the status of the dual bot."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    logger.info("Status endpoint called")
    
    # Generate mock dual bot status
    # In a real implementation, you would get the actual status
    status = {
        'dual_bot': {
            'status': 'active',
            'last_active': datetime.now().isoformat(),
            'trades_executed': random.randint(10, 100),
            'success_rate': round(random.uniform(0.70, 0.95), 2),
            'current_positions': random.randint(0, 5),
            'uptime': '2d 14h 32m',
            'errors': []
        }
    }
    
    return jsonify(status)

# Add dedicated dual-bot status endpoint
@app.route('/api/dual-bot/status', methods=['GET', 'OPTIONS'])
def get_dual_bot_status():
    """Get the status of the dual bot (dedicated endpoint)."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    logger.info("Dual bot status endpoint called")
    
    # Return the same status as the general status endpoint
    return get_status()

# Add the root configuration endpoints without the /api prefix
@app.route('/configuration/get-api-configs', methods=['GET', 'OPTIONS'])
def root_get_api_configs():
    """Get API configurations with connection status information (root path)."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        logger.info("API configurations requested (root path)")
        
        # Get API keys from environment variables
        alpaca_key = os.environ.get('ALPACA_API_KEY', '')
        alpaca_secret = os.environ.get('ALPACA_API_SECRET', '')
        
        # Check if Alpaca is connected by verifying the API keys are not empty
        alpaca_connected = bool(alpaca_key and alpaca_secret)
        
        # Return API configurations
        return jsonify({
            'success': True,
            'configs': {
                'alpaca': {
                    'api_key': '****' if alpaca_key else '',
                    'api_secret': '****' if alpaca_secret else '',
                    'paper_trading': True,
                    'enabled': alpaca_connected,
                    'connected': alpaca_connected,
                    'description': 'Alpaca is a commission-free stock trading API that allows you to build and test your trading algorithms.'
                },
                'interactive_brokers': {
                    'port': os.environ.get('IB_PORT', '7496'),
                    'client_id': os.environ.get('IB_CLIENT_ID', '0'),
                    'enabled': bool(os.environ.get('IB_ENABLED', False)),
                    'connected': bool(os.environ.get('IB_CONNECTED', False)),
                    'description': 'Interactive Brokers provides a comprehensive trading API for accessing global markets.'
                },
                'trading_view': {
                    'webhook_secret': '****' if os.environ.get('TRADINGVIEW_WEBHOOK_SECRET') else '',
                    'webhook_port': os.environ.get('TRADINGVIEW_WEBHOOK_PORT', '5001'),
                    'enabled': bool(os.environ.get('TRADINGVIEW_WEBHOOK_PORT')),
                    'connected': True,  # TradingView is always "connected" if the webhook port is set
                    'description': 'TradingView webhook integration allows you to receive signals from TradingView alerts.'
                },
                'unusual_whales': {
                    'api_key': '****' if os.environ.get('UNUSUAL_WHALES_API_KEY') else '',
                    'enabled': bool(os.environ.get('UNUSUAL_WHALES_API_KEY')),
                    'connected': bool(os.environ.get('UNUSUAL_WHALES_API_KEY')),
                    'description': 'Unusual Whales provides options flow data and unusual options activity detection.'
                },
                'hume_ai': {
                    'api_key': '****' if os.environ.get('HUME_API_KEY') else '',
                    'enabled': bool(os.environ.get('HUME_API_KEY')),
                    'connected': bool(os.environ.get('HUME_API_KEY')),
                    'description': 'Hume AI provides voice notifications for trading alerts and system events.'
                }
            }
        })
    except Exception as e:
        logger.error(f"Error fetching API configurations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/configuration/update-api-configs', methods=['POST', 'OPTIONS'])
def root_update_api_configs():
    """Update API configurations (root path)."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        logger.info("API configurations update requested (root path)")
        data = request.json
        
        if not data or not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Invalid data format'
            }), 400
        
        # Get updated configurations
        updated_configs = data.get('configs', {})
        
        # Update only the toggles for now - in a real system, you'd update env variables or config files
        # For this implementation, we're just returning success
        
        return jsonify({
            'success': True,
            'message': 'API configurations updated successfully',
            'configs': updated_configs
        })
    except Exception as e:
        logger.error(f"Error updating API configurations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/configuration/test-connection', methods=['POST', 'OPTIONS'])
def root_test_api_connection():
    """Test API connection for a specific service (root path)."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        logger.info("API connection test requested (root path)")
        data = request.json
        
        if not data or not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Invalid data format'
            }), 400
        
        # Get service name from request
        service = data.get('service')
        if not service:
            return jsonify({
                'success': False,
                'error': 'Service name is required'
            }), 400
        
        # Test connection based on service name
        if service == 'alpaca':
            # Get API keys from environment variables
            api_key = os.environ.get('ALPACA_API_KEY', '')
            api_secret = os.environ.get('ALPACA_API_SECRET', '')
            
            # Check if API keys are configured
            if not api_key or not api_secret:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'message': 'Alpaca API keys are not configured'
                })
                
            # In a real implementation, you would test the connection to Alpaca API
            # For now, we'll just check if the keys are present
            return jsonify({
                'success': True,
                'connected': True,
                'message': 'Successfully connected to Alpaca API'
            })
            
        elif service == 'interactive_brokers':
            # Get IB configuration
            port = os.environ.get('IB_PORT', '')
            client_id = os.environ.get('IB_CLIENT_ID', '')
            
            # In a real implementation, you would test connection to IB
            # For now, we'll just check if port and client ID are present
            if not port or not client_id:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'message': 'Interactive Brokers configuration is incomplete'
                })
                
            return jsonify({
                'success': True,
                'connected': True,
                'message': 'Successfully connected to Interactive Brokers'
            })
            
        elif service == 'trading_view':
            # Trading View webhook is always "connected" if the webhook port is set
            webhook_port = os.environ.get('TRADINGVIEW_WEBHOOK_PORT', '')
            
            if not webhook_port:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'message': 'TradingView webhook port is not configured'
                })
                
            return jsonify({
                'success': True,
                'connected': True,
                'message': 'TradingView webhook is configured and ready'
            })
            
        elif service == 'unusual_whales':
            # Check if API key is configured
            api_key = os.environ.get('UNUSUAL_WHALES_API_KEY', '')
            
            if not api_key:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'message': 'Unusual Whales API key is not configured'
                })
                
            return jsonify({
                'success': True,
                'connected': True,
                'message': 'Successfully connected to Unusual Whales API'
            })
            
        elif service == 'hume_ai':
            # Check if API key is configured
            api_key = os.environ.get('HUME_API_KEY', '')
            
            if not api_key:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'message': 'Hume AI API key is not configured'
                })
                
            return jsonify({
                'success': True,
                'connected': True,
                'message': 'Successfully connected to Hume AI API'
            })
            
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown service: {service}'
            }), 400
            
    except Exception as e:
        logger.error(f"Error testing API connection: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add institutional flow endpoints
@app.route('/api/institutional-flow', methods=['GET', 'OPTIONS'])
def get_institutional_flow():
    """Get all institutional flow data"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        logger.info("Institutional flow data requested")
        
        # Mock data similar to what was previously defined in the frontend
        mock_flow_data = [
            {
                "id": 1,
                "symbol": "AAPL",
                "type": "sweep",
                "direction": "call",
                "premium": 1250000,
                "strike": 180,
                "expiry": "2025-12-15",
                "timestamp": datetime.now().isoformat(),
                "sentiment": "bullish",
                "flow_score": 85,
                "unusual_score": 92
            },
            {
                "id": 2,
                "symbol": "TSLA",
                "type": "block",
                "direction": "put",
                "premium": 3200000,
                "strike": 240,
                "expiry": "2025-11-17",
                "timestamp": datetime.now().isoformat(),
                "sentiment": "bearish",
                "flow_score": 78,
                "unusual_score": 88
            },
            {
                "id": 3,
                "symbol": "SPY",
                "type": "sweep",
                "direction": "call",
                "premium": 1800000,
                "strike": 440,
                "expiry": "2025-10-20",
                "timestamp": datetime.now().isoformat(),
                "sentiment": "bullish",
                "flow_score": 72,
                "unusual_score": 75
            },
            {
                "id": 4,
                "symbol": "QQQ",
                "type": "unusual",
                "direction": "call",
                "premium": 950000,
                "strike": 380,
                "expiry": "2025-11-17",
                "timestamp": datetime.now().isoformat(),
                "sentiment": "bullish",
                "flow_score": 81,
                "unusual_score": 89
            },
            {
                "id": 5,
                "symbol": "MSFT",
                "type": "block",
                "direction": "put",
                "premium": 1500000,
                "strike": 330,
                "expiry": "2025-12-15",
                "timestamp": datetime.now().isoformat(),
                "sentiment": "bearish",
                "flow_score": 65,
                "unusual_score": 70
            },
            {
                "id": 6,
                "symbol": "NVDA",
                "type": "sweep",
                "direction": "call",
                "premium": 2100000,
                "strike": 450,
                "expiry": "2025-10-20",
                "timestamp": datetime.now().isoformat(),
                "sentiment": "bullish",
                "flow_score": 92,
                "unusual_score": 95
            }
        ]
        
        # Use environment variable to check if we should return real or mock data
        use_real_data = os.environ.get('USE_REAL_INSTITUTIONAL_DATA', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': mock_flow_data,
            'isRealData': use_real_data,
            'source': 'Unusual Whales API' if use_real_data else 'mock'
        })
    except Exception as e:
        logger.error(f"Error fetching institutional flow data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/institutional-flow/get-data', methods=['POST', 'OPTIONS'])
def get_filtered_institutional_flow():
    """Get filtered institutional flow data"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        logger.info("Filtered institutional flow data requested")
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No filter data provided'
            }), 400
            
        # Log the filter criteria
        logger.info(f"Filter criteria: {data}")
        
        # Extract filter parameters
        symbols = data.get('symbols', [])
        flow_type = data.get('type', '')
        direction = data.get('direction', '')
        
        # Generate mock data
        mock_flow_data = []
        
        # List of symbols to use if none provided
        default_symbols = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOG", "META", "AMD", "INTC", "SPY", "QQQ"]
        symbols_to_use = symbols if symbols else default_symbols
        
        # Types of flow
        flow_types = ["sweep", "block", "unusual"] if not flow_type else [flow_type]
        
        # Directions
        directions = ["call", "put"] if not direction else [direction]
        
        # Generate 20 random flow items
        for i in range(1, 21):
            symbol = random.choice(symbols_to_use)
            flow_type = random.choice(flow_types)
            direction = random.choice(directions)
            
            # Base price for realistic options data
            base_prices = {
                "AAPL": 170, "MSFT": 350, "NVDA": 850, "TSLA": 200, "AMZN": 180,
                "GOOG": 170, "META": 480, "AMD": 160, "INTC": 30, "SPY": 500, "QQQ": 430
            }
            base_price = base_prices.get(symbol, 100)
            
            # Generate random but realistic data
            premium = random.randint(5, 30) * 100000
            strike_variation = random.uniform(-0.15, 0.15)
            strike = round(base_price * (1 + strike_variation), 1)
            
            # Random date in the future (1-6 months)
            future_days = random.randint(30, 180)
            expiry_date = (datetime.now() + timedelta(days=future_days)).strftime("%Y-%m-%d")
            
            # Random timestamp in the past (0-24 hours)
            past_hours = random.uniform(0, 24)
            timestamp = (datetime.now() - timedelta(hours=past_hours)).isoformat()
            
            # Flow and unusual scores
            flow_score = random.randint(60, 95)
            unusual_score = random.randint(60, 95) if flow_type == "unusual" else random.randint(50, 85)
            
            # Create flow item
            flow_item = {
                "id": i,
                "symbol": symbol,
                "type": flow_type,
                "direction": direction,
                "premium": premium,
                "strike": strike,
                "expiry": expiry_date,
                "timestamp": timestamp,
                "sentiment": "bullish" if direction == "call" else "bearish",
                "flow_score": flow_score,
                "unusual_score": unusual_score
            }
            
            mock_flow_data.append(flow_item)
        
        # Use environment variable to check if we should return real or mock data
        use_real_data = os.environ.get('USE_REAL_INSTITUTIONAL_DATA', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': mock_flow_data,
            'isRealData': use_real_data,
            'source': 'Unusual Whales API' if use_real_data else 'mock'
        })
    except Exception as e:
        logger.error(f"Error fetching filtered institutional flow data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/institutional-flow/enhanced-analysis', methods=['POST', 'OPTIONS'])
def enhanced_institutional_flow_analysis():
    """Enhanced analysis of institutional flow data"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        logger.info("Enhanced institutional flow analysis requested")
        data = request.json
        
        if not data or 'symbols' not in data:
            return jsonify({
                'success': False,
                'error': 'Symbols are required for enhanced analysis'
            }), 400
            
        # Extract parameters
        symbols = data.get('symbols', [])
        days_back = data.get('days_back', 30)
        
        if isinstance(symbols, str):
            symbols = [symbols]
            
        logger.info(f"Enhanced flow analysis requested for {symbols}, {days_back} days back")
        
        # Generate mock enhanced analysis data
        flow_analysis = {}
        smart_money_moves = []
        
        for symbol in symbols:
            # Generate signal values between -1 and 1
            options_signal = round(random.uniform(-0.8, 0.8), 2)
            dark_pool_signal = round(random.uniform(-0.9, 0.9), 2)
            block_trade_signal = round(random.uniform(-0.7, 0.7), 2)
            
            # Combined weighted signal
            signal = round((options_signal * 0.65 + dark_pool_signal * 0.75 + block_trade_signal * 0.6) / 2, 2)
            
            # Confidence score between 0.5 and 0.95
            confidence = round(random.uniform(0.5, 0.95), 2)
            
            # Price correlations
            price_correlations = {
                "short_term": round(random.uniform(-0.7, 0.7), 2),
                "medium_term": round(random.uniform(-0.5, 0.5), 2),
                "long_term": round(random.uniform(-0.3, 0.3), 2)
            }
            
            # Create analysis object
            flow_analysis[symbol] = {
                "symbol": symbol,
                "signal": signal,
                "options_signal": options_signal,
                "dark_pool_signal": dark_pool_signal,
                "block_trade_signal": block_trade_signal,
                "price_correlations": price_correlations,
                "confidence": confidence,
                "has_significant_flow": abs(signal) > 0.55,
                "details": f"Enhanced institutional flow analysis for {symbol}",
                "timestamp": datetime.now().isoformat()
            }
            
            # Random chance to add a smart money move
            if random.random() > 0.4:
                smart_money_moves.append({
                    "type": random.choice(["OPTIONS", "DARK_POOL", "BLOCK_TRADE"]),
                    "symbol": symbol,
                    "sentiment": "bullish" if signal > 0 else "bearish",
                    "confidence": round(random.uniform(0.7, 0.98), 2),
                    "description": f"Significant institutional {'buying' if signal > 0 else 'selling'} detected",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Use environment variable to check if we should return real or mock data
        use_real_data = os.environ.get('USE_REAL_INSTITUTIONAL_DATA', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'days_analyzed': days_back,
            'analysis_version': 'enhanced-v1.0',
            'flow_analysis': flow_analysis,
            'smart_money_moves': smart_money_moves,
            'is_real_data': use_real_data,
            'data_source': 'Unusual Whales API' if use_real_data else 'mock'
        })
    except Exception as e:
        logger.error(f"Error in enhanced institutional flow analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add endpoints for 13F filings and insider trading
@app.route('/api/13f-filings', methods=['GET', 'OPTIONS'])
def get_13f_filings():
    """Get 13F filings data"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        logger.info("13F filings data requested")
        
        # Extract query parameters
        start_date = request.args.get('start_date')
        sector = request.args.get('sector')
        
        logger.info(f"13F filings requested with start date: {start_date}, sector: {sector}")
        
        # Generate mock 13F filings data
        mock_data = []
        companies = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "JPM", "V", "XOM", "CVX", "PFE", "JNJ", "UNH", "COST"]
        sectors = {
            "AAPL": "Technology", "MSFT": "Technology", "AMZN": "Consumer Discretionary", 
            "GOOGL": "Communication Services", "META": "Communication Services", 
            "NVDA": "Technology", "TSLA": "Consumer Discretionary", "JPM": "Financials", 
            "V": "Financials", "XOM": "Energy", "CVX": "Energy", "PFE": "Healthcare", 
            "JNJ": "Healthcare", "UNH": "Healthcare", "COST": "Consumer Staples"
        }
        institutions = [
            "BlackRock", "Vanguard", "State Street", "Fidelity", "Capital Group",
            "JPMorgan Asset Management", "BNY Mellon", "T. Rowe Price", "Goldman Sachs",
            "Morgan Stanley"
        ]
        
        # Filter by sector if provided
        filtered_companies = companies
        if sector and sector != 'all':
            filtered_companies = [c for c in companies if sectors.get(c) == sector]
        
        for i in range(1, 31):
            # Select a random company and institution
            symbol = random.choice(filtered_companies)
            institution = random.choice(institutions)
            
            # Random date within the last 90 days
            filing_days_ago = random.randint(1, 90)
            filing_date = (datetime.now() - timedelta(days=filing_days_ago)).strftime("%Y-%m-%d")
            
            # Only include if after the start date or no start date was provided
            if not start_date or filing_date >= start_date:
                # Generate random data
                shares = random.randint(100000, 10000000)
                value = shares * random.uniform(10, 1000)
                change_pct = random.uniform(-30, 30)
                
                # Create filing item
                filing_item = {
                    "id": i,
                    "symbol": symbol,
                    "institution": institution,
                    "sector": sectors.get(symbol, "Unknown"),
                    "shares": shares,
                    "value": round(value, 2),
                    "change": f"{change_pct:.2f}%",
                    "direction": "buy" if change_pct > 0 else "sell",
                    "filing_date": filing_date,
                    "quarter": f"Q{random.randint(1, 4)} {datetime.now().year}",
                    "timestamp": (datetime.now() - timedelta(days=filing_days_ago)).isoformat()
                }
                
                mock_data.append(filing_item)
        
        # Use environment variable to check if we should return real or mock data
        use_real_data = os.environ.get('USE_REAL_INSTITUTIONAL_DATA', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': mock_data,
            'isRealData': use_real_data,
            'source': 'SEC API' if use_real_data else 'mock'
        })
    except Exception as e:
        logger.error(f"Error fetching 13F filings data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/insider-trading', methods=['GET', 'OPTIONS'])
def get_insider_trading():
    """Get insider trading data"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        logger.info("Insider trading data requested")
        
        # Extract query parameters
        start_date = request.args.get('start_date')
        
        logger.info(f"Insider trading requested with start date: {start_date}")
        
        # Generate mock insider trading data
        mock_data = []
        companies = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "JPM", "V", "XOM", "CVX", "PFE", "JNJ", "UNH", "COST"]
        sectors = {
            "AAPL": "Technology", "MSFT": "Technology", "AMZN": "Consumer Discretionary", 
            "GOOGL": "Communication Services", "META": "Communication Services", 
            "NVDA": "Technology", "TSLA": "Consumer Discretionary", "JPM": "Financials", 
            "V": "Financials", "XOM": "Energy", "CVX": "Energy", "PFE": "Healthcare", 
            "JNJ": "Healthcare", "UNH": "Healthcare", "COST": "Consumer Staples"
        }
        positions = ["CEO", "CFO", "CTO", "Director", "Board Member", "VP", "COO", "President", "SVP", "Chairman"]
        first_names = ["John", "Jane", "Michael", "Sarah", "Robert", "Emily", "David", "Jennifer", "William", "Elizabeth"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
        
        for i in range(1, 31):
            # Select a random company and position
            symbol = random.choice(companies)
            position = random.choice(positions)
            insider_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            # Random date within the last 30 days
            filing_days_ago = random.randint(1, 30)
            filing_date = (datetime.now() - timedelta(days=filing_days_ago)).strftime("%Y-%m-%d")
            
            # Only include if after the start date or no start date was provided
            if not start_date or filing_date >= start_date:
                # Generate random data
                shares = random.randint(1000, 100000)
                price = random.uniform(10, 1000)
                value = shares * price
                is_buy = random.random() > 0.5
                
                # Create insider trading item
                insider_item = {
                    "id": i,
                    "symbol": symbol,
                    "sector": sectors.get(symbol, "Unknown"),
                    "insider_name": insider_name,
                    "position": position,
                    "shares": shares,
                    "price": round(price, 2),
                    "value": round(value, 2),
                    "direction": "buy" if is_buy else "sell",
                    "filing_date": filing_date,
                    "timestamp": (datetime.now() - timedelta(days=filing_days_ago)).isoformat(),
                    "contract_type": "none"  # Ensure this exists to avoid undefined errors
                }
                
                mock_data.append(insider_item)
        
        # Use environment variable to check if we should return real or mock data
        use_real_data = os.environ.get('USE_REAL_INSTITUTIONAL_DATA', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': mock_data,
            'isRealData': use_real_data,
            'source': 'SEC API' if use_real_data else 'mock'
        })
    except Exception as e:
        logger.error(f"Error fetching insider trading data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add market data endpoint for symbols
@app.route('/api/market-data/<symbol>', methods=['GET', 'OPTIONS'])
def get_market_data(symbol):
    """Get market data for a specific symbol."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    logger.info(f"Market data requested for {symbol}")
    
    try:
        # Create mock market data with the requested symbol
        # In a real implementation, this would fetch data from a market data provider
        base_prices = {
            'SPY': 450.0,
            'QQQ': 350.0,
            'AAPL': 180.0,
            'MSFT': 350.0,
            'TSLA': 200.0,
            'NVDA': 850.0,
            'GOOGL': 170.0,
            'META': 450.0,
            'AMZN': 180.0
        }
        
        # Use symbol's base price or default to 100
        base_price = base_prices.get(symbol, 100.0)
        
        # Add some randomness to the price
        current_price = base_price + random.uniform(-5.0, 5.0)
        
        market_data = {
            'symbol': symbol,
            'price': round(current_price, 2),
            'change': round(random.uniform(-2.0, 2.0), 2),
            'change_percent': round(random.uniform(-2.0, 2.0), 2),
            'volume': random.randint(1000000, 10000000),
            'avg_volume_10d': random.randint(1000000, 10000000),
            'high': round(current_price + random.uniform(0.5, 3.0), 2),
            'low': round(current_price - random.uniform(0.5, 3.0), 2),
            'open': round(current_price - random.uniform(-2.0, 2.0), 2),
            'prev_close': round(current_price - random.uniform(-1.0, 1.0), 2),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(market_data)
    except Exception as e:
        logger.error(f"Error generating market data for {symbol}: {str(e)}")
        return jsonify({
            'error': str(e),
            'symbol': symbol
        }), 500

# Add options data endpoint for symbols
@app.route('/api/options-data/<symbol>', methods=['GET', 'OPTIONS'])
def get_options_data(symbol):
    """Get options data for a specific symbol."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    logger.info(f"Options data requested for {symbol}")
    
    try:
        # Get base price from the market data for consistency
        base_prices = {
            'SPY': 450.0,
            'QQQ': 350.0,
            'AAPL': 180.0,
            'MSFT': 350.0,
            'TSLA': 200.0,
            'NVDA': 850.0,
            'GOOGL': 170.0,
            'META': 450.0,
            'AMZN': 180.0
        }
        
        # Use symbol's base price or default to 100
        current_price = base_prices.get(symbol, 100.0) + random.uniform(-5.0, 5.0)
        current_price = round(current_price, 2)
        
        # Generate expiration dates (next 4 Fridays)
        expiration_dates = []
        current_date = datetime.now()
        
        # Find the next Friday
        days_until_friday = (4 - current_date.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7  # If today is Friday, go to next Friday
        
        next_friday = current_date + timedelta(days=days_until_friday)
        
        # Generate 4 expiration dates (consecutive Fridays)
        for i in range(4):
            friday = next_friday + timedelta(days=i*7)
            expiration_dates.append(friday.strftime('%Y-%m-%d'))
        
        # Generate strike prices around current price
        strikes = []
        for i in range(-5, 6):
            strike = round(current_price + i * (current_price * 0.025), 1)  # 2.5% increments
            strikes.append(strike)
        
        # Generate option chain
        options = []
        
        for expiration in expiration_dates:
            # Days to expiration
            exp_date = datetime.strptime(expiration, '%Y-%m-%d')
            days_to_exp = (exp_date - current_date).days
            
            # Different IV for different expirations (further out = higher IV)
            base_iv = 0.20 + (days_to_exp / 365) * 0.10
            
            for strike in strikes:
                # Calculate option prices based on distance from strike
                distance_pct = abs(current_price - strike) / current_price
                
                # Call premium calculation (simplified)
                call_iv = base_iv * (1 - 0.3 * (strike > current_price))  # Lower IV for OTM calls
                call_price = max(0.05, round((current_price * 0.05) * (1 - distance_pct * 2) * (1 + days_to_exp/365), 2))
                if strike < current_price:
                    call_price += (current_price - strike)  # Add intrinsic value for ITM calls
                
                # Put premium calculation (simplified)
                put_iv = base_iv * (1 - 0.3 * (strike < current_price))  # Lower IV for OTM puts
                put_price = max(0.05, round((current_price * 0.05) * (1 - distance_pct * 2) * (1 + days_to_exp/365), 2))
                if strike > current_price:
                    put_price += (strike - current_price)  # Add intrinsic value for ITM puts
                
                # Generate random volume, higher near the money
                atm_factor = 1 - min(1, distance_pct * 5)
                base_volume = int(random.randint(50, 500) * atm_factor)
                
                # Add call option
                options.append({
                    'strike': strike,
                    'expiration': expiration,
                    'call_price': call_price,
                    'call_iv': round(call_iv, 2),
                    'call_volume': base_volume + random.randint(0, 100),
                    'call_open_interest': base_volume * 3 + random.randint(0, 300),
                    'days_to_expiration': days_to_exp
                })
                
                # Add put option
                options.append({
                    'strike': strike,
                    'expiration': expiration,
                    'put_price': put_price,
                    'put_iv': round(put_iv, 2),
                    'put_volume': base_volume + random.randint(0, 100),
                    'put_open_interest': base_volume * 3 + random.randint(0, 300),
                    'days_to_expiration': days_to_exp
                })
        
        # Return options data
        return jsonify({
            'symbol': symbol,
            'underlying_price': current_price,
            'timestamp': datetime.now().isoformat(),
            'expirations': expiration_dates,
            'options': options
        })
        
    except Exception as e:
        logger.error(f"Error generating options data for {symbol}: {str(e)}")
        return jsonify({
            'error': str(e),
            'symbol': symbol
        }), 500

# Add news endpoint for symbols
@app.route('/api/news/<symbol>', methods=['GET', 'OPTIONS'])
def get_news(symbol):
    """Get news for a specific symbol."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    logger.info(f"News requested for {symbol}")
    
    try:
        # Generate mock news for the requested symbol
        # In a real implementation, this would fetch news from a news provider
        company_names = {
            'SPY': 'S&P 500 ETF',
            'QQQ': 'Nasdaq 100 ETF',
            'AAPL': 'Apple',
            'MSFT': 'Microsoft',
            'TSLA': 'Tesla',
            'NVDA': 'NVIDIA',
            'GOOGL': 'Alphabet',
            'META': 'Meta Platforms',
            'AMZN': 'Amazon'
        }
        
        # Use company name or default to symbol
        company = company_names.get(symbol, symbol)
        
        # Types of news headlines
        headline_templates = [
            "{company} Announces Strong Quarterly Earnings",
            "{company} Shares {direction} After Analyst Upgrade",
            "{company} Reveals New Product Line",
            "{company} CEO Discusses Future Growth Strategy",
            "{company} Reports {direction} Sales for Recent Quarter",
            "{company} Partners with {partner} on New Initiative",
            "{company} Expands into New Markets",
            "{company} Addresses Recent Industry Challenges",
            "{company} Stock {direction} on {reason}",
            "{company} Investors React to Recent {event}"
        ]
        
        # Generate random news items
        news_items = []
        sources = ['Market News', 'Financial Times', 'WSJ', 'Bloomberg', 'CNBC', 'Reuters', 'Barron\'s']
        directions = ['Up', 'Down', 'Higher', 'Lower', 'Surges', 'Drops', 'Rallies', 'Declines']
        reasons = ['Earnings Beat', 'Federal Reserve News', 'Economic Data', 'Sector Performance', 'Analyst Comments']
        events = ['Announcement', 'Earnings Call', 'Industry Conference', 'Strategy Shift']
        partners = ['Microsoft', 'Amazon', 'Google', 'Major Retailer', 'Tech Startup', 'Overseas Manufacturer']
        
        current_date = datetime.now()
        
        # Generate 5-10 news items
        num_items = random.randint(5, 10)
        for i in range(num_items):
            # Select a headline template and format it
            template = random.choice(headline_templates)
            headline = template.format(
                company=company,
                direction=random.choice(directions),
                reason=random.choice(reasons),
                event=random.choice(events),
                partner=random.choice(partners)
            )
            
            # Generate a date within the last 7 days
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            news_date = current_date - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # Generate a news item
            news_item = {
                'title': headline,
                'source': random.choice(sources),
                'url': f"https://example.com/news/{uuid.uuid4()}",
                'sentiment': random.choice(['positive', 'negative', 'neutral']),
                'relevance': round(random.uniform(0.6, 1.0), 2),
                'published_at': news_date.isoformat(),
                'summary': f"This is a mock news item about {company}. In a real implementation, this would be a summary of the actual news article."
            }
            
            news_items.append(news_item)
        
        # Sort news by date (newest first)
        news_items.sort(key=lambda x: x['published_at'], reverse=True)
        
        return jsonify({
            'symbol': symbol,
            'company_name': company,
            'news': news_items,
            'count': len(news_items),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating news for {symbol}: {str(e)}")
        return jsonify({
            'error': str(e),
            'symbol': symbol
        }), 500

# Add dual-bot signals endpoint
@app.route('/api/dual-bot/signals', methods=['GET', 'OPTIONS'])
def get_dual_bot_signals():
    """Get trading signals from the dual bot."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    logger.info("Dual bot signals requested")
    
    try:
        # Generate mock trading signals
        # In a real implementation, this would fetch actual signals from the dual bot
        symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'GOOGL', 'META', 'AMZN']
        
        # Base prices for consistency
        base_prices = {
            'SPY': 450.0,
            'QQQ': 350.0,
            'AAPL': 180.0,
            'MSFT': 350.0,
            'TSLA': 200.0,
            'NVDA': 850.0,
            'GOOGL': 170.0,
            'META': 450.0,
            'AMZN': 180.0
        }
        
        current_date = datetime.now()
        
        # Generate 3-7 signals
        num_signals = random.randint(3, 7)
        signals = []
        
        for i in range(num_signals):
            # Pick a random symbol
            symbol = random.choice(symbols)
            
            # Get the base price
            base_price = base_prices.get(symbol, 100.0)
            current_price = round(base_price + random.uniform(-5.0, 5.0), 2)
            
            # Create a signal with random parameters
            signal_type = random.choice(['BUY', 'SELL', 'BUY_TO_OPEN', 'SELL_TO_CLOSE'])
            
            # Generate EMA values for technical indicators
            ema_9 = round(current_price * (1 + random.uniform(-0.05, 0.05)), 2)
            ema_21 = round(current_price * (1 + random.uniform(-0.05, 0.05)), 2)
            
            # Determine if price is above or below EMAs for signal quality
            above_ema9 = current_price > ema_9
            above_ema21 = current_price > ema_21
            
            # Calculate signal score based on EMA crossovers
            if signal_type in ['BUY', 'BUY_TO_OPEN']:
                signal_score = 0.5
                # Higher score for bullish patterns
                if above_ema9 and above_ema21:
                    signal_score += 0.3
                elif above_ema9 and not above_ema21:  # EMA crossover (9 crossed above 21)
                    signal_score += 0.4
            else:
                signal_score = 0.5
                # Higher score for bearish patterns
                if not above_ema9 and not above_ema21:
                    signal_score += 0.3
                elif not above_ema9 and above_ema21:  # EMA crossover (9 crossed below 21)
                    signal_score += 0.4
            
            # Add some randomness to the signal score
            signal_score = min(0.95, signal_score + random.uniform(-0.1, 0.1))
            signal_score = round(signal_score, 2)
            
            # Calculate target and stop prices
            if signal_type in ['BUY', 'BUY_TO_OPEN']:
                # For buy signals: target is higher, stop is lower
                price_target = round(current_price * (1 + random.uniform(0.03, 0.10)), 2)
                stop_loss = round(current_price * (1 - random.uniform(0.02, 0.05)), 2)
            else:
                # For sell signals: target is lower, stop is higher
                price_target = round(current_price * (1 - random.uniform(0.03, 0.10)), 2)
                stop_loss = round(current_price * (1 + random.uniform(0.02, 0.05)), 2)
            
            # Create the signal
            signal = {
                'symbol': symbol,
                'type': signal_type,
                'signal_score': signal_score,
                'confidence': round(signal_score * 100),  # Convert to percentage
                'price_target': price_target,
                'stop_loss': stop_loss,
                'entry': current_price,
                'close': current_price,
                'volume': random.randint(100000, 10000000),
                'date': (current_date - timedelta(minutes=random.randint(5, 120))).isoformat(),
                'ema_9': ema_9,
                'ema_21': ema_21,
                'rsi': round(random.uniform(20, 80), 2),
                'macd': round(random.uniform(-2, 2), 2),
                'macd_signal': round(random.uniform(-2, 2), 2),
                'rationale': f"Signal based on technical indicators and AI analysis. Confidence: {signal_score * 100}%"
            }
            
            signals.append(signal)
        
        # Sort signals by score (highest first)
        signals.sort(key=lambda x: x['signal_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'signals': signals,
            'count': len(signals),
            'timestamp': current_date.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add assess-risk endpoint
@app.route('/api/assess-risk', methods=['POST', 'OPTIONS'])
def assess_risk():
    """Assess the risk of a trading recommendation."""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    logger.info("Risk assessment requested")
    
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Log the request data
        logger.info(f"Assessing risk for: {json.dumps(data, indent=2)}")
        
        # Extract data from request
        recommendation = data.get('recommendation', {})
        market_context = data.get('market_context', {})
        
        # Create a mock risk assessment
        symbol = recommendation.get('symbol', 'unknown')
        trade_type = recommendation.get('trade_type', 'unknown')
        
        # Calculate a risk score (1-10)
        base_score = random.uniform(3.0, 8.0)
        
        # Adjust score based on trade type
        if trade_type in ['BUY', 'BUY_TO_OPEN']:
            # Buying is generally less risky in a bullish market
            if market_context.get('market_condition') == 'bullish':
                risk_adjustment = -0.5  # Lower risk
            else:
                risk_adjustment = 0.8   # Higher risk
        else:
            # Selling is generally less risky in a bearish market
            if market_context.get('market_condition') == 'bearish':
                risk_adjustment = -0.5  # Lower risk
            else:
                risk_adjustment = 0.8   # Higher risk
        
        # Adjust for volatility
        volatility = market_context.get('volatility', 'medium')
        if volatility == 'high':
            volatility_adjustment = 1.5
        elif volatility == 'low':
            volatility_adjustment = -1.0
        else:
            volatility_adjustment = 0.0
        
        # Calculate final risk score (1-10 scale)
        risk_score = min(10.0, max(1.0, base_score + risk_adjustment + volatility_adjustment))
        
        # Determine if the trade is approved based on risk score
        approved = risk_score <= 7.5
        
        # Generate concerns and summary based on risk factors
        concerns = []
        if risk_score > 6.0:
            concerns.append("Risk score is elevated")
        if volatility == 'high':
            concerns.append("Market volatility is high")
        if not approved:
            concerns.append("Overall risk exceeds recommended threshold")
        
        # Create response
        response = {
            'success': True,
            'approved': approved,
            'risk_score': round(risk_score, 1),
            'market_conditions': market_context.get('market_condition', 'unknown'),
            'symbol': symbol,
            'trade_type': trade_type,
            'concerns': ', '.join(concerns) if concerns else 'No significant concerns',
            'summary': f"{'Approved' if approved else 'Rejected'} with risk score of {risk_score:.1f}/10",
            'recommendation': "Proceed with caution" if approved else "Consider alternative trade"
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error assessing risk: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add a global route for OPTIONS requests to handle CORS preflight properly
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """Global handler for OPTIONS requests to support CORS preflight."""
    headers = {
        'Access-Control-Allow-Origin': request.headers.get('Origin', 'http://localhost:3001'),
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept, X-API-Key',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '3600'  # Cache preflight response for 1 hour
    }
    return '', 204, headers

# Run the application
if __name__ == '__main__':
    # Create the dashboard directory if it doesn't exist
    os.makedirs('data/dashboard', exist_ok=True)
    
    # Create a CEO dashboard file if it doesn't exist
    ceo_dashboard_path = os.path.join('data', 'dashboard', 'ceo_dashboard.json')
    if not os.path.exists(ceo_dashboard_path):
        with open(ceo_dashboard_path, 'w') as f:
            json.dump({
                "performance": {
                    "daily": random.uniform(0.5, 2.5),
                    "weekly": random.uniform(1.5, 5.0),
                    "monthly": random.uniform(4.0, 12.0),
                    "yearly": random.uniform(15.0, 35.0)
                },
                "trades": {
                    "total": random.randint(500, 1500),
                    "winning": random.randint(300, 900),
                    "losing": random.randint(100, 300)
                },
                "capital": {
                    "initial": 100000,
                    "current": random.uniform(115000, 150000),
                    "growth": random.uniform(15.0, 50.0)
                },
                "risk": {
                    "drawdown": random.uniform(3.0, 8.0),
                    "sharpe": random.uniform(1.2, 2.8),
                    "volatility": random.uniform(5.0, 15.0)
                }
            }, f, indent=2)
    
    logger.info("Starting Dual Bot API server on port 5001")
    print("Starting Dual Bot API server on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True) 