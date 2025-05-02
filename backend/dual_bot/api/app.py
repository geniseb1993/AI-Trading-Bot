from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import datetime
import random
import os
import json
from .routes import api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    # Add error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info("Flask application created and configured")
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info("Starting Dual Bot API server on port 5001")
    app.run(host='0.0.0.0', port=5001, debug=True) 