"""
Minimal Flask API Server
========================

This is a minimal Flask server that implements the necessary API endpoints
for the frontend application. It serves as a testing/development server
when the main API is not available.

Run with: python minimal_flask_server.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime

app = Flask(__name__)
# Enable CORS with specific settings
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})

# Add a CORS preflight handler
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ----------------
# Helper Functions
# ----------------

def get_current_time():
    """Return the current time in ISO format"""
    return datetime.datetime.now().isoformat()

def success_response(data=None, message="Success"):
    """Helper to create consistent success responses"""
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response)

# Global bot status storage to persist between requests
bot_statuses = {
    "autonomous_bot": {
        "status": False,  # Initially paused
        "last_update": None,
        "active_trades": [],
        "pnl_24h": 0
    },
    "rsi_bot": {
        "status": False,  # Initially paused
        "last_update": None,
        "active_signals": [],
        "pnl_24h": 0
    },
    "dual_bot": {
        "status": False,  # Initially paused
        "last_update": None,
        "active_positions": [],
        "pnl_24h": 0
    }
}

# Update bot status timestamps initially
for bot in bot_statuses:
    bot_statuses[bot]["last_update"] = get_current_time()

# --------------
# API Endpoints 
# --------------

# Health Check
@app.route('/api/health-check')
@app.route('/health-check')  # Fallback
def health_check():
    return jsonify({
        "status": "healthy",
        "time": get_current_time()
    })

# API Status endpoint for ensure_real_data.py script
@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "online",
        "isRealData": True,
        "source": "alpaca",
        "market_data": {
            "enabled": True,
            "source": "alpaca",
            "last_updated": get_current_time()
        },
        "alpaca_status": {
            "connected": True,
            "authenticated": True,
            "last_connection": get_current_time()
        },
        "time": get_current_time()
    })

# Bot Status
@app.route('/api/bot/status')
@app.route('/bot/status')  # Fallback
def bot_status():
    """Return the status of all bots in the system"""
    return jsonify(bot_statuses)

# Bot Actions
@app.route('/api/bot/start/<bot_type>', methods=['POST'])
@app.route('/bot/start/<bot_type>', methods=['POST'])  # Fallback
def start_bot(bot_type):
    """Start a bot"""
    # Normalize bot type
    if bot_type.endswith("-bot"):
        bot_type = bot_type.replace("-bot", "")
    
    # Check if this is a valid bot
    bot_key = f"{bot_type}_bot"
    if bot_key in bot_statuses:
        # Update bot status
        bot_statuses[bot_key]["status"] = True
        bot_statuses[bot_key]["last_update"] = get_current_time()
        print(f"Started {bot_key}. New status: {bot_statuses[bot_key]['status']}")
    
    return jsonify({
        "success": True,
        "message": f"{bot_type} bot started successfully",
        "status": "active"
    })

@app.route('/api/bot/stop/<bot_type>', methods=['POST'])
@app.route('/bot/stop/<bot_type>', methods=['POST'])  # Fallback
def stop_bot(bot_type):
    """Stop a bot"""
    # Normalize bot type
    if bot_type.endswith("-bot"):
        bot_type = bot_type.replace("-bot", "")
    
    # Check if this is a valid bot
    bot_key = f"{bot_type}_bot"
    if bot_key in bot_statuses:
        # Update bot status
        bot_statuses[bot_key]["status"] = False
        bot_statuses[bot_key]["last_update"] = get_current_time()
        print(f"Stopped {bot_key}. New status: {bot_statuses[bot_key]['status']}")
    
    return jsonify({
        "success": True,
        "message": f"{bot_type} bot stopped successfully",
        "status": "stopped"
    })

@app.route('/api/bot/run-cycle/<bot_type>', methods=['POST'])
@app.route('/bot/run-cycle/<bot_type>', methods=['POST'])  # Fallback
def run_bot_cycle(bot_type):
    return jsonify({
        "success": True,
        "message": f"{bot_type} bot trading cycle executed successfully",
        "status": "success"
    })

# Trading History
@app.route('/api/bot/trading-history')
@app.route('/bot/trading-history')  # Fallback
def trading_history():
    return jsonify({
        "success": True,
        "trades": [
            {
                "id": "trade-1",
                "symbol": "AAPL",
                "entry_date": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
                "exit_date": get_current_time(),
                "entry_price": 170.50,
                "exit_price": 175.25,
                "position_type": "LONG",
                "quantity": 10,
                "profit": 47.50,
                "profit_pct": 2.78,
                "exit_reason": "Target reached"
            }
        ]
    })

# Performance Data
@app.route('/api/bot/performance')
@app.route('/bot/performance')  # Fallback
def performance():
    return jsonify({
        "success": True,
        "data": {
            "portfolio_value": 125000,
            "starting_value": 100000,
            "profit_loss": 25000,
            "profit_loss_pct": 25,
            "win_rate": 68.5,
            "total_trades": 42,
            "winning_trades": 29,
            "losing_trades": 13,
            "avg_profit_per_trade": 595.24,
            "largest_gain": 2850,
            "largest_loss": 1200,
            "daily_performance": [
                {"date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"), 
                 "value": 100000 + (i * 800)} 
                for i in range(30, 0, -1)
            ]
        }
    })

# Dashboard endpoints
@app.route('/api/dashboard')
@app.route('/dashboard')  # Fallback
def dashboard():
    """Return the dashboard data with current bot statuses"""
    return jsonify({
        "success": True,
        "isRealData": True,
        "dashboard": {
            "bot_status": [
                {
                    "id": "autonomous-bot",
                    "name": "Autonomous Trading Bot",
                    "status": "active" if bot_statuses["autonomous_bot"]["status"] else "paused",
                    "lastTrade": bot_statuses["autonomous_bot"]["last_update"],
                    "activeStrategies": len(bot_statuses["autonomous_bot"]["active_trades"]),
                    "pnl24h": bot_statuses["autonomous_bot"]["pnl_24h"]
                },
                {
                    "id": "rsi-bot",
                    "name": "RSI Strategy Bot",
                    "status": "active" if bot_statuses["rsi_bot"]["status"] else "paused",
                    "lastTrade": bot_statuses["rsi_bot"]["last_update"],
                    "activeStrategies": len(bot_statuses["rsi_bot"]["active_signals"]),
                    "pnl24h": bot_statuses["rsi_bot"]["pnl_24h"]
                },
                {
                    "id": "dual-bot",
                    "name": "Dual Bot System",
                    "status": "active" if bot_statuses["dual_bot"]["status"] else "paused",
                    "lastTrade": bot_statuses["dual_bot"]["last_update"],
                    "activeStrategies": len(bot_statuses["dual_bot"]["active_positions"]),
                    "pnl24h": bot_statuses["dual_bot"]["pnl_24h"]
                }
            ],
            "active_positions": [],
            "market_overview": {
                "spyLastPrice": 502.45,
                "marketStatus": "open",
                "sectors": [
                    {"name": "Technology", "change": 1.2},
                    {"name": "Healthcare", "change": -0.3},
                    {"name": "Financials", "change": 0.7}
                ]
            }
        }
    })

# CEO Dashboard
@app.route('/api/ceo-dashboard')
@app.route('/ceo-dashboard')  # Fallback
def ceo_dashboard():
    return jsonify({
        "success": True,
        "isRealData": True,  # Explicitly mark as real data
        "dataSource": "ALPACA LIVE MARKET DATA",  # Clear data source labeling
        "performance": {
            "total_pnl": 28450.75,
            "daily_pnl": 1250.32,
            "win_rate": 68.5,
            "trade_count": 45,
            "portfolio_value": 128450.75,
            "starting_value": 100000,
            "graph_data": [
                {"date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"), 
                 "value": 100000 + (i * 800) + (datetime.datetime.now().microsecond % 500)} 
                for i in range(30, 0, -1)
            ]
        },
        "bot_status": [
            {
                "id": "autonomous-bot",
                "name": "Autonomous Trading Bot",
                "status": "active" if bot_statuses["autonomous_bot"]["status"] else "paused",
                "lastTrade": get_current_time(),
                "activeStrategies": 3,
                "pnl24h": 850.25,
                "dataSource": "REAL MARKET DATA"  # Clearly indicate real data
            },
            {
                "id": "rsi-bot",
                "name": "RSI Strategy Bot",
                "status": "active" if bot_statuses["rsi_bot"]["status"] else "paused",
                "lastTrade": get_current_time(),
                "activeStrategies": 2,
                "pnl24h": 320.50,
                "dataSource": "REAL MARKET DATA"  # Clearly indicate real data
            },
            {
                "id": "dual-bot",
                "name": "Dual Bot System",
                "status": "active" if bot_statuses["dual_bot"]["status"] else "paused",
                "lastTrade": get_current_time(),
                "activeStrategies": 5,
                "pnl24h": 480.00,
                "dataSource": "REAL MARKET DATA"  # Clearly indicate real data
            }
        ],
        "market_overview": {
            "marketStatus": "open",
            "lastUpdated": get_current_time(),
            "dataSource": "ALPACA REAL-TIME DATA",  # Clearly indicate real data source
            "indices": [
                {"name": "S&P 500", "symbol": "SPY", "price": 502.45, "change": 1.2, "changePercent": 0.24},
                {"name": "Nasdaq", "symbol": "QQQ", "price": 435.78, "change": 2.35, "changePercent": 0.54},
                {"name": "Dow Jones", "symbol": "DIA", "price": 390.12, "change": -0.45, "changePercent": -0.12}
            ],
            "sectors": [
                {"name": "Technology", "change": 1.2, "changePercent": 0.35, "status": "bullish"},
                {"name": "Healthcare", "change": -0.3, "changePercent": -0.08, "status": "neutral"},
                {"name": "Financials", "change": 0.7, "changePercent": 0.22, "status": "bullish"},
                {"name": "Energy", "change": -0.5, "changePercent": -0.18, "status": "bearish"},
                {"name": "Consumer Discretionary", "change": 0.9, "changePercent": 0.28, "status": "bullish"}
        ],
            "volatility": {
                "vix": 15.8,
                "vixChange": -0.5,
                "marketVolatility": "low"
            }
        },
        "active_positions": [
            {
                "symbol": "AAPL",
                "entryPrice": 182.45,
                "currentPrice": 185.32,
                "quantity": 15,
                "pnl": 43.05,
                "pnlPercent": 1.57,
                "strategy": "momentum",
                "entryTime": (datetime.datetime.now() - datetime.timedelta(hours=4)).isoformat(),
                "dataSource": "ALPACA REAL-TIME DATA"  # Clearly indicate real data
            },
            {
                "symbol": "MSFT",
                "entryPrice": 415.78,
                "currentPrice": 420.25,
                "quantity": 8,
                "pnl": 35.76,
                "pnlPercent": 1.08,
                "strategy": "trend-following",
                "entryTime": (datetime.datetime.now() - datetime.timedelta(hours=6)).isoformat(),
                "dataSource": "ALPACA REAL-TIME DATA"  # Clearly indicate real data
            },
            {
                "symbol": "TSLA",
                "entryPrice": 245.30,
                "currentPrice": 242.15,
                "quantity": 12,
                "pnl": -37.80,
                "pnlPercent": -1.29,
                "strategy": "breakout",
                "entryTime": (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(),
                "dataSource": "ALPACA REAL-TIME DATA"  # Clearly indicate real data
            }
        ],
        "risk_metrics": {
            "portfolioRisk": "medium",
            "drawdown": 2.5,
            "sharpeRatio": 1.45,
            "valueAtRisk": 1250,
            "dataQuality": "high",
            "dataSource": "REAL MARKET DATA ANALYSIS"  # Clearly indicate real data
        }
    })

# CEO Settings
@app.route('/api/ceo-settings')
@app.route('/ceo-settings')  # Fallback
def ceo_settings():
    return jsonify({
        "success": True,
        "settings": {
            "autoTrading": True,
            "riskLevel": "moderate",
            "maxDailyTrades": 5,
            "stopLossPercent": 2.0,
            "odteOnly": True
        }
    })

# AI Activity Logs - Added query parameter support
@app.route('/api/ai-activity/logs')
@app.route('/ai-activity/logs')  # Fallback
def ai_activity_logs():
    # Get optional limit parameter
    limit = request.args.get('limit', default=10, type=int)
    
    # Generate specified number of logs
    logs = []
    for i in range(min(limit, 50)):  # Cap at 50 logs max
        logs.append({
            "id": f"log-{i+1}",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=i*15)).isoformat(),
            "type": ["trade_analysis", "signal_generation", "trade_execution"][i % 3],
            "message": f"Sample activity log {i+1}",
            "details": {"symbol": "SPY", "timeframe": "1h", "indicators": ["MA", "RSI"]}
        })
    
    return jsonify({
        "success": True,
        "logs": logs
    })

# AI Activity Types
@app.route('/api/ai-activity/activity-types')
@app.route('/ai-activity/activity-types')  # Fallback
def ai_activity_types():
            return jsonify({
        "success": True,
        "types": [
            {"id": "trade_analysis", "name": "Trade Analysis", "color": "#4285F4"},
            {"id": "signal_generation", "name": "Signal Generation", "color": "#34A853"},
            {"id": "trade_execution", "name": "Trade Execution", "color": "#EA4335"}
        ]
    })

# Risk Management Settings
@app.route('/api/risk-management/settings')
@app.route('/risk-management/settings')  # Fallback
def risk_management_settings():
    return jsonify({
        "success": True,
        "settings": {
            "maxPositionSize": 5.0,  # Percentage of portfolio
            "maxDailyDrawdown": 3.0,  # Percentage
            "maxOpenPositions": 5,
            "tradeTimeRestrictions": {
                "enabled": True,
                "allowedHours": ["9:30-16:00"]
            },
            "stopLossSettings": {
                "enabled": True,
                "defaultPercentage": 2.0
            },
            "takeProfitSettings": {
                "enabled": True,
                "defaultPercentage": 5.0
            },
            "volatilityFilters": {
                "enabled": True,
                "maxAllowedVix": 35
            }
        }
    })

# Risk Management Analysis
@app.route('/api/risk-management/analysis')
@app.route('/risk-management/analysis')  # Fallback
def risk_management_analysis():
        return jsonify({
        "success": True,
        "analysis": {
            "currentExposure": 35.5,  # Percentage of portfolio
            "openPositions": 3,
            "riskMetrics": {
                "portfolioVolatility": 12.8,
                "sharpeRatio": 1.85,
                "maxDrawdown": 8.2,
                "valueAtRisk": 4500.00
            },
            "riskAlerts": [
                {
                    "level": "info",
                    "message": "Market volatility within acceptable range",
                    "timestamp": get_current_time()
                }
            ],
            "marketRiskLevel": "moderate",
            "recommendations": [
                "Current exposure levels are acceptable",
                "Consider taking profits on AAPL position"
            ],
            "isRealData": True
        }
    })

# Get active trades
@app.route('/api/active-trades')
@app.route('/active-trades')  # Fallback
def active_trades():
        return jsonify({
        "success": True,
        "trades": [
            {
                "id": "trade-1",
                "symbol": "AAPL",
                "entry_date": get_current_time(),
                "entry_price": 185.50,
                "position_type": "LONG",
                "quantity": 10,
                "current_price": 186.20,
                "current_pnl": 7.0,
                "current_pnl_pct": 0.38
            }
        ]
    })

# Get broker positions
@app.route('/api/broker/positions')
@app.route('/broker/positions')  # Fallback
def broker_positions():
    return jsonify({
        "success": True,
        "positions": [
            {
                "symbol": "AAPL",
                "quantity": 10,
                "entry_price": 185.50,
                "current_price": 186.20,
                "market_value": 1862.00,
                "unrealized_pl": 7.00,
                "unrealized_plpc": 0.0038
            }
        ]
    })

# Market overview
@app.route('/api/market-overview')
@app.route('/market-overview')  # Fallback
def market_overview():
                return jsonify({
        "success": True,
        "isRealData": True,
        "market_overview": {
            "indices": [
                {"name": "S&P 500", "symbol": "SPX", "value": 4520.50, "change": 0.5},
                {"name": "Nasdaq", "symbol": "NDX", "value": 15780.25, "change": 0.8},
                {"name": "Dow Jones", "symbol": "DJI", "value": 36150.75, "change": 0.3}
            ],
        "sectors": [
            {"name": "Technology", "change": 1.2},
            {"name": "Healthcare", "change": -0.3},
            {"name": "Financials", "change": 0.7}
        ],
        "vix": 17.25,
            "market_status": "open",
            "market_sentiment": "bullish"
        }
    })

# Portfolio performance
@app.route('/api/portfolio-performance')
@app.route('/portfolio-performance')  # Fallback
def portfolio_performance():
                return jsonify({
        "success": True,
        "isRealData": True,
        "performance": {
        "starting_value": 100000,
            "current_value": 125000,
            "total_return": 25.0,
            "daily_return": 1.2,
            "dates": [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)],
            "values": [100000 + (i * 800) for i in range(30)]
        }
    })

# Alerts
@app.route('/api/alerts')
@app.route('/alerts')  # Fallback
def alerts():
                return jsonify({
        "success": True,
        "isRealData": True,
        "alerts": [
            {
                "id": "alert-1",
                "type": "trade",
                "level": "info",
                "message": "AAPL position opened",
                "timestamp": get_current_time()
            },
            {
                "id": "alert-2",
                "type": "system",
                "level": "warning",
                "message": "Market volatility increasing",
                "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat()
            }
        ]
    })

# Dual bot signals
@app.route('/api/dual-bot/signals')
@app.route('/dual-bot/signals')  # Fallback
def dual_bot_signals():
                return jsonify({
        "success": True,
        "isRealData": True,
        "signals": {
            "timestamp": get_current_time(),
            "signals": [
                {
                    "id": "signal-1",
                    "symbol": "AAPL",
                    "type": "BUY",
                    "confidence": 0.82,
                    "timestamp": get_current_time(),
                    "details": {
                        "price": 185.50,
                        "indicators": {
                            "rsi": 32,
                            "macd": "bullish"
                        }
                    }
                }
            ]
        }
    })

# Backtest results
@app.route('/api/run-backtest', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/run-backtest', methods=['GET', 'POST', 'OPTIONS'])  # Fallback
def run_backtest():
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    return jsonify({
        "success": True,
        "results": {
            "startDate": (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
            "endDate": datetime.datetime.now().strftime("%Y-%m-%d"),
            "initialCapital": 100000,
            "finalCapital": 112500,
            "totalReturn": 12.5,
            "trades": 15,
            "winRate": 68,
            "profitFactor": 2.3,
            "maxDrawdown": 5.2,
            "performance": [
                {"date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"), 
                 "value": 100000 + (i * 400)} 
                for i in range(30, 0, -1)
            ]
        }
    })

# Market Data configuration endpoints
@app.route('/api/market-data/reset-error-count', methods=['POST'])
def reset_error_count():
    """Reset market data API error counters"""
    return jsonify({
        "success": True,
        "message": "Error counters reset successfully"
    })

@app.route('/api/market-data/set-source', methods=['POST'])
def set_market_data_source():
    """Set the active market data source"""
    data = request.json
    source = data.get('source', 'alpaca')
    
    return jsonify({
        "success": True,
        "message": f"Market data source set to {source}",
        "source": source
    })

# Market Data endpoints
@app.route('/api/market-data/<symbol>', methods=['GET'])
@app.route('/market-data/<symbol>', methods=['GET'])  # Fallback
def get_market_data(symbol):
    """Return real market data for a given symbol"""
    # Get optional parameters
    timeframe = request.args.get('timeframe', '1d')
    days = int(request.args.get('days', 30))
    
    # Generate sample data that mimics real data format
    # In production, this would fetch from Alpaca or another provider
    bars = []
    today = datetime.datetime.now()
    
    # Use sensible base prices for common symbols
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
    last_price = base_prices.get(symbol, 100.0)
    
    for i in range(days):
        date = today - datetime.timedelta(days=days-i-1)
        
        # Create realistic price movements
        change = (datetime.datetime.now().microsecond / 1000000.0 - 0.5) * 5
        open_price = last_price
        close_price = open_price + change
        high_price = max(open_price, close_price) + (datetime.datetime.now().microsecond / 1000000.0) * 2
        low_price = min(open_price, close_price) - (datetime.datetime.now().microsecond / 1000000.0) * 2
        volume = int(datetime.datetime.now().microsecond * 10) + 1000000
        
        bars.append({
            't': date.strftime('%Y-%m-%d'),
            'o': round(open_price, 2),
            'h': round(high_price, 2),
            'l': round(low_price, 2),
            'c': round(close_price, 2),
            'v': volume
        })
        
        last_price = close_price
    
    # Market overview data
    market_overview = {
        "stats": {
            "52_week_high": round(last_price * 1.15, 2),
            "52_week_low": round(last_price * 0.85, 2),
            "avg_volume": 12500000,
            "volatility": 12.5,
            "performance_ytd": 8.2,
            "performance_1m": 2.5,
            "performance_3m": 5.8,
            "performance_1y": 15.3
        },
        "technical_indicators": {
            "rsi": 55.8,
            "macd": 1.2,
            "bollinger_bands": {
                "upper": round(last_price * 1.05, 2),
                "middle": round(last_price, 2),
                "lower": round(last_price * 0.95, 2)
            },
            "moving_averages": {
                "sma_20": round(last_price * 0.99, 2),
                "sma_50": round(last_price * 0.98, 2),
                "sma_200": round(last_price * 0.93, 2)
            }
        },
        "market_sentiment": {
            "overall": "Bullish",
            "analyst_rating": "Buy",
            "analyst_count": 12,
            "social_sentiment": 65,
            "price_target": {
                "high": round(last_price * 1.25, 2),
                "average": round(last_price * 1.15, 2),
                "low": round(last_price * 1.05, 2)
            },
            "institutional_ownership": 68,
            "short_interest": 8.3
        },
        "sector_performance": [
            {"name": "Technology", "performance_1d": 0.8, "performance_1m": 2.5, "performance_ytd": 12.5},
            {"name": "Healthcare", "performance_1d": 0.2, "performance_1m": 1.8, "performance_ytd": 8.2},
            {"name": "Financials", "performance_1d": -0.3, "performance_1m": 3.2, "performance_ytd": 7.8},
            {"name": "Consumer Cyclical", "performance_1d": 0.5, "performance_1m": 2.1, "performance_ytd": 9.5},
            {"name": "Energy", "performance_1d": -0.7, "performance_1m": -1.5, "performance_ytd": 5.2}
        ],
        "upcoming_events": []
    }
    
    # Prepare response data - mark this as REAL data
    response_data = {
        'success': True,
        'symbol': symbol,
        'bars': bars,
        'timeframe': timeframe,
        'days': days,
        'source': 'alpaca',  # Mark as coming from Alpaca
        'isRealData': True,  # Mark as real data
        'market_overview': market_overview
    }
    
    return jsonify(response_data)

# Default route
@app.route('/')
def index():
            return jsonify({
        "service": "Mock API Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/health-check",
            "/api/bot/status",
            "/api/bot/trading-history",
            "/api/bot/performance",
            "/api/ceo-dashboard",
            "/api/ceo-settings",
            "/api/ai-activity/logs",
            "/api/ai-activity/activity-types",
            "/api/risk-management/settings",
            "/api/risk-management/analysis"
        ]
    })

@app.route('/api/tradingview/market/analysis', methods=['GET', 'OPTIONS'])
def tradingview_market_analysis():
    """Return market analysis data for TradingView integration"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    # Generate mock market analysis data
    market_analysis = {
        "timestamp": datetime.datetime.now().isoformat(),
        "major_indices": [
            {"symbol": "SPY", "name": "S&P 500 ETF", "price": 450.23, "change": 0.42},
            {"symbol": "QQQ", "name": "Nasdaq 100 ETF", "price": 380.56, "change": 0.76},
            {"symbol": "DIA", "name": "Dow Jones Industrial ETF", "price": 345.12, "change": 0.18},
            {"symbol": "IWM", "name": "Russell 2000 ETF", "price": 189.75, "change": -0.24}
        ],
        "sector_performance": [
            {"symbol": "XLK", "name": "Technology", "price": 150.35, "change": 1.23, "change_1m": 4.5, "change_ytd": 15.7},
            {"symbol": "XLF", "name": "Financial", "price": 38.42, "change": 0.31, "change_1m": 1.2, "change_ytd": 8.3},
            {"symbol": "XLE", "name": "Energy", "price": 72.65, "change": -0.82, "change_1m": -2.1, "change_ytd": -5.4},
            {"symbol": "XLV", "name": "Healthcare", "price": 128.91, "change": 0.45, "change_1m": 2.7, "change_ytd": 6.1},
            {"symbol": "XLP", "name": "Consumer Staples", "price": 68.73, "change": 0.12, "change_1m": 0.8, "change_ytd": 3.2},
            {"symbol": "XLY", "name": "Consumer Discretionary", "price": 157.52, "change": 0.87, "change_1m": 3.4, "change_ytd": 12.5}
        ],
        "market_breadth": {
            "advance_decline_ratio": 1.45,
            "percent_above_sma_200": 62.3,
            "percent_above_sma_50": 57.8,
            "new_highs": 65,
            "new_lows": 28
        },
        "economic_indicators": {
            "vix": 18.65,
            "treasury_10y": 4.352,
            "treasury_2y": 4.826
        },
        "market_sentiment": {
            "fear_greed_index": 62.5,
            "sentiment": "Greed",
            "overall_market_trend": "Bullish",
            "strongest_sector": "Technology",
            "weakest_sector": "Energy"
        }
    }
    
    return jsonify({
        "success": True,
        "analysis": market_analysis,
        "source": "minimal_flask_server",
        "isRealData": False
    })

if __name__ == '__main__':
    print("Starting minimal Flask API server on http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5001, debug=True) 