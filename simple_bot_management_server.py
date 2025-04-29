from flask import Flask, jsonify, request
import logging
from datetime import datetime, timedelta
import json
import os
import threading
import time
import random
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_management_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Frontend URL - explicitly allow this origin 
FRONTEND_URL = "http://localhost:3001"

# Enable CORS for all routes with a more robust implementation
CORS(app, resources={r"/*": {
    "origins": [FRONTEND_URL, "http://localhost:3000", "*"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# Add CORS headers to all responses as a backup
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

# Handle OPTIONS requests for CORS preflight
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = app.make_default_options_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight response for 1 hour
    return response

# In-memory storage for bot status
bot_status = {
    "autonomous_bot": {
        "status": "inactive",
        "last_active": (datetime.now() - timedelta(hours=4)).isoformat(),
        "trades_executed": 28,
        "success_rate": 0.75,
        "current_positions": 2,
        "error_count": 0,
        "uptime": "2d 4h 15m",
        "next_scan": (datetime.now() + timedelta(minutes=15)).isoformat(),
        "cpu_usage": 0.05,
        "memory_usage": 128.5
    },
    "rsi_bot": {
        "status": "inactive",
        "last_active": (datetime.now() - timedelta(minutes=30)).isoformat(),
        "trades_executed": 42,
        "success_rate": 0.82,
        "current_positions": 3,
        "error_count": 1,
        "uptime": "5d 12h 30m",
        "next_scan": (datetime.now() + timedelta(minutes=30)).isoformat(),
        "cpu_usage": 0.08,
        "memory_usage": 145.2
    },
    "dual_bot": {
        "status": "inactive",
        "last_active": (datetime.now() - timedelta(minutes=15)).isoformat(),
        "trades_executed": 36,
        "success_rate": 0.88,
        "current_positions": 4,
        "error_count": 0,
        "uptime": "3d 9h 45m",
        "next_scan": (datetime.now() + timedelta(minutes=45)).isoformat(),
        "cpu_usage": 0.12,
        "memory_usage": 186.7
    }
}

# Status file path for persistence
STATUS_FILE = "bot_status.json"

# Load status from file if it exists
def load_status():
    global bot_status
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                loaded_status = json.load(f)
                bot_status.update(loaded_status)
                logger.info(f"Loaded bot status from {STATUS_FILE}")
    except Exception as e:
        logger.error(f"Error loading bot status: {e}")

# Save status to file
def save_status():
    try:
        with open(STATUS_FILE, 'w') as f:
            json.dump(bot_status, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving bot status: {e}")

# Load status at startup
load_status()

# In-memory AI activity logs
ai_activity_logs = [
    {
        "id": f"log-{i:03d}",
        "timestamp": (datetime.now() - timedelta(minutes=i*15)).isoformat(),
        "activity_type": random.choice(["market_analysis", "trade_recommendation", "risk_assessment", "portfolio_optimization"]),
        "description": f"Sample AI activity log entry {i}",
        "model_used": random.choice(["GPT-4-turbo", "DeepSeek-8B", "Claude 3 Opus"]),
        "confidence": round(random.uniform(0.7, 0.95), 2),
        "execution_time": round(random.uniform(1.5, 5.0), 1),
        "tokens_used": random.randint(800, 3000)
    }
    for i in range(1, 51)  # Generate 50 sample log entries
]

# AI activity types definitions
ai_activity_types = [
    {
        "id": "act-001",
        "name": "market_analysis",
        "description": "Daily market sentiment and trend analysis",
        "average_execution_time": 3.5,
        "average_tokens": 1950
    },
    {
        "id": "act-002",
        "name": "trade_recommendation",
        "description": "Generation of trade ideas with entry/exit points",
        "average_execution_time": 2.8,
        "average_tokens": 1350
    },
    {
        "id": "act-003",
        "name": "risk_assessment",
        "description": "Evaluation of potential trades for risk factors",
        "average_execution_time": 3.0,
        "average_tokens": 1750
    },
    {
        "id": "act-004",
        "name": "portfolio_optimization",
        "description": "Analysis of current positions and optimization recommendations",
        "average_execution_time": 4.2,
        "average_tokens": 2250
    }
]

# In-memory trading history
trading_history = [
    {
        "id": f"trade-{i:03d}",
        "symbol": random.choice(["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]),
        "entry_price": round(random.uniform(100, 200), 2),
        "exit_price": round(random.uniform(100, 200), 2),
        "entry_date": (datetime.now() - timedelta(days=i*2, hours=random.randint(1, 8))).isoformat(),
        "exit_date": (datetime.now() - timedelta(days=i*2 - 1, hours=random.randint(1, 8))).isoformat(),
        "profit_loss": 0,  # Will be calculated below
        "profit_loss_percent": 0,  # Will be calculated below
        "trade_type": random.choice(["long", "short"]),
        "strategy": random.choice(["momentum_breakout", "trend_following", "mean_reversion", "ai_signal"]),
        "status": "closed",
        "risk_level": random.choice(["low", "medium", "high"]),
        "confidence_score": round(random.uniform(0.6, 0.95), 2),
        "bot_id": random.choice(["autonomous_bot", "rsi_bot", "dual_bot"])
    }
    for i in range(1, 31)  # Generate 30 sample trade history entries
]

# Calculate profit/loss for each trade
for trade in trading_history:
    if trade["trade_type"] == "long":
        trade["profit_loss"] = round(trade["exit_price"] - trade["entry_price"], 2)
    else:  # short
        trade["profit_loss"] = round(trade["entry_price"] - trade["exit_price"], 2)
    
    trade["profit_loss_percent"] = round((trade["profit_loss"] / trade["entry_price"]) * 100, 2)

# In-memory performance data
daily_performance = []
for i in range(30, 0, -1):  # Last 30 days
    day_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
    daily_performance.append({
        "date": day_date,
        "profit_loss": round(random.uniform(-10, 20), 2)
    })

performance_data = {
    "total_trades": len(trading_history),
    "winning_trades": sum(1 for trade in trading_history if trade["profit_loss"] > 0),
    "losing_trades": sum(1 for trade in trading_history if trade["profit_loss"] <= 0),
    "win_rate": 0,  # Will be calculated below
    "average_profit": round(sum(trade["profit_loss"] for trade in trading_history if trade["profit_loss"] > 0) / max(1, sum(1 for trade in trading_history if trade["profit_loss"] > 0)), 2),
    "average_loss": round(sum(trade["profit_loss"] for trade in trading_history if trade["profit_loss"] <= 0) / max(1, sum(1 for trade in trading_history if trade["profit_loss"] <= 0)), 2),
    "profit_factor": 0,  # Will be calculated below
    "total_profit": round(sum(trade["profit_loss"] for trade in trading_history), 2),
    "max_drawdown": round(min(0, min(perf["profit_loss"] for perf in daily_performance)), 2),
    "sharpe_ratio": round(random.uniform(0.8, 2.5), 2),
    "daily_performance": daily_performance
}

# Calculate win rate
performance_data["win_rate"] = round(performance_data["winning_trades"] / max(1, len(trading_history)), 3)

# Calculate profit factor
total_gains = sum(trade["profit_loss"] for trade in trading_history if trade["profit_loss"] > 0)
total_losses = abs(sum(trade["profit_loss"] for trade in trading_history if trade["profit_loss"] < 0))
performance_data["profit_factor"] = round(total_gains / max(0.01, total_losses), 2)  # Avoid division by zero

# API Routes

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# Bot status endpoint
@app.route('/api/bot/status', methods=['GET'])
def get_bot_status():
    logger.info("Bot status endpoint called")
    # Update last update time for all bots
    for bot in bot_status:
        bot_status[bot]['last_active'] = datetime.now().isoformat()
    
    # Return the bot_status directly without the extra 'status' nesting
    return jsonify({
        'success': True,
        'autonomous_bot': bot_status['autonomous_bot'],
        'rsi_bot': bot_status['rsi_bot'],
        'dual_bot': bot_status['dual_bot']
    })

# Standard status endpoint (for compatibility)
@app.route('/api/status', methods=['GET'])
def get_status():
    logger.info("Standard status endpoint called")
    return get_bot_status()

# Dual bot status endpoint (for compatibility)
@app.route('/api/dual-bot/status', methods=['GET'])
def get_dual_bot_status():
    logger.info("Dual bot status endpoint called")
    return get_bot_status()

# Start bot endpoint
@app.route('/api/bot/<bot_id>/start', methods=['POST'])
def start_bot(bot_id):
    if bot_id not in bot_status:
        return jsonify({'success': False, 'message': f'Bot {bot_id} not found'}), 404
    
    current_status = bot_status[bot_id]['status']
    
    # Only allow starting if the bot is paused or stopped
    if current_status not in ['paused', 'stopped', 'inactive']:
        return jsonify({'success': False, 'message': f'Bot {bot_id} is already running ({current_status})'}), 400
    
    # Update bot status
    bot_status[bot_id]['status'] = 'active'
    bot_status[bot_id]['last_active'] = datetime.now().isoformat()
    
    # Log the action
    logger.info(f"Bot {bot_id} started")
    
    # Save status to file
    save_status()
    
    return jsonify({
        'success': True, 
        'message': f'Bot {bot_id} started successfully',
        'data': bot_status[bot_id]
    })

# Stop bot endpoint
@app.route('/api/bot/<bot_id>/stop', methods=['POST'])
def stop_bot(bot_id):
    if bot_id not in bot_status:
        return jsonify({'success': False, 'message': f'Bot {bot_id} not found'}), 404
    
    current_status = bot_status[bot_id]['status']
    
    # Only allow stopping if the bot is active or in an error state
    if current_status not in ['active', 'error']:
        return jsonify({'success': False, 'message': f'Bot {bot_id} is already stopped or paused ({current_status})'}), 400
    
    # Update bot status
    bot_status[bot_id]['status'] = 'paused'
    
    # Log the action
    logger.info(f"Bot {bot_id} stopped")
    
    # Save status to file
    save_status()
    
    return jsonify({
        'success': True, 
        'message': f'Bot {bot_id} stopped successfully',
        'data': bot_status[bot_id]
    })

# AI activity logs endpoint
@app.route('/api/ai-activity/logs', methods=['GET'])
def get_ai_activity_logs():
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    activity_type = request.args.get('activity_type')
    logger.info(f"AI activity logs endpoint called, limit={limit}, offset={offset}, type={activity_type}")
    
    # Filter logs if activity_type is provided
    filtered_logs = ai_activity_logs
    if activity_type:
        filtered_logs = [log for log in ai_activity_logs if log['activity_type'] == activity_type]
    
    # Apply pagination
    paginated_logs = filtered_logs[offset:offset+limit]
    
    return jsonify({
        'success': True,
        'data': paginated_logs,
        'total': len(filtered_logs)
    })

# AI activity types endpoint
@app.route('/api/ai-activity/activity-types', methods=['GET'])
def get_ai_activity_types():
    logger.info("AI activity types endpoint called")
    
    return jsonify({
        'success': True,
        'data': ai_activity_types
    })

# Trading history endpoint
@app.route('/api/bot/trading-history', methods=['GET'])
def get_trading_history():
    limit = int(request.args.get('limit', 30))
    offset = int(request.args.get('offset', 0))
    bot_id = request.args.get('bot_id')
    strategy = request.args.get('strategy')
    trade_type = request.args.get('trade_type')
    
    logger.info(f"Trading history endpoint called, limit={limit}, offset={offset}, bot_id={bot_id}, strategy={strategy}, type={trade_type}")
    
    # Filter history based on query parameters
    filtered_history = trading_history
    
    if bot_id:
        filtered_history = [trade for trade in filtered_history if trade['bot_id'] == bot_id]
    
    if strategy:
        filtered_history = [trade for trade in filtered_history if trade['strategy'] == strategy]
    
    if trade_type:
        filtered_history = [trade for trade in filtered_history if trade['trade_type'] == trade_type]
    
    # Sort by date (most recent first)
    filtered_history.sort(key=lambda x: x['entry_date'], reverse=True)
    
    # Apply pagination
    paginated_history = filtered_history[offset:offset+limit]
    
    # Format to match frontend expectations
    return jsonify({
        'success': True,
        'trades': paginated_history,
        'total': len(filtered_history)
    })

# Performance data endpoint
@app.route('/api/bot/performance', methods=['GET'])
def get_performance_data():
    bot_id = request.args.get('bot_id')
    time_range = request.args.get('time_range', 'all')
    
    logger.info(f"Performance data endpoint called, bot_id={bot_id}, time_range={time_range}")
    
    # For simplicity, we'll ignore the filters in this example
    # In a real implementation, you would filter the data based on bot_id and time_range
    
    return jsonify({
        'success': True,
        'data': performance_data
    })

# Automatic status updates in the background
def update_bots_status():
    while True:
        try:
            # Update the last_update time for all bots
            current_time = datetime.now().isoformat()
            for bot in bot_status:
                bot_status[bot]['last_active'] = current_time
            
            # Save status periodically
            save_status()
            
            # Sleep for 30 seconds
            time.sleep(30)
        except Exception as e:
            logger.error(f"Error in background task: {e}")
            time.sleep(60)  # If there's an error, wait longer before trying again

# Start background task for status updates
status_thread = threading.Thread(target=update_bots_status, daemon=True)
status_thread.start()

# Main entry point
if __name__ == '__main__':
    # Ensure we have the status file directory
    os.makedirs(os.path.dirname(STATUS_FILE) if os.path.dirname(STATUS_FILE) else '.', exist_ok=True)
    
    port = 5002  # Use a different port from the main server
    logger.info(f"Starting bot management server on port {port}")
    print(f"Bot Management API running at http://localhost:{port}")
    print(f"Status endpoint: http://localhost:{port}/api/bot/status")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True) 