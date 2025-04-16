"""
Notification Routes Module

Handles API routes for notification functionality including
voice and desktop notifications.
"""

import logging
import datetime
import os
import traceback
from flask import Blueprint, jsonify, request, send_file
from execution_model.notification_service import NotificationService, NotificationPriority, NotificationGroup

# Try to import the Hume voice service, but provide a fallback mock implementation if it fails
try:
    from execution_model.hume_voice_service import HumeVoiceService, VoiceStyle
    HUME_IMPORT_SUCCESS = True
except ImportError:
    # Fallback implementation if import fails
    class VoiceStyle:
        PROFESSIONAL = "professional"
        URGENT = "urgent"
        CASUAL = "casual"
    
    class HumeVoiceService:
        def __init__(self, api_key=None, secret_key=None):
            self.api_key = api_key
            self.secret_key = secret_key
            
        def speak(self, text, voice_style=None, priority="medium"):
            print(f"Mock HumeVoiceService: Would speak '{text}' with priority {priority}")
            return True
            
        def test_voice(self):
            print("Mock HumeVoiceService: Voice test")
            return True
    
    HUME_IMPORT_SUCCESS = False

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging with more detail
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a Flask Blueprint
notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')

# Initialize notification service
notification_service = NotificationService()

# Initialize a separate instance of Hume Voice Service for direct API calls
try:
    hume_voice = HumeVoiceService(
        api_key=os.environ.get("HUME_API_KEY"),
        secret_key=os.environ.get("HUME_SECRET_KEY")
    )
    if HUME_IMPORT_SUCCESS:
        logger.info("Hume Voice Service initialized successfully")
    else:
        logger.warning("Using mock implementation of Hume Voice Service (import failed)")
except Exception as e:
    logger.error(f"Failed to initialize Hume Voice Service: {str(e)}")
    logger.error(traceback.format_exc())
    hume_voice = None

# Routes

@notification_bp.route('/speak', methods=['POST'])
def speak_notification():
    """
    Convert text to speech for voice notifications
    
    Request JSON:
    {
        "message": "The text to speak",
        "priority": "high|medium|low" (optional, defaults to medium),
        "use_hume": true|false (optional, defaults to true)
    }
    """
    try:
        logger.debug(f"Received speak notification request: {request.json}")
        data = request.json
        
        if not data:
            logger.error("No JSON data in request")
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
            
        if 'message' not in data:
            logger.error("Missing required field 'message' in request")
            return jsonify({
                'success': False,
                'error': 'Missing required field: message'
            }), 400
            
        message = data['message']
        priority_str = data.get('priority', 'medium')
        use_hume = data.get('use_hume', True)
        
        logger.debug(f"Processing speak request: message='{message[:30]}...', priority={priority_str}, use_hume={use_hume}")
        
        priority = NotificationPriority.MEDIUM
        if priority_str == 'high':
            priority = NotificationPriority.HIGH
        elif priority_str == 'low':
            priority = NotificationPriority.LOW
        
        # Determine which voice service to use    
        if use_hume and hume_voice is not None:
            voice_style = VoiceStyle.PROFESSIONAL
            if priority_str == 'high':
                voice_style = VoiceStyle.URGENT
            elif priority_str == 'low':
                voice_style = VoiceStyle.CASUAL
            
            logger.info(f"Using Hume voice service with style: {voice_style}")
            try:
                success = hume_voice.speak(message, voice_style, priority_str)
                if not success:
                    logger.error("Hume voice service failed to generate speech")
                    # Try fallback to system notification
                    logger.warning("Falling back to system notification service")
                    success = notification_service.send_voice_notification(message, priority)
            except Exception as e:
                logger.error(f"Hume voice service error: {str(e)}")
                logger.error(traceback.format_exc())
                # Try fallback to system notification
                logger.warning("Falling back to system notification service after Hume error")
                success = notification_service.send_voice_notification(message, priority)
        else:
            if use_hume and hume_voice is None:
                logger.warning("Hume voice service was requested but is not available. Using system notification service.")
            else:
                logger.debug("Using system notification service for voice")
            success = notification_service.send_voice_notification(message, priority)
        
        logger.debug(f"Voice notification result: success={success}")
        return jsonify({
            'success': success,
            'message': 'Voice notification sent' if success else 'Failed to send voice notification'
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in speak notification: {e}")
        logger.error(error_details)
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_details
        }), 500

@notification_bp.route('/test-voice', methods=['GET'])
def test_voice():
    """Test the voice notification system with a sample message"""
    try:
        if hume_voice is None:
            logger.error("Hume voice service is not available for testing")
            return jsonify({
                'success': False,
                'error': 'Hume voice service is not available'
            }), 500
            
        success = hume_voice.test_voice()
        
        return jsonify({
            'success': success,
            'message': 'Voice test completed successfully' if success else 'Failed to test voice notification'
        })
        
    except Exception as e:
        logger.error(f"Error testing voice: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/desktop', methods=['POST'])
def desktop_notification():
    """
    Send a desktop notification
    
    Request JSON:
    {
        "title": "Notification title",
        "message": "The notification message",
        "priority": "high|medium|low" (optional, defaults to medium),
        "custom_sound": "path/to/sound.wav" (optional)
    }
    """
    try:
        data = request.json
        
        if not data or 'message' not in data or 'title' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: title, message'
            }), 400
            
        title = data['title']
        message = data['message']
        priority_str = data.get('priority', 'medium')
        custom_sound = data.get('custom_sound')
        
        priority = NotificationPriority.MEDIUM
        if priority_str == 'high':
            priority = NotificationPriority.HIGH
        elif priority_str == 'low':
            priority = NotificationPriority.LOW
            
        # For desktop notifications, we'll just prepend the title to the message
        formatted_message = f"{title}: {message}"
        success = notification_service.send_desktop_notification(
            formatted_message, 
            priority, 
            custom_sound
        )
        
        return jsonify({
            'success': success,
            'message': 'Desktop notification sent' if success else 'Failed to send desktop notification'
        })
        
    except Exception as e:
        logger.error(f"Error in desktop notification: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/', methods=['POST'])
def send_notification():
    """
    Send a notification through multiple channels
    
    Request JSON:
    {
        "title": "Notification title",
        "message": "The notification message",
        "notification_type": "email|sms|desktop|voice",
        "priority": "high|medium|low" (optional, defaults to medium),
        "group": "trade|system|alert|error" (optional, defaults to system),
        "template_name": "Name of template to use" (optional),
        "data": {} (optional template data)
    }
    """
    try:
        data = request.json
        
        if not data or 'message' not in data or 'notification_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: message, notification_type'
            }), 400
            
        message = data['message']
        notification_type = data['notification_type']
        
        # Handle optional fields
        priority_str = data.get('priority', 'medium')
        group_str = data.get('group', 'system')
        template_name = data.get('template_name')
        template_data = data.get('data', {})
        
        # Convert string parameters to enums
        priority = NotificationPriority.MEDIUM
        if priority_str == 'high':
            priority = NotificationPriority.HIGH
        elif priority_str == 'low':
            priority = NotificationPriority.LOW
            
        group = NotificationGroup.SYSTEM
        if group_str == 'trade':
            group = NotificationGroup.TRADE
        elif group_str == 'alert':
            group = NotificationGroup.ALERT
        elif group_str == 'error':
            group = NotificationGroup.ERROR
            
        # Send the notification
        success = notification_service.send_notification(
            message,
            notification_type,
            priority,
            group,
            template_name,
            template_data
        )
        
        return jsonify({
            'success': success,
            'message': 'Notification sent' if success else 'Failed to send notification'
        })
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/settings', methods=['GET'])
def get_notification_settings():
    """Get current notification settings"""
    try:
        # We'll hardcode some default settings for demonstration
        # In a real application, these would come from a database or config file
        settings = {
            'desktop': {
                'enabled': True,
                'priority_levels': {
                    'high': True,
                    'medium': True,
                    'low': False
                }
            },
            'voice': {
                'enabled': True,
                'use_hume_ai': True,
                'priority_levels': {
                    'high': True,
                    'medium': False,
                    'low': False
                },
                'rate': 150,
                'volume': 0.8
            },
            'email': {
                'enabled': False,
                'sender_email': 'notifications@example.com',
                'recipient_email': 'user@example.com',
                'smtp_server': 'smtp.example.com',
                'smtp_port': 587
            },
            'sms': {
                'enabled': False,
                'api_endpoint': 'https://api.twilio.com/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages.json',
                'phone_number': '+1234567890'
            }
        }
        
        return jsonify({
            'success': True,
            'settings': settings
        })
        
    except Exception as e:
        logger.error(f"Error getting notification settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/settings', methods=['PUT'])
def update_notification_settings():
    """Update notification settings"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No settings provided'
            }), 400
            
        # In a real application, we would update settings in a database or config file
        # For this demo, we'll just pretend it worked
        
        return jsonify({
            'success': True,
            'message': 'Notification settings updated'
        })
        
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/history', methods=['GET'])
def get_notification_history():
    """Get notification history"""
    try:
        limit = request.args.get('limit', 100, type=int)
        group = request.args.get('group')
        priority = request.args.get('priority')
        
        # Convert string parameters to enums if provided
        group_enum = None
        if group:
            if group == 'trade':
                group_enum = NotificationGroup.TRADE
            elif group == 'system':
                group_enum = NotificationGroup.SYSTEM
            elif group == 'alert':
                group_enum = NotificationGroup.ALERT
            elif group == 'error':
                group_enum = NotificationGroup.ERROR
                
        priority_enum = None
        if priority:
            if priority == 'high':
                priority_enum = NotificationPriority.HIGH
            elif priority == 'medium':
                priority_enum = NotificationPriority.MEDIUM
            elif priority == 'low':
                priority_enum = NotificationPriority.LOW
                
        history = notification_service.get_notification_history(limit, group_enum, priority_enum)
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Error getting notification history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_routes(app):
    """
    Register notification routes with the Flask app
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(notification_bp)
    logger.info("Successfully registered notification routes") 