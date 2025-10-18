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
from utils.ai_translator import ai_translator

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
    """Validate location based on user type and chef availability"""
    try:
        data = request.json
        city = data.get('city', '').strip()
        state = data.get('state', '').strip()
        user_type = data.get('user_type', 'consumer')
        zip_code = data.get('zip_code', '').strip()
        
        if not city or not state:
            return jsonify({'valid': False, 'error': 'City and state are required'}), 400
        
        # CHEFS: Can signup anywhere - they CREATE service areas
        if user_type == 'chef':
            return jsonify({
                'valid': True,
                'message': 'Welcome Chef! You can start serving in this area.',
                'is_new_service_area': True
            })
        
        # For CONSUMERS and DELIVERY AGENTS: Check if chefs exist in the area
        # Query database to find chefs in the area
        try:
            # Get chefs in this city/state
            with DatabaseConnection.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, full_name, city, state, latitude, longitude, chef_specialties
                    FROM users 
                    WHERE user_type = 'chef' 
                    AND is_active = 1
                    AND city = ? AND state = ?
                """, (city, state))
                local_chefs = cursor.fetchall()
                
                # If no exact match, find nearest chefs
                if not local_chefs:
                    cursor.execute("""
                        SELECT id, full_name, city, state, latitude, longitude, chef_specialties
                        FROM users 
                        WHERE user_type = 'chef' 
                        AND is_active = 1
                        LIMIT 5
                    """)
                    nearest_chefs = cursor.fetchall()
                    
                    if user_type == 'delivery':
                        # DELIVERY AGENTS: Can signup and add service areas even without chefs
                        # They can add service areas from their dashboard later
                        return jsonify({
                            'valid': True,
                            'message': 'Location validated. You can add service areas from your dashboard after registration.',
                            'user_type': 'delivery',
                            'note': 'No chefs in this area yet, but you can still register and add service areas for future opportunities.'
                        })
                    else:
                        # CONSUMERS: Can signup but show nearest chefs
                        if nearest_chefs:
                            chef_list = [{
                                'name': chef['full_name'],
                                'city': chef['city'],
                                'state': chef['state'],
                                'specialties': chef.get('chef_specialties', '[]')
                            } for chef in nearest_chefs[:3]]
                            
                            return jsonify({
                                'valid': True,
                                'message': f'No chefs in {city}, {state} yet. Here are nearby chefs.',
                                'warning': 'Delivery may not be available. You might need to pickup your order.',
                                'nearest_chefs': chef_list,
                                'has_local_chefs': False
                            })
                        else:
                            return jsonify({
                                'valid': True,
                                'message': 'You can signup, but no chefs are available yet in your area.',
                                'warning': 'Be the first to encourage chefs in your area!',
                                'has_local_chefs': False
                            })
                else:
                    # Chefs exist in the area
                    chef_count = len(local_chefs)
                    return jsonify({
                        'valid': True,
                        'message': f'Great! {chef_count} chef(s) are serving in {city}, {state}.',
                        'has_local_chefs': True,
                        'chef_count': chef_count
                    })
                    
        except Exception as db_error:
            print(f"Database error in location validation: {db_error}")
            # Fallback to allowing signup
            if user_type == 'chef':
                return jsonify({
                    'valid': True,
                    'message': 'Welcome Chef! You can start serving in this area.'
                })
            else:
                return jsonify({
                    'valid': True,
                    'message': 'Location validated',
                    'warning': 'Could not verify chef availability. You can still signup.'
                })
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

@bp.route('/detect-location', methods=['POST'])
def detect_location():
    """Automatically detect user location and return localization data"""
    try:
        # Get client IP
        client_ip = request.remote_addr
        if client_ip in ['127.0.0.1', 'localhost']:
            client_ip = '8.8.8.8'  # Use Google DNS for local testing
        
        # Detect location
        location_data = geolocation_service.get_location_by_ip(client_ip)
        
        if not location_data:
            # Fallback to default location
            return jsonify({
                'success': True,
                'location': {
                    'city': 'Dallas',
                    'state': 'TX',
                    'country': 'United States',
                    'currency': 'USD',
                    'timezone': 'America/Chicago'
                }
            })
        
        return jsonify({
            'success': True,
            'location': {
                'city': location_data.city,
                'state': location_data.state,
                'country': location_data.country,
                'currency': location_data.currency,
                'timezone': location_data.timezone
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/translate', methods=['POST'])
def translate_text():
    """Translate text to target language using AI"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        text = data.get('text', '')
        target_language = data.get('target_language', 'en')
        source_language = data.get('source_language', 'en')
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        if not target_language:
            return jsonify({'success': False, 'error': 'No target language provided'}), 400
        
        # Translate the text
        translated_text = ai_translator.translate_text(text, target_language, source_language)
        
        return jsonify({
            'success': True,
            'translation': translated_text,
            'original_text': text,
            'source_language': source_language,
            'target_language': target_language
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/translate-batch', methods=['POST'])
def translate_batch():
    """Translate multiple texts at once"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        texts = data.get('texts', [])
        target_language = data.get('target_language', 'en')
        source_language = data.get('source_language', 'en')
        
        if not texts or not isinstance(texts, list):
            return jsonify({'success': False, 'error': 'No texts provided or invalid format'}), 400
        
        if not target_language:
            return jsonify({'success': False, 'error': 'No target language provided'}), 400
        
        # Translate the texts
        translations = ai_translator.translate_batch(texts, target_language, source_language)
        
        return jsonify({
            'success': True,
            'translations': translations,
            'source_language': source_language,
            'target_language': target_language
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/test', methods=['GET'])
def test_auth():
    """Test auth endpoint"""
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
    """Register new user - Debug version"""
    print("=== SIGNUP REQUEST START ===")
    try:
        data = request.json
        print(f"📝 Signup data received: {data}")
        
        # Validate required fields
        required = ['email', 'password', 'full_name', 'phone', 'user_type', 'zip_code']
        for field in required:
            if field not in data:
                print(f"❌ Missing field: {field}")
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        print("✅ All required fields present")
        
        # Validate user type
        if data['user_type'] not in ['consumer', 'chef', 'delivery']:
            print(f"❌ Invalid user type: {data['user_type']}")
            return jsonify({'success': False, 'error': 'Invalid user type'}), 400
        
        print(f"✅ Valid user type: {data['user_type']}")
        
        # Basic email validation
        if '@' not in data['email'] or '.' not in data['email']:
            print(f"❌ Invalid email: {data['email']}")
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        print(f"✅ Valid email: {data['email']}")
        
        # Check if user exists
        print("🔍 Checking if user exists...")
        try:
            existing_user = DatabaseHelper.get_user_by_email(data['email'])
            if existing_user:
                print(f"❌ User already exists: {data['email']}")
                return jsonify({'success': False, 'error': 'Email already registered'}), 400
            print("✅ User does not exist, can proceed")
        except Exception as e:
            print(f"⚠️ Database check error (continuing): {e}")
        
        # Basic password validation
        if len(data['password']) < 8:
            print(f"❌ Password too short: {len(data['password'])} chars")
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400
        
        print("✅ Password validation passed")
        
        # Hash password
        print("🔐 Hashing password...")
        try:
            password_hash = AuthUtils.hash_password(data['password'])
            print("✅ Password hashed successfully")
        except Exception as e:
            print(f"❌ Password hashing error: {e}")
            return jsonify({'success': False, 'error': 'Error processing password'}), 500
        
        # Create user data
        
        user_data = {
            'email': data['email'],
            'password_hash': password_hash,
            'full_name': data['full_name'],
            'phone': data['phone'],
            'user_type': data['user_type'],
            'zip_code': data['zip_code'],
            'city': data.get('city', 'Dallas'),
            'state': data.get('state', 'TX'),
            'address': data.get('address', ''),
            'latitude': 32.7767,
            'longitude': -96.7970
        }
        
        print(f"👤 User data prepared: {user_data['email']}")
        
        # Create user in database
        print("💾 Creating user in database...")
        try:
            user_id = DatabaseHelper.create_user(user_data)
            print(f"✅ User created with ID: {user_id}")
        except Exception as e:
            print(f"❌ Database creation error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': 'Database error creating user'}), 500
        
        if not user_id:
            print("❌ User ID is None/False")
            return jsonify({'success': False, 'error': 'Failed to create user account'}), 500
        
        # Generate session token
        print("🎟️ Generating session token...")
        try:
            token = AuthUtils.generate_token(user_id, data['user_type'], data['email'])
            print("✅ Token generated successfully")
        except Exception as e:
            print(f"❌ Token generation error: {e}")
            return jsonify({'success': False, 'error': 'Error generating session'}), 500
        
        print("🎉 Signup successful!")
        print("=== SIGNUP REQUEST END ===")
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully! Welcome to Potluck!',
            'data': {
                'token': token,
                'user': {
                    'id': user_id,
                    'email': data['email'],
                    'full_name': data['full_name'],
                    'user_type': data['user_type'],
                    'location': f"{user_data['city']}, {user_data['state']}"
                }
            }
        })
        
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=== SIGNUP REQUEST END (ERROR) ===")
        return jsonify({'success': False, 'error': 'Error creating user account'}), 500

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
        
        payload = AuthUtils.decode_token(token)
        if not payload:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Get fresh user data
        user = DatabaseHelper.get_user_by_id(payload['user_id'])
        if not user or not user['is_active']:
            return jsonify({'success': False, 'error': 'User not found or inactive'}), 401
        
        user_data = {
            'id': user['id'],
            'email': user['email'],
            'full_name': user['full_name'],
            'user_type': user['user_type'],
            'phone': user['phone'],
            'profile_image': user['profile_image']
        }
        
        return jsonify({
            'success': True,
            'valid': True,
            'user': user_data
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
