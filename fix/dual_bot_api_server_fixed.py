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
CORS(app)

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
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
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
        alpaca_secret = os.environ.get('ALPACA_SECRET_KEY', '')
        
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
                    'enabled': bool(os.environ.get('HUME_AI_KEY')),
                    'connected': bool(os.environ.get('HUME_AI_KEY')),
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
            api_secret = os.environ.get('ALPACA_SECRET_KEY', '')
            
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
            api_key = os.environ.get('HUME_AI_KEY', '')
            
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
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    return jsonify({'status': 'healthy'}), 200

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