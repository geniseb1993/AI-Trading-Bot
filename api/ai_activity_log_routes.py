"""
AI Activity Log API Routes
"""

from flask import Blueprint, jsonify, request
import logging
import os
import json
from datetime import datetime
import time
import threading

logger = logging.getLogger(__name__)

# In-memory storage for activity logs
activity_logs = []
active_types = ["bot_start", "bot_stop", "trading_cycle", "market_analysis", 
                "signal_generation", "risk_adjustment", "trade_entry", "trade_exit"]

def register_routes(app):
    """
    Register AI activity log routes with the Flask app
    
    Args:
        app: Flask application instance
    """
    ai_log_bp = Blueprint('ai_activity_log', __name__, url_prefix='/api/ai-activity')
    
    @ai_log_bp.route('/logs', methods=['GET'])
    def get_activity_logs():
        """Get AI activity logs"""
        try:
            # Optional filtering
            activity_type = request.args.get('type')
            limit = request.args.get('limit', type=int, default=100)
            
            # Apply filters
            filtered_logs = activity_logs
            if activity_type:
                filtered_logs = [log for log in filtered_logs if log.get('type') == activity_type]
                
            # Sort by timestamp (newest first) and limit
            sorted_logs = sorted(filtered_logs, key=lambda x: x.get('timestamp', ''), reverse=True)
            limited_logs = sorted_logs[:limit]
            
            return jsonify({
                'success': True,
                'activity_logs': limited_logs
            })
        except Exception as e:
            logger.error(f"Error getting activity logs: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @ai_log_bp.route('/logs', methods=['POST'])
    def add_activity_log():
        """Add a new activity log"""
        try:
            data = request.json
            
            # Validate required fields
            if not data.get('type') or not data.get('message'):
                return jsonify({
                    'success': False,
                    'error': 'Activity type and message are required'
                }), 400
                
            # Create log entry
            log_entry = {
                'id': str(int(time.time() * 1000)),  # Timestamp as ID
                'type': data.get('type'),
                'message': data.get('message'),
                'details': data.get('details', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to in-memory storage
            activity_logs.append(log_entry)
            
            # Keep only the last 1000 logs
            if len(activity_logs) > 1000:
                activity_logs.pop(0)
                
            return jsonify({
                'success': True,
                'log_entry': log_entry
            })
        except Exception as e:
            logger.error(f"Error adding activity log: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @ai_log_bp.route('/types', methods=['GET'])
    def get_activity_types():
        """Get available activity types"""
        try:
            return jsonify({
                'success': True,
                'activity_types': active_types
            })
        except Exception as e:
            logger.error(f"Error getting activity types: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @ai_log_bp.route('/clear', methods=['POST'])
    def clear_activity_logs():
        """Clear all activity logs"""
        try:
            activity_logs.clear()
            return jsonify({
                'success': True,
                'message': 'All activity logs cleared'
            })
        except Exception as e:
            logger.error(f"Error clearing activity logs: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Register the blueprint
    app.register_blueprint(ai_log_bp)
    logger.info("Registered AI activity log routes") 