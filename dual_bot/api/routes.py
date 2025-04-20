from flask import Blueprint, jsonify, request
import logging
from ..data.data_fetcher import DataFetcher
from ..ai.deepseek_scanner import DeepSeekScanner
from ..ai.chatgpt_risk_check import ChatGPTRiskManager
from ..execution.auto_closer import AutoCloser
from ..config.config_loader import load_config

# Create blueprint
api = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Load configuration
config = load_config()

# Initialize components
data_fetcher = DataFetcher()
data_fetcher.initialize()
data_fetcher.start()

deepseek_scanner = DeepSeekScanner(config)
chatgpt_risk_manager = ChatGPTRiskManager(config)
auto_closer = AutoCloser(config)

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

@api.route('/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    """Get market data for a symbol."""
    try:
        market_data = data_fetcher.get_market_data(symbol)
        return jsonify(market_data)
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/options-data/<symbol>', methods=['GET'])
def get_options_data(symbol):
    """Get options data for a symbol."""
    try:
        options_data = data_fetcher.get_options_data(symbol)
        return jsonify(options_data)
    except Exception as e:
        logger.error(f"Error fetching options data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/news/<symbol>', methods=['GET'])
def get_news(symbol):
    """Get news for a symbol."""
    try:
        news = data_fetcher.get_news(symbol)
        return jsonify(news)
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/scan', methods=['POST'])
def scan_trades():
    """Scan for trade recommendations."""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        recommendations = deepseek_scanner.generate_recommendations(symbol)
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error scanning trades: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/assess-risk', methods=['POST'])
def assess_risk():
    """Assess risk for a trade recommendation."""
    try:
        data = request.get_json()
        recommendation = data.get('recommendation')
        market_context = data.get('market_context')
        
        if not recommendation or not market_context:
            return jsonify({'error': 'Recommendation and market context are required'}), 400
        
        assessment = chatgpt_risk_manager.assess_trade(recommendation, market_context)
        return jsonify(assessment)
    except Exception as e:
        logger.error(f"Error assessing risk: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/check-position', methods=['POST'])
def check_position():
    """Check if a position should be closed."""
    try:
        data = request.get_json()
        position = data.get('position')
        market_data = data.get('market_data')
        
        if not position or not market_data:
            return jsonify({'error': 'Position and market data are required'}), 400
        
        should_close = auto_closer.should_close_position(position, market_data)
        return jsonify({'should_close': should_close})
    except Exception as e:
        logger.error(f"Error checking position: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/config', methods=['GET'])
def get_config():
    """Get the current configuration."""
    try:
        return jsonify(config)
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        return jsonify({'error': str(e)}), 500 