#!/usr/bin/env python
"""
TradingView Integration Module for AI Trading Bot V2.0
This module provides Flask endpoints for TradingView integration
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
import random
import json
import os
from datetime import datetime, timedelta
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a Flask app
app = Flask(__name__)
CORS(app)

# Store received webhook alerts
webhook_alerts = []
MAX_ALERTS = 100

# Bot management server URL
BOT_MANAGEMENT_URL = "http://localhost:5002"

# Helper functions for TradingView integration
def get_index_name(symbol):
    """Get index name from symbol"""
    index_names = {
        'SPY': 'S&P 500 ETF',
        'QQQ': 'Nasdaq 100 ETF',
        'DIA': 'Dow Jones Industrial ETF',
        'IWM': 'Russell 2000 ETF'
    }
    return index_names.get(symbol, symbol)

def get_sector_name(symbol):
    """Get sector name from symbol"""
    sector_names = {
        'XLK': 'Technology',
        'XLF': 'Financial',
        'XLE': 'Energy',
        'XLV': 'Healthcare',
        'XLP': 'Consumer Staples',
        'XLY': 'Consumer Discretionary'
    }
    return sector_names.get(symbol, symbol)

def trigger_bot_action(bot_id, action, signal_data=None):
    """Trigger a bot action via the bot management server"""
    try:
        if action == "start":
            url = f"{BOT_MANAGEMENT_URL}/api/bot/{bot_id}/start"
        elif action == "stop":
            url = f"{BOT_MANAGEMENT_URL}/api/bot/{bot_id}/stop"
        else:
            logger.error(f"Unknown bot action: {action}")
            return False, f"Unknown bot action: {action}"

        logger.info(f"Triggering {action} action for bot {bot_id}")
        
        payload = {}
        if signal_data:
            payload["signal_data"] = signal_data
            
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            logger.info(f"Successfully triggered {action} for {bot_id}")
            return True, response.json()
        else:
            logger.error(f"Failed to trigger {action} for {bot_id}: {response.text}")
            return False, response.text
    except Exception as e:
        logger.error(f"Error triggering bot action: {str(e)}")
        return False, str(e)

def _build_cors_preflight_response():
    """Build a CORS preflight response"""
    response = jsonify({})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,Accept,X-Requested-With,X-API-Key")
    response.headers.add('Access-Control-Allow-Methods', "GET,POST,OPTIONS,PUT,DELETE")
    response.headers.add('Access-Control-Max-Age', "3600")  # Cache preflight response for 1 hour
    return response

# API Routes
@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint to verify the server is running"""
    return jsonify({
        'success': True,
        'message': 'TradingView integration server is running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    })

@app.route('/api/tradingview/webhook', methods=['POST', 'OPTIONS'])
def receive_tradingview_webhook():
    """
    Receive webhook alerts from TradingView
    """
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
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
        
        # Handle bot actions based on signal
        if 'signal' in alert_data and 'strategy' in alert_data:
            bot_id = 'dual_bot'  # Default to dual_bot
            
            # Map strategy to specific bot if needed
            if alert_data['strategy'].lower() == 'rsi strategy':
                bot_id = 'rsi_bot'
            elif alert_data['strategy'].lower() == 'autonomous strategy':
                bot_id = 'autonomous_bot'
                
            # Start or stop bot based on signal
            if alert_data['signal'] == 'BUY':
                success, result = trigger_bot_action(bot_id, "start", alert_data)
                if success:
                    alert_data['bot_action_result'] = result
            elif alert_data['signal'] == 'SELL':
                success, result = trigger_bot_action(bot_id, "stop", alert_data)
                if success:
                    alert_data['bot_action_result'] = result
                    
        return jsonify({
            'success': True,
            'message': 'Alert received successfully',
            'alert_id': len(webhook_alerts)
        })
    except Exception as e:
        logger.error(f"Error processing TradingView webhook: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tradingview/alerts', methods=['GET', 'OPTIONS'])
def get_tradingview_alerts():
    """
    Get all received TradingView webhook alerts
    """
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
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

@app.route('/api/tradingview/bot/control', methods=['POST', 'OPTIONS'])
def control_bot():
    """
    Endpoint to control bots based on TradingView signals
    """
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
            
        bot_id = data.get('bot_id', 'dual_bot')
        action = data.get('action')
        
        if not action:
            return jsonify({
                'success': False,
                'message': 'No action specified'
            }), 400
            
        success, result = trigger_bot_action(bot_id, action, data.get('signal_data'))
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Bot {bot_id} {action} action triggered successfully',
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to trigger {action} for bot {bot_id}',
                'error': result
            }), 500
            
    except Exception as e:
        logger.error(f"Error controlling bot: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tradingview/bots/status', methods=['GET', 'OPTIONS'])
def get_bots_status():
    """
    Get status of all bots from the bot management server
    """
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        # Get bot status from the bot management server
        response = requests.get(f"{BOT_MANAGEMENT_URL}/api/bot/status")
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'status': response.json()
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to get bot status: {response.text}'
            }), response.status_code
            
    except Exception as e:
        logger.error(f"Error getting bot status: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tradingview/symbols/technical-data', methods=['GET', 'OPTIONS'])
def get_technical_indicators():
    """
    Get technical indicators for a specific stock symbol and interval
    Uses real market data when available
    """
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        # Get query parameters
        symbol = request.args.get('symbol', 'SPY')
        interval = request.args.get('interval', '1d')
        
        # Try to get real market data
        try:
            # Convert interval to timeframe and days for our API
            timeframe = '1d'
            days = 30
            
            if interval == '1m':
                timeframe = '1Min'
                days = 1
            elif interval == '5m':
                timeframe = '5Min'
                days = 1
            elif interval == '15m':
                timeframe = '15Min'
                days = 3
            elif interval == '1h':
                timeframe = '1H'
                days = 7
            elif interval == '4h':
                timeframe = '4H'
                days = 14
            elif interval == '1d':
                timeframe = '1D'
                days = 60
            
            # Get market data from our API
            response = requests.get(f"http://localhost:5000/api/market-data/{symbol}?timeframe={timeframe}&days={days}")
            if response.status_code == 200:
                market_data = response.json()
                
                if market_data and 'bars' in market_data and len(market_data['bars']) > 0:
                    # Get the latest bar
                    latest_bar = market_data['bars'][-1]
                    
                    # Calculate some basic technical indicators
                    bars = market_data['bars']
                    
                    # Simple moving averages
                    sma_20 = sum([bar['close'] for bar in bars[-20:]]) / min(20, len(bars)) if len(bars) >= 5 else latest_bar['close']
                    sma_50 = sum([bar['close'] for bar in bars[-50:]]) / min(50, len(bars)) if len(bars) >= 10 else latest_bar['close']
                    sma_200 = sum([bar['close'] for bar in bars[-200:]]) / min(200, len(bars)) if len(bars) >= 20 else latest_bar['close']
                    
                    # EMA calculations (simplified)
                    ema_9 = latest_bar['close']
                    ema_21 = latest_bar['close']
                    
                    if len(bars) >= 9:
                        # Simple EMA calculation
                        multiplier_9 = 2 / (9 + 1)
                        ema_9 = bars[-9]['close']
                        for i in range(-8, 0):
                            ema_9 = (bars[i]['close'] - ema_9) * multiplier_9 + ema_9
                    
                    if len(bars) >= 21:
                        # Simple EMA calculation
                        multiplier_21 = 2 / (21 + 1)
                        ema_21 = bars[-21]['close']
                        for i in range(-20, 0):
                            ema_21 = (bars[i]['close'] - ema_21) * multiplier_21 + ema_21
                    
                    # Bollinger Bands (20-period SMA with 2 standard deviations)
                    std_dev = 0
                    if len(bars) >= 20:
                        prices = [bar['close'] for bar in bars[-20:]]
                        std_dev = (sum([(price - sma_20) ** 2 for price in prices]) / len(prices)) ** 0.5
                    
                    # RSI (simplified)
                    rsi = 50  # Default neutral
                    if len(bars) >= 14:
                        changes = [bars[i]['close'] - bars[i-1]['close'] for i in range(-14, 0)]
                        gains = sum([change for change in changes if change > 0]) / 14
                        losses = sum([abs(change) for change in changes if change < 0]) / 14
                        
                        if losses > 0:
                            rs = gains / losses
                            rsi = 100 - (100 / (1 + rs))
                        elif gains > 0:
                            rsi = 100
                    
                    # Create data structure
                    data = {
                        'symbol': symbol,
                        'interval': interval,
                        'timestamp': latest_bar['timestamp'],
                        'price': latest_bar['close'],
                        'technical_indicators': {
                            'rsi': round(rsi, 2),
                            'macd': {
                                'macd_line': round(ema_9 - ema_21, 2),
                                'signal_line': round((ema_9 - ema_21) * 0.9, 2),  # Simplified
                                'histogram': round((ema_9 - ema_21) * 0.1, 2),  # Simplified
                            },
                            'moving_averages': {
                                'sma_20': round(sma_20, 2),
                                'sma_50': round(sma_50, 2),
                                'sma_200': round(sma_200, 2),
                                'ema_9': round(ema_9, 2),
                                'ema_21': round(ema_21, 2),
                            },
                            'bollinger_bands': {
                                'upper': round(sma_20 + 2 * std_dev, 2),
                                'middle': round(sma_20, 2),
                                'lower': round(sma_20 - 2 * std_dev, 2),
                                'width': round(4 * std_dev / sma_20 if sma_20 > 0 else 0, 2),
                            },
                            'fibonacci_levels': {
                                '0.0': round(latest_bar['close'] * 0.9, 2),
                                '0.236': round(latest_bar['close'] * 0.95, 2),
                                '0.382': round(latest_bar['close'] * 0.97, 2),
                                '0.5': round(latest_bar['close'], 2),
                                '0.618': round(latest_bar['close'] * 1.03, 2),
                                '0.786': round(latest_bar['close'] * 1.05, 2),
                                '1.0': round(latest_bar['close'] * 1.1, 2),
                            }
                        }
                    }
                    
                    return jsonify({
                        'success': True,
                        'data': data
                    })
        except Exception as e:
            logger.warning(f"Error fetching real market data: {str(e)}, using simulated data instead")
            
        # If we couldn't get real data, generate simulated data
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
            },
            'is_simulated': True
        }
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        logger.error(f"Error getting technical indicators: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/tradingview/market/analysis', methods=['GET', 'OPTIONS'])
def get_market_analysis():
    """
    Get comprehensive market analysis
    Uses real market data when available
    """
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
    try:
        # Generate market analysis data
        current_date = datetime.now()
        
        # Try to get real market data for indices
        indices_symbols = ['SPY', 'QQQ', 'DIA', 'IWM']
        sector_symbols = ['XLK', 'XLF', 'XLE', 'XLV', 'XLP', 'XLY']
        
        indices = []
        sectors = []
        
        # Get real market data for indices
        for symbol in indices_symbols:
            try:
                response = requests.get(f"http://localhost:5000/api/market-data/{symbol}?timeframe=1d&days=5")
                if response.status_code == 200:
                    market_data = response.json()
                    
                    if market_data and 'bars' in market_data and len(market_data['bars']) >= 2:
                        latest_bar = market_data['bars'][-1]
                        prev_bar = market_data['bars'][-2]
                        
                        change = (latest_bar['close'] - prev_bar['close']) / prev_bar['close'] * 100
                        
                        indices.append({
                            'symbol': symbol,
                            'name': get_index_name(symbol),
                            'price': round(latest_bar['close'], 2),
                            'change': round(change, 2)
                        })
                        continue
            except Exception as e:
                logger.warning(f"Error fetching real market data for {symbol}: {str(e)}")
            
            # If real data fails, use mock data
            indices.append({
                'symbol': symbol,
                'name': get_index_name(symbol),
                'price': round(100 + random.random() * 300, 2),
                'change': round(random.random() * 2 - 0.5, 2)
            })
        
        # Get real market data for sectors
        for symbol in sector_symbols:
            try:
                response = requests.get(f"http://localhost:5000/api/market-data/{symbol}?timeframe=1d&days=5")
                if response.status_code == 200:
                    market_data = response.json()
                    
                    if market_data and 'bars' in market_data and len(market_data['bars']) >= 2:
                        latest_bar = market_data['bars'][-1]
                        prev_bar = market_data['bars'][-2]
                        
                        change = (latest_bar['close'] - prev_bar['close']) / prev_bar['close'] * 100
                        
                        sectors.append({
                            'symbol': symbol,
                            'name': get_sector_name(symbol),
                            'price': round(latest_bar['close'], 2),
                            'change': round(change, 2)
                        })
                        continue
            except Exception as e:
                logger.warning(f"Error fetching real market data for {symbol}: {str(e)}")
            
            # If real data fails, use mock data
            sectors.append({
                'symbol': symbol,
                'name': get_sector_name(symbol),
                'price': round(50 + random.random() * 100, 2),
                'change': round(random.random() * 2 - 0.5, 2)
            })
        
        # Market breadth indicators (mock data)
        breadth = {
            'advance_decline_ratio': round(random.random() * 3 + 0.5, 2),
            'percent_above_sma_200': round(random.random() * 50 + 30, 1),
            'percent_above_sma_50': round(random.random() * 40 + 40, 1),
            'new_highs': int(random.random() * 100),
            'new_lows': int(random.random() * 50),
        }
        
        # Try to get real VIX data
        vix = 20  # Default value
        try:
            response = requests.get("http://localhost:5000/api/market-data/VIX?timeframe=1d&days=1")
            if response.status_code == 200:
                market_data = response.json()
                
                if market_data and 'bars' in market_data and len(market_data['bars']) > 0:
                    latest_bar = market_data['bars'][-1]
                    vix = latest_bar['close']
        except Exception as e:
            logger.warning(f"Error fetching real VIX data: {str(e)}")
            vix = 15 + random.random() * 15  # VIX between 15-30
        
        # Calculate market sentiment
        avg_index_change = sum(float(idx['change']) for idx in indices) / len(indices)
        avg_sector_change = sum(float(sec['change']) for sec in sectors) / len(sectors)
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
                'vix': round(vix, 2),
                'treasury_10y': round(3 + random.random() * 2, 3),
                'treasury_2y': round(4 + random.random() * 1, 3),
            },
            'market_sentiment': {
                'fear_greed_index': round(fear_greed, 1),
                'sentiment': sentiment,
                'overall_market_trend': 'Bullish' if avg_index_change > 0 else 'Bearish',
                'strongest_sector': max(sectors, key=lambda x: float(x['change']))['name'],
                'weakest_sector': min(sectors, key=lambda x: float(x['change']))['name'],
            }
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        logger.error(f"Error generating market analysis: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Run the application
if __name__ == '__main__':
    try:
        port = 5003  # Use a different port to avoid conflicts
        print(f"\nStarting TradingView integration server on port {port}...")
        print(f"Test route: http://localhost:{port}/api/test")
        print(f"TradingView webhook: http://localhost:{port}/api/tradingview/webhook")
        print(f"TradingView alerts: http://localhost:{port}/api/tradingview/alerts")
        print(f"Bot control: http://localhost:{port}/api/tradingview/bot/control")
        print(f"Bot status: http://localhost:{port}/api/tradingview/bots/status")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc() 