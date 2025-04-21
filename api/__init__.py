# api package initialization
import os
import logging
from flask import Flask
from flask_cors import CORS

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Enable CORS with better configuration
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"]
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
    
    # Simple root endpoint
    @app.route('/')
    def root():
        return {'service': 'AI Trading Bot API', 'status': 'running'}
    
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