"""
Translation API Routes
Provides real-time AI translation services
"""

from flask import Blueprint, request, jsonify
from utils.ai_translator import ai_translator

bp = Blueprint('translation', __name__)

@bp.route('/translate', methods=['POST'])
def translate_text():
    """Translate text to target language"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        text = data.get('text', '')
        target_language = data.get('target_language', 'en')
        source_language = data.get('source_language', 'en')
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        if not target_language:
            return jsonify({'success': False, 'error': 'No target language provided'}), 400
        
        # Translate the text
        translated_text = ai_translator.translate_text(text, target_language, source_language)
        
        return jsonify({
            'success': True,
            'translation': translated_text,
            'original_text': text,
            'source_language': source_language,
            'target_language': target_language
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/translate-batch', methods=['POST'])
def translate_batch():
    """Translate multiple texts at once"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        texts = data.get('texts', [])
        target_language = data.get('target_language', 'en')
        source_language = data.get('source_language', 'en')
        
        if not texts or not isinstance(texts, list):
            return jsonify({'success': False, 'error': 'No texts provided or invalid format'}), 400
        
        if not target_language:
            return jsonify({'success': False, 'error': 'No target language provided'}), 400
        
        # Translate the texts
        translations = ai_translator.translate_batch(texts, target_language, source_language)
        
        return jsonify({
            'success': True,
            'translations': translations,
            'source_language': source_language,
            'target_language': target_language
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """Check translation service health"""
    return jsonify({
        'success': True,
        'ai_available': ai_translator.has_api_key,
        'service': 'AI Translation Service'
    })
