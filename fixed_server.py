"""
Fixed Flask API Server
=====================

A simplified server focusing on handling both prefixed (/api/*) and non-prefixed routes.
This version has improved logging to help debug routing issues.
"""

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configure CORS to allow all origins, methods, and headers
CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "X-Request-ID"],
    "expose_headers": ["Content-Type", "X-Request-ID"],
    "supports_credentials": True
}})

# Bot status storage
bots_status = {
    "autonomous_bot": {
        "status": False,
        "last_update": datetime.datetime.now().isoformat(),
        "active_trades": []
    },
    "rsi_bot": {
        "status": False,
        "last_update": datetime.datetime.now().isoformat(),
        "active_signals": []
    },
    "dual_bot": {
        "status": False,
        "last_update": datetime.datetime.now().isoformat(),
        "active_positions": []
    }
}

# Enable detailed request logging
@app.before_request
def log_request_info():
    logger.info(f'Request: {request.method} {request.path}')
    logger.info(f'Headers: {dict(request.headers)}')
    
    # Log request body for POST/PUT requests
    if request.method in ['POST', 'PUT'] and request.is_json:
        logger.info(f'JSON Body: {request.json}')
    elif request.data:
        logger.info(f'Body: {request.data}')
    
    # Log query parameters
    if request.args:
        logger.info(f'Query Parameters: {dict(request.args)}')

@app.after_request
def after_request(response):
    logger.info(f'Response status: {response.status_code}')
    
    # Add CORS headers to every response
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,X-Request-ID')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    return response

# Current time helper
def get_current_time():
    return datetime.datetime.now().isoformat()

# Standard response helper
def success_response(data=None, message="Success"):
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response)

# Helper to define routes with both prefixed and non-prefixed paths
def register_dual_routes(app, endpoint, view_func, methods=None, defaults=None):
    """Register both /api/path and /path routes for the same view function"""
    if methods is None:
        methods = ['GET']
    
    # Register with /api prefix
    api_route = f'/api{endpoint}'
    app.add_url_rule(api_route, f'api_{view_func.__name__}', view_func, 
                     methods=methods, defaults=defaults)
    
    # Register without prefix
    app.add_url_rule(endpoint, view_func.__name__, view_func, 
                     methods=methods, defaults=defaults)
    
    logger.info(f"Registered route {endpoint} with methods {methods}")

# Special OPTIONS handler for all routes
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    logger.info(f"OPTIONS request for /{path}")
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,X-Request-ID')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Health Check
@app.route('/api/health-check')
@app.route('/health-check')
def health_check():
    logger.info("Health check endpoint called")
    return jsonify({
        "status": "healthy",
        "time": get_current_time()
    })

# Bot Status
@app.route('/api/bot/status')
@app.route('/bot/status')
def bot_status():
    logger.info("Bot status endpoint called")
    return jsonify(bots_status)

# Bot Actions
@app.route('/api/bot/start/<bot_type>', methods=['POST', 'OPTIONS'])
@app.route('/bot/start/<bot_type>', methods=['POST', 'OPTIONS'])
def start_bot(bot_type):
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,X-Request-ID')
        return response
        
    logger.info(f"Start bot endpoint called for {bot_type}")
    
    # Update the bot status
    if bot_type == 'autonomous':
        bots_status["autonomous_bot"]["status"] = True
        bots_status["autonomous_bot"]["last_update"] = get_current_time()
    elif bot_type == 'rsi':
        bots_status["rsi_bot"]["status"] = True
        bots_status["rsi_bot"]["last_update"] = get_current_time()
    elif bot_type == 'dual':
        bots_status["dual_bot"]["status"] = True
        bots_status["dual_bot"]["last_update"] = get_current_time()
    
    return jsonify({
        "success": True,
        "message": f"{bot_type} bot started successfully",
        "status": "success"
    })

@app.route('/api/bot/stop/<bot_type>', methods=['POST', 'OPTIONS'])
@app.route('/bot/stop/<bot_type>', methods=['POST', 'OPTIONS'])
def stop_bot(bot_type):
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,X-Request-ID')
        return response
        
    logger.info(f"Stop bot endpoint called for {bot_type}")
    
    # Update the bot status
    if bot_type == 'autonomous':
        bots_status["autonomous_bot"]["status"] = False
        bots_status["autonomous_bot"]["last_update"] = get_current_time()
    elif bot_type == 'rsi':
        bots_status["rsi_bot"]["status"] = False
        bots_status["rsi_bot"]["last_update"] = get_current_time()
    elif bot_type == 'dual':
        bots_status["dual_bot"]["status"] = False
        bots_status["dual_bot"]["last_update"] = get_current_time()
    
    return jsonify({
        "success": True,
        "message": f"{bot_type} bot stopped successfully",
        "status": "success"
    })

@app.route('/api/bot/run-cycle/<bot_type>', methods=['POST', 'OPTIONS'])
@app.route('/bot/run-cycle/<bot_type>', methods=['POST', 'OPTIONS'])
def run_bot_cycle(bot_type):
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,X-Request-ID')
        return response
        
    logger.info(f"Run cycle endpoint called for {bot_type}")
    return jsonify({
        "success": True,
        "message": f"{bot_type} bot trading cycle executed successfully",
        "status": "success"
    })

# AI Activity Logs
@app.route('/api/ai-activity/logs')
@app.route('/ai-activity/logs')
def ai_activity_logs():
    limit = request.args.get('limit', default=10, type=int)
    logger.info(f"AI activity logs endpoint called with limit={limit}")
    
    logs = []
    for i in range(min(limit, 50)):
        logs.append({
            "id": f"log-{i+1}",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=i*15)).isoformat(),
            "type": ["trade_analysis", "signal_generation", "trade_execution"][i % 3],
            "message": f"Sample activity log {i+1}",
            "details": {"symbol": "SPY", "timeframe": "1h", "indicators": ["MA", "RSI"]}
        })
    
    return jsonify({
        "success": True,
        "logs": logs
    })

# AI Activity Types
@app.route('/api/ai-activity/activity-types')
@app.route('/ai-activity/activity-types')
def ai_activity_types():
    logger.info("AI activity types endpoint called")
    return jsonify({
        "success": True,
        "types": [
            {"id": "trade_analysis", "name": "Trade Analysis", "color": "#4285F4"},
            {"id": "signal_generation", "name": "Signal Generation", "color": "#34A853"},
            {"id": "trade_execution", "name": "Trade Execution", "color": "#EA4335"}
        ]
    })

# Risk Management Settings
@app.route('/api/risk-management/settings')
@app.route('/risk-management/settings')
def risk_management_settings():
    logger.info("Risk management settings endpoint called")
    return jsonify({
        "success": True,
        "settings": {
            "maxPositionSize": 5.0,
            "maxDailyDrawdown": 3.0,
            "maxOpenPositions": 5,
            "tradeTimeRestrictions": {
                "enabled": True,
                "allowedHours": ["9:30-16:00"]
            },
            "stopLossSettings": {
                "enabled": True,
                "defaultPercentage": 2.0
            },
            "takeProfitSettings": {
                "enabled": True,
                "defaultPercentage": 5.0
            },
            "volatilityFilters": {
                "enabled": True,
                "maxAllowedVix": 35
            }
        }
    })

# CEO Dashboard
@app.route('/api/ceo-dashboard')
@app.route('/ceo-dashboard')
def ceo_dashboard():
    logger.info("CEO dashboard endpoint called")
    return jsonify({
        "success": True,
        "performance": {
            "dailyPnL": 3.2,
            "weeklyPnL": 8.5,
            "monthlyPnL": 12.7,
            "winRate": 68,
            "totalTrades": 25,
            "avgWin": 5.2,
            "avgLoss": -1.8
        },
        "riskStatus": {
            "currentExposure": 35,
            "maxExposure": 80,
            "marketCondition": "Bullish",
            "volatilityLevel": "Moderate",
            "riskLevel": "Moderate",
            "controls": {
                "autoTrading": True,
                "odteOnly": True
            }
        },
        "tradeSetups": [
            {
                "id": "setup_1",
                "symbol": "SPX",
                "type": "CALL",
                "strategy": "0DTE Momentum",
                "price": 4520.50,
                "confidence": 0.87,
                "recommendation": "BUY SPX CALL @ 4525",
                "expiration": "0DTE",
                "timestamp": get_current_time()
            }
        ]
    })

# CEO Settings
@app.route('/api/ceo-settings')
@app.route('/ceo-settings')
def ceo_settings():
    logger.info("CEO settings endpoint called")
    return jsonify({
        "success": True,
        "settings": {
            "autoTrading": True,
            "riskLevel": "moderate",
            "maxDailyTrades": 5,
            "stopLossPercent": 2.0,
            "odteOnly": True
        }
    })

# Default landing page
@app.route('/')
def index():
    endpoints = [
        '/api/health-check',
        '/api/bot/status',
        '/api/bot/start/<bot_type>',
        '/api/bot/stop/<bot_type>',
        '/api/bot/run-cycle/<bot_type>',
        '/api/ceo-dashboard',
        '/api/ceo-settings',
        '/api/ai-activity/logs',
        '/api/ai-activity/activity-types',
        '/api/risk-management/settings'
    ]
    
    return jsonify({
        "service": "Fixed API Server",
        "version": "1.0.0",
        "status": "running",
        "message": "This server handles both /api prefixed and non-prefixed routes",
        "endpoints": endpoints
    })

if __name__ == '__main__':
    print("Starting fixed Flask API server on http://localhost:5000")
    print("This server handles both /api prefixed and non-prefixed routes")
    print("Press Ctrl+C to stop the server")
    
    # Print all registered routes
    for rule in app.url_map.iter_rules():
        logger.info(f"Route: {rule.rule}, Methods: {rule.methods}")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 