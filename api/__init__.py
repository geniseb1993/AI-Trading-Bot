# api package initialization
import os
import logging
from flask import Flask, send_from_directory, send_file, render_template_string, redirect
from flask_cors import CORS

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
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
        app.logger.info("Frontend serving enabled - will serve React frontend from /frontend/build")
        
        # Serve static files from the React build directory
        @app.route('/static/<path:path>')
        def serve_static(path):
            app.logger.info(f"Serving static file: {path}")
            return send_from_directory(os.path.join(os.getcwd(), 'frontend', 'build', 'static'), path)
        
        # Serve manifest.json and other root files
        @app.route('/manifest.json')
        def serve_manifest():
            app.logger.info("Serving manifest.json")
            return send_from_directory(os.path.join(os.getcwd(), 'frontend', 'build'), 'manifest.json')

        @app.route('/favicon.ico')
        def serve_favicon():
            app.logger.info("Serving favicon.ico")
            return send_from_directory(os.path.join(os.getcwd(), 'frontend', 'build'), 'favicon.ico')
            
        @app.route('/logo192.png')
        def serve_logo192():
            app.logger.info("Serving logo192.png")
            return send_from_directory(os.path.join(os.getcwd(), 'frontend', 'build'), 'logo192.png')
        
        @app.route('/logo512.png')
        def serve_logo512():
            app.logger.info("Serving logo512.png") 
            return send_from_directory(os.path.join(os.getcwd(), 'frontend', 'build'), 'logo512.png')
            
        # For all frontend routes (not starting with /api), serve the React index.html
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_react(path):
            # Skip API routes
            if path.startswith('api/'):
                return {"error": "Not Found"}, 404
                
            # Try to serve the file directly if it exists
            try:
                frontend_path = os.path.join(os.getcwd(), 'frontend', 'build', path)
                if os.path.exists(frontend_path) and not os.path.isdir(frontend_path):
                    return send_file(frontend_path)
            except:
                pass
                
            # Otherwise serve index.html for client-side routing to handle
            app.logger.info(f"Serving React app for path: {path}")
            return send_file(os.path.join(os.getcwd(), 'frontend', 'build', 'index.html'))
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