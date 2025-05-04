#!/usr/bin/env python
"""
Optimized WSGI Application Entry Point for Render Deployment
"""

import os
import sys
import logging
from flask import Flask, send_from_directory, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('wsgi')

# Set the RENDER_DEPLOYMENT environment variable
os.environ['RENDER_DEPLOYMENT'] = 'true'

# Create basic directory structure if needed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
    full_path = os.path.join(BASE_DIR, directory)
    os.makedirs(full_path, exist_ok=True)

# Try to import the main application from different possible locations
application = None
import_attempts = [
    'backend.app',
    'app',
    'api.app'
]

for module in import_attempts:
    try:
        module_obj = __import__(module, fromlist=['app'])
        application = getattr(module_obj, 'app')
        logger.info(f"Successfully imported app from {module}")
        break
    except (ImportError, AttributeError) as e:
        logger.warning(f"Failed to import from {module}: {str(e)}")

# Fallback Flask app if no application found
if not application:
    logger.warning("No application found in standard locations, creating fallback app")
    application = Flask(__name__, static_folder='static')
    
    @application.route('/')
    def index():
        return "AI Trading Bot (fallback mode)"
    
    @application.route('/api/health')
    def health():
        return jsonify({'status': 'healthy', 'mode': 'fallback'})

# Configure static file serving
@application.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(application.static_folder, filename)

# Ensure frontend build is properly served
if os.path.exists(os.path.join(BASE_DIR, 'frontend', 'build')):
    @application.route('/', defaults={'path': ''})
    @application.route('/<path:path>')
    def serve_frontend(path):
        static_path = os.path.join(application.static_folder, path)
        if path != "" and os.path.exists(static_path):
            return send_from_directory(application.static_folder, path)
        return send_from_directory(application.static_folder, 'index.html')

# The WSGI entry point
app = application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)