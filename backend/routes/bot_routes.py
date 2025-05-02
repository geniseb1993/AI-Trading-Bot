from flask import Blueprint, jsonify, request
from datetime import datetime
import logging
from typing import Dict, Any, Optional

from ..broker_integration.alpaca_broker import AlpacaBroker
from ..execution_model.institutional_flow import InstitutionalFlowAnalyzer
from ..execution_model.rsi_strategy import RSIStrategy
from ..dual_bot.dual_bot_manager import DualBotManager
from ..config import bot_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot_routes = Blueprint('bot_routes', __name__)

# Create dictionary-like config object for InstitutionalFlowAnalyzer
flow_config = {
    "institutional_flow": {
        "unusual_options_weight": 0.7,
        "dark_pool_weight": 0.8,
        "min_flow_signal": 0.6,
        "correlation_window": 20
    }
}

# Initialize components
alpaca_broker = AlpacaBroker()
institutional_flow = InstitutionalFlowAnalyzer(config=flow_config)
rsi_strategy = RSIStrategy()
dual_bot = DualBotManager()

@bot_routes.route('/status', methods=['GET'])
def get_bot_status() -> Dict[str, Any]:
    """Get status of all bots"""
    try:
        # Get status for each bot, handling potential errors individually
        autonomous_status = {}
        rsi_status = {}
        dual_status = {}
        
        try:
            autonomous_status = {
                'status': alpaca_broker.get_bot_status(),
                'last_update': datetime.now().isoformat(),
                'active_trades': alpaca_broker.get_active_trades()
            }
        except Exception as e:
            logger.error(f"Error getting autonomous bot status: {str(e)}")
            autonomous_status = {
                'status': False,
                'last_update': datetime.now().isoformat(),
                'active_trades': [],
                'error': str(e)
            }
            
        try:
            rsi_status = {
                'status': rsi_strategy.get_status(),
                'last_update': datetime.now().isoformat(),
                'active_signals': rsi_strategy.get_active_signals()
            }
        except Exception as e:
            logger.error(f"Error getting RSI bot status: {str(e)}")
            rsi_status = {
                'status': False,
                'last_update': datetime.now().isoformat(),
                'active_signals': [],
                'error': str(e)
            }
            
        try:
            dual_status = {
                'status': dual_bot.is_running,
                'last_update': datetime.now().isoformat(),
                'active_positions': dual_bot.get_active_positions()
            }
        except Exception as e:
            logger.error(f"Error getting dual bot status: {str(e)}")
            dual_status = {
                'status': False,
                'last_update': datetime.now().isoformat(),
                'active_positions': [],
                'error': str(e)
            }
        
        return jsonify({
            'autonomous_bot': autonomous_status,
            'rsi_bot': rsi_status,
            'dual_bot': dual_status
        }), 200
    except Exception as e:
        logger.error(f"Error getting bot status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bot_routes.route('/start/<bot_type>', methods=['POST'])
def start_bot(bot_type: str) -> Dict[str, Any]:
    """Start specified bot"""
    try:
        if bot_type == 'autonomous':
            success = alpaca_broker.start_bot()
        elif bot_type == 'rsi':
            success = rsi_strategy.start()
        elif bot_type == 'dual':
            success = dual_bot.start()
        else:
            return jsonify({'error': 'Invalid bot type'}), 400

        if success:
            logger.info(f"Successfully started {bot_type} bot")
            return jsonify({'status': 'success', 'message': f'{bot_type} bot started'}), 200
        else:
            return jsonify({'error': f'Failed to start {bot_type} bot'}), 500

    except Exception as e:
        logger.error(f"Error starting {bot_type} bot: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bot_routes.route('/stop/<bot_type>', methods=['POST'])
def stop_bot(bot_type: str) -> Dict[str, Any]:
    """Stop specified bot"""
    try:
        if bot_type == 'autonomous':
            success = alpaca_broker.stop_bot()
        elif bot_type == 'rsi':
            success = rsi_strategy.stop()
        elif bot_type == 'dual':
            success = dual_bot.stop()
        else:
            return jsonify({'error': 'Invalid bot type'}), 400

        if success:
            logger.info(f"Successfully stopped {bot_type} bot")
            return jsonify({'status': 'success', 'message': f'{bot_type} bot stopped'}), 200
        else:
            return jsonify({'error': f'Failed to stop {bot_type} bot'}), 500

    except Exception as e:
        logger.error(f"Error stopping {bot_type} bot: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bot_routes.route('/data/<bot_type>', methods=['GET'])
def get_bot_data(bot_type: str) -> Dict[str, Any]:
    """Get real-time data for specified bot"""
    try:
        if bot_type == 'autonomous':
            data = alpaca_broker.get_real_time_data()
        elif bot_type == 'rsi':
            data = rsi_strategy.get_current_data()
        elif bot_type == 'dual':
            data = dual_bot.get_current_data()
        else:
            return jsonify({'error': 'Invalid bot type'}), 400

        return jsonify(data), 200

    except Exception as e:
        logger.error(f"Error getting data for {bot_type} bot: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bot_routes.route('/connection-check', methods=['GET'])
def check_connection() -> Dict[str, Any]:
    """Check API connection status and verify bot components are available"""
    try:
        # Check if each bot component can be accessed
        autonomous_available = hasattr(alpaca_broker, 'get_bot_status')
        rsi_available = hasattr(rsi_strategy, 'get_status')
        dual_available = hasattr(dual_bot, 'is_running')
        
        # Return status of each component
        return jsonify({
            'status': 'connected',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'autonomous_bot': autonomous_available,
                'rsi_bot': rsi_available,
                'dual_bot': dual_available
            },
            'blueprint_url_prefix': '/api/bot'
        }), 200
    except Exception as e:
        logger.error(f"Error checking connection: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@bot_routes.route('/run-cycle/<bot_type>', methods=['POST'])
def run_trading_cycle(bot_type: str) -> Dict[str, Any]:
    """Run a trading cycle for a specific bot"""
    try:
        if bot_type == 'autonomous':
            success = alpaca_broker.run_trading_cycle()
        elif bot_type == 'rsi':
            success = rsi_strategy.run_trading_cycle()
        elif bot_type == 'dual':
            success = dual_bot.run_trading_cycle()
        else:
            return jsonify({'error': 'Invalid bot type'}), 400

        if success:
            logger.info(f"Successfully ran trading cycle for {bot_type} bot")
            return jsonify({
                'success': True, 
                'message': f'{bot_type} bot trading cycle executed successfully',
                'status': 'success'
            }), 200
        else:
            return jsonify({'success': False, 'error': f'Failed to run trading cycle for {bot_type} bot'}), 500

    except Exception as e:
        logger.error(f"Error running trading cycle for {bot_type} bot: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500 