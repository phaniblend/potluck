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