# Standard imports
import os
import sys
import time
import json
import logging
import datetime
from logging.handlers import RotatingFileHandler

# Flask and related
from flask import Flask, request, jsonify, abort, send_from_directory, send_file, render_template_string, redirect, Response
from flask_cors import CORS

def create_app(test_config=None):
    """Create and configure the Flask application."""
    
    # Check for required static files
    check_required_files()
    
    # Get the project root directory
    project_root = os.path.abspath(os.path.dirname(__file__) + '/..')
    static_folder = os.path.join(project_root, 'static')
    
    # Create and configure the app - explicitly set the static folder
    app = Flask(__name__, 
                static_folder=static_folder,
                static_url_path='/static')
    
    app.logger.setLevel(logging.INFO)
    app.logger.info(f"Using static folder: {static_folder}")
    
    # Enable CORS with better configuration
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:5001", "http://127.0.0.1:5001", "http://localhost:5002", "http://127.0.0.1:5002"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With", "X-API-Key"],
            "supports_credentials": True
        }
    })
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register a before_request handler to check static files
    @app.before_request
    def check_files_before_request():
        # Only run check for static file requests
        if request.path.startswith('/static/'):
            try:
                # Import here to avoid circular imports
                from check_static_files import check_static_files, emergency_create_static_files
                
                # Check static files first
                if not check_static_files():
                    # If normal check fails, try emergency creation
                    app.logger.warning("Static file check failed, using emergency creation")
                    emergency_create_static_files()
            except Exception as e:
                app.logger.error(f"Error checking static files: {str(e)}")
    
    # Add emergency function to directly write frontend files
    def create_frontend_files():
        """Emergency function to create essential frontend files"""
        try:
            # Create directories
            directories = [
                os.path.join(os.getcwd(), 'frontend', 'build'),
                os.path.join(os.getcwd(), 'frontend', 'build', 'static'),
                os.path.join(os.getcwd(), 'frontend', 'build', 'static', 'css'),
                os.path.join(os.getcwd(), 'frontend', 'build', 'static', 'js'),
                os.path.join(os.getcwd(), 'frontend', 'build', 'images'),
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                
            # Create CSS file
            css_path = os.path.join(os.getcwd(), 'frontend', 'build', 'static', 'css', 'main.8a689c36.css')
            with open(css_path, 'w') as f:
                f.write("""
/* Emergency CSS file created by Flask app */
body {
    font-family: Arial, sans-serif;
    background-color: #121212;
    color: #ffffff;
    margin: 0;
    padding: 0;
}
#root {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.app-container {
    max-width: 1200px;
    width: 100%;
    padding: 20px;
    box-sizing: border-box;
}
.placeholder-message {
    text-align: center;
    margin-top: 100px;
    font-size: 1.5rem;
}
h1 {
    color: #61dafb;
}
""")
            
            # Create JS file
            js_path = os.path.join(os.getcwd(), 'frontend', 'build', 'static', 'js', 'main.75e22b8e.js')
            with open(js_path, 'w') as f:
                f.write("""
// Emergency JS file created by Flask app
console.log('Emergency JS file loaded');
document.addEventListener('DOMContentLoaded', function() {
    const root = document.getElementById('root');
    if (root) {
        root.innerHTML = `
            <div class="app-container">
                <div class="placeholder-message">
                    <h1>Vicki AI Trading Bot</h1>
                    <p>This is an emergency interface created by the Flask app.</p>
                    <p>The frontend build files were not properly created or are inaccessible.</p>
                    <p>Please visit <a href="/api/health" style="color: #61dafb;">API Health Check</a> to ensure the API is working.</p>
                    <div style="margin-top: 40px; text-align: left;">
                        <h2>API Endpoints:</h2>
                        <ul>
                            <li><a href="/api/health" style="color: #61dafb;">Health Check</a></li>
                            <li><a href="/api/bot/status" style="color: #61dafb;">Bot Status</a></li>
                            <li><a href="/api/market-overview" style="color: #61dafb;">Market Overview</a></li>
                            <li><a href="/api/portfolio-performance" style="color: #61dafb;">Portfolio Performance</a></li>
                            <li><a href="/api/diagnostic" style="color: #61dafb;">Diagnostic Information</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }
});
""")
            
            # Create index.html
            index_path = os.path.join(os.getcwd(), 'frontend', 'build', 'index.html')
            if not os.path.exists(index_path):
                with open(index_path, 'w') as f:
                    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vicki AI Trading Bot</title>
    <link rel="stylesheet" href="/static/css/main.8a689c36.css">
</head>
<body>
    <div id="root"></div>
    <script src="/static/js/main.75e22b8e.js"></script>
</body>
</html>""")
                
            return True
        except Exception as e:
            logging.error(f"Error creating frontend files: {str(e)}")
            return False
    
    # Create the frontend files immediately
    create_frontend_files()
    
    # Load configurations
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Register blueprints
    from .routes.bot_routes import bot_routes
    from .routes.health_routes import health_routes
    app.register_blueprint(bot_routes, url_prefix='/api/bot')
    app.register_blueprint(health_routes, url_prefix='/api/health')
    
    # Register dashboard routes
    try:
        from .routes.dashboard_routes import dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/api')
        logging.info("Dashboard routes registered successfully")
    except Exception as e:
        logging.error(f"Failed to register dashboard routes: {str(e)}")
    
    # Register CEO dashboard routes
    try:
        from .routes.ceo_dashboard_routes import ceo_dashboard_bp
        app.register_blueprint(ceo_dashboard_bp)
        logging.info("CEO Dashboard routes registered successfully")
    except Exception as e:
        logging.error(f"Failed to register CEO dashboard routes: {str(e)}")
    
    # Register dual bot routes
    try:
        from .routes.dual_bot_routes import dual_bot_bp
        app.register_blueprint(dual_bot_bp)
        logging.info("Dual Bot routes registered successfully")
    except Exception as e:
        logging.error(f"Failed to register dual bot routes: {str(e)}")
    
    # Function to find a file in multiple potential directories
    def find_file_in_dirs(filename, dirs):
        """Try to find a file in multiple directories and return the first match."""
        for dir_path in dirs:
            full_path = os.path.join(os.getcwd(), dir_path, filename)
            if os.path.exists(full_path):
                return dir_path
        return None
    
    # Create a diagnostic endpoint to check files and directories
    @app.route('/api/diagnostic', methods=['GET'])
    def diagnostic():
        """Diagnostic endpoint to check files and directories"""
        try:
            result = {
                'cwd': os.getcwd(),
                'directories': {},
                'frontend_files': {},
                'static_files': {},
                'environment': dict(os.environ),
            }
            
            # Check key directories
            for directory in ['frontend', 'frontend/build', 'frontend/build/static', 
                             'frontend/build/static/css', 'frontend/build/static/js',
                             'frontend/public', 'public', 'public/images']:
                path = os.path.join(os.getcwd(), directory)
                exists = os.path.exists(path)
                result['directories'][directory] = {
                    'exists': exists,
                    'files': os.listdir(path) if exists else []
                }
            
            # Check specific frontend files
            for filepath in ['frontend/build/index.html', 'frontend/build/manifest.json']:
                path = os.path.join(os.getcwd(), filepath)
                result['frontend_files'][filepath] = {
                    'exists': os.path.exists(path),
                    'size': os.path.getsize(path) if os.path.exists(path) else 0
                }
                
            # Check specific static files
            for filepath in ['frontend/build/static/css/main.8a689c36.css', 
                            'frontend/build/static/js/main.75e22b8e.js']:
                path = os.path.join(os.getcwd(), filepath)
                result['static_files'][filepath] = {
                    'exists': os.path.exists(path),
                    'size': os.path.getsize(path) if os.path.exists(path) else 0
                }
                
            # Try to create the files again
            create_frontend_files()
            
            return result
        except Exception as e:
            return {
                'error': str(e),
                'traceback': str(logging.traceback.format_exc())
            }

    # Add a static-specific diagnostic endpoint
    @app.route('/api/static-diagnostic', methods=['GET'])
    def static_file_diagnostic():
        """Diagnostic endpoint specifically for static files"""
        try:
            project_root = os.path.abspath(os.path.dirname(__file__) + '/..')
            
            result = {
                'project_root': project_root,
                'cwd': os.getcwd(),
                'static_files': {},
                'static_folder': app.static_folder,
                'static_url_path': app.static_url_path
            }
            
            # Check specific files
            static_files = [
                'index.html',
                os.path.join('static', 'css', 'main.css'),
                os.path.join('static', 'js', 'main.js')
            ]
            
            for file_path in static_files:
                full_path = os.path.join(project_root, file_path)
                exists = os.path.exists(full_path)
                
                result['static_files'][file_path] = {
                    'exists': exists,
                    'path': full_path,
                    'size': os.path.getsize(full_path) if exists else 0,
                    'url': f"/{file_path}" if file_path == 'index.html' else f"/{file_path}"
                }
                
                # If file doesn't exist, try to create it
                if not exists:
                    try:
                        from check_static_files import emergency_create_static_files
                        emergency_create_static_files()
                        # Update result after creation
                        if os.path.exists(full_path):
                            result['static_files'][file_path]['exists'] = True
                            result['static_files'][file_path]['size'] = os.path.getsize(full_path)
                            result['static_files'][file_path]['created'] = True
                    except Exception as e:
                        result['static_files'][file_path]['error'] = str(e)
            
            return result
        except Exception as e:
            return {
                'error': str(e)
            }

    # Add static file routes with better fallbacks
    @app.route('/data/dashboard/<path:filename>')
    def serve_dashboard_data(filename):
        """Serve dashboard data files."""
        app.logger.info(f"Serving dashboard data file: {filename}")
        return send_from_directory(os.path.join(os.getcwd(), 'data', 'dashboard'), filename)

    @app.route('/images/<path:filename>')
    def serve_images(filename):
        """Serve image files with better fallbacks."""
        app.logger.info(f"Serving image file: {filename}")
        # Try multiple image directories with frontend taking precedence
        image_dirs = [
            'frontend/public/images',
            'frontend/build/images',
            'public/images'
        ]
        
        image_dir = find_file_in_dirs(filename, image_dirs)
        if image_dir:
            return send_from_directory(os.path.join(os.getcwd(), image_dir), filename)
            
        # Fallback for images not found - serve a default
        app.logger.warning(f"Image not found: {filename} - using fallback")
        return send_from_directory(os.path.join(os.getcwd(), 'frontend/public/images'), 'vicky.png')

    @app.route('/sounds/<path:filename>')
    def serve_sounds(filename):
        """Serve sound files with better fallbacks."""
        app.logger.info(f"Serving sound file: {filename}")
        # Try multiple sound directories with frontend taking precedence
        sound_dirs = [
            'frontend/public/sounds',
            'frontend/build/sounds',
            'public/sounds'
        ]
        
        sound_dir = find_file_in_dirs(filename, sound_dirs)
        if sound_dir:
            return send_from_directory(os.path.join(os.getcwd(), sound_dir), filename)
            
        # If sound not found, just return 404 or a default sound
        app.logger.warning(f"Sound not found: {filename}")
        return send_file(os.path.join(os.getcwd(), 'public/sounds', 'notification.mp3')) if os.path.exists(os.path.join(os.getcwd(), 'public/sounds', 'notification.mp3')) else ('Sound file not found', 404)

    @app.route('/backtest_results.csv')
    def serve_backtest_results():
        """Serve backtest results file."""
        app.logger.info("Serving backtest results file")
        return send_from_directory(os.getcwd(), 'backtest_results.csv')
    
    # Check if we should serve the frontend
    serve_frontend = os.environ.get('SERVE_FRONTEND', '').lower() == 'true'
    
    # Serve the React frontend if enabled
    if serve_frontend:
        app.logger.info("Frontend serving enabled - will serve React frontend")

        # Serve static files directly from the static directory
        @app.route('/static/<path:path>')
        def serve_static(path):
            project_root = os.path.abspath(os.path.dirname(__file__) + '/..')
            app.logger.info(f"Serving static file: {path} from {project_root}/static")
            return send_from_directory(os.path.join(project_root, 'static'), path)
        
        # Serve specific static files at the root level
        @app.route('/manifest.json')
        def serve_manifest():
            app.logger.info("Serving manifest.json")
            return send_from_directory('static', 'manifest.json')

        @app.route('/favicon.ico')
        def serve_favicon():
            app.logger.info("Serving favicon.ico")
            if os.path.exists(os.path.join(os.getcwd(), 'static', 'favicon.ico')):
                return send_from_directory('static', 'favicon.ico')
            # Fallback to any available icon
            for icon_name in ['logo.png', 'vicky.png', 'velma.png']:
                if os.path.exists(os.path.join(os.getcwd(), 'static', 'images', icon_name)):
                    return send_from_directory(os.path.join('static', 'images'), icon_name)
            return "No favicon found", 404
            
        @app.route('/robots.txt')
        def serve_robots():
            app.logger.info("Serving robots.txt")
            return send_from_directory('static', 'robots.txt')
            
        # For all frontend routes (not starting with /api), serve the index.html
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_react(path):
            from flask import current_app
            
            # Skip API routes
            if path.startswith('api/'):
                return {"error": "Not Found"}, 404
            
            # Get the project root directory - one level up from the api directory
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            
            # Log the paths for debugging
            app.logger.info(f"Current working directory: {os.getcwd()}")
            app.logger.info(f"Project root: {project_root}")
            app.logger.info(f"Looking for static file: {path}")
            
            # First try to serve static files if the path exists
            static_path = os.path.join(project_root, 'static', path)
            if path and os.path.exists(static_path):
                app.logger.info(f"Serving static file from: {static_path}")
                # The directory is 'static' and the file is the path
                return send_from_directory(os.path.join(project_root, 'static'), path)
            
            # Otherwise serve index.html for client-side routing
            index_path = os.path.join(project_root, 'index.html')
            app.logger.info(f"Serving React app index from: {index_path}")
            
            if os.path.exists(index_path):
                return send_file(index_path)
            else:
                app.logger.error(f"Index file not found at: {index_path}")
                return "Application Error: Index file not found. Please check server logs.", 500

        # Add explicit routes for main.css and main.js
        @app.route('/static/css/main.css')
        def serve_main_css():
            project_root = os.path.abspath(os.path.dirname(__file__) + '/..')
            css_path = os.path.join(project_root, 'static', 'css', 'main.css')
            app.logger.info(f"Serving main.css from {css_path}")
            if os.path.exists(css_path):
                return send_file(css_path, mimetype='text/css')
            else:
                app.logger.error(f"main.css not found at {css_path}")
                return "/* CSS file not found */", 404, {'Content-Type': 'text/css'}
            
        @app.route('/static/js/main.js')
        def serve_main_js():
            project_root = os.path.abspath(os.path.dirname(__file__) + '/..')
            js_path = os.path.join(project_root, 'static', 'js', 'main.js')
            app.logger.info(f"Serving main.js from {js_path}")
            if os.path.exists(js_path):
                return send_file(js_path, mimetype='application/javascript')
            else:
                app.logger.error(f"main.js not found at {js_path}")
                return "// JavaScript file not found", 404, {'Content-Type': 'application/javascript'}
    else:
        # Root route - serve a simple dashboard with links to APIs (only if not serving the frontend)
        @app.route('/')
        def root():
            html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>AI Trading Bot Dashboard</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        color: #333;
                        background-color: #f4f7f9;
                    }
                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: white;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                        border-radius: 5px;
                    }
                    h1 {
                        color: #2c3e50;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                    }
                    h2 {
                        color: #3498db;
                    }
                    .card {
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        padding: 15px;
                        margin-bottom: 20px;
                        background-color: #fff;
                    }
                    .card h3 {
                        margin-top: 0;
                        color: #2c3e50;
                    }
                    .stats {
                        display: flex;
                        flex-wrap: wrap;
                        gap: 20px;
                    }
                    .stat-card {
                        flex: 1;
                        min-width: 200px;
                        background-color: #ecf0f1;
                        padding: 15px;
                        border-radius: 4px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .links {
                        margin-top: 30px;
                    }
                    .links a {
                        display: inline-block;
                        margin-right: 15px;
                        margin-bottom: 10px;
                        color: #3498db;
                        text-decoration: none;
                        padding: 5px 10px;
                        border: 1px solid #3498db;
                        border-radius: 4px;
                    }
                    .links a:hover {
                        background-color: #3498db;
                        color: white;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>AI Trading Bot Dashboard</h1>
                    
                    <div class="card">
                        <h3>System Status</h3>
                        <p>The AI Trading Bot API is currently running in production mode.</p>
                    </div>
                    
                    <h2>Quick Links</h2>
                    <div class="links">
                        <a href="/api/health">API Health Status</a>
                        <a href="/api/bot/status">Bot Status</a>
                        <a href="/api/dashboard">Dashboard Data</a>
                        <a href="/api/broker/positions">Current Positions</a>
                        <a href="/api/market-overview">Market Overview</a>
                        <a href="/api/portfolio-performance">Portfolio Performance</a>
                        <a href="/api/alerts">Trading Alerts</a>
                        <a href="/api/dual-bot/signals">Dual Bot Signals</a>
                        <a href="/api/ceo-dashboard">CEO Dashboard</a>
                    </div>
                    
                    <h2>API Documentation</h2>
                    <div class="card">
                        <h3>Available Endpoints</h3>
                        <ul>
                            <li><strong>/api/health</strong> - Check system health</li>
                            <li><strong>/api/bot</strong> - Bot management endpoints</li>
                            <li><strong>/api/dashboard</strong> - Dashboard data</li>
                            <li><strong>/api/broker/positions</strong> - Current trading positions</li>
                            <li><strong>/api/market-overview</strong> - Market overview data</li>
                            <li><strong>/api/portfolio-performance</strong> - Portfolio performance metrics</li>
                            <li><strong>/api/alerts</strong> - Trading alerts</li>
                            <li><strong>/api/dual-bot/signals</strong> - Dual bot trading signals</li>
                            <li><strong>/api/ceo-dashboard</strong> - CEO dashboard metrics</li>
                        </ul>
                    </div>
                </div>
            </body>
            </html>
            """
            return render_template_string(html)
    
    # API info endpoints
    @app.route('/api')
    def api_root():
        return {
            'service': 'AI Trading Bot API',
            'version': '2.0',
            'endpoints': {
                'health': '/api/health',
                'bot': '/api/bot',
                'dashboard': '/api/dashboard',
                'positions': '/api/broker/positions',
                'market-overview': '/api/market-overview',
                'portfolio-performance': '/api/portfolio-performance',
                'alerts': '/api/alerts',
                'dual-bot': '/api/dual-bot/signals',
                'ceo-dashboard': '/api/ceo-dashboard',
                'ceo-settings': '/api/ceo-settings'
            }
        }
    
    return app 

def check_required_files():
    """Check that all required static files exist, create them if needed."""
    try:
        # Get the project root directory
        project_root = os.path.abspath(os.path.dirname(__file__) + '/..')
        index_path = os.path.join(project_root, 'index.html')
        static_dir = os.path.join(project_root, 'static')
        
        logger = logging.getLogger(__name__)
        logger.info(f"Checking required files in {project_root}")
        
        # If index.html or static directory doesn't exist, run setup script
        if not os.path.exists(index_path) or not os.path.exists(static_dir):
            logger.warning("Missing required files. Running setup_static_files.py")
            
            # Import setup function
            import sys
            sys.path.append(project_root)
            
            try:
                from setup_static_files import setup_static_files
                setup_static_files()
                logger.info("Successfully created static files")
            except Exception as e:
                logger.error(f"Error creating static files: {e}")
        else:
            logger.info("All required static files exist")
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error checking required files: {e}") 