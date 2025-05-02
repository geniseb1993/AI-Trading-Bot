from flask import Blueprint, jsonify, request, make_response
import logging
from datetime import datetime
import pandas as pd
import os
import sys
import importlib.util

# Add parent directory to path to import from main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import CORS utils
from backend.utils.cors_utils import add_cors_headers

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
dual_bot_bp = Blueprint('dual_bot', __name__, url_prefix='/api/dual-bot')

def load_signals():
    """Load signals from CSV files"""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        buy_file = os.path.join(data_dir, 'buy_signals.csv')
        short_file = os.path.join(data_dir, 'short_signals.csv')
        
        buy_signals = pd.read_csv(buy_file) if os.path.exists(buy_file) else pd.DataFrame()
        short_signals = pd.read_csv(short_file) if os.path.exists(short_file) else pd.DataFrame()
        
        # Check if the date column exists, use 'time' if it doesn't
        if not buy_signals.empty and 'date' not in buy_signals.columns and 'time' in buy_signals.columns:
            buy_signals = buy_signals.rename(columns={'time': 'date'})
        
        if not short_signals.empty and 'date' not in short_signals.columns and 'time' in short_signals.columns:
            short_signals = short_signals.rename(columns={'time': 'date'})
        
        return buy_signals, short_signals
    except Exception as e:
        logger.error(f"Error loading signals: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

@dual_bot_bp.route('/status', methods=['GET', 'OPTIONS'])
def get_status():
    """Get the current status of the dual bot system"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
        
    try:
        buy_signals, short_signals = load_signals()
        
        # Calculate actual performance metrics
        total_signals = len(buy_signals) + len(short_signals)
        
        status = {
            'running': True,
            'last_updated': datetime.now().isoformat(),
            'components': {
                'data_fetcher': True,
                'signal_generator': True,
                'risk_manager': True,
                'execution_engine': True
            },
            'performance': {
                'total_signals': total_signals,
                'buy_signals': len(buy_signals),
                'short_signals': len(short_signals),
                'last_update': buy_signals['date'].max() if not buy_signals.empty else None
            }
        }
        
        response = make_response(jsonify({
            'success': True,
            'status': status
        }))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error getting dual bot status: {str(e)}")
        response = make_response(jsonify({
            'success': False,
            'error': str(e)
        }), 500)
        return add_cors_headers(response)

@dual_bot_bp.route('/signals', methods=['GET', 'OPTIONS'])
def get_signals():
    """Get current trading signals from the dual bot system"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
        
    try:
        buy_signals, short_signals = load_signals()
        
        # Convert signals to the expected format
        formatted_signals = []
        
        # Process buy signals
        if not buy_signals.empty:
            for _, signal in buy_signals.iterrows():
                formatted_signals.append({
                    'symbol': signal['symbol'],
                    'type': 'BUY',
                    'confidence': abs(signal['signal_score']) / 10,  # Convert to 0-1 range
                    'price_target': signal['close'] * 1.05,  # 5% target
                    'stop_loss': signal['close'] * 0.95,     # 5% stop loss
                    'timeframe': '1D',
                    'signal_score': signal['signal_score'],
                    'ema_9': signal['ema_9'],
                    'ema_21': signal['ema_21'],
                    'volume': signal['volume']
                })
        
        # Process short signals
        if not short_signals.empty:
            for _, signal in short_signals.iterrows():
                formatted_signals.append({
                    'symbol': signal['symbol'],
                    'type': 'SELL',
                    'confidence': abs(signal['signal_score']) / 10,  # Convert to 0-1 range
                    'price_target': signal['close'] * 0.95,  # 5% target
                    'stop_loss': signal['close'] * 1.05,     # 5% stop loss
                    'timeframe': '1D',
                    'signal_score': signal['signal_score'],
                    'ema_9': signal['ema_9'],
                    'ema_21': signal['ema_21'],
                    'volume': signal['volume']
                })
        
        response_data = {
            'timestamp': datetime.now().isoformat(),
            'signals': formatted_signals
        }
        
        response = make_response(jsonify({
            'success': True,
            'signals': response_data
        }))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error getting dual bot signals: {str(e)}")
        response = make_response(jsonify({
            'success': False,
            'error': str(e)
        }), 500)
        return add_cors_headers(response)

@dual_bot_bp.route('/generate-signals', methods=['POST', 'OPTIONS'])
def generate_signals():
    """Generate new trading signals for the dual bot system"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
        
    try:
        # Import the signal generation function from app-starter.py
        # Get the path to app-starter.py
        app_starter_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'app-starter.py')
        
        # Load the module
        spec = importlib.util.spec_from_file_location("app_starter", app_starter_path)
        app_starter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_starter)
        
        # Call the generate_signals function
        result = app_starter.generate_signals()
        
        # Load the newly generated signals
        buy_signals, short_signals = load_signals()
        
        # Return the paths to the generated signal files
        response = make_response(jsonify({
            'success': True,
            'message': 'Signals generated successfully',
            'buy_signals_file': os.path.join(os.getcwd(), 'data', 'buy_signals.csv'),
            'short_signals_file': os.path.join(os.getcwd(), 'data', 'short_signals.csv'),
            'buy_signals_count': len(buy_signals),
            'short_signals_count': len(short_signals)
        }))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        response = make_response(jsonify({
            'success': False,
            'error': str(e)
        }), 500)
        return add_cors_headers(response) 