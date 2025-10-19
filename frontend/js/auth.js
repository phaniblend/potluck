// Authentication JavaScript for Potluck

// API Configuration
// Use environment-aware base URL (works both locally and in production)
const API_URL = (typeof window !== 'undefined' && window.location && window.location.origin)
    ? `${window.location.origin}/api`
    : '/api';
// Expose globally for other scripts
window.API_URL = API_URL;

// Centralized logout function for all user roles
function logout() {
    try {
        // Clear all stored data
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('userLang');
        localStorage.removeItem('userLangManual');
        localStorage.removeItem('userLocation');
        
        // Show logout confirmation
        if (typeof showToast === 'function') {
            showToast('Logged out successfully!', 'success');
        } else {
            alert('Logged out successfully!');
        }
        
        // Redirect to login page
        setTimeout(() => {
            window.location.href = '/';
        }, 1000);
        
    } catch (error) {
        console.error('Logout error:', error);
        // Force redirect even if there's an error
        window.location.href = '/';
    }
}

// Make logout function globally available
window.logout = logout;

// Switch between login and signup tabs
function switchTab(tab) {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loginTab = document.querySelector('[onclick="switchTab(\'login\')"]');
    const signupTab = document.querySelector('[onclick="switchTab(\'signup\')"]');
    
    if (tab === 'login') {
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
        if (loginTab) loginTab.classList.add('active');
        if (signupTab) signupTab.classList.remove('active');
    } else if (tab === 'signup') {
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
        if (signupTab) signupTab.classList.add('active');
        if (loginTab) loginTab.classList.remove('active');
    }
}

// Select user role during signup
let selectedRole = 'consumer';

function selectRole(role) {
    selectedRole = role;
    
    // Update UI to show selected role
    document.querySelectorAll('.role-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    const selectedOption = document.querySelector(`[data-role="${role}"]`);
    if (selectedOption) {
        selectedOption.classList.add('selected');
    }
}

// Check service area availability
async function checkServiceArea() {
    const city = document.getElementById('signupCity').value.trim();
    const state = document.getElementById('signupState').value.trim();
    const zip_code = document.getElementById('signupZip').value.trim();
    const serviceStatus = document.getElementById('serviceStatus');
    const signupBtn = document.getElementById('signupBtn');
    
    if (!city || !state) {
        showError('Please enter both city and state');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/validate-location`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                city, 
                state, 
                zip_code,
                user_type: selectedRole  // Pass the selected role
            })
        });
        
        const data = await response.json();
        
        serviceStatus.style.display = 'block';
        
        if (data.valid) {
            serviceStatus.className = 'service-status available';
            
            // Different messages based on user type and situation
            if (selectedRole === 'chef') {
                if (data.is_new_service_area) {
                    serviceStatus.innerHTML = `✓ <strong>Welcome Chef!</strong><br>${data.message}<br><small>You'll be pioneering food service in this area!</small>`;
                } else {
                    serviceStatus.innerHTML = `✓ ${data.message}`;
                }
                signupBtn.disabled = false;
            } else if (selectedRole === 'consumer') {
                if (data.has_local_chefs) {
                    serviceStatus.innerHTML = `✓ ${data.message}`;
                } else {
                    // Show warning about no local chefs
                    serviceStatus.className = 'service-status available';
                    let message = `⚠️ ${data.message}`;
                    if (data.warning) {
                        message += `<br><small><strong>Note:</strong> ${data.warning}</small>`;
                    }
                    if (data.nearest_chefs && data.nearest_chefs.length > 0) {
                        message += `<br><small><strong>Nearby chefs:</strong><br>`;
                        data.nearest_chefs.forEach(chef => {
                            message += `• ${chef.name} in ${chef.city}, ${chef.state}<br>`;
                        });
                        message += '</small>';
                    }
                    serviceStatus.innerHTML = message;
                }
                signupBtn.disabled = false;
            } else if (selectedRole === 'delivery') {
                // Delivery agents can signup and add service areas
                if (data.has_local_chefs) {
                    serviceStatus.innerHTML = `✓ ${data.message}<br><small>You can start delivering orders in this area!</small>`;
                } else {
                    // No chefs yet, but DA can still register and add service areas
                    serviceStatus.innerHTML = `✓ ${data.message}<br><small>${data.note || 'You can add service areas from your dashboard after registration.'}</small>`;
                }
                signupBtn.disabled = false;
            }
        } else {
            // Invalid location (only for delivery agents without chefs)
            serviceStatus.className = 'service-status unavailable';
            serviceStatus.innerHTML = `✗ ${data.message}`;
            signupBtn.disabled = true;
        }
    } catch (error) {
        console.error('Error checking service area:', error);
        showError('Could not verify service area. Please try again.');
    }
}

// Detect user location automatically
async function detectUserLocation() {
    console.log('Detecting user location...');
    try {
        const response = await fetch(`${API_URL}/auth/detect-location`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        console.log('Location detected:', data);

        if (data.success && data.location) {
            return data.location;
        } else {
            // Return default location if detection fails
            return {
                city: 'Dallas',
                state: 'TX',
                country: 'United States',
                currency: 'USD',
                timezone: 'America/Chicago'
            };
        }
    } catch (error) {
        console.log('Error detecting location:', error);
        // Return default location on error
        return {
            city: 'Dallas',
            state: 'TX',
            country: 'United States',
            currency: 'USD',
            timezone: 'America/Chicago'
        };
    }
}

// Show error message
function showError(message) {
    const errorMsg = document.getElementById('errorMsg');
    const successMsg = document.getElementById('successMsg');
    
    errorMsg.textContent = message;
    errorMsg.style.display = 'block';
    successMsg.style.display = 'none';
    
    setTimeout(() => {
        errorMsg.style.display = 'none';
    }, 5000);
}

// Show success message
function showSuccess(message) {
    const errorMsg = document.getElementById('errorMsg');
    const successMsg = document.getElementById('successMsg');
    
    successMsg.textContent = message;
    successMsg.style.display = 'block';
    errorMsg.style.display = 'none';
    
    setTimeout(() => {
        successMsg.style.display = 'none';
    }, 5000);
}

// Handle login form submission
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value.trim();
            const password = document.getElementById('loginPassword').value;
            
            if (!email || !password) {
                showError('Please enter both email and password');
                return;
            }
            
            try {
                const response = await fetch(`${API_URL}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                console.log('Login response:', data);
                
                if (response.ok && data.success) {
                    showSuccess('Login successful! Redirecting...');
                    
                    // Handle nested data structure
                    const token = data.token || (data.data && data.data.token);
                    const user = data.user || (data.data && data.data.user);
                    
                    // Store user data and token
                    if (token) {
                        localStorage.setItem('token', token);
                        console.log('Token stored:', token.substring(0, 20) + '...');
                    }
                    if (user) {
                        localStorage.setItem('user', JSON.stringify(user));
                        console.log('User stored:', user);
                    }
                    
                    // Redirect based on user type
                    setTimeout(() => {
                        const userType = user.user_type;
                        console.log('Redirecting user type:', userType);
                        
                        if (userType === 'consumer') {
                            window.location.href = '/pages/consumer-dashboard.html';
                        } else if (userType === 'chef') {
                            window.location.href = '/pages/chef-dashboard.html';
                        } else if (userType === 'delivery') {
                            window.location.href = '/pages/delivery-dashboard.html';
                        } else {
                            showError('Unknown user type');
                        }
                    }, 1000);
                } else {
                    // Login failed
                    const errorMsg = data.message || data.error || 'Login failed. Please check your credentials.';
                    showError(errorMsg);
                    console.error('Login failed:', data);
                }
            } catch (error) {
                console.error('Login error:', error);
                showError('An error occurred during login. Please try again.');
            }
        });
    }
    
    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                user_type: selectedRole,
                full_name: document.getElementById('signupName').value,
                email: document.getElementById('signupEmail').value,
                phone: document.getElementById('signupPhone').value,
                password: document.getElementById('signupPassword').value,
                address: document.getElementById('signupAddress').value,
                city: document.getElementById('signupCity').value,
                state: document.getElementById('signupState').value,
                zip_code: document.getElementById('signupZip').value
            };
            
            try {
                const response = await fetch(`${API_URL}/auth/signup`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                console.log('Signup response:', data);
                
                if (data.success) {
                    showSuccess('Account created successfully! You can now login.');
                    
                    // Handle nested data structure (some responses have token/user in data object)
                    const token = data.token || (data.data && data.data.token);
                    const user = data.user || (data.data && data.data.user);
                    
                    // If we got a token back, store it and redirect (auto-login)
                    if (token && user) {
                        localStorage.setItem('token', token);
                        localStorage.setItem('user', JSON.stringify(user));
                        
                        showSuccess('Account created! Redirecting to dashboard...');
                        setTimeout(() => {
                            const userType = user.user_type;
                            if (userType === 'consumer') {
                                window.location.href = '/pages/consumer-dashboard.html';
                            } else if (userType === 'chef') {
                                window.location.href = '/pages/chef-dashboard.html';
                            } else if (userType === 'delivery') {
                                window.location.href = '/pages/delivery-dashboard.html';
                            }
                        }, 1500);
                    } else {
                        // Switch to login tab after 2 seconds
                        setTimeout(() => {
                            switchTab('login');
                            // Pre-fill email
                            document.getElementById('loginEmail').value = formData.email;
                        }, 2000);
                    }
                } else {
                    showError(data.message || data.error || 'Signup failed. Please try again.');
                }
            } catch (error) {
                console.error('Signup error:', error);
                showError('An error occurred during signup. Please try again.');
            }
        });
    }
});

// Check if user is already logged in
function checkAuth() {
    try {
        const token = localStorage.getItem('token');
        const userStr = localStorage.getItem('user');
        
        if (token && userStr && userStr !== 'undefined' && userStr !== 'null') {
            // User is logged in, redirect to appropriate dashboard
            const userData = JSON.parse(userStr);
            const userType = userData.user_type;
            
            if (userType === 'consumer') {
                window.location.href = '/pages/consumer-dashboard.html';
            } else if (userType === 'chef') {
                window.location.href = '/pages/chef-dashboard.html';
            } else if (userType === 'delivery') {
                window.location.href = '/pages/delivery-dashboard.html';
            }
        }
    } catch (error) {
        console.error('Auth check error:', error);
        // Clear invalid data
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    }
}

// Run auth check on page load
if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
    checkAuth();
}

console.log('Auth.js loaded successfully');
