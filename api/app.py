from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import pandas as pd
import sys
import os
import random
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app first
app = Flask(__name__)
CORS(app)

# Add market data integration
from lib.market_data import MarketDataSourceManager
from lib.market_data_config import load_market_data_config, save_market_data_config

# Import execution model routes
from execution_model_routes import register_routes as register_execution_model_routes

# Import broker integration routes
from broker_integration.broker_routes import register_routes as register_broker_routes

# Import auto trader routes
from broker_integration.auto_trade_routes import register_routes as register_auto_trade_routes

# Import notification routes
from notification_routes import register_routes as register_notification_routes

# Import risk management routes
from risk_management_routes import register_routes as register_risk_management_routes

# Import market analysis routes
from market_analysis_routes import register_routes as register_market_analysis_routes

# Import autonomous bot routes
from api.autonomous_bot_routes import register_routes as register_autonomous_bot_routes

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
                'message': 'AI Signal Ranking module is being initialized'
            })
        
        @ai_bp.route('/market-insights', methods=['POST'])
        def get_market_insights():
            return jsonify({
                'success': True,
                'insights': {
                    'market_summary': 'AI market analysis is being prepared',
                    'key_insights': []
                },
                'message': 'GPT insights module is being initialized'
            })
        
        app.register_blueprint(ai_bp)
        logger.info("Successfully registered fallback AI signal ranking routes")
    except Exception as fallback_error:
        logger.error(f"Error registering fallback AI signal ranking routes: {fallback_error}")
        logger.error("AI signal ranking features will be disabled")

# Test route to verify server is running
@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint to verify the Flask server is running"""
    app_env = os.environ.get('APP_ENV', 'development')
    return jsonify({
        'success': True,
        'message': 'Flask API server is running correctly',
        'timestamp': datetime.now().isoformat(),
        'environment': app_env
    })

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

# Register execution model routes
try:
    register_execution_model_routes(app)
    logger.info("Successfully registered execution model routes")
except Exception as e:
    logger.error(f"Error registering execution model routes: {e}")

# Register broker integration routes
try:
    register_broker_routes(app)
    logger.info("Successfully registered broker integration routes")
except Exception as e:
    logger.error(f"Error registering broker integration routes: {e}")

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

# Register autonomous bot routes
try:
    register_autonomous_bot_routes(app)
    logger.info("Successfully registered autonomous bot routes")
except Exception as e:
    logger.error(f"Error registering autonomous bot routes: {e}")

# Register AI activity log routes
try:
    from api.ai_activity_log_routes import register_routes as register_ai_activity_log_routes
    register_ai_activity_log_routes(app)
    logger.info("Successfully registered AI activity log routes")
except Exception as e:
    logger.error(f"Error registering AI activity log routes: {e}")
    logger.error("AI activity logging features will be disabled")

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
        # Try multiple possible locations for the CSV files
        possible_paths = [
            # Current directory
            ("buy_signals.csv", "short_signals.csv"),
            # Root project directory
            (os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "buy_signals.csv"),
             os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "short_signals.csv")),
            # Data directory
            (os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "buy_signals.csv"),
             os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "short_signals.csv"))
        ]
        
        buy_signals = None
        short_signals = None
        
        # Try each possible path
        for buy_path, short_path in possible_paths:
            logger.info(f"Trying to load signals from: {buy_path} and {short_path}")
            
            if os.path.exists(buy_path) and os.path.exists(short_path):
                logger.info(f"Found signal files at: {buy_path} and {short_path}")
                try:
                    buy_signals = pd.read_csv(buy_path)
                    short_signals = pd.read_csv(short_path)
                    logger.info(f"Successfully loaded {len(buy_signals)} buy signals and {len(short_signals)} short signals")
                    break
                except Exception as e:
                    logger.error(f"Error reading CSV files at {buy_path} and {short_path}: {str(e)}")
                    continue
        
        # If all paths failed, use mock data
        if buy_signals is None or short_signals is None:
            logger.warning("Could not load signals from any location, using mock data")
            # Return mock data as fallback
            buy_signals = pd.DataFrame({
                'date': [datetime.now().strftime('%Y-%m-%d')],
                'symbol': ['AAPL'],
                'price': [180.0],
                'signal_type': ['buy'],
                'confidence': [0.85]
            })
            short_signals = pd.DataFrame({
                'date': [datetime.now().strftime('%Y-%m-%d')],
                'symbol': ['TSLA'],
                'price': [220.0],
                'signal_type': ['short'],
                'confidence': [0.78]
            })
        
        return jsonify({
            'success': True,
            'buy_signals': buy_signals.to_dict('records'),
            'short_signals': short_signals.to_dict('records')
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
            # Root project directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backtest_results.csv"),
            # Data directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "backtest_results.csv")
        ]
        
        backtest_results = None
        
        # Try each possible path
        for path in possible_paths:
            logger.info(f"Trying to load backtest results from: {path}")
            
            if os.path.exists(path):
                logger.info(f"Found backtest results file at: {path}")
                try:
                    backtest_results = pd.read_csv(path)
                    logger.info(f"Successfully loaded {len(backtest_results)} backtest results")
                    break
                except Exception as e:
                    logger.error(f"Error reading CSV file at {path}: {str(e)}")
                    continue
        
        # If all paths failed, use mock data
        if backtest_results is None:
            logger.warning("Could not load backtest results from any location, using mock data")
            # Return mock data as fallback
            backtest_results = pd.DataFrame({
                'date': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)],
                'symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
                'entry_price': [180.0, 310.0, 140.0, 130.0, 220.0],
                'exit_price': [185.0, 315.0, 145.0, 128.0, 225.0],
                'profit': [5.0, 5.0, 5.0, -2.0, 5.0],
                'profit_percent': [2.8, 1.6, 3.6, -1.5, 2.3],
                'trade_outcome': ['win', 'win', 'win', 'loss', 'win']
            })
        
        return jsonify({
            'success': True,
            'backtest_results': backtest_results.to_dict('records')
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
                        'symbol': symbol,
                        'timestamp': time.isoformat(),
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

# Main entry point
if __name__ == '__main__':
    print("Starting Flask API server...")
    print(f"API endpoints available at http://localhost:5000")
    print("Press Ctrl+C to shut down the server")
    print("Available test endpoint: http://localhost:5000/api/test")
    
    # Run the Flask application with debug mode
    app.run(host='0.0.0.0', port=5000, debug=True) 