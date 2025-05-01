#!/usr/bin/env python
"""
WSGI entry point for the AI Trading Bot API.
This file is used by Gunicorn to run the application in production.
"""

import os
import sys
import logging
from flask import request, send_file
from pathlib import Path

# Add current directory and api directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'api'))

# Add mock_modules directory to sys.path to handle missing dependencies
mock_modules_dir = os.path.join(current_dir, 'mock_modules')
if os.path.exists(mock_modules_dir):
    sys.path.insert(0, mock_modules_dir)
    
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to install mock modules
try:
    from install_mock_modules import install_mock_modules
    install_mock_modules()
    logger.info("Mock modules installed successfully")
except Exception as e:
    logger.warning(f"Failed to install mock modules: {e}")

# Try to check and install required packages
try:
    from check_requirements import check_and_install_packages
    missing_packages = check_and_install_packages()
    if missing_packages:
        logger.warning(f"Some packages could not be installed: {', '.join(missing_packages)}")
    else:
        logger.info("All required packages are installed")
except Exception as e:
    logger.warning(f"Failed to check and install required packages: {e}")

# Run render fix script to ensure all files and directories exist
try:
    from render_fix import run_render_fix
    run_render_fix()
    logger.info("Render fix script executed successfully")
except Exception as e:
    logger.warning(f"Failed to run render fix script: {e}")

# Import the Flask app
try:
    from api import app
except Exception as e:
    logger.error(f"Failed to import app from api module: {e}")
    # Create a simple fallback Flask app if the main app fails to load
    from flask import Flask, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/')
    def index():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vicki AI Trading Bot - Fallback Mode</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #121212; color: white; text-align: center; padding: 50px; }
                .container { max-width: 800px; margin: 0 auto; background-color: #1a1a1a; padding: 30px; border-radius: 10px; }
                h1 { color: #ff00ff; }
                .error { color: #ff6b6b; margin: 20px 0; padding: 10px; background-color: #2d2d2d; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Vicki AI Trading Bot</h1>
                <p>The application is running in fallback mode due to an error loading the main app.</p>
                <div class="error">
                    <p>API endpoint still available at <a href="/api/health" style="color: #ff00ff;">/api/health</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'ok',
            'mode': 'fallback',
            'message': 'API is running in fallback mode'
        })
    
    logger.info("Created fallback Flask app")

# -----------------------------
# Logging Configuration
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -----------------------------
# Optional Setup Scripts
# -----------------------------
def try_import_and_run(module_name, function_name):
    try:
        module = __import__(module_name)
        func = getattr(module, function_name)
        func()
        logger.info(f"{function_name} from {module_name} executed successfully.")
    except (ImportError, AttributeError) as e:
        logger.warning(f"{function_name} not run. Reason: {e}")

try_import_and_run("check_static_files", "check_static_files")
try_import_and_run("ensure_directories", "ensure_directories")
try_import_and_run("setup_static_files", "setup_static_files")
try_import_and_run("copy_to_frontend_build", "copy_to_frontend_build")

# -----------------------------
# Default ENV Config
# -----------------------------
if 'SERVE_FRONTEND' not in os.environ:
    os.environ['SERVE_FRONTEND'] = 'true'
    logger.info("Environment variable SERVE_FRONTEND was not set. Defaulting to 'true'.")

# -----------------------------
# Debug Hook (Not for Production)
# -----------------------------
@app.before_request
def enable_debug_in_non_debug_mode():
    if not app.debug:
        app.debug = True

# -----------------------------
# Custom 404 to Serve React SPA
# -----------------------------
@app.errorhandler(404)
def fallback_to_index(e):
    path = request.path
    logger.warning(f"404 for path: {path}")

    if path.startswith('/static/'):
        frontend_path = os.path.join('frontend', 'build', path[1:])
        if os.path.exists(frontend_path):
            logger.info(f"Serving fallback static file: {frontend_path}")
            return send_file(frontend_path)

    if os.environ.get('SERVE_FRONTEND', 'false').lower() == 'true':
        index_paths = [
            os.path.join('frontend', 'build', 'index.html'),
            os.path.join('index.html'),
        ]
        for index_path in index_paths:
            if os.path.exists(index_path):
                logger.info(f"Serving index.html from {index_path}")
                return send_file(index_path)

    return e

# -----------------------------
# Local Run Entry Point
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=True)
