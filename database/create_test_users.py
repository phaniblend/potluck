#!/usr/bin/env python3
"""
Create 3 test users in the same area: Consumer, Chef, Delivery Agent
"""

import sqlite3
import bcrypt
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'potluck.db')

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_test_users():
    """Create 3 test users in the same area"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating test users...")
    
    # Use Philadelphia area (same as your current location)
    test_city = 'Philadelphia'
    test_state = 'PA'
    test_zip = '19146'
    test_lat = 39.9442
    test_lon = -75.1665
    
    # Common password for all
    password_hash = hash_password('Passw0rd!')
    
    # 1. Consumer
    cursor.execute('''
        INSERT OR REPLACE INTO users (
            email, phone, password_hash, full_name, user_type,
            address, city, state, zip_code, latitude, longitude,
            is_active, is_verified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'cathy@demo.tld',
        '+15551234567',
        password_hash,
        'Cathy Consumer',
        'consumer',
        f'123 Main Street, {test_city}, {test_state} {test_zip}',
        test_city,
        test_state,
        test_zip,
        test_lat,
        test_lon,
        1,
        1
    ))
    consumer_id = cursor.lastrowid
    print(f"[OK] Created Consumer: cathy@demo.tld / Passw0rd! (ID: {consumer_id})")
    
    # 2. Chef
    cursor.execute('''
        INSERT OR REPLACE INTO users (
            email, phone, password_hash, full_name, user_type,
            address, city, state, zip_code, latitude, longitude,
            chef_bio, chef_specialties, kitchen_type,
            max_orders_per_day, preparation_time, is_available,
            is_active, is_verified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'chef.anu@demo.tld',
        '+15551234568',
        password_hash,
        'Chef Anu',
        'chef',
        f'456 Chef Avenue, {test_city}, {test_state} {test_zip}',
        test_city,
        test_state,
        test_zip,
        test_lat + 0.01,  # Slightly different location
        test_lon + 0.01,
        'Expert chef specializing in Indian and fusion cuisine',
        '["indian", "fusion", "vegetarian"]',
        'home',
        15,
        45,
        1,
        1,
        1
    ))
    chef_id = cursor.lastrowid
    print(f"[OK] Created Chef: chef.anu@demo.tld / Passw0rd! (ID: {chef_id})")
    
    # Add 2 dishes for Chef Anu
    cursor.execute('''
        INSERT OR REPLACE INTO dishes (
            chef_id, name, description, price, cuisine_type,
            ingredients, allergens, dietary_tags, is_available,
            preparation_time, rating, total_orders
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        chef_id,
        'Chicken Curry Bowl',
        'Tender chicken in aromatic curry sauce with basmati rice',
        16.99,
        'indian',
        '["chicken", "onions", "tomatoes", "spices", "rice"]',
        '[]',
        '["gluten-free"]',
        1,
        45,
        4.9,
        67
    ))
    
    cursor.execute('''
        INSERT OR REPLACE INTO dishes (
            chef_id, name, description, price, cuisine_type,
            ingredients, allergens, dietary_tags, is_available,
            preparation_time, rating, total_orders
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        chef_id,
        'Veg Pulao',
        'Fragrant basmati rice with mixed vegetables and aromatic spices',
        14.99,
        'indian',
        '["rice", "vegetables", "spices", "cashews"]',
        '[]',
        '["vegetarian", "vegan", "gluten-free"]',
        1,
        40,
        4.8,
        54
    ))
    print(f"[OK] Added 2 dishes for Chef Anu: Chicken Curry Bowl ($16.99), Veg Pulao ($14.99)")
    
    # 3. Delivery Agent
    cursor.execute('''
        INSERT OR REPLACE INTO users (
            email, phone, password_hash, full_name, user_type,
            address, city, state, zip_code, latitude, longitude,
            vehicle_type, delivery_radius, current_status,
            is_active, is_verified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'ravi.rider@demo.tld',
        '+15551234569',
        password_hash,
        'Ravi Rider',
        'delivery',
        f'789 Rider Road, {test_city}, {test_state} {test_zip}',
        test_city,
        test_state,
        test_zip,
        test_lat - 0.01,  # Slightly different location
        test_lon - 0.01,
        'car',
        5,
        'online',
        1,
        1
    ))
    da_id = cursor.lastrowid
    print(f"[OK] Created Delivery Agent: ravi.rider@demo.tld / Passw0rd! (ID: {da_id})")
    
    # Add service area for delivery agent
    cursor.execute('''
        INSERT OR REPLACE INTO service_areas (
            delivery_agent_id, area_name, zip_code, city, state, country,
            is_primary, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        da_id,
        'Philadelphia Center',
        test_zip,
        test_city,
        test_state,
        'US',
        1,
        1
    ))
    print(f"[OK] Added service area for Ravi Rider: {test_city}, {test_state} {test_zip}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("[OK] Test Users Created Successfully!")
    print("="*60)
    print("\nLogin Credentials (all use same password: Passw0rd!):")
    print("\nConsumer:")
    print("   Email: cathy@demo.tld")
    print("   Password: Passw0rd!")
    print("\nChef:")
    print("   Email: chef.anu@demo.tld")
    print("   Password: Passw0rd!")
    print("   Dishes: Chicken Curry Bowl, Veg Pulao")
    print("\nDelivery Agent:")
    print("   Email: ravi.rider@demo.tld")
    print("   Password: Passw0rd!")
    print("\nAll users are in: Philadelphia, PA 19146")
    print("="*60)

if __name__ == '__main__':
    create_test_users()

