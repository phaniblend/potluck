"""
Chef routes for Potluck app
Handles dish management, orders, earnings, and AI price suggestions
"""

from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import DatabaseHelper, DatabaseConnection
from middleware.auth import require_auth, require_role
from utils.price_advisor import PriceAdvisor
import json
from datetime import datetime

bp = Blueprint('chef', __name__)
price_advisor = PriceAdvisor()


def get_currency_for_location(city, state):
    """Get currency info based on location"""
    city_lower = (city or '').lower()
    state_upper = (state or '').upper()
    
    # India
    if state_upper in ['MH', 'DL', 'KA', 'TN', 'GJ', 'RJ', 'UP', 'WB', 'AP', 'TS']:
        return {
            'code': 'INR',
            'symbol': '₹',
            'name': 'Indian Rupee'
        }
    
    # Mexico
    if state_upper in ['CDMX', 'JAL', 'NL', 'BCN', 'QRO', 'PUE']:
        return {
            'code': 'MXN',
            'symbol': '$',
            'name': 'Mexican Peso'
        }
    
    # Canada
    if state_upper in ['ON', 'QC', 'BC', 'AB']:
        return {
            'code': 'CAD',
            'symbol': '$',
            'name': 'Canadian Dollar'
        }
    
    # UK (if we add it)
    if 'london' in city_lower or 'manchester' in city_lower:
        return {
            'code': 'GBP',
            'symbol': '£',
            'name': 'British Pound'
        }
    
    # Default: USD (USA and others)
    return {
        'code': 'USD',
        'symbol': '$',
        'name': 'US Dollar'
    }


@bp.route('/dashboard', methods=['GET'])
@require_auth
@require_role('chef')
def get_dashboard(current_user_id):
    """Get chef dashboard data with stats and analytics"""
    try:
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            
            # Get chef details
            cursor.execute("SELECT * FROM users WHERE id = ?", (current_user_id,))
            chef = cursor.fetchone()
            
            if not chef:
                return jsonify({'success': False, 'error': 'Chef not found'}), 404
            
            # Get dish count
            cursor.execute("""
                SELECT COUNT(*) as count, SUM(CASE WHEN is_available = 1 THEN 1 ELSE 0 END) as active_count
                FROM dishes WHERE chef_id = ?
            """, (current_user_id,))
            dish_stats = cursor.fetchone()
            
            # Get order statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(CASE WHEN order_status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
                    SUM(CASE WHEN order_status IN ('delivered', 'completed') THEN 1 ELSE 0 END) as completed_orders,
                    SUM(CASE WHEN order_status IN ('delivered', 'completed') THEN total_amount ELSE 0 END) as total_earnings
                FROM orders 
                WHERE chef_id = ?
            """, (current_user_id,))
            order_stats = cursor.fetchone()
            
            # Get rating statistics
            cursor.execute("""
                SELECT AVG(chef_rating) as avg_rating, COUNT(chef_rating) as rating_count
                FROM orders 
                WHERE chef_id = ? AND chef_rating IS NOT NULL
            """, (current_user_id,))
            rating_stats = cursor.fetchone()
            
            # Get recent reviews
            cursor.execute("""
                SELECT o.chef_review, o.chef_rating, o.order_number, o.delivered_at, u.full_name as customer_name
                FROM orders o
                LEFT JOIN users u ON o.consumer_id = u.id
                WHERE o.chef_id = ? AND o.chef_review IS NOT NULL
                ORDER BY o.delivered_at DESC
                LIMIT 5
            """, (current_user_id,))
            recent_reviews = cursor.fetchall()
            
            # Determine currency based on location
            currency_info = get_currency_for_location(chef['city'], chef['state'])
            
            return jsonify({
                'success': True,
                'data': {
                    'chef': {
                        'id': chef['id'],
                        'name': chef['full_name'],
                        'email': chef['email'],
                        'city': chef['city'],
                        'state': chef['state'],
                        'rating': chef['chef_rating'] or 0,
                        'bio': chef['chef_bio'],
                        'specialties': json.loads(chef['chef_specialties'] or '[]')
                    },
                    'stats': {
                        'total_dishes': dish_stats['count'] or 0,
                        'active_dishes': dish_stats['active_count'] or 0,
                        'total_orders': order_stats['total_orders'] or 0,
                        'pending_orders': order_stats['pending_orders'] or 0,
                        'completed_orders': order_stats['completed_orders'] or 0,
                        'total_earnings': float(order_stats['total_earnings'] or 0),
                        'avg_rating': round(float(rating_stats['avg_rating'] or 0), 1),
                        'rating_count': rating_stats['rating_count'] or 0
                    },
                    'recent_reviews': recent_reviews,
                    'currency': currency_info
                }
            })
            
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/dishes', methods=['GET'])
@require_auth
@require_role('chef')
def get_dishes(current_user_id):
    """Get all dishes for current chef"""
    try:
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.*, 
                       COUNT(DISTINCT o.id) as order_count,
                       AVG(o.chef_rating) as avg_rating
                FROM dishes d
                LEFT JOIN orders o ON d.id IN (
                    SELECT json_extract(value, '$.dish_id')
                    FROM orders, json_each(orders.items)
                    WHERE orders.chef_id = d.chef_id
                )
                WHERE d.chef_id = ?
                GROUP BY d.id
                ORDER BY d.created_at DESC
            """, (current_user_id,))
            
            dishes = cursor.fetchall()
            
            # Parse JSON fields
            for dish in dishes:
                dish['ingredients'] = json.loads(dish['ingredients'] or '[]')
                dish['allergens'] = json.loads(dish['allergens'] or '[]')
                dish['dietary_tags'] = json.loads(dish['dietary_tags'] or '[]')
            
            return jsonify({
                'success': True,
                'data': dishes
            })
            
    except Exception as e:
        print(f"Get dishes error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/dishes', methods=['POST'])
@require_auth
@require_role('chef')
def add_dish(current_user_id):
    """Add a new dish"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['name', 'description', 'price', 'cuisine_type', 'meal_type', 
                   'ingredients', 'portion_size']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Validate price
        price = float(data['price'])
        if price <= 0:
            return jsonify({'success': False, 'error': 'Price must be greater than 0'}), 400
        
        # Get AI price suggestion for validation
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city, state, total_dishes_sold, chef_rating FROM users WHERE id = ?", (current_user_id,))
            chef = cursor.fetchone()
            
            dish_data = {
                'name': data['name'],
                'cuisine': data['cuisine_type'],
                'ingredients': data.get('ingredients', []),
                'portion_size': data['portion_size'],
                'location': f"{chef['city']}, {chef['state']}",
                'currency': 'USD',
                'currency_symbol': '$',
                'chef_experience': 'intermediate' if (chef['total_dishes_sold'] or 0) > 10 else 'new'
            }
            
            # Get AI recommendation
            ai_suggestion = price_advisor.get_price_suggestion(dish_data)
            
            if ai_suggestion['success']:
                pricing = ai_suggestion['pricing']
                max_price = pricing['max_price']
                suggested_price = pricing['suggested_price']
                min_price = pricing['min_price']
                
                # Get cost breakdown for detailed explanation
                breakdown = pricing.get('breakdown', {})
                ingredients_cost = breakdown.get('ingredients', 0)
                
                # Check if price is way above AI recommendation
                if price > max_price * 2:
                    # Analyze ingredients for expensive items
                    ingredients_list = data.get('ingredients', [])
                    expensive_ingredients = ['caviar', 'truffle', 'lobster', 'wagyu', 'saffron', 'kobe', 'foie gras']
                    has_expensive = any(exp_ing in ' '.join(ingredients_list).lower() for exp_ing in expensive_ingredients)
                    
                    # Create contextual message
                    dish_name = data['name']
                    ingredients_str = ', '.join(ingredients_list[:3])  # First 3 ingredients
                    if len(ingredients_list) > 3:
                        ingredients_str += '...'
                    
                    # Build detailed explanation
                    if has_expensive:
                        explanation = f"While {dish_name} contains premium ingredients, ${price:.2f} is still significantly above market rates for homemade food."
                    else:
                        explanation = f"${price:.2f} for {dish_name} ({ingredients_str}) is {int((price/suggested_price - 1)*100)}% above typical market rates."
                    
                    # Price is more than 2x the maximum recommended
                    return jsonify({
                        'success': False,
                        'error': 'Price validation failed',
                        'price_rejection': {
                            'dish_name': dish_name,
                            'your_price': price,
                            'suggested': suggested_price,
                            'min': min_price,
                            'max': max_price,
                            'explanation': explanation,
                            'breakdown': {
                                'ingredients_cost': ingredients_cost,
                                'total_cost': breakdown.get('total_cost', 0),
                                'margin': breakdown.get('margin', 0)
                            },
                            'has_premium_ingredients': has_expensive,
                            'reasoning': ai_suggestion.get('reasoning', '')
                        }
                    }), 400
                elif price > max_price * 1.5:
                    # Warning but allow (between 1.5x and 2x max)
                    print(f"⚠️ Warning: Chef set price ${price:.2f} which is {int((price/max_price)*100)}% of AI max (${max_price:.2f})")
        
        # Insert dish
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dishes (
                    chef_id, name, description, price, cuisine_type, meal_type,
                    ingredients, allergens, dietary_tags, spice_level, portion_size,
                    calories, preparation_time, is_available
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                current_user_id,
                data['name'],
                data['description'],
                data['price'],
                data['cuisine_type'],
                data['meal_type'],
                json.dumps(data.get('ingredients', [])),
                json.dumps(data.get('allergens', [])),
                json.dumps(data.get('dietary_tags', [])),
                data.get('spice_level', 1),
                data['portion_size'],
                data.get('calories'),
                data.get('preparation_time', 30),
                data.get('is_available', 1)
            ))
            conn.commit()
            dish_id = cursor.lastrowid
            
            return jsonify({
                'success': True,
                'message': 'Dish added successfully!',
                'dish_id': dish_id
            })
            
    except Exception as e:
        print(f"Add dish error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/dishes/<int:dish_id>', methods=['PUT'])
@require_auth
@require_role('chef')
def update_dish(current_user_id, dish_id):
    """Update an existing dish"""
    try:
        data = request.json
        
        # Verify dish belongs to chef
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chef_id FROM dishes WHERE id = ?", (dish_id,))
            dish = cursor.fetchone()
            
            if not dish:
                return jsonify({'success': False, 'error': 'Dish not found'}), 404
            
            if dish['chef_id'] != current_user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            # Build update query dynamically
            updates = []
            params = []
            
            allowed_fields = ['name', 'description', 'price', 'cuisine_type', 'meal_type',
                            'spice_level', 'portion_size', 'calories', 'preparation_time', 
                            'is_available']
            
            for field in allowed_fields:
                if field in data:
                    updates.append(f"{field} = ?")
                    params.append(data[field])
            
            # Handle JSON fields
            if 'ingredients' in data:
                updates.append("ingredients = ?")
                params.append(json.dumps(data['ingredients']))
            if 'allergens' in data:
                updates.append("allergens = ?")
                params.append(json.dumps(data['allergens']))
            if 'dietary_tags' in data:
                updates.append("dietary_tags = ?")
                params.append(json.dumps(data['dietary_tags']))
            
            if not updates:
                return jsonify({'success': False, 'error': 'No fields to update'}), 400
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(dish_id)
            
            query = f"UPDATE dishes SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, tuple(params))
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Dish updated successfully!'
            })
            
    except Exception as e:
        print(f"Update dish error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/dishes/<int:dish_id>', methods=['DELETE'])
@require_auth
@require_role('chef')
def delete_dish(current_user_id, dish_id):
    """Delete a dish"""
    try:
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            
            # Verify dish belongs to chef
            cursor.execute("SELECT chef_id FROM dishes WHERE id = ?", (dish_id,))
            dish = cursor.fetchone()
            
            if not dish:
                return jsonify({'success': False, 'error': 'Dish not found'}), 404
            
            if dish['chef_id'] != current_user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            # Soft delete (just mark as unavailable) or hard delete
            cursor.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Dish deleted successfully!'
            })
            
    except Exception as e:
        print(f"Delete dish error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/price-suggestion', methods=['POST'])
@require_auth
@require_role('chef')
def get_price_suggestion(current_user_id):
    """Get AI-powered price suggestion for a dish"""
    try:
        data = request.json
        
        # Get chef location
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city, state FROM users WHERE id = ?", (current_user_id,))
            chef = cursor.fetchone()
            
            if not chef:
                return jsonify({'success': False, 'error': 'Chef not found'}), 404
            
            # Prepare dish data for AI
            dish_data = {
                'name': data.get('name', ''),
                'cuisine': data.get('cuisine_type', ''),
                'ingredients': data.get('ingredients', []),
                'portion_size': data.get('portion_size', ''),
                'location': f"{chef['city']}, {chef['state']}",
                'currency': 'USD',
                'currency_symbol': '$',
                'chef_experience': 'intermediate'  # Can be dynamic based on chef stats
            }
            
            # Get similar dishes for comparison
            cursor.execute("""
                SELECT name, price, cuisine_type, AVG(chef_rating) as avg_rating,
                       COUNT(*) as order_count
                FROM dishes d
                LEFT JOIN orders o ON d.id IN (
                    SELECT json_extract(value, '$.dish_id')
                    FROM orders, json_each(orders.items)
                )
                WHERE d.cuisine_type = ? AND d.is_available = 1
                GROUP BY d.id
                ORDER BY order_count DESC
                LIMIT 5
            """, (data.get('cuisine_type', ''),))
            similar_dishes = cursor.fetchall()
            
            # Get AI suggestion
            suggestion = price_advisor.get_price_suggestion(dish_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'ai_suggestion': suggestion,
                    'similar_dishes': similar_dishes,
                    'market_insights': {
                        'popular_cuisines': ['Mexican', 'Indian', 'Italian'],  # Can be from DB
                        'trending_dishes': ['Tacos', 'Biryani', 'Pasta']  # Can be from DB
                    }
                }
            })
            
    except Exception as e:
        print(f"Price suggestion error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/orders', methods=['GET'])
@require_auth
@require_role('chef')
def get_orders(current_user_id):
    """Get all orders for chef"""
    try:
        status_filter = request.args.get('status', 'all')  # all, pending, completed
        
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT o.*, 
                       u.full_name as customer_name, 
                       u.phone as customer_phone,
                       u.address as customer_address
                FROM orders o
                LEFT JOIN users u ON o.consumer_id = u.id
                WHERE o.chef_id = ?
            """
            
            if status_filter == 'pending':
                query += " AND o.order_status IN ('pending', 'accepted', 'preparing')"
            elif status_filter == 'completed':
                query += " AND o.order_status IN ('delivered', 'completed')"
            
            query += " ORDER BY o.order_placed_at DESC"
            
            cursor.execute(query, (current_user_id,))
            orders = cursor.fetchall()
            
            # Parse JSON items
            for order in orders:
                order['items'] = json.loads(order['items'] or '[]')
            
            return jsonify({
                'success': True,
                'data': orders
            })
            
    except Exception as e:
        print(f"Get orders error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@require_auth
@require_role('chef')
def update_order_status(current_user_id, order_id):
    """Update order status"""
    try:
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'error': 'Status is required'}), 400
        
        valid_statuses = ['accepted', 'preparing', 'ready', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            
            # Verify order belongs to chef
            cursor.execute("SELECT chef_id FROM orders WHERE id = ?", (order_id,))
            order = cursor.fetchone()
            
            if not order:
                return jsonify({'success': False, 'error': 'Order not found'}), 404
            
            if order['chef_id'] != current_user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            # Update status
            cursor.execute("""
                UPDATE orders 
                SET order_status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_status, order_id))
            
            # Add to status history
            cursor.execute("""
                INSERT INTO order_status_history (order_id, status, changed_by, notes)
                VALUES (?, ?, ?, ?)
            """, (order_id, new_status, current_user_id, data.get('notes', '')))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': f'Order status updated to {new_status}'
            })
            
    except Exception as e:
        print(f"Update order status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/feedback', methods=['GET'])
@require_auth
@require_role('chef')
def get_feedback(current_user_id):
    """Get customer feedback and reviews"""
    try:
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    o.id as order_id,
                    o.order_number,
                    o.chef_rating,
                    o.chef_review,
                    o.delivered_at,
                    u.full_name as customer_name,
                    o.items
                FROM orders o
                LEFT JOIN users u ON o.consumer_id = u.id
                WHERE o.chef_id = ? 
                AND (o.chef_rating IS NOT NULL OR o.chef_review IS NOT NULL)
                ORDER BY o.delivered_at DESC
                LIMIT 50
            """, (current_user_id,))
            
            feedback = cursor.fetchall()
            
            # Parse items to show which dishes were rated
            for item in feedback:
                item['items'] = json.loads(item['items'] or '[]')
            
            return jsonify({
                'success': True,
                'data': feedback
            })
            
    except Exception as e:
        print(f"Get feedback error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
