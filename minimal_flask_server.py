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
    CORS(app)

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

# Bot Status
@app.route('/api/bot/status')
@app.route('/bot/status')  # Fallback
def bot_status():
    return jsonify({
        "autonomous_bot": {
            "status": False,
            "last_update": get_current_time(),
            "active_trades": []
        },
        "rsi_bot": {
            "status": False,
            "last_update": get_current_time(),
            "active_signals": []
        },
        "dual_bot": {
            "status": False,
            "last_update": get_current_time(),
            "active_positions": []
        }
    })

# Bot Actions
@app.route('/api/bot/start/<bot_type>', methods=['POST'])
@app.route('/bot/start/<bot_type>', methods=['POST'])  # Fallback
def start_bot(bot_type):
    return jsonify({
        "success": True,
        "message": f"{bot_type} bot started successfully",
        "status": "running"
    })

@app.route('/api/bot/stop/<bot_type>', methods=['POST'])
@app.route('/bot/stop/<bot_type>', methods=['POST'])  # Fallback
def stop_bot(bot_type):
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
    return jsonify({
        "success": True,
        "data": {
            "botStatus": [
                {
                    "id": "autonomous-bot",
                    "name": "Autonomous Trading Bot",
                    "status": "paused",
                    "lastTrade": get_current_time(),
                    "activeStrategies": 0,
                    "pnl24h": 2.1
                },
                {
                    "id": "rsi-bot",
                    "name": "RSI Strategy Bot",
                    "status": "paused",
                    "lastTrade": get_current_time(),
                    "activeStrategies": 0,
                    "pnl24h": 1.5
                },
                {
                    "id": "dual-bot",
                    "name": "Dual Bot System",
                    "status": "paused",
                    "lastTrade": get_current_time(),
                    "activeStrategies": 0,
                    "pnl24h": 3.2
                }
            ],
            "activeTrades": [],
            "marketOverview": {
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
        "performance": {
            "dailyPnL": 3.2,
            "weeklyPnL": 8.5,
            "monthlyPnL": 12.7,
            "winRate": 68,
            "totalTrades": 25,
            "avgWin": 5.2,
            "avgLoss": -1.8
        },
        "riskStatus": {
            "currentExposure": 35,
            "maxExposure": 80,
            "marketCondition": "Bullish",
            "volatilityLevel": "Moderate",
            "riskLevel": "Moderate",
            "controls": {
                "autoTrading": True,
                "odteOnly": True
            }
        },
        "tradeSetups": [
            {
                "id": "setup_1",
                "symbol": "SPX",
                "type": "CALL",
                "strategy": "0DTE Momentum",
                "price": 4520.50,
                "confidence": 0.87,
                "recommendation": "BUY SPX CALL @ 4525",
                "expiration": "0DTE",
                "timestamp": get_current_time()
            }
        ],
        "systemHealth": {
            "components": {
                "dataFetcher": {"status": "operational", "latency": 120},
                "signalGenerator": {"status": "operational", "latency": 450}
            },
            "lastUpdated": get_current_time()
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
            ]
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
        "status": "open",
        "indices": {
            "SPY": {"price": 502.45, "change": 0.75},
            "QQQ": {"price": 432.20, "change": 1.2},
            "IWM": {"price": 201.30, "change": -0.2}
        },
        "sectors": [
            {"name": "Technology", "change": 1.2},
            {"name": "Healthcare", "change": -0.3},
            {"name": "Financials", "change": 0.7}
        ],
        "vix": 17.25,
        "market_breadth": {
            "advancers": 320,
            "decliners": 180
        }
    })

# Portfolio performance
@app.route('/api/portfolio-performance')
@app.route('/portfolio-performance')  # Fallback
def portfolio_performance():
                return jsonify({
        "success": True,
        "portfolio_value": 125000,
        "starting_value": 100000,
        "total_return": 25000,
        "total_return_pct": 25,
        "daily_return": 850,
        "daily_return_pct": 0.7,
        "performance_chart": [
            {"date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"), 
             "value": 100000 + (i * 800)} 
            for i in range(30, 0, -1)
        ]
    })

# Alerts
@app.route('/api/alerts')
@app.route('/alerts')  # Fallback
def alerts():
                return jsonify({
        "success": True,
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

if __name__ == '__main__':
    print("Starting minimal Flask API server on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5000, debug=True) 