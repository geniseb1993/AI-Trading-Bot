"""
Standalone TradingView mock API server
"""
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
import random
import json
import logging
from datetime import datetime, timedelta
import os
import sys

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a Flask app
app = Flask(__name__)

# Configure CORS to allow all origins
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": "*"}})

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Store received webhook alerts
webhook_alerts = []
MAX_ALERTS = 100

# Get port from environment variable or command line argument, default to 5003
def get_port():
    # First check environment variable
    port = os.environ.get('TRADINGVIEW_PORT')
    if port:
        try:
            return int(port)
        except ValueError:
            logger.warning(f"Invalid TRADINGVIEW_PORT value: {port}, using default 5003")
    
    # Then check command line arguments
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except ValueError:
            logger.warning(f"Invalid port argument: {sys.argv[1]}, using default 5003")
    
    # Default port
    return 5003

@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint to verify the server is running"""
    return jsonify({
        'success': True,
        'message': 'TradingView integration server is running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    })

@app.route('/api/tradingview/test', methods=['GET'])
def test_tradingview_route():
    """
    Simple test endpoint to verify the TradingView routes are registered
    """
    return jsonify({
        'success': True,
        'message': 'TradingView integration routes are working',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/tradingview/webhook', methods=['POST'])
def receive_tradingview_webhook():
    """
    Receive webhook alerts from TradingView
    """
    try:
        # Get the alert data from request
        alert_data = request.json
        
        if not alert_data:
            logger.warning("Received empty webhook data")
            return jsonify({
                'success': False,
                'message': 'No data received'
            }), 400
        
        # Add timestamp if not provided
        if 'timestamp' not in alert_data:
            alert_data['timestamp'] = datetime.now().isoformat()
        
        # Store the alert (limit to MAX_ALERTS)
        webhook_alerts.append(alert_data)
        if len(webhook_alerts) > MAX_ALERTS:
            webhook_alerts.pop(0)  # Remove oldest alert
        
        logger.info(f"Received TradingView alert: {alert_data.get('symbol', 'Unknown Symbol')}")
        
        return jsonify({
            'success': True,
            'message': 'Alert received successfully'
        })
    except Exception as e:
        logger.error(f"Error processing TradingView webhook: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tradingview/alerts', methods=['GET'])
def get_tradingview_alerts():
    """
    Get all received TradingView webhook alerts
    """
    try:
        # Get query parameters
        symbol = request.args.get('symbol')
        limit = request.args.get('limit', default=50, type=int)
        
        # Filter alerts by symbol if provided
        filtered_alerts = webhook_alerts
        if symbol:
            filtered_alerts = [alert for alert in webhook_alerts if alert.get('symbol') == symbol]
        
        # Limit the number of alerts returned
        limited_alerts = filtered_alerts[-limit:] if limit > 0 else filtered_alerts
        
        return jsonify({
            'success': True,
            'alerts': limited_alerts,
            'count': len(limited_alerts)
        })
    except Exception as e:
        logger.error(f"Error getting TradingView alerts: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tradingview/symbols/technical-data', methods=['GET'])
def get_technical_indicators():
    """
    Get technical indicators for a specific stock symbol and interval
    Simulates fetching technical indicator data from TradingView
    """
    try:
        # Get query parameters
        symbol = request.args.get('symbol', 'SPY')
        interval = request.args.get('interval', '1d')
        
        # Generate simulated technical indicators
        base_price = 100 + random.random() * 400
        
        # Create simulated data
        data = {
            'symbol': symbol,
            'interval': interval,
            'timestamp': datetime.now().isoformat(),
            'price': round(base_price, 2),
            'technical_indicators': {
                'rsi': round(30 + random.random() * 40, 2),  # RSI between 30-70
                'macd': {
                    'macd_line': round(random.random() * 4 - 2, 2),  # MACD line between -2 and 2
                    'signal_line': round(random.random() * 4 - 2, 2),  # Signal line between -2 and 2
                    'histogram': round(random.random() * 2 - 1, 2),  # Histogram between -1 and 1
                },
                'moving_averages': {
                    'sma_20': round(base_price * (1 + (random.random() - 0.5) * 0.1), 2),
                    'sma_50': round(base_price * (1 + (random.random() - 0.5) * 0.15), 2),
                    'sma_200': round(base_price * (1 + (random.random() - 0.5) * 0.2), 2),
                    'ema_9': round(base_price * (1 + (random.random() - 0.5) * 0.05), 2),
                    'ema_21': round(base_price * (1 + (random.random() - 0.5) * 0.08), 2),
                },
                'bollinger_bands': {
                    'upper': round(base_price * 1.05, 2),
                    'middle': round(base_price, 2),
                    'lower': round(base_price * 0.95, 2),
                    'width': round(0.05 + random.random() * 0.05, 2),
                },
                'fibonacci_levels': {
                    '0.0': round(base_price * 0.9, 2),
                    '0.236': round(base_price * 0.95, 2),
                    '0.382': round(base_price * 0.97, 2),
                    '0.5': round(base_price, 2),
                    '0.618': round(base_price * 1.03, 2),
                    '0.786': round(base_price * 1.05, 2),
                    '1.0': round(base_price * 1.1, 2),
                }
            }
        }
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        logger.error(f"Error getting technical indicators: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tradingview/market/analysis', methods=['GET'])
def get_market_analysis():
    """
    Get comprehensive market analysis
    Simulates fetching market analysis data from TradingView
    """
    try:
        # Generate simulated market analysis data
        current_date = datetime.now()
        
        # Major indices
        indices = [
            {'symbol': 'SPY', 'name': 'S&P 500 ETF', 'price': round(420 + random.random() * 30, 2), 'change': round(random.random() * 2 - 0.5, 2)},
            {'symbol': 'QQQ', 'name': 'Nasdaq 100 ETF', 'price': round(350 + random.random() * 40, 2), 'change': round(random.random() * 2.5 - 0.8, 2)},
            {'symbol': 'DIA', 'name': 'Dow Jones Industrial ETF', 'price': round(330 + random.random() * 20, 2), 'change': round(random.random() * 1.8 - 0.5, 2)},
            {'symbol': 'IWM', 'name': 'Russell 2000 ETF', 'price': round(180 + random.random() * 20, 2), 'change': round(random.random() * 2.2 - 0.7, 2)},
        ]
        
        # Sector performance
        sectors = [
            {'symbol': 'XLK', 'name': 'Technology', 'price': round(140 + random.random() * 20, 2), 'change': round(random.random() * 2.2 - 0.6, 2)},
            {'symbol': 'XLF', 'name': 'Financial', 'price': round(35 + random.random() * 5, 2), 'change': round(random.random() * 1.8 - 0.5, 2)},
            {'symbol': 'XLE', 'name': 'Energy', 'price': round(70 + random.random() * 10, 2), 'change': round(random.random() * 2.5 - 1, 2)},
            {'symbol': 'XLV', 'name': 'Healthcare', 'price': round(120 + random.random() * 15, 2), 'change': round(random.random() * 1.5 - 0.4, 2)},
            {'symbol': 'XLP', 'name': 'Consumer Staples', 'price': round(65 + random.random() * 8, 2), 'change': round(random.random() * 1.2 - 0.3, 2)},
            {'symbol': 'XLY', 'name': 'Consumer Discretionary', 'price': round(150 + random.random() * 20, 2), 'change': round(random.random() * 2 - 0.6, 2)},
        ]
        
        # Market breadth indicators
        breadth = {
            'advance_decline_ratio': round(random.random() * 3 + 0.5, 2),
            'percent_above_sma_200': round(random.random() * 50 + 30, 1),
            'percent_above_sma_50': round(random.random() * 40 + 40, 1),
            'new_highs': int(random.random() * 100),
            'new_lows': int(random.random() * 50),
        }
        
        # Economic indicators
        vix = round(15 + random.random() * 15, 2)  # VIX between 15-30
        
        # Calculate market sentiment
        avg_index_change = sum(idx['change'] for idx in indices) / len(indices)
        avg_sector_change = sum(sec['change'] for sec in sectors) / len(sectors)
        fear_greed = 50  # Neutral default
        
        if vix > 25:
            fear_greed -= 15  # Higher VIX means more fear
        elif vix < 20:
            fear_greed += 10  # Lower VIX means less fear
            
        if avg_index_change > 0.5:
            fear_greed += 15  # Strong index performance means more greed
        elif avg_index_change < -0.5:
            fear_greed -= 20  # Weak index performance means more fear
            
        if breadth['advance_decline_ratio'] > 2:
            fear_greed += 10  # Strong breadth means more greed
        elif breadth['advance_decline_ratio'] < 1:
            fear_greed -= 10  # Weak breadth means more fear
            
        # Ensure fear/greed is within 0-100 range
        fear_greed = max(0, min(100, fear_greed))
        
        # Sentiment category based on fear/greed value
        sentiment = 'Neutral'
        if fear_greed >= 75:
            sentiment = 'Extreme Greed'
        elif fear_greed >= 60:
            sentiment = 'Greed'
        elif fear_greed <= 25:
            sentiment = 'Extreme Fear'
        elif fear_greed <= 40:
            sentiment = 'Fear'
            
        # Compile the analysis
        analysis = {
            'timestamp': current_date.isoformat(),
            'major_indices': indices,
            'sector_performance': sectors,
            'market_breadth': breadth,
            'economic_indicators': {
                'vix': vix,
                'treasury_10y': round(3 + random.random() * 2, 3),
                'treasury_2y': round(4 + random.random() * 1, 3),
            },
            'market_sentiment': {
                'fear_greed_index': round(fear_greed, 1),
                'sentiment': sentiment,
                'overall_market_trend': 'Bullish' if avg_index_change > 0 else 'Bearish',
                'strongest_sector': max(sectors, key=lambda x: x['change'])['name'],
                'weakest_sector': min(sectors, key=lambda x: x['change'])['name'],
            }
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        logger.error(f"Error generating market analysis: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Print all available routes
print("\nAvailable routes:")
for rule in app.url_map.iter_rules():
    print(f"Route: {rule.endpoint} -> {rule.rule}")

# Run the server
if __name__ == '__main__':
    try:
        port = get_port()
        print(f"\nStarting TradingView mock API server on port {port}...")
        print(f"Test route: http://localhost:{port}/api/test")
        print(f"TradingView routes available at: http://localhost:{port}/api/tradingview/")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc() 