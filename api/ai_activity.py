import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from flask import Blueprint, jsonify, request, current_app
from pymongo import DESCENDING

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Blueprint
ai_activity_bp = Blueprint('ai_activity', __name__)

# Activity log schema
"""
{
    "id": "unique_id", # Generated UUID
    "timestamp": "ISO formatted timestamp",
    "activity_type": "TRADE_ENTRY|TRADE_EXIT|SIGNAL_GENERATED|STRATEGY_UPDATED|RISK_ALERT|SYSTEM_EVENT|ERROR",
    "description": "Human readable description of the activity",
    "symbol": "Stock symbol if applicable",
    "source": "ai_trader|auto_trader|strategy_manager|risk_manager|system",
    "details": {
        # Arbitrary JSON object with activity-specific details
    }
}
"""

# Activity types
ACTIVITY_TYPES = [
    "TRADE_ENTRY",
    "TRADE_EXIT",
    "SIGNAL_GENERATED",
    "STRATEGY_UPDATED",
    "RISK_ALERT",
    "SYSTEM_EVENT",
    "ANALYSIS_COMPLETED",
    "BACKTEST_RESULT",
    "ERROR"
]

# Routes
@ai_activity_bp.route('/logs', methods=['GET'])
def get_logs():
    """Get AI activity logs with optional filtering"""
    try:
        # Get query parameters
        activity_type = request.args.get('type')
        symbol = request.args.get('symbol')
        source = request.args.get('source')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = int(request.args.get('limit', 50))
        
        # Build query
        query = {}
        if activity_type:
            query['activity_type'] = activity_type
        if symbol:
            query['symbol'] = symbol
        if source:
            query['source'] = source
        
        # Handle time range
        if start_time or end_time:
            time_query = {}
            if start_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    time_query['$gte'] = start_dt.isoformat()
                except ValueError:
                    logger.warning(f"Invalid start_time format: {start_time}")
            
            if end_time:
                try:
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    time_query['$lte'] = end_dt.isoformat()
                except ValueError:
                    logger.warning(f"Invalid end_time format: {end_time}")
            
            if time_query:
                query['timestamp'] = time_query
        
        # Get database reference
        db = current_app.mongo_client.ai_trading_bot
        
        # Query logs
        logs = list(db.ai_activity_logs.find(
            query,
            {'_id': 0}
        ).sort('timestamp', DESCENDING).limit(limit))
        
        return jsonify({
            'success': True,
            'logs': logs,
            'count': len(logs),
            'limit': limit
        })
    
    except Exception as e:
        logger.error(f"Error fetching AI activity logs: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'logs': []
        }), 500

@ai_activity_bp.route('/activity-types', methods=['GET'])
def get_activity_types():
    """Get available activity types"""
    return jsonify({
        'success': True,
        'activity_types': ACTIVITY_TYPES
    })

@ai_activity_bp.route('/log', methods=['POST'])
def log_activity():
    """Log a new AI activity"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['activity_type', 'description', 'source']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Ensure activity type is valid
        if data['activity_type'] not in ACTIVITY_TYPES:
            return jsonify({
                'success': False,
                'error': f'Invalid activity type: {data["activity_type"]}'
            }), 400
        
        # Add timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat()
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = str(int(time.time() * 1000))  # Simple timestamp-based ID
        
        # Insert into database
        db = current_app.mongo_client.ai_trading_bot
        result = db.ai_activity_logs.insert_one(data)
        
        return jsonify({
            'success': True,
            'id': data['id'],
            'inserted_id': str(result.inserted_id)
        })
    
    except Exception as e:
        logger.error(f"Error logging AI activity: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_activity_bp.route('/clear', methods=['POST'])
def clear_logs():
    """Clear all activity logs (development/testing only)"""
    try:
        # Check if this is a development environment
        if not current_app.config.get('DEVELOPMENT_MODE', False):
            return jsonify({
                'success': False,
                'error': 'This endpoint is only available in development mode'
            }), 403
        
        # Delete all logs
        db = current_app.mongo_client.ai_trading_bot
        result = db.ai_activity_logs.delete_many({})
        
        return jsonify({
            'success': True,
            'deleted_count': result.deleted_count
        })
    
    except Exception as e:
        logger.error(f"Error clearing AI activity logs: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_activity_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about activity logs"""
    try:
        db = current_app.mongo_client.ai_trading_bot
        
        # Get total count
        total_count = db.ai_activity_logs.count_documents({})
        
        # Get counts by activity type
        type_counts = {}
        for activity_type in ACTIVITY_TYPES:
            count = db.ai_activity_logs.count_documents({'activity_type': activity_type})
            type_counts[activity_type] = count
        
        # Get counts by source
        pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        source_counts = list(db.ai_activity_logs.aggregate(pipeline))
        
        # Get recent activity
        recent = list(db.ai_activity_logs.find(
            {},
            {'_id': 0}
        ).sort('timestamp', DESCENDING).limit(5))
        
        return jsonify({
            'success': True,
            'total_count': total_count,
            'by_type': type_counts,
            'by_source': source_counts,
            'recent': recent
        })
    
    except Exception as e:
        logger.error(f"Error getting AI activity stats: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Register blueprint function
def register_ai_activity_routes(app):
    try:
        app.register_blueprint(ai_activity_bp, url_prefix='/api/ai-activity')
        logger.info("✅ AI activity routes registered")
    except Exception as e:
        logger.error(f"❌ Error registering AI activity routes: {str(e)}", exc_info=True) 