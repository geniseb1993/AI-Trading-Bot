"""
AI Activity Log Routes

API endpoints for managing AI activity logs
"""

import logging
from flask import Blueprint, jsonify, request
from api.ai_activity_log import get_activity_logger, ActivityType

logger = logging.getLogger(__name__)

# Create Flask Blueprint
ai_activity_bp = Blueprint('ai_activity_log', __name__, url_prefix='/api/ai-activity')

@ai_activity_bp.route('/logs', methods=['GET'])
def get_activity_logs():
    """
    Get AI activity logs with optional filtering
    
    Query parameters:
    - limit: Maximum number of logs to return (default: 100)
    - type: Filter by activity type
    - symbol: Filter by trading symbol
    - source: Filter by source
    - start_time: Filter logs after this ISO timestamp
    - end_time: Filter logs before this ISO timestamp
    
    Returns:
        JSON response with filtered logs
    """
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        activity_type = request.args.get('type')
        symbol = request.args.get('symbol')
        source = request.args.get('source')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        # Validate activity type
        if activity_type and not any(activity_type == t.value for t in ActivityType):
            return jsonify({
                'success': False,
                'error': f'Invalid activity type: {activity_type}'
            }), 400
        
        # Get activity logger
        activity_logger = get_activity_logger()
        
        # Get filtered logs
        logs = activity_logger.get_logs(
            limit=limit,
            activity_type=activity_type,
            symbol=symbol,
            source=source,
            start_time=start_time,
            end_time=end_time
        )
        
        return jsonify({
            'success': True,
            'logs': logs,
            'count': len(logs)
        })
        
    except Exception as e:
        logger.error(f"Error getting activity logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_activity_bp.route('/log', methods=['POST'])
def add_activity_log():
    """
    Add a new activity log entry
    
    Request JSON:
    {
        "activity_type": "trade_entry",
        "description": "Description of the activity",
        "details": {...},  # Optional details
        "symbol": "AAPL",  # Optional symbol
        "source": "ai_trader"  # Optional source
    }
    
    Returns:
        JSON response with created log entry
    """
    try:
        # Get JSON data from request
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        activity_type = data.get('activity_type')
        description = data.get('description')
        
        if not activity_type:
            return jsonify({
                'success': False,
                'error': 'Activity type is required'
            }), 400
        
        if not description:
            return jsonify({
                'success': False,
                'error': 'Description is required'
            }), 400
        
        # Validate activity type
        if not any(activity_type == t.value for t in ActivityType):
            return jsonify({
                'success': False,
                'error': f'Invalid activity type: {activity_type}'
            }), 400
        
        # Get activity logger
        activity_logger = get_activity_logger()
        
        # Log activity
        log_entry = activity_logger.log_activity(
            activity_type=activity_type,
            description=description,
            details=data.get('details'),
            symbol=data.get('symbol'),
            source=data.get('source', 'ai_trader')
        )
        
        return jsonify({
            'success': True,
            'log_entry': log_entry
        })
        
    except Exception as e:
        logger.error(f"Error adding activity log: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_activity_bp.route('/activity-types', methods=['GET'])
def get_activity_types():
    """
    Get available activity types
    
    Returns:
        JSON response with activity types
    """
    try:
        activity_types = {t.name: t.value for t in ActivityType}
        
        return jsonify({
            'success': True,
            'activity_types': activity_types
        })
        
    except Exception as e:
        logger.error(f"Error getting activity types: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_activity_bp.route('/clear', methods=['POST'])
def clear_activity_logs():
    """
    Clear all activity logs
    
    Returns:
        JSON response with success status
    """
    try:
        # Get activity logger
        activity_logger = get_activity_logger()
        
        # Clear logs
        activity_logger.clear_logs()
        
        return jsonify({
            'success': True,
            'message': 'All activity logs cleared'
        })
        
    except Exception as e:
        logger.error(f"Error clearing activity logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_routes(app):
    """
    Register AI activity log routes with Flask application
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(ai_activity_bp)
    logger.info("Successfully registered AI activity log routes")
    return True 