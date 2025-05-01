"""
Execution Model Routes Module

This module contains route handlers for the execution model.
"""

from flask import Blueprint, jsonify, request
import logging

logger = logging.getLogger(__name__)

def register_routes(app):
    """
    Register execution model routes with the Flask app.
    
    Args:
        app: Flask application instance
    """
    logger.info("Registering execution model routes")
    
    @app.route('/api/execution-model/status', methods=['GET'])
    def get_execution_model_status():
        """Get the status of the execution model."""
        return jsonify({
            'success': True,
            'status': 'inactive',
            'last_updated': None,
            'is_mock': True
        })
    
    @app.route('/api/execution-model/configure', methods=['POST'])
    def configure_execution_model():
        """Configure the execution model."""
        data = request.json or {}
        return jsonify({
            'success': True,
            'message': 'Execution model configured',
            'config': data
        })
    
    @app.route('/api/execution-model/start', methods=['POST'])
    def start_execution_model():
        """Start the execution model."""
        return jsonify({
            'success': True,
            'message': 'Execution model started',
            'status': 'active'
        })
    
    @app.route('/api/execution-model/stop', methods=['POST'])
    def stop_execution_model():
        """Stop the execution model."""
        return jsonify({
            'success': True,
            'message': 'Execution model stopped',
            'status': 'inactive'
        })
    
    logger.info("Execution model routes registered successfully") 