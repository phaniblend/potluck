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
