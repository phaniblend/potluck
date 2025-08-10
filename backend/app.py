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

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import our modules
from config.database import DatabaseHelper, DatabaseConnection
from utils.auth_utils import AuthUtils, login_required, role_required

# Import routes (we'll create these next)
from routes import auth, consumer, chef, delivery, orders, common
# Create Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'potluck-secret-key-change-in-production')

# Enable CORS for all routes
CORS(app, origins=['http://localhost:3000', 'http://localhost:5000'])

# Database initialization check
def check_database():
    """Check if database exists and is accessible"""
    try:
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            result = cursor.fetchone()
            table_count = result['COUNT(*)'] if isinstance(result, dict) else result[0]
            if table_count == 0:
                print("⚠️  Warning: Database has no tables. Run 'python database/init_db.py' to initialize.")
                return False
            print(f"✅ Database connected successfully with {table_count} tables")
            return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("Please run 'python database/init_db.py' to initialize the database.")
        return False

# Register blueprints
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(consumer.bp, url_prefix='/api/consumer')
app.register_blueprint(chef.bp, url_prefix='/api/chef')
app.register_blueprint(delivery.bp, url_prefix='/api/delivery')
app.register_blueprint(orders.bp, url_prefix='/api/orders')
app.register_blueprint(common.bp, url_prefix='/api/common')

# =====================
# Basic Routes
# =====================

@app.route('/')
def index():
    """Serve the main frontend page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/health')
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Potluck API',
        'version': '1.0.0'
    })

@app.route('/api/stats')
def platform_stats():
    """Get platform statistics"""
    try:
        stats = {}
        
        # Get user counts by type
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            
            # Total users by type
            cursor.execute("""
                SELECT user_type, COUNT(*) as count 
                FROM users 
                GROUP BY user_type
            """)
            user_counts = cursor.fetchall()
            stats['users'] = {row['user_type']: row['count'] for row in user_counts}
            
            # Total dishes
            cursor.execute("SELECT COUNT(*) FROM dishes WHERE is_available = 1")
            result = cursor.fetchone()
            stats['active_dishes'] = result['COUNT(*)'] if isinstance(result, dict) else result[0]
            
            # Total orders
            cursor.execute("SELECT COUNT(*) FROM orders")
            result = cursor.fetchone()
            stats['total_orders'] = result['COUNT(*)'] if isinstance(result, dict) else result[0]
            
            # Today's orders
            cursor.execute("""
                SELECT COUNT(*) FROM orders 
                WHERE DATE(order_placed_at) = DATE('now')
            """)
            result = cursor.fetchone()
            stats['orders_today'] = result['COUNT(*)'] if isinstance(result, dict) else result[0]
            
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search')
def search():
    """Search for dishes and chefs"""
    try:
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')  # all, dishes, chefs
        
        results = {
            'dishes': [],
            'chefs': []
        }
        
        if search_type in ['all', 'dishes']:
            # Search dishes
            dishes = DatabaseHelper.search_dishes(query)
            results['dishes'] = dishes
        
        if search_type in ['all', 'chefs']:
            # Search chefs
            with DatabaseConnection.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, full_name, chef_bio, chef_specialties, 
                           chef_rating, total_dishes_sold, profile_image
                    FROM users 
                    WHERE user_type = 'chef' 
                      AND is_active = 1
                      AND (full_name LIKE ? OR chef_bio LIKE ? OR chef_specialties LIKE ?)
                    LIMIT 20
                """, (f'%{query}%', f'%{query}%', f'%{query}%'))
                
                chefs = []
                for row in cursor.fetchall():
                    chefs.append({
                        'id': row['id'],
                        'name': row['full_name'],
                        'bio': row['chef_bio'],
                        'specialties': row['chef_specialties'],
                        'rating': row['chef_rating'],
                        'total_dishes_sold': row['total_dishes_sold'],
                        'profile_image': row['profile_image']
                    })
                results['chefs'] = chefs
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/featured')
def get_featured():
    """Get featured dishes and top chefs"""
    try:
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            
            # Get top rated dishes
            cursor.execute("""
                SELECT d.*, u.full_name as chef_name, u.chef_rating
                FROM dishes d
                JOIN users u ON d.chef_id = u.id
                WHERE d.is_available = 1
                ORDER BY d.rating DESC, d.total_orders DESC
                LIMIT 6
            """)
            
            featured_dishes = []
            for row in cursor.fetchall():
                featured_dishes.append(dict(row))
            
            # Get top rated chefs
            cursor.execute("""
                SELECT id, full_name, chef_bio, chef_specialties, 
                       chef_rating, total_dishes_sold, profile_image
                FROM users
                WHERE user_type = 'chef' AND is_active = 1
                ORDER BY chef_rating DESC, total_dishes_sold DESC
                LIMIT 4
            """)
            
            top_chefs = []
            for row in cursor.fetchall():
                top_chefs.append(dict(row))
        
        return jsonify({
            'success': True,
            'featured_dishes': featured_dishes,
            'top_chefs': top_chefs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cuisines')
def get_cuisines():
    """Get list of available cuisines"""
    try:
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT cuisine_type, COUNT(*) as dish_count
                FROM dishes
                WHERE is_available = 1 AND cuisine_type IS NOT NULL
                GROUP BY cuisine_type
                ORDER BY dish_count DESC
            """)
            
            cuisines = []
            for row in cursor.fetchall():
                cuisines.append({
                    'name': row['cuisine_type'],
                    'dish_count': row['dish_count']
                })
        
        return jsonify({
            'success': True,
            'cuisines': cuisines
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =====================
# Protected Test Routes
# =====================

@app.route('/api/protected')
@login_required
def protected_route():
    """Test protected route"""
    user = request.current_user
    return jsonify({
        'message': 'This is a protected route',
        'user': user
    })

@app.route('/api/chef-only')
@role_required('chef')
def chef_only_route():
    """Test chef-only route"""
    user = request.current_user
    return jsonify({
        'message': 'This route is for chefs only',
        'user': user
    })

# =====================
# Error Handlers
# =====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle uncaught exceptions"""
    app.logger.error(f"Unhandled exception: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'An unexpected error occurred'
    }), 500

# =====================
# Static File Serving
# =====================

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from frontend directory"""
    return send_from_directory('../frontend', path)

# =====================
# Main Entry Point
# =====================

if __name__ == '__main__':
    print("=" * 50)
    print("   POTLUCK API SERVER")
    print("=" * 50)
    
    # Check database
    if not check_database():
        print("\n⚠️  Please initialize the database before starting the server.")
        print("Run: python database/init_db.py")
        sys.exit(1)
    
    # Get configuration from environment
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print(f"\n🚀 Starting server...")
    print(f"📍 Local URL: http://localhost:{port}")
    print(f"📍 API Health: http://localhost:{port}/api/health")
    print(f"🔧 Debug mode: {debug}")
    print("\nPress CTRL+C to stop the server")
    print("=" * 50)
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )