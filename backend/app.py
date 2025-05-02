from flask import Flask, jsonify, request, render_template, redirect, url_for, abort, send_file, Response, send_from_directory, render_template_string
from flask_cors import CORS
import pandas as pd
import sys
import os
import random
import logging
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import traceback
import time
import json
import csv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('data', 'logs', f'api_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the current directory to the path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set the static folder to the frontend build directory
static_folder = os.path.join(BASE_DIR, 'frontend', 'build')
if not os.path.exists(static_folder):
    os.makedirs(static_folder, exist_ok=True)
    logging.info(f"Created static folder at {static_folder}")

# Initialize Flask app with static folder configuration
app = Flask(__name__, 
    static_folder=static_folder,
    static_url_path=''
)
CORS(app)

# Additional static folder for compatibility
# This allows serving from /static/ URL path
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from the frontend build static directory"""
    static_path = os.path.join(static_folder, 'static')
    return send_from_directory(static_path, filename)

# Import and register bot routes directly
try:
    from backend.routes.bot_routes import bot_routes
    app.register_blueprint(bot_routes, url_prefix='/api/bot')
    logger.info("Successfully registered bot routes")
except Exception as e:
    try:
        # Try alternative import path
        from routes.bot_routes import bot_routes
        app.register_blueprint(bot_routes, url_prefix='/api/bot')
        logger.info("Successfully registered bot routes from alternative path")
    except Exception as e:
        logger.error(f"Error registering bot routes: {e}")

# Import and register CEO dashboard routes directly
try:
    # Now try to import, but check if it's already registered
    from backend.routes.ceo_dashboard_routes import ceo_dashboard_bp
    if hasattr(app, 'blueprints') and 'ceo_dashboard' not in app.blueprints:
        app.register_blueprint(ceo_dashboard_bp)
        logger.info("Successfully registered CEO dashboard routes")
    else:
        logger.info("CEO dashboard blueprint already registered, skipping")
except Exception as e:
    logger.error(f"Error registering CEO dashboard routes: {e}")

# Import and register dashboard routes
try:
    from backend.routes.dashboard_routes import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    logger.info("Successfully registered dashboard routes")
except Exception as e:
    try:
        # Try alternative import path
        from routes.dashboard_routes import dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/api')
        logger.info("Successfully registered dashboard routes from alternative path")
    except Exception as e:
        logger.error(f"Error registering dashboard routes: {e}")

# Add market data integration
try:
    from backend.lib.market_data import MarketDataSourceManager
    from backend.lib.market_data_config import load_market_data_config, save_market_data_config
    logger.info("Successfully imported market data modules")
except ImportError:
    try:
        # Try alternative import paths
        from lib.market_data import MarketDataSourceManager
        from lib.market_data_config import load_market_data_config, save_market_data_config
        logger.info("Successfully imported market data modules from lib")
    except ImportError:
        logger.warning("Could not import market data modules, using mock implementations")
        # Define fallback implementations
        class MarketDataSourceManager:
            def __init__(self, config=None):
                self.active_source = 'mock'
                self.sources = {'mock': None}
                
            def get_market_data(self, symbols, data_type='bars', timeframe='1Day', limit=100):
                return {'bars': {symbol: [] for symbol in symbols}}
                
            def set_active_source(self, source):
                if source in self.sources:
                    self.active_source = source
                    return True
                return False
        
        def load_market_data_config():
            return {'active_source': 'mock'}
            
        def save_market_data_config(config):
            pass

# Initialize market data manager
try:
    # Check APP_ENV for data source decisions
    app_env = os.environ.get('APP_ENV', 'development')
    logger.info(f"Application environment: {app_env}")
    
    # Load market data configuration
    market_data_config = load_market_data_config()
    
    # Initialize market data manager
    market_data_manager = MarketDataSourceManager(market_data_config)
    
    logger.info(f"Market data manager initialized with source: {market_data_manager.active_source}")
    
    # Check if we should use real data based on environment
    use_real_data = app_env == 'production'
    if use_real_data:
        logger.info("Using REAL market data (production environment)")
    else:
        logger.warning("Using MOCK market data (non-production environment)")
        
except Exception as e:
    logger.error(f"Warning: Could not initialize market data manager: {e}")
    logger.error("Using mock implementation for market data manager")
    market_data_manager = None
    market_data_config = {}

# Import execution model routes
from backend.execution_model.routes import register_routes as register_execution_model_routes

# Import broker integration routes
try:
    from backend.broker_integration.routes import register_routes as register_broker_integration_routes
    register_broker_integration_routes(app)
    logger.info("Broker integration routes registered successfully")
except Exception as e:
    logger.error(f"Failed to register broker routes: {str(e)}")

# Import auto trader routes
from backend.broker_integration.auto_trade_routes import register_routes as register_auto_trade_routes

# Import notification routes
from backend.routes.notification_routes import register_routes as register_notification_routes

# Import risk management routes
from backend.routes.risk_management_routes import register_routes as register_risk_management_routes

# Import market analysis routes
from backend.routes.market_analysis_routes import register_routes as register_market_analysis_routes

# Import TradingView routes directly
try:
    from backend.routes.tradingview_integration import tradingview_bp, register_tradingview_routes
    HAS_TRADINGVIEW = True
except ImportError:
    try:
        from routes.tradingview_integration import tradingview_bp, register_tradingview_routes
        HAS_TRADINGVIEW = True
    except ImportError as e:
        logger.error(f"Failed to import TradingView routes: {e}")
        tradingview_bp = None
        register_tradingview_routes = None
        HAS_TRADINGVIEW = False

# Import autonomous bot routes
try:
    from backend.routes.autonomous_bot_routes import register_routes as register_autonomous_bot_routes
except ImportError:
    try:
        from routes.autonomous_bot_routes import register_routes as register_autonomous_bot_routes  
    except ImportError as e:
        logger.error(f"Error importing autonomous_bot_routes: {e}")
        register_autonomous_bot_routes = None

# Import AI signal ranking routes
try:
    from backend.routes.ai_signal_ranking_routes import register_routes as register_ai_signal_ranking_routes
    register_ai_signal_ranking_routes(app)
    logger.info("Successfully registered AI signal ranking routes")
except Exception as e:
    try:
        # If import fails, check if the module exists in the execution_model
        from backend.execution_model.ai_signal_ranking import AISignalRanking
        from flask import Blueprint, jsonify
        
        # Create a minimal implementation as fallback
        logger.info("Creating fallback AI signal ranking routes")
        ai_bp = Blueprint('ai_signal_ranking', __name__, url_prefix='/api/ai-signal-ranking')
        
        @ai_bp.route('/rank-signals', methods=['POST'])
        def rank_signals():
            return jsonify({
                'success': True,
                'ranked_signals': [],
            })
        
        app.register_blueprint(ai_bp)
        logger.info("Registered fallback AI signal ranking routes")
    except Exception as e:
        logger.error(f"Failed to create fallback AI signal ranking routes: {e}")

# Import bot management routes
try:
    from backend.routes.bot_management import register_routes as register_bot_management_routes
except ImportError:
    try:
        from routes.bot_management import register_routes as register_bot_management_routes
    except ImportError as e:
        logger.error(f"Error importing bot_management: {e}")
        register_bot_management_routes = None

# Import dual bot routes 
try:
    from backend.dual_bot.controller import dual_bot_bp
    app.register_blueprint(dual_bot_bp)
    logger.info("Successfully registered dual bot routes")
except Exception as e:
    logger.error(f"Error registering dual bot routes: {e}")
    try:
        from dual_bot.controller import dual_bot_bp
        app.register_blueprint(dual_bot_bp)
        logger.info("Successfully registered dual bot routes from alternative path")
    except Exception as e:
        logger.error(f"Failed to register dual bot routes from all known paths: {e}")

# Test route to verify server is running
@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint to verify the Flask server is running"""
    app_env = os.environ.get('APP_ENV', 'production')
    return jsonify({
        'success': True,
        'message': 'Flask server is running',
        'timestamp': datetime.now().isoformat(),
        'environment': app_env,
        'version': '2.0'
    })

# Register execution model routes
try:
    register_execution_model_routes(app)
    logger.info("Successfully registered execution model routes")
except Exception as e:
    logger.error(f"Error registering execution model routes: {e}")

# Register auto trader routes
try:
    register_auto_trade_routes(app)
    logger.info("Successfully registered auto trader routes")
except Exception as e:
    logger.error(f"Error registering auto trader routes: {e}")

# Register notification routes
try:
    register_notification_routes(app)
    logger.info("Successfully registered notification routes")
except Exception as e:
    logger.error(f"Error registering notification routes: {e}")

# Register risk management routes
try:
    register_risk_management_routes(app)
    logger.info("Successfully registered risk management routes")
except Exception as e:
    logger.error(f"Error registering risk management routes: {e}")

# Register market analysis routes
try:
    register_market_analysis_routes(app)
    logger.info("Successfully registered market analysis routes")
except Exception as e:
    logger.error(f"Error registering market analysis routes: {e}")

# Register TradingView routes
if HAS_TRADINGVIEW:
    if tradingview_bp:
        try:
            app.register_blueprint(tradingview_bp)
            logger.info("Successfully registered TradingView blueprint")
        except Exception as e:
            logger.error(f"Error registering TradingView blueprint: {e}")
    elif register_tradingview_routes:
        try:
            register_tradingview_routes(app)
            logger.info("Successfully registered TradingView routes via function")
        except Exception as e:
            logger.error(f"Error registering TradingView routes via function: {e}")
    else:
        logger.warning("TradingView integration components not available")
else:
    logger.warning("TradingView integration is not available")

# Register bot management routes
if register_bot_management_routes:
    try:
        register_bot_management_routes(app)
        logger.info("Successfully registered bot management routes")
    except Exception as e:
        logger.error(f"Error registering bot management routes: {e}")

# Register autonomous bot routes
if register_autonomous_bot_routes:
    try:
        register_autonomous_bot_routes(app)
        logger.info("Successfully registered autonomous bot routes")
    except Exception as e:
        logger.error(f"Error registering autonomous bot routes: {e}")

# Add a health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring services"""
    return jsonify({'status': 'healthy'})

@app.route('/api/health')
def api_health_check():
    """API health check endpoint for monitoring services"""
    return jsonify({'status': 'healthy', 'api': 'online'})

# Add root route to serve the frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve the frontend React application"""
    try:
        # If the path exists as a static file, serve it directly
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
            
        # Otherwise, serve the index.html file (for SPA routing)
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        logging.error(f"Error serving frontend: {str(e)}")
        # Fallback to a simple HTML response
        return render_template_string('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>AI Trading Bot</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        background-color: #121212;
                        color: #e1e1e1;
                    }
                    .container {
                        max-width: 800px;
                        padding: 2rem;
                        background-color: #1e1e1e;
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
                    <div class="status">API Status: Running</div>
                    <p>The API server is operational and ready to process requests.</p>
                    <p>However, the frontend assets could not be loaded.</p>
                </div>
            </body>
        </html>
        ''')

if __name__ == '__main__':
    # Print all registered routes for debugging
    print("\n=== REGISTERED ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule.endpoint} -> {rule.rule}")
    print("=========================\n")
    
    try:
        port = int(os.environ.get('PORT', 5000))
        print("Starting Flask server...")
        print(f"Server running at: http://localhost:{port}")
        print(f"Test endpoint: http://localhost:{port}/api/test")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"Error starting Flask server: {str(e)}")
        import traceback
        traceback.print_exc() 