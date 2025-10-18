/**
 * Location Service for Potluck
 * Handles GPS detection and reverse geocoding
 */

const GEOCODING_API = 'https://nominatim.openstreetmap.org/reverse';

/**
 * Get current GPS location
 */
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported by your browser'));
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            position => {
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                });
            },
            error => {
                let errorMessage = 'Could not detect location';
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = 'Location permission denied. Please allow location access in your browser settings.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = 'Location information is unavailable.';
                        break;
                    case error.TIMEOUT:
                        errorMessage = 'Location request timed out.';
                        break;
                }
                reject(new Error(errorMessage));
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    });
}

/**
 * Convert coordinates to address (reverse geocoding)
 */
async function reverseGeocode(latitude, longitude) {
    try {
        const url = `${GEOCODING_API}?lat=${latitude}&lon=${longitude}&format=json`;
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'Potluck App'
            }
        });
        
        if (!response.ok) {
            throw new Error('Geocoding failed');
        }
        
        const data = await response.json();
        const address = data.address;
        
        return {
            city: address.city || address.town || address.village || address.county,
            state: address.state || address.region,
            country: address.country,
            country_code: address.country_code?.toUpperCase(),
            zip: address.postcode,
            full_address: data.display_name,
            latitude,
            longitude
        };
    } catch (error) {
        console.error('Reverse geocoding error:', error);
        throw new Error('Could not determine address from coordinates');
    }
}

/**
 * Get location from IP (fallback method)
 */
async function getLocationFromIP() {
    try {
        const response = await fetch('https://ipapi.co/json/');
        const data = await response.json();
        
        return {
            city: data.city,
            state: data.region,
            country: data.country_name,
            country_code: data.country_code,
            zip: data.postal,
            latitude: data.latitude,
            longitude: data.longitude,
            full_address: `${data.city}, ${data.region}, ${data.country_name}`
        };
    } catch (error) {
        console.error('IP location detection failed:', error);
        throw new Error('Could not detect location from IP');
    }
}

/**
 * Update user location in localStorage
 */
async function updateUserLocation(locationData) {
    try {
        // Update localStorage with new location data
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        user.city = locationData.city;
        user.state = locationData.state;
        user.country = locationData.country;
        user.zip = locationData.zip;
        user.latitude = locationData.latitude;
        user.longitude = locationData.longitude;
        localStorage.setItem('user', JSON.stringify(user));
        
        console.log('✅ Location updated in localStorage:', locationData);
        return { success: true };
    } catch (error) {
        console.error('Update location error:', error);
        throw error;
    }
}

/**
 * Main function to detect and update location
 */
async function detectAndUpdateLocation() {
    try {
        showToast('Detecting your location...', 'info');
        
        let locationData;
        
        // Try GPS first
        try {
            const coords = await getCurrentLocation();
            console.log('✅ GPS coordinates:', coords);
            
            // Reverse geocode to get address
            locationData = await reverseGeocode(coords.latitude, coords.longitude);
            console.log('✅ Address from GPS:', locationData);
        } catch (gpsError) {
            console.warn('GPS failed, trying IP fallback:', gpsError);
            
            // Try IP-based location
            try {
                locationData = await getLocationFromIP();
                console.log('✅ Location from IP:', locationData);
            } catch (ipError) {
                console.warn('IP location failed, trying backend fallback:', ipError);
                
                // Fallback to backend detection
                try {
                    const response = await fetch('http://localhost:5000/api/auth/detect-location', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({})
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    if (data.success && data.location) {
                        locationData = {
                            city: data.location.city,
                            state: data.location.state,
                            country: data.location.country,
                            zip: data.location.zip || '',
                            latitude: data.location.latitude || null,
                            longitude: data.location.longitude || null,
                            full_address: `${data.location.city}, ${data.location.state}, ${data.location.country}`
                        };
                        console.log('✅ Location from backend:', locationData);
                    } else {
                        throw new Error('Backend location detection failed');
                    }
                } catch (backendError) {
                    console.error('Backend location detection failed:', backendError);
                    // Final fallback to default location
                    locationData = {
                        city: 'Dallas',
                        state: 'TX',
                        country: 'United States',
                        zip: '75201',
                        latitude: 32.7815,
                        longitude: -96.7968,
                        full_address: 'Dallas, TX, United States'
                    };
                    console.log('✅ Using default location:', locationData);
                }
            }
        }
        
        // Update localStorage
        await updateUserLocation(locationData);
        
        // Update UI
        const locationElement = document.getElementById('currentLocation');
        if (locationElement) {
            locationElement.textContent = `${locationData.city}, ${locationData.state}`;
        }
        
        showToast('Location detected successfully!', 'success');
        
        return locationData;
    } catch (error) {
        console.error('Location detection failed:', error);
        showToast(error.message || 'Could not detect location', 'error');
        throw error;
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Check if showSuccess/showError functions exist (from chef.js)
    if (typeof showSuccess === 'function' && type === 'success') {
        showSuccess(message);
    } else if (typeof showError === 'function' && type === 'error') {
        showError(message);
    } else {
        // Create simple toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#667eea'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Add CSS for toast animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Show manual location entry modal
function showManualLocationModal() {
    const modal = document.getElementById('manualLocationModal');
    if (modal) {
        modal.classList.add('active');
        // Focus on the first input
        const firstInput = modal.querySelector('input');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
}

// Close manual location modal
function closeManualLocationModal() {
    const modal = document.getElementById('manualLocationModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Save manual location
async function saveManualLocation() {
    const countryName = document.getElementById('manualCountry').value;
    const state = document.getElementById('manualState').value;
    const city = document.getElementById('manualCity').value;
    const postalCode = document.getElementById('manualPostalCode').value;
    
    if (!countryName || !state || !city || !postalCode) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    try {
        // Use AI to get country code from country name
        const country = await getCountryCodeFromAI(countryName);
        
        // Validate postal code format based on country
        if (!validatePostalCode(postalCode, country)) {
            showToast('Invalid postal code format for selected country', 'error');
            return;
        }
        
        // Get coordinates from postal code (reverse geocoding)
        const coords = await getCoordinatesFromPostalCode(postalCode, country);
        
        const locationData = {
            city: city,
            state: state,
            country: country,
            country_name: countryName,
            zip: postalCode,
            latitude: coords.latitude,
            longitude: coords.longitude,
            full_address: `${city}, ${state}, ${countryName} ${postalCode}`
        };
        
        // Store location in localStorage for language detection
        localStorage.setItem('userLocation', JSON.stringify(locationData));
        
        // Clear the manual language flag so user can be prompted about language switch
        // when they manually set their location
        localStorage.removeItem('userLangManual');
        console.log('Cleared userLangManual flag for location-based language prompt');
        
        // Update localStorage
        await updateUserLocation(locationData);
        
        // Update UI
        const locationElement = document.getElementById('currentLocation');
        if (locationElement) {
            locationElement.textContent = `${city}, ${state}`;
        }
        
        // Close modal
        closeManualLocationModal();
        
        showToast('Location updated successfully!', 'success');
        
        // Prompt user about language switch if available
        console.log('Checking for language switch prompt...');
        console.log('promptLanguageSwitch function exists:', typeof promptLanguageSwitch === 'function');
        console.log('Location data:', locationData);
        
        if (typeof promptLanguageSwitch === 'function') {
            console.log('Calling promptLanguageSwitch...');
            await promptLanguageSwitch(locationData);
        } else {
            console.log('promptLanguageSwitch function not found!');
        }
        
        return locationData;
        
    } catch (error) {
        console.error('Error saving manual location:', error);
        showToast('Failed to save location: ' + error.message, 'error');
    }
}

// Get country code from country name using AI
async function getCountryCodeFromAI(countryName) {
    try {
        const response = await fetch('/api/auth/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                text: `What is the ISO 3166-1 alpha-2 country code for "${countryName}"? Return only the 2-letter code (e.g., US, IN, CA, GB, AU).`,
                target_language: 'en'
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            const countryCode = data.translated_text?.trim().toUpperCase();
            
            // Validate that it's a 2-letter code
            if (countryCode && countryCode.length === 2 && /^[A-Z]{2}$/.test(countryCode)) {
                return countryCode;
            }
        }
        
        // Fallback: try to match common country names
        const commonCountries = {
            'united states': 'US', 'usa': 'US', 'america': 'US',
            'india': 'IN', 'bharat': 'IN',
            'canada': 'CA',
            'united kingdom': 'GB', 'uk': 'GB', 'britain': 'GB',
            'australia': 'AU',
            'germany': 'DE', 'deutschland': 'DE',
            'france': 'FR',
            'japan': 'JP',
            'brazil': 'BR', 'brasil': 'BR',
            'mexico': 'MX', 'méxico': 'MX',
            'spain': 'ES', 'españa': 'ES',
            'italy': 'IT', 'italia': 'IT',
            'china': 'CN',
            'russia': 'RU', 'россия': 'RU',
            'south africa': 'ZA',
            'nigeria': 'NG',
            'kenya': 'KE',
            'egypt': 'EG',
            'saudi arabia': 'SA',
            'united arab emirates': 'AE', 'uae': 'AE',
            'turkey': 'TR', 'türkiye': 'TR',
            'indonesia': 'ID',
            'thailand': 'TH',
            'vietnam': 'VN', 'việt nam': 'VN',
            'philippines': 'PH', 'filipinas': 'PH',
            'malaysia': 'MY',
            'singapore': 'SG',
            'south korea': 'KR', 'korea': 'KR',
            'taiwan': 'TW',
            'hong kong': 'HK',
            'new zealand': 'NZ',
            'argentina': 'AR',
            'chile': 'CL',
            'colombia': 'CO',
            'peru': 'PE', 'perú': 'PE',
            'venezuela': 'VE',
            'uruguay': 'UY',
            'paraguay': 'PY',
            'bolivia': 'BO',
            'ecuador': 'EC',
            'guyana': 'GY',
            'suriname': 'SR',
            'french guiana': 'GF'
        };
        
        const normalizedName = countryName.toLowerCase().trim();
        return commonCountries[normalizedName] || 'US'; // Default to US if not found
        
    } catch (error) {
        console.error('AI country code detection failed:', error);
        // Fallback to common countries
        const commonCountries = {
            'united states': 'US', 'usa': 'US', 'america': 'US',
            'india': 'IN', 'bharat': 'IN',
            'canada': 'CA',
            'united kingdom': 'GB', 'uk': 'GB', 'britain': 'GB',
            'australia': 'AU'
        };
        const normalizedName = countryName.toLowerCase().trim();
        return commonCountries[normalizedName] || 'US';
    }
}

// Validate postal code format based on country
function validatePostalCode(postalCode, country) {
    const patterns = {
        'US': /^\d{5}(-\d{4})?$/,  // US ZIP: 12345 or 12345-6789
        'IN': /^\d{6}$/,           // India PIN: 123456
        'CA': /^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$/, // Canada: A1A 1A1
        'GB': /^[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}$/, // UK: SW1A 1AA
        'AU': /^\d{4}$/,           // Australia: 1234
        'DE': /^\d{5}$/,           // Germany: 12345
        'FR': /^\d{5}$/,           // France: 12345
        'JP': /^\d{3}-\d{4}$/,     // Japan: 123-4567
        'BR': /^\d{5}-?\d{3}$/,    // Brazil: 12345-678
        'MX': /^\d{5}$/,           // Mexico: 12345
        'ES': /^\d{5}$/,           // Spain: 12345
        'IT': /^\d{5}$/,           // Italy: 12345
        'CN': /^\d{6}$/,           // China: 123456
        'RU': /^\d{6}$/,           // Russia: 123456
        'ZA': /^\d{4}$/,           // South Africa: 1234
        'NG': /^\d{6}$/,           // Nigeria: 123456
        'KE': /^\d{5}$/,           // Kenya: 12345
        'EG': /^\d{5}$/,           // Egypt: 12345
        'SA': /^\d{5}$/,           // Saudi Arabia: 12345
        'AE': /^\d{5}$/,           // UAE: 12345
        'TR': /^\d{5}$/,           // Turkey: 12345
        'ID': /^\d{5}$/,           // Indonesia: 12345
        'TH': /^\d{5}$/,           // Thailand: 12345
        'VN': /^\d{6}$/,           // Vietnam: 123456
        'PH': /^\d{4}$/,           // Philippines: 1234
        'MY': /^\d{5}$/,           // Malaysia: 12345
        'SG': /^\d{6}$/,           // Singapore: 123456
        'KR': /^\d{5}$/,           // South Korea: 12345
        'TW': /^\d{3,5}$/,         // Taiwan: 123 or 12345
        'HK': /^\d{6}$/,           // Hong Kong: 123456
        'NZ': /^\d{4}$/,           // New Zealand: 1234
        'AR': /^[A-Z]?\d{4}[A-Z]{3}?$/, // Argentina: 1234 or A1234ABC
        'CL': /^\d{7}$/,           // Chile: 1234567
        'CO': /^\d{6}$/,           // Colombia: 123456
        'PE': /^\d{5}$/,           // Peru: 12345
        'VE': /^\d{4}$/,           // Venezuela: 1234
        'UY': /^\d{5}$/,           // Uruguay: 12345
        'PY': /^\d{4}$/,           // Paraguay: 1234
        'BO': /^\d{4}$/,           // Bolivia: 1234
        'EC': /^\d{6}$/,           // Ecuador: 123456
        'GY': /^\d{6}$/,           // Guyana: 123456
        'SR': /^\d{6}$/,           // Suriname: 123456
        'GF': /^\d{5}$/,           // French Guiana: 12345
        'FK': /^FIQQ 1ZZ$/,        // Falkland Islands: FIQQ 1ZZ
        'GS': /^SIQQ 1ZZ$/,        // South Georgia: SIQQ 1ZZ
        'SH': /^STHL 1ZZ$/,        // Saint Helena: STHL 1ZZ
        'AC': /^ASCN 1ZZ$/,        // Ascension Island: ASCN 1ZZ
        'TA': /^TDCU 1ZZ$/,        // Tristan da Cunha: TDCU 1ZZ
        'BV': /^BIQQ 1ZZ$/,        // Bouvet Island: BIQQ 1ZZ
        'HM': /^HM 1ZZ$/,          // Heard Island: HM 1ZZ
        'TF': /^98400$/,           // French Southern Territories: 98400
        'AQ': /^BIQQ 1ZZ$/,        // Antarctica: BIQQ 1ZZ
        'UM': /^96898$/,           // US Minor Outlying Islands: 96898
        'VI': /^008\d{2}$/,        // US Virgin Islands: 00801-00851
        'PR': /^\d{5}$/,           // Puerto Rico: 12345
        'GU': /^969\d{2}$/,        // Guam: 96910-96932
        'AS': /^96799$/,           // American Samoa: 96799
        'MP': /^96950$/,           // Northern Mariana Islands: 96950
        'PW': /^96940$/,           // Palau: 96940
        'FM': /^96941$/,           // Micronesia: 96941
        'MH': /^96960$/,           // Marshall Islands: 96960
        'KI': /^96960$/,           // Kiribati: 96960
        'TV': /^96960$/,           // Tuvalu: 96960
        'NR': /^96960$/,           // Nauru: 96960
        'VU': /^96960$/,           // Vanuatu: 96960
        'SB': /^96960$/,           // Solomon Islands: 96960
        'PG': /^96960$/,           // Papua New Guinea: 96960
        'FJ': /^96960$/,           // Fiji: 96960
        'TO': /^96960$/,           // Tonga: 96960
        'WS': /^96960$/,           // Samoa: 96960
        'CK': /^96960$/,           // Cook Islands: 96960
        'NU': /^96960$/,           // Niue: 96960
        'TK': /^96960$/,           // Tokelau: 96960
        'WF': /^98600$/,           // Wallis and Futuna: 98600
        'NC': /^98800$/,           // New Caledonia: 98800
        'PF': /^98700$/,           // French Polynesia: 98700
        'PN': /^96960$/            // Pitcairn Islands: 96960
    };
    
    const pattern = patterns[country];
    if (!pattern) {
        // If no pattern exists, accept any format
        return true;
    }
    
    return pattern.test(postalCode);
}

// Get coordinates from postal code using reverse geocoding
async function getCoordinatesFromPostalCode(postalCode, country) {
    try {
        // Use OpenStreetMap Nominatim for reverse geocoding
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?postalcode=${encodeURIComponent(postalCode)}&country=${encodeURIComponent(country)}&format=json&limit=1`
        );
        
        if (!response.ok) {
            throw new Error(`Geocoding API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data && data.length > 0) {
            return {
                latitude: parseFloat(data[0].lat),
                longitude: parseFloat(data[0].lon)
            };
        } else {
            // Fallback to country center coordinates
            const countryCenters = {
                'US': { latitude: 39.8283, longitude: -98.5795 },
                'IN': { latitude: 20.5937, longitude: 78.9629 },
                'CA': { latitude: 56.1304, longitude: -106.3468 },
                'GB': { latitude: 55.3781, longitude: -3.4360 },
                'AU': { latitude: -25.2744, longitude: 133.7751 },
                'DE': { latitude: 51.1657, longitude: 10.4515 },
                'FR': { latitude: 46.2276, longitude: 2.2137 },
                'JP': { latitude: 36.2048, longitude: 138.2529 },
                'BR': { latitude: -14.2350, longitude: -51.9253 },
                'MX': { latitude: 23.6345, longitude: -102.5528 },
                'ES': { latitude: 40.4637, longitude: -3.7492 },
                'IT': { latitude: 41.8719, longitude: 12.5674 },
                'CN': { latitude: 35.8617, longitude: 104.1954 },
                'RU': { latitude: 61.5240, longitude: 105.3188 },
                'ZA': { latitude: -30.5595, longitude: 22.9375 },
                'NG': { latitude: 9.0820, longitude: 8.6753 },
                'KE': { latitude: -0.0236, longitude: 37.9062 },
                'EG': { latitude: 26.0975, longitude: 30.0444 },
                'SA': { latitude: 23.8859, longitude: 45.0792 },
                'AE': { latitude: 23.4241, longitude: 53.8478 },
                'TR': { latitude: 38.9637, longitude: 35.2433 },
                'ID': { latitude: -0.7893, longitude: 113.9213 },
                'TH': { latitude: 15.8700, longitude: 100.9925 },
                'VN': { latitude: 14.0583, longitude: 108.2772 },
                'PH': { latitude: 12.8797, longitude: 121.7740 },
                'MY': { latitude: 4.2105, longitude: 101.9758 },
                'SG': { latitude: 1.3521, longitude: 103.8198 },
                'KR': { latitude: 35.9078, longitude: 127.7669 },
                'TW': { latitude: 23.6978, longitude: 120.9605 },
                'HK': { latitude: 22.3193, longitude: 114.1694 },
                'NZ': { latitude: -40.9006, longitude: 174.8860 },
                'AR': { latitude: -38.4161, longitude: -63.6167 },
                'CL': { latitude: -35.6751, longitude: -71.5430 },
                'CO': { latitude: 4.5709, longitude: -74.2973 },
                'PE': { latitude: -9.1900, longitude: -75.0152 },
                'VE': { latitude: 6.4238, longitude: -66.5897 },
                'UY': { latitude: -32.5228, longitude: -55.7658 },
                'PY': { latitude: -23.4425, longitude: -58.4438 },
                'BO': { latitude: -16.2902, longitude: -63.5887 },
                'EC': { latitude: -1.8312, longitude: -78.1834 },
                'GY': { latitude: 4.8604, longitude: -58.9302 },
                'SR': { latitude: 3.9193, longitude: -56.0278 },
                'GF': { latitude: 3.9339, longitude: -58.1258 },
                'FK': { latitude: -51.7963, longitude: -59.5236 },
                'GS': { latitude: -54.4296, longitude: -36.5879 },
                'SH': { latitude: -24.1434, longitude: -10.0307 },
                'AC': { latitude: -7.9467, longitude: -14.3559 },
                'TA': { latitude: -37.0686, longitude: -12.2777 },
                'BV': { latitude: -54.4208, longitude: 3.3464 },
                'HM': { latitude: -53.0818, longitude: 73.5042 },
                'TF': { latitude: -49.2804, longitude: 69.3486 },
                'AQ': { latitude: -75.2509, longitude: -0.0713 },
                'UM': { latitude: 19.2823, longitude: 166.6470 },
                'VI': { latitude: 18.3358, longitude: -64.8963 },
                'PR': { latitude: 18.2208, longitude: -66.5901 },
                'GU': { latitude: 13.4443, longitude: 144.7937 },
                'AS': { latitude: -14.2710, longitude: -170.1322 },
                'MP': { latitude: 17.3308, longitude: 145.3846 },
                'PW': { latitude: 7.5150, longitude: 134.5825 },
                'FM': { latitude: 7.4256, longitude: 150.5508 },
                'MH': { latitude: 7.1315, longitude: 171.1845 },
                'KI': { latitude: -3.3704, longitude: -168.7340 },
                'TV': { latitude: -7.1095, longitude: 177.6493 },
                'NR': { latitude: -0.5228, longitude: 166.9315 },
                'VU': { latitude: -15.3767, longitude: 166.9592 },
                'SB': { latitude: -9.6457, longitude: 160.1562 },
                'PG': { latitude: -6.3150, longitude: 143.9555 },
                'FJ': { latitude: -16.5780, longitude: 179.4144 },
                'TO': { latitude: -21.1789, longitude: -175.1982 },
                'WS': { latitude: -13.7590, longitude: -172.1046 },
                'CK': { latitude: -21.2367, longitude: -159.7777 },
                'NU': { latitude: -19.0544, longitude: -169.8672 },
                'TK': { latitude: -8.9674, longitude: -171.8559 },
                'WF': { latitude: -13.7687, longitude: -177.1561 },
                'NC': { latitude: -20.9043, longitude: 165.6180 },
                'PF': { latitude: -17.6797, longitude: -149.4068 },
                'PN': { latitude: -24.7036, longitude: -127.4393 }
            };
            
            const center = countryCenters[country] || { latitude: 0, longitude: 0 };
            console.warn(`No coordinates found for postal code ${postalCode} in ${country}, using country center`);
            return center;
        }
    } catch (error) {
        console.error('Reverse geocoding error:', error);
        // Fallback to country center
        const countryCenters = {
            'US': { latitude: 39.8283, longitude: -98.5795 },
            'IN': { latitude: 20.5937, longitude: 78.9629 },
            'CA': { latitude: 56.1304, longitude: -106.3468 },
            'GB': { latitude: 55.3781, longitude: -3.4360 },
            'AU': { latitude: -25.2744, longitude: 133.7751 }
        };
        
        const center = countryCenters[country] || { latitude: 0, longitude: 0 };
        console.warn(`Reverse geocoding failed for ${postalCode} in ${country}, using country center`);
        return center;
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getCurrentLocation,
        reverseGeocode,
        getLocationFromIP,
        updateUserLocation,
        detectAndUpdateLocation,
        showManualLocationModal,
        closeManualLocationModal,
        saveManualLocation,
        validatePostalCode,
        getCoordinatesFromPostalCode
    };
}


