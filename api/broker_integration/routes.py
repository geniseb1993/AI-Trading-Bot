"""
Broker Integration API Routes

This module provides Flask routes for interacting with broker integrations.
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any, List, Optional

from .broker_adapter import BrokerAdapter
from .config import load_config, save_config, get_active_broker_config
from .broker_utils import (
    format_order_for_response,
    format_position_for_response,
    format_account_for_response,
    get_trade_stats,
    check_broker_credentials,
    set_broker_credentials
)

# Create blueprint
broker_bp = Blueprint('broker', __name__, url_prefix='/api/broker')

# Configure logging
logger = logging.getLogger(__name__)

# Create broker adapter instance
broker_adapter = None

@broker_bp.before_request
def initialize_broker_adapter():
    """Initialize broker adapter before handling request"""
    global broker_adapter
    if broker_adapter is None:
        broker_adapter = BrokerAdapter()

@broker_bp.route('/status', methods=['GET'])
def get_broker_status():
    """Get broker connection status"""
    is_connected = broker_adapter.is_connected()
    return jsonify({
        "status": "connected" if is_connected else "disconnected",
        "broker_type": broker_adapter.broker.__class__.__name__
    })

@broker_bp.route('/connect', methods=['POST'])
def connect_broker():
    """Connect to broker"""
    success = broker_adapter.connect()
    return jsonify({
        "success": success,
        "status": "connected" if success else "disconnected",
        "message": "Successfully connected to broker" if success else "Failed to connect to broker"
    })

@broker_bp.route('/disconnect', methods=['POST'])
def disconnect_broker():
    """Disconnect from broker"""
    success = broker_adapter.disconnect()
    return jsonify({
        "success": success,
        "status": "disconnected" if success else "still connected",
        "message": "Successfully disconnected from broker" if success else "Failed to disconnect from broker"
    })

@broker_bp.route('/account', methods=['GET'])
def get_account():
    """Get account information"""
    account_info = broker_adapter.get_account_info()
    formatted_account = format_account_for_response(account_info)
    return jsonify(formatted_account)

@broker_bp.route('/positions', methods=['GET'])
def get_positions():
    """Get all positions"""
    positions = broker_adapter.get_positions()
    formatted_positions = [format_position_for_response(p) for p in positions]
    return jsonify(formatted_positions)

@broker_bp.route('/positions/<symbol>', methods=['GET'])
def get_position(symbol):
    """Get position for a specific symbol"""
    position = broker_adapter.get_position(symbol)
    if position:
        formatted_position = format_position_for_response(position)
        return jsonify(formatted_position)
    else:
        return jsonify({"error": f"No position found for {symbol}"}), 404

@broker_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get orders"""
    status = request.args.get('status')
    orders = broker_adapter.get_orders(status)
    formatted_orders = [format_order_for_response(o) for o in orders]
    return jsonify(formatted_orders)

@broker_bp.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order"""
    order = broker_adapter.get_order(order_id)
    if order:
        formatted_order = format_order_for_response(order)
        return jsonify(formatted_order)
    else:
        return jsonify({"error": f"Order {order_id} not found"}), 404

@broker_bp.route('/orders', methods=['POST'])
def place_order():
    """Place a new order"""
    data = request.json
    
    # Validate required fields
    required_fields = ['symbol', 'qty', 'side']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Place order
    order = broker_adapter.place_order(
        symbol=data['symbol'],
        qty=float(data['qty']),
        side=data['side'],
        order_type=data.get('type', 'market'),
        limit_price=data.get('limit_price'),
        stop_price=data.get('stop_price'),
        time_in_force=data.get('time_in_force', 'day')
    )
    
    # Check for error in response
    if order.get('error'):
        return jsonify({"error": order['error']}), 400
    
    # Format and return order
    formatted_order = format_order_for_response(order)
    return jsonify(formatted_order), 201

@broker_bp.route('/orders/<order_id>', methods=['DELETE'])
def cancel_order(order_id):
    """Cancel an order"""
    success = broker_adapter.cancel_order(order_id)
    if success:
        return jsonify({"success": True, "message": f"Order {order_id} cancelled"})
    else:
        return jsonify({"error": f"Failed to cancel order {order_id}"}), 400

@broker_bp.route('/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    """Get market data for a symbol"""
    market_data = broker_adapter.get_market_data(symbol)
    return jsonify(market_data)

@broker_bp.route('/brokers', methods=['GET'])
def get_brokers():
    """Get available brokers"""
    available_brokers = broker_adapter.get_available_brokers()
    config = load_config()
    active_broker = config.get('active_broker', 'mock')
    
    return jsonify({
        "available_brokers": available_brokers,
        "active_broker": active_broker
    })

@broker_bp.route('/switch', methods=['POST'])
def switch_broker():
    """Switch active broker"""
    data = request.json
    if 'broker' not in data:
        return jsonify({"error": "Missing required field: broker"}), 400
    
    broker_name = data['broker']
    success = broker_adapter.switch_broker(broker_name)
    
    if success:
        return jsonify({
            "success": True,
            "message": f"Successfully switched to broker: {broker_name}"
        })
    else:
        return jsonify({
            "error": f"Failed to switch to broker: {broker_name}"
        }), 400

@broker_bp.route('/config', methods=['GET'])
def get_config():
    """Get broker configuration"""
    config = load_config()
    # Remove sensitive information
    for broker_name, broker_config in config.get('brokers', {}).items():
        if 'api_secret' in broker_config:
            broker_config['api_secret'] = '****' if broker_config['api_secret'] else ''
    
    return jsonify(config)

@broker_bp.route('/config', methods=['PUT'])
def update_config():
    """Update broker configuration"""
    data = request.json
    config = load_config()
    
    # Update configuration
    for key, value in data.items():
        # Don't allow direct update of brokers to prevent accidentally removing credentials
        if key != 'brokers':
            config[key] = value
    
    # Update specific broker configuration if provided
    if 'broker' in data and 'broker_config' in data:
        broker_name = data['broker']
        broker_config = data['broker_config']
        
        if 'brokers' not in config:
            config['brokers'] = {}
        
        if broker_name not in config['brokers']:
            config['brokers'][broker_name] = {}
        
        # Update specific fields without overwriting entire config
        for key, value in broker_config.items():
            config['brokers'][broker_name][key] = value
    
    # Save configuration
    success = save_config(config)
    
    if success:
        return jsonify({
            "success": True,
            "message": "Configuration updated successfully"
        })
    else:
        return jsonify({
            "error": "Failed to update configuration"
        }), 500

@broker_bp.route('/credentials', methods=['POST'])
def update_credentials():
    """Update broker credentials"""
    data = request.json
    
    # Validate required fields
    required_fields = ['broker_type', 'credentials']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    broker_type = data['broker_type']
    credentials = data['credentials']
    
    # Validate credentials
    validation = check_broker_credentials(broker_type, credentials)
    if not validation['is_valid']:
        return jsonify({
            "error": validation['error'],
            "missing_fields": validation['missing_fields']
        }), 400
    
    # Set credentials
    success = set_broker_credentials(broker_type, credentials)
    
    if success:
        return jsonify({
            "success": True,
            "message": f"Credentials for {broker_type} updated successfully"
        })
    else:
        return jsonify({
            "error": f"Failed to update credentials for {broker_type}"
        }), 500

@broker_bp.route('/trade-stats', methods=['GET'])
def trade_statistics():
    """Get trading statistics"""
    # Parse date range parameters
    from datetime import datetime, timedelta
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
    
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
    
    # Get statistics
    stats = get_trade_stats(start_date, end_date)
    return jsonify(stats)

def init_app(app):
    """Initialize the broker blueprint with the Flask app"""
    app.register_blueprint(broker_bp)
    logger.info("Registered broker routes") 