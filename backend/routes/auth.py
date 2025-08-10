"""
Authentication routes for Potluck app
Handles signup, login, logout
"""

from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import DatabaseHelper, DatabaseConnection
from utils.auth_utils import AuthUtils, SessionManager, validate_password_strength
from utils.location import location_service

bp = Blueprint('auth', __name__)

@bp.route('/signup', methods=['POST'])
def signup():
    """Register new user"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['email', 'password', 'full_name', 'phone', 'user_type', 'zip_code']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Validate user type
        if data['user_type'] not in ['consumer', 'chef', 'delivery']:
            return jsonify({'success': False, 'error': 'Invalid user type'}), 400
        
        # Validate zip code and get location info
        zip_code = data.get('zip_code', '').strip()
        location_info = location_service.get_local_market_info(zip_code)
        
        if not location_info.get('coordinates'):
            return jsonify({
                'success': False, 
                'error': 'Service not available in your area yet. We currently serve Dallas, Mumbai, and Mexico City areas.'
            }), 400
        
        # Validate email format
        if not AuthUtils.validate_email(data['email']):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Check if user exists
        existing_user = DatabaseHelper.get_user_by_email(data['email'])
        if existing_user:
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
        
        # Validate password strength
        is_valid, msg = validate_password_strength(data['password'])
        if not is_valid:
            return jsonify({'success': False, 'error': msg}), 400
        
        # Hash password
        password_hash = AuthUtils.hash_password(data['password'])
        
        # Create user with location data
        user_data = {
            'email': data['email'],
            'password_hash': password_hash,
            'full_name': data['full_name'],
            'phone': AuthUtils.format_phone(data['phone']),
            'user_type': data['user_type'],
            'zip_code': zip_code,
            'city': location_info['city'],
            'state': location_info['state'],
            'latitude': location_info['coordinates']['latitude'],
            'longitude': location_info['coordinates']['longitude']
        }
        
        # Add address if provided
        if data.get('address'):
            user_data['address'] = data['address']
        
        # Set delivery radius for delivery agents
        if data['user_type'] == 'delivery':
            user_data['delivery_radius'] = 3  # 3km default for bicycle delivery
        
        user_id = DatabaseHelper.create_user(user_data)
        
        # Create session
        session = SessionManager.create_session(user_id, data['user_type'], data['email'])
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                **session,
                'location': location_info['location']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        # Get user
        user = DatabaseHelper.get_user_by_email(data['email'])
        if not user:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not AuthUtils.verify_password(data['password'], user['password_hash']):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Check if user is active
        if not user['is_active']:
            return jsonify({'success': False, 'error': 'Account is deactivated'}), 403
        
        # Create session
        session = SessionManager.create_session(
            user['id'], 
            user['user_type'], 
            user['email']
        )
        
        # Get user stats
        stats = DatabaseHelper.get_user_stats(user['id'], user['user_type'])
        
        # Format location
        location = f"{user.get('city', '')}, {user.get('state', '')}" if user.get('city') else 'Unknown'
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                **session,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'user_type': user['user_type'],
                    'phone': user['phone'],
                    'profile_image': user['profile_image'],
                    'location': location,
                    'zip_code': user.get('zip_code'),
                    'stats': stats
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    """User logout"""
    try:
        token = AuthUtils.extract_token_from_header()
        if token:
            SessionManager.end_session(token)
        
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/verify-token', methods=['GET'])
def verify_token():
    """Verify if token is valid"""
    try:
        token = AuthUtils.extract_token_from_header()
        if not token:
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        is_valid, user_data = SessionManager.validate_session(token)
        if not is_valid:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        return jsonify({
            'success': True,
            'valid': True,
            'user': user_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/check-service-area', methods=['POST'])
def check_service_area():
    """Check if a zip code is in service area"""
    try:
        data = request.json
        zip_code = data.get('zip_code', '').strip()
        
        if not zip_code:
            return jsonify({'success': False, 'error': 'Zip code required'}), 400
        
        location_info = location_service.get_local_market_info(zip_code)
        
        if not location_info.get('coordinates'):
            return jsonify({
                'success': False,
                'serviceable': False,
                'message': 'Service not available in your area yet'
            })
        
        # Find nearby chefs
        nearby_chefs = location_service.find_nearby_chefs(zip_code)
        
        return jsonify({
            'success': True,
            'serviceable': True,
            'location': location_info,
            'nearby_chefs_count': len(nearby_chefs),
            'message': f"Great! We serve {location_info['location']} with {len(nearby_chefs)} chefs nearby"
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500