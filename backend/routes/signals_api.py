from flask import Blueprint, jsonify, request, make_response
import logging
import os
import pandas as pd
from datetime import datetime
import sys

# Add parent directory to path to import from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from routes.dual_bot_routes import load_signals, add_cors_headers

# Set up logging
logger = logging.getLogger(__name__)

# Create signals blueprint to handle traditional endpoint paths
signals_api_bp = Blueprint('signals_api', __name__)

@signals_api_bp.route('/api/get-saved-signals', methods=['GET', 'OPTIONS'])
def get_saved_signals():
    """Legacy endpoint that returns signals in the old format for backwards compatibility"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
        
    try:
        # Load signals using the dual_bot function
        buy_signals_df, short_signals_df = load_signals()
        
        # Convert DataFrames to lists of dictionaries for JSON serialization
        buy_signals = []
        if not buy_signals_df.empty:
            for _, row in buy_signals_df.iterrows():
                signal = {
                    'symbol': row['symbol'],
                    'date': row['date'] if 'date' in row else row.get('time', datetime.now().strftime('%Y-%m-%d')),
                    'signal_score': float(row['signal_score']) if 'signal_score' in row else float(row.get('confidence', 0.7) * 10),
                    'close': float(row['close']) if 'close' in row else float(row.get('price', 0)),
                    'volume': float(row['volume']) if 'volume' in row else 0,
                    'strategy': 'Dual Bot V2',
                }
                
                # Add technical indicators if available
                if 'ema_9' in row:
                    signal['ema_9'] = float(row['ema_9'])
                if 'ema_21' in row:
                    signal['ema_21'] = float(row['ema_21'])
                
                buy_signals.append(signal)
        
        short_signals = []
        if not short_signals_df.empty:
            for _, row in short_signals_df.iterrows():
                signal = {
                    'symbol': row['symbol'],
                    'date': row['date'] if 'date' in row else row.get('time', datetime.now().strftime('%Y-%m-%d')),
                    'signal_score': float(row['signal_score']) if 'signal_score' in row else float(row.get('confidence', -0.7) * -10),
                    'close': float(row['close']) if 'close' in row else float(row.get('price', 0)),
                    'volume': float(row['volume']) if 'volume' in row else 0,
                    'strategy': 'Dual Bot V2',
                }
                
                # Add technical indicators if available
                if 'ema_9' in row:
                    signal['ema_9'] = float(row['ema_9'])
                if 'ema_21' in row:
                    signal['ema_21'] = float(row['ema_21'])
                
                short_signals.append(signal)
        
        logger.info(f"Returning {len(buy_signals)} buy signals and {len(short_signals)} short signals")
        
        response = make_response(jsonify({
            'buy_signals': buy_signals,
            'short_signals': short_signals,
            'timestamp': datetime.now().isoformat()
        }))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error getting saved signals: {str(e)}")
        response = make_response(jsonify({
            'success': False,
            'error': str(e)
        }), 500)
        return add_cors_headers(response)

@signals_api_bp.route('/api/generate-signals', methods=['POST', 'OPTIONS'])
def generate_signals():
    """Legacy endpoint to generate signals for backwards compatibility"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
        
    try:
        # If available, directly import and call the function from app-starter.py
        try:
            app_starter_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'app-starter.py')
            
            # Load the module
            import importlib.util
            spec = importlib.util.spec_from_file_location("app_starter", app_starter_path)
            app_starter = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(app_starter)
            
            # Call the generate_signals function
            result = app_starter.generate_signals()
            
            # Load the newly generated signals
            buy_signals, short_signals = load_signals()
            
            response = make_response(jsonify({
                'success': True,
                'message': 'Signals generated successfully',
                'buy_signals_count': len(buy_signals),
                'short_signals_count': len(short_signals)
            }))
            return add_cors_headers(response)
        except Exception as direct_call_error:
            logger.warning(f"Direct call failed, falling back to API: {str(direct_call_error)}")
            
            # Fall back to API call if direct import fails
            import requests
            
            # Make a POST request to the dual-bot generate-signals endpoint
            response = requests.post('http://localhost:5000/api/dual-bot/generate-signals')
            data = response.json()
            
            if data.get('success', False):
                api_response = make_response(jsonify({
                    'success': True,
                    'message': 'Signals generated successfully',
                    'buy_signals_count': data.get('buy_signals_count', 0),
                    'short_signals_count': data.get('short_signals_count', 0)
                }))
                return add_cors_headers(api_response)
            else:
                api_response = make_response(jsonify({
                    'success': False,
                    'error': data.get('error', 'Unknown error')
                }), 500)
                return add_cors_headers(api_response)
                
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        response = make_response(jsonify({
            'success': False,
            'error': str(e)
        }), 500)
        return add_cors_headers(response) 