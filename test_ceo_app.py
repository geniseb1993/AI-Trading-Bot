"""
Simple Flask app to test CEO dashboard routes
"""
from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create Flask app
app = Flask(__name__)
CORS(app)

# Register CEO dashboard routes
try:
    from api.routes.ceo_dashboard_routes import ceo_dashboard_bp
    app.register_blueprint(ceo_dashboard_bp)
    logger.info("Successfully registered CEO dashboard routes")
except ImportError as e1:
    logger.error(f"Error importing from api.routes: {e1}")
    try:
        from routes.ceo_dashboard_routes import ceo_dashboard_bp
        app.register_blueprint(ceo_dashboard_bp)
        logger.info("Successfully registered CEO dashboard routes from alternative path")
    except ImportError as e2:
        logger.error(f"Error importing from routes: {e2}")
        
        # Create a mock blueprint for testing
        from flask import Blueprint, request, make_response, jsonify
        mock_bp = Blueprint('ceo_dashboard', __name__)
        
        @mock_bp.route('/ceo-dashboard', methods=['GET', 'OPTIONS'])
        def get_dashboard():
            """Get all CEO dashboard data in a single request"""
            if request.method == 'OPTIONS':
                response = make_response('')
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
                return response
            
            # Mock data for testing
            mock_data = {
                "success": True,
                "performance": {
                    "dailyPnL": 3.5,
                    "weeklyPnL": 7.2,
                    "monthlyPnL": 15.5,
                    "winRate": 68,
                    "totalTrades": 25,
                    "avgWin": 5.3,
                    "avgLoss": -2.1,
                    "biggestWin": 15.8,
                    "biggestLoss": -5.2
                },
                "tradeSetups": [
                    {
                        "id": "setup_mock_1",
                        "symbol": "SPY",
                        "type": "CALL",
                        "strategy": "0DTE Momentum",
                        "price": 425.75,
                        "confidence": 0.85,
                        "recommendation": "BUY SPY CALL @ 425.75",
                        "expiration": "0DTE",
                        "timestamp": "2023-05-18T14:30:00"
                    }
                ],
                "riskStatus": {
                    "currentExposure": 45,
                    "maxExposure": 80,
                    "dailyPnLRisk": 15.2,
                    "marketCondition": "Bullish",
                    "volatilityLevel": "Moderate",
                    "riskLevel": "Moderate",
                    "warningMessage": None
                },
                "systemHealth": {
                    "components": {
                        "dataFetcher": {
                            "status": "operational",
                            "latency": 120
                        },
                        "signalGenerator": {
                            "status": "operational",
                            "latency": 450
                        },
                        "riskManager": {
                            "status": "operational",
                            "latency": 85
                        },
                        "executionEngine": {
                            "status": "operational",
                            "latency": 220
                        }
                    },
                    "lastUpdated": "2023-05-18T14:35:00"
                }
            }
            
            response = make_response(jsonify(mock_data))
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        app.register_blueprint(mock_bp)
        logger.info("Registered mock CEO dashboard blueprint")

# Test route
@app.route('/test', methods=['GET'])
def test_route():
    return jsonify({
        'success': True,
        'message': 'Test app is running'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000) 