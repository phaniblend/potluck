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
