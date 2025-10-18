"""
Authentication middleware for Potluck
"""

from functools import wraps
from flask import request, jsonify
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auth_utils import AuthUtils


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        payload = AuthUtils.verify_token(token)
        
        if not payload:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Pass user_id to the route function
        return f(payload['user_id'], *args, **kwargs)
    
    return decorated_function


def require_role(required_role):
    """Decorator to require specific user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user_id, *args, **kwargs):
            # Get user from database to check role
            from config.database import DatabaseHelper
            
            user = DatabaseHelper.get_user_by_id(current_user_id)
            
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            if user['user_type'] != required_role:
                return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
            
            # Continue to the route function
            return f(current_user_id, *args, **kwargs)
        
        return decorated_function
    return decorator
