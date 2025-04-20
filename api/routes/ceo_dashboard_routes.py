from flask import Blueprint, jsonify, request, make_response
import pandas as pd
import numpy as np
import os
import json
import logging
from datetime import datetime, timedelta
import traceback
import random
from api.utils.cors_utils import add_cors_headers

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
ceo_dashboard_bp = Blueprint('ceo_dashboard', __name__)

# Constants
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
SIGNALS_DIR = os.path.join(DATA_DIR, 'signals')
PERFORMANCE_FILE = os.path.join(DATA_DIR, 'performance_metrics.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'ceo_settings.json')

# Helper Functions
def get_performance_data():
    """Retrieve or generate performance metrics for the dashboard"""
    try:
        if os.path.exists(PERFORMANCE_FILE):
            with open(PERFORMANCE_FILE, 'r') as f:
                return json.load(f)
        else:
            # Generate mock data if file doesn't exist
            return generate_mock_performance()
    except Exception as e:
        logger.error(f"Error retrieving performance data: {str(e)}")
        return generate_mock_performance()

def generate_mock_performance():
    """Generate mock performance data for testing"""
    return {
        "dailyPnL": round(random.uniform(-5.0, 8.0), 2),
        "weeklyPnL": round(random.uniform(-10.0, 15.0), 2),
        "monthlyPnL": round(random.uniform(-5.0, 25.0), 2),
        "winRate": random.randint(55, 78),
        "totalTrades": random.randint(15, 50),
        "avgWin": round(random.uniform(3.0, 8.0), 2),
        "avgLoss": round(random.uniform(-4.0, -1.5), 2),
        "biggestWin": round(random.uniform(10.0, 20.0), 2),
        "biggestLoss": round(random.uniform(-10.0, -3.0), 2)
    }

def get_trade_setups():
    """Get current trade setups from signals files or generate mock data"""
    try:
        setups = []
        
        # Check for buy signals
        buy_signal_path = os.path.join(DATA_DIR, 'buy_signals.csv')
        if os.path.exists(buy_signal_path):
            buy_df = pd.read_csv(buy_signal_path)
            if not buy_df.empty:
                for i, row in buy_df.head(3).iterrows():
                    timestamp = row.get('time', row.get('date', datetime.now().isoformat()))
                    setups.append({
                        "id": f"setup_buy_{i}",
                        "symbol": row['symbol'],
                        "type": "CALL",
                        "strategy": "AI Signal Generator",
                        "price": float(row.get('close', 0.0)),
                        "confidence": float(row.get('signal_score', 0.0)) / 100 if 'signal_score' in row else random.uniform(0.65, 0.95),
                        "recommendation": f"BUY {row['symbol']} CALL",
                        "expiration": "0DTE" if random.random() > 0.3 else "3DTE",
                        "timestamp": timestamp
                    })
        
        # Check for short signals
        short_signal_path = os.path.join(DATA_DIR, 'short_signals.csv')
        if os.path.exists(short_signal_path):
            short_df = pd.read_csv(short_signal_path)
            if not short_df.empty:
                for i, row in short_df.head(2).iterrows():
                    timestamp = row.get('time', row.get('date', datetime.now().isoformat()))
                    setups.append({
                        "id": f"setup_short_{i}",
                        "symbol": row['symbol'],
                        "type": "PUT",
                        "strategy": "AI Signal Generator",
                        "price": float(row.get('close', 0.0)),
                        "confidence": float(row.get('signal_score', 0.0)) / 100 if 'signal_score' in row else random.uniform(0.65, 0.95),
                        "recommendation": f"BUY {row['symbol']} PUT",
                        "expiration": "0DTE" if random.random() > 0.3 else "3DTE",
                        "timestamp": timestamp
                    })
        
        # If we don't have enough real setups, add some mock ones
        if len(setups) < 3:
            mock_setups = generate_mock_setups(3 - len(setups))
            setups.extend(mock_setups)
            
        return sorted(setups, key=lambda x: x['confidence'], reverse=True)
    except Exception as e:
        logger.error(f"Error retrieving trade setups: {str(e)}")
        return generate_mock_setups(3)

def generate_mock_setups(count=3):
    """Generate mock trade setups for testing"""
    symbols = ['SPX', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'AMZN']
    strategies = ['0DTE Momentum', '0DTE Reversal', 'Pre-Market Gap & Go', 'Support/Resistance Break']
    expirations = ['0DTE', '1DTE', '3DTE']
    
    setups = []
    for i in range(count):
        symbol = random.choice(symbols)
        type_opt = random.choice(['CALL', 'PUT'])
        confidence = random.uniform(0.65, 0.95)
        price = round(random.uniform(100, 500), 2)
        strategy = random.choice(strategies)
        expiration = random.choice(expirations)
        
        setups.append({
            "id": f"setup_mock_{i}",
            "symbol": symbol,
            "type": type_opt,
            "strategy": strategy,
            "price": price,
            "confidence": confidence,
            "recommendation": f"BUY {symbol} {type_opt} @ {price}",
            "expiration": expiration,
            "timestamp": datetime.now().isoformat()
        })
    
    return setups

def get_system_health():
    """Check the health of various system components"""
    try:
        # In a real implementation, you would check actual component statuses
        components = {
            "dataFetcher": {
                "status": "operational" if random.random() > 0.1 else "error",
                "latency": random.randint(80, 200)
            },
            "signalGenerator": {
                "status": "operational" if random.random() > 0.1 else "error",
                "latency": random.randint(300, 600)
            },
            "riskManager": {
                "status": "operational" if random.random() > 0.1 else "error",
                "latency": random.randint(50, 120)
            },
            "executionEngine": {
                "status": "operational" if random.random() > 0.1 else "error",
                "latency": random.randint(150, 300)
            }
        }
        
        return {
            "components": components,
            "lastUpdated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking system health: {str(e)}")
        return {
            "components": {
                "dataFetcher": {"status": "unknown", "latency": 0},
                "signalGenerator": {"status": "unknown", "latency": 0},
                "riskManager": {"status": "unknown", "latency": 0},
                "executionEngine": {"status": "unknown", "latency": 0}
            },
            "lastUpdated": datetime.now().isoformat()
        }

def get_risk_status():
    """Get current risk status metrics"""
    try:
        # Calculate exposure based on open positions or mock data
        current_exposure = random.randint(20, 60)
        
        # Determine market condition
        market_conditions = ['Bullish', 'Bearish', 'Neutral']
        market_condition = random.choice(market_conditions)
        
        # Determine risk level based on exposure and market condition
        risk_level = 'High' if current_exposure > 60 else 'Moderate' if current_exposure > 30 else 'Low'
        
        # Generate warning message if risk is high
        warning_message = None
        if risk_level == 'High':
            warning_message = "Current exposure exceeds recommended limits. Consider reducing position sizes."
        
        return {
            "currentExposure": current_exposure,
            "maxExposure": 80,
            "dailyPnLRisk": round(random.uniform(5, 25), 1),
            "marketCondition": market_condition,
            "volatilityLevel": random.choice(['Low', 'Moderate', 'High']),
            "riskLevel": risk_level,
            "warningMessage": warning_message
        }
    except Exception as e:
        logger.error(f"Error getting risk status: {str(e)}")
        return {
            "currentExposure": 30,
            "maxExposure": 80,
            "dailyPnLRisk": 15,
            "marketCondition": "Neutral",
            "volatilityLevel": "Moderate",
            "riskLevel": "Moderate",
            "warningMessage": None
        }

def get_settings():
    """Retrieve user settings from file or defaults"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        else:
            default_settings = {
                "autoTrading": False,
                "riskLevel": "moderate",
                "maxDailyTrades": 5,
                "stopLossPercent": 2.0,
                "odteOnly": True
            }
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(default_settings, f)
            return default_settings
    except Exception as e:
        logger.error(f"Error retrieving settings: {str(e)}")
        return {
            "autoTrading": False,
            "riskLevel": "moderate",
            "maxDailyTrades": 5,
            "stopLossPercent": 2.0,
            "odteOnly": True
        }

def save_settings(settings):
    """Save user settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
        return True
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return False

# Make sure we have an existing directory for data
if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
        logger.info(f"Created data directory at {DATA_DIR}")
    except Exception as e:
        logger.error(f"Failed to create data directory: {e}")

# Make sure we have a signals directory
if not os.path.exists(SIGNALS_DIR):
    try:
        os.makedirs(SIGNALS_DIR)
        logger.info(f"Created signals directory at {SIGNALS_DIR}")
    except Exception as e:
        logger.error(f"Failed to create signals directory: {e}")

# Routes
@ceo_dashboard_bp.route('/api/ceo-dashboard', methods=['GET', 'OPTIONS'])
@ceo_dashboard_bp.route('/ceo-dashboard', methods=['GET', 'OPTIONS'])
def get_dashboard():
    """Get all CEO dashboard data in a single request"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response(''))
    
    try:
        # Get all required data
        performance = get_performance_data()
        trade_setups = get_trade_setups()
        risk_status = get_risk_status()
        system_health = get_system_health()
        
        response_data = {
            "success": True,
            "performance": performance,
            "tradeSetups": trade_setups,
            "riskStatus": risk_status,
            "systemHealth": system_health
        }
        
        response = make_response(jsonify(response_data))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error in dashboard API: {str(e)}\n{traceback.format_exc()}")
        error_response = {
            "success": False,
            "error": "Failed to retrieve dashboard data",
            "details": str(e)
        }
        response = make_response(jsonify(error_response), 500)
        return add_cors_headers(response)

@ceo_dashboard_bp.route('/api/ceo-settings', methods=['GET', 'POST', 'OPTIONS'])
@ceo_dashboard_bp.route('/ceo-settings', methods=['GET', 'POST', 'OPTIONS'])
def manage_settings():
    """Get or update CEO dashboard settings"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response(''))
    
    try:
        if request.method == 'GET':
            settings = get_settings()
            response = make_response(jsonify({
                "success": True,
                "settings": settings
            }))
            return add_cors_headers(response)
        
        elif request.method == 'POST':
            new_settings = request.json
            if not new_settings:
                response = make_response(jsonify({
                    "success": False,
                    "error": "No settings provided"
                }), 400)
                return add_cors_headers(response)
            
            # Validate settings
            valid_keys = ["autoTrading", "riskLevel", "maxDailyTrades", "stopLossPercent", "odteOnly"]
            current_settings = get_settings()
            
            # Update only provided settings
            for key in valid_keys:
                if key in new_settings:
                    current_settings[key] = new_settings[key]
            
            save_result = save_settings(current_settings)
            
            if save_result:
                response = make_response(jsonify({
                    "success": True,
                    "settings": current_settings,
                    "message": "Settings updated successfully"
                }))
                return add_cors_headers(response)
            else:
                response = make_response(jsonify({
                    "success": False,
                    "error": "Failed to save settings"
                }), 500)
                return add_cors_headers(response)
    
    except Exception as e:
        logger.error(f"Error managing settings: {str(e)}\n{traceback.format_exc()}")
        error_response = {
            "success": False,
            "error": "Failed to manage settings",
            "details": str(e)
        }
        response = make_response(jsonify(error_response), 500)
        return add_cors_headers(response)

@ceo_dashboard_bp.route('/api/approve-trade-setup', methods=['POST', 'OPTIONS'])
@ceo_dashboard_bp.route('/approve-trade-setup', methods=['POST', 'OPTIONS'])
def approve_trade_setup():
    """Approve a trade setup for execution"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response(''))
    
    try:
        setup_data = request.json
        if not setup_data or 'setupId' not in setup_data:
            response = make_response(jsonify({
                "success": False,
                "error": "No setup ID provided"
            }), 400)
            return add_cors_headers(response)
        
        # In a real implementation, you would forward this to the execution engine
        # For now, we'll just acknowledge receipt
        logger.info(f"Trade setup approved: {setup_data['setupId']}")
        
        response = make_response(jsonify({
            "success": True,
            "message": f"Trade setup {setup_data['setupId']} approved for execution",
            "executionId": f"exec_{random.randint(1000, 9999)}"
        }))
        return add_cors_headers(response)
    
    except Exception as e:
        logger.error(f"Error approving trade: {str(e)}\n{traceback.format_exc()}")
        error_response = {
            "success": False,
            "error": "Failed to approve trade",
            "details": str(e)
        }
        response = make_response(jsonify(error_response), 500)
        return add_cors_headers(response)

@ceo_dashboard_bp.route('/api/reject-trade-setup', methods=['POST', 'OPTIONS'])
@ceo_dashboard_bp.route('/reject-trade-setup', methods=['POST', 'OPTIONS'])
def reject_trade_setup():
    """Reject a trade setup"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response(''))
    
    try:
        setup_data = request.json
        if not setup_data or 'setupId' not in setup_data:
            response = make_response(jsonify({
                "success": False,
                "error": "No setup ID provided"
            }), 400)
            return add_cors_headers(response)
        
        # In a real implementation, you would mark this in your database
        logger.info(f"Trade setup rejected: {setup_data['setupId']}")
        
        response = make_response(jsonify({
            "success": True,
            "message": f"Trade setup {setup_data['setupId']} rejected"
        }))
        return add_cors_headers(response)
    
    except Exception as e:
        logger.error(f"Error rejecting trade: {str(e)}\n{traceback.format_exc()}")
        error_response = {
            "success": False,
            "error": "Failed to reject trade",
            "details": str(e)
        }
        response = make_response(jsonify(error_response), 500)
        return add_cors_headers(response)

def register_routes(app):
    """
    Register CEO dashboard routes with the Flask app
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(ceo_dashboard_bp)
    logger.info("Successfully registered CEO dashboard routes") 