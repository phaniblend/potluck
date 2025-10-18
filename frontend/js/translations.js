/**
 * Translation System for Potluck
 * Supports multiple languages with automatic translation
 */

const translations = {
    en: {
        // Navbar
        'potluck_chef': 'Potluck',
        'logout': 'Logout',
        'location': 'Location',
        'language': 'Language',
        'use_current_location': 'Use Current Location',
        
        // Welcome section
        'welcome_back': 'Welcome back, {name}!',
        'manage_dishes_orders': 'Manage your dishes and orders from your dashboard',
        
        // Stats
        'active_dishes': 'Active Dishes',
        'pending_orders': 'Pending Orders',
        'total_earnings': 'Total Earnings',
        'average_rating': 'Average Rating',
        'reviews': 'reviews',
        
        // Buttons
        'add_new_dish': 'Add New Dish',
        'view_orders': 'View Orders',
        'save': 'Save',
        'cancel': 'Cancel',
        'edit': 'Edit',
        'delete': 'Delete',
        'hide': 'Hide',
        'available': 'Available',
        'unavailable': 'Unavailable',
        
        // Dish management
        'your_dishes': 'Your Dishes',
        'no_dishes': 'No dishes yet. Add your first dish!',
        'dish_name': 'Dish Name',
        'price': 'Price',
        'description': 'Description',
        'cuisine_type': 'Cuisine Type',
        'meal_type': 'Meal Type',
        'ingredients': 'Ingredients',
        'portion_size': 'Portion Size',
        'spice_level': 'Spice Level',
        'dietary_info': 'Dietary Info',
        'prep_time': 'Prep Time (minutes)',
        'ai_suggest': 'AI Suggest',
        'use': 'Use',
        
        // Spice levels
        'mild': 'Mild',
        'medium': 'Medium',
        'hot': 'Hot',
        'very_hot': 'Very Hot',
        
        // Meal types
        'breakfast': 'Breakfast',
        'lunch': 'Lunch',
        'dinner': 'Dinner',
        'snack': 'Snack',
        'dessert': 'Dessert',
        
        // Dietary
        'vegetarian': 'Vegetarian',
        'vegan': 'Vegan',
        'gluten_free': 'Gluten-Free',
        'halal': 'Halal',
        'kosher': 'Kosher',
        
        // Dish card content
        'available': 'Available',
        'unavailable': 'Unavailable',
        'cuisine': 'Cuisine',
        'spice': 'Spice',
        'orders': 'orders',
        'show': 'Show',
        'start_adding': 'Start by adding your first dish!',
        
        // Modals
        'select_language': 'Select Language',
        'price_too_high': 'Price Too High',
        'cost_breakdown': 'Cost Breakdown',
        'ingredients_cost': 'Ingredients Cost',
        'total_cost': 'Total Cost',
        'recommended_margin': 'Recommended Margin',
        'suggested_price': 'Suggested Price',
        'maximum_allowed': 'Maximum Allowed',
        'ai_analysis': 'AI Analysis',
        'premium_ingredients': 'Premium Ingredients',
        'edit_manually': 'Edit Manually',
        
        // Messages
        'loading': 'Loading...',
        'error': 'Error',
        'success': 'Success',
        'detecting_location': 'Detecting your location...',
        'location_detected': 'Location detected successfully!',
        'location_error': 'Could not detect location. Please allow location access.',
    },
    
    es: {
        // Navbar
        'potluck_chef': 'Potluck',
        'logout': 'Cerrar sesión',
        'location': 'Ubicación',
        'language': 'Idioma',
        'use_current_location': 'Usar ubicación actual',
        
        // Welcome section
        'welcome_back': '¡Bienvenido de nuevo, {name}!',
        'manage_dishes_orders': 'Gestiona tus platos y pedidos desde tu panel',
        
        // Stats
        'active_dishes': 'Platos activos',
        'pending_orders': 'Pedidos pendientes',
        'total_earnings': 'Ganancias totales',
        'average_rating': 'Calificación promedio',
        'reviews': 'reseñas',
        
        // Buttons
        'add_new_dish': 'Agregar nuevo plato',
        'view_orders': 'Ver pedidos',
        'save': 'Guardar',
        'cancel': 'Cancelar',
        'edit': 'Editar',
        'delete': 'Eliminar',
        'hide': 'Ocultar',
        'available': 'Disponible',
        'unavailable': 'No disponible',
        
        // Dish management
        'your_dishes': 'Tus platos',
        'no_dishes': '¡No hay platos todavía. Agrega tu primer plato!',
        'dish_name': 'Nombre del plato',
        'price': 'Precio',
        'description': 'Descripción',
        'cuisine_type': 'Tipo de cocina',
        'meal_type': 'Tipo de comida',
        'ingredients': 'Ingredientes',
        'portion_size': 'Tamaño de la porción',
        'spice_level': 'Nivel de picante',
        'dietary_info': 'Información dietética',
        'prep_time': 'Tiempo de preparación (minutos)',
        'ai_suggest': 'Sugerencia de IA',
        'use': 'Usar',
        
        // Spice levels
        'mild': 'Suave',
        'medium': 'Medio',
        'hot': 'Picante',
        'very_hot': 'Muy picante',
        
        // Meal types
        'breakfast': 'Desayuno',
        'lunch': 'Almuerzo',
        'dinner': 'Cena',
        'snack': 'Merienda',
        'dessert': 'Postre',
        
        // Dietary
        'vegetarian': 'Vegetariano',
        'vegan': 'Vegano',
        'gluten_free': 'Sin gluten',
        'halal': 'Halal',
        'kosher': 'Kosher',
        
        // Dish card content
        'available': 'Disponible',
        'unavailable': 'No disponible',
        'cuisine': 'Cocina',
        'spice': 'Picante',
        'orders': 'pedidos',
        'show': 'Mostrar',
        'start_adding': '¡Comienza agregando tu primer plato!',
        
        // Modals
        'select_language': 'Seleccionar idioma',
        'price_too_high': 'Precio demasiado alto',
        'cost_breakdown': 'Desglose de costos',
        'ingredients_cost': 'Costo de ingredientes',
        'total_cost': 'Costo total',
        'recommended_margin': 'Margen recomendado',
        'suggested_price': 'Precio sugerido',
        'maximum_allowed': 'Máximo permitido',
        'ai_analysis': 'Análisis de IA',
        'premium_ingredients': 'Ingredientes premium',
        'edit_manually': 'Editar manualmente',
        
        // Messages
        'loading': 'Cargando...',
        'error': 'Error',
        'success': 'Éxito',
        'detecting_location': 'Detectando tu ubicación...',
        'location_detected': '¡Ubicación detectada con éxito!',
        'location_error': 'No se pudo detectar la ubicación. Por favor, permite el acceso a la ubicación.',
    },
    
    hi: {
        'potluck_chef': 'पॉटलक शेफ',
        'logout': 'लॉगआउट',
        'location': 'स्थान',
        'language': 'भाषा',
        'use_current_location': 'वर्तमान स्थान उपयोग करें',
        'welcome_back': 'वापस स्वागत है, {name}!',
        'manage_dishes_orders': 'अपने डैशबोर्ड से अपने व्यंजन और ऑर्डर प्रबंधित करें',
        'active_dishes': 'सक्रिय व्यंजन',
        'pending_orders': 'लंबित ऑर्डर',
        'total_earnings': 'कुल कमाई',
        'average_rating': 'औसत रेटिंग',
        'reviews': 'समीक्षाएं',
        'add_new_dish': 'नया व्यंजन जोड़ें',
        'view_orders': 'ऑर्डर देखें',
        'your_dishes': 'आपके व्यंजन',
        'save': 'सहेजें',
        'cancel': 'रद्द करें',
        'edit': 'संपादित करें',
        'delete': 'हटाएं',
        'loading': 'लोड हो रहा है...',
        'available': 'उपलब्ध',
        'unavailable': 'अनुपलब्ध',
        'cuisine': 'व्यंजन',
        'spice': 'मसाला',
        'orders': 'ऑर्डर',
        'show': 'दिखाएं',
        'start_adding': 'अपना पहला व्यंजन जोड़कर शुरू करें!',
    },
    
    fr: {
        'potluck_chef': 'Potluck',
        'logout': 'Déconnexion',
        'location': 'Emplacement',
        'language': 'Langue',
        'use_current_location': 'Utiliser l\'emplacement actuel',
        'welcome_back': 'Bienvenue, {name}!',
        'manage_dishes_orders': 'Gérez vos plats et commandes depuis votre tableau de bord',
        'active_dishes': 'Plats actifs',
        'pending_orders': 'Commandes en attente',
        'total_earnings': 'Gains totaux',
        'average_rating': 'Note moyenne',
        'reviews': 'avis',
        'add_new_dish': 'Ajouter un nouveau plat',
        'view_orders': 'Voir les commandes',
        'your_dishes': 'Vos plats',
    },
    
    pt: {
        'potluck_chef': 'Potluck',
        'logout': 'Sair',
        'location': 'Localização',
        'language': 'Idioma',
        'use_current_location': 'Usar localização atual',
        'welcome_back': 'Bem-vindo de volta, {name}!',
        'manage_dishes_orders': 'Gerencie seus pratos e pedidos no painel',
        'active_dishes': 'Pratos ativos',
        'pending_orders': 'Pedidos pendentes',
        'total_earnings': 'Ganhos totais',
        'average_rating': 'Avaliação média',
        'reviews': 'avaliações',
        'add_new_dish': 'Adicionar novo prato',
        'view_orders': 'Ver pedidos',
        'your_dishes': 'Seus pratos',
    },
    
    zh: {
        'potluck_chef': 'Potluck 厨师',
        'logout': '登出',
        'location': '位置',
        'language': '语言',
        'use_current_location': '使用当前位置',
        'welcome_back': '欢迎回来，{name}！',
        'manage_dishes_orders': '从您的仪表板管理您的菜肴和订单',
        'active_dishes': '活跃菜肴',
        'pending_orders': '待处理订单',
        'total_earnings': '总收入',
        'average_rating': '平均评分',
        'reviews': '评论',
        'add_new_dish': '添加新菜肴',
        'view_orders': '查看订单',
        'your_dishes': '您的菜肴',
    },
    
    ar: {
        'potluck_chef': 'طاهي بوتلاك',
        'logout': 'تسجيل الخروج',
        'location': 'الموقع',
        'language': 'اللغة',
        'use_current_location': 'استخدام الموقع الحالي',
        'welcome_back': 'مرحبًا بعودتك، {name}!',
        'manage_dishes_orders': 'إدارة أطباقك وطلباتك من لوحة التحكم',
        'active_dishes': 'الأطباق النشطة',
        'pending_orders': 'الطلبات المعلقة',
        'total_earnings': 'إجمالي الأرباح',
        'average_rating': 'متوسط التقييم',
        'reviews': 'تعليقات',
        'add_new_dish': 'إضافة طبق جديد',
        'view_orders': 'عرض الطلبات',
        'your_dishes': 'أطباقك',
    },
    
    te: {
        'potluck_chef': 'పాట్లక్ చెఫ్',
        'logout': 'లాగ్ అవుట్',
        'location': 'స్థానం',
        'language': 'భాష',
        'use_current_location': 'ప్రస్తుత స్థానాన్ని ఉపయోగించండి',
        'welcome_back': 'మళ్లీ స్వాగతం, {name}!',
        'manage_dishes_orders': 'మీ డ్యాష్‌బోర్డ్ నుండి మీ వంటకాలు మరియు ఆర్డర్‌లను నిర్వహించండి',
        'active_dishes': 'క్రియాశీల వంటకాలు',
        'pending_orders': 'వేచి ఉన్న ఆర్డర్‌లు',
        'total_earnings': 'మొత్తం సంపాదన',
        'average_rating': 'సగటు రేటింగ్',
        'reviews': 'సమీక్షలు',
        'add_new_dish': 'కొత్త వంటకం జోడించండి',
        'view_orders': 'ఆర్డర్‌లను చూడండి',
        'your_dishes': 'మీ వంటకాలు',
        'save': 'సేవ్ చేయండి',
        'cancel': 'రద్దు చేయండి',
        'edit': 'సవరించండి',
        'delete': 'తొలగించండి',
        'loading': 'లోడ్ అవుతోంది...',
        'available': 'అందుబాటులో',
        'unavailable': 'అందుబాటులో లేదు',
        'cuisine': 'వంటకం',
        'spice': 'మసాలా',
        'orders': 'ఆర్డర్‌లు',
        'show': 'చూపించు',
        'start_adding': 'మీ మొదటి వంటకాన్ని జోడించడం ద్వారా ప్రారంభించండి!',
    },
    
    bn: {
        'potluck_chef': 'পটলাক শেফ',
        'logout': 'লগ আউট',
        'location': 'অবস্থান',
        'language': 'ভাষা',
        'use_current_location': 'বর্তমান অবস্থান ব্যবহার করুন',
        'welcome_back': 'আবার স্বাগতম, {name}!',
        'manage_dishes_orders': 'আপনার ড্যাশবোর্ড থেকে আপনার খাবার এবং অর্ডার পরিচালনা করুন',
        'active_dishes': 'সক্রিয় খাবার',
        'pending_orders': 'অপেক্ষমাণ অর্ডার',
        'total_earnings': 'মোট আয়',
        'average_rating': 'গড় রেটিং',
        'reviews': 'রিভিউ',
        'add_new_dish': 'নতুন খাবার যোগ করুন',
        'view_orders': 'অর্ডার দেখুন',
        'your_dishes': 'আপনার খাবার',
        'save': 'সংরক্ষণ করুন',
        'cancel': 'বাতিল করুন',
        'edit': 'সম্পাদনা করুন',
        'delete': 'মুছে ফেলুন',
        'loading': 'লোড হচ্ছে...',
        'available': 'উপলব্ধ',
        'unavailable': 'অনুপলব্ধ',
        'cuisine': 'রান্না',
        'spice': 'মসলা',
        'orders': 'অর্ডার',
    },
    
    ta: {
        'potluck_chef': 'பாட்லக் சேஃப்',
        'logout': 'வெளியேறு',
        'location': 'இடம்',
        'language': 'மொழி',
        'use_current_location': 'தற்போதைய இடத்தை பயன்படுத்தவும்',
        'welcome_back': 'மீண்டும் வரவேற்கிறோம், {name}!',
        'manage_dishes_orders': 'உங்கள் டாஷ்போர்டில் இருந்து உங்கள் உணவுகள் மற்றும் ஆர்டர்களை நிர்வகிக்கவும்',
        'active_dishes': 'செயலில் உள்ள உணவுகள்',
        'pending_orders': 'நிலுவையில் உள்ள ஆர்டர்கள்',
        'total_earnings': 'மொத்த வருவாய்',
        'average_rating': 'சராசரி மதிப்பீடு',
        'reviews': 'விமர்சனங்கள்',
        'add_new_dish': 'புதிய உணவு சேர்க்கவும்',
        'view_orders': 'ஆர்டர்களை பார்க்கவும்',
        'your_dishes': 'உங்கள் உணவுகள்',
        'save': 'சேமிக்கவும்',
        'cancel': 'ரத்து செய்யவும்',
        'edit': 'திருத்தவும்',
        'delete': 'நீக்கவும்',
        'loading': 'லோட் ஆகிறது...',
        'available': 'கிடைக்கும்',
        'unavailable': 'கிடைக்காது',
        'cuisine': 'சமையல்',
        'spice': 'மசாலா',
        'orders': 'ஆர்டர்கள்',
    },
    
    ru: {
        'potluck_chef': 'Повар Потлак',
        'logout': 'Выйти',
        'location': 'Местоположение',
        'language': 'Язык',
        'use_current_location': 'Использовать текущее местоположение',
        'welcome_back': 'Добро пожаловать, {name}!',
        'manage_dishes_orders': 'Управляйте своими блюдами и заказами с панели управления',
        'active_dishes': 'Активные блюда',
        'pending_orders': 'Ожидающие заказы',
        'total_earnings': 'Общий доход',
        'average_rating': 'Средний рейтинг',
        'reviews': 'отзывов',
        'add_new_dish': 'Добавить новое блюдо',
        'view_orders': 'Просмотр заказов',
        'your_dishes': 'Ваши блюда',
        'save': 'Сохранить',
        'cancel': 'Отмена',
        'edit': 'Редактировать',
        'delete': 'Удалить',
        'loading': 'Загрузка...',
        'available': 'Доступно',
        'unavailable': 'Недоступно',
        'cuisine': 'Кухня',
        'spice': 'Острота',
        'orders': 'заказы',
    },
    
    id: {
        'potluck_chef': 'Koki Potluck',
        'logout': 'Keluar',
        'location': 'Lokasi',
        'language': 'Bahasa',
        'use_current_location': 'Gunakan lokasi saat ini',
        'welcome_back': 'Selamat datang kembali, {name}!',
        'manage_dishes_orders': 'Kelola hidangan dan pesanan Anda dari dashboard',
        'active_dishes': 'Hidangan Aktif',
        'pending_orders': 'Pesanan Tertunda',
        'total_earnings': 'Total Penghasilan',
        'average_rating': 'Rating Rata-rata',
        'reviews': 'ulasan',
        'add_new_dish': 'Tambah Hidangan Baru',
        'view_orders': 'Lihat Pesanan',
        'your_dishes': 'Hidangan Anda',
        'save': 'Simpan',
        'cancel': 'Batal',
        'edit': 'Edit',
        'delete': 'Hapus',
        'loading': 'Memuat...',
        'available': 'Tersedia',
        'unavailable': 'Tidak Tersedia',
        'cuisine': 'Masakan',
        'spice': 'Pedas',
        'orders': 'pesanan',
    },
};

// Language names for display
const languageNames = {
    en: 'English',
    es: 'Español',
    hi: 'हिन्दी',
    bn: 'বাংলা',
    ta: 'தமிழ்',
    te: 'తెలుగు',
    zh: '中文',
    ar: 'العربية',
    pt: 'Português',
    fr: 'Français',
    ru: 'Русский',
    id: 'Indonesian'
};

// Country to language mapping
const countryLanguageMap = {
    'US': 'en', 'GB': 'en', 'CA': 'en', 'AU': 'en', 'NZ': 'en', 'IE': 'en',
    'ES': 'es', 'MX': 'es', 'AR': 'es', 'CO': 'es', 'CL': 'es', 'PE': 'es',
    'IN': 'hi', 
    'FR': 'fr', 'BE': 'fr', 'CH': 'fr',
    'BR': 'pt', 'PT': 'pt',
    'CN': 'zh', 'TW': 'zh', 'HK': 'zh',
    'SA': 'ar', 'AE': 'ar', 'EG': 'ar', 'MA': 'ar',
    'ID': 'id',
    'RU': 'ru'
};

// Current language
let currentLang = localStorage.getItem('userLang') || 'en';

/**
 * Get translation for a key
 */
function t(key, replacements = {}) {
    let text = translations[currentLang]?.[key] || translations['en'][key] || key;
    
    // Replace placeholders like {name}
    Object.keys(replacements).forEach(placeholder => {
        text = text.replace(`{${placeholder}}`, replacements[placeholder]);
    });
    
    return text;
}

/**
 * Translate all elements with data-i18n attribute
 */
function translatePage() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const replacements = {};
        
        // Check for dynamic replacements
        if (element.hasAttribute('data-i18n-name')) {
            replacements.name = element.getAttribute('data-i18n-name');
        }
        
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            element.placeholder = t(key, replacements);
        } else {
            element.textContent = t(key, replacements);
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
 * Set language
 */
function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('userLang', lang);
    document.getElementById('currentLanguage').textContent = languageNames[lang];
    translatePage();
}

/**
 * Detect language from IP
 */
async function detectLanguageFromIP() {
    try {
        const response = await fetch('https://ipapi.co/json/');
        const data = await response.json();
        const countryCode = data.country_code;
        const detectedLang = countryLanguageMap[countryCode] || 'en';
        
        // Only auto-set if user hasn't manually selected a language
        if (!localStorage.getItem('userLangManual')) {
            setLanguage(detectedLang);
            console.log(`✅ Language auto-detected: ${detectedLang} (${countryCode})`);
        }
        
        return detectedLang;
    } catch (error) {
        console.error('Failed to detect language from IP:', error);
        return 'en';
    }
}

/**
 * Initialize translation system
 */
async function initTranslations() {
    // Check if user has manually selected a language
    if (!localStorage.getItem('userLang')) {
        await detectLanguageFromIP();
    } else {
        currentLang = localStorage.getItem('userLang');
    }
    
    translatePage();
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { t, setLanguage, translatePage, detectLanguageFromIP, initTranslations };
}


