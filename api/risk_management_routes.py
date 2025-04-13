"""
Risk Management Routes Module

Handles API routes for risk management functionality including:
- Fetching and updating risk management settings
- Getting portfolio risk analysis
- Testing risk management on specific symbols
"""

import logging
import traceback
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from execution_model.risk_manager import RiskManager
from execution_model.ai_risk_manager import AIRiskManager
from execution_model.config import get_config, save_config
from lib.market_data import MarketDataSourceManager
from lib.market_data_config import load_market_data_config

# Set up logging
logger = logging.getLogger(__name__)

# Create Flask Blueprint
risk_bp = Blueprint('risk_management', __name__, url_prefix='/api/risk-management')

# Initialize risk manager with config
config = get_config()
risk_manager = RiskManager(config)

# Initialize market data manager
try:
    market_data_config = load_market_data_config()
    market_data_manager = MarketDataSourceManager(market_data_config)
except Exception as e:
    logger.error(f"Error initializing market data manager: {str(e)}")
    market_data_manager = None

# Routes

@risk_bp.route('/settings', methods=['GET'])
def get_risk_settings():
    """
    Get risk management settings from config
    
    Returns:
        JSON response with risk management settings
    """
    try:
        # Get current config
        config_obj = get_config()
        
        # Extract risk management settings
        settings = {
            'risk_management': config_obj.get('risk_management'),
            'ai_risk_management': config_obj.get('ai_risk_management')
        }
        
        return jsonify({
            'success': True,
            'settings': settings
        })
        
    except Exception as e:
        logger.error(f"Error getting risk management settings: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@risk_bp.route('/settings', methods=['POST'])
def update_risk_settings():
    """
    Update risk management settings
    
    Request JSON:
    {
        'risk_management': { ... },
        'ai_risk_management': { ... }
    }
    
    Returns:
        JSON response with success status
    """
    try:
        # Get JSON data from request
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Get current config
        config_obj = get_config()
        
        # Update risk management settings
        if 'risk_management' in data:
            for key, value in data['risk_management'].items():
                config_obj.update('risk_management', key, value)
            
        # Update AI risk management settings
        if 'ai_risk_management' in data:
            for key, value in data['ai_risk_management'].items():
                config_obj.update('ai_risk_management', key, value)
            
        # Save updated config
        config_obj.save_config()
        
        # Update risk manager with new config
        global risk_manager
        risk_manager = RiskManager(config_obj)
        
        return jsonify({
            'success': True,
            'message': 'Risk management settings updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating risk management settings: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@risk_bp.route('/analysis', methods=['GET'])
def get_risk_analysis():
    """
    Get current portfolio risk analysis
    
    Returns:
        JSON response with portfolio risk statistics
    """
    try:
        # Get portfolio statistics from risk manager
        try:
            statistics = risk_manager.get_portfolio_statistics()
        except Exception as stats_error:
            logger.error(f"Error getting portfolio statistics: {str(stats_error)}")
            # Provide default statistics if there's an error
            statistics = {
                'portfolio_value': 10000,
                'total_exposure': 0,
                'exposure_percent': 0,
                'total_risk_percent': 0,
                'max_risk_percent': 5.0,
                'available_risk_percent': 5.0,
                'num_positions': 0,
                'sector_exposure_percent': {},
                'daily_trades': 0,
                'max_daily_trades': 5
            }
        
        return jsonify({
            'success': True,
            'analysis': statistics
        })
        
    except Exception as e:
        logger.error(f"Error getting portfolio risk analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@risk_bp.route('/test', methods=['POST'])
def test_risk_management():
    """
    Test risk management on a specific symbol
    
    Request JSON:
    {
        'symbol': 'AAPL',
        'portfolio_value': 10000.0  # Optional, defaults to current portfolio value
    }
    
    Returns:
        JSON response with risk assessment results
    """
    try:
        # Get JSON data from request
        data = request.json
        
        if not data or 'symbol' not in data:
            return jsonify({
                'success': False,
                'error': 'Symbol is required'
            }), 400
            
        symbol = data['symbol']
        portfolio_value = data.get('portfolio_value')
        
        # Fetch market data for the symbol
        if market_data_manager:
            # Get market data (1-day resolution, 30 days lookback)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            market_data = market_data_manager.get_market_data(
                symbol,
                start_date,
                end_date,
                resolution='1d'
            )
        else:
            # Create mock market data if market data manager is not available
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            mock_price = 100.0
            prices = mock_price + np.random.normal(0, mock_price * 0.02, size=30)
            market_data = pd.DataFrame({
                'timestamp': dates,
                'open': prices * 0.99,
                'high': prices * 1.02,
                'low': prices * 0.98,
                'close': prices,
                'volume': np.random.randint(1000, 100000, size=30)
            })
            market_data.set_index('timestamp', inplace=True)
            
        # Update portfolio value if provided
        if portfolio_value:
            risk_manager.update_portfolio_value(portfolio_value)
            
        # Create a sample trade setup
        current_price = market_data['close'].iloc[-1]
        
        trade_setup = {
            'symbol': symbol,
            'entry_price': current_price,
            'direction': 'LONG',  # Default to LONG
            'setup_type': 'TEST'
        }
        
        # Evaluate risk for the trade setup
        if risk_manager.use_ai_risk_management and risk_manager.ai_risk_manager:
            risk_assessment = risk_manager.ai_risk_manager.evaluate_trade_risk(
                trade_setup, market_data, risk_manager.portfolio_value
            )
        else:
            risk_assessment = risk_manager.evaluate_trade_risk(trade_setup, market_data)
            
        # Add symbol to the result
        risk_assessment['symbol'] = symbol
        
        # Add current price for reference
        risk_assessment['current_price'] = current_price
        
        return jsonify({
            'success': True,
            'result': risk_assessment
        })
        
    except Exception as e:
        logger.error(f"Error testing risk management: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@risk_bp.route('/stop-loss', methods=['POST'])
def calculate_stop_loss():
    """
    Calculate adaptive stop loss for a trade
    
    Request JSON:
    {
        'symbol': 'AAPL',
        'entry_price': 150.0,
        'direction': 'LONG'  # or 'SHORT'
    }
    
    Returns:
        JSON response with calculated stop loss
    """
    try:
        # Get JSON data from request
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        symbol = data.get('symbol')
        entry_price = data.get('entry_price')
        direction = data.get('direction', 'LONG')
        
        if not all([symbol, entry_price, direction]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: symbol, entry_price, direction'
            }), 400
            
        # Fetch market data for the symbol
        if market_data_manager:
            # Get market data (1-day resolution, 30 days lookback)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            market_data = market_data_manager.get_market_data(
                symbol,
                start_date,
                end_date,
                resolution='1d'
            )
            
            # Create market condition object with market data
            market_condition = {'market_data': market_data}
            
            # Calculate stop loss
            stop_loss = risk_manager.calculate_stop_loss(
                symbol, entry_price, direction, market_condition
            )
            
            return jsonify({
                'success': True,
                'stop_loss': stop_loss,
                'entry_price': entry_price,
                'direction': direction
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Market data manager not available'
            }), 500
            
    except Exception as e:
        logger.error(f"Error calculating stop loss: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@risk_bp.route('/position-size', methods=['POST'])
def calculate_position_size():
    """
    Calculate position size for a trade
    
    Request JSON:
    {
        'symbol': 'AAPL',
        'entry_price': 150.0,
        'stop_loss': 145.0
    }
    
    Returns:
        JSON response with calculated position size
    """
    try:
        # Get JSON data from request
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        symbol = data.get('symbol')
        entry_price = data.get('entry_price')
        stop_loss = data.get('stop_loss')
        
        if not all([symbol, entry_price]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: symbol, entry_price'
            }), 400
            
        # Fetch market data for the symbol
        if market_data_manager:
            # Get market data (1-day resolution, 30 days lookback)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            market_data = market_data_manager.get_market_data(
                symbol,
                start_date,
                end_date,
                resolution='1d'
            )
            
            # Create market condition object with market data
            market_condition = {'market_data': market_data}
            
            # Calculate position size
            position_size_result = risk_manager.calculate_position_size(
                symbol, entry_price, stop_loss, market_condition
            )
            
            return jsonify({
                'success': True,
                'position_size': position_size_result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Market data manager not available'
            }), 500
            
    except Exception as e:
        logger.error(f"Error calculating position size: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_routes(app):
    """
    Register risk management routes with the Flask app
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(risk_bp)
    logger.info("Successfully registered risk management routes") 