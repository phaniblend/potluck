#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database initialization script for Potluck app
Creates SQLite database and tables from schema.sql
"""

import os
import sys
import sqlite3
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'potluck.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def create_database():
    """Create database and tables from schema"""
    print("🔧 Initializing Potluck database...")
    
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        # Auto-recreate if non-interactive or --force flag
        if '--force' in sys.argv or not sys.stdin.isatty():
            print("⚠️  Database already exists. Recreating...")
            os.remove(DB_PATH)
            print("🗑️  Existing database removed.")
        else:
            print("⚠️  Database already exists. Recreating it...")
            os.remove(DB_PATH)
            print("🗑️  Existing database removed.")
    
    # Create new database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Read and execute schema
        with open(SCHEMA_PATH, 'r') as f:
            schema = f.read()
        
        # Execute the entire schema
        cursor.executescript(schema)
        conn.commit()
        print("✅ Database tables created successfully!")
        
        # Show created tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {table[0]} (0 records)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def insert_sample_data():
    """Insert sample data for testing"""
    print("\n📝 Inserting sample data...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Sample users (password is 'password123' hashed with bcrypt)
        # In production, we'll use proper bcrypt hashing
        sample_password = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lsv2hLlGeRLBrjCBa'
        
        users_data = [
            # Consumers
            ('john.doe@email.com', '555-0101', sample_password, 'John Doe', 'consumer', 
             '123 Main St', 'Dallas', 'TX', '75201', 32.7767, -96.7970),
            ('jane.smith@email.com', '555-0102', sample_password, 'Jane Smith', 'consumer',
             '456 Oak Ave', 'Dallas', 'TX', '75202', 32.7831, -96.8067),
            
            # Chefs
            ('maria.chef@email.com', '555-0201', sample_password, 'Maria Garcia', 'chef',
             '789 Chef Lane', 'Dallas', 'TX', '75203', 32.7459, -96.7838),
            ('raj.chef@email.com', '555-0202', sample_password, 'Raj Patel', 'chef',
             '321 Curry St', 'Dallas', 'TX', '75204', 32.8007, -96.7699),
            
            # Delivery Agents
            ('mike.driver@email.com', '555-0301', sample_password, 'Mike Wilson', 'delivery',
             '654 Driver Ave', 'Dallas', 'TX', '75205', 32.8137, -96.7943),
            ('sarah.driver@email.com', '555-0302', sample_password, 'Sarah Johnson', 'delivery',
             '987 Delivery Rd', 'Dallas', 'TX', '75206', 32.7700, -96.7643)
        ]
        
        for data in users_data:
            cursor.execute("""
                INSERT INTO users (email, phone, password_hash, full_name, user_type,
                                 address, city, state, zip_code, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
        
        # Update chef-specific fields
        cursor.execute("""
            UPDATE users 
            SET chef_bio = 'Authentic Mexican cuisine from family recipes',
                chef_specialties = '["Mexican", "Tex-Mex"]',
                kitchen_type = 'home',
                chef_rating = 4.8,
                total_dishes_sold = 156
            WHERE email = 'maria.chef@email.com'
        """)
        
        cursor.execute("""
            UPDATE users 
            SET chef_bio = 'Traditional Indian dishes with a modern twist',
                chef_specialties = '["Indian", "Vegetarian", "Vegan"]',
                kitchen_type = 'home',
                chef_rating = 4.9,
                total_dishes_sold = 203
            WHERE email = 'raj.chef@email.com'
        """)
        
        # Update delivery-specific fields
        cursor.execute("""
            UPDATE users 
            SET vehicle_type = 'car',
                vehicle_number = 'TX-123456',
                delivery_radius = 10,
                current_status = 'online',
                delivery_rating = 4.7,
                total_deliveries = 89
            WHERE email = 'mike.driver@email.com'
        """)
        
        cursor.execute("""
            UPDATE users 
            SET vehicle_type = 'scooter',
                vehicle_number = 'TX-789012',
                delivery_radius = 7,
                current_status = 'online',
                delivery_rating = 4.9,
                total_deliveries = 124
            WHERE email = 'sarah.driver@email.com'
        """)
        
        # Sample dishes for Maria (chef_id = 3)
        dishes_maria = [
            ('Chicken Tacos', 'Authentic street-style tacos with homemade salsa', 12.99, 'Mexican', 'lunch',
             '["chicken", "tortillas", "onions", "cilantro", "lime"]', '["none"]', 
             '["gluten-free-option"]', 2, 'Serves 3 tacos', 450),
            ('Beef Enchiladas', 'Traditional enchiladas with red sauce and cheese', 15.99, 'Mexican', 'dinner',
             '["beef", "tortillas", "cheese", "red sauce", "sour cream"]', '["dairy"]',
             '[]', 3, 'Serves 2', 650),
            ('Vegetarian Quesadilla', 'Grilled quesadilla with mixed vegetables', 10.99, 'Mexican', 'lunch',
             '["tortillas", "cheese", "bell peppers", "onions", "mushrooms"]', '["dairy"]',
             '["vegetarian"]', 1, 'Serves 1-2', 380)
        ]
        
        for dish in dishes_maria:
            cursor.execute("""
                INSERT INTO dishes (chef_id, name, description, price, cuisine_type, meal_type,
                                  ingredients, allergens, dietary_tags, spice_level, portion_size, calories)
                VALUES (3, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, dish)
        
        # Sample dishes for Raj (chef_id = 4)
        dishes_raj = [
            ('Paneer Tikka Masala', 'Creamy tomato curry with grilled paneer', 13.99, 'Indian', 'dinner',
             '["paneer", "tomatoes", "cream", "spices", "rice"]', '["dairy"]',
             '["vegetarian", "gluten-free"]', 3, 'Serves 2', 520),
            ('Vegetable Biryani', 'Fragrant rice with mixed vegetables and spices', 11.99, 'Indian', 'lunch',
             '["basmati rice", "mixed vegetables", "spices", "yogurt"]', '["dairy"]',
             '["vegetarian"]', 2, 'Serves 2-3', 480),
            ('Dal Tadka', 'Yellow lentils tempered with spices', 9.99, 'Indian', 'dinner',
             '["yellow lentils", "tomatoes", "onions", "spices"]', '["none"]',
             '["vegan", "gluten-free"]', 2, 'Serves 2', 320)
        ]
        
        for dish in dishes_raj:
            cursor.execute("""
                INSERT INTO dishes (chef_id, name, description, price, cuisine_type, meal_type,
                                  ingredients, allergens, dietary_tags, spice_level, portion_size, calories)
                VALUES (4, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, dish)
        
        # Sample chef availability
        availability_slots = [
            (3, 1, '11:00', '14:00'),  # Maria - Monday lunch
            (3, 1, '18:00', '21:00'),  # Maria - Monday dinner
            (3, 2, '11:00', '14:00'),  # Maria - Tuesday lunch
            (3, 2, '18:00', '21:00'),  # Maria - Tuesday dinner
            (4, 1, '12:00', '15:00'),  # Raj - Monday lunch
            (4, 1, '19:00', '22:00'),  # Raj - Monday dinner
            (4, 3, '12:00', '15:00'),  # Raj - Wednesday lunch
            (4, 3, '19:00', '22:00'),  # Raj - Wednesday dinner
        ]
        
        for slot in availability_slots:
            cursor.execute("""
                INSERT INTO chef_availability (chef_id, day_of_week, start_time, end_time)
                VALUES (?, ?, ?, ?)
            """, slot)
        
        # Sample orders
        cursor.execute("""
            INSERT INTO orders (order_number, consumer_id, chef_id, delivery_agent_id,
                              items, subtotal, delivery_fee, platform_fee, tax, total_amount,
                              payment_method, payment_status, delivery_type, delivery_address,
                              order_status)
            VALUES ('POT-20240101-0001', 1, 3, 5,
                    '[{"dish_id": 1, "quantity": 2, "price": 12.99}]',
                    25.98, 3.00, 2.00, 2.31, 33.29,
                    'online', 'paid', 'delivery', '123 Main St, Dallas, TX 75201',
                    'delivered')
        """)
        
        conn.commit()
        print("✅ Sample data inserted successfully!")
        
        # Show record counts
        tables_to_check = ['users', 'dishes', 'orders', 'chef_availability']
        print("\n📊 Database statistics:")
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def main():
    """Main function"""
    import sys
    
    print("=" * 50)
    print("   POTLUCK DATABASE INITIALIZATION")
    print("=" * 50)
    
    # Check for --with-data flag
    insert_data = '--with-data' in sys.argv or '-d' in sys.argv
    
    # Create database
    if create_database():
        # Automatically insert sample data if flag provided, or if stdin is not available
        if insert_data or not sys.stdin.isatty():
            print("\n📦 Inserting sample data for testing...")
            insert_sample_data()
        else:
            print("\n📦 Skipping sample data insertion (using custom test data script).")
    
    print("\n✨ Database initialization complete!")
    print(f"📁 Database location: {DB_PATH}")
    print("=" * 50)

if __name__ == "__main__":
    main()