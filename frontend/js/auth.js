// Authentication handling for Potluck
const API_URL = 'https://potluck-production-e91a.up.railway.app/api';
console.log('API_URL set to:', API_URL); // Debug log
let selectedRole = 'consumer';
let zipValidated = false;

// Switch between login and signup tabs
function switchTab(tab) {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const tabs = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(t => t.classList.remove('active'));
    
    if (tab === 'login') {
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
        tabs[0].classList.add('active');
    } else {
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
        tabs[1].classList.add('active');
    }
    
    clearMessages();
}

// Select user role
function selectRole(role) {
    selectedRole = role;
    document.querySelectorAll('.role-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    document.querySelector(`[data-role="${role}"]`).classList.add('selected');
    
    // Show/hide ZIP validation based on role
    const zipValidationSection = document.getElementById('zipValidationSection');
    const serviceStatusDiv = document.getElementById('serviceStatus');
    const signupBtn = document.getElementById('signupBtn');
    
    if (role === 'chef') {
        // Chefs are expanding service globally - auto-detect location
        zipValidationSection.style.display = 'none';
        serviceStatusDiv.style.display = 'block';
        serviceStatusDiv.innerHTML = '🌍 Detecting your location...';
        serviceStatusDiv.className = 'service-status validating';
        
        // Auto-detect location for chefs
        detectUserLocation().then(locationData => {
            if (locationData) {
                signupBtn.disabled = false;
                zipValidated = true;
            }
        });
    } else {
        // Consumers and Delivery Agents - auto-detect location first
        zipValidationSection.style.display = 'block';
        serviceStatusDiv.style.display = 'block';
        serviceStatusDiv.innerHTML = '🌍 Detecting your location...';
        serviceStatusDiv.className = 'service-status validating';
        
        // Auto-detect location
        detectUserLocation().then(locationData => {
            if (locationData) {
                signupBtn.disabled = false;
                zipValidated = true;
            }
        });
    }
}

// Automatically detect user location
async function detectUserLocation() {
    try {
        const url = `${API_URL}/auth/detect-location`;
        console.log('Detecting user location...');
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        if (data.success) {
            const locationData = data.data;
            console.log('Location detected:', locationData);
            
            // Auto-fill form fields
            if (locationData.city) {
                document.getElementById('signupCity').value = locationData.city;
                document.getElementById('signupCity').classList.add('valid');
            }
            
            if (locationData.state) {
                document.getElementById('signupState').value = locationData.state;
                document.getElementById('signupState').classList.add('valid');
            }
            
            if (locationData.postal_code) {
                document.getElementById('signupZip').value = locationData.postal_code;
            }
            
            // Show location info
            const statusDiv = document.getElementById('serviceStatus');
            statusDiv.className = 'service-status available';
            statusDiv.innerHTML = `🌍 Location detected: ${locationData.city}, ${locationData.state}, ${locationData.country}`;
            statusDiv.style.display = 'block';
            
            // Enable signup button
            zipValidated = true;
            document.getElementById('signupBtn').disabled = false;
            
            // Store localization data
            localStorage.setItem('userLocation', JSON.stringify(locationData));
            
            return locationData;
        } else {
            showError('Could not detect location automatically. Please fill in manually.');
            return null;
        }
    } catch (error) {
        console.error('Error detecting location:', error);
        showError('Error detecting location. Please fill in manually.');
        return null;
    }
}

// Check if zip code is serviceable (fallback for manual entry)
async function checkServiceArea() {
    const zip = document.getElementById('signupZip').value;
    if (!zip) {
        showError('Please enter a zip code');
        return;
    }
    
    try {
        const url = `${API_URL}/auth/check-service-area`;
        console.log('Making request to:', url); // Debug log
        console.log('Full URL being fetched:', url); // Additional debug
        console.log('Protocol:', window.location.protocol); // Check current page protocol
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({zip_code: zip})
        });
        
        const data = await response.json();
        const statusDiv = document.getElementById('serviceStatus');
        
        if (data.serviceable) {
            statusDiv.className = 'service-status available';
            statusDiv.innerHTML = `✅ ${data.message}`;
            statusDiv.style.display = 'block';
            zipValidated = true;
            document.getElementById('signupBtn').disabled = false;
        } else {
            statusDiv.className = 'service-status unavailable';
            statusDiv.innerHTML = `❌ Service not available in your area yet`;
            statusDiv.style.display = 'block';
            zipValidated = false;
            document.getElementById('signupBtn').disabled = true;
        }
    } catch (error) {
        showError('Error checking service area');
    }
}

// Validate city and state against real geographic data
async function validateCityState() {
    const city = document.getElementById('signupCity').value.trim();
    const state = document.getElementById('signupState').value.trim();
    
    if (!city || !state) {
        return false;
    }
    
    try {
        const url = `${API_URL}/auth/validate-location`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({city: city, state: state})
        });
        
        const data = await response.json();
        return data.valid;
    } catch (error) {
        console.error('Error validating city/state:', error);
        return false;
    }
}

// Real-time validation for city field
function validateCityInput() {
    const cityInput = document.getElementById('signupCity');
    const city = cityInput.value.trim();
    
    // Remove existing classes
    cityInput.classList.remove('valid', 'invalid', 'validating');
    
    if (city.length < 2) {
        cityInput.classList.remove('valid', 'invalid', 'validating');
        return;
    }
    
    // Check against common city patterns
    const cityPattern = /^[A-Za-z\s\-']+$/;
    if (!cityPattern.test(city)) {
        cityInput.classList.add('invalid');
        showError('City name contains invalid characters');
        return;
    }
    
    // Check for suspicious patterns
    const suspiciousPatterns = [
        /^[a-z]{10,}$/i,  // Long random strings
        /^[a-z]{2,}[0-9]{2,}[a-z]{2,}$/i,  // Mixed alphanumeric patterns
        /^[a-z]+[0-9]+[a-z]+$/i,  // Alternating letters and numbers
        /^[a-z]{5,}[0-9]{3,}$/i,  // Many letters followed by many numbers
    ];
    
    for (const pattern of suspiciousPatterns) {
        if (pattern.test(city)) {
            cityInput.classList.add('invalid');
            showError('Please enter a valid city name');
            return;
        }
    }
    
    cityInput.classList.add('valid');
}

// Real-time validation for state field
function validateStateInput() {
    const stateInput = document.getElementById('signupState');
    const state = stateInput.value.trim();
    
    // Remove existing classes
    stateInput.classList.remove('valid', 'invalid', 'validating');
    
    if (state.length < 2) {
        stateInput.classList.remove('valid', 'invalid', 'validating');
        return;
    }
    
    // Check against common state/province patterns
    const statePattern = /^[A-Za-z\s\-']+$/;
    if (!statePattern.test(state)) {
        stateInput.classList.add('invalid');
        showError('State/Province contains invalid characters');
        return;
    }
    
    // Check for suspicious patterns
    const suspiciousPatterns = [
        /^[a-z]{10,}$/i,  // Long random strings
        /^[a-z]{2,}[0-9]{2,}[a-z]{2,}$/i,  // Mixed alphanumeric patterns
        /^[a-z]+[0-9]+[a-z]+$/i,  // Alternating letters and numbers
        /^[a-z]{5,}[0-9]{3,}$/i,  // Many letters followed by many numbers
    ];
    
    for (const pattern of suspiciousPatterns) {
        if (pattern.test(state)) {
            stateInput.classList.add('invalid');
            showError('Please enter a valid state/province name');
            return;
        }
    }
    
    stateInput.classList.add('valid');
}

// Handle login
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store token and user info
            localStorage.setItem('token', data.data.token);
            localStorage.setItem('user', JSON.stringify(data.data.user));
            
            showSuccess('Login successful! Redirecting...');
            
            // Redirect based on role
            setTimeout(() => {
                redirectToDashboard(data.data.user.user_type);
            }, 1000);
        } else {
            showError(data.error || 'Login failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    }
});

// Handle signup
document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Require ZIP validation for consumers and delivery agents
    if ((selectedRole === 'consumer' || selectedRole === 'delivery') && !zipValidated) {
        showError('Please verify your zip code first');
        return;
    }
    
    // Validate city and state format
    const city = document.getElementById('signupCity').value.trim();
    const state = document.getElementById('signupState').value.trim();
    
    if (city.length < 2) {
        showError('Please enter a valid city name');
        return;
    }
    
    if (state.length < 2) {
        showError('Please enter a valid state/province');
        return;
    }
    
    // Check for suspicious patterns (likely bot input)
    const suspiciousPatterns = [
        /^[a-z]{10,}$/i,  // Long random strings
        /^[a-z]{2,}[0-9]{2,}[a-z]{2,}$/i,  // Mixed alphanumeric patterns
        /^[a-z]+[0-9]+[a-z]+$/i,  // Alternating letters and numbers
        /^[a-z]{5,}[0-9]{3,}$/i,  // Many letters followed by many numbers
    ];
    
    for (const pattern of suspiciousPatterns) {
        if (pattern.test(city) || pattern.test(state)) {
            showError('Please enter valid city and state names');
            return;
        }
    }
    
    const formData = {
        user_type: selectedRole,
        full_name: document.getElementById('signupName').value,
        email: document.getElementById('signupEmail').value,
        phone: document.getElementById('signupPhone').value,
        address: document.getElementById('signupAddress').value,
        city: document.getElementById('signupCity').value,
        state: document.getElementById('signupState').value,
        zip_code: document.getElementById('signupZip').value,
        password: document.getElementById('signupPassword').value
    };
    
    try {
        const url = `${API_URL}/auth/signup`;
        console.log('Making signup request to:', url); // Debug log
        console.log('Request data:', formData); // Debug log
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });
        
        console.log('Response status:', response.status); // Debug log
        console.log('Response headers:', response.headers); // Debug log
        
        if (!response.ok) {
            if (response.status === 0) {
                showError('Network error: Unable to connect to server. Please check your internet connection.');
                return;
            }
            if (response.status === 429) {
                showError('Too many signup attempts. Please wait 5 minutes before trying again.');
                return;
            }
            showError(`Server error (${response.status}). Please try again later.`);
            return;
        }
        
        const data = await response.json();
        console.log('Response data:', data); // Debug log
        
        if (data.success) {
            // Store token and user info
            localStorage.setItem('token', data.data.token);
            localStorage.setItem('user', JSON.stringify(data.data.user));
            
            showSuccess('Account created successfully! Redirecting...');
            
            // Redirect based on role
            setTimeout(() => {
                redirectToDashboard(formData.user_type);
            }, 1500);
        } else {
            showError(data.error || 'Signup failed');
        }
    } catch (error) {
        console.error('Signup error:', error); // Debug log
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            showError('Network error: Unable to connect to server. Please check your internet connection.');
        } else {
            showError('An unexpected error occurred. Please try again.');
        }
    }
});

// Redirect to appropriate dashboard
function redirectToDashboard(userType) {
    switch(userType) {
        case 'chef':
            window.location.href = '/pages/chef-dashboard.html';
            break;
        case 'delivery':
            window.location.href = '/pages/delivery-dashboard.html';
            break;
        default:
            window.location.href = '/pages/consumer-dashboard.html';
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('errorMsg');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Show success message
function showSuccess(message) {
    const successDiv = document.getElementById('successMsg');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
}

// Clear all messages
function clearMessages() {
    document.getElementById('errorMsg').style.display = 'none';
    document.getElementById('successMsg').style.display = 'none';
}

// Check if already logged in
window.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
        const userData = JSON.parse(user);
        redirectToDashboard(userData.user_type);
    }
    
    // Initialize role selection (consumer is default)
    selectRole('consumer');
    
    // Add real-time validation for city and state fields
    const cityInput = document.getElementById('signupCity');
    const stateInput = document.getElementById('signupState');
    
    if (cityInput) {
        cityInput.addEventListener('input', validateCityInput);
        cityInput.addEventListener('blur', validateCityInput);
    }
    
    if (stateInput) {
        stateInput.addEventListener('input', validateStateInput);
        stateInput.addEventListener('blur', validateStateInput);
    }
});