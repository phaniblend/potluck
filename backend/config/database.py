"""
Database configuration and connection utilities
"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional, Any
import json

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'potluck.db')
print(f"Database path: {DB_PATH}")
class DatabaseConnection:
    """Database connection manager"""
    
    @staticmethod
    @contextmanager
    def get_db():
        """Get database connection with context manager"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = DatabaseConnection.dict_factory
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        try:
            yield conn
        finally:
            conn.close()
    
    @staticmethod
    def dict_factory(cursor, row):
        """Convert database rows to dictionaries"""
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}
    
    @staticmethod
    def execute_query(query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results"""
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    @staticmethod
    def execute_one(query: str, params: tuple = None) -> Optional[Dict]:
        """Execute SELECT query and return single result"""
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
    
    @staticmethod
    def execute_insert(query: str, params: tuple) -> int:
        """Execute INSERT query and return last inserted ID"""
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def execute_update(query: str, params: tuple) -> int:
        """Execute UPDATE/DELETE query and return affected rows"""
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    @staticmethod
    def execute_many(query: str, params_list: List[tuple]) -> int:
        """Execute multiple queries with different parameters"""
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount


class DatabaseHelper:
    """Helper functions for common database operations"""
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        return DatabaseConnection.execute_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        """Get user by email"""
        return DatabaseConnection.execute_one(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
    
    @staticmethod
    def get_user_by_phone(phone: str) -> Optional[Dict]:
        """Get user by phone"""
        return DatabaseConnection.execute_one(
            "SELECT * FROM users WHERE phone = ?",
            (phone,)
        )
    
    @staticmethod
    def create_user(user_data: Dict) -> int:
        """Create new user"""
        columns = ', '.join(user_data.keys())
        placeholders = ', '.join(['?' for _ in user_data])
        query = f"INSERT INTO users ({columns}) VALUES ({placeholders})"
        return DatabaseConnection.execute_insert(query, tuple(user_data.values()))
    
    @staticmethod
    def update_user(user_id: int, updates: Dict) -> bool:
        """Update user data"""
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE users SET {set_clause} WHERE id = ?"
        params = tuple(list(updates.values()) + [user_id])
        return DatabaseConnection.execute_update(query, params) > 0
    
    @staticmethod
    def get_dishes_by_chef(chef_id: int, available_only: bool = True) -> List[Dict]:
        """Get dishes by chef"""
        query = "SELECT * FROM dishes WHERE chef_id = ?"
        if available_only:
            query += " AND is_available = 1"
        query += " ORDER BY created_at DESC"
        return DatabaseConnection.execute_query(query, (chef_id,))
    
    @staticmethod
    def get_nearby_chefs(latitude: float, longitude: float, radius_km: float = 5) -> List[Dict]:
        """Get chefs within radius using Haversine formula"""
        # Simplified distance calculation for SQLite
        # In production, consider using PostGIS or similar
        query = """
            SELECT *, 
                   (6371 * acos(cos(radians(?)) * cos(radians(latitude)) * 
                   cos(radians(longitude) - radians(?)) + 
                   sin(radians(?)) * sin(radians(latitude)))) AS distance
            FROM users
            WHERE user_type = 'chef' 
              AND is_active = 1
              AND is_available = 1
            HAVING distance < ?
            ORDER BY distance
        """
        return DatabaseConnection.execute_query(
            query, 
            (latitude, longitude, latitude, radius_km)
        )
    
    @staticmethod
    def create_order(order_data: Dict) -> int:
        """Create new order"""
        # Generate order number
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        
        # Get today's order count
        count_query = "SELECT COUNT(*) as count FROM orders WHERE order_number LIKE ?"
        result = DatabaseConnection.execute_one(count_query, (f'POT-{date_str}-%',))
        count = result['count'] + 1 if result else 1
        
        order_data['order_number'] = f'POT-{date_str}-{count:04d}'
        
        # Convert items list to JSON
        if 'items' in order_data and isinstance(order_data['items'], list):
            order_data['items'] = json.dumps(order_data['items'])
        
        columns = ', '.join(order_data.keys())
        placeholders = ', '.join(['?' for _ in order_data])
        query = f"INSERT INTO orders ({columns}) VALUES ({placeholders})"
        return DatabaseConnection.execute_insert(query, tuple(order_data.values()))
    
    @staticmethod
    def update_order_status(order_id: int, status: str, user_id: int, notes: str = None) -> bool:
        """Update order status and log history"""
        with DatabaseConnection.get_db() as conn:
            cursor = conn.cursor()
            
            # Update order status
            cursor.execute(
                "UPDATE orders SET order_status = ? WHERE id = ?",
                (status, order_id)
            )
            
            # Log status change
            cursor.execute(
                """INSERT INTO order_status_history 
                   (order_id, status, changed_by, notes) 
                   VALUES (?, ?, ?, ?)""",
                (order_id, status, user_id, notes)
            )
            
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def get_active_orders_for_chef(chef_id: int) -> List[Dict]:
        """Get active orders for a chef"""
        query = """
            SELECT o.*, u.full_name as consumer_name, u.phone as consumer_phone
            FROM orders o
            JOIN users u ON o.consumer_id = u.id
            WHERE o.chef_id = ? 
              AND o.order_status IN ('pending', 'accepted', 'preparing', 'ready')
            ORDER BY o.order_placed_at DESC
        """
        return DatabaseConnection.execute_query(query, (chef_id,))
    
    @staticmethod
    def get_available_deliveries(latitude: float, longitude: float, radius_km: float = 5) -> List[Dict]:
        """Get available delivery jobs within radius"""
        query = """
            SELECT o.*, 
                   c.full_name as chef_name,
                   c.address as pickup_address,
                   c.latitude as pickup_lat,
                   c.longitude as pickup_lng,
                   (6371 * acos(cos(radians(?)) * cos(radians(c.latitude)) * 
                   cos(radians(c.longitude) - radians(?)) + 
                   sin(radians(?)) * sin(radians(c.latitude)))) AS distance
            FROM orders o
            JOIN users c ON o.chef_id = c.id
            WHERE o.order_status = 'ready'
              AND o.delivery_type = 'delivery'
              AND o.delivery_agent_id IS NULL
            HAVING distance < ?
            ORDER BY distance
        """
        return DatabaseConnection.execute_query(
            query,
            (latitude, longitude, latitude, radius_km)
        )
    
    @staticmethod
    def assign_delivery_agent(order_id: int, agent_id: int) -> bool:
        """Assign delivery agent to order"""
        query = """
            UPDATE orders 
            SET delivery_agent_id = ?, 
                order_status = 'picked_up'
            WHERE id = ? 
              AND delivery_agent_id IS NULL
        """
        return DatabaseConnection.execute_update(query, (agent_id, order_id)) > 0
    
    @staticmethod
    def get_user_stats(user_id: int, user_type: str) -> Dict:
        """Get statistics for user based on type"""
        stats = {}
        
        if user_type == 'chef':
            # Chef statistics
            orders = DatabaseConnection.execute_one(
                """SELECT COUNT(*) as total_orders, 
                          SUM(total_amount) as total_revenue,
                          AVG(chef_rating) as avg_rating
                   FROM orders 
                   WHERE chef_id = ? AND order_status = 'delivered'""",
                (user_id,)
            )
            
            dishes = DatabaseConnection.execute_one(
                "SELECT COUNT(*) as total_dishes FROM dishes WHERE chef_id = ?",
                (user_id,)
            )
            
            stats = {
                'total_orders': orders['total_orders'] or 0,
                'total_revenue': orders['total_revenue'] or 0,
                'average_rating': round(orders['avg_rating'] or 0, 1),
                'total_dishes': dishes['total_dishes'] or 0
            }
            
        elif user_type == 'delivery':
            # Delivery agent statistics
            deliveries = DatabaseConnection.execute_one(
                """SELECT COUNT(*) as total_deliveries,
                          SUM(delivery_fee) as total_earnings,
                          AVG(delivery_rating) as avg_rating
                   FROM orders 
                   WHERE delivery_agent_id = ? AND order_status = 'delivered'""",
                (user_id,)
            )
            
            stats = {
                'total_deliveries': deliveries['total_deliveries'] or 0,
                'total_earnings': deliveries['total_earnings'] or 0,
                'average_rating': round(deliveries['avg_rating'] or 0, 1)
            }
            
        elif user_type == 'consumer':
            # Consumer statistics
            orders = DatabaseConnection.execute_one(
                """SELECT COUNT(*) as total_orders,
                          SUM(total_amount) as total_spent
                   FROM orders 
                   WHERE consumer_id = ?""",
                (user_id,)
            )
            
            favorites = DatabaseConnection.execute_one(
                "SELECT COUNT(*) as total_favorites FROM favorites WHERE user_id = ?",
                (user_id,)
            )
            
            stats = {
                'total_orders': orders['total_orders'] or 0,
                'total_spent': orders['total_spent'] or 0,
                'total_favorites': favorites['total_favorites'] or 0
            }
        
        return stats
    
    @staticmethod
    def search_dishes(query: str, filters: Dict = None) -> List[Dict]:
        """Search dishes with filters"""
        search_query = """
            SELECT d.*, u.full_name as chef_name, u.rating as chef_rating
            FROM dishes d
            JOIN users u ON d.chef_id = u.id
            WHERE d.is_available = 1
              AND u.is_available = 1
        """
        
        params = []
        
        # Add search term
        if query:
            search_query += """ AND (d.name LIKE ? OR d.description LIKE ? 
                                   OR d.cuisine_type LIKE ? OR u.full_name LIKE ?)"""
            search_term = f'%{query}%'
            params.extend([search_term] * 4)
        
        # Add filters
        if filters:
            if filters.get('cuisine'):
                search_query += " AND d.cuisine_type = ?"
                params.append(filters['cuisine'])
            
            if filters.get('meal_type'):
                search_query += " AND d.meal_type = ?"
                params.append(filters['meal_type'])
            
            if filters.get('max_price'):
                search_query += " AND d.price <= ?"
                params.append(filters['max_price'])
            
            if filters.get('dietary_tags'):
                # Check if dietary tags contain required tags
                for tag in filters['dietary_tags']:
                    search_query += " AND d.dietary_tags LIKE ?"
                    params.append(f'%{tag}%')
        
        search_query += " ORDER BY d.rating DESC, d.total_orders DESC LIMIT 50"
        
        return DatabaseConnection.execute_query(search_query, tuple(params))


# Create singleton instance
db = DatabaseConnection()
db_helper = DatabaseHelper()