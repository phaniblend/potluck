"""
Global Geolocation and Localization Service
Automatically detects user location and provides localization data
"""

import requests
import json
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import time

@dataclass
class LocationData:
    """Location data structure"""
    latitude: float
    longitude: float
    city: str
    state: str
    country: str
    country_code: str
    postal_code: str
    timezone: str
    currency: str
    currency_symbol: str
    language: str
    language_code: str
    phone_code: str
    is_supported: bool

class GlobalGeolocationService:
    """Global geolocation service using multiple APIs"""
    
    # Free geolocation APIs (with fallbacks)
    GEOLOCATION_APIS = [
        {
            'name': 'ipapi',
            'url': 'http://ip-api.com/json/{ip}',
            'free_limit': '1000 requests/day',
            'fields': ['lat', 'lon', 'city', 'regionName', 'country', 'countryCode', 'zip', 'timezone', 'currency']
        },
        {
            'name': 'ipinfo',
            'url': 'https://ipinfo.io/{ip}/json',
            'free_limit': '1000 requests/day',
            'fields': ['loc', 'city', 'region', 'country', 'postal', 'timezone']
        }
    ]
    
    # Global localization data
    GLOBAL_LOCALIZATION = {
        # North America
        'US': {
            'currency': 'USD', 'symbol': '$', 'language': 'en', 'phone_code': '+1',
            'supported': True, 'pricing_tier': 'medium'
        },
        'CA': {
            'currency': 'CAD', 'symbol': 'C$', 'language': 'en', 'phone_code': '+1',
            'supported': True, 'pricing_tier': 'medium'
        },
        'MX': {
            'currency': 'MXN', 'symbol': '$', 'language': 'es', 'phone_code': '+52',
            'supported': True, 'pricing_tier': 'low'
        },
        
        # Europe
        'GB': {
            'currency': 'GBP', 'symbol': '£', 'language': 'en', 'phone_code': '+44',
            'supported': True, 'pricing_tier': 'high'
        },
        'DE': {
            'currency': 'EUR', 'symbol': '€', 'language': 'de', 'phone_code': '+49',
            'supported': True, 'pricing_tier': 'high'
        },
        'FR': {
            'currency': 'EUR', 'symbol': '€', 'language': 'fr', 'phone_code': '+33',
            'supported': True, 'pricing_tier': 'high'
        },
        'IT': {
            'currency': 'EUR', 'symbol': '€', 'language': 'it', 'phone_code': '+39',
            'supported': True, 'pricing_tier': 'medium'
        },
        'ES': {
            'currency': 'EUR', 'symbol': '€', 'language': 'es', 'phone_code': '+34',
            'supported': True, 'pricing_tier': 'medium'
        },
        
        # Asia
        'IN': {
            'currency': 'INR', 'symbol': '₹', 'language': 'en', 'phone_code': '+91',
            'supported': True, 'pricing_tier': 'low'
        },
        'CN': {
            'currency': 'CNY', 'symbol': '¥', 'language': 'zh', 'phone_code': '+86',
            'supported': True, 'pricing_tier': 'medium'
        },
        'JP': {
            'currency': 'JPY', 'symbol': '¥', 'language': 'ja', 'phone_code': '+81',
            'supported': True, 'pricing_tier': 'high'
        },
        'KR': {
            'currency': 'KRW', 'symbol': '₩', 'language': 'ko', 'phone_code': '+82',
            'supported': True, 'pricing_tier': 'medium'
        },
        'SG': {
            'currency': 'SGD', 'symbol': 'S$', 'language': 'en', 'phone_code': '+65',
            'supported': True, 'pricing_tier': 'high'
        },
        
        # Oceania
        'AU': {
            'currency': 'AUD', 'symbol': 'A$', 'language': 'en', 'phone_code': '+61',
            'supported': True, 'pricing_tier': 'high'
        },
        'NZ': {
            'currency': 'NZD', 'symbol': 'NZ$', 'language': 'en', 'phone_code': '+64',
            'supported': True, 'pricing_tier': 'high'
        },
        
        # South America
        'BR': {
            'currency': 'BRL', 'symbol': 'R$', 'language': 'pt', 'phone_code': '+55',
            'supported': True, 'pricing_tier': 'low'
        },
        'AR': {
            'currency': 'ARS', 'symbol': '$', 'language': 'es', 'phone_code': '+54',
            'supported': True, 'pricing_tier': 'low'
        },
        
        # Africa
        'ZA': {
            'currency': 'ZAR', 'symbol': 'R', 'language': 'en', 'phone_code': '+27',
            'supported': True, 'pricing_tier': 'low'
        },
        'NG': {
            'currency': 'NGN', 'symbol': '₦', 'language': 'en', 'phone_code': '+234',
            'supported': True, 'pricing_tier': 'low'
        },
        'EG': {
            'currency': 'EGP', 'symbol': 'E£', 'language': 'ar', 'phone_code': '+20',
            'supported': True, 'pricing_tier': 'low'
        }
    }
    
    @staticmethod
    def get_location_by_ip(ip_address: str = None) -> Optional[LocationData]:
        """Get location data by IP address"""
        if not ip_address:
            ip_address = '8.8.8.8'  # Default to Google DNS for testing
        
        for api in GlobalGeolocationService.GEOLOCATION_APIS:
            try:
                url = api['url'].format(ip=ip_address)
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    return GlobalGeolocationService._parse_api_response(data, api['name'])
                    
            except Exception as e:
                print(f"Error with {api['name']}: {e}")
                continue
        
        return None
    
    @staticmethod
    def get_location_by_coordinates(lat: float, lon: float) -> Optional[LocationData]:
        """Get location data by coordinates (reverse geocoding)"""
        try:
            # Use OpenStreetMap Nominatim API (free)
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            headers = {'User-Agent': 'PotluckApp/1.0'}
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return GlobalGeolocationService._parse_nominatim_response(data)
                
        except Exception as e:
            print(f"Error with reverse geocoding: {e}")
        
        return None
    
    @staticmethod
    def _parse_api_response(data: Dict, api_name: str) -> LocationData:
        """Parse response from geolocation API"""
        if api_name == 'ipapi':
            return LocationData(
                latitude=float(data.get('lat', 0)),
                longitude=float(data.get('lon', 0)),
                city=data.get('city', ''),
                state=data.get('regionName', ''),
                country=data.get('country', ''),
                country_code=data.get('countryCode', ''),
                postal_code=data.get('zip', ''),
                timezone=data.get('timezone', ''),
                currency=data.get('currency', 'USD'),
                currency_symbol=GlobalGeolocationService._get_currency_symbol(data.get('currency', 'USD')),
                language=GlobalGeolocationService._get_language(data.get('countryCode', 'US')),
                language_code=GlobalGeolocationService._get_language_code(data.get('countryCode', 'US')),
                phone_code=GlobalGeolocationService._get_phone_code(data.get('countryCode', 'US')),
                is_supported=GlobalGeolocationService._is_country_supported(data.get('countryCode', 'US'))
            )
        else:
            # Default parsing for other APIs
            return LocationData(
                latitude=0.0, longitude=0.0,
                city=data.get('city', ''), state=data.get('region', ''),
                country='', country_code='', postal_code=data.get('postal', ''),
                timezone=data.get('timezone', ''), currency='USD', currency_symbol='$',
                language='en', language_code='en', phone_code='+1', is_supported=True
            )
    
    @staticmethod
    def _parse_nominatim_response(data: Dict) -> LocationData:
        """Parse response from Nominatim API"""
        address = data.get('address', {})
        
        return LocationData(
            latitude=float(data.get('lat', 0)),
            longitude=float(data.get('lon', 0)),
            city=address.get('city', address.get('town', address.get('village', ''))),
            state=address.get('state', ''),
            country=address.get('country', ''),
            country_code=address.get('country_code', '').upper(),
            postal_code=address.get('postcode', ''),
            timezone='',
            currency=GlobalGeolocationService._get_currency_by_country(address.get('country_code', 'us')),
            currency_symbol=GlobalGeolocationService._get_currency_symbol(
                GlobalGeolocationService._get_currency_by_country(address.get('country_code', 'us'))
            ),
            language=GlobalGeolocationService._get_language(address.get('country_code', 'us')),
            language_code=GlobalGeolocationService._get_language_code(address.get('country_code', 'us')),
            phone_code=GlobalGeolocationService._get_phone_code(address.get('country_code', 'us')),
            is_supported=GlobalGeolocationService._is_country_supported(address.get('country_code', 'us'))
        )
    
    @staticmethod
    def _get_currency_by_country(country_code: str) -> str:
        """Get currency for country code"""
        country_code = country_code.upper()
        return GlobalGeolocationService.GLOBAL_LOCALIZATION.get(country_code, {}).get('currency', 'USD')
    
    @staticmethod
    def _get_currency_symbol(currency: str) -> str:
        """Get currency symbol"""
        for country_data in GlobalGeolocationService.GLOBAL_LOCALIZATION.values():
            if country_data.get('currency') == currency:
                return country_data.get('symbol', '$')
        return '$'
    
    @staticmethod
    def _get_language(country_code: str) -> str:
        """Get primary language for country"""
        country_code = country_code.upper()
        return GlobalGeolocationService.GLOBAL_LOCALIZATION.get(country_code, {}).get('language', 'en')
    
    @staticmethod
    def _get_language_code(country_code: str) -> str:
        """Get language code for country"""
        country_code = country_code.upper()
        return GlobalGeolocationService.GLOBAL_LOCALIZATION.get(country_code, {}).get('language', 'en')
    
    @staticmethod
    def _get_phone_code(country_code: str) -> str:
        """Get phone code for country"""
        country_code = country_code.upper()
        return GlobalGeolocationService.GLOBAL_LOCALIZATION.get(country_code, {}).get('phone_code', '+1')
    
    @staticmethod
    def _is_country_supported(country_code: str) -> bool:
        """Check if country is supported"""
        country_code = country_code.upper()
        return GlobalGeolocationService.GLOBAL_LOCALIZATION.get(country_code, {}).get('supported', False)
    
    @staticmethod
    def get_supported_countries() -> Dict:
        """Get list of supported countries"""
        return {
            code: {
                'name': data.get('name', code),
                'currency': data.get('currency'),
                'symbol': data.get('symbol'),
                'language': data.get('language'),
                'phone_code': data.get('phone_code'),
                'pricing_tier': data.get('pricing_tier')
            }
            for code, data in GlobalGeolocationService.GLOBAL_LOCALIZATION.items()
            if data.get('supported', False)
        }

# Singleton instance
geolocation_service = GlobalGeolocationService() 