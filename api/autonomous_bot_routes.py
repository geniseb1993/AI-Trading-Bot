"""
Autonomous Trading Bot API Routes.

This module implements API routes for managing and interacting with the autonomous trading bot.
"""

import logging
from flask import Blueprint, jsonify, request
from api.autonomous_bot_wrapper import get_bot_wrapper

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
autonomous_bot_bp = Blueprint('autonomous_bot', __name__)

@autonomous_bot_bp.route('/status', methods=['GET'])
def get_bot_status():
    """Get the current status of the autonomous trading bot."""
    try:
        bot_wrapper = get_bot_wrapper()
        status = bot_wrapper.get_bot_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"Error getting bot status: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Failed to get bot status: {str(e)}"
        }), 500

@autonomous_bot_bp.route('/start', methods=['POST'])
def start_bot():
    """Start the autonomous trading bot."""
    try:
        bot_wrapper = get_bot_wrapper()
        result = bot_wrapper.start_bot()
        return jsonify({
            'success': result['success'],
            'message': result['message']
        })
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Failed to start bot: {str(e)}"
        }), 500

@autonomous_bot_bp.route('/stop', methods=['POST'])
def stop_bot():
    """Stop the autonomous trading bot."""
    try:
        bot_wrapper = get_bot_wrapper()
        result = bot_wrapper.stop_bot()
        return jsonify({
            'success': result['success'],
            'message': result['message']
        })
    except Exception as e:
        logger.error(f"Error stopping bot: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Failed to stop bot: {str(e)}"
        }), 500

@autonomous_bot_bp.route('/run-cycle', methods=['POST'])
def run_trading_cycle():
    """Manually run a trading cycle."""
    try:
        bot_wrapper = get_bot_wrapper()
        result = bot_wrapper.run_trading_cycle()
        return jsonify({
            'success': result['success'],
            'message': result['message']
        })
    except Exception as e:
        logger.error(f"Error running trading cycle: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Failed to run trading cycle: {str(e)}"
        }), 500

@autonomous_bot_bp.route('/active-trades', methods=['GET'])
def get_active_trades():
    """Get all active trades made by the bot."""
    try:
        bot_wrapper = get_bot_wrapper()
        active_trades = bot_wrapper.get_active_trades()
        return jsonify({
            'success': True,
            'data': active_trades
        })
    except Exception as e:
        logger.error(f"Error getting active trades: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Failed to get active trades: {str(e)}"
        }), 500

@autonomous_bot_bp.route('/history', methods=['GET'])
def get_trading_history():
    """Get trading history."""
    try:
        limit = request.args.get('limit', type=int)
        bot_wrapper = get_bot_wrapper()
        history = bot_wrapper.get_trading_history(limit=limit)
        return jsonify({
            'success': True,
            'data': history
        })
    except Exception as e:
        logger.error(f"Error getting trading history: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Failed to get trading history: {str(e)}"
        }), 500

@autonomous_bot_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio information."""
    try:
        bot_wrapper = get_bot_wrapper()
        portfolio = bot_wrapper.get_portfolio_info()
        return jsonify({
            'success': True,
            'data': portfolio
        })
    except Exception as e:
        logger.error(f"Error getting portfolio info: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Failed to get portfolio info: {str(e)}"
        }), 500

@autonomous_bot_bp.route('/performance', methods=['GET'])
def get_portfolio_performance():
    """Get historical portfolio performance."""
    try:
        days = request.args.get('days', 30, type=int)
        bot_wrapper = get_bot_wrapper()
        performance = bot_wrapper.get_portfolio_performance(days=days)
        return jsonify({
            'success': True,
            'data': performance
        })
    except Exception as e:
        logger.error(f"Error getting portfolio performance: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Failed to get portfolio performance: {str(e)}"
        }), 500

def register_routes(app):
    """Register autonomous bot routes with Flask app."""
    app.register_blueprint(autonomous_bot_bp, url_prefix='/api/bot')
    logger.info("Registered autonomous bot routes") 