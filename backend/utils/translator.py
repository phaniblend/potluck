"""
AI-powered Translation Service for Potluck
Multi-language support for global home chefs
"""

import os
import json
from typing import Dict, List, Optional
import anthropic
from dotenv import load_dotenv

load_dotenv()

class TranslationService:
    """AI-powered translation for app localization"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY', '')
        )
        
        # Supported languages with their local names
        self.supported_languages = {
            'en': 'English',
            'es': 'Español (Spanish)',
            'pt': 'Português (Portuguese)',
            'hi': 'हिन्दी (Hindi)',
            'bn': 'বাংলা (Bengali)',
            'ta': 'தமிழ் (Tamil)',
            'te': 'తెలుగు (Telugu)',
            'ur': 'اردو (Urdu)',
            'ar': 'العربية (Arabic)',
            'zh': '中文 (Chinese)',
            'ja': '日本語 (Japanese)',
            'ko': '한국어 (Korean)',
            'th': 'ไทย (Thai)',
            'vi': 'Tiếng Việt (Vietnamese)',
            'id': 'Bahasa Indonesia',
            'ms': 'Bahasa Melayu (Malay)',
            'tl': 'Tagalog (Filipino)',
            'ru': 'Русский (Russian)',
            'uk': 'Українська (Ukrainian)',
            'pl': 'Polski (Polish)',
            'ro': 'Română (Romanian)',
            'tr': 'Türkçe (Turkish)',
            'fr': 'Français (French)',
            'de': 'Deutsch (German)',
            'it': 'Italiano (Italian)',
            'sw': 'Kiswahili (Swahili)'
        }
        
        # Cache for common translations
        self.translation_cache = {}
        
        # Common app phrases for quick translation
        self.common_phrases = {
            'welcome': 'Welcome to Potluck',
            'homemade_food': 'Homemade Food Marketplace',
            'add_dish': 'Add New Dish',
            'my_orders': 'My Orders',
            'earnings': 'Earnings',
            'price': 'Price',
            'ingredients': 'Ingredients',
            'portion_size': 'Portion Size',
            'available_now': 'Available Now',
            'order_now': 'Order Now',
            'chef_profile': 'Chef Profile',
            'customer': 'Customer',
            'delivery_agent': 'Delivery Agent',
            'signup': 'Sign Up',
            'login': 'Login',
            'logout': 'Logout'
        }
    
    def translate_text(self, text: str, target_lang: str, 
                       source_lang: str = 'en') -> Dict:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'hi' for Hindi)
            source_lang: Source language code (default: 'en')
        """
        
        # Check cache first
        cache_key = f"{source_lang}:{target_lang}:{text}"
        if cache_key in self.translation_cache:
            return {
                'success': True,
                'translated_text': self.translation_cache[cache_key],
                'from_cache': True
            }
        
        # Don't translate if same language
        if source_lang == target_lang:
            return {
                'success': True,
                'translated_text': text,
                'from_cache': False
            }
        
        target_name = self.supported_languages.get(target_lang, target_lang)
        
        prompt = f"""Translate the following text from {source_lang} to {target_lang} ({target_name}).
        
        Text to translate: "{text}"
        
        Rules:
        1. Keep the translation natural and conversational
        2. Use simple, everyday language that common people understand
        3. For food items, use local names where appropriate
        4. Maintain the friendly tone
        5. If it's a dish name, keep it recognizable
        
        Respond with ONLY the translated text, nothing else."""
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            translated = message.content[0].text.strip()
            
            # Cache the translation
            self.translation_cache[cache_key] = translated
            
            return {
                'success': True,
                'translated_text': translated,
                'from_cache': False
            }
            
        except Exception as e:
            print(f"Translation error: {e}")
            return {
                'success': False,
                'translated_text': text,  # Return original
                'error': str(e)
            }
    
    def translate_dish(self, dish_data: Dict, target_lang: str) -> Dict:
        """
        Translate a complete dish listing
        
        Args:
            dish_data: Dictionary with dish details
            target_lang: Target language code
        """
        
        if target_lang == 'en':
            return dish_data  # No translation needed
        
        # Build translation request for all dish fields
        fields_to_translate = {
            'name': dish_data.get('name', ''),
            'description': dish_data.get('description', ''),
            'ingredients': ', '.join(dish_data.get('ingredients', [])),
            'portion_size': dish_data.get('portion_size', '')
        }
        
        prompt = f"""Translate this food dish information to {self.supported_languages.get(target_lang, target_lang)}.
        Keep dish names recognizable but add local context.
        
        Dish Name: {fields_to_translate['name']}
        Description: {fields_to_translate['description']}
        Ingredients: {fields_to_translate['ingredients']}
        Portion Size: {fields_to_translate['portion_size']}
        
        Respond in JSON format:
        {{
            "name": "translated name",
            "description": "translated description",
            "ingredients": "translated ingredients",
            "portion_size": "translated portion"
        }}"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            translations = json.loads(response_text)
            
            # Merge translations back
            translated_dish = dish_data.copy()
            translated_dish['name'] = translations['name']
            translated_dish['description'] = translations['description']
            translated_dish['ingredients'] = translations['ingredients'].split(', ')
            translated_dish['portion_size'] = translations['portion_size']
            translated_dish['original_language'] = 'en'
            translated_dish['translated_to'] = target_lang
            
            return translated_dish
            
        except Exception as e:
            print(f"Dish translation error: {e}")
            return dish_data  # Return original if translation fails
    
    def translate_ui_bundle(self, target_lang: str) -> Dict:
        """
        Get all common UI translations for a language
        Used for initial app load
        """
        
        if target_lang == 'en':
            return self.common_phrases
        
        bundle = {}
        for key, phrase in self.common_phrases.items():
            result = self.translate_text(phrase, target_lang)
            bundle[key] = result['translated_text']
        
        return bundle
    
    def detect_language(self, text: str) -> str:
        """Detect the language of given text"""
        
        prompt = f"""Detect the language of this text: "{text}"
        
        Respond with ONLY the 2-letter language code (en, es, hi, zh, etc.)"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            lang_code = message.content[0].text.strip().lower()
            return lang_code if lang_code in self.supported_languages else 'en'
            
        except:
            return 'en'  # Default to English
    
    def get_localized_content(self, user_location: str) -> Dict:
        """
        Get localized content suggestions based on location
        """
        
        prompt = f"""For a home chef in {user_location}, provide localization advice.
        
        Respond in JSON:
        {{
            "recommended_language": "language_code",
            "local_cuisine_types": ["cuisine1", "cuisine2"],
            "popular_local_dishes": ["dish1", "dish2", "dish3"],
            "cultural_considerations": "brief advice",
            "price_currency": "currency_code"
        }}"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return json.loads(message.content[0].text)
            
        except:
            return {
                "recommended_language": "en",
                "local_cuisine_types": ["Local", "International"],
                "popular_local_dishes": ["Various dishes"],
                "cultural_considerations": "Be respectful of local customs",
                "price_currency": "USD"
            }
    
    def translate_sms(self, message: str, phone_number: str, 
                     target_lang: str = None) -> str:
        """
        Translate SMS messages for notifications
        Keep them short and simple
        """
        
        if not target_lang:
            # Try to detect from phone country code
            # This is simplified - in production, use proper phone number parsing
            target_lang = 'en'  # Default
        
        if target_lang == 'en':
            return message
        
        prompt = f"""Translate this SMS message to {self.supported_languages.get(target_lang, target_lang)}.
        Keep it SHORT (under 160 characters) and simple.
        
        Message: "{message}"
        
        Reply with ONLY the translation."""
        
        try:
            message_obj = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message_obj.content[0].text.strip()
            
        except:
            return message  # Return original if translation fails


# Singleton instance
translator = TranslationService()

# Helper functions for common translations
def get_user_language(user_id: int) -> str:
    """Get user's preferred language from database"""
    # TODO: Implement database lookup
    # For now, return default
    return 'en'

def translate_for_user(text: str, user_id: int) -> str:
    """Translate text to user's preferred language"""
    user_lang = get_user_language(user_id)
    if user_lang == 'en':
        return text
    
    result = translator.translate_text(text, user_lang)
    return result.get('translated_text', text)