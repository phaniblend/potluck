"""
Delivery agent routes for Potluck app
"""

from flask import Blueprint, request, jsonify

bp = Blueprint('delivery', __name__)

@bp.route('/available-jobs')
def available_jobs():
    """Get available delivery jobs"""
    return jsonify({'message': 'Delivery jobs endpoint'})