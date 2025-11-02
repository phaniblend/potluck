// Consumer Dashboard Logic
console.log('🍲 consumer.js loading...');

// API Configuration
const API_BASE = window.location.origin;
const CONSUMER_API_URL = `${API_BASE}/api`;

// State Management
let currentUser = null;
let cart = [];
let dishes = [];
let chefs = [];
let activeOrders = [];
let orderHistory = [];
let favorites = [];
let notifications = [];
let currentRatingOrder = null;
let ratings = { food: 0, chef: 0, delivery: 0 };
let selectedTip = 0;

// Initialize Dashboard
async function initConsumerDashboard() {
    console.log('🚀 Initializing consumer dashboard...');
    
    try {
        // Check authentication
        const token = localStorage.getItem('token');
        const userStr = localStorage.getItem('user');
        
        if (!token || !userStr) {
            console.log('No auth token or user data, redirecting to login...');
            window.location.href = '/';
            return;
        }
        
        const user = JSON.parse(userStr);
        if (user.user_type !== 'consumer') {
            console.log('User is not a consumer, redirecting...');
            window.location.href = '/';
            return;
        }
        
        currentUser = user;
        
        // Update UI with user info
        document.getElementById('userName').textContent = user.full_name || 'User';
        
        // Auto-detect location
        await loadCurrentLocation();
        
        // Load data (with error handling to prevent infinite loops)
        try {
            await Promise.all([
                loadDishes().catch(e => console.warn('Failed to load dishes:', e)),
                loadActiveOrders().catch(e => console.warn('Failed to load orders:', e)),
                loadOrderHistory().catch(e => console.warn('Failed to load history:', e)),
                loadFavorites().catch(e => console.warn('Failed to load favorites:', e)),
                loadNotifications().catch(e => console.warn('Failed to load notifications:', e))
            ]);
        } catch (error) {
            console.warn('Some data failed to load:', error);
        }
        
        // Load cart from localStorage
        loadCart();
        
        // Setup real-time updates (if WebSocket available)
        setupRealTimeUpdates();
        
        console.log('✅ Consumer dashboard initialized');
    } catch (error) {
        console.error('❌ Failed to initialize dashboard:', error);
        // Don't redirect on error, just show message
        console.error('Dashboard initialization error:', error);
    }
}

// Authentication
async function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    try {
        const response = await fetch(`${CONSUMER_API_URL}/auth/verify`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            return data.user;
        }
        return null;
    } catch (error) {
        console.error('Auth check failed:', error);
        return null;
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('cart');
    window.location.href = '/';
}

// Load current location
async function loadCurrentLocation() {
    try {
        // Get location from localStorage or user profile
        const storedLocation = localStorage.getItem('userLocation');
        if (storedLocation) {
            const location = JSON.parse(storedLocation);
            document.getElementById('userLocation').textContent = `📍 ${location.city}, ${location.state}`;
        } else if (currentUser && currentUser.city && currentUser.state) {
            // Use location from user profile
            document.getElementById('userLocation').textContent = `📍 ${currentUser.city}, ${currentUser.state}`;
        } else {
            // Try to detect location automatically
            try {
                if ('geolocation' in navigator) {
                    const position = await new Promise((resolve, reject) => {
                        navigator.geolocation.getCurrentPosition(resolve, reject);
                    });
                    
                    // Reverse geocode to get city/state
                    const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${position.coords.latitude}&lon=${position.coords.longitude}&format=json`);
                    const data = await response.json();
                    
                    const location = {
                        city: data.address.city || data.address.town || data.address.village || 'Unknown',
                        state: data.address.state || '',
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    
                    localStorage.setItem('userLocation', JSON.stringify(location));
                    document.getElementById('userLocation').textContent = `📍 ${location.city}, ${location.state}`;
                } else {
                    document.getElementById('userLocation').textContent = `📍 Location unavailable`;
                }
            } catch (error) {
                console.warn('Could not detect location:', error);
                document.getElementById('userLocation').textContent = `📍 Location unavailable`;
            }
        }
    } catch (error) {
        console.error('Failed to load location:', error);
        document.getElementById('userLocation').textContent = `📍 Location unavailable`;
    }
}

// Load Dishes
async function loadDishes() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${CONSUMER_API_URL}/consumer/dishes`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            dishes = (data.dishes || []).map(dish => {
                // Parse JSON fields that come as strings from the database
                try {
                    if (typeof dish.dietary_tags === 'string') {
                        dish.dietary_tags = JSON.parse(dish.dietary_tags || '[]');
                    }
                    if (typeof dish.ingredients === 'string') {
                        dish.ingredients = JSON.parse(dish.ingredients || '[]');
                    }
                    if (typeof dish.allergens === 'string') {
                        dish.allergens = JSON.parse(dish.allergens || '[]');
                    }
                } catch (e) {
                    console.warn('Error parsing dish JSON fields:', e);
                    dish.dietary_tags = dish.dietary_tags || [];
                    dish.ingredients = dish.ingredients || [];
                    dish.allergens = dish.allergens || [];
                }
                return dish;
            });
            chefs = data.chefs || [];
            displayDishes(dishes);
            populateAreaFilter();
        } else {
            console.warn('Failed to load dishes, using mock data');
            loadMockDishes();
        }
    } catch (error) {
        console.error('Error loading dishes:', error);
        loadMockDishes();
    }
}

// Mock data for testing
function loadMockDishes() {
    dishes = [
        {
            id: 1,
            name: 'Chicken Tacos',
            description: 'Authentic Mexican chicken tacos with fresh salsa',
            price: 12.99,
            chef_name: 'Maria Rodriguez',
            chef_id: 4,
            chef_rating: 4.9,
            dish_rating: 4.8,
            cuisine_type: 'mexican',
            dietary_tags: ['gluten-free'],
            image: '/images/tacos.jpg',
            area: 'Dallas',
            distance: 2.5
        },
        {
            id: 2,
            name: 'Chicken Curry',
            description: 'Spicy Indian chicken curry with basmati rice',
            price: 16.99,
            chef_name: 'Raj Patel',
            chef_id: 5,
            chef_rating: 4.8,
            dish_rating: 4.9,
            cuisine_type: 'indian',
            dietary_tags: ['gluten-free'],
            image: '/images/curry.jpg',
            area: 'Dallas',
            distance: 3.2
        },
        {
            id: 3,
            name: 'Grilled Salmon',
            description: 'Fresh Atlantic salmon with quinoa and roasted vegetables',
            price: 18.99,
            chef_name: 'Anna Thompson',
            chef_id: 6,
            chef_rating: 4.7,
            dish_rating: 4.7,
            cuisine_type: 'american',
            dietary_tags: ['gluten-free', 'healthy'],
            image: '/images/salmon.jpg',
            area: 'Dallas',
            distance: 1.8
        }
    ];
    displayDishes(dishes);
}

// Display Dishes
function displayDishes(dishesToDisplay) {
    const grid = document.getElementById('dishesGrid');
    
    if (!dishesToDisplay || dishesToDisplay.length === 0) {
        grid.innerHTML = '<div class="empty-state"><p>No dishes available in your area</p></div>';
        return;
    }
    
    grid.innerHTML = dishesToDisplay.map(dish => `
        <div class="dish-card" onclick="showDishDetails(${dish.id})">
            <div class="dish-image" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 3rem; height: 200px;">
                🍽️
            </div>
            <div class="dish-content">
                <div class="dish-header">
                    <div>
                        <div class="dish-name">${dish.name}</div>
                        <div class="dish-rating">
                            ⭐ ${dish.dish_rating || 4.5} (${dish.total_orders || 0} orders)
                        </div>
                    </div>
                    <button class="favorite-btn ${isFavorite(dish.id) ? 'active' : ''}" onclick="event.stopPropagation(); toggleFavorite(${dish.id})">
                        ${isFavorite(dish.id) ? '❤️' : '🤍'}
                    </button>
                </div>
                <div class="dish-chef">
                    👨‍🍳 ${dish.chef_name} (⭐ ${dish.chef_rating || 4.5})
                </div>
                <div class="dish-description">${dish.description}</div>
                <div class="dish-tags">
                    <span class="tag">${dish.cuisine_type}</span>
                    ${(dish.dietary_tags || []).map(tag => `<span class="tag">${tag}</span>`).join('')}
                    ${dish.distance ? `<span class="tag">📍 ${dish.distance} mi</span>` : ''}
                </div>
                <div class="dish-footer">
                    <div class="dish-price">$${dish.price.toFixed(2)}</div>
                    <button class="add-to-cart-btn" onclick="event.stopPropagation(); addToCart(${dish.id})">
                        Add to Cart
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Show Dish Details
function showDishDetails(dishId) {
    const dish = dishes.find(d => d.id === dishId);
    if (!dish) return;
    
    const modal = document.getElementById('dishModal');
    const modalBody = document.getElementById('dishModalBody');
    
    modalBody.innerHTML = `
        <div class="dish-detail">
            <div style="width: 100%; max-height: 300px; border-radius: 8px; margin-bottom: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 5rem; height: 300px;">
                🍽️
            </div>
            <h3>${dish.name}</h3>
            <div style="display: flex; gap: 1rem; margin: 1rem 0;">
                <div class="dish-rating">⭐ ${dish.dish_rating || 4.5} (Dish)</div>
                <div class="dish-rating">👨‍🍳 ${dish.chef_name} (⭐ ${dish.chef_rating || 4.5})</div>
            </div>
            <p style="margin: 1rem 0;">${dish.description}</p>
            <div style="margin: 1rem 0;">
                <strong>Cuisine:</strong> ${dish.cuisine_type}
            </div>
            ${dish.dietary_tags && dish.dietary_tags.length > 0 ? `
                <div style="margin: 1rem 0;">
                    <strong>Dietary:</strong> ${dish.dietary_tags.join(', ')}
                </div>
            ` : ''}
            ${dish.ingredients ? `
                <div style="margin: 1rem 0;">
                    <strong>Ingredients:</strong> ${JSON.parse(dish.ingredients).join(', ')}
                </div>
            ` : ''}
            ${dish.allergens ? `
                <div style="margin: 1rem 0;">
                    <strong>Allergens:</strong> ${JSON.parse(dish.allergens).join(', ')}
                </div>
            ` : ''}
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
                <div class="dish-price" style="font-size: 1.5rem;">$${dish.price.toFixed(2)}</div>
                <button class="btn btn-primary" onclick="addToCart(${dish.id}); closeDishModal();">Add to Cart</button>
            </div>
        </div>
    `;
    
    modal.style.display = 'flex';
}

function closeDishModal() {
    document.getElementById('dishModal').style.display = 'none';
}

// Cart Management
function addToCart(dishId) {
    const dish = dishes.find(d => d.id === dishId);
    if (!dish) return;
    
    const existingItem = cart.find(item => item.dish_id === dishId);
    
    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({
            dish_id: dishId,
            dish: dish,
            quantity: 1,
            price: dish.price
        });
    }
    
    saveCart();
    updateCartUI();
    showToast(`${dish.name} added to cart!`, 'success');
}

function removeFromCart(dishId) {
    cart = cart.filter(item => item.dish_id !== dishId);
    saveCart();
    updateCartUI();
}

function updateQuantity(dishId, change) {
    const item = cart.find(item => item.dish_id === dishId);
    if (!item) return;
    
    item.quantity += change;
    
    if (item.quantity <= 0) {
        removeFromCart(dishId);
    } else {
        saveCart();
        updateCartUI();
    }
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function loadCart() {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
        cart = JSON.parse(savedCart);
        updateCartUI();
    }
}

function updateCartUI() {
    const cartItems = document.getElementById('cartItems');
    const cartFooter = document.getElementById('cartFooter');
    const cartBadge = document.getElementById('cartBadge');
    
    const itemCount = cart.reduce((sum, item) => sum + item.quantity, 0);
    
    if (itemCount > 0) {
        cartBadge.textContent = itemCount;
        cartBadge.style.display = 'block';
    } else {
        cartBadge.style.display = 'none';
    }
    
    if (cart.length === 0) {
        cartItems.innerHTML = '<div class="empty-state"><p>Your cart is empty</p></div>';
        cartFooter.style.display = 'none';
        return;
    }
    
    cartItems.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-image" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 2rem; min-width: 60px; height: 60px; border-radius: 8px;">
                🍽️
            </div>
            <div class="cart-item-details">
                <div class="cart-item-name">${item.dish.name}</div>
                <div class="cart-item-chef">by ${item.dish.chef_name}</div>
                <div class="cart-item-quantity">
                    <button class="qty-btn" onclick="updateQuantity(${item.dish_id}, -1)">-</button>
                    <span>${item.quantity}</span>
                    <button class="qty-btn" onclick="updateQuantity(${item.dish_id}, 1)">+</button>
                </div>
            </div>
            <div class="cart-item-price">$${(item.price * item.quantity).toFixed(2)}</div>
        </div>
    `).join('');
    
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    document.getElementById('cartTotal').textContent = `$${subtotal.toFixed(2)}`;
    cartFooter.style.display = 'block';
}

function toggleCart() {
    const panel = document.getElementById('cartPanel');
    panel.style.display = panel.style.display === 'none' ? 'flex' : 'none';
}

// Checkout
function proceedToCheckout() {
    if (cart.length === 0) {
        showToast('Your cart is empty', 'warning');
        return;
    }
    
    // Close cart panel
    toggleCart();
    
    // Show checkout modal
    const modal = document.getElementById('checkoutModal');
    const summaryDiv = document.getElementById('checkoutSummary');
    
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const deliveryFee = 0; // Default to pickup (no delivery fee)
    const tax = subtotal * 0.08;
    const total = subtotal + deliveryFee + tax;
    
    summaryDiv.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            ${cart.map(item => `
                <div style="display: flex; justify-content: space-between;">
                    <span>${item.dish.name} x${item.quantity}</span>
                    <span>$${(item.price * item.quantity).toFixed(2)}</span>
                </div>
            `).join('')}
            <hr>
            <div style="display: flex; justify-content: space-between;">
                <span>Subtotal:</span>
                <span id="subtotalAmount">$${subtotal.toFixed(2)}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>Delivery Fee:</span>
                <span id="deliveryFeeAmount">$${deliveryFee.toFixed(2)}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>Tax:</span>
                <span id="taxAmount">$${tax.toFixed(2)}</span>
            </div>
            <hr>
            <div style="display: flex; justify-content: space-between; font-size: 1.2rem; font-weight: 600;">
                <span>Total:</span>
                <span id="totalAmount">$${total.toFixed(2)}</span>
            </div>
        </div>
    `;
    
    // Pre-fill address if available
    if (currentUser && currentUser.address) {
        document.getElementById('deliveryAddress').value = currentUser.address;
    }
    
    modal.style.display = 'flex';
    
    // Trigger delivery type update to set correct fees on initial load
    updateDeliveryType();
}

function updateDeliveryType() {
    const deliveryType = document.querySelector('input[name="deliveryType"]:checked').value;
    const addressGroup = document.getElementById('deliveryAddressGroup');
    const deliveryFeeAmount = document.getElementById('deliveryFeeAmount');
    const totalAmount = document.getElementById('totalAmount');
    
    // Calculate subtotal
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const deliveryFee = deliveryType === 'delivery' ? 3.99 : 0;
    const tax = subtotal * 0.08;
    const total = subtotal + deliveryFee + tax;
    
    if (deliveryType === 'pickup') {
        addressGroup.style.display = 'none';
        if (deliveryFeeAmount) deliveryFeeAmount.textContent = '$0.00';
    } else {
        addressGroup.style.display = 'block';
        if (deliveryFeeAmount) deliveryFeeAmount.textContent = '$3.99';
    }
    
    // Update the total display
    if (totalAmount) {
        totalAmount.textContent = `$${total.toFixed(2)}`;
    }
}

function closeCheckoutModal() {
    document.getElementById('checkoutModal').style.display = 'none';
}

async function placeOrder() {
    const deliveryType = document.querySelector('input[name="deliveryType"]:checked').value;
    const deliveryAddress = document.getElementById('deliveryAddress').value;
    const specialInstructions = document.getElementById('specialInstructions').value;
    const paymentMethod = document.getElementById('paymentMethod').value;
    
    if (deliveryType === 'delivery' && !deliveryAddress) {
        showToast('Please enter a delivery address', 'warning');
        return;
    }
    
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const deliveryFee = deliveryType === 'delivery' ? 3.99 : 0;
    const tax = subtotal * 0.08;
    const total = subtotal + deliveryFee + tax;
    
    const orderData = {
        items: cart.map(item => ({
            dish_id: item.dish_id,
            quantity: item.quantity,
            price: item.price
        })),
        chef_id: cart[0].dish.chef_id, // Assuming single chef per order
        subtotal: subtotal,
        delivery_fee: deliveryFee,
        tax: tax,
        total_amount: total,
        delivery_type: deliveryType,
        delivery_address: deliveryAddress,
        special_instructions: specialInstructions,
        payment_method: paymentMethod
    };
    
    try {
        const token = localStorage.getItem('token');
        console.log('Placing order with token:', token ? 'Token exists' : 'NO TOKEN');
        console.log('Order data:', orderData);
        
        if (!token) {
            showToast('Please login first', 'error');
            window.location.href = '/';
            return;
        }
        
        const response = await fetch(`${CONSUMER_API_URL}/consumer/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(orderData)
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('Order placed successfully!', 'success');
            
            // Clear cart
            cart = [];
            saveCart();
            updateCartUI();
            
            // Close modal
            closeCheckoutModal();
            
            // Reload orders
            await loadActiveOrders();
            
            // Switch to orders tab
            switchTab('orders');
        } else {
            const error = await response.json();
            console.error('Order placement failed:', response.status, error);
            showToast(error.error || error.message || 'Failed to place order', 'error');
        }
    } catch (error) {
        console.error('Error placing order:', error);
        showToast('Failed to place order. Please try again.', 'error');
    }
}

// Orders
async function loadActiveOrders() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${CONSUMER_API_URL}/consumer/orders?status=active`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            activeOrders = data.orders || [];
            displayActiveOrders();
        } else {
            console.warn('Failed to load active orders');
            activeOrders = [];
            displayActiveOrders();
        }
    } catch (error) {
        console.error('Error loading active orders:', error);
        activeOrders = [];
        displayActiveOrders();
    }
}

function displayActiveOrders() {
    const list = document.getElementById('activeOrdersList');
    
    if (activeOrders.length === 0) {
        list.innerHTML = '<div class="empty-state"><p>No active orders</p></div>';
        return;
    }
    
    list.innerHTML = activeOrders.map(order => `
        <div class="order-card">
            <div class="order-header">
                <div class="order-number">${order.order_number}</div>
                <div class="order-status ${order.order_status}">${formatStatus(order.order_status)}</div>
            </div>
            <div class="order-items">
                ${(typeof order.items === 'string' ? JSON.parse(order.items) : order.items).map(item => `
                    <div class="order-item">
                        <span>${item.dish_name || 'Dish'} x${item.quantity}</span>
                        <span>$${(item.price * item.quantity).toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>
            <div class="order-footer">
                <div class="order-total">Total: $${order.total_amount.toFixed(2)}</div>
                <div class="order-actions">
                    ${order.order_status === 'delivered' ? `
                        <button class="btn-sm btn-primary" onclick="showRatingModal(${order.id})">Rate Order</button>
                    ` : ''}
                    <button class="btn-sm btn-secondary" onclick="viewOrderDetails(${order.id})">View Details</button>
                </div>
            </div>
        </div>
    `).join('');
}

async function loadOrderHistory() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${CONSUMER_API_URL}/consumer/orders?status=completed`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            orderHistory = data.orders || [];
            displayOrderHistory();
        }
    } catch (error) {
        console.error('Error loading order history:', error);
    }
}

function displayOrderHistory() {
    const list = document.getElementById('historyList');
    
    if (orderHistory.length === 0) {
        list.innerHTML = '<div class="empty-state"><p>No order history</p></div>';
        return;
    }
    
    list.innerHTML = orderHistory.map(order => `
        <div class="order-card">
            <div class="order-header">
                <div class="order-number">${order.order_number}</div>
                <div class="order-status delivered">Delivered</div>
            </div>
            <div class="order-items">
                ${(typeof order.items === 'string' ? JSON.parse(order.items) : order.items).map(item => `
                    <div class="order-item">
                        <span>${item.dish_name || 'Dish'} x${item.quantity}</span>
                        <span>$${(item.price * item.quantity).toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>
            <div class="order-footer">
                <div class="order-total">Total: $${order.total_amount.toFixed(2)}</div>
                <div class="order-actions">
                    <button class="btn-sm btn-primary" onclick="reorder(${order.id})">🔄 Reorder</button>
                    <button class="btn-sm btn-secondary" onclick="viewOrderDetails(${order.id})">View Details</button>
                </div>
            </div>
        </div>
    `).join('');
}

async function reorder(orderId) {
    console.log('Reorder called with orderId:', orderId);
    console.log('Order history:', orderHistory);
    const order = orderHistory.find(o => o.id === orderId);
    console.log('Found order:', order);
    
    if (!order) {
        console.warn('Order not found');
        showToast('Order not found', 'error');
        return;
    }
    
    // Clear current cart
    cart = [];
    
    // Add items from order to cart
    const items = typeof order.items === 'string' ? JSON.parse(order.items) : order.items;
    console.log('Order items:', items);
    
    for (const item of items) {
        // Convert both to numbers for comparison
        const dishId = parseInt(item.dish_id);
        const dish = dishes.find(d => parseInt(d.id) === dishId);
        console.log('Looking for dish:', item.dish_id, '(parsed:', dishId, ') Found:', dish);
        console.log('Available dish IDs:', dishes.map(d => d.id));
        if (dish) {
            cart.push({
                dish_id: dish.id,
                dish: dish,
                quantity: item.quantity || 1,
                price: dish.price
            });
        } else {
            console.warn('Dish not found in current dishes list:', item.dish_id);
            showToast(`Dish "${item.dish_name || 'Unknown'}" is no longer available`, 'warning');
        }
    }
    
    console.log('Cart after reorder:', cart);
    
    if (cart.length === 0) {
        showToast('None of the dishes from this order are currently available', 'warning');
        return;
    }
    
    saveCart();
    updateCartUI();
    showToast(`${cart.length} item(s) added to cart!`, 'success');
    toggleCart(); // Open cart to show items
}

async function repeatLastOrder() {
    if (orderHistory.length === 0) {
        showToast('No previous orders found', 'warning');
        return;
    }
    
    const lastOrder = orderHistory[0];
    await reorder(lastOrder.id);
}


function formatStatus(status) {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Favorites
function isFavorite(dishId) {
    return favorites.some(f => f.dish_id === dishId);
}

async function toggleFavorite(dishId) {
    if (isFavorite(dishId)) {
        await removeFavorite(dishId);
    } else {
        await addFavorite(dishId);
    }
}

async function addFavorite(dishId) {
    try {
        const token = localStorage.getItem('token');
        
        if (!token) {
            console.error('No auth token found');
            showToast('Please log in to add favorites', 'error');
            return;
        }
        
        console.log('Adding favorite, dish ID:', dishId);
        console.log('Token exists:', !!token);
        
        const response = await fetch(`${CONSUMER_API_URL}/consumer/favorites`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ dish_id: dishId })
        });
        
        console.log('Add favorite response:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Favorite added successfully:', data);
            // Reload favorites to get complete data
            await loadFavorites();
            displayDishes(dishes);
            showToast('Added to favorites!', 'success');
        } else {
            const error = await response.json();
            console.error('Failed to add favorite:', error);
            showToast(error.error || 'Failed to add favorite', 'error');
        }
    } catch (error) {
        console.error('Error adding favorite:', error);
        showToast('Error adding favorite', 'error');
    }
}

async function removeFavorite(dishId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${CONSUMER_API_URL}/consumer/favorites/${dishId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            // Reload favorites to get updated data
            await loadFavorites();
            displayDishes(dishes);
            showToast('Removed from favorites', 'success');
        }
    } catch (error) {
        console.error('Error removing favorite:', error);
    }
}

async function loadFavorites() {
    try {
        const token = localStorage.getItem('token');
        console.log('Loading favorites, token exists:', !!token);
        const response = await fetch(`${CONSUMER_API_URL}/consumer/favorites`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Favorites loaded:', data);
            favorites = data.favorites || [];
            console.log('Favorites array:', favorites);
        }
    } catch (error) {
        console.error('Error loading favorites:', error);
    }
}

function showFavorites() {
    console.log('showFavorites called');
    console.log('Current favorites:', favorites);
    console.log('Current dishes:', dishes);
    const favoriteDishes = dishes.filter(d => isFavorite(d.id));
    console.log('Filtered favorite dishes:', favoriteDishes);
    const grid = document.getElementById('favoritesGrid');
    
    if (favoriteDishes.length === 0) {
        grid.innerHTML = '<div class="empty-state"><p>No favorites yet. Start adding dishes you love!</p></div>';
        return;
    }
    
    grid.innerHTML = favoriteDishes.map(dish => `
        <div class="dish-card" onclick="showDishDetails(${dish.id})">
            <div class="dish-image" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 3rem; height: 200px;">
                🍽️
            </div>
            <div class="dish-content">
                <div class="dish-header">
                    <div>
                        <div class="dish-name">${dish.name}</div>
                        <div class="dish-rating">⭐ ${dish.dish_rating || 4.5}</div>
                    </div>
                    <button class="favorite-btn active" onclick="event.stopPropagation(); toggleFavorite(${dish.id})">❤️</button>
                </div>
                <div class="dish-chef">👨‍🍳 ${dish.chef_name}</div>
                <div class="dish-footer">
                    <div class="dish-price">$${dish.price.toFixed(2)}</div>
                    <button class="add-to-cart-btn" onclick="event.stopPropagation(); addToCart(${dish.id})">Add to Cart</button>
                </div>
            </div>
        </div>
    `).join('');
}

// Rating
function showRatingModal(orderId) {
    currentRatingOrder = orderId;
    ratings = { food: 0, chef: 0, delivery: 0 };
    selectedTip = 0;
    
    // Reset UI
    document.querySelectorAll('.star').forEach(star => star.classList.remove('active'));
    document.querySelectorAll('.tip-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById('customTip').value = '';
    document.getElementById('reviewText').value = '';
    
    document.getElementById('ratingModal').style.display = 'flex';
}

function closeRatingModal() {
    document.getElementById('ratingModal').style.display = 'none';
    currentRatingOrder = null;
}

function setRating(type, value) {
    ratings[type] = value;
    
    // Update UI
    const container = document.getElementById(`${type}Rating`);
    const stars = container.querySelectorAll('.star');
    stars.forEach((star, index) => {
        if (index < value) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

function setTip(amount) {
    selectedTip = amount;
    document.querySelectorAll('.tip-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('customTip').value = '';
}

async function submitRating() {
    const customTip = parseFloat(document.getElementById('customTip').value) || 0;
    const finalTip = customTip || selectedTip;
    const review = document.getElementById('reviewText').value;
    
    if (ratings.food === 0 || ratings.chef === 0 || ratings.delivery === 0) {
        showToast('Please rate all aspects', 'warning');
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${CONSUMER_API_URL}/consumer/orders/${currentRatingOrder}/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                food_rating: ratings.food,
                chef_rating: ratings.chef,
                delivery_rating: ratings.delivery,
                tip: finalTip,
                review: review
            })
        });
        
        if (response.ok) {
            showToast('Thank you for your feedback!', 'success');
            closeRatingModal();
            await loadActiveOrders();
        } else {
            showToast('Failed to submit rating', 'error');
        }
    } catch (error) {
        console.error('Error submitting rating:', error);
        showToast('Failed to submit rating', 'error');
    }
}

// Notifications
async function loadNotifications() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${CONSUMER_API_URL}/consumer/notifications`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            notifications = data.notifications || [];
            updateNotificationsUI();
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

function updateNotificationsUI() {
    const list = document.getElementById('notificationsList');
    const badge = document.getElementById('notificationBadge');
    
    const unreadCount = notifications.filter(n => !n.is_read).length;
    
    if (unreadCount > 0) {
        badge.textContent = unreadCount;
        badge.style.display = 'block';
    } else {
        badge.style.display = 'none';
    }
    
    if (notifications.length === 0) {
        list.innerHTML = '<div class="empty-state"><p>No new notifications</p></div>';
        return;
    }
    
    list.innerHTML = notifications.map(notif => `
        <div class="notification-item ${notif.is_read ? '' : 'unread'}" onclick="markNotificationRead(${notif.id})">
            <div style="font-weight: 600; margin-bottom: 0.25rem;">${notif.title}</div>
            <div style="font-size: 0.9rem; color: #6b7280;">${notif.message}</div>
            <div style="font-size: 0.75rem; color: #9ca3af; margin-top: 0.25rem;">${formatTime(notif.created_at)}</div>
        </div>
    `).join('');
}

function toggleNotifications() {
    const panel = document.getElementById('notificationsPanel');
    panel.style.display = panel.style.display === 'none' ? 'flex' : 'none';
}

async function markNotificationRead(notifId) {
    try {
        const token = localStorage.getItem('token');
        await fetch(`${CONSUMER_API_URL}/consumer/notifications/${notifId}/read`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const notif = notifications.find(n => n.id === notifId);
        if (notif) notif.is_read = true;
        updateNotificationsUI();
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

// UI Helpers
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        content.style.display = 'none';
    });
    
    const activeTab = document.getElementById(`${tabName}Tab`);
    if (activeTab) {
        activeTab.classList.add('active');
        activeTab.style.display = 'block';
    }
    
    // Load tab-specific data
    if (tabName === 'favorites') {
        showFavorites();
    }
}

function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
}

function showProfile() {
    showToast('Profile page coming soon!', 'info');
}

function showSettings() {
    showToast('Settings page coming soon!', 'info');
}

// Search and Filter
function searchDishes() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    const filtered = dishes.filter(dish => 
        dish.name.toLowerCase().includes(query) ||
        dish.description.toLowerCase().includes(query) ||
        dish.chef_name.toLowerCase().includes(query) ||
        dish.cuisine_type.toLowerCase().includes(query)
    );
    displayDishes(filtered);
}

function filterDishes() {
    const area = document.getElementById('areaFilter').value;
    const cuisine = document.getElementById('cuisineFilter').value;
    const dietary = document.getElementById('dietaryFilter').value;
    const sort = document.getElementById('sortFilter').value;
    
    let filtered = [...dishes];
    
    if (area) {
        filtered = filtered.filter(d => d.area === area);
    }
    
    if (cuisine) {
        filtered = filtered.filter(d => d.cuisine_type === cuisine);
    }
    
    if (dietary) {
        filtered = filtered.filter(d => d.dietary_tags && d.dietary_tags.includes(dietary));
    }
    
    // Sort
    if (sort === 'rating') {
        filtered.sort((a, b) => (b.dish_rating || 0) - (a.dish_rating || 0));
    } else if (sort === 'price-low') {
        filtered.sort((a, b) => a.price - b.price);
    } else if (sort === 'price-high') {
        filtered.sort((a, b) => b.price - a.price);
    } else if (sort === 'distance') {
        filtered.sort((a, b) => (a.distance || 999) - (b.distance || 999));
    }
    
    displayDishes(filtered);
}

function populateAreaFilter() {
    const areas = [...new Set(dishes.map(d => d.area).filter(Boolean))];
    const select = document.getElementById('areaFilter');
    
    areas.forEach(area => {
        const option = document.createElement('option');
        option.value = area;
        option.textContent = area;
        select.appendChild(option);
    });
}

// Utility Functions
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
}

function showToast(message, type = 'info') {
    // Simple toast implementation
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function viewOrderDetails(orderId) {
    showToast('Order details coming soon!', 'info');
}

function setupRealTimeUpdates() {
    // Placeholder for WebSocket or polling implementation
    console.log('Real-time updates would be set up here');
}

// Expose functions to global scope
window.initConsumerDashboard = initConsumerDashboard;
window.switchTab = switchTab;
window.toggleCart = toggleCart;
window.toggleNotifications = toggleNotifications;
window.toggleUserMenu = toggleUserMenu;
// Cart functions
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.updateQuantity = updateQuantity;
window.proceedToCheckout = proceedToCheckout;
window.updateDeliveryType = updateDeliveryType;
window.closeCheckoutModal = closeCheckoutModal;
window.placeOrder = placeOrder;
// Dish functions
window.showDishDetails = showDishDetails;
window.closeDishModal = closeDishModal;
window.toggleFavorite = toggleFavorite;
window.showFavorites = showFavorites;
// Order functions
window.repeatLastOrder = repeatLastOrder;
window.reorder = reorder;
window.viewOrderDetails = viewOrderDetails;
// Rating functions
window.showRatingModal = showRatingModal;
window.closeRatingModal = closeRatingModal;
window.setRating = setRating;
window.setTip = setTip;
window.submitRating = submitRating;
// Search and filter
window.searchDishes = searchDishes;
window.filterDishes = filterDishes;
// Notifications
window.markNotificationRead = markNotificationRead;
// User menu
window.showProfile = showProfile;
window.showSettings = showSettings;
window.logout = logout;

console.log('✅ consumer.js loaded successfully');
