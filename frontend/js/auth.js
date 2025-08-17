// Authentication handling for Potluck
const API_URL = 'https://www.potluck.cafe/api/';
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
    const zipCheckDiv = document.querySelector('.zip-check');
    const serviceStatusDiv = document.getElementById('serviceStatus');
    const signupBtn = document.getElementById('signupBtn');
    
    if (role === 'consumer') {
        // Show ZIP validation for consumers
        zipCheckDiv.style.display = 'flex';
        serviceStatusDiv.style.display = 'none';
        signupBtn.disabled = true; // Disable until ZIP is validated
        zipValidated = false;
    } else {
        // Hide ZIP validation for chefs and delivery agents
        zipCheckDiv.style.display = 'none';
        serviceStatusDiv.style.display = 'none';
        signupBtn.disabled = false; // Enable immediately for service providers
        zipValidated = true;
    }
}

// Check if zip code is serviceable
async function checkServiceArea() {
    const zip = document.getElementById('signupZip').value;
    if (!zip) {
        showError('Please enter a zip code');
        return;
    }
    
    try {
        const url = `${API_URL}/auth/check-service-area`;
        console.log('Making request to:', url); // Debug log
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
    
    // Only require ZIP validation for consumers
    if (selectedRole === 'consumer' && !zipValidated) {
        showError('Please verify your zip code first');
        return;
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
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
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
        showError('Network error. Please try again.');
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
});