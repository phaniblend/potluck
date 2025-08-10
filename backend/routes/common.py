"""
Common routes for all users
Handles translations, languages, and shared features
"""

from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.translator import translator
from utils.price_advisor import price_advisor

bp = Blueprint('common', __name__)

@bp.route('/languages')
def get_languages():
    """Get list of supported languages"""
    return jsonify({
        'success': True,
        'languages': translator.supported_languages
    })

@bp.route('/translate', methods=['POST'])
def translate_text():
    """Translate text to target language"""
    try:
        data = request.json
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'en')
        source_lang = data.get('source_lang', 'en')
        
        result = translator.translate_text(text, target_lang, source_lang)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/translate-ui/<lang_code>')
def get_ui_translations(lang_code):
    """Get all UI translations for a language"""
    try:
        translations = translator.translate_ui_bundle(lang_code)
        return jsonify({
            'success': True,
            'language': lang_code,
            'translations': translations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/suggest-price', methods=['POST'])
def suggest_price():
    """Get AI-powered price suggestion for a dish"""
    try:
        dish_data = request.json
        
        # Check if API key is configured
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            # Return fallback pricing
            result = price_advisor._fallback_pricing(dish_data)
        else:
            result = price_advisor.get_price_suggestion(dish_data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/localize/<location>')
def get_localization_info(location):
    """Get localization info for a location"""
    try:
        info = translator.get_localized_content(location)
        return jsonify({
            'success': True,
            'location': location,
            'localization': info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500