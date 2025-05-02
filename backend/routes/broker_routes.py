from flask import Blueprint, jsonify, request, current_app
import logging
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List
import random

# Import broker configuration
from backend.broker_integration.config import (
    load_config,
    save_config,
    get_active_broker_config,
    DEFAULT_CONFIG
)

# Create blueprint for broker routes
broker_routes = Blueprint('broker_routes', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@broker_routes.route('/broker/available', methods=['GET'])
def get_available_brokers():
    """
    Get available brokers and current active broker.
    
    Returns:
        JSON response with available brokers and active broker.
    """
    try:
        # Load broker configuration
        config = load_config()
        
        # Extract broker names (excluding 'active_broker' key)
        available_brokers = [key for key in config.keys() if key != 'active_broker']
        active_broker = config.get('active_broker', 'mock')
        
        return jsonify({
            'success': True,
            'data': {
                'available_brokers': available_brokers,
                'active_broker': active_broker
            }
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving available brokers: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error retrieving available brokers: {str(e)}"
        }), 500

@broker_routes.route('/broker/config', methods=['GET'])
def get_broker_config():
    """
    Get broker configuration.
    
    Returns:
        JSON response with broker configuration.
    """
    try:
        # Load broker configuration
        config = load_config()
        
        return jsonify({
            'success': True,
            'data': config
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving broker configuration: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error retrieving broker configuration: {str(e)}"
        }), 500

@broker_routes.route('/broker/set-active', methods=['POST'])
def set_active_broker():
    """
    Set active broker.
    
    Returns:
        JSON response indicating success or failure.
    """
    try:
        data = request.json
        if not data or 'broker' not in data:
            return jsonify({
                'success': False,
                'message': "Missing required parameter: 'broker'"
            }), 400
        
        broker_name = data['broker']
        
        # Load current configuration
        config = load_config()
        
        # Check if broker exists in configuration
        if broker_name not in config:
            return jsonify({
                'success': False,
                'message': f"Broker '{broker_name}' not found in configuration"
            }), 400
        
        # Update active broker
        config['active_broker'] = broker_name
        
        # Save configuration
        if save_config(config):
            return jsonify({
                'success': True,
                'message': f"Active broker set to '{broker_name}'",
                'data': {
                    'active_broker': broker_name
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': "Failed to save configuration"
            }), 500
    
    except Exception as e:
        logger.error(f"Error setting active broker: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error setting active broker: {str(e)}"
        }), 500

@broker_routes.route('/broker/update-config', methods=['POST'])
def update_broker_config():
    """
    Update broker configuration.
    
    Returns:
        JSON response indicating success or failure.
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': "Missing request body"
            }), 400
        
        # Load current configuration
        config = load_config()
        
        # Update configuration with new data
        for key, value in data.items():
            config[key] = value
        
        # Save configuration
        if save_config(config):
            return jsonify({
                'success': True,
                'message': "Broker configuration updated successfully",
                'data': config
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': "Failed to save configuration"
            }), 500
    
    except Exception as e:
        logger.error(f"Error updating broker configuration: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error updating broker configuration: {str(e)}"
        }), 500

@broker_routes.route('/broker/test-connection', methods=['POST'])
def test_broker_connection():
    """
    Test connection to broker.
    
    Returns:
        JSON response indicating success or failure of connection test.
    """
    try:
        data = request.json
        if not data or 'broker' not in data:
            return jsonify({
                'success': False,
                'message': "Missing required parameter: 'broker'"
            }), 400
        
        broker_name = data['broker']
        
        # Load configuration
        config = load_config()
        
        # Check if broker exists in configuration
        if broker_name not in config:
            return jsonify({
                'success': False,
                'message': f"Broker '{broker_name}' not found in configuration"
            }), 400
        
        # In a real implementation, we would test the connection to the broker here
        # For now, just simulate a successful connection
        return jsonify({
            'success': True,
            'message': f"Successfully connected to {broker_name}",
            'data': {
                'broker': broker_name,
                'status': 'connected',
                'timestamp': datetime.datetime.now().isoformat(),
                'connection_details': {
                    'latency': random.randint(50, 200),
                    'server': f"{broker_name}-server-{random.randint(1, 10)}"
                }
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error testing broker connection: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error testing broker connection: {str(e)}"
        }), 500

# Additional route for advanced broker operations
@broker_routes.route('/broker/accounts', methods=['GET'])
def get_broker_accounts():
    """
    Get accounts from active broker.
    
    Returns:
        JSON response with accounts from active broker.
    """
    try:
        # Get active broker configuration
        active_broker_info = get_active_broker_config()
        broker_name = active_broker_info['broker']
        
        # In a real implementation, we would fetch accounts from the broker
        # For now, just return mock data
        mock_accounts = [
            {
                'id': f"acc-{random.randint(10000, 99999)}",
                'name': f"{broker_name} Trading Account",
                'type': 'margin',
                'status': 'active',
                'balance': round(random.uniform(10000, 50000), 2),
                'currency': 'USD'
            },
            {
                'id': f"acc-{random.randint(10000, 99999)}",
                'name': f"{broker_name} IRA Account",
                'type': 'cash',
                'status': 'active',
                'balance': round(random.uniform(50000, 200000), 2),
                'currency': 'USD'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'broker': broker_name,
                'accounts': mock_accounts
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving broker accounts: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error retrieving broker accounts: {str(e)}"
        }), 500 