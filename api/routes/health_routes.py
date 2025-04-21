from flask import Blueprint, jsonify
from datetime import datetime
import logging
import os
import sys
import platform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional dependency - we'll check if it's available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logger.warning("psutil module not found. Some health check features will be limited.")

health_routes = Blueprint('health_routes', __name__)

@health_routes.route('/', methods=['GET'])
def health_check():
    """Basic health check endpoint for the API"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'AI Trading Bot API',
            'timestamp': datetime.now().isoformat(),
            'environment': os.environ.get('FLASK_ENV', 'development')
        }), 200
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@health_routes.route('/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with system information"""
    try:
        # System info
        system_info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
        }
        
        # Add memory usage if psutil is available
        if HAS_PSUTIL:
            process = psutil.Process(os.getpid())
            memory_usage = process.memory_info().rss / 1024 / 1024  # in MB
            system_info['process_memory_usage_mb'] = round(memory_usage, 2)
        
        # Component status (very simple check that the imports work)
        component_status = {
            'flask': True,
            'psutil': HAS_PSUTIL
        }
        
        # Try to import some key components
        try:
            from ..broker_integration.alpaca_broker import AlpacaBroker
            component_status['alpaca_broker'] = True
        except:
            component_status['alpaca_broker'] = False
            
        try:
            from ..dual_bot.dual_bot_manager import DualBotManager
            component_status['dual_bot'] = True
        except:
            component_status['dual_bot'] = False
        
        try:
            from ..execution_model.rsi_strategy import RSIStrategy
            component_status['rsi_strategy'] = True
        except:
            component_status['rsi_strategy'] = False
        
        # Return detailed health check
        result = {
            'status': 'healthy',
            'service': 'AI Trading Bot API',
            'timestamp': datetime.now().isoformat(),
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'system': system_info,
            'components': component_status
        }
        
        # Add uptime if psutil is available
        if HAS_PSUTIL:
            result['uptime'] = psutil.boot_time()
            
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in detailed health check: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@health_routes.route('/ping', methods=['GET'])
def ping():
    """Simple ping endpoint for quick connectivity checks"""
    return jsonify({'ping': 'pong', 'timestamp': datetime.now().isoformat()}), 200 