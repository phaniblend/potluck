"""
Authentication routes for Potluck app
Handles signup, login, logout
"""

from flask import Blueprint, request, jsonify
import sys
import os
import time
from collections import defaultdict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import DatabaseHelper, DatabaseConnection
from utils.auth_utils import AuthUtils, SessionManager, validate_password_strength
from utils.location import location_service
from utils.geolocation import geolocation_service

# Simple in-memory rate limiting (in production, use Redis)
rate_limit_store = defaultdict(list)
MAX_ATTEMPTS = 5  # Max attempts per IP
WINDOW_SECONDS = 300  # 5 minutes

def check_rate_limit(ip_address):
    """Check if IP is rate limited"""
    current_time = time.time()
    
    # Clean old entries
    rate_limit_store[ip_address] = [
        attempt_time for attempt_time in rate_limit_store[ip_address]
        if current_time - attempt_time < WINDOW_SECONDS
    ]
    
    # Check if limit exceeded
    if len(rate_limit_store[ip_address]) >= MAX_ATTEMPTS:
        return False
    
    # Add current attempt
    rate_limit_store[ip_address].append(current_time)
    return True

bp = Blueprint('auth', __name__)

@bp.route('/validate-location', methods=['POST'])
def validate_location():
    """Validate city and state combination"""
    try:
        data = request.json
        city = data.get('city', '').strip()
        state = data.get('state', '').strip()
        
        if not city or not state:
            return jsonify({'valid': False, 'error': 'City and state are required'}), 400
        
        # Check if this city/state combination exists in our service areas
        valid_combinations = [
            ('Dallas', 'TX'),
            ('San Francisco', 'CA'),
            ('New York', 'NY'),
            ('Mumbai', 'MH'),
            ('Delhi', 'DL'),
            ('Bangalore', 'KA'),
            ('Mexico City', 'CDMX'),
            ('Guadalajara', 'JAL'),
        ]
        
        # Normalize for comparison (case-insensitive)
        city_normalized = city.lower().strip()
        state_normalized = state.upper().strip()
        
        # Check if combination exists
        is_valid = any(
            city_normalized == valid_city.lower() and 
            state_normalized == valid_state.upper()
            for valid_city, valid_state in valid_combinations
        )
        
        return jsonify({
            'valid': is_valid,
            'message': 'Location validated successfully' if is_valid else 'Location not in service area'
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

@bp.route('/detect-location', methods=['POST'])
def detect_location():
    """Automatically detect user location and return localization data"""
    try:
        data = request.json
        client_ip = request.remote_addr
        
        # Get location by IP address
        location_data = geolocation_service.get_location_by_ip(client_ip)
        
        if not location_data:
            return jsonify({
                'success': False,
                'error': 'Could not detect location automatically'
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'city': location_data.city,
                'state': location_data.state,
                'country': location_data.country,
                'country_code': location_data.country_code,
                'postal_code': location_data.postal_code,
                'latitude': location_data.latitude,
                'longitude': location_data.longitude,
                'timezone': location_data.timezone,
                'currency': location_data.currency,
                'currency_symbol': location_data.currency_symbol,
                'language': location_data.language,
                'language_code': location_data.language_code,
                'phone_code': location_data.phone_code,
                'is_supported': location_data.is_supported,
                'pricing_tier': geolocation_service.GLOBAL_LOCALIZATION.get(
                    location_data.country_code, {}).get('pricing_tier', 'medium')
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/test', methods=['GET'])
def test_auth():
    """Test endpoint to verify auth routes are working"""
    return jsonify({
        'success': True,
        'message': 'Auth routes are working!',
        'timestamp': time.time()
    })

@bp.route('/check-service-area', methods=['POST'])
def check_service_area():
    """Check if zip code is in service area"""
    try:
        data = request.json
        zip_code = data.get('zip_code', '').strip()
        
        if not zip_code:
            return jsonify({'success': False, 'error': 'Zip code required'}), 400
        
        # Get location info for the zip code
        location_info = location_service.get_local_market_info(zip_code)
        
        if not location_info.get('coordinates'):
            return jsonify({
                'success': False,
                'serviceable': False,
                'message': 'Service not available in your area yet. We currently serve Dallas, Mumbai, and Mexico City areas.'
            })
        
        return jsonify({
            'success': True,
            'serviceable': True,
            'message': f'Great! We serve {location_info["city"]}, {location_info["state"]} area (ZIP: {zip_code})',
            'location': location_info['location']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/signup', methods=['POST'])
def signup():
    """Register new user"""
    try:
        # Rate limiting
        client_ip = request.remote_addr
        if not check_rate_limit(client_ip):
            return jsonify({
                'success': False, 
                'error': 'Too many signup attempts. Please try again in 5 minutes.'
            }), 429
        
        data = request.json
        
        # Validate required fields
        required = ['email', 'password', 'full_name', 'phone', 'user_type', 'zip_code']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Validate user type
        if data['user_type'] not in ['consumer', 'chef', 'delivery']:
            return jsonify({'success': False, 'error': 'Invalid user type'}), 400
        
        # Get user's location automatically (IP-based geolocation)
        client_ip = request.remote_addr
        print(f"Client IP: {client_ip}")  # Debug log
        
        try:
            user_location = geolocation_service.get_location_by_ip(client_ip)
            print(f"Location detected: {user_location}")  # Debug log
        except Exception as e:
            print(f"Geolocation error: {e}")  # Debug log
            # Fallback to default location
            user_location = geolocation_service.get_location_by_ip('8.8.8.8')
        
        if not user_location:
            return jsonify({
                'success': False, 
                'error': 'Could not detect your location automatically. Please try again.'
            }), 400
        
        # Use provided ZIP code if available, otherwise use detected postal code
        zip_code = data.get('zip_code', '').strip() or user_location.postal_code
        
        # Validate that the user is in a supported country
        if not user_location.is_supported:
            return jsonify({
                'success': False, 
                'error': f'Service not yet available in {user_location.country}. We\'re expanding globally!'
            }), 400
        
        # Auto-fill city/state if not provided, or validate if provided
        user_city = data.get('city', '').strip() or user_location.city
        user_state = data.get('state', '').strip() or user_location.state
        
        # Validate city/state format (basic validation)
        if user_city and len(user_city) < 2:
            return jsonify({
                'success': False,
                'error': 'Please enter a valid city name'
            }), 400
        
        if user_state and len(user_state) < 2:
            return jsonify({
                'success': False,
                'error': 'Please enter a valid state/province'
            }), 400
        
        # Check for suspicious patterns (bot protection)
        suspicious_patterns = [
            r'^[a-z]{10,}$',  # Long random strings
            r'^[a-z]{2,}[0-9]{2,}[a-z]{2,}$',  # Mixed alphanumeric patterns
            r'^[a-z]+[0-9]+[a-z]+$',  # Alternating letters and numbers
            r'^[a-z]{5,}[0-9]{3,}$',  # Many letters followed by many numbers
        ]
        
        import re
        for pattern in suspicious_patterns:
            if re.search(pattern, user_city, re.IGNORECASE) or re.search(pattern, user_state, re.IGNORECASE):
                return jsonify({
                    'success': False,
                    'error': 'Please enter valid city and state names'
                }), 400
        
        # Validate email format
        if not AuthUtils.validate_email(data['email']):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Check if user exists
        try:
            existing_user = DatabaseHelper.get_user_by_email(data['email'])
            if existing_user:
                return jsonify({'success': False, 'error': 'Email already registered'}), 400
        except Exception as e:
            print(f"Database error checking existing user: {e}")
            # For now, allow registration if database check fails
            pass
        
        # Validate password strength
        try:
            is_valid, msg = validate_password_strength(data['password'])
            if not is_valid:
                return jsonify({'success': False, 'error': msg}), 400
        except Exception as e:
            print(f"Password validation error: {e}")
            # Basic password validation as fallback
            if len(data['password']) < 8:
                return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400
        
        # Hash password
        try:
            password_hash = AuthUtils.hash_password(data['password'])
        except Exception as e:
            print(f"Password hashing error: {e}")
            return jsonify({'success': False, 'error': 'Error processing password'}), 500
        
        # Create user with detected location data
        user_data = {
            'email': data['email'],
            'password_hash': password_hash,
            'full_name': data['full_name'],
            'phone': AuthUtils.format_phone(data['phone']),
            'user_type': data['user_type'],
            'zip_code': zip_code,
            'city': user_location.city,
            'state': user_location.state,
            'country': user_location.country,
            'country_code': user_location.country_code,
            'latitude': user_location.latitude,
            'longitude': user_location.longitude,
            'timezone': user_location.timezone,
            'currency': user_location.currency,
            'language': user_location.language_code
        }
        
        # Add address if provided
        if data.get('address'):
            user_data['address'] = data['address']
        
        # Set delivery radius for delivery agents
        if data['user_type'] == 'delivery':
            user_data['delivery_radius'] = 3  # 3km default for bicycle delivery
        
        # Create user
        try:
            user_id = DatabaseHelper.create_user(user_data)
            print(f"User created with ID: {user_id}")  # Debug log
        except Exception as e:
            print(f"User creation error: {e}")
            return jsonify({'success': False, 'error': 'Error creating user account'}), 500
        
        # Create session
        try:
            session = SessionManager.create_session(user_id, data['user_type'], data['email'])
            print(f"Session created: {session}")  # Debug log
        except Exception as e:
            print(f"Session creation error: {e}")
            # Return success without session for now
            session = {
                'token': 'temp-token-' + str(user_id),
                'user': {
                    'id': user_id,
                    'email': data['email'],
                    'full_name': data['full_name'],
                    'user_type': data['user_type']
                }
            }
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                **session,
                'location': f"{user_location.city}, {user_location.state}, {user_location.country}",
                'localization': {
                    'currency': user_location.currency,
                    'currency_symbol': user_location.currency_symbol,
                    'language': user_location.language,
                    'language_code': user_location.language_code,
                    'timezone': user_location.timezone,
                    'phone_code': user_location.phone_code
                }
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