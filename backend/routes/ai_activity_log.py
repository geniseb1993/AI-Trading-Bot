from flask import Blueprint, jsonify, request
import logging
import random
from datetime import datetime, timedelta
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint for AI activity logging
ai_activity_bp = Blueprint('ai_activity', __name__, url_prefix='/api/ai-activity')

# Define activity types
ACTIVITY_TYPES = [
    {
        'id': 'market_analysis',
        'name': 'Market Analysis',
        'description': 'AI analyzing market conditions and trends'
    },
    {
        'id': 'signal_generation',
        'name': 'Signal Generation',
        'description': 'AI generating trading signals based on analysis'
    },
    {
        'id': 'trade_execution',
        'name': 'Trade Execution',
        'description': 'AI executing trades based on signals'
    },
    {
        'id': 'risk_assessment',
        'name': 'Risk Assessment',
        'description': 'AI evaluating risk levels for potential trades'
    },
    {
        'id': 'portfolio_optimization',
        'name': 'Portfolio Optimization',
        'description': 'AI optimizing portfolio allocation'
    },
    {
        'id': 'anomaly_detection',
        'name': 'Anomaly Detection',
        'description': 'AI detecting unusual market behavior'
    },
    {
        'id': 'sentiment_analysis',
        'name': 'Sentiment Analysis',
        'description': 'AI analyzing market sentiment from news and social media'
    }
]

# Store AI activity logs
activity_logs = []

# Generate some initial activity logs
def generate_initial_logs(count=30):
    """Generate initial activity logs for demonstration"""
    logs = []
    current_time = datetime.now()
    
    for i in range(count):
        activity_type = random.choice(ACTIVITY_TYPES)
        log_time = current_time - timedelta(minutes=i*30)
        
        log = {
            'id': str(uuid.uuid4()),
            'timestamp': log_time.isoformat(),
            'activity_type': activity_type['id'],
            'activity_name': activity_type['name'],
            'status': random.choice(['completed', 'in_progress', 'failed']),
            'details': f"AI performed {activity_type['name']} operation"
        }
        
        # Add more specific details based on activity type
        if activity_type['id'] == 'market_analysis':
            log['symbols_analyzed'] = random.sample(['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META'], random.randint(3, 8))
            log['insights'] = [
                "Detected bullish trend in technology sector",
                "Market volatility indices show decreased fear"
            ] if random.random() > 0.3 else []
            
        elif activity_type['id'] == 'signal_generation':
            signals = []
            for _ in range(random.randint(0, 3)):
                symbol = random.choice(['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'])
                direction = random.choice(['buy', 'sell', 'hold'])
                confidence = round(random.uniform(0.6, 0.95), 2)
                signals.append({
                    'symbol': symbol,
                    'direction': direction,
                    'confidence': confidence
                })
            log['signals_generated'] = signals
            
        elif activity_type['id'] == 'risk_assessment':
            log['portfolio_risk'] = random.choice(['low', 'medium', 'high'])
            log['diversification_score'] = round(random.uniform(0.3, 0.9), 2)
            
        logs.append(log)
    
    return logs

# Initialize with some demo logs
activity_logs = generate_initial_logs()

@ai_activity_bp.route('/logs', methods=['GET'])
def get_activity_logs():
    """Get AI activity logs with optional filtering"""
    try:
        # Get query parameters
        limit = request.args.get('limit', default=50, type=int)
        activity_type = request.args.get('activity_type')
        status = request.args.get('status')
        
        # Filter logs
        filtered_logs = activity_logs
        
        if activity_type:
            filtered_logs = [log for log in filtered_logs if log['activity_type'] == activity_type]
            
        if status:
            filtered_logs = [log for log in filtered_logs if log['status'] == status]
        
        # Sort by timestamp (newest first)
        sorted_logs = sorted(filtered_logs, key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit
        limited_logs = sorted_logs[:limit]
        
        return jsonify({
            'success': True,
            'logs': limited_logs,
            'total': len(filtered_logs),
            'returned': len(limited_logs)
        })
    except Exception as e:
        logger.error(f"Error getting AI activity logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_activity_bp.route('/activity-types', methods=['GET'])
def get_activity_types():
    """Get all available AI activity types"""
    try:
        return jsonify({
            'success': True,
            'activity_types': ACTIVITY_TYPES
        })
    except Exception as e:
        logger.error(f"Error getting AI activity types: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_activity_bp.route('/add-log', methods=['POST'])
def add_activity_log():
    """Add a new AI activity log"""
    try:
        log_data = request.json
        
        # Validate required fields
        if not all(key in log_data for key in ['activity_type', 'status', 'details']):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Validate activity type
        if log_data['activity_type'] not in [at['id'] for at in ACTIVITY_TYPES]:
            return jsonify({
                'success': False,
                'error': f"Invalid activity type: {log_data['activity_type']}"
            }), 400
        
        # Add missing fields
        log_data['id'] = str(uuid.uuid4())
        log_data['timestamp'] = datetime.now().isoformat()
        
        # Add activity name based on type
        for activity_type in ACTIVITY_TYPES:
            if activity_type['id'] == log_data['activity_type']:
                log_data['activity_name'] = activity_type['name']
                break
        
        # Add to activity logs
        activity_logs.insert(0, log_data)  # Add to beginning to keep newest first
        
        return jsonify({
            'success': True,
            'log': log_data
        })
    except Exception as e:
        logger.error(f"Error adding AI activity log: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_activity_bp.route('/clear-logs', methods=['POST'])
def clear_activity_logs():
    """Clear all AI activity logs"""
    try:
        global activity_logs
        activity_logs = []
        
        return jsonify({
            'success': True,
            'message': 'All activity logs cleared'
        })
    except Exception as e:
        logger.error(f"Error clearing AI activity logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_routes(app):
    """Register all AI activity logging routes with the Flask app"""
    try:
        app.register_blueprint(ai_activity_bp)
        logger.info("AI activity logging routes registered")
        return True
    except Exception as e:
        logger.error(f"Failed to register AI activity logging routes: {str(e)}")
        return False 