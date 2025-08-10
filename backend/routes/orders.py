"""
Order management routes for Potluck app
"""

from flask import Blueprint, request, jsonify

bp = Blueprint('orders', __name__)

@bp.route('/create', methods=['POST'])
def create_order():
    """Create new order"""
    return jsonify({'message': 'Create order endpoint'})