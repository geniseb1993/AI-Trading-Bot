"""
Enhanced Institutional Flow API Routes

This module provides API endpoints for the enhanced institutional flow analyzer,
allowing for more detailed and accurate analysis of institutional trading activity.
"""

import logging
import random
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np

# Import the enhanced analyzer
from execution_model.enhanced_institutional_flow import EnhancedInstitutionalFlowAnalyzer

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('institutional_flow', __name__, url_prefix='/api/institutional-flow')

# Initialize analyzer with empty config (will be set in before_app_request)
enhanced_analyzer = None

# API keys and services
unusual_whales_api = None
polygon_api = None

def init_services(app_config):
    """Initialize services with application config"""
    global enhanced_analyzer, unusual_whales_api, polygon_api
    
    # Initialize the enhanced analyzer
    enhanced_analyzer = EnhancedInstitutionalFlowAnalyzer(app_config)
    
    # Initialize API services if available
    # This would normally connect to actual data providers
    
    logger.info("Enhanced institutional flow services initialized")

@bp.route('/enhanced-analysis', methods=['POST'])
def enhanced_flow_analysis():
    """
    Perform enhanced analysis of institutional flow for a symbol or list of symbols
    
    Expected JSON:
    {
        "symbols": ["AAPL", "MSFT", "GOOGL"],  # Required
        "days_back": 30,                        # Optional, default 30
        "include_raw_data": false              # Optional, default false
    }
    
    Returns:
        JSON with enhanced analysis results
    """
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        if 'symbols' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: symbols'
            }), 400
        
        # Get parameters
        symbols = data['symbols']
        days_back = int(data.get('days_back', 30))
        include_raw_data = data.get('include_raw_data', False)
        
        # Ensure symbols is a list
        if isinstance(symbols, str):
            symbols = [symbols]
        
        logger.info(f"Enhanced flow analysis requested for {len(symbols)} symbols, {days_back} days back")
        
        # Initialize result
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'days_analyzed': days_back,
            'analysis_version': 'enhanced-v1.0',
            'flow_analysis': {},
            'smart_money_moves': []
        }
        
        # Get flow data from API/service
        flow_data = get_flow_data(symbols, days_back)
        
        # Check if we got real or mock data
        result['is_real_data'] = flow_data.get('is_real_data', False)
        result['data_source'] = flow_data.get('source', 'mock')
        
        # Get market data for each symbol
        market_data = {}
        for symbol in symbols:
            market_data[symbol] = get_market_data(symbol, days_back)
        
        # Analyze each symbol
        for symbol in symbols:
            symbol_market_data = market_data.get(symbol)
            
            if enhanced_analyzer:
                # Perform enhanced analysis
                analysis = enhanced_analyzer.analyze_flow(flow_data, symbol_market_data, symbol)
                result['flow_analysis'][symbol] = analysis
                
                # Optionally exclude raw data components to reduce payload size
                if not include_raw_data:
                    if 'options_details' in analysis:
                        del analysis['options_details']
                    if 'dark_pool_details' in analysis:
                        del analysis['dark_pool_details']
                    if 'block_trade_details' in analysis:
                        del analysis['block_trade_details']
            else:
                logger.error("Enhanced analyzer not initialized")
                result['flow_analysis'][symbol] = {
                    'symbol': symbol,
                    'error': 'Analyzer not initialized',
                    'timestamp': datetime.now().isoformat()
                }
        
        # Detect smart money moves
        if enhanced_analyzer:
            smart_money_moves = enhanced_analyzer.get_smart_money_moves(flow_data)
            result['smart_money_moves'] = smart_money_moves
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in enhanced flow analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/data', methods=['GET'])
def get_flow_data_endpoint():
    """
    Get raw institutional flow data for client-side analysis
    
    Query parameters:
    - symbols: Comma-separated list of symbols
    - days: Number of days back to get data (default 7)
    - type: Type of data to retrieve (options, darkpool, block_trades, all)
    
    Returns:
        JSON with raw flow data
    """
    try:
        # Get parameters
        symbols_param = request.args.get('symbols', '')
        days = int(request.args.get('days', 7))
        data_type = request.args.get('type', 'all').lower()
        
        symbols = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]
        
        logger.info(f"Raw flow data requested for {len(symbols)} symbols, {days} days back, type={data_type}")
        
        # Get flow data
        flow_data = get_flow_data(symbols, days)
        
        # Filter by type if specified
        if data_type != 'all':
            filtered_data = {}
            if data_type in flow_data:
                filtered_data[data_type] = flow_data[data_type]
            flow_data = filtered_data
        
        # Add metadata
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'days': days,
            'is_real_data': flow_data.get('is_real_data', False),
            'source': flow_data.get('source', 'mock'),
            'data': flow_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting flow data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/smart-money', methods=['GET'])
def get_smart_money_moves_endpoint():
    """
    Get high-confidence smart money moves detected across all symbols
    
    Query parameters:
    - days: Number of days back to analyze (default 7)
    - min_confidence: Minimum confidence threshold (default 0.75)
    - limit: Maximum number of moves to return (default 20)
    
    Returns:
        JSON with smart money moves
    """
    try:
        # Get parameters
        days = int(request.args.get('days', 7))
        min_confidence = float(request.args.get('min_confidence', 0.75))
        limit = int(request.args.get('limit', 20))
        
        logger.info(f"Smart money moves requested, {days} days back, min_confidence={min_confidence}")
        
        # Get flow data (all symbols)
        flow_data = get_flow_data([], days)
        
        # Detect smart money moves
        smart_money_moves = []
        if enhanced_analyzer:
            smart_money_moves = enhanced_analyzer.get_smart_money_moves(
                flow_data, min_confidence=min_confidence
            )
            # Limit results
            smart_money_moves = smart_money_moves[:limit]
        
        # Add metadata
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'days_analyzed': days,
            'min_confidence': min_confidence,
            'is_real_data': flow_data.get('is_real_data', False),
            'source': flow_data.get('source', 'mock'),
            'smart_money_moves': smart_money_moves
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting smart money moves: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper functions

def get_flow_data(symbols=None, days_back=7):
    """
    Get institutional flow data from API or generate mock data
    
    Args:
        symbols: List of symbols or None for all
        days_back: Number of days back to get data
        
    Returns:
        Dict: Flow data with options_flow, dark_pool, and block_trades
    """
    # Check if API is available
    is_real_data = False
    data_source = "mock"
    
    if unusual_whales_api and hasattr(unusual_whales_api, 'token'):
        try:
            # Try to get real data
            # This would normally connect to actual data providers
            logger.info("Would connect to real data provider here")
            # For now, we'll use mock data
        except Exception as e:
            logger.error(f"Error fetching real flow data: {str(e)}")
    
    # Generate mock data if needed
    logger.info("Using mock institutional flow data")
    flow_data = generate_mock_flow_data(symbols, days_back)
    
    # Add metadata
    flow_data['is_real_data'] = is_real_data
    flow_data['source'] = data_source
    
    return flow_data

def get_market_data(symbol, days_back=30):
    """
    Get market price data for a symbol
    
    Args:
        symbol: Symbol to get data for
        days_back: Number of days back to get data
        
    Returns:
        pd.DataFrame: Market data with OHLCV
    """
    # This would normally connect to a market data provider
    # For now, generate mock data
    mock_data = generate_mock_market_data(symbol, days_back)
    return mock_data

def generate_mock_flow_data(symbols=None, days_back=7):
    """
    Generate mock institutional flow data for development/testing
    
    Args:
        symbols: List of symbols or None for all available
        days_back: Number of days to generate data for
        
    Returns:
        Dict: Mock flow data
    """
    if not symbols:
        symbols = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOG", "META", "AMD", "INTC", "SPY", "QQQ"]
    elif isinstance(symbols, str):
        symbols = [symbols]
    
    mock_data = {
        'options_flow': [],
        'dark_pool': [],
        'block_trades': []
    }
    
    # Generate timestamps spanning days_back
    now = datetime.now()
    timestamps = []
    for i in range(days_back):
        for _ in range(random.randint(1, 5)):  # 1-5 events per day
            hours_back = i * 24 + random.randint(0, 23)
            timestamps.append(now - timedelta(hours=hours_back))
    
    # Base prices for realistic mock data
    base_prices = {
        "AAPL": 170, "MSFT": 350, "NVDA": 850, "TSLA": 200, "AMZN": 180,
        "GOOG": 170, "META": 480, "AMD": 160, "INTC": 30, "SPY": 500, "QQQ": 430
    }
    
    # Institutions for block trades
    institutions = [
        "BlackRock", "Vanguard", "Fidelity", "State Street", "JP Morgan", 
        "Citadel", "Renaissance Technologies", "Two Sigma", "AQR Capital", 
        "Point72", "Millennium", "Bridgewater"
    ]
    
    # Generate options flow
    for _ in range(len(symbols) * 5):  # ~5 options events per symbol
        symbol = random.choice(symbols)
        timestamp = random.choice(timestamps)
        
        base_price = base_prices.get(symbol, random.uniform(100, 500))
        option_type = "CALL" if random.random() > 0.5 else "PUT"
        is_sweep = random.random() > 0.7
        is_block = not is_sweep and random.random() > 0.5
        
        exp_date = (now + timedelta(days=random.randint(7, 180)))
        strike = round(base_price * random.uniform(0.8, 1.2), 1)
        
        # More realistic volumes and premiums
        volume = random.randint(10, 500) * 10
        premium = volume * random.uniform(1, 20) * 100
        
        mock_data['options_flow'].append({
            'symbol': symbol,
            'type': option_type,
            'volume': volume,
            'premium': premium,
            'strike': strike,
            'expiration': exp_date.strftime("%Y-%m-%d"),
            'sweep': is_sweep,
            'block': is_block,
            'timestamp': timestamp.isoformat()
        })
    
    # Generate dark pool
    for _ in range(len(symbols) * 4):  # ~4 dark pool events per symbol
        symbol = random.choice(symbols)
        timestamp = random.choice(timestamps)
        
        base_price = base_prices.get(symbol, random.uniform(100, 500))
        price = round(base_price * random.uniform(0.95, 1.05), 2)
        
        volume = random.randint(1000, 50000)
        side = "BUY" if random.random() > 0.5 else "SELL"
        off_hours = random.random() > 0.7
        
        mock_data['dark_pool'].append({
            'symbol': symbol,
            'side': side,
            'volume': volume,
            'price': price,
            'value': round(price * volume, 2),
            'timestamp': timestamp.isoformat(),
            'off_hours': off_hours,
            'exchange': random.choice(["NYSE", "NASDAQ", "IEX", "CBOE"])
        })
    
    # Generate block trades
    for _ in range(len(symbols) * 3):  # ~3 block trades per symbol
        symbol = random.choice(symbols)
        timestamp = random.choice(timestamps)
        
        base_price = base_prices.get(symbol, random.uniform(100, 500))
        price = round(base_price * random.uniform(0.98, 1.02), 2)
        
        volume = random.randint(10000, 200000)
        side = "BUY" if random.random() > 0.5 else "SELL"
        institution = random.choice(institutions)
        
        mock_data['block_trades'].append({
            'symbol': symbol,
            'side': side,
            'volume': volume,
            'price': price,
            'value': round(price * volume, 2),
            'timestamp': timestamp.isoformat(),
            'institution': institution
        })
    
    return mock_data

def generate_mock_market_data(symbol, days_back=30):
    """
    Generate mock market data for development/testing
    
    Args:
        symbol: Symbol to generate data for
        days_back: Number of days to generate
        
    Returns:
        pd.DataFrame: Mock market data with OHLCV
    """
    # Base price for the symbol
    base_prices = {
        "AAPL": 170, "MSFT": 350, "NVDA": 850, "TSLA": 200, "AMZN": 180,
        "GOOG": 170, "META": 480, "AMD": 160, "INTC": 30, "SPY": 500, "QQQ": 430
    }
    
    base_price = base_prices.get(symbol, random.uniform(100, 500))
    volatility = 0.015  # 1.5% daily volatility
    
    # Generate dates
    end_date = pd.Timestamp.now().normalize()
    start_date = end_date - pd.Timedelta(days=days_back)
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
    
    # Initialize price
    price = base_price
    
    # Generate data
    data = []
    for date in dates:
        # Random daily return with slight upward bias
        daily_return = np.random.normal(0.0005, volatility)
        price *= (1 + daily_return)
        
        # Generate OHLC
        day_volatility = price * 0.01  # 1% intraday volatility
        high = price + abs(np.random.normal(0, day_volatility))
        low = price - abs(np.random.normal(0, day_volatility))
        open_price = price - daily_return * price / 2  # Halfway between yesterday and today
        close = price
        
        # Generate volume
        avg_volume = base_price * 50000  # Higher price = higher baseline volume
        volume = int(avg_volume * (1 + np.random.normal(0, 0.3)))  # 30% volume volatility
        
        data.append({
            'date': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    
    return df 