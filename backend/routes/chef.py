"""
Chef routes for Potluck app
"""

from flask import Blueprint, request, jsonify

bp = Blueprint('chef', __name__)

@bp.route('/dashboard')
def dashboard():
    """Get chef dashboard data"""
    return jsonify({'message': 'Chef dashboard endpoint'})