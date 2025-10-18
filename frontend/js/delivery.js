// Delivery agent dashboard logic
console.log('🚚 delivery.js loading...');
// Use existing API_URL if already defined (from auth.js or other files)
// Don't redeclare if it already exists
const DELIVERY_API_URL = typeof API_URL !== 'undefined' ? API_URL : 'http://localhost:5000/api';

// Safe showToast wrapper
function safeShowToast(message, type = 'info') {
    if (typeof showToast === 'function') {
        showToast(message, type);
    } else {
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

let user = null;
let serviceAreas = [];
let availableJobs = [];
let recentDeliveries = [];
let currentLocation = null;

// Initialize delivery dashboard
async function initDeliveryDashboard() {
    try {
        // Load user data
        user = JSON.parse(localStorage.getItem('user') || '{}');
        if (!user.id) {
            window.location.href = '/pages/login.html';
            return;
        }

        // Load current location first
        await loadCurrentLocation();
        
        // Load dashboard data
        await loadDashboardData();
        await loadServiceAreas();
        await loadAvailableJobs();
        await loadRecentDeliveries();
        await loadVerificationStatus();

    } catch (error) {
        console.error('Failed to initialize delivery dashboard:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

// Load current location
async function loadCurrentLocation() {
    try {
        // Get location from localStorage or detect
        const storedLocation = localStorage.getItem('userLocation');
        if (storedLocation) {
            currentLocation = JSON.parse(storedLocation);
            updateLocationDisplay();
        } else {
            // Try to detect location
            await detectAndUpdateLocation();
        }
    } catch (error) {
        console.error('Failed to load current location:', error);
        // Set default location
        currentLocation = {
            city: 'Dallas',
            state: 'TX',
            zip: '75201',
            latitude: 32.7767,
            longitude: -96.7970
        };
        updateLocationDisplay();
    }
}

// Update location display
function updateLocationDisplay() {
    const locationDisplay = document.getElementById('currentLocationDisplay');
    const zipCodeDisplay = document.getElementById('currentZipCode');
    
    if (currentLocation && locationDisplay && zipCodeDisplay) {
        locationDisplay.textContent = `${currentLocation.city}, ${currentLocation.state}`;
        zipCodeDisplay.textContent = currentLocation.zip || '--';
    }
}

// Calculate distance between two coordinates (Haversine formula)
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Load dashboard statistics
async function loadDashboardData() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${DELIVERY_API_URL}/delivery/dashboard`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        updateDashboardUI(data);
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        showDefaultDashboard();
    }
}

// Update dashboard UI with data
async function updateDashboardUI(data) {
    // Update today's deliveries
    const todayDeliveriesElement = document.getElementById('todayDeliveries');
    if (todayDeliveriesElement) {
        todayDeliveriesElement.textContent = data.today_deliveries || 0;
    }

    // Update today's earnings
    const todayEarningsElement = document.getElementById('todayEarnings');
    if (todayEarningsElement) {
        todayEarningsElement.textContent = `$${(data.today_earnings || 0).toFixed(2)}`;
    }

    // Update status
    const statusToggle = document.getElementById('statusToggle');
    const statusText = document.getElementById('statusText');
    if (statusToggle && statusText) {
        statusToggle.checked = data.current_status === 'online';
        statusText.textContent = data.current_status === 'online' ? 'Online' : 'Offline';
    }

    // Translate the page after updating content
    if (typeof translatePage === 'function') {
        await translatePage();
    }
}

// Show default dashboard when API fails
async function showDefaultDashboard() {
    const todayDeliveriesElement = document.getElementById('todayDeliveries');
    if (todayDeliveriesElement) {
        todayDeliveriesElement.textContent = '0';
    }

    const todayEarningsElement = document.getElementById('todayEarnings');
    if (todayEarningsElement) {
        todayEarningsElement.textContent = '$0.00';
    }

    // Translate the page after updating content
    if (typeof translatePage === 'function') {
        await translatePage();
    }
}

// Load service areas
async function loadServiceAreas() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${DELIVERY_API_URL}/delivery/service-areas`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        serviceAreas = data.service_areas || [];
        displayServiceAreas();
    } catch (error) {
        console.error('Failed to load service areas:', error);
        showToast('Failed to load service areas', 'error');
    }
}

// Display service areas
async function displayServiceAreas() {
    const list = document.getElementById('serviceAreasList');
    const countElement = document.getElementById('serviceAreasCount');
    
    if (!list) return;

    // Update service areas count
    if (countElement) {
        countElement.textContent = `${serviceAreas.length} area${serviceAreas.length !== 1 ? 's' : ''}`;
    }

    if (serviceAreas.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">🗺️</span>
                <p>No service areas added yet</p>
                <button onclick="showAddAreaModal()" class="btn btn-primary btn-sm">Add Your First Area</button>
            </div>
        `;
        return;
    }

    // Calculate distances for each area
    const areasWithDistance = serviceAreas.map(area => {
        let distance = null;
        if (currentLocation && area.latitude && area.longitude) {
            distance = calculateDistance(
                currentLocation.latitude, 
                currentLocation.longitude,
                area.latitude, 
                area.longitude
            );
        }
        return { ...area, distance };
    });

    // Sort by distance (closest first)
    areasWithDistance.sort((a, b) => {
        if (a.distance === null) return 1;
        if (b.distance === null) return -1;
        return a.distance - b.distance;
    });

    list.innerHTML = areasWithDistance.map(area => `
        <div class="service-area-item ${area.is_primary ? 'primary' : ''}">
            <div class="area-info">
                <div class="area-name">
                    <strong>${area.area_name}</strong>
                    ${area.is_primary ? '<span class="primary-badge">Primary</span>' : ''}
                </div>
                <div class="area-location">
                    <span class="location-icon">📍</span>
                    <span>${area.city}, ${area.state} ${area.zip_code}</span>
                    ${area.distance !== null ? `<span class="distance-badge">${area.distance.toFixed(1)} km away</span>` : ''}
                </div>
                <div class="area-meta">
                    <small>Added: ${new Date(area.added_at).toLocaleDateString()}</small>
                </div>
            </div>
            <div class="area-actions">
                <button onclick="navigateToArea('${area.area_name}', ${area.latitude}, ${area.longitude})" class="btn btn-outline btn-sm">Navigate</button>
                <button onclick="editServiceArea(${area.id})" class="btn btn-outline btn-sm">Edit</button>
                <button onclick="removeServiceArea(${area.id})" class="btn btn-danger btn-sm">Remove</button>
            </div>
        </div>
    `).join('');

    // Translate the page after updating content
    if (typeof translatePage === 'function') {
        await translatePage();
    }
}

// Load available jobs
async function loadAvailableJobs() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${DELIVERY_API_URL}/delivery/available-jobs`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        availableJobs = data.jobs || [];
        displayAvailableJobs();
    } catch (error) {
        console.error('Failed to load available jobs:', error);
        showToast('Failed to load available jobs', 'error');
    }
}

// Display available jobs
async function displayAvailableJobs() {
    const list = document.getElementById('jobsList');
    if (!list) return;

    if (availableJobs.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📦</div>
                <h3 data-i18n="no_available_jobs">No Available Jobs</h3>
                <p data-i18n="no_jobs_description">No delivery jobs available in your service areas at the moment</p>
            </div>
        `;
    } else {
        // Calculate distances for each job
        const jobsWithDistance = availableJobs.map(job => {
            let distance = null;
            if (currentLocation && job.pickup_latitude && job.pickup_longitude) {
                distance = calculateDistance(
                    currentLocation.latitude, 
                    currentLocation.longitude,
                    job.pickup_latitude, 
                    job.pickup_longitude
                );
            }
            return { ...job, distance };
        });

        // Sort by distance (closest first)
        jobsWithDistance.sort((a, b) => {
            if (a.distance === null) return 1;
            if (b.distance === null) return -1;
            return a.distance - b.distance;
        });

        list.innerHTML = jobsWithDistance.map(job => `
            <div class="job-card">
                <div class="job-header">
                    <h4 data-i18n="delivery_job">Delivery Job #${job.id}</h4>
                    <div class="job-badges">
                        ${job.distance !== null ? `<span class="job-distance">${job.distance.toFixed(1)} km away</span>` : ''}
                        <span class="job-earnings">$${job.estimated_earnings}</span>
                    </div>
                </div>
                <div class="job-details">
                    <p><strong data-i18n="pickup_from">Pickup from:</strong> 
                        <a href="#" onclick="navigateToChef('${job.chef_name}', ${job.pickup_latitude}, ${job.pickup_longitude})" class="chef-link">${job.chef_name}</a>
                        <br><span class="address-detail">${job.pickup_address}</span>
                    </p>
                    <p><strong data-i18n="deliver_to">Deliver to:</strong> ${job.delivery_address}</p>
                    <p><strong data-i18n="estimated_time">Time:</strong> ${job.estimated_time} min</p>
                    ${job.distance !== null ? `<p><strong data-i18n="distance_to_pickup">Distance to pickup:</strong> ${job.distance.toFixed(1)} km</p>` : ''}
                </div>
                <div class="job-actions">
                    <button onclick="acceptJob(${job.id})" class="btn btn-primary" data-i18n="accept">Accept</button>
                    <button onclick="viewJobDetails(${job.id})" class="btn btn-outline" data-i18n="details">Details</button>
                    <button onclick="navigateToPickup(${job.pickup_latitude}, ${job.pickup_longitude})" class="btn btn-secondary" data-i18n="navigate">Navigate</button>
                </div>
            </div>
        `).join('');
    }

    // Translate the page after updating content
    if (typeof translatePage === 'function') {
        await translatePage();
    }
}

// Load recent deliveries
async function loadRecentDeliveries() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${DELIVERY_API_URL}/delivery/recent-deliveries`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        recentDeliveries = data.deliveries || [];
        displayRecentDeliveries();
    } catch (error) {
        console.error('Failed to load recent deliveries:', error);
        showToast('Failed to load recent deliveries', 'error');
    }
}

// Display recent deliveries
async function displayRecentDeliveries() {
    const list = document.getElementById('deliveriesList');
    if (!list) return;

    if (recentDeliveries.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🚚</div>
                <h3 data-i18n="no_recent_deliveries">No Recent Deliveries</h3>
                <p data-i18n="no_deliveries_description">Your recent delivery history will appear here</p>
            </div>
        `;
    } else {
        list.innerHTML = recentDeliveries.map(delivery => `
            <div class="delivery-card">
                <div class="delivery-header">
                    <h4 data-i18n="delivery">Delivery #${delivery.id}</h4>
                    <span class="delivery-status ${delivery.status}">${delivery.status}</span>
                </div>
                <div class="delivery-details">
                    <p><strong data-i18n="from">From:</strong> ${delivery.pickup_address}</p>
                    <p><strong data-i18n="to">To:</strong> ${delivery.delivery_address}</p>
                    <p><strong data-i18n="earnings">Earnings:</strong> $${delivery.earnings}</p>
                    <p><strong data-i18n="completed">Completed:</strong> ${new Date(delivery.completed_at).toLocaleString()}</p>
                </div>
            </div>
        `).join('');
    }

    // Translate the page after updating content
    if (typeof translatePage === 'function') {
        await translatePage();
    }
}

// Load verification status
async function loadVerificationStatus() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${DELIVERY_API_URL}/delivery/verification-status`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayVerificationStatus(data);
    } catch (error) {
        console.error('Failed to load verification status:', error);
    }
}

// Display verification status
async function displayVerificationStatus(data) {
    const container = document.getElementById('verificationItems');
    if (!container) return;

    const verificationItems = [
        { type: 'driving_license', name: 'Driving License', status: data.driving_license_status || 'pending' },
        { type: 'id_card', name: 'ID Card', status: data.id_card_status || 'pending' },
        { type: 'selfie', name: 'Selfie with ID', status: data.selfie_status || 'pending' },
        { type: 'vehicle_registration', name: 'Vehicle Registration', status: data.vehicle_registration_status || 'pending' }
    ];

    container.innerHTML = verificationItems.map(item => `
        <div class="verification-item">
            <div class="verification-info">
                <span class="verification-name">${item.name}</span>
                <span class="verification-status ${item.status}">${item.status}</span>
            </div>
            <div class="verification-icon">
                ${item.status === 'approved' ? '✅' : item.status === 'rejected' ? '❌' : '⏳'}
            </div>
        </div>
    `).join('');

    // Translate the page after updating content
    if (typeof translatePage === 'function') {
        await translatePage();
    }
}

// Modal functions
function showAddAreaModal() {
    document.getElementById('addAreaModal').style.display = 'block';
}

function closeAddAreaModal() {
    document.getElementById('addAreaModal').style.display = 'none';
    // Clear form
    document.getElementById('areaName').value = '';
    document.getElementById('areaZipCode').value = '';
    document.getElementById('areaCity').value = '';
    document.getElementById('areaState').value = '';
    document.getElementById('isPrimaryArea').checked = false;
}

function showVerificationModal() {
    document.getElementById('verificationModal').style.display = 'block';
}

function closeVerificationModal() {
    document.getElementById('verificationModal').style.display = 'none';
}

// Get country code from country name using AI
async function getCountryCodeFromAI(countryName) {
    try {
        const response = await fetch(`${DELIVERY_API_URL}/auth/translate`, {
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
        
        // Fallback: try to match common country names including 3rd/5th world countries
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
            'french guiana': 'GF',
            // 3rd/5th world countries
            'somalia': 'SO', 'soomaaliya': 'SO',
            'myanmar': 'MM', 'burma': 'MM',
            'ethiopia': 'ET', 'habesha': 'ET',
            'tanzania': 'TZ', 'tanzania': 'TZ',
            'uganda': 'UG',
            'ghana': 'GH',
            'senegal': 'SN',
            'mali': 'ML',
            'burkina faso': 'BF',
            'niger': 'NE',
            'chad': 'TD',
            'cameroon': 'CM',
            'central african republic': 'CF',
            'democratic republic of congo': 'CD', 'drc': 'CD', 'congo': 'CD',
            'republic of congo': 'CG',
            'gabon': 'GA',
            'equatorial guinea': 'GQ',
            'sao tome and principe': 'ST',
            'angola': 'AO',
            'zambia': 'ZM',
            'zimbabwe': 'ZW',
            'botswana': 'BW',
            'namibia': 'NA',
            'lesotho': 'LS',
            'swaziland': 'SZ', 'eswatini': 'SZ',
            'madagascar': 'MG',
            'mauritius': 'MU',
            'seychelles': 'SC',
            'comoros': 'KM',
            'djibouti': 'DJ',
            'eritrea': 'ER',
            'sudan': 'SD',
            'south sudan': 'SS',
            'libya': 'LY',
            'tunisia': 'TN',
            'algeria': 'DZ',
            'morocco': 'MA',
            'western sahara': 'EH',
            'mauritania': 'MR',
            'gambia': 'GM',
            'guinea-bissau': 'GW',
            'guinea': 'GN',
            'sierra leone': 'SL',
            'liberia': 'LR',
            'ivory coast': 'CI', 'cote d\'ivoire': 'CI',
            'togo': 'TG',
            'benin': 'BJ',
            'rwanda': 'RW',
            'burundi': 'BI',
            'malawi': 'MW',
            'mozambique': 'MZ',
            'afghanistan': 'AF',
            'bangladesh': 'BD',
            'pakistan': 'PK',
            'sri lanka': 'LK',
            'nepal': 'NP',
            'bhutan': 'BT',
            'maldives': 'MV',
            'laos': 'LA',
            'cambodia': 'KH',
            'mongolia': 'MN',
            'north korea': 'KP',
            'yemen': 'YE',
            'syria': 'SY',
            'iraq': 'IQ',
            'iran': 'IR',
            'lebanon': 'LB',
            'jordan': 'JO',
            'israel': 'IL',
            'palestine': 'PS',
            'cyprus': 'CY',
            'armenia': 'AM',
            'azerbaijan': 'AZ',
            'georgia': 'GE',
            'kazakhstan': 'KZ',
            'uzbekistan': 'UZ',
            'turkmenistan': 'TM',
            'tajikistan': 'TJ',
            'kyrgyzstan': 'KG',
            'albania': 'AL',
            'bosnia and herzegovina': 'BA',
            'serbia': 'RS',
            'montenegro': 'ME',
            'north macedonia': 'MK',
            'kosovo': 'XK',
            'moldova': 'MD',
            'belarus': 'BY',
            'ukraine': 'UA',
            'cuba': 'CU',
            'haiti': 'HT',
            'dominican republic': 'DO',
            'jamaica': 'JM',
            'trinidad and tobago': 'TT',
            'barbados': 'BB',
            'saint lucia': 'LC',
            'saint vincent and the grenadines': 'VC',
            'grenada': 'GD',
            'antigua and barbuda': 'AG',
            'saint kitts and nevis': 'KN',
            'dominica': 'DM',
            'belize': 'BZ',
            'guatemala': 'GT',
            'honduras': 'HN',
            'el salvador': 'SV',
            'nicaragua': 'NI',
            'costa rica': 'CR',
            'panama': 'PA',
            'fiji': 'FJ',
            'papua new guinea': 'PG',
            'solomon islands': 'SB',
            'vanuatu': 'VU',
            'samoa': 'WS',
            'tonga': 'TO',
            'kiribati': 'KI',
            'tuvalu': 'TV',
            'nauru': 'NR',
            'palau': 'PW',
            'marshall islands': 'MH',
            'micronesia': 'FM'
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
        'CA': /^[A-Z]\d[A-Z] \d[A-Z]\d$/, // Canada: A1A 1A1
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
        'AR': /^[A-Z]?\d{4}[A-Z]{3}$/, // Argentina: A1234ABC
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
        'GF': /^\d{5}$/            // French Guiana: 12345
    };
    
    const pattern = patterns[country];
    if (!pattern) {
        // If no specific pattern, allow alphanumeric with 3-10 characters
        return /^[A-Za-z0-9\s-]{3,10}$/.test(postalCode);
    }
    
    return pattern.test(postalCode);
}

// Save service area
async function saveServiceArea() {
    console.log('saveServiceArea called');
    const areaName = document.getElementById('areaName').value;
    const countryName = document.getElementById('areaCountry').value;
    const state = document.getElementById('areaState').value;
    const city = document.getElementById('areaCity').value;
    const zipCode = document.getElementById('areaZipCode').value;
    const isPrimary = document.getElementById('isPrimaryArea').checked;

    console.log('Form values:', { areaName, countryName, state, city, zipCode, isPrimary });

    if (!areaName || !countryName || !state || !city || !zipCode) {
        console.log('Validation failed - missing fields');
        if (typeof showToast === 'function') {
            showToast('Please fill in all fields', 'error');
        } else {
            alert('Please fill in all fields');
        }
        return;
    }

    try {
        // Use AI to get country code from country name
        const country = await getCountryCodeFromAI(countryName);
        
        // Validate postal code format based on country
        if (!validatePostalCode(zipCode, country)) {
            showToast('Invalid postal code format for selected country', 'error');
            return;
        }

        const token = localStorage.getItem('token');
        const response = await fetch(`${DELIVERY_API_URL}/delivery/service-areas`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                area_name: areaName,
                country: country,
                country_name: countryName,
                state: state,
                city: city,
                zip_code: zipCode,
                is_primary: isPrimary
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Service area saved successfully:', data);
        
        if (typeof showToast === 'function') {
            showToast('Service area added successfully!', 'success');
        } else {
            alert('Service area added successfully!');
        }
        
        closeAddAreaModal();
        await loadServiceAreas();
        
        // Sync location, language, and currency
        if (typeof syncLocationLanguageCurrency === 'function') {
            console.log('Calling syncLocationLanguageCurrency...');
            const locationData = {
                city: city,
                state: state,
                country: country,
                country_name: countryName,
                zip: zipCode
            };
            await syncLocationLanguageCurrency(locationData);
        } else {
            console.log('syncLocationLanguageCurrency not available');
        }
    } catch (error) {
        console.error('Failed to save service area:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to save service area: ' + error.message, 'error');
        } else {
            alert('Failed to save service area: ' + error.message);
        }
    }
}

// Toggle delivery status
async function toggleStatus() {
    const statusToggle = document.getElementById('statusToggle');
    const statusText = document.getElementById('statusText');
    const newStatus = statusToggle.checked ? 'online' : 'offline';

    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${DELIVERY_API_URL}/delivery/status`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        statusText.textContent = newStatus === 'online' ? 'Online' : 'Offline';
        showToast(`Status changed to ${newStatus}`, 'success');
    } catch (error) {
        console.error('Failed to update status:', error);
        showToast('Failed to update status', 'error');
        // Revert toggle
        statusToggle.checked = !statusToggle.checked;
    }
}

// Refresh jobs
async function refreshJobs() {
    showToast('Refreshing jobs...', 'info');
    await loadAvailableJobs();
}

// Take selfie for verification
async function takeSelfie() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const video = document.createElement('video');
        video.srcObject = stream;
        video.play();

        // Create camera modal
        const cameraModal = document.createElement('div');
        cameraModal.className = 'modal';
        cameraModal.style.display = 'block';
        cameraModal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3 data-i18n="take_selfie">Take Selfie</h3>
                    <button onclick="closeCameraModal()" class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <video id="cameraVideo" autoplay style="width: 100%; max-width: 400px;"></video>
                    <div class="camera-instructions">
                        <p data-i18n="selfie_instructions">Hold your ID next to your face and click capture</p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button onclick="closeCameraModal()" class="btn btn-outline" data-i18n="cancel">Cancel</button>
                    <button onclick="captureSelfie()" class="btn btn-primary" data-i18n="capture">Capture</button>
                </div>
            </div>
        `;

        document.body.appendChild(cameraModal);
        document.getElementById('cameraVideo').srcObject = stream;

        // Make functions available
        window.closeCameraModal = () => {
            stream.getTracks().forEach(track => track.stop());
            document.body.removeChild(cameraModal);
        };

        window.captureSelfie = () => {
            const canvas = document.createElement('canvas');
            const video = document.getElementById('cameraVideo');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            
            const imageData = canvas.toDataURL('image/jpeg');
            // Store image data for verification submission
            localStorage.setItem('selfieData', imageData);
            
            stream.getTracks().forEach(track => track.stop());
            document.body.removeChild(cameraModal);
            showToast('Selfie captured successfully!', 'success');
        };

    } catch (error) {
        console.error('Failed to access camera:', error);
        showToast('Failed to access camera. Please check permissions.', 'error');
    }
}

// Submit verification
async function submitVerification() {
    const licenseFile = document.getElementById('licenseUpload').files[0];
    const vehicleFile = document.getElementById('vehicleUpload').files[0];
    const selfieData = localStorage.getItem('selfieData');

    if (!licenseFile || !selfieData) {
        showToast('Please upload driving license and take a selfie', 'error');
        return;
    }

    try {
        const token = localStorage.getItem('token');
        const formData = new FormData();
        
        formData.append('driving_license', licenseFile);
        if (vehicleFile) {
            formData.append('vehicle_registration', vehicleFile);
        }
        formData.append('selfie', selfieData);

        const response = await fetch(`${DELIVERY_API_URL}/delivery/verification`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        showToast('Verification documents submitted successfully!', 'success');
        closeVerificationModal();
        await loadVerificationStatus();
    } catch (error) {
        console.error('Failed to submit verification:', error);
        showToast('Failed to submit verification', 'error');
    }
}

// Navigation functions
function navigateToArea(areaName, latitude, longitude) {
    if (latitude && longitude) {
        // Open in Google Maps
        const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`;
        window.open(mapsUrl, '_blank');
        showToast(`Opening navigation to ${areaName}`, 'info');
    } else {
        showToast('Location coordinates not available', 'error');
    }
}

function navigateToChef(chefName, latitude, longitude) {
    if (latitude && longitude) {
        // Open in Google Maps
        const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`;
        window.open(mapsUrl, '_blank');
        showToast(`Opening navigation to ${chefName}`, 'info');
    } else {
        showToast('Chef location coordinates not available', 'error');
    }
}

function navigateToPickup(latitude, longitude) {
    if (latitude && longitude) {
        // Open in Google Maps
        const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`;
        window.open(mapsUrl, '_blank');
        showToast('Opening navigation to pickup location', 'info');
    } else {
        showToast('Pickup location coordinates not available', 'error');
    }
}

// Job filtering
function filterJobs() {
    const filter = document.getElementById('jobFilter').value;
    const jobCards = document.querySelectorAll('.job-card');
    
    jobCards.forEach(card => {
        if (filter === 'all') {
            card.style.display = 'block';
        } else if (filter === 'nearby') {
            const distanceElement = card.querySelector('.job-distance');
            if (distanceElement) {
                const distance = parseFloat(distanceElement.textContent);
                card.style.display = distance <= 10 ? 'block' : 'none'; // Show only jobs within 10km
            } else {
                card.style.display = 'block';
            }
        }
    });
}

// Other functions
function editServiceArea(areaId) {
    // Implementation for editing service area
    showToast('Edit functionality coming soon', 'info');
}

function removeServiceArea(areaId) {
    if (confirm('Are you sure you want to remove this service area?')) {
        // Implementation for removing service area
        showToast('Remove functionality coming soon', 'info');
    }
}

function acceptJob(jobId) {
    // Implementation for accepting job
    safeShowToast('Job acceptance functionality coming soon', 'info');
}

function viewJobDetails(jobId) {
    // Implementation for viewing job details
    safeShowToast('Job details functionality coming soon', 'info');
}

function loadActiveOrders() {
    // Stub implementation - will be implemented later
    console.log('loadActiveOrders called');
}

function loadEarningsChart() {
    // Stub implementation - will be implemented later
    console.log('loadEarningsChart called');
}

// Expose functions to global scope
if (typeof window !== 'undefined') {
    console.log('✅ Exposing delivery.js functions to global scope...');
    window.initDeliveryDashboard = initDeliveryDashboard;
    window.loadServiceAreas = loadServiceAreas;
    window.displayServiceAreas = displayServiceAreas;
    window.saveServiceArea = saveServiceArea;
    window.editServiceArea = editServiceArea;
    window.removeServiceArea = removeServiceArea;
    window.acceptJob = acceptJob;
    window.viewJobDetails = viewJobDetails;
    window.filterJobs = filterJobs;
    window.refreshJobs = refreshJobs;
    window.navigateToArea = navigateToArea;
    window.navigateToChef = navigateToChef;
    window.navigateToPickup = navigateToPickup;
    window.toggleStatus = toggleStatus;
    window.showAddAreaModal = showAddAreaModal;
    window.closeAddAreaModal = closeAddAreaModal;
    window.showVerificationModal = showVerificationModal;
    window.closeVerificationModal = closeVerificationModal;
    window.submitVerification = submitVerification;
    window.takeSelfie = takeSelfie;
    window.loadActiveOrders = loadActiveOrders;
    window.loadEarningsChart = loadEarningsChart;
    console.log('✅ saveServiceArea exposed:', typeof window.saveServiceArea);
    console.log('✅ initDeliveryDashboard exposed:', typeof window.initDeliveryDashboard);
}