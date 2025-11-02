"""
Consumer routes for Potluck app
Handles dish browsing, ordering, favorites, and ratings
"""

from flask import Blueprint, request, jsonify
import sqlite3
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from middleware.auth import require_auth, require_role
from config.database import DatabaseConnection

bp = Blueprint('consumer', __name__)

def get_db_connection():
    """Helper function to get database connection"""
    import sqlite3
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'potluck.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/profile')
@require_auth
@require_role('consumer')
def get_profile(user_id):
    """Get consumer profile"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, full_name, phone, address, city, state, zip_code,
                   latitude, longitude, consumer_rating, total_orders_placed,
                   dietary_preferences, profile_image
            FROM users
            WHERE id = ? AND user_type = 'consumer'
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'profile': dict(user)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/dishes')
@require_auth
def get_dishes(user_id):
    """Get available dishes with chef information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user location
        cursor.execute('SELECT latitude, longitude, zip_code FROM users WHERE id = ?', (user_id,))
        user_location = cursor.fetchone()
        
        # Get all active dishes with chef info
        cursor.execute('''
            SELECT 
                d.id, d.name, d.description, d.price, d.cuisine_type, d.meal_type,
                d.ingredients, d.allergens, d.dietary_tags, d.spice_level,
                d.portion_size, d.calories, d.preparation_time, d.rating as dish_rating,
                d.total_orders, d.image_url,
                u.id as chef_id, u.full_name as chef_name, u.chef_rating,
                u.city, u.state, u.zip_code, u.latitude, u.longitude,
                u.chef_bio, u.chef_specialties
            FROM dishes d
            JOIN users u ON d.chef_id = u.id
            WHERE d.is_available = 1 AND u.is_available = 1 AND u.is_active = 1
            ORDER BY d.rating DESC, d.total_orders DESC
        ''')
        
        dishes = []
        for row in cursor.fetchall():
            dish = dict(row)
            
            # Calculate distance if user location available
            if user_location and user_location['latitude'] and dish['latitude']:
                # Simple distance calculation (in real app, use proper geospatial functions)
                lat_diff = abs(user_location['latitude'] - dish['latitude'])
                lon_diff = abs(user_location['longitude'] - dish['longitude'])
                distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 69  # Rough miles
                dish['distance'] = round(distance, 1)
            else:
                dish['distance'] = None
            
            dish['area'] = f"{dish['city']}, {dish['state']}"
            dishes.append(dish)
        
        # Get unique chefs
        chefs = {}
        for dish in dishes:
            chef_id = dish['chef_id']
            if chef_id not in chefs:
                chefs[chef_id] = {
                    'id': chef_id,
                    'name': dish['chef_name'],
                    'rating': dish['chef_rating'],
                    'bio': dish['chef_bio'],
                    'specialties': dish['chef_specialties'],
                    'location': dish['area']
                }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'dishes': dishes,
            'chefs': list(chefs.values())
        })
        
    except Exception as e:
        print(f"Error getting dishes: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/orders', methods=['GET'])
@require_auth
@require_role('consumer')
def get_orders(user_id):
    """Get consumer orders"""
    try:
        status = request.args.get('status', 'all')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if status == 'active':
            cursor.execute('''
                SELECT o.*, u.full_name as chef_name, d.full_name as delivery_agent_name
                FROM orders o
                LEFT JOIN users u ON o.chef_id = u.id
                LEFT JOIN users d ON o.delivery_agent_id = d.id
                WHERE o.consumer_id = ? 
                AND o.order_status NOT IN ('delivered', 'cancelled')
                ORDER BY o.order_placed_at DESC
            ''', (user_id,))
        elif status == 'completed':
            cursor.execute('''
                SELECT o.*, u.full_name as chef_name, d.full_name as delivery_agent_name
                FROM orders o
                LEFT JOIN users u ON o.chef_id = u.id
                LEFT JOIN users d ON o.delivery_agent_id = d.id
                WHERE o.consumer_id = ? 
                AND o.order_status IN ('delivered', 'cancelled')
                ORDER BY o.order_placed_at DESC
                LIMIT 50
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT o.*, u.full_name as chef_name, d.full_name as delivery_agent_name
                FROM orders o
                LEFT JOIN users u ON o.chef_id = u.id
                LEFT JOIN users d ON o.delivery_agent_id = d.id
                WHERE o.consumer_id = ?
                ORDER BY o.order_placed_at DESC
            ''', (user_id,))
        
        orders = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON items and fetch dish names
        for order in orders:
            if 'items' in order and order['items']:
                items = json.loads(order['items']) if isinstance(order['items'], str) else order['items']
                # Enrich items with dish names
                for item in items:
                    cursor.execute("SELECT name FROM dishes WHERE id = ?", (item['dish_id'],))
                    dish = cursor.fetchone()
                    item['dish_name'] = dish['name'] if dish else f"Unknown Dish (ID: {item['dish_id']})"
                order['items'] = items
        
        conn.close()
        
        return jsonify({
            'success': True,
            'orders': orders
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/orders', methods=['POST'])
@require_auth
@require_role('consumer')
def create_order(user_id):
    """Create new order"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['items', 'chef_id', 'subtotal', 'total_amount', 'delivery_type']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the next order sequence number for today
        today = datetime.now().strftime('%Y%m%d')
        cursor.execute('''
            SELECT COUNT(*) FROM orders 
            WHERE order_number LIKE ?
        ''', (f'POT-{today}-%',))
        order_count = cursor.fetchone()[0] + 1
        
        # Generate order number
        order_number = f"POT-{today}-{order_count:04d}"
        
        # Create order
        cursor.execute('''
            INSERT INTO orders (
                order_number, consumer_id, chef_id, items, subtotal,
                delivery_fee, platform_fee, tax, total_amount,
                delivery_type, delivery_address, special_instructions,
                payment_method, order_status, order_placed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_number,
            user_id,
            data['chef_id'],
            json.dumps(data['items']),
            data['subtotal'],
            data.get('delivery_fee', 0),
            data.get('platform_fee', 0),
            data.get('tax', 0),
            data['total_amount'],
            data['delivery_type'],
            data.get('delivery_address', ''),
            data.get('special_instructions', ''),
            data.get('payment_method', 'cash'),
            'pending',
            datetime.now().isoformat()
        ))
        
        order_id = cursor.lastrowid
        
        # Create notification for chef
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['chef_id'],
            'New Order Received',
            f'You have a new order #{order_number}',
            'order',
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order_id': order_id,
            'order_number': order_number
        })
        
    except Exception as e:
        print(f"Error creating order: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/orders/<int:order_id>/rate', methods=['POST'])
@require_auth
@require_role('consumer')
def rate_order(user_id, order_id):
    """Rate order (food, chef, delivery agent) and add tip"""
    try:
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify order belongs to user
        cursor.execute('SELECT * FROM orders WHERE id = ? AND consumer_id = ?', (order_id, user_id))
        order = cursor.fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Create review
        cursor.execute('''
            INSERT INTO reviews (
                order_id, reviewer_id, chef_id, delivery_agent_id,
                food_rating, chef_rating, delivery_rating,
                comment, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_id,
            user_id,
            order['chef_id'],
            order['delivery_agent_id'],
            data.get('food_rating', 0),
            data.get('chef_rating', 0),
            data.get('delivery_rating', 0),
            data.get('review', ''),
            datetime.now()
        ))
        
        # Add tip if provided
        if data.get('tip', 0) > 0 and order['delivery_agent_id']:
            cursor.execute('''
                INSERT INTO earnings (user_id, order_id, amount, type, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                order['delivery_agent_id'],
                order_id,
                data['tip'],
                'tip',
                'processed',
                datetime.now()
            ))
        
        # Update ratings (simplified - in production, recalculate averages)
        # Update dish rating
        cursor.execute('''
            UPDATE dishes 
            SET rating = (rating * total_orders + ?) / (total_orders + 1)
            WHERE chef_id = ?
        ''', (data.get('food_rating', 0), order['chef_id']))
        
        # Update chef rating
        cursor.execute('''
            UPDATE users 
            SET chef_rating = (COALESCE(chef_rating, 0) * COALESCE(total_dishes_sold, 0) + ?) / (COALESCE(total_dishes_sold, 0) + 1)
            WHERE id = ?
        ''', (data.get('chef_rating', 0), order['chef_id']))
        
        # Update delivery agent rating
        if order['delivery_agent_id']:
            cursor.execute('''
                UPDATE users 
                SET delivery_rating = (COALESCE(delivery_rating, 0) * COALESCE(total_deliveries, 0) + ?) / (COALESCE(total_deliveries, 0) + 1)
                WHERE id = ?
            ''', (data.get('delivery_rating', 0), order['delivery_agent_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully'
        })
        
    except Exception as e:
        print(f"Error rating order: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/favorites', methods=['GET'])
@require_auth
@require_role('consumer')
def get_favorites(user_id):
    """Get user's favorite dishes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.*, d.name as dish_name, d.price, d.image_url,
                   u.full_name as chef_name
            FROM favorites f
            JOIN dishes d ON f.dish_id = d.id
            JOIN users u ON f.chef_id = u.id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
        ''', (user_id,))
        
        favorites = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'favorites': favorites
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/favorites', methods=['POST'])
@require_auth
@require_role('consumer')
def add_favorite(user_id):
    """Add dish to favorites"""
    try:
        data = request.json
        dish_id = data.get('dish_id')
        
        if not dish_id:
            return jsonify({'error': 'dish_id required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get chef_id for the dish
        cursor.execute('SELECT chef_id FROM dishes WHERE id = ?', (dish_id,))
        dish = cursor.fetchone()
        
        if not dish:
            return jsonify({'error': 'Dish not found'}), 404
        
        # Add to favorites
        cursor.execute('''
            INSERT OR IGNORE INTO favorites (user_id, dish_id, chef_id, created_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, dish_id, dish['chef_id'], datetime.now()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Added to favorites'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/favorites/<int:dish_id>', methods=['DELETE'])
@require_auth
@require_role('consumer')
def remove_favorite(user_id, dish_id):
    """Remove dish from favorites"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM favorites WHERE user_id = ? AND dish_id = ?', (user_id, dish_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Removed from favorites'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/notifications', methods=['GET'])
@require_auth
@require_role('consumer')
def get_notifications(user_id):
    """Get user notifications"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        ''', (user_id,))
        
        notifications = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'notifications': notifications
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/notifications/<int:notif_id>/read', methods=['PUT'])
@require_auth
@require_role('consumer')
def mark_notification_read(user_id, notif_id):
    """Mark notification as read"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET is_read = 1
            WHERE id = ? AND user_id = ?
        ''', (notif_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
