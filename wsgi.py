#!/usr/bin/env python
"""
Optimized WSGI Application Entry Point for Render Deployment
"""

import os
import sys
import logging
from flask import Flask, send_from_directory, jsonify

# Configure logging before anything else
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]  # Explicitly use stdout
)
logger = logging.getLogger('wsgi')

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

# Environment configuration
os.environ.setdefault('RENDER_DEPLOYMENT', 'true')
os.environ.setdefault('FLASK_ENV', 'production')

def create_app():
    """Factory pattern for application creation"""
    app = Flask(__name__, 
                static_folder=STATIC_FOLDER,
                static_url_path='')
    
    # Register blueprints or modules here if needed
    
    return app

# Initialize application
application = create_app()

# Directory structure setup
REQUIRED_DIRS = [
    'static/css',
    'static/js',
    'static/images',
    'data/logs',
    'data/broker',
    'data/market_data',
    'config/environments'
]

for directory in REQUIRED_DIRS:
    os.makedirs(os.path.join(BASE_DIR, directory), exist_ok=True)

# Application import attempts (order matters)
IMPORT_PATHS = [
    'backend.app',
    'app',
    'api.app'
]

for module_path in IMPORT_PATHS:
    try:
        module = __import__(module_path, fromlist=['app'])
        application = getattr(module, 'app')
        logger.info(f"Successfully imported app from {module_path}")
        break
    except (ImportError, AttributeError) as e:
        logger.warning(f"Import attempt failed for {module_path}: {str(e)}")

# Fallback routes if no app was imported
if not hasattr(application, 'route'):
    logger.warning("Initializing fallback application")
    
    @application.route('/')
    def index():
        return "AI Trading Bot (fallback mode)"
    
    @application.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'AI Trading Bot',
            'mode': 'fallback'
        })

# Static file serving
@application.route('/static/<path:filename>')
def serve_static(filename):
    """Enhanced static file serving with cache control"""
    response = send_from_directory(application.static_folder, filename)
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response

# Frontend SPA handling
FRONTEND_BUILD = os.path.join(BASE_DIR, 'frontend', 'build')
if os.path.exists(FRONTEND_BUILD):
    @application.route('/', defaults={'path': ''})
    @application.route('/<path:path>')
    def serve_spa(path):
        """Serve frontend SPA with proper fallback"""
        file_path = os.path.join(application.static_folder, path)
        
        if path and os.path.exists(file_path):
            return send_from_directory(application.static_folder, path)
        
        return send_from_directory(application.static_folder, 'index.html')

# WSGI entry point
app = application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting application on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    )