-- Potluck Database Schema
-- Three main roles: Consumer, Chef, Delivery Agent

-- Users table (common for all roles)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    user_type TEXT NOT NULL CHECK(user_type IN ('consumer', 'chef', 'delivery')),
    is_active BOOLEAN DEFAULT 1,
    is_verified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Profile fields
    profile_image TEXT,
    address TEXT,
    city TEXT DEFAULT 'Dallas',
    state TEXT DEFAULT 'TX',
    zip_code TEXT,
    latitude REAL,
    longitude REAL,
    
    -- Chef-specific fields
    chef_bio TEXT,
    chef_specialties TEXT, -- JSON array of cuisines
    kitchen_type TEXT, -- 'home', 'commercial', 'shared'
    max_orders_per_day INTEGER DEFAULT 10,
    preparation_time INTEGER DEFAULT 60, -- minutes
    is_available BOOLEAN DEFAULT 1,
    chef_rating REAL DEFAULT 0,
    total_dishes_sold INTEGER DEFAULT 0,
    
    -- Delivery-specific fields
    vehicle_type TEXT, -- 'bike', 'scooter', 'car'
    vehicle_number TEXT,
    driving_license TEXT,
    delivery_radius INTEGER DEFAULT 5, -- km
    current_status TEXT DEFAULT 'offline', -- 'offline', 'online', 'busy'
    delivery_rating REAL DEFAULT 0,
    total_deliveries INTEGER DEFAULT 0,
    
    -- Consumer-specific fields
    consumer_rating REAL DEFAULT 0,
    total_orders_placed INTEGER DEFAULT 0,
    dietary_preferences TEXT -- JSON array
);

-- Chef disclaimer/agreement
CREATE TABLE IF NOT EXISTS chef_agreements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chef_id INTEGER NOT NULL,
    agreement_version TEXT NOT NULL,
    agreed_terms TEXT NOT NULL, -- JSON with all terms
    ip_address TEXT,
    signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chef_id) REFERENCES users(id)
);

-- Dishes table
CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chef_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    cuisine_type TEXT,
    meal_type TEXT, -- 'breakfast', 'lunch', 'dinner', 'snack'
    
    -- Food details
    ingredients TEXT NOT NULL, -- JSON array
    allergens TEXT, -- JSON array
    dietary_tags TEXT, -- JSON array: 'vegan', 'vegetarian', 'gluten-free', etc.
    spice_level INTEGER DEFAULT 1, -- 1-5 scale
    portion_size TEXT,
    calories INTEGER,
    
    -- Availability
    is_available BOOLEAN DEFAULT 1,
    preparation_time INTEGER DEFAULT 30, -- minutes
    max_quantity_per_day INTEGER DEFAULT 10,
    advance_order_hours INTEGER DEFAULT 2,
    
    -- Images and media
    image_url TEXT,
    thumbnail_url TEXT,
    
    -- Stats
    rating REAL DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    total_reviews INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chef_id) REFERENCES users(id)
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL, -- POT-YYYYMMDD-XXXX
    
    -- Parties involved
    consumer_id INTEGER NOT NULL,
    chef_id INTEGER NOT NULL,
    delivery_agent_id INTEGER,
    
    -- Order details
    items TEXT NOT NULL, -- JSON array of {dish_id, quantity, price}
    subtotal REAL NOT NULL,
    delivery_fee REAL DEFAULT 0,
    platform_fee REAL DEFAULT 0,
    tax REAL DEFAULT 0,
    total_amount REAL NOT NULL,
    
    -- Payment
    payment_method TEXT DEFAULT 'cash', -- 'cash', 'online', 'upi'
    payment_status TEXT DEFAULT 'pending', -- 'pending', 'paid', 'failed', 'refunded'
    transaction_id TEXT,
    
    -- Delivery details
    delivery_type TEXT NOT NULL, -- 'pickup', 'delivery'
    delivery_address TEXT,
    delivery_latitude REAL,
    delivery_longitude REAL,
    delivery_instructions TEXT,
    special_instructions TEXT,
    
    -- Timing
    order_placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_ready_time TIMESTAMP,
    actual_ready_time TIMESTAMP,
    picked_up_at TIMESTAMP,
    delivered_at TIMESTAMP,
    
    -- Status tracking
    order_status TEXT DEFAULT 'pending', 
    -- 'pending', 'accepted', 'preparing', 'ready', 'picked_up', 'out_for_delivery', 'delivered', 'cancelled'
    
    -- Cancellation
    cancelled_by TEXT, -- 'consumer', 'chef', 'delivery', 'system'
    cancellation_reason TEXT,
    
    -- Ratings and feedback
    chef_rating INTEGER,
    chef_review TEXT,
    delivery_rating INTEGER,
    delivery_review TEXT,
    
    FOREIGN KEY (consumer_id) REFERENCES users(id),
    FOREIGN KEY (chef_id) REFERENCES users(id),
    FOREIGN KEY (delivery_agent_id) REFERENCES users(id)
);

-- Order status history for tracking
CREATE TABLE IF NOT EXISTS order_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    changed_by INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    reviewer_id INTEGER NOT NULL,
    reviewed_user_id INTEGER,
    dish_id INTEGER,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,
    is_verified_purchase BOOLEAN DEFAULT 1,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id),
    FOREIGN KEY (reviewed_user_id) REFERENCES users(id),
    FOREIGN KEY (dish_id) REFERENCES dishes(id)
);

-- Messages/Chat table
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    message_text TEXT NOT NULL,
    message_type TEXT DEFAULT 'text', -- 'text', 'image', 'location'
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);

-- Delivery tracking
CREATE TABLE IF NOT EXISTS delivery_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    delivery_agent_id INTEGER NOT NULL,
    current_latitude REAL,
    current_longitude REAL,
    status TEXT, -- 'assigned', 'heading_to_pickup', 'at_pickup', 'heading_to_delivery', 'near_delivery', 'delivered'
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (delivery_agent_id) REFERENCES users(id)
);

-- Favorites
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    dish_id INTEGER,
    chef_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (dish_id) REFERENCES dishes(id),
    FOREIGN KEY (chef_id) REFERENCES users(id)
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT, -- 'order', 'payment', 'review', 'promotion'
    related_id INTEGER, -- order_id or other relevant id
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Earnings/Payouts for chefs and delivery agents
CREATE TABLE IF NOT EXISTS earnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL, -- 'order_revenue', 'delivery_fee', 'tip'
    status TEXT DEFAULT 'pending', -- 'pending', 'processed', 'paid'
    payout_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- Availability slots for chefs
CREATE TABLE IF NOT EXISTS chef_availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chef_id INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL, -- 0=Sunday, 6=Saturday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (chef_id) REFERENCES users(id)
);

-- Service areas for delivery agents
CREATE TABLE IF NOT EXISTS service_areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_agent_id INTEGER NOT NULL,
    area_name TEXT NOT NULL, -- e.g., "Downtown Dallas", "Uptown"
    zip_code TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT DEFAULT 'US',
    latitude REAL,
    longitude REAL,
    is_primary BOOLEAN DEFAULT 0, -- Primary service area
    is_active BOOLEAN DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (delivery_agent_id) REFERENCES users(id)
);

-- Delivery agent verification documents
CREATE TABLE IF NOT EXISTS delivery_verification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_agent_id INTEGER NOT NULL,
    document_type TEXT NOT NULL, -- 'driving_license', 'id_card', 'selfie', 'vehicle_registration'
    document_url TEXT NOT NULL,
    verification_status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    verified_by INTEGER, -- admin user id
    verified_at TIMESTAMP,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (delivery_agent_id) REFERENCES users(id),
    FOREIGN KEY (verified_by) REFERENCES users(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_dishes_chef ON dishes(chef_id);
CREATE INDEX IF NOT EXISTS idx_dishes_available ON dishes(is_available);
CREATE INDEX IF NOT EXISTS idx_orders_consumer ON orders(consumer_id);
CREATE INDEX IF NOT EXISTS idx_orders_chef ON orders(chef_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_messages_order ON messages(order_id);
CREATE INDEX IF NOT EXISTS idx_delivery_tracking_order ON delivery_tracking(order_id);
CREATE INDEX IF NOT EXISTS idx_service_areas_da ON service_areas(delivery_agent_id);
CREATE INDEX IF NOT EXISTS idx_service_areas_zip ON service_areas(zip_code);
CREATE INDEX IF NOT EXISTS idx_delivery_verification_da ON delivery_verification(delivery_agent_id);