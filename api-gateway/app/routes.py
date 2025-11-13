"""
Routes pour l'API Gateway
"""
from flask import Blueprint, request, jsonify, g
from .auth_middleware import token_required, AUTH_SERVICE_URL, USER_SERVICE_URL, ORDERS_SERVICE_URL
from .service_client import ServiceClient

bp = Blueprint('gateway', __name__)

@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'api-gateway',
        'services': {
            'auth': AUTH_SERVICE_URL,
            'user': USER_SERVICE_URL,
            'orders': ORDERS_SERVICE_URL
        }
    }), 200

# ========== Routes Auth Service (pas de protection) ==========
@bp.route('/auth/login', methods=['POST'])
def auth_login():
    """Forward vers Auth Service - Login"""
    data = request.get_json(silent=True) or {}
    result, error, status = ServiceClient.forward_to_auth('/auth/login', 'POST', data)
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

@bp.route('/auth/refresh', methods=['POST'])
def auth_refresh():
    """Forward vers Auth Service - Refresh"""
    data = request.get_json(silent=True) or {}
    result, error, status = ServiceClient.forward_to_auth('/auth/refresh', 'POST', data)
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

@bp.route('/auth/verify', methods=['POST'])
def auth_verify():
    """Forward vers Auth Service - Verify"""
    data = request.get_json(silent=True) or {}
    result, error, status = ServiceClient.forward_to_auth('/auth/verify', 'POST', data)
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

@bp.route('/auth/logout', methods=['POST'])
@token_required
def auth_logout():
    """Forward vers Auth Service - Logout"""
    data = request.get_json(silent=True) or {}
    result, error, status = ServiceClient.forward_to_auth('/auth/logout', 'POST', data)
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

@bp.route('/auth/register', methods=['POST'])
def auth_register():
    """Forward vers Auth Service - Création d'utilisateur"""
    data = request.get_json(silent=True) or {}
    result, error, status = ServiceClient.forward_to_auth('/auth/register', 'POST', data)
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

# ========== Routes User Service (protégées) ==========
@bp.route('/users', methods=['GET', 'POST'])
@token_required
def users():
    """Forward vers User Service"""
    method = request.method
    data = request.get_json(silent=True) if method in ['POST', 'PUT'] else None
    
    # Ajouter l'utilisateur courant dans les headers
    headers = {'X-User-Id': g.current_user}
    
    result, error, status = ServiceClient.forward_to_user('/users', method, data, headers)
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

@bp.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def user_detail(user_id):
    """Forward vers User Service - Détails utilisateur"""
    method = request.method
    data = request.get_json(silent=True) if method == 'PUT' else None
    
    headers = {'X-User-Id': g.current_user}
    
    result, error, status = ServiceClient.forward_to_user(f'/users/{user_id}', method, data, headers)
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

@bp.route('/users/profile', methods=['GET'])
@token_required
def user_profile():
    """Forward vers User Service - Profil utilisateur"""
    headers = {'X-User-Id': g.current_user}
    
    result, error, status = ServiceClient.forward_to_user('/users/profile', 'GET', None, headers)
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

# ========== Routes Orders Service ==========
@bp.route('/products', methods=['GET'])
def products():
    """Forward vers Orders Service - Liste des produits (public)"""
    result, error, status = ServiceClient.forward_to_orders('/products', 'GET')
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

@bp.route('/products/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    """Forward vers Orders Service - Détails produit (public)"""
    result, error, status = ServiceClient.forward_to_orders(f'/products/{product_id}', 'GET')
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

@bp.route('/orders', methods=['GET', 'POST'])
@token_required
def orders():
    """Forward vers Orders Service - Commandes (protégé)"""
    method = request.method
    data = request.get_json(silent=True) if method == 'POST' else None
    
    headers = {'X-User-Id': g.current_user}
    
    result, error, status = ServiceClient.forward_to_orders('/orders', method, data, headers)
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

@bp.route('/orders/<int:order_id>', methods=['GET', 'PUT'])
@token_required
def order_detail(order_id):
    """Forward vers Orders Service - Détails commande (protégé)"""
    method = request.method
    data = request.get_json(silent=True) if method == 'PUT' else None
    
    headers = {'X-User-Id': g.current_user}
    
    result, error, status = ServiceClient.forward_to_orders(f'/orders/{order_id}', method, data, headers)
    
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify(result), status

