"""
Execution Model API Routes

API endpoints for the execution model component
"""

from flask import Blueprint, jsonify, request
import logging
from datetime import datetime, timedelta
import random
import json

logger = logging.getLogger(__name__)

# Import execution model components
try:
    from execution_model.risk_manager import RiskManager
    from execution_model.config import get_config, update_config
    REAL_RISK_MANAGER = True
except ImportError:
    logger.warning("Could not import real risk manager, using mock implementation")
    REAL_RISK_MANAGER = False
    
    # Create mock risk manager
    class MockRiskManager:
        def __init__(self):
            self.enabled = True
        
        def get_risk_metrics(self):
            return {
                "max_position_size": 1000,
                "max_daily_loss": 500,
                "max_open_positions": 5,
                "risk_per_trade": 2.0,
                "stop_loss_percent": 2.0,
                "take_profit_percent": 5.0
            }

# Initialize risk manager
risk_manager = RiskManager() if REAL_RISK_MANAGER else MockRiskManager()

def register_routes(app):
    """
    Register execution model routes with the Flask app
    
    Args:
        app: Flask application instance
    """
    bp = Blueprint('execution_model', __name__, url_prefix='/api/execution')
    
    @bp.route('/status', methods=['GET'])
    def get_status():
        """Get execution model status"""
        try:
            status = {
                "enabled": True,
                "mode": "simulated",
                "last_updated": datetime.now().isoformat(),
                "risk_management": {
                    "enabled": risk_manager.enabled if hasattr(risk_manager, 'enabled') else True,
                    "metrics": risk_manager.get_risk_metrics() if hasattr(risk_manager, 'get_risk_metrics') else {}
                }
            }
            
            return jsonify({
                'success': True,
                'status': status
            })
        except Exception as e:
            logger.error(f"Error getting execution model status: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/cooldown', methods=['GET'])
    def get_cooldown():
        """Get trade cooldown status"""
        try:
            now = datetime.now()
            
            # Mock cooldown status
            cooldown_status = {
                "cooldown_enabled": True,
                "hourly_trade_count": random.randint(0, 3),
                "max_trades_per_hour": 3,
                "daily_trade_count": random.randint(0, 10),
                "max_trades_per_day": 10,
                "next_available_trade_time": (now + timedelta(minutes=random.randint(0, 15))).isoformat(),
                "cooldown_minutes": 15,
                "cooldown_remaining_minutes": random.randint(0, 15),
                "cooldown_active": random.choice([True, False])
            }
            
            return jsonify({
                'success': True,
                'cooldown': cooldown_status
            })
        except Exception as e:
            logger.error(f"Error getting cooldown status: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/config', methods=['GET'])
    def get_execution_config():
        """Get execution model configuration"""
        try:
            config = {
                "execution": {
                    "enabled": True,
                    "mode": "simulated",
                    "allow_premarket": False,
                    "allow_afterhours": False
                },
                "risk_management": {
                    "enabled": True,
                    "max_position_size": 1000,
                    "risk_per_trade": 2.0
                },
                "trade_cooldown": {
                    "enabled": True,
                    "cooldown_minutes": 15,
                    "max_trades_per_hour": 3,
                    "max_trades_per_day": 10
                }
            }
            
            return jsonify({
                'success': True,
                'config': config
            })
        except Exception as e:
            logger.error(f"Error getting execution config: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Register the blueprint
    app.register_blueprint(bp)
    logger.info("Registered execution model routes") 