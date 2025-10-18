#!/usr/bin/env python3
"""
Test Data Seeder for Potluck Database
Populates all tables with realistic test data for development and testing
"""

import sqlite3
import json
import bcrypt
import random
from datetime import datetime, timedelta
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'potluck.db')

def hash_password(password):
    """Hash password using bcrypt (same as backend)"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def generate_order_number():
    """Generate order number like POT-20241015-0001"""
    today = datetime.now().strftime('%Y%m%d')
    return f"POT-{today}-{random.randint(1000, 9999)}"

def seed_database():
    """Populate database with test data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Seeding database with test data...")
    
    # Clear existing data (except schema)
    tables_to_clear = [
        'delivery_verification', 'service_areas', 'chef_availability', 'earnings',
        'notifications', 'favorites', 'delivery_tracking', 'messages', 'reviews',
        'order_status_history', 'orders', 'dishes', 'chef_agreements', 'users'
    ]
    
    for table in tables_to_clear:
        cursor.execute(f"DELETE FROM {table}")
    
    print("Cleared existing data")
    
    # 1. USERS - Create test users for all roles
    users_data = [
        # Consumers
        {
            'email': 'john.doe@email.com', 'phone': '+1234567890', 'password': 'password123',
            'full_name': 'John Doe', 'user_type': 'consumer', 'address': '123 Main St, Dallas, TX 75201',
            'city': 'Dallas', 'state': 'TX', 'zip_code': '75201', 'latitude': 32.7767, 'longitude': -96.7970,
            'consumer_rating': 4.8, 'total_orders_placed': 15, 'dietary_preferences': '["vegetarian"]'
        },
        {
            'email': 'sarah.wilson@email.com', 'phone': '+1234567891', 'password': 'password123',
            'full_name': 'Sarah Wilson', 'user_type': 'consumer', 'address': '456 Oak Ave, Dallas, TX 75202',
            'city': 'Dallas', 'state': 'TX', 'zip_code': '75202', 'latitude': 32.7849, 'longitude': -96.8084,
            'consumer_rating': 4.9, 'total_orders_placed': 23, 'dietary_preferences': '["vegan", "gluten-free"]'
        },
        {
            'email': 'mike.chen@email.com', 'phone': '+1234567892', 'password': 'password123',
            'full_name': 'Mike Chen', 'user_type': 'consumer', 'address': '789 Pine St, Dallas, TX 75203',
            'city': 'Dallas', 'state': 'TX', 'zip_code': '75203', 'latitude': 32.7931, 'longitude': -96.8198,
            'consumer_rating': 4.7, 'total_orders_placed': 8, 'dietary_preferences': '[]'
        },
        
        # Chefs
        {
            'email': 'chef.maria@email.com', 'phone': '+1234567893', 'password': 'password123',
            'full_name': 'Maria Rodriguez', 'user_type': 'chef', 'address': '321 Chef Lane, Dallas, TX 75204',
            'city': 'Dallas', 'state': 'TX', 'zip_code': '75204', 'latitude': 32.8013, 'longitude': -96.8312,
            'chef_bio': 'Passionate home chef specializing in authentic Mexican cuisine',
            'chef_specialties': '["mexican", "tex-mex", "spicy"]', 'kitchen_type': 'home',
            'max_orders_per_day': 15, 'preparation_time': 45, 'is_available': 1,
            'chef_rating': 4.9, 'total_dishes_sold': 127
        },
        {
            'email': 'chef.raj@email.com', 'phone': '+1234567894', 'password': 'password123',
            'full_name': 'Raj Patel', 'user_type': 'chef', 'address': '654 Spice Street, Dallas, TX 75205',
            'city': 'Dallas', 'state': 'TX', 'zip_code': '75205', 'latitude': 32.8095, 'longitude': -96.8426,
            'chef_bio': 'Expert in Indian cuisine with 20 years of experience',
            'chef_specialties': '["indian", "vegetarian", "spicy"]', 'kitchen_type': 'home',
            'max_orders_per_day': 20, 'preparation_time': 60, 'is_available': 1,
            'chef_rating': 4.8, 'total_dishes_sold': 203
        },
        {
            'email': 'chef.anna@email.com', 'phone': '+1234567895', 'password': 'password123',
            'full_name': 'Anna Thompson', 'user_type': 'chef', 'address': '987 Garden Way, Dallas, TX 75206',
            'city': 'Dallas', 'state': 'TX', 'zip_code': '75206', 'latitude': 32.8177, 'longitude': -96.8540,
            'chef_bio': 'Farm-to-table specialist focusing on healthy, organic meals',
            'chef_specialties': '["american", "healthy", "organic"]', 'kitchen_type': 'home',
            'max_orders_per_day': 12, 'preparation_time': 30, 'is_available': 1,
            'chef_rating': 4.7, 'total_dishes_sold': 89
        },
        
        # Delivery Agents
        {
            'email': 'delivery.tom@email.com', 'phone': '+1234567896', 'password': 'password123',
            'full_name': 'Tom Johnson', 'user_type': 'delivery', 'address': '147 Delivery Blvd, Dallas, TX 75207',
            'city': 'Dallas', 'state': 'TX', 'zip_code': '75207', 'latitude': 32.8259, 'longitude': -96.8654,
            'vehicle_type': 'car', 'vehicle_number': 'TX-ABC123', 'driving_license': 'DL123456789',
            'delivery_radius': 10, 'current_status': 'online', 'delivery_rating': 4.9, 'total_deliveries': 156
        },
        {
            'email': 'delivery.lisa@email.com', 'phone': '+1234567897', 'password': 'password123',
            'full_name': 'Lisa Garcia', 'user_type': 'delivery', 'address': '258 Speed Lane, Dallas, TX 75208',
            'city': 'Dallas', 'state': 'TX', 'zip_code': '75208', 'latitude': 32.8341, 'longitude': -96.8768,
            'vehicle_type': 'bike', 'vehicle_number': 'BIKE-001', 'driving_license': 'DL987654321',
            'delivery_radius': 5, 'current_status': 'online', 'delivery_rating': 4.8, 'total_deliveries': 98
        },
        {
            'email': 'delivery.venkat@email.com', 'phone': '+1234567898', 'password': 'password123',
            'full_name': 'Venkat Kumar', 'user_type': 'delivery', 'address': '369 Fast Street, Dallas, TX 75209',
            'city': 'Dallas', 'state': 'TX', 'zip_code': '75209', 'latitude': 32.8423, 'longitude': -96.8882,
            'vehicle_type': 'scooter', 'vehicle_number': 'SCOOT-456', 'driving_license': 'DL456789123',
            'delivery_radius': 8, 'current_status': 'online', 'delivery_rating': 4.9, 'total_deliveries': 134
        }
    ]
    
    user_ids = {}
    for user in users_data:
        cursor.execute('''
            INSERT INTO users (email, phone, password_hash, full_name, user_type, is_active, is_verified,
                             address, city, state, zip_code, latitude, longitude, chef_bio, chef_specialties,
                             kitchen_type, max_orders_per_day, preparation_time, is_available, chef_rating,
                             total_dishes_sold, vehicle_type, vehicle_number, driving_license, delivery_radius,
                             current_status, delivery_rating, total_deliveries, consumer_rating,
                             total_orders_placed, dietary_preferences)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user['email'], user['phone'], hash_password(user['password']), user['full_name'], user['user_type'],
            1, 1, user['address'], user['city'], user['state'], user['zip_code'], user['latitude'], user['longitude'],
            user.get('chef_bio'), user.get('chef_specialties'), user.get('kitchen_type'),
            user.get('max_orders_per_day'), user.get('preparation_time'), user.get('is_available'),
            user.get('chef_rating'), user.get('total_dishes_sold'), user.get('vehicle_type'),
            user.get('vehicle_number'), user.get('driving_license'), user.get('delivery_radius'),
            user.get('current_status'), user.get('delivery_rating'), user.get('total_deliveries'),
            user.get('consumer_rating'), user.get('total_orders_placed'), user.get('dietary_preferences')
        ))
        user_ids[user['email']] = cursor.lastrowid
    
    print(f"Created {len(users_data)} users")
    
    # 2. CHEF AGREEMENTS
    chef_emails = ['chef.maria@email.com', 'chef.raj@email.com', 'chef.anna@email.com']
    for chef_email in chef_emails:
        cursor.execute('''
            INSERT INTO chef_agreements (chef_id, agreement_version, agreed_terms, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (
            user_ids[chef_email], 'v1.0', 
            json.dumps({'terms_accepted': True, 'privacy_policy': True, 'data_usage': True}),
            '127.0.0.1'
        ))
    
    print("Created chef agreements")
    
    # 3. DISHES - Create dishes for each chef
    dishes_data = [
        # Maria's Mexican dishes
        {
            'chef_email': 'chef.maria@email.com', 'name': 'Chicken Tacos', 'description': 'Authentic Mexican chicken tacos with fresh salsa',
            'price': 12.99, 'cuisine_type': 'mexican', 'meal_type': 'lunch', 'ingredients': '["chicken", "tortillas", "salsa", "onions", "cilantro"]',
            'allergens': '["gluten"]', 'dietary_tags': '["gluten-free"]', 'spice_level': 3, 'portion_size': '3 tacos',
            'calories': 450, 'preparation_time': 30, 'max_quantity_per_day': 20, 'rating': 4.8, 'total_orders': 45
        },
        {
            'chef_email': 'chef.maria@email.com', 'name': 'Beef Burrito', 'description': 'Large burrito with seasoned beef, rice, and beans',
            'price': 15.99, 'cuisine_type': 'mexican', 'meal_type': 'lunch', 'ingredients': '["beef", "rice", "beans", "cheese", "sour cream"]',
            'allergens': '["dairy", "gluten"]', 'dietary_tags': '[]', 'spice_level': 2, 'portion_size': '1 large burrito',
            'calories': 650, 'preparation_time': 25, 'max_quantity_per_day': 15, 'rating': 4.6, 'total_orders': 32
        },
        {
            'chef_email': 'chef.maria@email.com', 'name': 'Vegetarian Quesadilla', 'description': 'Cheese and vegetable quesadilla with guacamole',
            'price': 10.99, 'cuisine_type': 'mexican', 'meal_type': 'lunch', 'ingredients': '["cheese", "bell peppers", "onions", "tortilla", "guacamole"]',
            'allergens': '["dairy", "gluten"]', 'dietary_tags': '["vegetarian"]', 'spice_level': 1, 'portion_size': '2 quesadillas',
            'calories': 380, 'preparation_time': 20, 'max_quantity_per_day': 25, 'rating': 4.7, 'total_orders': 28
        },
        
        # Raj's Indian dishes
        {
            'chef_email': 'chef.raj@email.com', 'name': 'Chicken Curry', 'description': 'Spicy Indian chicken curry with basmati rice',
            'price': 16.99, 'cuisine_type': 'indian', 'meal_type': 'dinner', 'ingredients': '["chicken", "onions", "tomatoes", "spices", "coconut milk"]',
            'allergens': '[]', 'dietary_tags': '["gluten-free"]', 'spice_level': 4, 'portion_size': '1 serving with rice',
            'calories': 520, 'preparation_time': 45, 'max_quantity_per_day': 12, 'rating': 4.9, 'total_orders': 67
        },
        {
            'chef_email': 'chef.raj@email.com', 'name': 'Vegetable Biryani', 'description': 'Fragrant basmati rice with mixed vegetables and spices',
            'price': 14.99, 'cuisine_type': 'indian', 'meal_type': 'dinner', 'ingredients': '["basmati rice", "mixed vegetables", "spices", "saffron", "cashews"]',
            'allergens': '["nuts"]', 'dietary_tags': '["vegetarian", "vegan"]', 'spice_level': 3, 'portion_size': '1 large serving',
            'calories': 480, 'preparation_time': 40, 'max_quantity_per_day': 18, 'rating': 4.8, 'total_orders': 54
        },
        {
            'chef_email': 'chef.raj@email.com', 'name': 'Dal Tadka', 'description': 'Lentil curry with aromatic tempering',
            'price': 11.99, 'cuisine_type': 'indian', 'meal_type': 'dinner', 'ingredients': '["lentils", "onions", "garlic", "ginger", "spices"]',
            'allergens': '[]', 'dietary_tags': '["vegetarian", "vegan", "gluten-free"]', 'spice_level': 2, 'portion_size': '1 serving',
            'calories': 320, 'preparation_time': 35, 'max_quantity_per_day': 20, 'rating': 4.6, 'total_orders': 41
        },
        
        # Anna's American dishes
        {
            'chef_email': 'chef.anna@email.com', 'name': 'Grilled Salmon', 'description': 'Fresh Atlantic salmon with quinoa and roasted vegetables',
            'price': 18.99, 'cuisine_type': 'american', 'meal_type': 'dinner', 'ingredients': '["salmon", "quinoa", "broccoli", "carrots", "lemon"]',
            'allergens': '["fish"]', 'dietary_tags': '["gluten-free", "healthy"]', 'spice_level': 1, 'portion_size': '1 fillet with sides',
            'calories': 420, 'preparation_time': 25, 'max_quantity_per_day': 10, 'rating': 4.7, 'total_orders': 23
        },
        {
            'chef_email': 'chef.anna@email.com', 'name': 'Caesar Salad', 'description': 'Fresh romaine lettuce with homemade croutons and parmesan',
            'price': 9.99, 'cuisine_type': 'american', 'meal_type': 'lunch', 'ingredients': '["romaine lettuce", "croutons", "parmesan", "caesar dressing"]',
            'allergens': '["dairy", "gluten"]', 'dietary_tags': '["vegetarian"]', 'spice_level': 1, 'portion_size': '1 large salad',
            'calories': 280, 'preparation_time': 15, 'max_quantity_per_day': 30, 'rating': 4.5, 'total_orders': 19
        },
        {
            'chef_email': 'chef.anna@email.com', 'name': 'Veggie Wrap', 'description': 'Fresh vegetables in a whole wheat tortilla with hummus',
            'price': 8.99, 'cuisine_type': 'american', 'meal_type': 'lunch', 'ingredients': '["whole wheat tortilla", "hummus", "cucumber", "tomatoes", "lettuce"]',
            'allergens': '["gluten", "sesame"]', 'dietary_tags': '["vegetarian", "vegan", "healthy"]', 'spice_level': 1, 'portion_size': '1 large wrap',
            'calories': 350, 'preparation_time': 10, 'max_quantity_per_day': 25, 'rating': 4.4, 'total_orders': 16
        }
    ]
    
    dish_ids = {}
    for dish in dishes_data:
        cursor.execute('''
            INSERT INTO dishes (chef_id, name, description, price, cuisine_type, meal_type, ingredients,
                              allergens, dietary_tags, spice_level, portion_size, calories, preparation_time,
                              max_quantity_per_day, rating, total_orders)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_ids[dish['chef_email']], dish['name'], dish['description'], dish['price'], dish['cuisine_type'],
            dish['meal_type'], dish['ingredients'], dish['allergens'], dish['dietary_tags'], dish['spice_level'],
            dish['portion_size'], dish['calories'], dish['preparation_time'], dish['max_quantity_per_day'],
            dish['rating'], dish['total_orders']
        ))
        dish_ids[f"{dish['chef_email']}_{dish['name']}"] = cursor.lastrowid
    
    print(f"Created {len(dishes_data)} dishes")
    
    # 4. ORDERS - Create sample orders
    orders_data = [
        {
            'consumer_email': 'john.doe@email.com', 'chef_email': 'chef.maria@email.com',
            'delivery_email': 'delivery.tom@email.com', 'items': '[{"dish_id": 1, "quantity": 2, "price": 12.99}]',
            'subtotal': 25.98, 'delivery_fee': 3.99, 'platform_fee': 1.30, 'tax': 2.60, 'total_amount': 33.87,
            'delivery_type': 'delivery', 'delivery_address': '123 Main St, Dallas, TX 75201',
            'delivery_latitude': 32.7767, 'delivery_longitude': -96.7970, 'order_status': 'delivered',
            'order_placed_at': datetime.now() - timedelta(hours=2), 'delivered_at': datetime.now() - timedelta(hours=1)
        },
        {
            'consumer_email': 'sarah.wilson@email.com', 'chef_email': 'chef.raj@email.com',
            'delivery_email': 'delivery.lisa@email.com', 'items': '[{"dish_id": 4, "quantity": 1, "price": 16.99}]',
            'subtotal': 16.99, 'delivery_fee': 3.99, 'platform_fee': 1.05, 'tax': 1.76, 'total_amount': 23.79,
            'delivery_type': 'delivery', 'delivery_address': '456 Oak Ave, Dallas, TX 75202',
            'delivery_latitude': 32.7849, 'delivery_longitude': -96.8084, 'order_status': 'ready',
            'order_placed_at': datetime.now() - timedelta(minutes=30)
        },
        {
            'consumer_email': 'mike.chen@email.com', 'chef_email': 'chef.anna@email.com',
            'delivery_email': 'delivery.venkat@email.com', 'items': '[{"dish_id": 7, "quantity": 1, "price": 18.99}]',
            'subtotal': 18.99, 'delivery_fee': 0, 'platform_fee': 0, 'tax': 1.52, 'total_amount': 20.51,
            'delivery_type': 'pickup', 'delivery_address': '789 Pine St, Dallas, TX 75203',
            'delivery_latitude': 32.7931, 'delivery_longitude': -96.8198, 'order_status': 'preparing',
            'order_placed_at': datetime.now() - timedelta(minutes=15)
        }
    ]
    
    order_ids = {}
    for order in orders_data:
        order_number = generate_order_number()
        cursor.execute('''
            INSERT INTO orders (order_number, consumer_id, chef_id, delivery_agent_id, items, subtotal,
                              delivery_fee, platform_fee, tax, total_amount, delivery_type, delivery_address,
                              delivery_latitude, delivery_longitude, order_status, order_placed_at, delivered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_number, user_ids[order['consumer_email']], user_ids[order['chef_email']],
            user_ids.get(order['delivery_email']), order['items'], order['subtotal'], order['delivery_fee'],
            order['platform_fee'], order['tax'], order['total_amount'], order['delivery_type'],
            order['delivery_address'], order['delivery_latitude'], order['delivery_longitude'],
            order['order_status'], order['order_placed_at'], order.get('delivered_at')
        ))
        order_ids[order_number] = cursor.lastrowid
    
    print(f"Created {len(orders_data)} orders")
    
    # 5. SERVICE AREAS - Create service areas for delivery agents
    service_areas_data = [
        {'delivery_email': 'delivery.tom@email.com', 'area_name': 'Downtown Dallas', 'zip_code': '75201', 'city': 'Dallas', 'state': 'TX', 'is_primary': 1},
        {'delivery_email': 'delivery.tom@email.com', 'area_name': 'Uptown', 'zip_code': '75204', 'city': 'Dallas', 'state': 'TX', 'is_primary': 0},
        {'delivery_email': 'delivery.lisa@email.com', 'area_name': 'Deep Ellum', 'zip_code': '75226', 'city': 'Dallas', 'state': 'TX', 'is_primary': 1},
        {'delivery_email': 'delivery.venkat@email.com', 'area_name': 'Oak Lawn', 'zip_code': '75219', 'city': 'Dallas', 'state': 'TX', 'is_primary': 1},
        {'delivery_email': 'delivery.venkat@email.com', 'area_name': 'Bishop Arts', 'zip_code': '75208', 'city': 'Dallas', 'state': 'TX', 'is_primary': 0}
    ]
    
    for area in service_areas_data:
        cursor.execute('''
            INSERT INTO service_areas (delivery_agent_id, area_name, zip_code, city, state, is_primary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_ids[area['delivery_email']], area['area_name'], area['zip_code'],
            area['city'], area['state'], area['is_primary']
        ))
    
    print(f"Created {len(service_areas_data)} service areas")
    
    # 6. EARNINGS - Create earnings records
    earnings_data = [
        {'user_email': 'chef.maria@email.com', 'order_number': list(order_ids.keys())[0], 'amount': 25.98, 'type': 'order_revenue'},
        {'user_email': 'delivery.tom@email.com', 'order_number': list(order_ids.keys())[0], 'amount': 3.99, 'type': 'delivery_fee'},
        {'user_email': 'chef.raj@email.com', 'order_number': list(order_ids.keys())[1], 'amount': 16.99, 'type': 'order_revenue'},
        {'user_email': 'delivery.lisa@email.com', 'order_number': list(order_ids.keys())[1], 'amount': 3.99, 'type': 'delivery_fee'},
        {'user_email': 'chef.anna@email.com', 'order_number': list(order_ids.keys())[2], 'amount': 18.99, 'type': 'order_revenue'}
    ]
    
    for earning in earnings_data:
        cursor.execute('''
            INSERT INTO earnings (user_id, order_id, amount, type, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_ids[earning['user_email']], order_ids[earning['order_number']],
            earning['amount'], earning['type'], 'processed'
        ))
    
    print(f"Created {len(earnings_data)} earnings records")
    
    # 7. NOTIFICATIONS - Create sample notifications
    notifications_data = [
        {'user_email': 'john.doe@email.com', 'title': 'Order Delivered', 'message': 'Your order POT-20241015-0001 has been delivered!', 'type': 'order'},
        {'user_email': 'chef.maria@email.com', 'title': 'New Order', 'message': 'You have a new order from John Doe', 'type': 'order'},
        {'user_email': 'delivery.tom@email.com', 'title': 'Delivery Complete', 'message': 'You have successfully completed delivery POT-20241015-0001', 'type': 'order'},
        {'user_email': 'sarah.wilson@email.com', 'title': 'Order Ready', 'message': 'Your order is ready for pickup!', 'type': 'order'}
    ]
    
    for notification in notifications_data:
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, is_read)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_ids[notification['user_email']], notification['title'], notification['message'],
            notification['type'], random.choice([0, 1])
        ))
    
    print(f"Created {len(notifications_data)} notifications")
    
    # 8. FAVORITES - Create some favorite dishes
    favorites_data = [
        {'user_email': 'john.doe@email.com', 'dish_name': 'Chicken Tacos', 'chef_email': 'chef.maria@email.com'},
        {'user_email': 'sarah.wilson@email.com', 'dish_name': 'Vegetable Biryani', 'chef_email': 'chef.raj@email.com'},
        {'user_email': 'mike.chen@email.com', 'dish_name': 'Grilled Salmon', 'chef_email': 'chef.anna@email.com'}
    ]
    
    for favorite in favorites_data:
        dish_key = f"{favorite['chef_email']}_{favorite['dish_name']}"
        if dish_key in dish_ids:
            cursor.execute('''
                INSERT INTO favorites (user_id, dish_id, chef_id)
                VALUES (?, ?, ?)
            ''', (
                user_ids[favorite['user_email']], dish_ids[dish_key],
                user_ids[favorite['chef_email']]
            ))
    
    print(f"Created {len(favorites_data)} favorites")
    
    # 9. CHEF AVAILABILITY - Create availability slots
    chef_emails = ['chef.maria@email.com', 'chef.raj@email.com', 'chef.anna@email.com']
    for chef_email in chef_emails:
        # Monday to Friday availability
        for day in range(1, 6):  # Monday = 1, Friday = 5
            cursor.execute('''
                INSERT INTO chef_availability (chef_id, day_of_week, start_time, end_time)
                VALUES (?, ?, ?, ?)
            ''', (user_ids[chef_email], day, '09:00', '21:00'))
        
        # Weekend availability
        for day in [0, 6]:  # Sunday = 0, Saturday = 6
            cursor.execute('''
                INSERT INTO chef_availability (chef_id, day_of_week, start_time, end_time)
                VALUES (?, ?, ?, ?)
            ''', (user_ids[chef_email], day, '10:00', '20:00'))
    
    print("Created chef availability slots")
    
    # 10. DELIVERY VERIFICATION - Create verification records
    delivery_emails = ['delivery.tom@email.com', 'delivery.lisa@email.com', 'delivery.venkat@email.com']
    for delivery_email in delivery_emails:
        cursor.execute('''
            INSERT INTO delivery_verification (delivery_agent_id, document_type, document_url, verification_status)
            VALUES (?, ?, ?, ?)
        ''', (user_ids[delivery_email], 'driving_license', f'/uploads/{delivery_email}_license.jpg', 'approved'))
        
        cursor.execute('''
            INSERT INTO delivery_verification (delivery_agent_id, document_type, document_url, verification_status)
            VALUES (?, ?, ?, ?)
        ''', (user_ids[delivery_email], 'vehicle_registration', f'/uploads/{delivery_email}_vehicle.jpg', 'approved'))
        
        cursor.execute('''
            INSERT INTO delivery_verification (delivery_agent_id, document_type, document_url, verification_status)
            VALUES (?, ?, ?, ?)
        ''', (user_ids[delivery_email], 'selfie', f'/uploads/{delivery_email}_selfie.jpg', 'approved'))
    
    print("Created delivery verification records")
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    print("\nDatabase seeding completed successfully!")
    print("\nSummary:")
    print(f"   - {len(users_data)} users created")
    print(f"   - {len(dishes_data)} dishes created")
    print(f"   - {len(orders_data)} orders created")
    print(f"   - {len(service_areas_data)} service areas created")
    print(f"   - {len(earnings_data)} earnings records created")
    print(f"   - {len(notifications_data)} notifications created")
    print(f"   - {len(favorites_data)} favorites created")
    print(f"   - Chef availability slots created")
    print(f"   - Delivery verification records created")
    
    print("\nTest Login Credentials:")
    print("   Consumer: john.doe@email.com / password123")
    print("   Chef: chef.maria@email.com / password123")
    print("   Delivery: delivery.tom@email.com / password123")

if __name__ == "__main__":
    seed_database()
