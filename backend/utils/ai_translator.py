"""
AI-Powered Real-time Translation Service
Uses Anthropic Claude for high-quality translations
"""

import anthropic
import json
from typing import Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv()

class AITranslator:
    """AI-powered translation service using Anthropic Claude"""
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.has_api_key = bool(self.api_key)
        self.client = None
        
        if self.has_api_key:
            try:
                # Initialize Anthropic client
                self.client = anthropic.Anthropic(api_key=self.api_key)
                print("AI Translator initialized successfully")
            except Exception as e:
                print(f"Failed to initialize AI Translator: {e}")
                self.has_api_key = False
                self.client = None
        else:
            print("No Anthropic API key found, using simple translation fallback")
    
    def translate_text(self, text: str, target_language: str, source_language: str = "en") -> str:
        """Translate text to target language using AI"""
        if not self.has_api_key or not self.client:
            return self._fallback_translation(text, target_language)
        
        try:
            # Language code mapping
            language_codes = {
                'en': 'English',
                'es': 'Spanish', 
                'hi': 'Hindi',
                'te': 'Telugu',
                'bn': 'Bengali',
                'ta': 'Tamil',
                'zh': 'Chinese',
                'ar': 'Arabic',
                'pt': 'Portuguese',
                'fr': 'French',
                'ru': 'Russian',
                'id': 'Indonesian'
            }
            
            target_lang_name = language_codes.get(target_language, 'English')
            source_lang_name = language_codes.get(source_language, 'English')
            
            prompt = f"""Translate the following text from {source_lang_name} to {target_lang_name}. 
            Keep the translation natural and contextually appropriate for a food delivery app.
            Only return the translated text, nothing else.
            
            Text to translate: "{text}"
            """
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            translated_text = response.content[0].text.strip()
            return translated_text
            
        except Exception as e:
            print(f"AI translation failed: {e}")
            return self._fallback_translation(text, target_language)
    
    def translate_batch(self, texts: list, target_language: str, source_language: str = "en") -> Dict[str, str]:
        """Translate multiple texts at once for efficiency"""
        if not self.has_api_key or not self.client:
            return {text: self._fallback_translation(text, target_language) for text in texts}
        
        try:
            language_codes = {
                'en': 'English', 'es': 'Spanish', 'hi': 'Hindi', 'te': 'Telugu',
                'bn': 'Bengali', 'ta': 'Tamil', 'zh': 'Chinese', 'ar': 'Arabic',
                'pt': 'Portuguese', 'fr': 'French', 'ru': 'Russian', 'id': 'Indonesian'
            }
            
            target_lang_name = language_codes.get(target_language, 'English')
            source_lang_name = language_codes.get(source_language, 'English')
            
            # Create a single prompt for all texts
            texts_str = '\n'.join([f'"{text}"' for text in texts])
            
            prompt = f"""Translate the following texts from {source_lang_name} to {target_lang_name}. 
            Keep translations natural and contextually appropriate for a food delivery app.
            Return only a JSON object with original text as key and translation as value.
            
            Texts to translate:
            {texts_str}
            
            Return format: {{"original text": "translated text", ...}}
            """
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            result = json.loads(response.content[0].text.strip())
            return result
            
        except Exception as e:
            print(f"Batch AI translation failed: {e}")
            return {text: self._fallback_translation(text, target_language) for text in texts}
    
    def _fallback_translation(self, text: str, target_language: str) -> str:
        """Simple fallback translation using basic language mappings"""
        # Basic language mappings for common terms
        basic_translations = {
            'logout': {'te': 'లాగ్ అవుట్', 'es': 'Cerrar sesión', 'hi': 'लॉग आउट'},
            'location': {'te': 'స్థానం', 'es': 'Ubicación', 'hi': 'स्थान'},
            'language': {'te': 'భాష', 'es': 'Idioma', 'hi': 'भाषा'},
            'cancel': {'te': 'రద్దు చేయండి', 'es': 'Cancelar', 'hi': 'रद्द करें'},
            'save': {'te': 'సేవ్ చేయండి', 'es': 'Guardar', 'hi': 'सहेजें'},
            'use_current_location': {'te': 'ప్రస్తుత స్థానాన్ని ఉపయోగించండి', 'es': 'Usar ubicación actual', 'hi': 'वर्तमान स्थान का उपयोग करें'},
            'manage_dishes_orders': {'te': 'మీ వంటకాలు మరియు ఆర్డర్‌లను మీ డాష్‌బోర్డ్ నుండి నిర్వహించండి', 'es': 'Gestiona tus platos y pedidos desde tu panel', 'hi': 'अपने व्यंजन और ऑर्डर को अपने डैशबोर्ड से प्रबंधित करें'},
            'select_language': {'te': 'భాషను ఎంచుకోండి', 'es': 'Seleccionar idioma', 'hi': 'भाषा चुनें'},
            'enter_location_manually': {'te': 'స్థానాన్ని మాన్యువల్‌గా నమోదు చేయండి', 'es': 'Introducir ubicación manualmente', 'hi': 'स्थान मैन्युअल रूप से दर्ज करें'},
            'welcome_back': {'te': 'స్వాగతం, {name}!', 'es': '¡Bienvenido de nuevo, {name}!', 'hi': 'वापस स्वागत है, {name}!'}
        }
        
        if text in basic_translations and target_language in basic_translations[text]:
            return basic_translations[text][target_language]
        
        # For any other text, return original
        return text

# Global instance
ai_translator = AITranslator()
