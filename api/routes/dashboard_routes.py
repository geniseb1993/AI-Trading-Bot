from flask import Blueprint, jsonify, request, make_response
import logging
import random
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
from api.utils.cors_utils import add_cors_headers

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Constants
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
DASHBOARD_DIR = os.path.join(DATA_DIR, 'dashboard')

# Helper Functions
def get_mock_positions():
    """Generate mock positions for testing"""
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'AMD', 'META']
    positions = []
    
    for i in range(random.randint(3, 6)):
        symbol = random.choice(symbols)
        symbols.remove(symbol)  # Avoid duplicates
        
        price = round(random.uniform(100, 800), 2)
        quantity = random.randint(1, 10)
        entry_price = round(price * random.uniform(0.9, 1.1), 2)
        
        profit_loss = round((price - entry_price) * quantity, 2)
        profit_loss_pct = round((price - entry_price) / entry_price * 100, 2)
        
        positions.append({
            "symbol": symbol,
            "quantity": quantity,
            "entry_price": entry_price,
            "current_price": price,
            "profit_loss": profit_loss,
            "profit_loss_pct": profit_loss_pct,
            "entry_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        })
    
    return positions

def get_mock_portfolio_performance():
    """Generate mock portfolio performance data"""
    # Generate daily performance for the last 30 days
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    
    # Start with a base value and generate a somewhat realistic performance curve
    base_value = 10000
    daily_changes = [random.uniform(-0.03, 0.04) for _ in range(30)]
    
    # Calculate cumulative values
    values = []
    current_value = base_value
    
    for change in daily_changes:
        current_value *= (1 + change)
        values.append(round(current_value, 2))
    
    values.reverse()  # Reverse to match chronological order of dates
    
    return {
        "dates": dates,
        "values": values,
        "start_value": values[0],
        "current_value": values[-1],
        "total_return": round((values[-1] - values[0]) / values[0] * 100, 2),
        "daily_return": round((values[-1] - values[-2]) / values[-2] * 100, 2) if len(values) > 1 else 0
    }

def get_mock_market_overview():
    """Generate mock market overview data"""
    indices = [
        {"name": "S&P 500", "symbol": "SPX", "value": round(random.uniform(4000, 5000), 2)},
        {"name": "Nasdaq", "symbol": "NDX", "value": round(random.uniform(15000, 17000), 2)},
        {"name": "Dow Jones", "symbol": "DJI", "value": round(random.uniform(34000, 36000), 2)},
        {"name": "Russell 2000", "symbol": "RUT", "value": round(random.uniform(1800, 2100), 2)}
    ]
    
    # Add daily change to each index
    for index in indices:
        change_pct = round(random.uniform(-1.5, 1.5), 2)
        index["change_pct"] = change_pct
        index["change"] = round(index["value"] * change_pct / 100, 2)
    
    # Get sector performance
    sectors = [
        "Technology", "Healthcare", "Financials", "Consumer Discretionary", 
        "Communication Services", "Industrials", "Consumer Staples", 
        "Energy", "Utilities", "Real Estate", "Materials"
    ]
    
    sector_performance = []
    for sector in sectors:
        change_pct = round(random.uniform(-2.0, 2.0), 2)
        sector_performance.append({
            "name": sector,
            "change_pct": change_pct
        })
    
    # Sort sectors by performance
    sector_performance = sorted(sector_performance, key=lambda x: x["change_pct"], reverse=True)
    
    return {
        "indices": indices,
        "sector_performance": sector_performance,
        "market_sentiment": random.choice(["Bullish", "Bearish", "Neutral"]),
        "vix": round(random.uniform(15, 30), 2),
        "timestamp": datetime.now().isoformat()
    }

def get_mock_active_trades():
    """Generate mock active trades for testing"""
    symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'AMZN']
    trade_types = ['LONG', 'SHORT']
    
    trades = []
    for i in range(random.randint(2, 5)):
        symbol = random.choice(symbols)
        trade_type = random.choice(trade_types)
        
        entry_price = round(random.uniform(100, 800), 2)
        current_price = round(entry_price * random.uniform(0.9, 1.1), 2)
        
        profit_loss = round((current_price - entry_price) * (1 if trade_type == 'LONG' else -1), 2)
        profit_loss_pct = round(profit_loss / entry_price * 100, 2)
        
        trades.append({
            "id": f"trade_{i}",
            "symbol": symbol,
            "type": trade_type,
            "entry_price": entry_price,
            "current_price": current_price,
            "quantity": random.randint(1, 10),
            "profit_loss": profit_loss,
            "profit_loss_pct": profit_loss_pct,
            "entry_date": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
            "stop_loss": round(entry_price * (0.95 if trade_type == 'LONG' else 1.05), 2),
            "take_profit": round(entry_price * (1.05 if trade_type == 'LONG' else 0.95), 2),
            "status": "OPEN"
        })
    
    return trades

def get_mock_alerts():
    """Generate mock alerts for testing"""
    alert_types = ["PRICE_ALERT", "TECHNICAL_SIGNAL", "NEWS_ALERT", "TRADE_EXECUTED", "RISK_WARNING"]
    symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'AMZN']
    
    alerts = []
    for i in range(random.randint(3, 7)):
        alert_type = random.choice(alert_types)
        symbol = random.choice(symbols)
        
        timestamp = (datetime.now() - timedelta(minutes=random.randint(5, 180))).isoformat()
        
        if alert_type == "PRICE_ALERT":
            message = f"{symbol} crossed your price target of ${round(random.uniform(100, 800), 2)}"
        elif alert_type == "TECHNICAL_SIGNAL":
            signal_types = ["MACD Crossover", "RSI Oversold", "RSI Overbought", "Golden Cross", "Death Cross"]
            message = f"{symbol} triggered a {random.choice(signal_types)} signal"
        elif alert_type == "NEWS_ALERT":
            news_events = ["Earnings Report", "FDA Approval", "CEO Change", "Acquisition", "Stock Split"]
            message = f"{symbol} announced {random.choice(news_events)}"
        elif alert_type == "TRADE_EXECUTED":
            trade_types = ["BUY", "SELL"]
            message = f"{random.choice(trade_types)} order for {symbol} executed at ${round(random.uniform(100, 800), 2)}"
        else:  # RISK_WARNING
            message = f"Risk level for {symbol} position exceeds threshold"
        
        alerts.append({
            "id": f"alert_{i}",
            "type": alert_type,
            "symbol": symbol,
            "message": message,
            "timestamp": timestamp,
            "priority": random.choice(["HIGH", "MEDIUM", "LOW"]),
            "read": random.choice([True, False])
        })
    
    # Sort by timestamp (newest first)
    alerts = sorted(alerts, key=lambda x: x["timestamp"], reverse=True)
    
    return alerts

# API Endpoints
@dashboard_bp.route('/dashboard', methods=['GET', 'OPTIONS'])
def get_dashboard():
    """Get dashboard overview data"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
    
    try:
        # In a production environment, this would fetch real data
        # For now, we'll generate mock data for demonstration
        
        response_data = {
            "success": True,
            "dashboard": {
                "account_summary": {
                    "total_value": round(random.uniform(10000, 100000), 2),
                    "cash_balance": round(random.uniform(5000, 50000), 2),
                    "total_pnl": round(random.uniform(-5000, 15000), 2),
                    "total_pnl_pct": round(random.uniform(-15, 35), 2),
                    "win_rate": round(random.uniform(50, 80), 2),
                    "trade_count": random.randint(10, 50)
                },
                "active_positions": get_mock_positions()[:3],  # Just show top 3
                "recent_trades": get_mock_active_trades()[:3],  # Just show top 3
                "recent_alerts": get_mock_alerts()[:3],  # Just show top 3
                "market_overview": {
                    "indices": get_mock_market_overview()["indices"][:3]  # Just show top 3
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        response = make_response(jsonify(response_data))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {str(e)}")
        response = make_response(jsonify({
            "success": False,
            "error": str(e)
        }), 500)
        return add_cors_headers(response)

@dashboard_bp.route('/active-trades', methods=['GET', 'OPTIONS'])
def get_active_trades():
    """Get all active trades"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
    
    try:
        response_data = {
            "success": True,
            "trades": get_mock_active_trades(),
            "timestamp": datetime.now().isoformat()
        }
        
        response = make_response(jsonify(response_data))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error retrieving active trades: {str(e)}")
        response = make_response(jsonify({
            "success": False,
            "error": str(e)
        }), 500)
        return add_cors_headers(response)

@dashboard_bp.route('/broker/positions', methods=['GET', 'OPTIONS'])
def get_positions():
    """Get all current positions"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
    
    try:
        response_data = {
            "success": True,
            "positions": get_mock_positions(),
            "timestamp": datetime.now().isoformat()
        }
        
        response = make_response(jsonify(response_data))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error retrieving positions: {str(e)}")
        response = make_response(jsonify({
            "success": False,
            "error": str(e)
        }), 500)
        return add_cors_headers(response)

@dashboard_bp.route('/market-overview', methods=['GET', 'OPTIONS'])
def get_market_overview():
    """Get market overview data"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
    
    try:
        response_data = {
            "success": True,
            "market_overview": get_mock_market_overview(),
            "timestamp": datetime.now().isoformat()
        }
        
        response = make_response(jsonify(response_data))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error retrieving market overview: {str(e)}")
        response = make_response(jsonify({
            "success": False,
            "error": str(e)
        }), 500)
        return add_cors_headers(response)

@dashboard_bp.route('/portfolio-performance', methods=['GET', 'OPTIONS'])
def get_portfolio_performance():
    """Get portfolio performance data"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
    
    try:
        response_data = {
            "success": True,
            "performance": get_mock_portfolio_performance(),
            "timestamp": datetime.now().isoformat()
        }
        
        response = make_response(jsonify(response_data))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error retrieving portfolio performance: {str(e)}")
        response = make_response(jsonify({
            "success": False,
            "error": str(e)
        }), 500)
        return add_cors_headers(response)

@dashboard_bp.route('/alerts', methods=['GET', 'OPTIONS'])
def get_alerts():
    """Get all alerts"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
    
    try:
        response_data = {
            "success": True,
            "alerts": get_mock_alerts(),
            "timestamp": datetime.now().isoformat()
        }
        
        response = make_response(jsonify(response_data))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error retrieving alerts: {str(e)}")
        response = make_response(jsonify({
            "success": False,
            "error": str(e)
        }), 500)
        return add_cors_headers(response)

@dashboard_bp.route('/run-backtest', methods=['POST', 'OPTIONS'])
def run_backtest():
    """Run a backtest with specified parameters"""
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response('', 200))
    
    try:
        data = request.get_json() or {}
        
        # In a real implementation, this would run an actual backtest
        # For now, we'll generate mock results
        
        # Extract parameters with defaults
        symbols = data.get('symbols', ['SPY'])
        start_date = data.get('start_date', (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
        end_date = data.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        strategy = data.get('strategy', 'dual_bot')
        
        # Generate mock backtest results
        backtest_days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days
        
        # Start with a base value and generate a somewhat realistic performance curve
        base_value = 10000
        daily_returns = [random.uniform(-0.02, 0.025) for _ in range(backtest_days)]
        
        # Calculate cumulative values
        equity_curve = [base_value]
        for ret in daily_returns:
            equity_curve.append(equity_curve[-1] * (1 + ret))
        
        # Calculate metrics
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0] * 100
        max_drawdown = 0
        peak = equity_curve[0]
        
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Generate random trades
        trades = []
        trade_count = random.randint(15, 30)
        win_count = int(trade_count * random.uniform(0.5, 0.7))
        
        for i in range(trade_count):
            is_win = i < win_count  # Ensure win_rate matches win_count/trade_count
            
            trade_return = random.uniform(1.5, 5.0) if is_win else random.uniform(-4.0, -1.0)
            
            trades.append({
                "id": i,
                "symbol": random.choice(symbols),
                "entry_date": (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=random.randint(0, backtest_days))).strftime('%Y-%m-%d'),
                "exit_date": (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=random.randint(0, backtest_days))).strftime('%Y-%m-%d'),
                "type": random.choice(["LONG", "SHORT"]),
                "return": round(trade_return, 2),
                "is_win": is_win
            })
        
        backtest_results = {
            "equity_curve": [round(v, 2) for v in equity_curve],
            "dates": [(datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(backtest_days + 1)],
            "total_return": round(total_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "sharpe_ratio": round(random.uniform(0.8, 2.5), 2),
            "win_rate": round(win_count / trade_count * 100, 2),
            "trade_count": trade_count,
            "avg_trade_return": round(sum(t["return"] for t in trades) / len(trades), 2),
            "trades": trades
        }
        
        response_data = {
            "success": True,
            "backtest": {
                "parameters": {
                    "symbols": symbols,
                    "start_date": start_date,
                    "end_date": end_date,
                    "strategy": strategy
                },
                "results": backtest_results
            },
            "timestamp": datetime.now().isoformat()
        }
        
        response = make_response(jsonify(response_data))
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Error running backtest: {str(e)}")
        response = make_response(jsonify({
            "success": False,
            "error": str(e)
        }), 500)
        return add_cors_headers(response) 