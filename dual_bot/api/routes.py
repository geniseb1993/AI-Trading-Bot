from flask import Blueprint, jsonify, request
import logging
from datetime import datetime
import random
import json
import os

# Create blueprint
api = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Sample data for demonstration when real AI models aren't available
SAMPLE_DATA = {
    'symbols': ['QQQ', 'TSLA', 'PLTR', 'AAPL', 'NVDA', 'SPY', 'MSFT'],
    'active_positions': [],
    'trades_executed': 36,
    'success_rate': 0.88,
}

# In-memory storage for demo data
bot_status = {
    'status': True,
    'active_positions': SAMPLE_DATA['active_positions'],
    'last_update': datetime.now().isoformat(),
    'trades_executed': SAMPLE_DATA['trades_executed'],
    'success_rate': SAMPLE_DATA['success_rate'],
    'next_scan': (datetime.now().replace(microsecond=0, second=0) + 
                  datetime.timedelta(minutes=5)).isoformat()
}

market_data = {
    symbol: {
        'symbol': symbol,
        'price': random.uniform(100, 1000) if symbol != 'QQQ' else 456.78,
        'timestamp': datetime.now().isoformat()
    } for symbol in SAMPLE_DATA['symbols']
}

config = {
    'symbols': SAMPLE_DATA['symbols'],
    'trading_hours': {
        'start': '09:30',
        'end': '16:00'
    },
    'risk_limits': {
        'max_position_size': 5000,
        'max_daily_loss': 2000
    }
}

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    logger.info("Health check called")
    return jsonify({'status': 'healthy'})

@api.route('/status', methods=['GET'])
def get_status():
    """Get the status of the Dual Bot."""
    logger.info("Status endpoint called")
    # Update the last_update time
    bot_status['last_update'] = datetime.now().isoformat()
    return jsonify(bot_status)

@api.route('/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    """Get simplified market data for a symbol."""
    logger.info(f"Market data requested for {symbol}")
    
    # Check if symbol exists in our data
    if symbol not in market_data:
        market_data[symbol] = {
            'symbol': symbol,
            'price': random.uniform(100, 1000),
            'timestamp': datetime.now().isoformat()
        }
    else:
        # Slightly change the price to simulate real-time updates
        current_price = market_data[symbol]['price']
        change = random.uniform(-0.02, 0.02) * current_price
        market_data[symbol]['price'] = current_price + change
        market_data[symbol]['timestamp'] = datetime.now().isoformat()
    
    return jsonify(market_data[symbol])

@api.route('/options-data/<symbol>', methods=['GET'])
def get_options_data(symbol):
    """Get options data for a symbol."""
    logger.info(f"Options data requested for {symbol}")
    
    # Generate mock options data
    base_price = market_data.get(symbol, {'price': 100.0})['price']
    
    options_data = {
        'symbol': symbol,
        'options': [
            {
                'strike': round(base_price * (1 + i * 0.01), 2),
                'callPrice': round(random.uniform(1.0, 5.0), 2),
                'putPrice': round(random.uniform(1.0, 5.0), 2),
                'expirationDate': (datetime.now() + datetime.timedelta(days=i*7)).strftime('%Y-%m-%d'),
                'iv': round(random.uniform(0.2, 0.5), 2),
                'volume': random.randint(100, 5000)
            } for i in range(-5, 6)
        ]
    }
    
    return jsonify(options_data)

@api.route('/news/<symbol>', methods=['GET'])
def get_news(symbol):
    """Get news for a symbol."""
    logger.info(f"News requested for {symbol}")
    
    # Generate mock news data
    news = [
        {
            'title': f"{symbol} Reaches New High on Strong Earnings",
            'source': "Financial Times",
            'url': f"https://example.com/news/{symbol.lower()}/1",
            'sentiment': "positive",
            'relevance': round(random.uniform(0.7, 0.95), 2),
            'published_at': (datetime.now() - datetime.timedelta(hours=random.randint(1, 24))).isoformat()
        },
        {
            'title': f"Analysts Upgrade {symbol} After Product Announcement",
            'source': "Market News",
            'url': f"https://example.com/news/{symbol.lower()}/2",
            'sentiment': "positive",
            'relevance': round(random.uniform(0.7, 0.95), 2),
            'published_at': (datetime.now() - datetime.timedelta(hours=random.randint(1, 24))).isoformat()
        }
    ]
    
    return jsonify(news)

@api.route('/scan', methods=['POST'])
def scan_trades():
    """Scan for trade recommendations."""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        logger.info(f"Scanning for trade recommendations for {symbol}")
        
        # Check if we have market data for this symbol
        if symbol not in market_data:
            # Create it if not
            get_market_data(symbol)
        
        price = market_data[symbol]['price']
        
        # Generate a mock trade recommendation
        is_bullish = random.random() > 0.3  # 70% chance of bullish recommendation
        
        recommendation = {
            'symbol': symbol,
            'trade_type': 'BUY_CALL' if is_bullish else 'BUY_PUT',
            'strike': round(price * (1.01 if is_bullish else 0.99), 2),
            'expiration': (datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
            'entry_price': round(random.uniform(2.0, 4.0), 2),
            'target_price': round(random.uniform(4.0, 8.0), 2),
            'stop_loss': round(random.uniform(1.0, 1.8), 2),
            'confidence': round(random.uniform(0.65, 0.95), 2),
            'rationale': (
                "Strong bullish momentum with increasing volume and positive technicals. "
                "Recent price action shows consolidation above key support, with MACD showing "
                "bullish crossover and RSI indicating room for upward movement."
            ) if is_bullish else (
                "Bearish divergence on technical indicators with weakening price momentum. "
                "Recent resistance levels holding firm with decreasing volume on rallies. "
                "Options flow shows increasing put activity and sentiment turning negative."
            )
        }
        
        logger.info(f"Generated recommendation for {symbol}: {recommendation['trade_type']}")
        return jsonify(recommendation)
    except Exception as e:
        logger.error(f"Error scanning trades: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/assess-risk', methods=['POST'])
def assess_risk():
    """Assess risk for a trade recommendation."""
    try:
        data = request.get_json()
        recommendation = data.get('recommendation')
        market_context = data.get('market_context')
        
        if not recommendation or not market_context:
            return jsonify({'error': 'Recommendation and market context are required'}), 400
        
        logger.info(f"Assessing risk for {recommendation.get('symbol')} recommendation")
        
        # Generate a mock risk assessment
        confidence = recommendation.get('confidence', 0.75)
        approved = random.random() < confidence  # Higher confidence trades more likely to be approved
        
        assessment = {
            'approved': approved,
            'risk_score': round(random.uniform(3.0, 9.0), 1),
            'market_conditions': 'Favorable' if approved else 'Uncertain',
            'concerns': None if approved else 'Elevated volatility and weakening technical indicators suggest caution',
            'summary': (
                "This trade has a positive risk/reward ratio with well-defined exit points. "
                "The technicals align with the trade direction and current market sentiment is supportive."
            ) if approved else (
                "While the trade setup has merit, current market conditions suggest increased risk. "
                "Consider reducing position size or waiting for confirmation before entering this trade."
            )
        }
        
        logger.info(f"Risk assessment for {recommendation.get('symbol')}: {'APPROVED' if approved else 'REJECTED'}")
        return jsonify(assessment)
    except Exception as e:
        logger.error(f"Error assessing risk: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/check-position', methods=['POST'])
def check_position():
    """Check if a position should be closed."""
    try:
        data = request.get_json()
        position = data.get('position')
        market_data_input = data.get('market_data')
        
        if not position or not market_data_input:
            return jsonify({'error': 'Position and market data are required'}), 400
        
        logger.info(f"Checking position for {position.get('symbol')}")
        
        # Randomly decide if position should be closed
        should_close = random.random() > 0.7  # 30% chance of recommending closure
        
        return jsonify({
            'should_close': should_close,
            'reason': 'Target price reached' if should_close else 'Position still valid'
        })
    except Exception as e:
        logger.error(f"Error checking position: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/config', methods=['GET'])
def get_config():
    """Get the current configuration."""
    logger.info("Config requested")
    return jsonify(config) 