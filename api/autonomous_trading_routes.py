"""
API Routes for the Autonomous Trading Bot.

Provides endpoints to start, stop, and monitor the autonomous trading bot.
"""

from flask import Blueprint, jsonify, request
import logging
from autonomous_trading_bot import get_bot_instance

logger = logging.getLogger(__name__)

# Create a Flask Blueprint
autonomous_trading_bp = Blueprint('autonomous_trading', __name__, url_prefix='/api/autonomous-trading')

@autonomous_trading_bp.route('/status', methods=['GET'])
def get_bot_status():
    """Get the current status of the autonomous trading bot"""
    try:
        bot = get_bot_instance()
        status = bot.get_status()
        
        return jsonify({
            'success': True,
            'status': status,
            'message': 'Bot is running' if status['running'] else 'Bot is stopped'
        })
    except Exception as e:
        logger.error(f"Error getting bot status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@autonomous_trading_bp.route('/start', methods=['POST'])
def start_bot():
    """Start the autonomous trading bot"""
    try:
        bot = get_bot_instance()
        
        if bot.running:
            return jsonify({
                'success': True,
                'message': 'Bot is already running',
                'status': bot.get_status()
            })
        
        result = bot.start()
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Bot started successfully',
                'status': bot.get_status()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to start bot',
                'status': bot.get_status()
            }), 400
            
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@autonomous_trading_bp.route('/stop', methods=['POST'])
def stop_bot():
    """Stop the autonomous trading bot"""
    try:
        bot = get_bot_instance()
        
        if not bot.running:
            return jsonify({
                'success': True,
                'message': 'Bot is already stopped',
                'status': bot.get_status()
            })
        
        result = bot.stop()
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Bot stopped successfully',
                'status': bot.get_status()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to stop bot',
                'status': bot.get_status()
            }), 400
            
    except Exception as e:
        logger.error(f"Error stopping bot: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@autonomous_trading_bp.route('/run-cycle', methods=['POST'])
def run_trading_cycle():
    """Manually trigger a trading cycle"""
    try:
        bot = get_bot_instance()
        bot.run_trading_cycle()
        
        return jsonify({
            'success': True,
            'message': 'Trading cycle executed successfully',
            'status': bot.get_status()
        })
    except Exception as e:
        logger.error(f"Error running trading cycle: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@autonomous_trading_bp.route('/active-trades', methods=['GET'])
def get_active_trades():
    """Get the current active trades"""
    try:
        bot = get_bot_instance()
        
        return jsonify({
            'success': True,
            'active_trades': bot.active_trades,
            'count': len(bot.active_trades)
        })
    except Exception as e:
        logger.error(f"Error getting active trades: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@autonomous_trading_bp.route('/trading-history', methods=['GET'])
def get_trading_history():
    """Get the trading history"""
    try:
        bot = get_bot_instance()
        
        # Extract limit parameter with default of 20
        limit = request.args.get('limit', 20, type=int)
        
        # Get the most recent trades up to the limit
        recent_trades = bot.trading_history[-limit:] if bot.trading_history else []
        
        return jsonify({
            'success': True,
            'trading_history': recent_trades,
            'count': len(recent_trades),
            'total_trades': len(bot.trading_history)
        })
    except Exception as e:
        logger.error(f"Error getting trading history: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@autonomous_trading_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Get the current portfolio information"""
    try:
        bot = get_bot_instance()
        
        portfolio = {
            'portfolio_value': bot.portfolio_value,
            'cash_balance': bot.cash_balance,
            'equity_value': bot.equity_value,
            'active_positions': len(bot.active_trades)
        }
        
        return jsonify({
            'success': True,
            'portfolio': portfolio
        })
    except Exception as e:
        logger.error(f"Error getting portfolio: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_routes(app):
    """Register blueprint with Flask app"""
    app.register_blueprint(autonomous_trading_bp)
    logger.info("Successfully registered autonomous trading routes")
    
    # Add an auto-start feature if environment variable is set
    try:
        import os
        if os.environ.get('AUTO_START_TRADING_BOT', 'false').lower() == 'true':
            logger.info("AUTO_START_TRADING_BOT is set to true, starting bot...")
            bot = get_bot_instance()
            bot.start()
    except Exception as e:
        logger.error(f"Error auto-starting trading bot: {str(e)}") 