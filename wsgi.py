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
from flask import send_from_directory

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
    os.path.join('config', 'environments', 'market_data_config.json')
]

for config_file in CONFIG_FILES:
    config_path = os.path.join(BASE_DIR, config_file)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    if not os.path.exists(config_path):
        logger.warning(f"Config file {config_file} does not exist. Using default settings.")

# Create data directory structure
data_dirs = [
    os.path.join(BASE_DIR, 'data'),
    os.path.join(BASE_DIR, 'data', 'logs'),
    os.path.join(BASE_DIR, 'data', 'broker'),
    os.path.join(BASE_DIR, 'frontend', 'build'),
    os.path.join(BASE_DIR, 'static')
]

for data_dir in data_dirs:
    if not os.path.exists(data_dir):
        logger.info(f"Creating directory: {data_dir}")
        os.makedirs(data_dir, exist_ok=True)

# Try to import the main application from the new backend structure
try:
    logger.info("Attempting to import Flask application from backend package")
    
    # First, try to import from backend.app
    try:
        from backend.app import app as application
        logger.info("Successfully imported app from backend.app")
    except ImportError as e:
        logger.warning(f"Failed to import app from backend.app: {e}")
        
        # Try the original app.py
        try:
            from app import app as application
            logger.info("Successfully imported app from app module")
        except ImportError:
            logger.warning("Failed to import app from app module, trying fallback")
            
            # Try the api/app.py as a last resort
            try:
                from api.app import app as application
                logger.info("Successfully imported app from api.app module")
            except ImportError:
                logger.error("Could not import application from any known location")
                from flask import Flask
                application = Flask(__name__)
                
                @application.route('/')
                def index():
                    return "AI Trading Bot API is running (minimal fallback mode)"
                
                @application.route('/api/status')
                def status():
                    from flask import jsonify
                    return jsonify({
                        'status': 'error',
                        'message': 'Failed to load main application',
                        'mode': 'emergency_fallback'
                    })
except Exception as e:
    logger.error(f"Critical error in WSGI initialization: {e}")
    # Create a minimal Flask app as last resort
    from flask import Flask, jsonify
    application = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'))
    
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

# Check for blueprint conflicts and fix them
try:
    logger.info("Checking for blueprint conflicts")
    
    # Helper function to check for duplicate blueprints
    def fix_blueprint_conflicts(app_instance):
        """Check for and fix any blueprint naming conflicts"""
        blueprint_names = {}
        conflict_count = 0
        
        if not hasattr(app_instance, 'blueprints'):
            logger.warning("App has no blueprints attribute")
            return 0
            
        for name, blueprint in app_instance.blueprints.items():
            if name in blueprint_names:
                logger.warning(f"Duplicate blueprint name detected: {name}")
                conflict_count += 1
                
                # Try to fix CEO dashboard conflicts (most common issue)
                if name == 'ceo_dashboard':
                    try:
                        from backend.routes.ceo_dashboard_routes import ceo_dashboard_bp
                        # Rename the blueprint
                        ceo_dashboard_bp.name = 'ceo_dashboard_ui'
                        # Re-register with new name if not already registered
                        if 'ceo_dashboard_ui' not in app_instance.blueprints:
                            app_instance.register_blueprint(ceo_dashboard_bp)
                            logger.info("Renamed CEO dashboard blueprint to avoid conflict")
                    except Exception as e:
                        logger.error(f"Failed to fix CEO dashboard blueprint conflict: {e}")
            else:
                blueprint_names[name] = blueprint
        
        return conflict_count
    
    # Fix any blueprint conflicts
    conflicts = fix_blueprint_conflicts(application)
    if conflicts > 0:
        logger.info(f"Found and attempted to fix {conflicts} blueprint conflicts")
    else:
        logger.info("No blueprint conflicts detected")
except Exception as e:
    logger.error(f"Error checking for blueprint conflicts: {e}")

# Check for the presence of static files and ensure they're accessible
try:
    logger.info("Checking for frontend static files")
    
    # Helper function to verify and fix static serving
    def verify_static_files(app_instance):
        """Verify static files are accessible and fix if needed"""
        static_folder = app_instance.static_folder
        static_url_path = app_instance.static_url_path
        
        logger.info(f"Current static configuration: folder={static_folder}, url_path={static_url_path}")
        
        # Check if static folder exists
        if static_folder and os.path.exists(static_folder):
            logger.info(f"Static folder exists: {static_folder}")
            
            # Check for index.html
            index_path = os.path.join(static_folder, 'index.html')
            if os.path.exists(index_path):
                logger.info(f"index.html found at {index_path}")
            else:
                logger.warning(f"index.html not found in static folder")
                # Create a simple index.html
                try:
                    with open(index_path, 'w') as f:
                        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>AI Trading Bot</title>
    <style>
        body { font-family: sans-serif; margin: 0; padding: 20px; background: #121212; color: #e1e1e1; }
        h1 { color: #4a90e2; }
        .container { max-width: 800px; margin: 40px auto; padding: 20px; background: #1e1e1e; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Trading Bot</h1>
        <p>The API server is running successfully.</p>
        <p><a href="/api/health" style="color: #4a90e2;">Check API Health</a></p>
    </div>
</body>
</html>""")
                    logger.info(f"Created basic index.html at {index_path}")
                except Exception as e:
                    logger.error(f"Failed to create index.html: {e}")
                
            # Check for static/css directory
            css_dir = os.path.join(static_folder, 'static', 'css')
            if os.path.exists(css_dir):
                logger.info(f"CSS directory found at {css_dir}")
            else:
                logger.warning(f"CSS directory not found at {css_dir}")
                # Create the css directory
                os.makedirs(css_dir, exist_ok=True)
                logger.info(f"Created CSS directory at {css_dir}")
                
                # Create a basic CSS file
                css_file = os.path.join(css_dir, 'main.css')
                try:
                    with open(css_file, 'w') as f:
                        f.write("""/* Basic CSS for AI Trading Bot */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #121212;
    color: #e1e1e1;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}
.card {
    background-color: #1e1e1e;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
h1, h2, h3 {
    color: #4a90e2;
}
a {
    color: #4a90e2;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}""")
                    logger.info(f"Created basic CSS file at {css_file}")
                except Exception as e:
                    logger.error(f"Failed to create CSS file: {e}")
                
            # Add route to explicitly serve static files if needed
            if static_url_path != '':
                @app_instance.route('/static/<path:filename>')
                def serve_static(filename):
                    """Serve static files from static folder"""
                    return app_instance.send_static_file(os.path.join('static', filename))
                logger.info("Added explicit /static/ route handler")
        else:
            logger.warning(f"Static folder does not exist: {static_folder}")
            # Create the static folder
            if static_folder:
                os.makedirs(static_folder, exist_ok=True)
                logger.info(f"Created static folder at {static_folder}")
    
    # Verify and fix static file serving
    verify_static_files(application)
except Exception as e:
    logger.error(f"Error checking static files: {e}")

# Add missing frontend routes
@application.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files from multiple potential locations"""
    # Try different possible CSS locations
    for css_dir in [
        os.path.join(application.static_folder, 'static', 'css'),
        os.path.join(application.static_folder, 'css'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'css')
    ]:
        if os.path.exists(os.path.join(css_dir, filename)):
            return send_from_directory(css_dir, filename)
    
    # Return 404 if not found
    return "CSS file not found", 404

@application.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JS files from multiple potential locations"""
    # Try different possible JS locations
    for js_dir in [
        os.path.join(application.static_folder, 'static', 'js'),
        os.path.join(application.static_folder, 'js'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'js')
    ]:
        if os.path.exists(os.path.join(js_dir, filename)):
            return send_from_directory(js_dir, filename)
    
    # Return 404 if not found
    return "JS file not found", 404

# The WSGI entry point - make sure this is correctly defined for gunicorn
app = application

# Create a health check route to verify the app is running
try:
    # Only add the health check if it doesn't already exist
    route_rules = [rule.rule for rule in app.url_map.iter_rules()]
    if '/health' not in route_rules:
        @app.route('/health')
        def wsgi_main_health_check():
            from flask import jsonify
            return jsonify({'status': 'healthy'})
        logger.info("Added health check route")
    else:
        logger.info("Health check route already exists, skipping")
except Exception as e:
    logger.error(f"Failed to add health check route: {e}")

# Make sure the app variable is properly defined and exported for gunicorn
if __name__ == '__main__':
    logger.info(f"Running app directly via wsgi.py")
    port = os.environ.get('PORT')
    # Fix for the 'int' object has no attribute 'get' error
    if port is not None:
        port = int(port)
    else:
        port = 5000
    app.run(host='0.0.0.0', port=port, debug=False)
