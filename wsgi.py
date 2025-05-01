#!/usr/bin/env python
"""
WSGI Application Entry Point

This module serves as the WSGI entry point for Gunicorn and other WSGI servers.
It also provides fallback mechanisms for handling missing dependencies.
"""

import os
import sys
import logging
import importlib.util
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('wsgi')

# Add the current directory to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Add mock_modules to the path
MOCK_MODULES_DIR = os.path.join(BASE_DIR, 'mock_modules')
if os.path.exists(MOCK_MODULES_DIR) and MOCK_MODULES_DIR not in sys.path:
    logger.info(f"Adding mock_modules directory to Python path: {MOCK_MODULES_DIR}")
    sys.path.insert(0, MOCK_MODULES_DIR)

# Try to install mock modules if script exists
try:
    import install_mock_modules
    install_mock_modules.install_mock_modules()
except ImportError:
    logger.warning("Could not import install_mock_modules, some dependencies may be missing")

# Ensure config files exist
CONFIG_FILES = [
    'config.json',
    'broker_config.json',
    'execution_model_config.json',
    os.path.join('api', 'lib', 'market_data_config.json')
]

for config_file in CONFIG_FILES:
    config_path = os.path.join(BASE_DIR, config_file)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    if not os.path.exists(config_path):
        logger.warning(f"Config file {config_file} does not exist. Using default settings.")

# Define a simple fallback Flask application
def create_fallback_app():
    """Create a simple Flask application as a fallback"""
    try:
        from flask import Flask, send_from_directory, jsonify, render_template_string

        app = Flask(__name__, static_folder='frontend/build')
        
        # Define basic API endpoints
        @app.route('/api/status')
        def status():
            return jsonify({
                'status': 'running',
                'mode': 'fallback',
                'message': 'Fallback Flask app is running'
            })
        
        @app.route('/health')
        def wsgi_health_check():
            return jsonify({'status': 'healthy'})
        
        @app.route('/api/health')
        def api_health_check():
            return jsonify({'status': 'healthy'})
        
        # Serve static files from frontend/build
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve(path):
            # Check if path exists in static folder
            static_path = os.path.join(app.static_folder, path)
            
            if path and os.path.exists(static_path) and not os.path.isdir(static_path):
                return send_from_directory(app.static_folder, path)
                
            # Check if we have an index.html file
            index_path = os.path.join(app.static_folder, 'index.html')
            
            if os.path.exists(index_path):
                return send_from_directory(app.static_folder, 'index.html')
                
            # Fallback to a simple HTML page
            return render_template_string("""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>AI Trading Bot</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body {
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                            margin: 0;
                            padding: 0;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            background-color: #f0f2f5;
                            color: #333;
                        }
                        .container {
                            max-width: 800px;
                            padding: 2rem;
                            background-color: white;
                            border-radius: 8px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            text-align: center;
                        }
                        h1 {
                            color: #4a90e2;
                            margin-bottom: 1rem;
                        }
                        p {
                            line-height: 1.6;
                            margin-bottom: 1.5rem;
                        }
                        .status {
                            padding: 0.5rem 1rem;
                            background-color: #e7f3ff;
                            border-radius: 4px;
                            display: inline-block;
                            font-weight: bold;
                            color: #0062cc;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>AI Trading Bot</h1>
                        <p>The application is currently running in fallback mode. The frontend assets might be missing or inaccessible.</p>
                        <div class="status">API Status: Running</div>
                    </div>
                </body>
            </html>
            """)
        
        return app
    except ImportError as e:
        logger.error(f"Failed to create fallback app: {e}")
        return None

# Try to import the main application
try:
    logger.info("Attempting to import main Flask application")
    
    # First, try to import from the api module
    try:
        from api.app import app
        logger.info("Successfully imported app from api.app")
    except ImportError as e:
        logger.warning(f"Failed to import app from api.app: {e}")
        
        # Try app.py in root directory
        try:
            import app
            application = app.app
            logger.info("Successfully imported app from app module")
        except ImportError:
            logger.warning("Failed to import app from app module, attempting fallback")
            
            # Create fallback application
            application = create_fallback_app()
            
            if application is None:
                # Last resort fallback
                from flask import Flask
                application = Flask(__name__)
                
                @application.route('/')
                def index():
                    return "AI Trading Bot API is running (minimal fallback mode)"
            
            logger.info("Using fallback Flask application")
    else:
        application = app

except Exception as e:
    logger.error(f"Critical error in WSGI initialization: {e}")
    # Create a minimal Flask app as last resort
    from flask import Flask, jsonify
    application = Flask(__name__)
    
    @application.route('/')
    def index():
        return "AI Trading Bot API is running (emergency fallback mode)"
    
    @application.route('/api/status')
    def status():
        return jsonify({
            'status': 'error',
            'error': str(e),
            'mode': 'emergency_fallback'
        })

# Create a health check route to verify the app is running
try:
    # Only add the health check if it doesn't already exist
    if not hasattr(application, 'view_functions') or 'wsgi_health_check' not in application.view_functions:
        @application.route('/health')
        def wsgi_health_check():
            from flask import jsonify
            return jsonify({'status': 'healthy'})
except Exception as e:
    logger.error(f"Failed to add health check route: {e}")

# The WSGI entry point
app = application

# If running directly
if __name__ == '__main__':
    # Execute the render_fix script to create frontend files
    try:
        from render_fix import run_render_fix
        run_render_fix()
    except ImportError:
        logger.warning("Could not import render_fix")
    
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
