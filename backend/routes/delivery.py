"""
Delivery agent routes for Potluck app
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import sqlite3
import os
import base64
from datetime import datetime, timedelta

bp = Blueprint('delivery', __name__)

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'potluck.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        
        # In a real app, you'd verify the JWT token here
        # For now, we'll just check if it exists
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@require_auth
def dashboard():
    """Get delivery agent dashboard data"""
    try:
        conn = get_db_connection()
        
        # Get today's date
        today = datetime.now().date()
        
        # Get today's deliveries count
        deliveries_cursor = conn.execute('''
            SELECT COUNT(*) as count, COALESCE(SUM(earnings.amount), 0) as earnings
            FROM orders 
            LEFT JOIN earnings ON orders.id = earnings.order_id AND earnings.type = 'delivery_fee'
            WHERE delivery_agent_id = 1 -- This should be the actual user ID from token
            AND DATE(order_placed_at) = ?
            AND order_status = 'delivered'
        ''', (today,))
        
        delivery_data = deliveries_cursor.fetchone()
        
        # Get current status
        user_cursor = conn.execute('''
            SELECT current_status FROM users WHERE id = 1
        ''')
        user_data = user_cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'today_deliveries': delivery_data['count'],
            'today_earnings': delivery_data['earnings'],
            'current_status': user_data['current_status'] if user_data else 'offline'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/service-areas', methods=['GET', 'POST'])
@require_auth
def service_areas():
    """Get or add service areas"""
    try:
        conn = get_db_connection()
        
        if request.method == 'GET':
            # Get service areas
            cursor = conn.execute('''
                SELECT * FROM service_areas 
                WHERE delivery_agent_id = 1 -- This should be the actual user ID from token
                AND is_active = 1
                ORDER BY is_primary DESC, added_at DESC
            ''')
            
            areas = []
            for row in cursor.fetchall():
                areas.append({
                    'id': row['id'],
                    'area_name': row['area_name'],
                    'zip_code': row['zip_code'],
                    'city': row['city'],
                    'state': row['state'],
                    'country': row['country'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'is_primary': bool(row['is_primary']),
                    'is_active': bool(row['is_active']),
                    'added_at': row['added_at']
                })
            
            conn.close()
            return jsonify({'service_areas': areas})
            
        elif request.method == 'POST':
            # Add new service area
            data = request.get_json()
            
            # If this is set as primary, unset other primary areas
            if data.get('is_primary'):
                conn.execute('''
                    UPDATE service_areas 
                    SET is_primary = 0 
                    WHERE delivery_agent_id = 1
                ''')
            
            # Insert new service area
            conn.execute('''
                INSERT INTO service_areas 
                (delivery_agent_id, area_name, zip_code, city, state, country, is_primary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                1, # This should be the actual user ID from token
                data['area_name'],
                data['zip_code'],
                data['city'],
                data['state'],
                data.get('country', 'US'),
                data.get('is_primary', False)
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({'message': 'Service area added successfully'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/available-jobs')
@require_auth
def available_jobs():
    """Get available delivery jobs"""
    try:
        conn = get_db_connection()
        
        # Get service areas for this delivery agent
        service_areas_cursor = conn.execute('''
            SELECT zip_code FROM service_areas 
            WHERE delivery_agent_id = 1 AND is_active = 1
        ''')
        service_zips = [row['zip_code'] for row in service_areas_cursor.fetchall()]
        
        if not service_zips:
            conn.close()
            return jsonify({'jobs': []})
        
        # Get available jobs in service areas
        # This is a simplified query - in reality, you'd have more complex matching
        cursor = conn.execute('''
            SELECT o.id, o.delivery_address, o.pickup_address, o.total_amount,
                   o.delivery_latitude, o.delivery_longitude,
                   c.full_name as chef_name, c.address as chef_address,
                   c.latitude as chef_latitude, c.longitude as chef_longitude
            FROM orders o
            JOIN users c ON o.chef_id = c.id
            WHERE o.order_status = 'ready'
            AND o.delivery_agent_id IS NULL
            AND o.delivery_type = 'delivery'
            AND (o.delivery_address LIKE '%' || ? || '%' OR ? IN (
                SELECT zip_code FROM service_areas 
                WHERE delivery_agent_id = 1 AND is_active = 1
            ))
            ORDER BY o.order_placed_at ASC
            LIMIT 10
        ''', (service_zips[0], service_zips[0]))
        
        jobs = []
        for row in cursor.fetchall():
            # Calculate estimated earnings (simplified)
            estimated_earnings = max(5.0, row['total_amount'] * 0.1)  # 10% of order value, min $5
            
            jobs.append({
                'id': row['id'],
                'pickup_address': row['chef_address'],
                'delivery_address': row['delivery_address'],
                'pickup_latitude': row['chef_latitude'],
                'pickup_longitude': row['chef_longitude'],
                'delivery_latitude': row['delivery_latitude'],
                'delivery_longitude': row['delivery_longitude'],
                'chef_name': row['chef_name'],
                'estimated_earnings': round(estimated_earnings, 2),
                'estimated_time': 30,  # Simplified
                'distance': 5.2  # Simplified - will be calculated on frontend
            })
        
        conn.close()
        return jsonify({'jobs': jobs})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/recent-deliveries')
@require_auth
def recent_deliveries():
    """Get recent deliveries"""
    try:
        conn = get_db_connection()
        
        cursor = conn.execute('''
            SELECT o.id, o.delivery_address, o.pickup_address, o.order_status,
                   o.delivered_at, e.amount as earnings
            FROM orders o
            LEFT JOIN earnings e ON o.id = e.order_id AND e.type = 'delivery_fee'
            WHERE o.delivery_agent_id = 1
            AND o.order_status IN ('delivered', 'cancelled')
            ORDER BY o.delivered_at DESC
            LIMIT 10
        ''')
        
        deliveries = []
        for row in cursor.fetchall():
            deliveries.append({
                'id': row['id'],
                'pickup_address': row['pickup_address'],
                'delivery_address': row['delivery_address'],
                'status': row['order_status'],
                'earnings': row['earnings'] or 0,
                'completed_at': row['delivered_at']
            })
        
        conn.close()
        return jsonify({'deliveries': deliveries})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/verification-status')
@require_auth
def verification_status():
    """Get verification status"""
    try:
        conn = get_db_connection()
        
        cursor = conn.execute('''
            SELECT document_type, verification_status
            FROM delivery_verification
            WHERE delivery_agent_id = 1
            ORDER BY created_at DESC
        ''')
        
        status = {}
        for row in cursor.fetchall():
            status[f"{row['document_type']}_status"] = row['verification_status']
        
        conn.close()
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/verification', methods=['POST'])
@require_auth
def submit_verification():
    """Submit verification documents"""
    try:
        # In a real app, you'd save the files to a secure location
        # and store the file paths in the database
        
        conn = get_db_connection()
        
        # Get uploaded files
        files = request.files
        
        if 'driving_license' in files:
            # Save driving license
            conn.execute('''
                INSERT INTO delivery_verification 
                (delivery_agent_id, document_type, document_url, verification_status)
                VALUES (?, ?, ?, ?)
            ''', (1, 'driving_license', 'saved_file_path', 'pending'))
        
        if 'vehicle_registration' in files:
            # Save vehicle registration
            conn.execute('''
                INSERT INTO delivery_verification 
                (delivery_agent_id, document_type, document_url, verification_status)
                VALUES (?, ?, ?, ?)
            ''', (1, 'vehicle_registration', 'saved_file_path', 'pending'))
        
        # Handle selfie (base64 data)
        if 'selfie' in request.form:
            conn.execute('''
                INSERT INTO delivery_verification 
                (delivery_agent_id, document_type, document_url, verification_status)
                VALUES (?, ?, ?, ?)
            ''', (1, 'selfie', 'saved_selfie_path', 'pending'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Verification documents submitted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/status', methods=['POST'])
@require_auth
def update_status():
    """Update delivery agent status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['online', 'offline', 'busy']:
            return jsonify({'error': 'Invalid status'}), 400
        
        conn = get_db_connection()
        conn.execute('''
            UPDATE users 
            SET current_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        ''', (new_status,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Status updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500