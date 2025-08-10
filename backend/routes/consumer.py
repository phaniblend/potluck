"""
Consumer routes for Potluck app
"""

from flask import Blueprint, request, jsonify

bp = Blueprint('consumer', __name__)

@bp.route('/profile')
def get_profile():
    """Get consumer profile"""
    return jsonify({'message': 'Consumer profile endpoint'})