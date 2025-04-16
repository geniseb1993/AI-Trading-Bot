"""
Autonomous Bot API Routes

API endpoints for controlling the autonomous trading bot
"""

from flask import Blueprint, jsonify, request
import logging
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)

# Import the autonomous bot wrapper
try:
    from api.autonomous_bot_wrapper import AutonomousBotWrapper
    bot_wrapper = AutonomousBotWrapper()
    REAL_BOT = True
    logger.info("Successfully initialized autonomous bot wrapper")
except ImportError as e:
    logger.warning(f"Could not import real autonomous bot wrapper: {e}")
    REAL_BOT = False
    
    # Create mock bot wrapper
    class MockBotWrapper:
        def __init__(self):
            self.running = False
            self.last_cycle_time = None
            self.start_time = None
            
        def start(self):
            self.running = True
            self.start_time = datetime.now()
            logger.info("Mock bot started")
            return True
            
        def stop(self):
            self.running = False
            logger.info("Mock bot stopped")
            return True
            
        def run_trading_cycle(self):
            self.last_cycle_time = datetime.now()
            logger.info("Mock bot trading cycle executed")
            return {
                "success": True,
                "trades_analyzed": 5,
                "new_positions": 0,
                "positions_closed": 0
            }
            
        def get_status(self):
            return {
                "running": self.running,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "last_cycle_time": self.last_cycle_time.isoformat() if self.last_cycle_time else None,
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                "mode": "simulated"
            }
            
        def get_active_trades(self):
            return []
            
        def get_trading_history(self, limit=10):
            return []
    
    bot_wrapper = MockBotWrapper()
    logger.info("Using mock autonomous bot wrapper")

def register_routes(app):
    """
    Register autonomous bot routes with the Flask app
    
    Args:
        app: Flask application instance
    """
    bp = Blueprint('autonomous_bot', __name__, url_prefix='/api/bot')
    
    @bp.route('/status', methods=['GET'])
    def get_status():
        """Get bot status"""
        try:
            status = bot_wrapper.get_status()
            return jsonify({
                'success': True,
                'status': status
            })
        except Exception as e:
            logger.error(f"Error getting bot status: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/start', methods=['POST'])
    def start_bot():
        """Start the autonomous trading bot"""
        try:
            success = bot_wrapper.start()
            return jsonify({
                'success': success,
                'message': "Bot started successfully" if success else "Failed to start bot"
            })
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/stop', methods=['POST'])
    def stop_bot():
        """Stop the autonomous trading bot"""
        try:
            success = bot_wrapper.stop()
            return jsonify({
                'success': success,
                'message': "Bot stopped successfully" if success else "Failed to stop bot"
            })
        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/cycle', methods=['POST'])
    def run_cycle():
        """Run a single trading cycle"""
        try:
            result = bot_wrapper.run_trading_cycle()
            return jsonify({
                'success': True,
                'result': result
            })
        except Exception as e:
            logger.error(f"Error running trading cycle: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/trades/active', methods=['GET'])
    def get_active_trades():
        """Get active trades"""
        try:
            trades = bot_wrapper.get_active_trades()
            return jsonify({
                'success': True,
                'trades': trades
            })
        except Exception as e:
            logger.error(f"Error getting active trades: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @bp.route('/trades/history', methods=['GET'])
    def get_trade_history():
        """Get trade history"""
        try:
            limit = request.args.get('limit', 10, type=int)
            history = bot_wrapper.get_trading_history(limit=limit)
            return jsonify({
                'success': True,
                'history': history
            })
        except Exception as e:
            logger.error(f"Error getting trade history: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Register the blueprint
    app.register_blueprint(bp)
    logger.info("Registered autonomous bot routes") 