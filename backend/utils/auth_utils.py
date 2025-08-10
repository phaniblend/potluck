"""
Authentication utilities for Potluck app
Handles JWT tokens, password hashing, and auth helpers
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict, Tuple

# Get secret key from environment or use default
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'potluck-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

class AuthUtils:
    """Authentication utility functions"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            password_hash.encode('utf-8')
        )
    
    @staticmethod
    def generate_token(user_id: int, user_type: str, email: str) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'user_type': user_type,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token has expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
    
    @staticmethod
    def extract_token_from_header() -> Optional[str]:
        """Extract token from Authorization header"""
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        return None
    
    @staticmethod
    def get_current_user() -> Optional[Dict]:
        """Get current user from JWT token"""
        token = AuthUtils.extract_token_from_header()
        
        if not token:
            return None
        
        payload = AuthUtils.decode_token(token)
        return payload
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number (US format)"""
        import re
        # Remove any non-digit characters
        digits = re.sub(r'\D', '', phone)
        # Check if it's 10 digits (US phone)
        return len(digits) == 10
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number to standard format"""
        import re
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        return phone


# Decorators for route protection
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = AuthUtils.extract_token_from_header()
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_data = AuthUtils.decode_token(token)
        
        if not user_data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user data to request context
        request.current_user = user_data
        return f(*args, **kwargs)
    
    return decorated_function


def role_required(*allowed_roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = AuthUtils.extract_token_from_header()
            
            if not token:
                return jsonify({'error': 'Authentication required'}), 401
            
            user_data = AuthUtils.decode_token(token)
            
            if not user_data:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            if user_data.get('user_type') not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            request.current_user = user_data
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def chef_required(f):
    """Decorator to require chef role"""
    return role_required('chef')(f)


def delivery_required(f):
    """Decorator to require delivery role"""
    return role_required('delivery')(f)


def consumer_required(f):
    """Decorator to require consumer role"""
    return role_required('consumer')(f)


def admin_required(f):
    """Decorator to require admin role"""
    return role_required('admin')(f)


# Session management utilities
class SessionManager:
    """Manage user sessions and active tokens"""
    
    # In production, use Redis or database for token blacklist
    _blacklisted_tokens = set()
    
    @classmethod
    def blacklist_token(cls, token: str):
        """Add token to blacklist (for logout)"""
        cls._blacklisted_tokens.add(token)
    
    @classmethod
    def is_token_blacklisted(cls, token: str) -> bool:
        """Check if token is blacklisted"""
        return token in cls._blacklisted_tokens
    
    @classmethod
    def create_session(cls, user_id: int, user_type: str, email: str) -> Dict:
        """Create new session for user"""
        token = AuthUtils.generate_token(user_id, user_type, email)
        
        return {
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'user_type': user_type
            },
            'expires_in': JWT_EXPIRATION_HOURS * 3600  # in seconds
        }
    
    @classmethod
    def validate_session(cls, token: str) -> Tuple[bool, Optional[Dict]]:
        """Validate session token"""
        if cls.is_token_blacklisted(token):
            return False, None
        
        user_data = AuthUtils.decode_token(token)
        if not user_data:
            return False, None
        
        return True, user_data
    
    @classmethod
    def end_session(cls, token: str):
        """End user session (logout)"""
        cls.blacklist_token(token)


# Password strength validator
def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, "Password is strong"


# OTP generation for phone verification (placeholder)
def generate_otp() -> str:
    """Generate 6-digit OTP for phone verification"""
    import random
    return str(random.randint(100000, 999999))


# Rate limiting helper (basic implementation)
class RateLimiter:
    """Basic rate limiting for API endpoints"""
    
    _attempts = {}  # In production, use Redis
    
    @classmethod
    def check_rate_limit(cls, identifier: str, max_attempts: int = 5, 
                         window_minutes: int = 15) -> bool:
        """
        Check if identifier has exceeded rate limit
        Returns True if within limit, False if exceeded
        """
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        if identifier not in cls._attempts:
            cls._attempts[identifier] = []
        
        # Clean old attempts
        cls._attempts[identifier] = [
            attempt for attempt in cls._attempts[identifier]
            if attempt > window_start
        ]
        
        # Check limit
        if len(cls._attempts[identifier]) >= max_attempts:
            return False
        
        # Record new attempt
        cls._attempts[identifier].append(now)
        return True