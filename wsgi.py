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
        imported_app = getattr(module, 'app')
        
        # Copy routes and configuration from imported app
        application.config.update(imported_app.config)
        application.url_map = imported_app.url_map
        application.view_functions = imported_app.view_functions
        application.blueprints = imported_app.blueprints
        
        logger.info(f"Successfully imported app from {module_path}")
        break
    except (ImportError, AttributeError) as e:
        logger.warning(f"Import attempt failed for {module_path}: {str(e)}")

# Add debug endpoints
@application.route('/debug/static')
def debug_static():
    """List all static files for debugging"""
    files = []
    for root, _, filenames in os.walk(STATIC_FOLDER):
        for f in filenames:
            files.append(os.path.relpath(os.path.join(root, f), STATIC_FOLDER))
    return jsonify({"static_files": files})

@application.route('/debug/routes')
def debug_routes():
    """List all routes for debugging"""
    routes = []
    for rule in application.url_map.iter_rules():
        routes.append({
            "route": str(rule),
            "methods": list(rule.methods)
        })
    return jsonify(routes)

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

# Static file serving with caching
@application.route('/static/<path:filename>')
def serve_static(filename):
    """Enhanced static file serving with cache control"""
    response = send_from_directory(application.static_folder, filename)
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response

# Single-page application (SPA) route handling
@application.route('/', defaults={'path': ''})
@application.route('/<path:path>')
def serve_spa(path):
    """
    Serve frontend SPA with proper fallback
    
    This ensures React/Vue router paths work correctly by falling back
    to index.html for routes not matching specific files
    """
    # First, try to serve the path as a static file
    static_file_path = os.path.join(STATIC_FOLDER, path)
    
    if path and os.path.isfile(static_file_path):
        return send_from_directory(STATIC_FOLDER, path)
    
    # Special case for favicon
    if path == 'favicon.ico':
        favicon_path = os.path.join(STATIC_FOLDER, 'favicon.ico')
        if os.path.exists(favicon_path):
            return send_from_directory(STATIC_FOLDER, 'favicon.ico')
    
    # Fallback to serving index.html for SPA
    index_path = os.path.join(STATIC_FOLDER, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(STATIC_FOLDER, 'index.html')
    
    # Extreme fallback in case something is wrong with the static files
    return """
    <!DOCTYPE html>
    <html>
        <head><title>AI Trading Bot</title></head>
        <body>
            <h1>AI Trading Bot</h1>
            <p>Static files not found. Please check your deployment configuration.</p>
        </body>
    </html>
    """

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