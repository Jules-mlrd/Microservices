"""
Routes pour le Orders Service
"""
from flask import Blueprint, request, jsonify
from .database import (
    get_all_products, get_product_by_id,
    get_orders_by_user, get_order_by_id,
    create_order, update_order_status
)

bp = Blueprint('orders', __name__)

def get_current_user_id():
    """Récupère l'ID de l'utilisateur depuis les headers"""
    return request.headers.get('X-User-Id')

@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'orders-service'}), 200

# ========== Routes Products (public) ==========
@bp.route('/products', methods=['GET'])
def list_products():
    """Liste tous les produits"""
    products = get_all_products()
    return jsonify({
        'success': True,
        'data': products,
        'count': len(products)
    }), 200

@bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Récupère un produit par son ID"""
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PRODUCT_NOT_FOUND',
                'message': f'Produit avec ID {product_id} non trouvé.'
            }
        }), 404
    
    return jsonify({
        'success': True,
        'data': product
    }), 200

# ========== Routes Orders (protégées) ==========
@bp.route('/orders', methods=['GET'])
def list_orders():
    """Liste toutes les commandes de l'utilisateur connecté"""
    user_id = get_current_user_id()
    
    if not user_id:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_USER',
                'message': 'Utilisateur non identifié.'
            }
        }), 401
    
    orders = get_orders_by_user(user_id)
    return jsonify({
        'success': True,
        'data': orders,
        'count': len(orders)
    }), 200

@bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Récupère une commande par son ID"""
    user_id = get_current_user_id()
    
    if not user_id:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_USER',
                'message': 'Utilisateur non identifié.'
            }
        }), 401
    
    order = get_order_by_id(order_id, user_id)
    if not order:
        return jsonify({
            'success': False,
            'error': {
                'code': 'ORDER_NOT_FOUND',
                'message': f'Commande avec ID {order_id} non trouvée.'
            }
        }), 404
    
    return jsonify({
        'success': True,
        'data': order
    }), 200

@bp.route('/orders', methods=['POST'])
def create_order_route():
    """Crée une nouvelle commande"""
    user_id = get_current_user_id()
    
    if not user_id:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_USER',
                'message': 'Utilisateur non identifié.'
            }
        }), 401
    
    data = request.get_json(silent=True) or {}
    items = data.get('items', [])
    
    if not items:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_ITEMS',
                'message': 'La liste des items est requise.'
            }
        }), 400
    
    success, order_id, error = create_order(user_id, items)
    
    if not success:
        return jsonify({
            'success': False,
            'error': {
                'code': 'ORDER_CREATION_FAILED',
                'message': error
            }
        }), 400
    
    order = get_order_by_id(order_id, user_id)
    return jsonify({
        'success': True,
        'data': order,
        'message': 'Commande créée avec succès.'
    }), 201

@bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order_route(order_id):
    """Met à jour le statut d'une commande"""
    user_id = get_current_user_id()
    
    if not user_id:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_USER',
                'message': 'Utilisateur non identifié.'
            }
        }), 401
    
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    
    if not status:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_STATUS',
                'message': 'Le statut est requis.'
            }
        }), 400
    
    updated = update_order_status(order_id, status, user_id)
    
    if not updated:
        return jsonify({
            'success': False,
            'error': {
                'code': 'ORDER_NOT_FOUND',
                'message': f'Commande avec ID {order_id} non trouvée.'
            }
        }), 404
    
    order = get_order_by_id(order_id, user_id)
    return jsonify({
        'success': True,
        'data': order,
        'message': 'Commande mise à jour avec succès.'
    }), 200

