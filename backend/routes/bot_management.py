from flask import Blueprint, jsonify, request
import logging
import random
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint for bot management
bot_bp = Blueprint('bot_management', __name__, url_prefix='/api/bot')

# Store bot state
bot_status = {
    'active': False,
    'running_since': None,
    'mode': 'manual',
    'trading_pairs': ['SPY', 'QQQ', 'AAPL', 'MSFT'],
    'performance': {
        'trades_executed': 0,
        'profit_loss': 0.0,
        'win_rate': 0.0
    },
    'last_action': None,
    'next_scheduled_action': None,
    'system_health': 'normal'
}

@bot_bp.route('/status', methods=['GET'])
def get_bot_status():
    """Get the current status of the trading bot"""
    try:
        global bot_status
        
        # Add some dynamic data for demonstration
        if bot_status['active']:
            trades = random.randint(1, 5)
            bot_status['performance']['trades_executed'] += trades
            profit = random.uniform(-2.5, 3.5) * trades
            bot_status['performance']['profit_loss'] += profit
            
            if bot_status['performance']['trades_executed'] > 0:
                # Calculate win rate based on simulated trade outcomes
                wins = bot_status['performance']['trades_executed'] * (0.5 + random.uniform(-0.1, 0.2))
                bot_status['performance']['win_rate'] = round(wins / bot_status['performance']['trades_executed'] * 100, 1)
            
            # Update last action time
            bot_status['last_action'] = (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat()
            
            # Set next scheduled action
            bot_status['next_scheduled_action'] = (datetime.now() + timedelta(minutes=random.randint(5, 30))).isoformat()
        
        return jsonify({
            'success': True,
            'status': bot_status
        })
    except Exception as e:
        logger.error(f"Error getting bot status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_bp.route('/toggle', methods=['POST'])
def toggle_bot():
    """Toggle the bot's active state"""
    try:
        global bot_status
        
        # Toggle the active state
        bot_status['active'] = not bot_status['active']
        
        # Update running_since if bot is activated
        if bot_status['active']:
            bot_status['running_since'] = datetime.now().isoformat()
            bot_status['system_health'] = 'normal'
        else:
            bot_status['running_since'] = None
        
        return jsonify({
            'success': True,
            'status': bot_status
        })
    except Exception as e:
        logger.error(f"Error toggling bot: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_bp.route('/update-settings', methods=['POST'])
def update_bot_settings():
    """Update the bot's settings"""
    try:
        global bot_status
        
        # Get settings from request
        settings = request.json
        
        # Update settings
        if 'mode' in settings:
            bot_status['mode'] = settings['mode']
        
        if 'trading_pairs' in settings:
            bot_status['trading_pairs'] = settings['trading_pairs']
        
        return jsonify({
            'success': True,
            'status': bot_status
        })
    except Exception as e:
        logger.error(f"Error updating bot settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bot_bp.route('/recent-actions', methods=['GET'])
def get_recent_actions():
    """Get the bot's recent actions"""
    try:
        # Generate mock recent actions
        recent_actions = []
        
        for i in range(10):
            action_time = datetime.now() - timedelta(minutes=i*15)
            action_type = random.choice(['scan', 'analysis', 'trade', 'status_check'])
            
            action = {
                'id': 1000 + i,
                'timestamp': action_time.isoformat(),
                'type': action_type,
                'description': f"Bot performed {action_type} operation"
            }
            
            if action_type == 'trade':
                symbol = random.choice(['SPY', 'QQQ', 'AAPL', 'MSFT'])
                direction = random.choice(['buy', 'sell'])
                action['details'] = {
                    'symbol': symbol,
                    'direction': direction,
                    'price': round(random.uniform(100, 500), 2),
                    'quantity': random.randint(1, 10),
                    'status': 'completed'
                }
            elif action_type == 'analysis':
                action['details'] = {
                    'symbols_analyzed': random.randint(3, 15),
                    'signals_generated': random.randint(0, 5)
                }
            
            recent_actions.append(action)
        
        return jsonify({
            'success': True,
            'actions': recent_actions
        })
    except Exception as e:
        logger.error(f"Error getting recent bot actions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_routes(app):
    """Register all bot management routes with the Flask app"""
    try:
        app.register_blueprint(bot_bp)
        logger.info("Bot management routes registered")
        return True
    except Exception as e:
        logger.error(f"Failed to register bot management routes: {str(e)}")
        return False 