from flask import request, jsonify
from functools import wraps

# Mock token storage (would be a proper authentication system in production)
valid_tokens = set()

def setup_auth(app):
    """Setup authentication middleware for the Flask app"""
    @app.before_request
    def authenticate_request():
        # Skip authentication for certain routes
        if request.path in ['/api/user/login', '/api/user/register', '/'] or request.path.startswith('/api/test'):
            return None
            
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            # Allow the request to proceed for now, would reject in production
            return None
            
        token = auth_header.split(' ')[1]
        
        # Validate the token
        if token not in valid_tokens:
            # Allow the request to proceed for now, would reject in production
            return None
            
        # Token is valid, attach user info to the request
        # This would typically extract user details from the token or a database
        return None

def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
            
        token = auth_header.split(' ')[1]
        
        # Validate the token
        if token not in valid_tokens:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
            
        # Token is valid, proceed with the route
        return f(*args, **kwargs)
    return decorated

def register_token(token):
    """Register a valid token"""
    valid_tokens.add(token)
    
def invalidate_token(token):
    """Invalidate a token"""
    if token in valid_tokens:
        valid_tokens.remove(token) 