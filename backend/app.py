"""
Potluck - Main Flask Application
Homemade Food Marketplace API
"""

import os
import sys
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'potluck-secret-key-change-in-production')

# Enable CORS for all routes
CORS(app, origins=['*'])

# Import and register route blueprints
try:
    from routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    print("✅ Auth routes registered successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not register auth routes: {e}")
    print("⚠️ Authentication endpoints will not be available")

# Add a simple test endpoint for service area check
@app.route('/api/auth/check-service-area', methods=['POST'])
def check_service_area_simple():
    """Simple service area check without database dependencies"""
    try:
        data = request.json
        zip_code = data.get('zip_code', '').strip()
        
        if not zip_code:
            return jsonify({'success': False, 'error': 'Zip code required'}), 400
        
        # Simple zip code validation for Dallas area
        dallas_zips = ['75201', '75202', '75203', '75204', '75205', '75206']
        
        if zip_code in dallas_zips:
            return jsonify({
                'success': True,
                'serviceable': True,
                'message': f'Great! We serve Dallas area (ZIP: {zip_code})',
                'location': 'Dallas, TX'
            })
        else:
            return jsonify({
                'success': False,
                'serviceable': False,
                'message': 'Service not available in your area yet'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Add a simple signup endpoint for testing
@app.route('/api/auth/signup', methods=['POST'])
def signup_simple():
    """Simple signup endpoint without database dependencies"""
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
        
        # Simple validation
        if len(data['password']) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400
        
        # For chefs, they're expanding service to new areas (no validation needed)
        # For consumers and delivery agents, we validate the service area
        if data['user_type'] in ['consumer', 'delivery']:
            # Check if service is available in their area
            dallas_zips = ['75201', '75202', '75203', '75204', '75205', '75206']
            if data['zip_code'] not in dallas_zips:
                return jsonify({
                    'success': False, 
                    'error': 'Service not available in your area yet. We currently serve Dallas area.'
                }), 400
        
        # Return success (in production, this would create a user)
        return jsonify({
            'success': True,
            'message': f'User registered successfully (test mode) - {data["user_type"]} expanding service to {data["zip_code"]}',
            'data': {
                'token': 'test-token-123',
                'user': {
                    'id': 1,
                    'email': data['email'],
                    'full_name': data['full_name'],
                    'user_type': data['user_type']
                }
            }
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Add a simple login endpoint for testing
@app.route('/api/auth/login', methods=['POST'])
def login_simple():
    """Simple login endpoint without database dependencies"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        # Simple test login (in production, this would validate against database)
        if data['email'] == 'test@example.com' and data['password'] == 'password123':
            return jsonify({
                'success': True,
                'message': 'Login successful (test mode)',
                'data': {
                    'token': 'test-token-123',
                    'user': {
                        'id': 1,
                        'email': data['email'],
                        'full_name': 'Test User',
                        'user_type': 'consumer'
                    }
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =====================
# Basic Routes
# =====================

@app.route('/')
def index():
    """Serve the main frontend page"""
    try:
        return send_from_directory('../frontend', 'index.html')
    except:
        return "Potluck API is running!"

@app.route('/api/health')
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Potluck API',
        'version': '1.0.0',
        'message': 'Application is running successfully'
    })

@app.route('/api/stats')
def platform_stats():
    """Get platform statistics"""
    return jsonify({
        'success': True,
        'data': {
            'users': {'total': 0},
            'active_dishes': 0,
            'total_orders': 0,
            'orders_today': 0
        },
        'message': 'Basic stats endpoint - database not yet configured'
    })

@app.route('/api/test')
def test():
    """Test endpoint"""
    return jsonify({
        'message': 'Potluck API is working!',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/auth/test')
def auth_test():
    """Test auth endpoint"""
    return jsonify({
        'message': 'Auth routes are working!',
        'timestamp': datetime.utcnow().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)