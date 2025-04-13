from flask import Blueprint, jsonify, request
import logging
from typing import Dict, Any

from .auto_trade import AutoTrader
from .broker_manager import BrokerManager

logger = logging.getLogger(__name__)

# Initialize broker manager
broker_manager = BrokerManager()

# Initialize auto trader
auto_trader = AutoTrader(broker_manager)

# Create Blueprint
auto_trade_bp = Blueprint('auto_trade', __name__, url_prefix='/api/auto-trade')

@auto_trade_bp.route('/status', methods=['GET'])
def get_status():
    """Get current status of the auto trader system"""
    try:
        status = auto_trader.get_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting auto trader status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auto_trade_bp.route('/start', methods=['POST'])
def start_auto_trader():
    """Start the auto trader monitoring system"""
    try:
        if auto_trader.running:
            return jsonify({
                'success': True,
                'message': 'Auto trader is already running'
            })
        
        auto_trader.start()
        return jsonify({
            'success': True,
            'message': 'Auto trader started successfully'
        })
    except Exception as e:
        logger.error(f"Error starting auto trader: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auto_trade_bp.route('/stop', methods=['POST'])
def stop_auto_trader():
    """Stop the auto trader monitoring system"""
    try:
        if not auto_trader.running:
            return jsonify({
                'success': True,
                'message': 'Auto trader is not running'
            })
        
        auto_trader.stop()
        return jsonify({
            'success': True,
            'message': 'Auto trader stopped successfully'
        })
    except Exception as e:
        logger.error(f"Error stopping auto trader: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auto_trade_bp.route('/config', methods=['GET'])
def get_config():
    """Get current auto trader configuration"""
    try:
        status = auto_trader.get_status()
        return jsonify({
            'success': True,
            'config': status['config']
        })
    except Exception as e:
        logger.error(f"Error getting auto trader config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auto_trade_bp.route('/config', methods=['PUT'])
def update_config():
    """Update auto trader configuration"""
    try:
        config = request.json
        if not config:
            return jsonify({
                'success': False,
                'error': 'No configuration provided'
            }), 400
        
        success = auto_trader.update_config(config)
        if success:
            return jsonify({
                'success': True,
                'message': 'Configuration updated successfully',
                'config': auto_trader.config
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update configuration'
            }), 500
    except Exception as e:
        logger.error(f"Error updating auto trader config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auto_trade_bp.route('/enable', methods=['POST'])
def enable_auto_trader():
    """Enable auto trading"""
    try:
        success = auto_trader.update_config({'enabled': True})
        if success:
            # Ensure the system is running
            if not auto_trader.running:
                auto_trader.start()
            
            return jsonify({
                'success': True,
                'message': 'Auto trading enabled'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to enable auto trading'
            }), 500
    except Exception as e:
        logger.error(f"Error enabling auto trader: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auto_trade_bp.route('/disable', methods=['POST'])
def disable_auto_trader():
    """Disable auto trading"""
    try:
        success = auto_trader.update_config({'enabled': False})
        if success:
            return jsonify({
                'success': True,
                'message': 'Auto trading disabled'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to disable auto trading'
            }), 500
    except Exception as e:
        logger.error(f"Error disabling auto trader: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auto_trade_bp.route('/signal', methods=['POST'])
def submit_signal():
    """Submit a trading signal for processing"""
    try:
        signal_data = request.json
        if not signal_data:
            return jsonify({
                'success': False,
                'error': 'No signal data provided'
            }), 400
        
        # Validate basic signal structure
        required_fields = ['symbol', 'position_type', 'entry_price']
        missing_fields = [field for field in required_fields if field not in signal_data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Add signal to queue
        success = auto_trader.add_signal(signal_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Signal for {signal_data["symbol"]} added to queue'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add signal to queue'
            }), 500
    except Exception as e:
        logger.error(f"Error submitting signal: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auto_trade_bp.route('/history', methods=['GET'])
def get_trade_history():
    """Get auto trader trade history"""
    try:
        limit = request.args.get('limit', 20, type=int)
        history = auto_trader.get_trade_history(limit=limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
    except Exception as e:
        logger.error(f"Error getting trade history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auto_trade_bp.route('/queue', methods=['GET'])
def get_signal_queue():
    """Get current signal queue size"""
    try:
        status = auto_trader.get_status()
        
        return jsonify({
            'success': True,
            'queue_size': status.get('signals_in_queue', 0)
        })
    except Exception as e:
        logger.error(f"Error getting signal queue: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_routes(app):
    """
    Register all auto trader routes with the Flask app
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(auto_trade_bp)
    logger.info("Registered auto trade routes") 