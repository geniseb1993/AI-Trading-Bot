"""
AI Signal Ranking Routes Module

Provides API routes for AI signal ranking and GPT-powered market insights:
- Signal ranking based on ML models
- GPT-powered market analysis
- Trade setup optimization with AI
"""

import logging
import traceback
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from execution_model.ai_signal_ranking import AISignalRanking
from execution_model.config import get_config
from execution_model.pnl_logger import PnLLogger
from lib.market_data import MarketDataSourceManager
from lib.market_data_config import load_market_data_config

# Set up logging
logger = logging.getLogger(__name__)

# Create Flask Blueprint
ai_bp = Blueprint('ai_signal_ranking', __name__, url_prefix='/api/ai-signal-ranking')

# Initialize configuration
config = get_config()

# Initialize PnL logger
pnl_logger = PnLLogger(config)

# Initialize AI signal ranking
ai_signal_ranking = AISignalRanking(config, pnl_logger)

# Initialize market data manager
try:
    market_data_config = load_market_data_config()
    market_data_manager = MarketDataSourceManager(market_data_config)
except Exception as e:
    logger.error(f"Error initializing market data manager: {str(e)}")
    market_data_manager = None

# Routes

@ai_bp.route('/rank-signals', methods=['POST'])
def rank_signals():
    """
    Rank trade signals based on AI/ML models
    
    Request JSON:
    {
        'signals': [...],  # List of signal dictionaries
        'market_data': {...}  # Market data dictionary
    }
    
    Returns:
        JSON response with ranked signals
    """
    try:
        # Get JSON data from request
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        signals = data.get('signals', [])
        market_data = data.get('market_data', {})
        
        if not signals:
            return jsonify({
                'success': True,
                'ranked_signals': []
            })
            
        # Rank signals using AI Signal Ranking
        ranked_signals = ai_signal_ranking.rank_signals(signals, market_data)
        
        return jsonify({
            'success': True,
            'ranked_signals': ranked_signals
        })
        
    except Exception as e:
        logger.error(f"Error ranking signals: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/market-insights', methods=['POST'])
def get_market_insights():
    """
    Get GPT-powered market insights
    
    Request JSON:
    {
        'symbols': [...],  # List of symbol strings
        'lookback_days': 5  # Optional, defaults to 5
    }
    
    Returns:
        JSON response with GPT insights
    """
    try:
        # Get JSON data from request
        data = request.json
        
        if not data or 'symbols' not in data:
            return jsonify({
                'success': False,
                'error': 'Symbols are required'
            }), 400
            
        symbols = data.get('symbols', [])
        lookback_days = data.get('lookback_days', 5)
        recent_signals = data.get('recent_signals', [])
        
        if not symbols:
            return jsonify({
                'success': False,
                'error': 'At least one symbol is required'
            }), 400
            
        # Fetch market data for the symbols
        market_data = {}
        if market_data_manager:
            for symbol in symbols:
                try:
                    # Get market data for the symbol
                    symbol_data = market_data_manager.get_market_data(
                        symbol, 
                        lookback_days=lookback_days
                    )
                    market_data[symbol] = symbol_data
                except Exception as symbol_error:
                    logger.error(f"Error fetching market data for {symbol}: {str(symbol_error)}")
        
        # If no market data available, return error
        if not market_data:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch market data for symbols'
            }), 500
            
        # Get GPT insights
        insights = ai_signal_ranking.get_gpt_insights(symbols, market_data, recent_signals, lookback_days)
        
        return jsonify({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        logger.error(f"Error getting market insights: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/optimize-trade', methods=['POST'])
def optimize_trade_setup():
    """
    Optimize trade setup using AI and GPT
    
    Request JSON:
    {
        'trade_setup': {...},  # Trade setup dictionary
        'market_data': {...}   # Market data for the symbol
    }
    
    Returns:
        JSON response with optimized trade setup
    """
    try:
        # Get JSON data from request
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        trade_setup = data.get('trade_setup', {})
        market_data = data.get('market_data', {})
        
        if not trade_setup:
            return jsonify({
                'success': False,
                'error': 'Trade setup is required'
            }), 400
            
        # Optimize trade setup
        optimized_setup = ai_signal_ranking.optimize_trade_setup(trade_setup, market_data)
        
        return jsonify({
            'success': True,
            'optimized_setup': optimized_setup
        })
        
    except Exception as e:
        logger.error(f"Error optimizing trade setup: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/market-summary', methods=['POST'])
def get_market_summary():
    """
    Get AI-powered market summary for multiple symbols
    
    Request JSON:
    {
        'market_data': {...},  # Market data dictionary by symbol
        'top_symbols': [...]   # Optional list of key symbols to focus on
    }
    
    Returns:
        JSON response with market summary
    """
    try:
        # Get JSON data from request
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        market_data = data.get('market_data', {})
        top_symbols = data.get('top_symbols')
        
        if not market_data:
            return jsonify({
                'success': False,
                'error': 'Market data is required'
            }), 400
            
        # Get market summary
        summary = ai_signal_ranking.get_market_summary(market_data, top_symbols)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting market summary: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_routes(app):
    """
    Register AI signal ranking routes with Flask application
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(ai_bp)
    logger.info("Successfully registered AI signal ranking routes")
    return True 