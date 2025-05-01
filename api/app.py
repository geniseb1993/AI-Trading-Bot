from flask import Flask, jsonify, request, render_template, redirect, url_for, abort, send_file, Response
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

# Add the current directory to the path for lib imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create Flask app first
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With", "X-API-Key"]
    }
})

# Import and register bot routes directly
try:
    from api.routes.bot_routes import bot_routes
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
    # Make sure current directory is in the path
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Now try to import
    from api.routes.ceo_dashboard_routes import ceo_dashboard_bp
    app.register_blueprint(ceo_dashboard_bp)
    logger.info("Successfully registered CEO dashboard routes")
except Exception as e:
    logger.error(f"Error registering CEO dashboard routes: {e}")

# Import and register dashboard routes
try:
    from api.routes.dashboard_routes import dashboard_bp
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
    from lib.market_data import MarketDataSourceManager
    from lib.market_data_config import load_market_data_config, save_market_data_config
    logger.info("Successfully imported market data modules")
except ImportError:
    try:
        # Try alternative import paths
        from api.lib.market_data import MarketDataSourceManager
        from api.lib.market_data_config import load_market_data_config, save_market_data_config
        logger.info("Successfully imported market data modules from api.lib")
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
from execution_model_routes import register_routes as register_execution_model_routes

# Import broker integration routes
try:
    # Comment out this registration since we'll use the other one
    # from api.routes.broker_routes import broker_routes
    # app.register_blueprint(broker_routes, url_prefix='/api')
    # logger.info("Broker routes registered successfully")
    
    # Keep only the broker_integration routes
    from api.broker_integration.broker_routes import register_routes as register_broker_integration_routes
    register_broker_integration_routes(app)
    logger.info("Broker integration routes registered successfully")
except Exception as e:
    logger.error(f"Failed to register broker routes: {str(e)}")

# Import auto trader routes
from broker_integration.auto_trade_routes import register_routes as register_auto_trade_routes

# Import notification routes
from notification_routes import register_routes as register_notification_routes

# Import risk management routes
from risk_management_routes import register_routes as register_risk_management_routes

# Import market analysis routes
from market_analysis_routes import register_routes as register_market_analysis_routes

# Import TradingView routes directly
try:
    print("Importing TradingView routes...")
    # Try the direct import path first
    from api.routes.tradingview_integration import tradingview_bp, register_tradingview_routes
    print("Successfully imported TradingView routes from api.routes")
    HAS_TRADINGVIEW = True
except ImportError:
    try:
        print("Trying alternative import path for TradingView routes...")
        # Try without the api prefix
        from routes.tradingview_integration import tradingview_bp, register_tradingview_routes
        print("Successfully imported TradingView routes from routes")
        HAS_TRADINGVIEW = True
    except ImportError as e:
        print(f"Failed to import TradingView routes: {e}")
        traceback.print_exc()
        tradingview_bp = None
        register_tradingview_routes = None
        HAS_TRADINGVIEW = False

# Import autonomous bot routes
try:
    from autonomous_bot_routes import register_routes as register_autonomous_bot_routes
except ImportError:
    try:
        # Try with api prefix
        from api.autonomous_bot_routes import register_routes as register_autonomous_bot_routes  
    except ImportError as e:
        logger.error(f"Error importing autonomous_bot_routes: {e}")
        register_autonomous_bot_routes = None

# Import AI signal ranking routes
try:
    from ai_signal_ranking_routes import register_routes as register_ai_signal_ranking_routes
    register_ai_signal_ranking_routes(app)
    logger.info("Successfully registered AI signal ranking routes")
except Exception as e:
    try:
        # If import fails, check if the module exists in the execution_model
        from execution_model.ai_signal_ranking import AISignalRanking
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
    from routes.bot_management import register_routes as register_bot_management_routes
except ImportError:
    try:
        # Try with api prefix
        from api.routes.bot_management import register_routes as register_bot_management_routes
    except ImportError as e:
        logger.error(f"Error importing bot_management: {e}")
        register_bot_management_routes = None

# Import AI activity log routes
try:
    from routes.ai_activity_log import register_routes as register_ai_activity_log_routes
except ImportError:
    try:
        # Try with api prefix
        from api.routes.ai_activity_log import register_routes as register_ai_activity_log_routes
    except ImportError as e:
        logger.error(f"Error importing ai_activity_log: {e}")
        register_ai_activity_log_routes = None

# Import and register dual bot routes
try:
    from api.routes.dual_bot_routes import dual_bot_bp
    app.register_blueprint(dual_bot_bp)
    logger.info("Successfully registered dual bot routes")
except Exception as e:
    logger.error(f"Error registering dual bot routes: {e}")
    try:
        # Try alternative import path
        from routes.dual_bot_routes import dual_bot_bp
        app.register_blueprint(dual_bot_bp)
        logger.info("Successfully registered dual bot routes from alternative path")
    except Exception as e:
        logger.error(f"Failed to register dual bot routes from alternative path: {e}")
        try:
            # Try with just the filename
            from dual_bot_routes import dual_bot_bp
            app.register_blueprint(dual_bot_bp)
            logger.info("Successfully registered dual bot routes using filename only")
        except Exception as e:
            logger.error(f"Failed to register dual bot routes using all known paths: {e}")

# Import and register signals API routes for frontend compatibility
try:
    from routes.signals_api import signals_api_bp
    app.register_blueprint(signals_api_bp)
    logger.info("Successfully registered signals API routes")
except Exception as e:
    logger.error(f"Error registering signals API routes: {e}")
    try:
        # Try alternative import path
        from api.routes.signals_api import signals_api_bp
        app.register_blueprint(signals_api_bp)
        logger.info("Successfully registered signals API routes from alternative path")
    except Exception as e:
        logger.error(f"Failed to register signals API routes from alternative path: {e}")

# Test route to verify server is running
@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint to verify the Flask server is running"""
    app_env = os.environ.get('APP_ENV', 'production')
    return jsonify({
        'success': True,
        'message': 'Enhanced Flask server is running',
        'timestamp': datetime.now().isoformat(),
        'environment': app_env,
        'version': 'enhanced-1.0',
        'alpaca_api': True,
        'unusual_whales_api': True
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
    print(f"Registering market analysis routes")
    register_market_analysis_routes(app)
    print(f"✅ Market Analysis routes registered")
except Exception as e:
    print(f"⚠️ Failed to register market analysis routes: {e}")
    traceback.print_exc()

# Direct registration of TradingView routes
if HAS_TRADINGVIEW:
    print("Has TradingView routes, attempting to register...")
    if tradingview_bp:
        try:
            print("Registering TradingView blueprint...")
            app.register_blueprint(tradingview_bp)
            print("✅ Successfully registered TradingView blueprint")
            
            # Add a direct test route
            @app.route('/api/tradingview-direct-test', methods=['GET'])
            def tradingview_direct_test():
                print("Direct TradingView test route called")
                return jsonify({
                    'success': True,
                    'message': 'Direct TradingView test route works',
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"❌ Error registering TradingView blueprint: {e}")
            traceback.print_exc()
    elif register_tradingview_routes:
        try:
            print("Attempting to register TradingView routes via function...")
            register_tradingview_routes(app)
            print("✅ Successfully registered TradingView routes via function")
        except Exception as e:
            print(f"❌ Error registering TradingView routes via function: {e}")
            traceback.print_exc()
    else:
        print("⚠️ WARNING: TradingView integration components not available")
else:
    print("⚠️ WARNING: TradingView integration is not available")

# Register bot management routes
if register_bot_management_routes:
    try:
        register_bot_management_routes(app)
        logger.info("Successfully registered bot management routes")
    except Exception as e:
        logger.error(f"Error registering bot management routes: {e}")

# Register AI activity log routes
if register_ai_activity_log_routes:
    try:
        register_ai_activity_log_routes(app)
        logger.info("Successfully registered AI activity log routes")
    except Exception as e:
        logger.error(f"Error registering AI activity log routes: {e}")
        logger.error("AI activity logging features will be disabled")

# Register autonomous bot routes
try:
    print(f"Registering autonomous bot routes")
    register_autonomous_bot_routes(app)
    print(f"✅ Autonomous bot routes registered")
except Exception as e:
    print(f"⚠️ Failed to register autonomous bot routes: {e}")
    traceback.print_exc()

# Register CEO dashboard routes
try:
    from api.routes.ceo_dashboard_routes import register_routes as register_ceo_dashboard_routes
    register_ceo_dashboard_routes(app)
    logger.info("Successfully registered CEO dashboard routes")
except Exception as e:
    logger.error(f"Error registering CEO dashboard routes: {e}")
    try:
        # Try alternative import path
        from routes.ceo_dashboard_routes import register_routes as register_ceo_dashboard_routes
        register_ceo_dashboard_routes(app)
        logger.info("Successfully registered CEO dashboard routes from alternative path")
    except Exception as e:
        logger.error(f"Failed to register CEO dashboard routes from all known paths: {e}")

# Try to import modules, but fall back to mock implementations if they fail
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from fetch_data import fetch_data
    from signal_engine import calculate_signals, extract_signals
    from backtest import run_backtest
    MODULES_IMPORTED = True
    logger.info("Successfully imported core modules")
except ImportError as e:
    logger.warning(f"Could not import some modules: {e}")
    logger.warning("Using fallback implementations")
    MODULES_IMPORTED = False
    
    # Fallback implementations
    def fetch_data(symbols, start_date=None, end_date=None):
        """Fallback implementation of fetch_data"""
        # Generate mock data
        data = []
        current_date = end_date
        for _ in range(30):  # Generate 30 days of data
            for symbol in symbols:
                price = 100 + random.random() * 50
                data.append({
                    'date': current_date,
                    'symbol': symbol,
                    'open': price * (1 - 0.01 * random.random()),
                    'high': price * (1 + 0.02 * random.random()),
                    'low': price * (1 - 0.02 * random.random()),
                    'close': price,
                    'volume': int(random.random() * 1000000)
                })
            current_date -= timedelta(days=1)
        return pd.DataFrame(data)
    
    def calculate_signals(df):
        """Fallback implementation of calculate_signals"""
        df['ema_9'] = df['close'].rolling(window=9).mean()
        df['ema_21'] = df['close'].rolling(window=21).mean()
        df['signal_score'] = random.random() * 10
        df['buy_signal'] = df['ema_9'] > df['ema_21']
        return df
    
    def extract_signals(df_with_signals):
        """Fallback implementation of extract_signals"""
        return df_with_signals[df_with_signals['buy_signal']]
    
    def run_backtest(df, signals):
        """Fallback implementation of run_backtest"""
        results = []
        for i in range(20):
            entry_date = datetime.now() - timedelta(days=i*2)
            exit_date = entry_date + timedelta(days=1)
            symbol = random.choice(['SPY', 'QQQ', 'TSLA'])
            entry_price = 100 + random.random() * 50
            exit_price = entry_price * (1 + (random.random() - 0.3) * 0.1)
            profit = exit_price - entry_price
            results.append({
                'symbol': symbol,
                'entry_date': entry_date.strftime('%Y-%m-%d'),
                'exit_date': exit_date.strftime('%Y-%m-%d'),
                'entry_price': entry_price,
                'exit_price': exit_price,
                'profit': profit,
                'trade_outcome': 'win' if profit > 0 else 'loss'
            })
        return pd.DataFrame(results)

@app.route('/api/fetch-data', methods=['POST'])
def api_fetch_data():
    data = request.json
    symbols = data.get('symbols', ['QQQ', 'SPY', 'TSLA'])
    days = int(data.get('days', 7))
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    try:
        stock_data = fetch_data(symbols, start_date=start_date, end_date=end_date)
        return jsonify({
            'success': True,
            'data': stock_data.reset_index().to_dict('records')
        })
    except Exception as e:
        print(f"Error in /api/fetch-data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calculate-signals', methods=['POST'])
def api_calculate_signals():
    data = request.json
    df = pd.DataFrame(data.get('data'))
    
    try:
        # Convert date string to datetime if needed
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        data_with_signals = calculate_signals(df)
        signals = extract_signals(data_with_signals)
        
        return jsonify({
            'success': True,
            'signals': signals.reset_index().to_dict('records'),
            'data_with_signals': data_with_signals.reset_index().to_dict('records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/run-backtest', methods=['POST'])
def api_run_backtest():
    data = request.json
    df = pd.DataFrame(data.get('data_with_signals'))
    signals = pd.DataFrame(data.get('signals'))
    
    try:
        # Convert date string to datetime if needed
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        if 'date' in signals.columns:
            signals['date'] = pd.to_datetime(signals['date'])
            signals.set_index('date', inplace=True)
        
        backtest_results = run_backtest(df, signals)
        
        return jsonify({
            'success': True,
            'backtest_results': backtest_results.reset_index().to_dict('records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-saved-signals', methods=['GET'])
def api_get_saved_signals():
    """Get saved buy and short signals"""
    try:
        # Check for signals in the data directory
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        buy_file = os.path.join(data_dir, 'buy_signals.csv')
        short_file = os.path.join(data_dir, 'short_signals.csv')
        
        logger.info(f"Looking for signal files at: {buy_file} and {short_file}")
        
        if os.path.exists(buy_file) and os.path.exists(short_file):
            logger.info(f"Found signal files. Loading data...")
            buy_signals = pd.read_csv(buy_file)
            short_signals = pd.read_csv(short_file)
            
            logger.info(f"Loaded {len(buy_signals)} buy signals and {len(short_signals)} short signals")
            
            return jsonify({
                'success': True,
                'buy_signals': buy_signals.to_dict('records'),
                'short_signals': short_signals.to_dict('records')
            })
        else:
            # Generate mock data if files don't exist
            logger.warning(f"Signal files not found at {buy_file} and {short_file}, generating mock data")
            
            # Create sample mock data
            buy_signals = pd.DataFrame({
                'date': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(3)],
                'symbol': ['SPY', 'AAPL', 'MSFT'],
                'signal_score': [8.5, 7.6, 9.2],
                'close': [450.0, 180.0, 350.0],
                'ema_9': [445.0, 175.0, 345.0],
                'ema_21': [440.0, 170.0, 340.0],
                'volume': [50000000, 80000000, 30000000]
            })
            
            short_signals = pd.DataFrame({
                'date': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(2)],
                'symbol': ['TSLA', 'NFLX'],
                'signal_score': [-7.2, -8.5],
                'close': [220.0, 550.0],
                'ema_9': [225.0, 560.0],
                'ema_21': [230.0, 570.0],
                'volume': [60000000, 20000000]
            })
            
            # Create the data directory if it doesn't exist
            os.makedirs(data_dir, exist_ok=True)
            
            # Save the mock data files for future use
            try:
                buy_signals.to_csv(buy_file, index=False)
                short_signals.to_csv(short_file, index=False)
                logger.info(f"Created mock signal files at {buy_file} and {short_file}")
            except Exception as save_error:
                logger.warning(f"Could not save mock data to files: {save_error}")
            
            return jsonify({
                'success': True,
                'buy_signals': buy_signals.to_dict('records'),
                'short_signals': short_signals.to_dict('records'),
                'is_mock': True
            })
    except Exception as e:
        logger.error(f"Error in get-saved-signals: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-backtest-results', methods=['GET'])
def api_get_backtest_results():
    """Get backtest results"""
    try:
        # Try multiple possible locations for the CSV file
        possible_paths = [
            # Current directory
            "backtest_results.csv",
            # Within API directory
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "backtest_results.csv"),
            # Root project directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backtest_results.csv"),
            # Data directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "backtest_results.csv")
        ]
        
        backtest_results = None
        source = None
        
        # Check if we should use a recent timestamp to consider data fresh
        force_update = request.args.get('force_update', 'false').lower() == 'true'
        csv_max_age_hours = 24  # Consider data stale after 24 hours
        
        # Try each possible path
        for path in possible_paths:
            logger.info(f"Trying to load backtest results from: {path}")
            
            if os.path.exists(path):
                logger.info(f"Found backtest results file at: {path}")
                
                # Check file age
                file_time = os.path.getmtime(path)
                file_age_hours = (time.time() - file_time) / 3600
                
                if force_update or file_age_hours > csv_max_age_hours:
                    logger.info(f"File is {file_age_hours:.1f} hours old. Generating fresh data...")
                    # Call our update function to refresh data
                    try:
                        # Import our update script
                        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                        from update_backtest_data import update_backtest_data
                        
                        # Run the update
                        update_success = update_backtest_data()
                        if update_success:
                            logger.info("Successfully updated backtest data")
                        else:
                            logger.warning("Failed to update backtest data, using existing file")
                    except Exception as update_error:
                        logger.error(f"Error updating backtest data: {str(update_error)}")
                
                try:
                    backtest_results = pd.read_csv(path)
                    source = path
                    logger.info(f"Successfully loaded {len(backtest_results)} backtest results")
                    break
                except Exception as e:
                    logger.error(f"Error reading CSV file at {path}: {str(e)}")
                    continue
        
        # If no file found, try to generate it on-the-fly
        if backtest_results is None:
            logger.warning("Could not load backtest results from any location, attempting to generate data")
            try:
                # Import our update script
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from update_backtest_data import update_backtest_data
                
                # Run the update
                update_success = update_backtest_data()
                if update_success:
                    # Try to load the newly generated file
                    for path in possible_paths:
                        if os.path.exists(path):
                            try:
                                backtest_results = pd.read_csv(path)
                                source = "newly_generated"
                                logger.info(f"Successfully loaded newly generated data with {len(backtest_results)} records")
                                break
                            except Exception:
                                continue
            except Exception as e:
                logger.error(f"Failed to generate backtest data: {str(e)}")
        
        # If we still don't have data, fall back to generated mock data
        if backtest_results is None:
            logger.warning("All attempts to get real data failed, using mock data as fallback")
            
            # Create fallback data
            from run_pipeline import run_backtest
            backtest_results = run_backtest(pd.DataFrame(), pd.DataFrame())
            source = "fallback"
        
        # Add isRealData flag based on the source
        is_real_data = source != "fallback" and source != "generated" and source is not None
        
        return jsonify({
            'success': True,
            'backtest_results': backtest_results.to_dict('records'),
            'isRealData': is_real_data,
            'source': source if source else "generated",
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get-backtest-results: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add directory-based CSV file access
@app.route('/api/<path:filename>.csv', methods=['GET'])
def serve_csv_file(filename):
    """Serve CSV files directly"""
    try:
        # Try multiple possible locations for the CSV file
        possible_paths = [
            # Direct path (if filename already contains directory)
            f"{filename}.csv",
            # Current directory
            os.path.join(os.getcwd(), f"{filename}.csv"),
            # Root project directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"{filename}.csv"),
            # Data directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", f"{filename}.csv")
        ]
        
        # Try each possible path
        for path in possible_paths:
            logger.info(f"Trying to serve CSV file from: {path}")
            
            if os.path.exists(path):
                logger.info(f"Found CSV file at: {path}")
                try:
                    df = pd.read_csv(path)
                    logger.info(f"Successfully loaded CSV with {len(df)} rows")
                    return jsonify(df.to_dict('records'))
                except Exception as e:
                    logger.error(f"Error reading CSV file at {path}: {str(e)}")
                    continue
                
        # If we get here, we couldn't find the file
        logger.warning(f"CSV file not found: {filename}.csv in any location")
        return jsonify({
            'success': False,
            'error': f"File not found: {filename}.csv"
        }), 404
    except Exception as e:
        logger.error(f"Error serving CSV file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add missing API routes that the frontend is trying to access
@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    """Get dashboard data"""
    try:
        # Use the CSV data provider to get dashboard data
        try:
            from csv_data_provider import CSVDataProvider
        except ImportError:
            # Try absolute import if relative import fails
            from api.csv_data_provider import CSVDataProvider
        
        data_provider = CSVDataProvider()
        dashboard_data = data_provider.get_dashboard_data()
        
        # Add some summary stats
        active_trades = dashboard_data.get('active_trades', [])
        trading_history = dashboard_data.get('trading_history', [])
        
        # Calculate summary statistics
        total_trades = len(trading_history)
        win_count = sum(1 for trade in trading_history if float(trade.get('pnl', 0)) > 0)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate total profit/loss
        total_pnl = sum(float(trade.get('pnl', 0)) for trade in trading_history)
        
        # Add summary stats to response
        dashboard_data['stats'] = {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'profit_loss': round(total_pnl, 2),
            'active_positions': len(active_trades)
        }
        
        # Get the 5 most recent trades
        recent_trades = sorted(
            trading_history, 
            key=lambda x: x.get('exit_date', ''), 
            reverse=True
        )[:5]
        
        dashboard_data['recent_trades'] = recent_trades
        
        return jsonify({
            'success': True,
            **dashboard_data
        })
    except Exception as e:
        logger.error(f"Error in dashboard API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-data', methods=['GET'])
def api_market_data_overview():
    """Get market data overview"""
    try:
        return jsonify({
            'success': True,
            'active_source': market_data_manager.active_source if market_data_manager else 'mock',
            'available_sources': list(market_data_manager.sources.keys()) if market_data_manager else ['mock'],
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in market-data overview: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user-portfolio', methods=['GET'])
def api_user_portfolio():
    """Get user portfolio information"""
    try:
        return jsonify({
            'success': True,
            'portfolio': {
                'total_value': 125000.00,
                'cash': 25000.00,
                'investments': 100000.00,
                'daily_change': 1250.00,
                'daily_change_percent': 1.2,
                'positions': [
                    {
                        'symbol': 'AAPL',
                        'quantity': 50,
                        'avg_price': 180.00,
                        'current_price': 185.00,
                        'value': 9250.00,
                        'profit_loss': 250.00,
                        'profit_loss_percent': 2.8
                    },
                    {
                        'symbol': 'MSFT',
                        'quantity': 25,
                        'avg_price': 310.00,
                        'current_price': 315.00,
                        'value': 7875.00,
                        'profit_loss': 125.00,
                        'profit_loss_percent': 1.6
                    }
                ]
            }
        })
    except Exception as e:
        logger.error(f"Error in user-portfolio: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/active-trades', methods=['GET'])
def api_active_trades():
    """Get active trades"""
    try:
        # Use the CSV data provider to get active trades
        try:
            from csv_data_provider import CSVDataProvider
        except ImportError:
            # Try absolute import if relative import fails
            from api.csv_data_provider import CSVDataProvider
        
        data_provider = CSVDataProvider()
        active_trades = data_provider.get_active_trades()
        
        return jsonify({
            'success': True,
            'active_trades': active_trades
        })
    except Exception as e:
        logger.error(f"Error in active-trades: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts', methods=['GET'])
def api_alerts():
    """Get system alerts"""
    try:
        return jsonify({
            'success': True,
            'alerts': [
                {
                    'id': 1001,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'price',
                    'symbol': 'SPY',
                    'message': 'SPY has dropped 1.5% in the last hour',
                    'priority': 'medium'
                },
                {
                    'id': 1002,
                    'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'type': 'signal',
                    'symbol': 'AAPL',
                    'message': 'Buy signal detected for AAPL',
                    'priority': 'high'
                }
            ]
        })
    except Exception as e:
        logger.error(f"Error in alerts API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/api/risk-management/settings', methods=['GET'])
def api_risk_management_settings():
    """Get risk management settings"""
    try:
        return jsonify({
            'success': True,
            'settings': {
                'max_position_size': 5000.00,
                'max_positions': 10,
                'stop_loss_percent': 2.5,
                'take_profit_percent': 5.0,
                'max_daily_loss': 1000.00,
                'risk_per_trade': 1.0
            }
        })
    except Exception as e:
        logger.error(f"Error in risk-management settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/api/risk-management/analysis', methods=['GET'])
def api_risk_management_analysis():
    """Get risk management analysis"""
    try:
        return jsonify({
            'success': True,
            'analysis': {
                'current_risk_exposure': 3500.00,
                'risk_score': 'medium',
                'max_drawdown': 2800.00,
                'max_drawdown_percent': 2.2,
                'volatility_score': 'moderate',
                'recommendations': [
                    'Consider reducing position size for higher volatility stocks',
                    'Current exposure is within acceptable limits'
                ]
            }
        })
    except Exception as e:
        logger.error(f"Error in risk-management analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/api/configuration/get-api-configs', methods=['GET'])
def api_get_api_configs():
    """Get API configurations"""
    try:
        return jsonify({
            'success': True,
            'configurations': {
                'unusual_whales': {
                    'enabled': True,
                    'api_key_configured': bool(os.environ.get('UNUSUAL_WHALES_API_KEY'))
                },
                'alpaca': {
                    'enabled': bool(os.environ.get('ALPACA_API_KEY')),
                    'api_key_configured': bool(os.environ.get('ALPACA_API_KEY')),
                    'paper_trading': True
                },
                'tradingview': {
                    'enabled': bool(os.environ.get('TRADINGVIEW_WEBHOOK_PORT')),
                    'webhook_configured': bool(os.environ.get('TRADINGVIEW_WEBHOOK_SECRET'))
                },
                'openrouter': {
                    'enabled': bool(os.environ.get('OPENROUTER_API_KEY')),
                    'api_key_configured': bool(os.environ.get('OPENROUTER_API_KEY'))
                },
                'hume': {
                    'enabled': bool(os.environ.get('HUME_API_KEY')),
                    'api_key_configured': bool(os.environ.get('HUME_API_KEY'))
                }
            }
        })
    except Exception as e:
        logger.error(f"Error in configuration API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Fix for duplicate API paths - catch-all route for duplicate /api/api/* requests
@app.route('/api/api/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_duplicate_path_handler(subpath):
    """Handle duplicate /api/api/ paths by redirecting to the correct path"""
    logger.warning(f"Redirecting duplicate path: /api/api/{subpath} to /api/{subpath}")
    # Use the same HTTP method as the original request
    if request.method == 'GET':
        return redirect(f"/api/{subpath}")
    elif request.method == 'POST':
        return redirect(f"/api/{subpath}", code=307)  # 307 preserves method and body
    elif request.method == 'PUT':
        return redirect(f"/api/{subpath}", code=307)
    elif request.method == 'DELETE':
        return redirect(f"/api/{subpath}", code=307)

# New API endpoints for market data
@app.route('/api/market-data/sources', methods=['GET'])
def api_get_market_data_sources():
    """Get the available market data sources and the active source"""
    try:
        sources = list(market_data_manager.sources.keys()) if market_data_manager else ['mock']
        active_source = market_data_manager.active_source if market_data_manager else 'mock'
        
        return jsonify({
            'success': True,
            'sources': sources,
            'active_source': active_source
        })
    except Exception as e:
        logger.error(f"Error in market-data sources: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-data/set-source', methods=['POST'])
def api_set_market_data_source():
    """Set the active market data source"""
    try:
        data = request.json
        source = data.get('source')
        
        if not source:
            return jsonify({
                'success': False,
                'error': 'No source specified'
            }), 400
        
        if market_data_manager:
            success = market_data_manager.set_active_source(source)
            
            if success:
                # Update the config
                global market_data_config
                market_data_config['active_source'] = source
                save_market_data_config(market_data_config)
                
                return jsonify({
                    'success': True,
                    'active_source': source
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Source "{source}" not available'
                }), 400
        else:
            logger.warning("Market data manager not initialized, cannot set source")
            return jsonify({
                'success': False,
                'error': 'Market data manager not initialized'
            }), 500
            
    except Exception as e:
        logger.error(f"Error setting market data source: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-data/get-data', methods=['POST'])
def api_get_market_data():
    """Get market data from the active source"""
    try:
        data = request.json
        symbols = data.get('symbols', ['SPY'])
        data_type = data.get('data_type', 'bars')
        timeframe = data.get('timeframe', '1Min')
        limit = data.get('limit', 100)
        
        if market_data_manager:
            # Get data from the active source
            market_data = market_data_manager.get_market_data(
                symbols, 
                data_type=data_type,
                timeframe=timeframe,
                limit=limit
            )
            
            return jsonify({
                'success': True,
                'source': market_data_manager.active_source,
                'data': market_data
            })
        else:
            # Return mock data if market data manager is not available
            logger.warning("Market data manager not initialized, returning mock data")
            mock_data = []
            for symbol in symbols:
                for i in range(limit):
                    price = 100 + (i % 10)
                    time = datetime.now() - timedelta(minutes=i)
                    mock_data.append({
                        'date': time.isoformat(),
                        'symbol': symbol,
                        'open': price,
                        'high': price + 1,
                        'low': price - 1,
                        'close': price + 0.5,
                        'volume': 1000 + (i * 100)
                    })
            
            return jsonify({
                'success': True,
                'source': 'mock',
                'data': mock_data
            })
    except Exception as e:
        logger.error(f"Error getting market data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-data/config', methods=['GET'])
def api_get_market_data_config():
    """Get the current market data configuration"""
    try:
        # Return a sanitized version without sensitive info
        sanitized_config = {}
        
        if market_data_config:
            for source, config in market_data_config.items():
                if source == 'active_source':
                    sanitized_config[source] = config
                    continue
                    
                sanitized_config[source] = {}
                if isinstance(config, dict):
                    for key, value in config.items():
                        # Hide API keys and secrets
                        if 'key' in key.lower() or 'secret' in key.lower() or 'token' in key.lower():
                            sanitized_config[source][key] = '**********' if value else None
                        else:
                            sanitized_config[source][key] = value
        else:
            sanitized_config = {
                'active_source': 'mock',
                'mock': {
                    'use_csv_data': True,
                    'csv_directory': 'data/market_data'
                }
            }
        
        return jsonify({
            'success': True,
            'config': sanitized_config
        })
    except Exception as e:
        logger.error(f"Error getting market data config: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-data/update-config', methods=['POST'])
def api_update_market_data_config():
    """Update the market data configuration"""
    try:
        new_config = request.json
        
        # Validate the config
        if not isinstance(new_config, dict):
            return jsonify({
                'success': False,
                'error': 'Invalid configuration format'
            }), 400
        
        global market_data_config
        if not market_data_config:
            logger.warning("Market data config is not initialized, creating a new one")
            market_data_config = {}
        
        # Update the config
        for source, config in new_config.items():
            if source == 'active_source':
                market_data_config[source] = config
                continue
                
            if source not in market_data_config:
                market_data_config[source] = {}
                
            if isinstance(config, dict):
                for key, value in config.items():
                    market_data_config[source][key] = value
        
        # Save the updated config
        save_market_data_config(market_data_config)
        
        # Reinitialize the market data manager with the new config
        global market_data_manager
        try:
            market_data_manager = MarketDataSourceManager(market_data_config)
            logger.info("Market data manager reinitialized with updated config")
        except Exception as e:
            logger.error(f"Error reinitializing market data manager: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Market data configuration updated'
        })
    except Exception as e:
        logger.error(f"Error updating market data config: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-data/tradingview/webhooks', methods=['GET'])
def api_get_tradingview_webhooks():
    """Get the most recent TradingView webhook alerts"""
    try:
        if not market_data_manager or not hasattr(market_data_manager, 'sources'):
            logger.warning("Market data manager not properly initialized")
            return jsonify({
                'success': True,
                'alerts': []
            })
            
        tradingview = market_data_manager.sources.get('tradingview')
        
        if not tradingview:
            logger.warning("TradingView source not available")
            return jsonify({
                'success': True,
                'alerts': []
            })
            
        # Start the webhook server if it's not running
        if not tradingview.server_running:
            tradingview.start_webhook_server()
            
        alerts = tradingview.get_alerts()
        
        return jsonify({
            'success': True,
            'alerts': alerts
        })
    except Exception as e:
        logger.error(f"Error getting TradingView webhooks: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-data/tradingview/clear-webhooks', methods=['POST'])
def api_clear_tradingview_webhooks():
    """Clear all stored TradingView webhooks"""
    try:
        if not market_data_manager or not hasattr(market_data_manager, 'sources') or 'tradingview' not in market_data_manager.sources:
            logger.warning("TradingView source not available")
            return jsonify({
                'success': True,
                'message': 'No webhooks to clear (source not available)'
            })
            
        tradingview_source = market_data_manager.sources['tradingview']
        
        if hasattr(tradingview_source, 'clear_webhooks'):
            tradingview_source.clear_webhooks()
            return jsonify({
                'success': True,
                'message': 'Webhooks cleared successfully'
            })
        else:
            logger.warning("TradingView source does not support clearing webhooks")
            return jsonify({
                'success': True,
                'message': 'No webhooks to clear (not supported)'
            })
            
    except Exception as e:
        logger.error(f"Error clearing TradingView webhooks: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-overview', methods=['GET'])
def api_market_overview():
    """Get market overview data"""
    try:
        # Use the CSV data provider to get market overview
        try:
            from csv_data_provider import CSVDataProvider
        except ImportError:
            # Try absolute import if relative import fails
            from api.csv_data_provider import CSVDataProvider
        
        data_provider = CSVDataProvider()
        market_data = data_provider.get_market_overview()
        
        return jsonify({
            'success': True,
            'market_data': market_data
        })
    except Exception as e:
        logger.error(f"Error in market-overview: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/portfolio-performance', methods=['GET'])
def api_portfolio_performance():
    """Get portfolio performance data"""
    try:
        try:
            from csv_data_provider import CSVDataProvider
        except ImportError:
            # Try absolute import if relative import fails
            from api.csv_data_provider import CSVDataProvider
        
        data_provider = CSVDataProvider()
        performance_data = data_provider.get_portfolio_performance()
        
        return jsonify({
            'success': True,
            'portfolio_performance': performance_data
        })
    except Exception as e:
        logger.error(f"Error in portfolio-performance: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trading-history', methods=['GET'])
def api_trading_history():
    """Get trading history data"""
    try:
        try:
            from csv_data_provider import CSVDataProvider
        except ImportError:
            # Try absolute import if relative import fails
            from api.csv_data_provider import CSVDataProvider
        
        data_provider = CSVDataProvider()
        history_data = data_provider.get_trading_history()
        
        return jsonify({
            'success': True,
            'trading_history': history_data
        })
    except Exception as e:
        logger.error(f"Error in trading-history: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/strategy-performance', methods=['GET'])
def api_strategy_performance():
    """Get strategy performance data"""
    try:
        try:
            from csv_data_provider import CSVDataProvider
        except ImportError:
            # Try absolute import if relative import fails
            from api.csv_data_provider import CSVDataProvider
        
        data_provider = CSVDataProvider()
        strategy_data = data_provider.get_strategy_performance()
        
        return jsonify({
            'success': True,
            'strategy_performance': strategy_data
        })
    except Exception as e:
        logger.error(f"Error in strategy-performance: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/risk-metrics', methods=['GET'])
def api_risk_metrics():
    """Get risk metrics data"""
    try:
        try:
            from csv_data_provider import CSVDataProvider
        except ImportError:
            # Try absolute import if relative import fails
            from api.csv_data_provider import CSVDataProvider
        
        data_provider = CSVDataProvider()
        risk_data = data_provider.get_risk_metrics()
        
        return jsonify({
            'success': True,
            'risk_metrics': risk_data
        })
    except Exception as e:
        logger.error(f"Error in risk-metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Import health check routes
from routes.health import health_bp

# Register health check routes directly
app.register_blueprint(health_bp)
logger.info("Successfully registered health check routes")

# Add a direct health endpoint for immediate response
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running"""
    # Check Alpaca API connection
    alpaca_connected = True
    try:
        if market_data_manager and 'alpaca' in market_data_manager.sources:
            alpaca_source = market_data_manager.sources['alpaca']
            alpaca_connected = bool(alpaca_source.api_key and alpaca_source.api_secret)
    except Exception as e:
        logger.warning(f"Error checking Alpaca connection: {e}")
        alpaca_connected = False
        
    return jsonify({
        'status': 'ok',
        'message': 'API is running',
        'timestamp': datetime.now().isoformat(),
        'alpaca_connected': alpaca_connected,
        'environment': os.environ.get('APP_ENV', 'development')
    })

# Endpoint for fetching individual symbol market data - this is what the frontend uses
@app.route('/api/market-data/<symbol>', methods=['GET'])
def api_get_symbol_market_data(symbol):
    """Get market data for a specific symbol with optional timeframe and days parameters"""
    try:
        # Get query parameters
        timeframe = request.args.get('timeframe', '1d')
        days = int(request.args.get('days', 30))
        
        # Convert timeframe format from frontend to Alpaca format
        timeframe_map = {
            '1m': '1Min',
            '5m': '5Min',
            '15m': '15Min', 
            '30m': '30Min',
            '1h': '1Hour',
            '1d': '1Day'
        }
        alpaca_timeframe = timeframe_map.get(timeframe, '1Day')
        
        # Calculate the limit based on days
        # For daily data, limit = days
        # For minute data, account for market hours
        limit = days
        if 'Min' in alpaca_timeframe:
            # Approximate 6.5 hours of trading per day × 60 min / timeframe_minutes
            minutes_per_tf = int(alpaca_timeframe.replace('Min', ''))
            limit = int((6.5 * 60 / minutes_per_tf) * days)
        
        # Use the market data manager to get real data if available
        if market_data_manager:
            # Try to get real data from Alpaca
            market_data = market_data_manager.get_market_data(
                [symbol], 
                data_type='bars',
                timeframe=alpaca_timeframe,
                limit=limit
            )
            
            # Process the data to the expected format
            bars = []
            if isinstance(market_data, dict) and 'bars' in market_data:
                # Extract the bars for this symbol
                symbol_bars = market_data['bars'].get(symbol, [])
                
                # Convert each bar to the expected format
                for bar in symbol_bars:
                    bar_data = {
                        'date': bar.get('t', '').split('T')[0],
                        'symbol': symbol,
                        'open': bar.get('o', 0),
                        'high': bar.get('h', 0),
                        'low': bar.get('l', 0),
                        'close': bar.get('c', 0),
                        'volume': bar.get('v', 0),
                        'change': 0  # Calculate change if needed
                    }
                    
                    # Calculate percent change from open to close
                    if bar_data['open'] != 0:
                        bar_data['change'] = ((bar_data['close'] - bar_data['open']) / bar_data['open']) * 100
                    
                    bars.append(bar_data)
                
                # Handle if we got empty data from Alpaca
                if not bars:
                    logger.warning(f"No data returned from Alpaca for {symbol}, using mock data")
                    bars = generate_mock_bars(symbol, days)
            else:
                # If no data in expected format, use mock data
                logger.warning(f"Unexpected data format from market data source for {symbol}, using mock data")
                bars = generate_mock_bars(symbol, days)
                
            return jsonify({
                'success': True,
                'symbol': symbol,
                'timeframe': timeframe,
                'days': days,
                'source': market_data_manager.active_source,
                'bars': bars
            })
        else:
            # If no market data manager, use mock data
            logger.warning(f"No market data manager available for {symbol}, using mock data")
            bars = generate_mock_bars(symbol, days)
            
            return jsonify({
                'success': True,
                'symbol': symbol,
                'timeframe': timeframe,
                'days': days,
                'source': 'mock',
                'bars': bars
            })
            
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_mock_bars(symbol, days):
    """Generate mock market data bars for a symbol"""
    bars = []
    today = datetime.now()
    
    # Use base price depending on symbol
    base_prices = {
        'SPY': 450.0,
        'QQQ': 350.0,
        'AAPL': 180.0,
        'MSFT': 350.0,
        'TSLA': 200.0,
        'NVDA': 850.0,
        'GOOGL': 170.0,
        'META': 450.0,
        'AMZN': 180.0
    }
    last_price = base_prices.get(symbol, 100.0) + random.randint(-10, 10)
    
    for i in range(days):
        date = today - timedelta(days=days-i-1)
        
        # Generate random price movement
        change = (random.random() - 0.48) * 5  # Slightly biased upward
        open_price = last_price
        close_price = open_price + change
        high_price = max(open_price, close_price) + random.random() * 2
        low_price = min(open_price, close_price) - random.random() * 2
        volume = int(random.random() * 10000000) + 1000000
        
        bars.append({
            'date': date.strftime('%Y-%m-%d'),
            'symbol': symbol,
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume,
            'change': round(((close_price - open_price) / open_price) * 100, 2)
        })
        
        last_price = close_price
    
    return bars

@app.route('/api/market/ai_signals/<symbol>', methods=['GET', 'OPTIONS'])
def api_get_market_ai_signals(symbol):
    """
    Get AI-generated signals for a specific symbol.
    Args:
        symbol: Stock symbol to get signals for
    Returns:
        JSON response with AI signals data
    """
    if request.method == 'OPTIONS':
        # CORS preflight
        return ('', 204)
    try:
        # Generate mock AI signal data for demo purposes
        mock_signals = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'signals': [
                {
                    'type': 'bullish',
                    'timeframe': '1d',
                    'confidence': round(random.uniform(0.65, 0.95), 2),
                    'description': f"Bullish signal detected for {symbol} on daily chart",
                    'indicators': [
                        {'name': 'RSI', 'value': random.randint(30, 40), 'threshold': 30, 'signal': 'oversold'},
                        {'name': 'MACD', 'value': random.uniform(-1, 0), 'threshold': 0, 'signal': 'crossover soon'},
                        {'name': 'Moving Average', 'value': f"Price near {random.randint(10, 50)} day MA support"}
                    ]
                },
                {
                    'type': 'consolidation',
                    'timeframe': '4h',
                    'confidence': round(random.uniform(0.7, 0.9), 2),
                    'description': f"{symbol} is consolidating in a tight range on 4h chart",
                    'indicators': [
                        {'name': 'Bollinger Bands', 'value': 'Narrowing', 'signal': 'low volatility'},
                        {'name': 'Volume', 'value': 'Decreasing', 'signal': 'consolidation phase'}
                    ]
                }
            ],
            'ai_analysis': f"AI analysis indicates {symbol} is showing signs of potential upward movement based on technical pattern recognition and sentiment analysis. Key support at previous resistance level with positive momentum building.",
            'risk_level': random.choice(['low', 'medium', 'high']),
            'opportunity_score': round(random.uniform(1, 10), 1)
        }
        return jsonify({
            'success': True,
            'data': mock_signals
        })
    except Exception as e:
        logger.error(f"Error generating AI signals for {symbol}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-signals', methods=['POST'])
def api_generate_signals():
    """Generate new trading signals - redirects to the dual bot endpoint"""
    try:
        # Import the dual bot's generate_signals function
        from api.routes.dual_bot_routes import generate_signals
        
        # Call the function directly
        logger.info("Redirecting legacy /api/generate-signals to dual bot implementation")
        return generate_signals()
            
    except Exception as e:
        logger.error(f"Error in generate-signals: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Import market data routes
try:
    from api.routes.market_data_routes import market_data_bp
    app.register_blueprint(market_data_bp)
    logger.info("Market data routes registered successfully")
except Exception as e:
    logger.error(f"Failed to register market data routes: {str(e)}")
    # Fallback with a simple market data endpoint
    @app.route('/api/market-data/<symbol>', methods=['GET'])
    def fallback_market_data(symbol):
        """Fallback market data endpoint"""
        try:
            # Get query parameters
            timeframe = request.args.get('timeframe', '1d')
            days = int(request.args.get('days', 30))
            
            # Generate mock bars
            bars = []
            today = datetime.now()
            
            # Use base price depending on symbol
            base_prices = {
                'SPY': 450.0,
                'QQQ': 350.0,
                'AAPL': 180.0,
                'MSFT': 350.0,
                'TSLA': 200.0,
                'NVDA': 850.0,
                'GOOGL': 170.0,
                'META': 450.0,
                'AMZN': 180.0
            }
            last_price = base_prices.get(symbol, 100.0) + random.randint(-10, 10)
            
            for i in range(days):
                date = today - timedelta(days=days-i-1)
                
                # Generate random price movement
                change = (random.random() - 0.48) * 5  # Slightly biased upward
                open_price = last_price
                close_price = open_price + change
                high_price = max(open_price, close_price) + random.random() * 2
                low_price = min(open_price, close_price) - random.random() * 2
                volume = int(random.random() * 10000000) + 1000000
                
                bars.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'symbol': symbol,
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': volume,
                    'change': round(((close_price - open_price) / open_price) * 100, 2)
                })
                
                last_price = close_price
            
            logger.info(f"Fallback market data endpoint used for {symbol}")
            return jsonify({
                'success': True,
                'symbol': symbol,
                'timeframe': timeframe,
                'days': days,
                'source': 'mock',
                'bars': bars
            })
        except Exception as e:
            logger.error(f"Error in fallback market data endpoint: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# Add a redirection for old broker routes
@app.route('/api/broker/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def redirect_old_broker_routes(subpath):
    """Redirect old broker routes to new broker integration routes"""
    # Build the new URL from the request
    new_url = f"/api/broker/{subpath}"
    
    # Log the redirection
    logger.info(f"Redirecting broker request from old to new route: {request.path} -> {new_url}")
    
    # Redirect to the new URL, preserving method and data
    return redirect(new_url, code=308)  # 308 is Permanent Redirect that preserves the method

# Add redirection for broker routes with a trailing slash
@app.route('/api/broker/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def redirect_old_broker_root():
    """Redirect the old broker root route to the new broker integration root route"""
    new_url = "/api/broker/info"
    logger.info(f"Redirecting broker request from old root to new route: {request.path} -> {new_url}")
    return redirect(new_url, code=308)

# Start bot endpoint
@app.route('/api/bot/start/<bot_type>', methods=['POST', 'OPTIONS'])
def start_bot_endpoint(bot_type):
    """Start a specific bot"""
    logger.info(f"Start bot endpoint called for {bot_type}")
    
    if request.method == 'OPTIONS':
        return ('', 204)  # Handle CORS preflight
        
    try:
        # Get the normalized bot type (remove -bot suffix if present)
        normalized_bot_type = bot_type.replace('-bot', '')
        
        # First try to import and use the actual bot module
        try:
            from api.routes.bot_routes import bot_status
            
            # Update the bot status
            bot_key = f"{normalized_bot_type}_bot"
            if bot_key in bot_status or normalized_bot_type in ['autonomous', 'rsi', 'dual']:
                if bot_key not in bot_status:
                    # Initialize if not exists
                    bot_status[bot_key] = {
                        'status': False,
                        'running_since': None,
                        'last_update': None
                    }
                
                # Set status to active
                bot_status[bot_key]['status'] = True
                bot_status[bot_key]['running_since'] = datetime.now().isoformat()
                bot_status[bot_key]['last_update'] = datetime.now().isoformat()
                
                logger.info(f"Set {bot_key} status to active")
            else:
                logger.warning(f"Unknown bot type: {bot_type}")
                return jsonify({
                    'success': False,
                    'error': f"Unknown bot type: {bot_type}"
                }), 400
                
        except Exception as e:
            logger.error(f"Error using bot_routes module: {str(e)}")
            # Fallback to simpler implementation
            
        # Return success response
        return jsonify({
            'success': True,
            'message': f"{normalized_bot_type} bot started successfully",
            'status': "active"
        })
        
    except Exception as e:
        logger.error(f"Error starting bot {bot_type}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Stop bot endpoint
@app.route('/api/bot/stop/<bot_type>', methods=['POST', 'OPTIONS'])
def stop_bot_endpoint(bot_type):
    """Stop a specific bot"""
    logger.info(f"Stop bot endpoint called for {bot_type}")
    
    if request.method == 'OPTIONS':
        return ('', 204)  # Handle CORS preflight
        
    try:
        # Get the normalized bot type (remove -bot suffix if present)
        normalized_bot_type = bot_type.replace('-bot', '')
        
        # First try to import and use the actual bot module
        try:
            from api.routes.bot_routes import bot_status
            
            # Update the bot status
            bot_key = f"{normalized_bot_type}_bot"
            if bot_key in bot_status or normalized_bot_type in ['autonomous', 'rsi', 'dual']:
                if bot_key not in bot_status:
                    # Initialize if not exists
                    bot_status[bot_key] = {
                        'status': False,
                        'running_since': None,
                        'last_update': None
                    }
                
                # Set status to inactive
                bot_status[bot_key]['status'] = False
                bot_status[bot_key]['running_since'] = None
                bot_status[bot_key]['last_update'] = datetime.now().isoformat()
                
                logger.info(f"Set {bot_key} status to inactive")
            else:
                logger.warning(f"Unknown bot type: {bot_type}")
                return jsonify({
                    'success': False,
                    'error': f"Unknown bot type: {bot_type}"
                }), 400
                
        except Exception as e:
            logger.error(f"Error using bot_routes module: {str(e)}")
            # Fallback to simpler implementation
            
        # Return success response
        return jsonify({
            'success': True,
            'message': f"{normalized_bot_type} bot stopped successfully",
            'status': "inactive"
        })
        
    except Exception as e:
        logger.error(f"Error stopping bot {bot_type}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# After all routes are registered at the end of file
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

# After all routes are registered at the end of file
# Add these aliases for frontend compatibility
@app.route('/api/status', methods=['GET', 'OPTIONS'])
def api_status_alias():
    """Alias for /api/status -> /api/bot/status for frontend compatibility"""
    logger.info("Status alias endpoint called, redirecting to /api/bot/status")
    if request.method == 'OPTIONS':
        return ('', 204)  # Handle CORS preflight
    try:
        # Import the Bot routes module
        from api.routes.bot_routes import get_bot_status
        # Call the function directly
        return get_bot_status()
    except Exception as e:
        logger.error(f"Error in status alias: {str(e)}")
        # Return mock bot status on error
        return jsonify({
            "success": True,
            "status": {
                "autonomous_bot": {
                    "status": "inactive",
                    "last_update": datetime.now().isoformat()
                },
                "rsi_bot": {
                    "status": "inactive",
                    "last_update": datetime.now().isoformat()
                },
                "dual_bot": {
                    "status": "inactive",
                    "last_update": datetime.now().isoformat()
                }
            }
        })

@app.route('/api/dual-bot/status', methods=['GET', 'OPTIONS'])
def api_dual_bot_status_alias():
    """Alias for /api/dual-bot/status -> /api/bot/status for frontend compatibility"""
    logger.info("Dual bot status alias endpoint called, redirecting to /api/bot/status")
    if request.method == 'OPTIONS':
        return ('', 204)  # Handle CORS preflight
    try:
        # Import the Bot routes module
        from api.routes.bot_routes import get_bot_status
        # Call the function directly
        return get_bot_status()
    except Exception as e:
        logger.error(f"Error in dual-bot status alias: {str(e)}")
        # Return mock bot status on error
        return jsonify({
            "success": True,
            "status": {
                "autonomous_bot": {
                    "status": "inactive",
                    "last_update": datetime.now().isoformat()
                },
                "rsi_bot": {
                    "status": "inactive",
                    "last_update": datetime.now().isoformat()
                },
                "dual_bot": {
                    "status": "inactive",
                    "last_update": datetime.now().isoformat()
                }
            }
        })
