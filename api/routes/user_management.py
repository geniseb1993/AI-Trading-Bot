from flask import Blueprint, jsonify, request
from datetime import datetime
import json
import os
import uuid

# Create blueprint
user_bp = Blueprint('user', __name__)

# Mock user database (would be replaced with a real DB in production)
mock_users = {
    "1": {
        "id": "1",
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "created_at": "2023-01-01T00:00:00Z"
    },
    "2": {
        "id": "2",
        "username": "trader1",
        "email": "trader1@example.com",
        "role": "user",
        "created_at": "2023-01-02T00:00:00Z"
    }
}

# Routes for user management
@user_bp.route('/login', methods=['POST'])
def login():
    """Login a user and return an authentication token"""
    data = request.json
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'error': 'Username and password are required'
        }), 400
    
    # Mock authentication (would validate against DB in production)
    if data['username'] in [user['username'] for user in mock_users.values()]:
        # Generate mock token
        token = str(uuid.uuid4())
        return jsonify({
            'success': True,
            'token': token,
            'user': next(user for user in mock_users.values() if user['username'] == data['username'])
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Invalid credentials'
        }), 401

@user_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'error': 'Username, email, and password are required'
        }), 400
    
    # Check if username is already taken
    if data['username'] in [user['username'] for user in mock_users.values()]:
        return jsonify({
            'success': False,
            'error': 'Username already exists'
        }), 400
    
    # Create new user
    user_id = str(len(mock_users) + 1)
    new_user = {
        'id': user_id,
        'username': data['username'],
        'email': data['email'],
        'role': 'user',
        'created_at': datetime.now().isoformat()
    }
    
    # Add to mock database
    mock_users[user_id] = new_user
    
    return jsonify({
        'success': True,
        'user': new_user
    })

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get the user's profile"""
    # In a real app, this would extract user ID from the authenticated request
    # For now, just return a mock user
    return jsonify({
        'success': True,
        'profile': mock_users["2"]
    })

@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update the user's profile"""
    data = request.json
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided'
        }), 400
    
    # In a real app, this would extract user ID from the authenticated request
    # and update the DB record
    user_id = "2"  # Mock user ID
    
    # Update fields
    for field in ['username', 'email']:
        if field in data:
            mock_users[user_id][field] = data[field]
    
    return jsonify({
        'success': True,
        'profile': mock_users[user_id]
    }) 