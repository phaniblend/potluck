/**
 * AI-Powered Real-time Translation System
 * Replaces hardcoded translations with dynamic AI translation
 */

// Translation cache to avoid repeated API calls
const translationCache = new Map();

// Current language
let currentLang = localStorage.getItem('userLang') || 'en';

/**
 * Translate text using AI
 */
async function translateText(text, targetLanguage = currentLang, sourceLanguage = 'en') {
    if (!text || text.trim() === '') return text;
    if (targetLanguage === sourceLanguage) return text;
    
    // Check cache first
    const cacheKey = `${text}|${sourceLanguage}|${targetLanguage}`;
    if (translationCache.has(cacheKey)) {
        return translationCache.get(cacheKey);
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/auth/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                target_language: targetLanguage,
                source_language: sourceLanguage
            })
        });
        
        if (!response.ok) {
            throw new Error(`Translation API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            const translatedText = data.translation;
            // Cache the translation
            translationCache.set(cacheKey, translatedText);
            return translatedText;
        } else {
            throw new Error(data.error || 'Translation failed');
        }
        
    } catch (error) {
        console.warn('AI translation failed:', error);
        // Return original text if translation fails
        return text;
    }
}

/**
 * Translate multiple texts at once (more efficient)
 */
async function translateBatch(texts, targetLanguage = currentLang, sourceLanguage = 'en') {
    if (!texts || texts.length === 0) return {};
    if (targetLanguage === sourceLanguage) {
        return texts.reduce((acc, text) => ({ ...acc, [text]: text }), {});
    }
    
    // Check cache for all texts
    const uncachedTexts = [];
    const results = {};
    
    for (const text of texts) {
        const cacheKey = `${text}|${sourceLanguage}|${targetLanguage}`;
        if (translationCache.has(cacheKey)) {
            results[text] = translationCache.get(cacheKey);
        } else {
            uncachedTexts.push(text);
        }
    }
    
    if (uncachedTexts.length === 0) {
        return results;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/auth/translate-batch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                texts: uncachedTexts,
                target_language: targetLanguage,
                source_language: sourceLanguage
            })
        });
        
        if (!response.ok) {
            throw new Error(`Batch translation API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            const translations = data.translations;
            
            // Cache the translations
            Object.entries(translations).forEach(([original, translated]) => {
                const cacheKey = `${original}|${sourceLanguage}|${targetLanguage}`;
                translationCache.set(cacheKey, translated);
            });
            
            return { ...results, ...translations };
        } else {
            throw new Error(data.error || 'Batch translation failed');
        }
        
    } catch (error) {
        console.warn('Batch AI translation failed:', error);
        // Return original texts if translation fails
        const fallbackResults = uncachedTexts.reduce((acc, text) => ({ ...acc, [text]: text }), {});
        return { ...results, ...fallbackResults };
    }
}

/**
 * Translate all elements with data-i18n attribute
 */
async function translatePage() {
    const elements = document.querySelectorAll('[data-i18n]');
    
    if (elements.length === 0) return;
    
    // Collect all unique texts to translate
    const textsToTranslate = new Set();
    elements.forEach(element => {
        const text = element.textContent.trim();
        if (text) {
            textsToTranslate.add(text);
        }
    });
    
    // Translate all texts at once
    const translations = await translateBatch(Array.from(textsToTranslate));
    
    // Apply translations to elements
    elements.forEach(element => {
        const originalText = element.textContent.trim();
        const translatedText = translations[originalText] || originalText;
        
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            element.placeholder = translatedText;
        } else {
            element.textContent = translatedText;
        }
    });
    
    // Update HTML lang attribute
    document.documentElement.lang = currentLang;
    
    // Set RTL for Arabic
    if (currentLang === 'ar') {
        document.documentElement.dir = 'rtl';
    } else {
        document.documentElement.dir = 'ltr';
    }
}

/**
 * Set language and translate page
 */
async function setLanguage(lang, isManual = false) {
    currentLang = lang;
    localStorage.setItem('userLang', lang);
    
    // Mark if this is a manual language selection by user
    if (isManual) {
        localStorage.setItem('userLangManual', 'true');
    }
    
    // Update language display
    const languageNames = {
        en: 'English', es: 'Español', hi: 'हिन्दी', bn: 'বাংলা', ta: 'தமிழ்', 
        te: 'తెలుగు', zh: '中文', ar: 'العربية', pt: 'Português', 
        fr: 'Français', ru: 'Русский', id: 'Indonesian', de: 'Deutsch',
        it: 'Italiano', ja: '日本語', ko: '한국어', th: 'ไทย', vi: 'Tiếng Việt',
        tl: 'Filipino', ms: 'Bahasa Melayu'
    };
    
    const currentLanguageElement = document.getElementById('currentLanguage');
    if (currentLanguageElement && languageNames[lang]) {
        currentLanguageElement.textContent = languageNames[lang];
    }
    
    // Translate the page
    await translatePage();
}

/**
 * Translate specific text (for dynamic content)
 */
async function t(key, replacements = {}) {
    // First try to get from cache
    const cacheKey = `${key}|en|${currentLang}`;
    if (translationCache.has(cacheKey)) {
        let text = translationCache.get(cacheKey);
        
        // Replace placeholders like {name}
        Object.keys(replacements).forEach(placeholder => {
            text = text.replace(`{${placeholder}}`, replacements[placeholder]);
        });
        
        return text;
    }
    
    // Translate the key
    const translatedText = await translateText(key, currentLang, 'en');
    
    // Replace placeholders
    let result = translatedText;
    Object.keys(replacements).forEach(placeholder => {
        result = result.replace(`{${placeholder}}`, replacements[placeholder]);
    });
    
    return result;
}

/**
 * Initialize AI translation system with intelligent language detection
 */
async function initAITranslations() {
    // Priority 1: Check if user has manually set a language preference
    const userPreferredLang = localStorage.getItem('userLang');
    const isManualLanguageSet = localStorage.getItem('userLangManual') === 'true';
    
    if (isManualLanguageSet && userPreferredLang) {
        // User has explicitly set their language preference - use it
        currentLang = userPreferredLang;
        await translatePage();
        console.log(`✅ Using user's preferred language: ${currentLang}`);
        return;
    }
    
    // Priority 2: Auto-detect language based on current location
    try {
        const detectedLang = await detectLanguageFromLocation();
        if (detectedLang && detectedLang !== 'en') {
            await setLanguage(detectedLang);
            console.log(`✅ Language auto-detected from location: ${detectedLang}`);
        } else {
            await setLanguage('en');
            console.log('✅ Using default language: English');
        }
    } catch (error) {
        console.error('Failed to detect language from location:', error);
        await setLanguage('en');
    }
}

/**
 * Detect language based on current location
 */
async function detectLanguageFromLocation() {
    // First try to get location from localStorage (user's current location)
    const userLocation = JSON.parse(localStorage.getItem('userLocation') || '{}');
    const country = userLocation.country;
    
    if (country) {
        return await getLanguageFromCountry(country);
    }
    
    // Fallback: Try IP-based detection
    try {
        const response = await fetch('https://ipapi.co/json/');
        const data = await response.json();
        return await getLanguageFromCountry(data.country_code);
    } catch (error) {
        console.error('IP-based language detection failed:', error);
        return 'en';
    }
}

/**
 * Get language from location using AI
 */
async function getLanguageFromCountry(countryCode) {
    try {
        // Use AI to determine the appropriate language for the country
        const response = await fetch(`${API_URL}/auth/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                text: `What is the primary local language spoken in ${countryCode}? Return only the language code (e.g., 'en', 'es', 'hi', 'te', 'zh').`,
                target_language: 'en'
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            const suggestedLang = data.translated_text?.toLowerCase() || 'en';
            console.log(`AI suggested language for ${countryCode}: ${suggestedLang}`);
            return suggestedLang;
        }
    } catch (error) {
        console.error('AI language detection failed:', error);
    }
    
    // Fallback to basic mapping only if AI fails
    const basicMap = {
        'US': 'en', 'GB': 'en', 'CA': 'en', 'AU': 'en', 'NZ': 'en', 'IE': 'en',
        'ES': 'es', 'MX': 'es', 'AR': 'es', 'CO': 'es', 'CL': 'es', 'PE': 'es', 'VE': 'es', 'UY': 'es',
        'IN': 'te', 'FR': 'fr', 'BE': 'fr', 'CH': 'fr', 'LU': 'fr', 'MC': 'fr',
        'BR': 'pt', 'PT': 'pt', 'AO': 'pt', 'MZ': 'pt',
        'CN': 'zh', 'TW': 'zh', 'HK': 'zh', 'SG': 'zh',
        'SA': 'ar', 'AE': 'ar', 'EG': 'ar', 'MA': 'ar', 'DZ': 'ar', 'TN': 'ar', 'LY': 'ar',
        'ID': 'id', 'RU': 'ru', 'BY': 'ru', 'KZ': 'ru', 'KG': 'ru',
        'DE': 'de', 'AT': 'de', 'CH': 'de',
        'IT': 'it', 'SM': 'it', 'VA': 'it',
        'JP': 'ja', 'KR': 'ko', 'TH': 'th', 'VN': 'vi', 'PH': 'tl', 'MY': 'ms'
    };
    
    return basicMap[countryCode] || 'en';
}

/**
 * Prompt user to switch language when they manually enter a location
 */
async function promptLanguageSwitch(newLocation) {
    console.log('promptLanguageSwitch called with:', newLocation);
    const country = newLocation.country;
    const suggestedLang = await getLanguageFromCountry(country);
    const currentLang = localStorage.getItem('userLang') || 'en';
    
    console.log('Country:', country, 'Suggested lang:', suggestedLang, 'Current lang:', currentLang);
    
    // Don't prompt if already using the suggested language
    if (suggestedLang === currentLang) {
        console.log('Already using suggested language, no prompt needed');
        return;
    }
    
    // Check if user has explicitly set their language preference
    const isManualLanguageSet = localStorage.getItem('userLangManual') === 'true';
    console.log('Is manual language set:', isManualLanguageSet);
    console.log('Current language:', currentLang);
    console.log('Suggested language:', suggestedLang);
    
    // If user has manually set their language AND it's not English (default),
    // then respect their preference and don't prompt
    if (isManualLanguageSet && currentLang !== 'en') {
        console.log('User has manually set a non-English language preference, no prompt needed');
        return;
    }
    
    // If user is using English (default) or hasn't manually set language,
    // then prompt them about switching to local language
    console.log('Proceeding to show language switch prompt...');
    
    const languageNames = {
        en: 'English', es: 'Español', hi: 'हिन्दी', te: 'తెలుగు', 
        zh: '中文', ar: 'العربية', pt: 'Português', fr: 'Français', 
        ru: 'Русский', id: 'Indonesian', de: 'Deutsch', it: 'Italiano',
        ja: '日本語', ko: '한국어', th: 'ไทย', vi: 'Tiếng Việt',
        tl: 'Filipino', ms: 'Bahasa Melayu'
    };
    
    const suggestedLangName = languageNames[suggestedLang] || suggestedLang;
    const currentLangName = languageNames[currentLang] || currentLang;
    
    console.log('Showing language switch prompt...');
    console.log('Suggested lang name:', suggestedLangName, 'Current lang name:', currentLangName);
    
    // Show in-app modal instead of browser confirm
    showLanguageSwitchModal(newLocation, suggestedLang, suggestedLangName, currentLangName);
}

/**
 * Show language switch modal
 */
function showLanguageSwitchModal(newLocation, suggestedLang, suggestedLangName, currentLangName) {
    const modal = document.getElementById('languageSwitchModal');
    const message = document.getElementById('languageSwitchMessage');
    const switchBtn = document.getElementById('switchToLocalLang');
    const keepBtn = document.getElementById('keepCurrentLang');
    
    if (!modal || !message || !switchBtn || !keepBtn) {
        console.error('Language switch modal elements not found');
        return;
    }
    
    // Set the message
    message.textContent = `You've set your location to ${newLocation.city}, ${newLocation.state}. Would you like to switch to ${suggestedLangName} (the local language) or keep using ${currentLangName}?`;
    
    // Set up button handlers
    switchBtn.onclick = async () => {
        await setLanguage(suggestedLang, true); // Mark as manual selection
        if (typeof showToast === 'function') {
            showToast(`Language switched to ${suggestedLangName}`, 'success');
        }
        closeLanguageSwitchModal();
    };
    
    keepBtn.onclick = () => {
        localStorage.setItem('userLangManual', 'true');
        if (typeof showToast === 'function') {
            showToast(`Keeping ${currentLangName} as your preferred language`, 'info');
        }
        closeLanguageSwitchModal();
    };
    
    // Show modal
    modal.style.display = 'block';
}

/**
 * Close language switch modal
 */
function closeLanguageSwitchModal() {
    const modal = document.getElementById('languageSwitchModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Clear translation cache
 */
function clearTranslationCache() {
    translationCache.clear();
    console.log('Translation cache cleared');
}

// Export functions for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        translateText, 
        translateBatch, 
        translatePage, 
        setLanguage, 
        t, 
        initAITranslations,
        clearTranslationCache,
        showLanguageSwitchModal,
        closeLanguageSwitchModal
    };
}

/**
 * Sync location, language, and currency
 */
async function syncLocationLanguageCurrency(locationData) {
    console.log('🔄 Syncing location, language, and currency...', locationData);
    
    // 1. Update location in localStorage
    localStorage.setItem('userLocation', JSON.stringify(locationData));
    
    // 2. Get suggested language for this location
    const suggestedLang = await getLanguageFromCountry(locationData.country);
    console.log(`📍 Location: ${locationData.city}, ${locationData.state}, ${locationData.country_name}`);
    console.log(`🗣️ Suggested language: ${suggestedLang}`);
    
    // 3. Get currency for this location
    const currency = getCurrencyForCountry(locationData.country);
    console.log(`💰 Currency: ${currency}`);
    localStorage.setItem('userCurrency', currency);
    
    // 4. Update UI
    updateLocationUI(locationData);
    updateCurrencyUI(currency);
    
    // 5. Prompt for language switch if needed
    await promptLanguageSwitch(locationData);
}

/**
 * Get currency for a country
 */
function getCurrencyForCountry(countryCode) {
    const currencyMap = {
        'US': 'USD', 'CA': 'CAD', 'GB': 'GBP', 'EU': 'EUR', 'IN': 'INR',
        'CN': 'CNY', 'JP': 'JPY', 'AU': 'AUD', 'MX': 'MXN', 'BR': 'BRL',
        'ZA': 'ZAR', 'RU': 'RUB', 'KR': 'KRW', 'ID': 'IDR', 'TR': 'TRY',
        'SA': 'SAR', 'AE': 'AED', 'EG': 'EGP', 'NG': 'NGN', 'KE': 'KES',
        'PH': 'PHP', 'TH': 'THB', 'VN': 'VND', 'MY': 'MYR', 'SG': 'SGD',
        'PK': 'PKR', 'BD': 'BDT', 'AR': 'ARS', 'CL': 'CLP', 'CO': 'COP'
    };
    return currencyMap[countryCode] || 'USD';
}

/**
 * Update location UI
 */
function updateLocationUI(locationData) {
    const locationElement = document.getElementById('currentLocation');
    if (locationElement) {
        locationElement.textContent = `${locationData.city}, ${locationData.state}`;
        console.log('✅ Location UI updated');
    }
    
    const zipElement = document.getElementById('currentZip');
    if (zipElement) {
        zipElement.textContent = locationData.zip;
        console.log('✅ ZIP UI updated');
    }
}

/**
 * Update currency UI
 */
function updateCurrencyUI(currency) {
    // Update all currency symbols on the page
    const currencySymbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹', 'JPY': '¥',
        'CNY': '¥', 'CAD': '$', 'AUD': '$', 'MXN': '$', 'BRL': 'R$',
        'ZAR': 'R', 'RUB': '₽', 'KRW': '₩', 'IDR': 'Rp', 'TRY': '₺',
        'SAR': 'SR', 'AED': 'د.إ', 'EGP': 'E£', 'NGN': '₦', 'KES': 'KSh',
        'PHP': '₱', 'THB': '฿', 'VND': '₫', 'MYR': 'RM', 'SGD': '$',
        'PKR': 'Rs', 'BDT': '৳', 'ARS': '$', 'CLP': '$', 'COP': '$'
    };
    
    const symbol = currencySymbols[currency] || '$';
    localStorage.setItem('currencySymbol', symbol);
    console.log(`✅ Currency set to ${currency} (${symbol})`);
    
    // Update any price displays on the page
    const priceElements = document.querySelectorAll('.price, [data-currency]');
    priceElements.forEach(el => {
        if (el.dataset.currency) {
            el.dataset.currency = symbol;
        }
    });
}

// Make functions globally available
if (typeof window !== 'undefined') {
    window.showLanguageSwitchModal = showLanguageSwitchModal;
    window.closeLanguageSwitchModal = closeLanguageSwitchModal;
    window.promptLanguageSwitch = promptLanguageSwitch;
    window.syncLocationLanguageCurrency = syncLocationLanguageCurrency;
}
