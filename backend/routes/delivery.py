"""
Delivery agent routes for Potluck app
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import sqlite3
import os
import base64
from datetime import datetime, timedelta
from middleware.auth import require_auth

bp = Blueprint('delivery', __name__)

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'potluck.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/dashboard')
@require_auth
def dashboard(user_id):
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
            WHERE delivery_agent_id = ?
            AND DATE(order_placed_at) = ?
            AND order_status = 'delivered'
        ''', (user_id, today))
        
        delivery_data = deliveries_cursor.fetchone()
        
        # Get current status
        user_cursor = conn.execute('''
            SELECT current_status FROM users WHERE id = ?
        ''', (user_id,))
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
def service_areas(user_id):
    """Get or add service areas"""
    try:
        conn = get_db_connection()
        
        if request.method == 'GET':
            # Get service areas
            cursor = conn.execute('''
                SELECT * FROM service_areas 
                WHERE delivery_agent_id = ?
                AND is_active = 1
                ORDER BY is_primary DESC, added_at DESC
            ''', (user_id,))
            
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
                    WHERE delivery_agent_id = ?
                ''', (user_id,))
            
            # Insert new service area
            conn.execute('''
                INSERT INTO service_areas 
                (delivery_agent_id, area_name, zip_code, city, state, country, is_primary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
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
def available_jobs(user_id):
    """Get available delivery jobs (orders that have been accepted by chef)"""
    try:
        from datetime import datetime
        from math import radians, sin, cos, sqrt, atan2
        
        conn = get_db_connection()
        
        # Get delivery agent location
        da_cursor = conn.execute('SELECT latitude, longitude, zip_code FROM users WHERE id = ?', (user_id,))
        da_info = da_cursor.fetchone()
        
        if not da_info or not da_info['latitude'] or not da_info['longitude']:
            conn.close()
            return jsonify({'jobs': [], 'message': 'Please update your location first'})
        
        da_lat = da_info['latitude']
        da_lon = da_info['longitude']
        
        # Get service areas for this delivery agent
        service_areas_cursor = conn.execute('''
            SELECT zip_code FROM service_areas 
            WHERE delivery_agent_id = ? AND is_active = 1
        ''', (user_id,))
        service_zips = [row['zip_code'] for row in service_areas_cursor.fetchall()]
        
        if not service_zips:
            conn.close()
            return jsonify({'jobs': [], 'message': 'Please add service areas first'})
        
        # Get available jobs - orders that are accepted/preparing/ready but not yet assigned
        cursor = conn.execute('''
            SELECT o.id, o.order_number, o.delivery_address, o.total_amount,
                   o.delivery_latitude, o.delivery_longitude, o.expected_ready_time,
                   o.order_status,
                   c.full_name as chef_name, c.address as chef_address,
                   c.latitude as chef_latitude, c.longitude as chef_longitude,
                   c.zip_code as chef_zip,
                   consumer.full_name as consumer_name,
                   consumer.latitude as consumer_lat, consumer.longitude as consumer_lon,
                   consumer.zip_code as consumer_zip
            FROM orders o
            JOIN users c ON o.chef_id = c.id
            JOIN users consumer ON o.consumer_id = consumer.id
            WHERE o.order_status IN ('accepted', 'preparing', 'ready')
            AND o.delivery_agent_id IS NULL
            AND o.delivery_type = 'delivery'
            AND consumer.zip_code IN ({})
            ORDER BY o.order_placed_at ASC
            LIMIT 20
        '''.format(','.join('?' * len(service_zips))), service_zips)
        
        # Helper function to calculate distance (Haversine)
        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 3959  # Earth's radius in miles
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        
        jobs = []
        for row in cursor.fetchall():
            # Calculate distances
            da_to_chef_distance = calculate_distance(da_lat, da_lon, row['chef_latitude'], row['chef_longitude'])
            chef_to_consumer_distance = calculate_distance(
                row['chef_latitude'], row['chef_longitude'],
                row['consumer_lat'], row['consumer_lon']
            )
            
            # Calculate estimated earnings
            base_fee = 3.99
            distance_fee = chef_to_consumer_distance * 0.50  # $0.50 per mile
            estimated_earnings = round(base_fee + distance_fee, 2)
            
            # Calculate ETA (minutes until ready)
            eta_minutes = None
            status_text = row['order_status'].capitalize()
            if row['expected_ready_time']:
                try:
                    ready_time = datetime.fromisoformat(row['expected_ready_time'])
                    now = datetime.now()
                    time_diff = (ready_time - now).total_seconds() / 60
                    eta_minutes = max(0, int(time_diff))
                    status_text = f"Ready in ~{eta_minutes} min"
                except:
                    pass
            
            jobs.append({
                'id': row['id'],
                'order_number': row['order_number'],
                'pickup_address': row['chef_address'],
                'delivery_address': row['delivery_address'],
                'pickup_latitude': row['chef_latitude'],
                'pickup_longitude': row['chef_longitude'],
                'delivery_latitude': row['delivery_latitude'],
                'delivery_longitude': row['delivery_longitude'],
                'chef_name': row['chef_name'],
                'consumer_name': row['consumer_name'],
                'estimated_earnings': estimated_earnings,
                'da_to_chef_distance': round(da_to_chef_distance, 1),
                'chef_to_consumer_distance': round(chef_to_consumer_distance, 1),
                'eta_minutes': eta_minutes,
                'order_status': row['order_status'],
                'status_text': status_text
            })
        
        conn.close()
        return jsonify({'jobs': jobs})
        
    except Exception as e:
        print(f"Error fetching available jobs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/recent-deliveries')
@require_auth
def recent_deliveries(user_id):
    """Get recent deliveries"""
    try:
        conn = get_db_connection()
        
        cursor = conn.execute('''
            SELECT o.id, o.delivery_address, c.address as pickup_address, o.order_status,
                   o.delivered_at, e.amount as earnings
            FROM orders o
            JOIN users c ON o.chef_id = c.id
            LEFT JOIN earnings e ON o.id = e.order_id AND e.type = 'delivery_fee'
            WHERE o.delivery_agent_id = ?
            AND o.order_status IN ('delivered', 'cancelled')
            ORDER BY o.delivered_at DESC
            LIMIT 10
        ''', (user_id,))
        
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

@bp.route('/update-status/<int:order_id>', methods=['PUT'])
@require_auth
def update_order_status(user_id, order_id):
    """DA updates order status to picked_up or delivered"""
    try:
        data = request.get_json(silent=True) or {}
        new_status = data.get('status')
        if new_status not in ['picked_up', 'delivered']:
            return jsonify({'error': 'Invalid status'}), 400
        
        conn = get_db_connection()
        cursor = conn.execute('SELECT delivery_agent_id, order_status FROM orders WHERE id = ?', (order_id,))
        order = cursor.fetchone()
        if not order:
            conn.close()
            return jsonify({'error': 'Order not found'}), 404
        
        # Ensure the order is assigned to this DA
        if order['delivery_agent_id'] != user_id:
            conn.close()
            return jsonify({'error': 'Order not assigned to this delivery agent'}), 403
        
        now = datetime.utcnow().isoformat()
        if new_status == 'picked_up':
            # Enforce: can pick up only when chef marked as ready
            if order['order_status'] == 'picked_up':
                conn.close()
                return jsonify({'error': 'Order has already been picked up'}), 400
            elif order['order_status'] == 'delivered':
                conn.close()
                return jsonify({'error': 'Order has already been delivered'}), 400
            elif order['order_status'] != 'ready':
                conn.close()
                return jsonify({'error': f'Order is not ready for pickup yet. Current status: {order["order_status"]}'}), 400
            conn.execute('''
                UPDATE orders
                SET order_status = 'picked_up', picked_up_at = ?
                WHERE id = ?
            ''', (now, order_id))
        elif new_status == 'delivered':
            # Enforce: can deliver only after picked_up
            if order['order_status'] == 'delivered':
                conn.close()
                return jsonify({'error': 'Order has already been delivered'}), 400
            elif order['order_status'] != 'picked_up':
                conn.close()
                return jsonify({'error': f'Order must be picked up before marking delivered. Current status: {order["order_status"]}'}), 400
            conn.execute('''
                UPDATE orders
                SET order_status = 'delivered', delivered_at = ?
                WHERE id = ?
            ''', (now, order_id))
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'Order status updated', 'status': new_status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/verification-status')
@require_auth
def verification_status(user_id):
    """Get verification status"""
    try:
        conn = get_db_connection()
        
        cursor = conn.execute('''
            SELECT document_type, verification_status
            FROM delivery_verification
            WHERE delivery_agent_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        status = {}
        for row in cursor.fetchall():
            status[f"{row['document_type']}_status"] = row['verification_status']
        
        conn.close()
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/verification', methods=['POST'])
@require_auth
def submit_verification(user_id):
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
            ''', (user_id, 'driving_license', 'saved_file_path', 'pending'))
        
        if 'vehicle_registration' in files:
            # Save vehicle registration
            conn.execute('''
                INSERT INTO delivery_verification 
                (delivery_agent_id, document_type, document_url, verification_status)
                VALUES (?, ?, ?, ?)
            ''', (user_id, 'vehicle_registration', 'saved_file_path', 'pending'))
        
        # Handle selfie (base64 data)
        if 'selfie' in request.form:
            conn.execute('''
                INSERT INTO delivery_verification 
                (delivery_agent_id, document_type, document_url, verification_status)
                VALUES (?, ?, ?, ?)
            ''', (user_id, 'selfie', 'saved_selfie_path', 'pending'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Verification documents submitted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/status', methods=['POST'])
@require_auth
def update_status(user_id):
    """Update delivery agent status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['online', 'offline', 'busy']:
            return jsonify({'error': 'Invalid status'}), 400
        
        conn = get_db_connection()
        conn.execute('''
            UPDATE users 
            SET current_status = ?
            WHERE id = ?
        ''', (new_status, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Status updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/accept-job/<int:order_id>', methods=['POST'])
@require_auth
def accept_job(user_id, order_id):
    """Accept a delivery job"""
    try:
        conn = get_db_connection()
        
        # Check if order exists and is available
        cursor = conn.execute('''
            SELECT id, order_status, delivery_agent_id, chef_id, consumer_id
            FROM orders 
            WHERE id = ? AND delivery_type = 'delivery'
        ''', (order_id,))
        order = cursor.fetchone()
        
        if not order:
            conn.close()
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        if order['delivery_agent_id'] is not None:
            conn.close()
            return jsonify({'success': False, 'error': 'Order already assigned'}), 400
        
        if order['order_status'] not in ['accepted', 'preparing', 'ready']:
            conn.close()
            return jsonify({'success': False, 'error': 'Order not available for pickup'}), 400
        
        # Assign delivery agent to order
        conn.execute('''
            UPDATE orders 
            SET delivery_agent_id = ?
            WHERE id = ?
        ''', (user_id, order_id))
        
        # Create notification for chef
        conn.execute('''
            INSERT INTO notifications (user_id, type, title, message, related_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            order['chef_id'],
            'delivery_assigned',
            'Delivery Agent Assigned',
            f'A delivery agent has been assigned to order #{order_id}',
            order_id
        ))
        
        # Create notification for consumer
        conn.execute('''
            INSERT INTO notifications (user_id, type, title, message, related_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            order['consumer_id'],
            'delivery_assigned',
            'Delivery Agent On The Way',
            f'Your order #{order_id} has been assigned to a delivery agent',
            order_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Job accepted successfully'
        })
        
    except Exception as e:
        print(f"Accept job error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/active-orders')
@require_auth
def active_orders(user_id):
    """Get active orders assigned to this delivery agent"""
    try:
        from math import radians, sin, cos, sqrt, atan2
        
        conn = get_db_connection()
        
        # Get delivery agent location
        da_cursor = conn.execute('SELECT latitude, longitude FROM users WHERE id = ?', (user_id,))
        da_info = da_cursor.fetchone()
        
        if not da_info or not da_info['latitude'] or not da_info['longitude']:
            conn.close()
            return jsonify({'orders': []})
        
        da_lat = da_info['latitude']
        da_lon = da_info['longitude']
        
        # Get active orders assigned to this DA
        cursor = conn.execute('''
            SELECT o.id, o.order_number, o.delivery_address, o.total_amount,
                   o.delivery_latitude, o.delivery_longitude, o.expected_ready_time,
                   o.order_status, o.order_placed_at,
                   c.full_name as chef_name, c.address as chef_address,
                   c.latitude as chef_latitude, c.longitude as chef_longitude,
                   c.phone as chef_phone,
                   consumer.full_name as consumer_name, consumer.phone as consumer_phone,
                   consumer.latitude as consumer_lat, consumer.longitude as consumer_lon
            FROM orders o
            JOIN users c ON o.chef_id = c.id
            JOIN users consumer ON o.consumer_id = consumer.id
            WHERE o.delivery_agent_id = ?
            AND o.order_status NOT IN ('delivered', 'cancelled')
            ORDER BY o.order_placed_at ASC
        ''', (user_id,))
        
        # Helper function to calculate distance (Haversine)
        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 3959  # Earth's radius in miles
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        
        orders = []
        for row in cursor.fetchall():
            # Calculate distances
            da_to_chef_distance = round(calculate_distance(
                da_lat, da_lon,
                row['chef_latitude'], row['chef_longitude']
            ), 2)
            
            chef_to_consumer_distance = round(calculate_distance(
                row['chef_latitude'], row['chef_longitude'],
                row['consumer_lat'], row['consumer_lon']
            ), 2)
            
            # Calculate ETA
            eta_minutes = None
            status_text = row['order_status'].replace('_', ' ').title()
            if row['expected_ready_time']:
                from datetime import datetime
                ready_time = datetime.fromisoformat(row['expected_ready_time'])
                now = datetime.now()
                if ready_time > now:
                    eta_minutes = int((ready_time - now).total_seconds() / 60)
                    status_text = f"{status_text} (Ready in {eta_minutes} min)"
                else:
                    status_text = f"{status_text} (Ready now!)"
            
            orders.append({
                'id': row['id'],
                'order_number': row['order_number'],
                'chef_name': row['chef_name'],
                'chef_address': row['chef_address'],
                'chef_phone': row['chef_phone'],
                'chef_latitude': row['chef_latitude'],
                'chef_longitude': row['chef_longitude'],
                'consumer_name': row['consumer_name'],
                'consumer_phone': row['consumer_phone'],
                'delivery_address': row['delivery_address'],
                'delivery_latitude': row['delivery_latitude'],
                'delivery_longitude': row['delivery_longitude'],
                'order_status': row['order_status'],
                'status_text': status_text,
                'da_to_chef_distance': da_to_chef_distance,
                'chef_to_consumer_distance': chef_to_consumer_distance,
                'eta_minutes': eta_minutes,
                'total_amount': row['total_amount']
            })
        
        conn.close()
        return jsonify({'orders': orders})
        
    except Exception as e:
        print(f"Error fetching active orders: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500