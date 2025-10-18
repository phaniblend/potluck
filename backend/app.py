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

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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

try:
    from routes.chef import bp as chef_bp
    app.register_blueprint(chef_bp, url_prefix='/api/chef')
    print("✅ Chef routes registered successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not register chef routes: {e}")
    print("⚠️ Chef endpoints will not be available")

try:
    from routes.translation import bp as translation_bp
    app.register_blueprint(translation_bp, url_prefix='/api/translation')
    print("✅ Translation routes registered successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not register translation routes: {e}")
    print("⚠️ Translation endpoints will not be available")

try:
    from routes.delivery import bp as delivery_bp
    app.register_blueprint(delivery_bp, url_prefix='/api/delivery')
    print("✅ Delivery routes registered successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not register delivery routes: {e}")
    print("⚠️ Delivery endpoints will not be available")

try:
    from routes.consumer import bp as consumer_bp
    app.register_blueprint(consumer_bp, url_prefix='/api/consumer')
    print("✅ Consumer routes registered successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not register consumer routes: {e}")
    print("⚠️ Consumer endpoints will not be available")

# Note: Service area check is now handled by the routes/auth.py blueprint

# Note: Signup is now handled by the routes/auth.py blueprint

# Note: Login is now handled by the routes/auth.py blueprint

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