/**
 * Potluck Dashboard JavaScript
 * Handles dish management, orders, AI price suggestions, and feedback
 */

// Use API_URL from auth.js (already declared globally)
// If not available, define it on window object
if (typeof API_URL === 'undefined') {
    window.API_URL = 'http://localhost:5000/api';
}
const CHEF_API_URL = window.API_URL || API_URL || 'http://localhost:5000/api';
const token = localStorage.getItem('token');
const user = JSON.parse(localStorage.getItem('user') || '{}');

// Check authentication
if (!token || user.user_type !== 'chef') {
    window.location.href = '/';
}

// Global state
let currentDishes = [];
let currentOrders = [];
let dashboardStats = {};
let currencySymbol = '$';
let currencyCode = 'USD';

// Initialize dashboard
async function initDashboard() {
    try {
        // Check if we have a valid token before making API calls
        if (!token || token === 'null' || token === 'undefined') {
            console.log('No valid token, showing default dashboard');
            showDefaultDashboard();
            displayDishes([]);
            displayOrders([]);
            return;
        }
        
        await loadDashboardData();
        await loadDishes();
        await loadOrders('pending');
    } catch (error) {
        console.error('Dashboard initialization error:', error);
        // Don't show error, just use default data
        await showDefaultDashboard();
        await displayDishes([]);
        await displayOrders([]);
    }
}

// Load dashboard statistics
async function loadDashboardData() {
    try {
        const response = await fetch(`${CHEF_API_URL}/chef/dashboard`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            dashboardStats = data.data.stats;
            updateDashboardUI(data.data);
        } else {
            throw new Error(data.error || 'Failed to load dashboard');
        }
    } catch (error) {
        console.error('Load dashboard error:', error);
        // Show default dashboard data instead of throwing
        await showDefaultDashboard();
        throw error;
    }
}

// Show default dashboard when API fails
async function showDefaultDashboard() {
    document.querySelector('.stats-grid').innerHTML = `
        <div class="stat-card">
            <h3>0</h3>
            <p data-i18n="active_dishes">Active Dishes</p>
        </div>
        <div class="stat-card">
            <h3>0</h3>
            <p data-i18n="pending_orders">Pending Orders</p>
        </div>
        <div class="stat-card">
            <h3>$0.00</h3>
            <p data-i18n="total_earnings">Total Earnings</p>
        </div>
        <div class="stat-card">
            <h3>0.0</h3>
            <p><span data-i18n="average_rating">Average Rating</span> (0 <span data-i18n="reviews">reviews</span>)</p>
        </div>
    `;
    
    // Re-translate the page to update the new elements
    if (typeof translatePage === 'function') {
        await translatePage();
    }
}

// Update dashboard UI
async function updateDashboardUI(data) {
    // Set currency from API response
    if (data.currency) {
        currencySymbol = data.currency.symbol;
        currencyCode = data.currency.code;
        console.log(`Currency set to: ${currencyCode} (${currencySymbol})`);
    }
    
    // Update stats
    const stats = data.stats;
    document.querySelector('.stats-grid').innerHTML = `
        <div class="stat-card">
            <h3>${stats.active_dishes}</h3>
            <p data-i18n="active_dishes">Active Dishes</p>
        </div>
        <div class="stat-card">
            <h3>${stats.pending_orders}</h3>
            <p data-i18n="pending_orders">Pending Orders</p>
        </div>
        <div class="stat-card">
            <h3>${currencySymbol}${stats.total_earnings.toFixed(2)}</h3>
            <p data-i18n="total_earnings">Total Earnings</p>
        </div>
        <div class="stat-card">
            <h3>${stats.avg_rating.toFixed(1)} ⭐</h3>
            <p><span data-i18n="average_rating">Average Rating</span> (${stats.rating_count} <span data-i18n="reviews">reviews</span>)</p>
        </div>
    `;
    
    // Re-translate the page to update the new elements
    if (typeof translatePage === 'function') {
        await translatePage();
    }
    
    // Update welcome message
    if (typeof t === 'function') {
        document.getElementById('welcomeText').textContent = await t('welcome_back', { name: data.chef.name });
    } else {
        document.getElementById('welcomeText').textContent = `Welcome back, ${data.chef.name}!`;
    }
}

// Load dishes
async function loadDishes() {
    try {
        const response = await fetch(`${CHEF_API_URL}/chef/dishes`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentDishes = data.data;
            displayDishes(currentDishes);
        } else {
            throw new Error(data.error || 'Failed to load dishes');
        }
    } catch (error) {
        console.error('Load dishes error:', error);
        // Show empty dishes grid instead of error
        await displayDishes([]);
    }
}

// Display dishes
async function displayDishes(dishes) {
    const dishesGrid = document.getElementById('dishesGrid');
    
    if (!dishes || dishes.length === 0) {
        dishesGrid.innerHTML = `
            <div class="empty-state">
                <i class="material-icons">restaurant</i>
                <h3 data-i18n="no_dishes">No dishes yet</h3>
                <p data-i18n="start_adding">Start by adding your first dish!</p>
            </div>
        `;
        // Re-translate the empty state
        if (typeof translatePage === 'function') {
            await translatePage();
        }
        return;
    }
    
    dishesGrid.innerHTML = dishes.map(dish => `
        <div class="dish-card" data-dish-id="${dish.id}">
            <div class="dish-header">
                <h3>${dish.name}</h3>
                <span class="dish-status ${dish.is_available ? 'available' : 'unavailable'}" data-i18n="${dish.is_available ? 'available' : 'unavailable'}">
                    ${dish.is_available ? 'Available' : 'Unavailable'}
                </span>
            </div>
            <p class="dish-description">${dish.description}</p>
            <div class="dish-meta">
                <span><i class="material-icons">restaurant</i> ${dish.cuisine_type}</span>
                <span><i class="material-icons">schedule</i> ${dish.meal_type}</span>
                <span><i class="material-icons">local_fire_department</i> <span data-i18n="spice">Spice</span>: ${dish.spice_level}/5</span>
            </div>
            <div class="dish-price">
                <span class="price">${currencySymbol}${dish.price}</span>
                <span class="portion">${dish.portion_size}</span>
            </div>
            ${dish.order_count ? `
            <div class="dish-stats">
                <span>${dish.order_count} <span data-i18n="orders">orders</span></span>
                ${dish.avg_rating ? `<span>⭐ ${dish.avg_rating.toFixed(1)}</span>` : ''}
            </div>
            ` : ''}
            <div class="dish-actions">
                <button class="btn-action btn-edit" onclick="editDish(${dish.id})">
                    <i class="material-icons">edit</i> <span data-i18n="edit">Edit</span>
                </button>
                <button class="btn-action btn-toggle" onclick="toggleDishAvailability(${dish.id}, ${dish.is_available})">
                    <i class="material-icons">${dish.is_available ? 'visibility_off' : 'visibility'}</i>
                    <span data-i18n="${dish.is_available ? 'hide' : 'show'}">${dish.is_available ? 'Hide' : 'Show'}</span>
                </button>
                <button class="btn-action btn-delete" onclick="deleteDish(${dish.id})">
                    <i class="material-icons">delete</i> <span data-i18n="delete">Delete</span>
                </button>
            </div>
        </div>
    `).join('');
    
    // Re-translate the dish cards
    if (typeof translatePage === 'function') {
        await translatePage();
    }
}

// Show add dish modal
function showAddDishModal() {
    const modalHTML = `
        <div class="modal active" id="dishModal">
            <div class="modal-content-large">
                <div class="modal-header">
                    <h2>Add New Dish</h2>
                    <button class="btn-close" onclick="closeDishModal()">
                        <i class="material-icons">close</i>
                    </button>
                </div>
                <form id="dishForm" onsubmit="handleDishSubmit(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Dish Name *</label>
                            <input type="text" name="name" required>
                        </div>
                        <div class="form-group">
                            <label>Price * <small style="color: #bc2106;">(Click AI Suggest for best pricing)</small></label>
                            <div class="price-input-group">
                                <input type="number" step="0.01" name="price" id="dishPrice" required oninput="checkPriceRange()">
                                <button type="button" class="btn-ai-suggest" onclick="getAIPriceSuggestion()">
                                    <i class="material-icons">psychology</i> AI Suggest
                                </button>
                            </div>
                            <div id="priceWarning" class="price-warning" style="display: none; color: #ff6b6b; margin-top: 5px; font-size: 0.9rem;"></div>
                            <div id="pricesuggestion" class="price-suggestion"></div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Description *</label>
                        <textarea name="description" rows="3" required></textarea>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Cuisine Type *</label>
                            <select name="cuisine_type" required>
                                <option value="">Select cuisine</option>
                                <option value="Mexican">Mexican</option>
                                <option value="Indian">Indian</option>
                                <option value="Italian">Italian</option>
                                <option value="Chinese">Chinese</option>
                                <option value="American">American</option>
                                <option value="Thai">Thai</option>
                                <option value="Mediterranean">Mediterranean</option>
                                <option value="Japanese">Japanese</option>
                                <option value="French">French</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Meal Type *</label>
                            <select name="meal_type" required>
                                <option value="">Select meal type</option>
                                <option value="breakfast">Breakfast</option>
                                <option value="lunch">Lunch</option>
                                <option value="dinner">Dinner</option>
                                <option value="snack">Snack/Appetizer</option>
                                <option value="dessert">Dessert</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Portion Size *</label>
                            <input type="text" name="portion_size" placeholder="e.g., Serves 2" required>
                        </div>
                        <div class="form-group">
                            <label>Preparation Time (minutes)</label>
                            <input type="number" name="preparation_time" value="30">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Spice Level</label>
                            <select name="spice_level">
                                <option value="1">1 - Mild</option>
                                <option value="2">2 - Medium</option>
                                <option value="3">3 - Spicy</option>
                                <option value="4">4 - Very Spicy</option>
                                <option value="5">5 - Extremely Hot</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Calories (optional)</label>
                            <input type="number" name="calories">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Ingredients (comma separated) *</label>
                        <textarea name="ingredients" rows="2" placeholder="chicken, rice, spices, tomatoes" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Allergens (comma separated)</label>
                        <input type="text" name="allergens" placeholder="dairy, nuts, gluten">
                    </div>
                    
                    <div class="form-group">
                        <label>Dietary Tags</label>
                        <div class="dietary-tags">
                            <label><input type="checkbox" name="dietary_vegetarian" value="vegetarian"> Vegetarian</label>
                            <label><input type="checkbox" name="dietary_vegan" value="vegan"> Vegan</label>
                            <label><input type="checkbox" name="dietary_gluten_free" value="gluten-free"> Gluten-Free</label>
                            <label><input type="checkbox" name="dietary_dairy_free" value="dairy-free"> Dairy-Free</label>
                            <label><input type="checkbox" name="dietary_halal" value="halal"> Halal</label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" name="is_available" checked>
                            Make dish available immediately
                        </label>
                    </div>
                    
                    <div class="modal-footer">
                        <button type="button" class="btn-cancel" onclick="closeDishModal()">Cancel</button>
                        <button type="submit" class="btn-save">Add Dish</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// Close dish modal
function closeDishModal() {
    const modal = document.getElementById('dishModal');
    if (modal) {
        modal.remove();
    }
}

// Store AI suggestion for price validation
let lastAISuggestion = null;

// Show price rejection modal with contextual information
function showPriceRejectionModal(rejection) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'priceRejectionModal';
    
    const premiumBadge = rejection.has_premium_ingredients 
        ? '<span class="premium-badge">🌟 Premium Ingredients</span>' 
        : '';
    
    const percentOver = Math.round((rejection.your_price / rejection.suggested - 1) * 100);
    
    modal.innerHTML = `
        <div class="modal price-rejection-modal">
            <div class="modal-header">
                <h2>⚠️ Price Too High</h2>
                <button class="close-modal" onclick="closePriceRejectionModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="rejection-info">
                    <h3>"${rejection.dish_name}" ${premiumBadge}</h3>
                    <p class="explanation">${rejection.explanation}</p>
                    
                    <div class="price-comparison">
                        <div class="price-item rejected">
                            <label>Your Price</label>
                            <span class="price">${currencySymbol}${rejection.your_price.toFixed(2)}</span>
                            <span class="badge-red">${percentOver}% too high</span>
                        </div>
                        <div class="arrow">→</div>
                        <div class="price-item recommended">
                            <label>AI Recommended</label>
                            <span class="price">${currencySymbol}${rejection.suggested.toFixed(2)}</span>
                            <span class="badge-green">Optimal</span>
                        </div>
                    </div>
                    
                    <div class="cost-breakdown">
                        <h4>💰 Cost Breakdown</h4>
                        <div class="breakdown-item">
                            <span>Ingredients Cost:</span>
                            <span>${currencySymbol}${rejection.breakdown.ingredients_cost.toFixed(2)}</span>
                        </div>
                        <div class="breakdown-item">
                            <span>Total Cost:</span>
                            <span>${currencySymbol}${rejection.breakdown.total_cost.toFixed(2)}</span>
                        </div>
                        <div class="breakdown-item">
                            <span>Recommended Margin:</span>
                            <span>${rejection.breakdown.margin.toFixed(0)}%</span>
                        </div>
                        <hr>
                        <div class="breakdown-item total">
                            <span><strong>Suggested Price:</strong></span>
                            <span><strong>${currencySymbol}${rejection.suggested.toFixed(2)}</strong></span>
                        </div>
                        <div class="breakdown-item max">
                            <span>Maximum Allowed:</span>
                            <span>${currencySymbol}${rejection.max.toFixed(2)}</span>
                        </div>
                    </div>
                    
                    ${rejection.reasoning ? `
                    <div class="ai-reasoning">
                        <h4>🤖 AI Analysis</h4>
                        <p>${rejection.reasoning}</p>
                    </div>
                    ` : ''}
                    
                    <div class="price-suggestions">
                        <p><strong>💡 Suggestion:</strong> Use ${currencySymbol}${rejection.suggested.toFixed(2)} for competitive pricing, or up to ${currencySymbol}${rejection.max.toFixed(2)} for premium positioning.</p>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-primary" onclick="useSuggestedPrice(${rejection.suggested})">
                    Use ${currencySymbol}${rejection.suggested.toFixed(2)}
                </button>
                <button class="btn btn-secondary" onclick="useMaxPrice(${rejection.max})">
                    Use Max ${currencySymbol}${rejection.max.toFixed(2)}
                </button>
                <button class="btn btn-outline" onclick="closePriceRejectionModal()">
                    Edit Manually
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function closePriceRejectionModal() {
    const modal = document.getElementById('priceRejectionModal');
    if (modal) {
        modal.remove();
    }
}

function useSuggestedPrice(price) {
    document.getElementById('dishPrice').value = price.toFixed(2);
    checkPriceRange();
    closePriceRejectionModal();
    showSuccess(`Price updated to recommended ${currencySymbol}${price.toFixed(2)}`);
}

function useMaxPrice(price) {
    document.getElementById('dishPrice').value = price.toFixed(2);
    checkPriceRange();
    closePriceRejectionModal();
    showSuccess(`Price updated to maximum ${currencySymbol}${price.toFixed(2)}`);
}

// Check if manually entered price is reasonable
function checkPriceRange() {
    const priceInput = document.getElementById('dishPrice');
    const warningDiv = document.getElementById('priceWarning');
    const price = parseFloat(priceInput.value);
    
    if (!price || price <= 0) {
        warningDiv.style.display = 'none';
        return;
    }
    
    // General sanity checks
    if (price > 100) {
        warningDiv.style.display = 'block';
        warningDiv.innerHTML = '⚠️ <strong>$' + price + ' is extremely high!</strong> Most homemade dishes are under $30. Please use AI Suggest for guidance.';
        return;
    } else if (price > 50) {
        warningDiv.style.display = 'block';
        warningDiv.innerHTML = '⚠️ <strong>$' + price + ' seems very high.</strong> Consider using AI Suggest to get optimal pricing.';
        return;
    }
    
    // Check against AI suggestion if available
    if (lastAISuggestion) {
        const maxPrice = lastAISuggestion.max_price;
        const suggested = lastAISuggestion.suggested_price;
        
        if (price > maxPrice * 2) {
            warningDiv.style.display = 'block';
            warningDiv.innerHTML = `⚠️ <strong>${currencySymbol}${price} is ${Math.round((price/suggested)*100)}% above AI recommendation!</strong> AI suggests ${currencySymbol}${suggested} (max ${currencySymbol}${maxPrice})`;
        } else if (price > maxPrice * 1.5) {
            warningDiv.style.display = 'block';
            warningDiv.innerHTML = `⚠️ Price is ${Math.round((price/suggested - 1)*100)}% above AI suggestion. Recommended: ${currencySymbol}${suggested}`;
        } else {
            warningDiv.style.display = 'none';
        }
    } else {
        // No AI suggestion yet, just basic warning
        if (price > 30) {
            warningDiv.style.display = 'block';
            warningDiv.innerHTML = '💡 Tip: Click "AI Suggest" to get optimal pricing based on actual costs.';
        } else {
            warningDiv.style.display = 'none';
        }
    }
}

// Get AI price suggestion
async function getAIPriceSuggestion() {
    const form = document.getElementById('dishForm');
    const formData = new FormData(form);
    
    const name = formData.get('name');
    const cuisine_type = formData.get('cuisine_type');
    const ingredients = formData.get('ingredients');
    const portion_size = formData.get('portion_size');
    
    if (!name || !cuisine_type || !ingredients) {
        showError('Please fill in dish name, cuisine type, and ingredients first');
        return;
    }
    
    const suggestionDiv = document.getElementById('pricesuggestion');
    suggestionDiv.innerHTML = '<div class="loading">🤖 AI is calculating the best price...</div>';
    
    try {
        const response = await fetch(`${CHEF_API_URL}/chef/price-suggestion`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                cuisine_type,
                ingredients: ingredients.split(',').map(i => i.trim()),
                portion_size
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.data.ai_suggestion) {
            const pricing = data.data.ai_suggestion.pricing;
            
            // Store for validation
            lastAISuggestion = pricing;
            
            // Clear any warnings
            const warningDiv = document.getElementById('priceWarning');
            if (warningDiv) warningDiv.style.display = 'none';
            
            suggestionDiv.innerHTML = `
                <div class="price-suggestion-box">
                    <div class="suggestion-header">
                        <h4>🤖 AI Price Recommendation</h4>
                        ${data.data.ai_suggestion.fallback ? '<span class="badge">Rule-based</span>' : '<span class="badge ai">AI-powered</span>'}
                    </div>
                    <div class="price-range">
                        <div class="price-option">
                            <label>Min Price</label>
                            <span class="price">${currencySymbol}${pricing.min_price}</span>
                            <button type="button" class="btn-use-price" onclick="document.getElementById('dishPrice').value = ${pricing.min_price}">Use</button>
                        </div>
                        <div class="price-option recommended">
                            <label>Recommended</label>
                            <span class="price">${currencySymbol}${pricing.suggested_price}</span>
                            <button type="button" class="btn-use-price" onclick="document.getElementById('dishPrice').value = ${pricing.suggested_price}">Use</button>
                        </div>
                        <div class="price-option">
                            <label>Max Price</label>
                            <span class="price">${currencySymbol}${pricing.max_price}</span>
                            <button type="button" class="btn-use-price" onclick="document.getElementById('dishPrice').value = ${pricing.max_price}">Use</button>
                        </div>
                    </div>
                    <div class="cost-breakdown">
                        <h5>Cost Breakdown (${currencyCode}):</h5>
                        <ul>
                            <li>Ingredients: ${currencySymbol}${pricing.cost_breakdown.ingredients}</li>
                            <li>Utilities: ${currencySymbol}${pricing.cost_breakdown.utilities}</li>
                            <li>Packaging: ${currencySymbol}${pricing.cost_breakdown.packaging}</li>
                            <li>Platform Fee (10%): ${currencySymbol}${pricing.cost_breakdown.platform_fee}</li>
                            <li><strong>Your Profit: ${currencySymbol}${pricing.cost_breakdown.profit}</strong></li>
                        </ul>
                    </div>
                    <div class="pricing-tip">
                        <p><strong>💡 Tip:</strong> ${pricing.tips}</p>
                        <p><small>Restaurant price for reference: ${currencySymbol}${pricing.restaurant_comparison} (not recommended for homemade)</small></p>
                    </div>
                    <div class="pricing-reasoning">
                        <details>
                            <summary>How was this calculated?</summary>
                            <p>${pricing.reasoning}</p>
                        </details>
                    </div>
                </div>
            `;
        } else {
            suggestionDiv.innerHTML = '<div class="error">Could not get price suggestion. Please set price manually.</div>';
        }
    } catch (error) {
        console.error('Price suggestion error:', error);
        suggestionDiv.innerHTML = '<div class="error">Failed to get price suggestion. Please try again.</div>';
    }
}

// Handle dish form submission
async function handleDishSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Parse ingredients and allergens
    const ingredients = formData.get('ingredients').split(',').map(i => i.trim()).filter(i => i);
    const allergens = formData.get('allergens') ? formData.get('allergens').split(',').map(a => a.trim()).filter(a => a) : [];
    
    // Get dietary tags
    const dietary_tags = [];
    if (formData.get('dietary_vegetarian')) dietary_tags.push('vegetarian');
    if (formData.get('dietary_vegan')) dietary_tags.push('vegan');
    if (formData.get('dietary_gluten_free')) dietary_tags.push('gluten-free');
    if (formData.get('dietary_dairy_free')) dietary_tags.push('dairy-free');
    if (formData.get('dietary_halal')) dietary_tags.push('halal');
    
    const dishData = {
        name: formData.get('name'),
        description: formData.get('description'),
        price: parseFloat(formData.get('price')),
        cuisine_type: formData.get('cuisine_type'),
        meal_type: formData.get('meal_type'),
        ingredients,
        allergens,
        dietary_tags,
        spice_level: parseInt(formData.get('spice_level')),
        portion_size: formData.get('portion_size'),
        preparation_time: parseInt(formData.get('preparation_time') || 30),
        calories: formData.get('calories') ? parseInt(formData.get('calories')) : null,
        is_available: formData.get('is_available') ? 1 : 0
    };
    
    try {
        const dishId = form.dataset.dishId;
        const url = dishId ? `${CHEF_API_URL}/chef/dishes/${dishId}` : `${CHEF_API_URL}/chef/dishes`;
        const method = dishId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dishData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message || 'Dish saved successfully!');
            closeDishModal();
            await loadDishes();
            await loadDashboardData();
        } else {
            // Check if it's a price validation error with detailed rejection info
            if (data.price_rejection) {
                showPriceRejectionModal(data.price_rejection);
            } else {
                showError(data.error || 'Failed to save dish');
            }
        }
    } catch (error) {
        console.error('Save dish error:', error);
        showError('Failed to save dish. Please try again.');
    }
}

// Edit dish
async function editDish(dishId) {
    const dish = currentDishes.find(d => d.id === dishId);
    if (!dish) {
        showError('Dish not found');
        return;
    }
    
    // Show modal with dish data pre-filled
    showAddDishModal();
    
    // Wait for modal to render
    setTimeout(() => {
        const form = document.getElementById('dishForm');
        form.dataset.dishId = dishId;
        form.querySelector('[name="name"]').value = dish.name;
        form.querySelector('[name="description"]').value = dish.description;
        form.querySelector('[name="price"]').value = dish.price;
        form.querySelector('[name="cuisine_type"]').value = dish.cuisine_type;
        form.querySelector('[name="meal_type"]').value = dish.meal_type;
        form.querySelector('[name="portion_size"]').value = dish.portion_size;
        form.querySelector('[name="preparation_time"]').value = dish.preparation_time;
        form.querySelector('[name="spice_level"]').value = dish.spice_level;
        if (dish.calories) form.querySelector('[name="calories"]').value = dish.calories;
        form.querySelector('[name="ingredients"]').value = dish.ingredients.join(', ');
        if (dish.allergens.length) form.querySelector('[name="allergens"]').value = dish.allergens.join(', ');
        form.querySelector('[name="is_available"]').checked = dish.is_available;
        
        // Check dietary tags
        dish.dietary_tags.forEach(tag => {
            const checkbox = form.querySelector(`[name="dietary_${tag.replace('-', '_')}"]`);
            if (checkbox) checkbox.checked = true;
        });
        
        document.querySelector('#dishModal h2').textContent = 'Edit Dish';
        document.querySelector('#dishModal .btn-save').textContent = 'Update Dish';
    }, 100);
}

// Toggle dish availability
async function toggleDishAvailability(dishId, currentStatus) {
    try {
        const response = await fetch(`${CHEF_API_URL}/chef/dishes/${dishId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                is_available: currentStatus ? 0 : 1
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(currentStatus ? 'Dish hidden' : 'Dish made available');
            await loadDishes();
            await loadDashboardData();
        } else {
            showError(data.error || 'Failed to update dish');
        }
    } catch (error) {
        console.error('Toggle availability error:', error);
        showError('Failed to update dish availability');
    }
}

// Delete dish
async function deleteDish(dishId) {
    if (!confirm('Are you sure you want to delete this dish? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${CHEF_API_URL}/chef/dishes/${dishId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Dish deleted successfully');
            await loadDishes();
            await loadDashboardData();
        } else {
            showError(data.error || 'Failed to delete dish');
        }
    } catch (error) {
        console.error('Delete dish error:', error);
        showError('Failed to delete dish');
    }
}

// Load orders
async function loadOrders(status = 'all') {
    try {
        const response = await fetch(`${CHEF_API_URL}/chef/orders?status=${status}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentOrders = data.data;
            displayOrders(currentOrders);
        } else {
            throw new Error(data.error || 'Failed to load orders');
        }
    } catch (error) {
        console.error('Load orders error:', error);
        // Show empty orders instead of error
        displayOrders([]);
    }
}

// Display orders (Implementation continues...)
function displayOrders(orders) {
    // This will be called from the orders page
    console.log('Orders loaded:', orders.length);
}

// View orders page
function viewOrders() {
    window.location.href = '/pages/chef-orders.html';
}

// Utility functions
function showSuccess(message) {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = 'toast success';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function showError(message) {
    const toast = document.createElement('div');
    toast.className = 'toast error';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

// Expose functions to global scope for HTML onclick handlers
window.initDashboard = initDashboard;
window.viewOrders = viewOrders;
window.editDish = editDish;
window.toggleDishAvailability = toggleDishAvailability;
window.toggleDishStatus = toggleDishAvailability; // Alias for compatibility
window.deleteDish = deleteDish;
window.openAddDishModal = openAddDishModal;
window.showAddDishModal = showAddDishModal;
window.closeAddDishModal = closeDishModal;
window.closeDishModal = closeDishModal;
window.handleDishSubmit = handleDishSubmit;
window.updateOrderStatus = updateOrderStatus;

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}

console.log('Chef dashboard initialized');
