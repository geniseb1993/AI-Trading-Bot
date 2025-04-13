from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Create the blueprint
analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/test', methods=['GET'])
def test_analysis():
    """Simple test endpoint for the analysis model routes"""
    return jsonify({
        'success': True,
        'message': 'Analysis model routes are working',
        'timestamp': datetime.now().isoformat()
    })

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_data():
    """Analyze market data and generate insights"""
    try:
        data = request.json
        if not data or 'market_data' not in data:
            return jsonify({
                'success': False,
                'error': 'No market data provided in the request'
            }), 400
            
        # Mock analysis results for now
        return jsonify({
            'success': True,
            'analysis': {
                'timestamp': datetime.now().isoformat(),
                'market_trend': 'bullish',
                'volatility': 'medium',
                'recommendation': 'buy',
                'confidence': 0.78,
                'metrics': {
                    'rsi': 65.4,
                    'macd': 0.42,
                    'bollinger_bands': {
                        'upper': 155.2,
                        'middle': 152.8,
                        'lower': 150.4
                    }
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/signals', methods=['GET'])
def get_signals():
    """Get the latest trading signals from the analysis model"""
    try:
        # Mock signals data
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        signals = []
        
        for symbol in symbols:
            signal_type = np.random.choice(['buy', 'sell', 'hold'], p=[0.4, 0.3, 0.3])
            signals.append({
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'signal': signal_type,
                'strength': round(np.random.random() * 100, 2),
                'price': round(100 + np.random.random() * 900, 2),
                'metrics': {
                    'rsi': round(np.random.random() * 100, 2),
                    'macd': round(np.random.random() * 2 - 1, 2),
                    'volume': int(np.random.random() * 10000000)
                }
            })
        
        return jsonify({
            'success': True,
            'signals': signals
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 