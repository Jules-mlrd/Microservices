"""
Routes pour le User Service
"""
from flask import Blueprint, request, jsonify
from .database import (
    get_all_users, get_user_by_id, get_user_by_username,
    create_user, update_user, delete_user
)

bp = Blueprint('user', __name__)

def get_current_user_id():
    """Récupère l'ID de l'utilisateur depuis les headers"""
    return request.headers.get('X-User-Id')

@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'user-service'}), 200

@bp.route('/users', methods=['GET'])
def list_users():
    """Liste tous les utilisateurs"""
    users = get_all_users()
    return jsonify({
        'success': True,
        'data': users,
        'count': len(users)
    }), 200

@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Récupère un utilisateur par son ID"""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': {
                'code': 'USER_NOT_FOUND',
                'message': f'Utilisateur avec ID {user_id} non trouvé.'
            }
        }), 404
    
    return jsonify({
        'success': True,
        'data': user
    }), 200

@bp.route('/users', methods=['POST'])
def create_user_route():
    """Crée un nouvel utilisateur"""
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    
    if not username:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_USERNAME',
                'message': 'Le champ username est requis.'
            }
        }), 400
    
    success, user_id, error = create_user(
        username=username,
        email=data.get('email'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    
    if not success:
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATION_FAILED',
                'message': error
            }
        }), 400
    
    user = get_user_by_id(user_id)
    return jsonify({
        'success': True,
        'data': user,
        'message': 'Utilisateur créé avec succès.'
    }), 201

@bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user_route(user_id):
    """Met à jour un utilisateur"""
    data = request.get_json(silent=True) or {}
    
    success, error = update_user(
        user_id=user_id,
        email=data.get('email'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    
    if not success:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_FAILED',
                'message': error
            }
        }), 400
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': {
                'code': 'USER_NOT_FOUND',
                'message': f'Utilisateur avec ID {user_id} non trouvé.'
            }
        }), 404
    
    return jsonify({
        'success': True,
        'data': user,
        'message': 'Utilisateur mis à jour avec succès.'
    }), 200

@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user_route(user_id):
    """Supprime un utilisateur"""
    deleted = delete_user(user_id)
    
    if not deleted:
        return jsonify({
            'success': False,
            'error': {
                'code': 'USER_NOT_FOUND',
                'message': f'Utilisateur avec ID {user_id} non trouvé.'
            }
        }), 404
    
    return jsonify({
        'success': True,
        'message': 'Utilisateur supprimé avec succès.'
    }), 200

@bp.route('/users/profile', methods=['GET'])
def get_profile():
    """Récupère le profil de l'utilisateur connecté"""
    username = get_current_user_id()
    
    if not username:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_USER',
                'message': 'Utilisateur non identifié.'
            }
        }), 401
    
    user = get_user_by_username(username)
    if not user:
        return jsonify({
            'success': False,
            'error': {
                'code': 'USER_NOT_FOUND',
                'message': f'Profil pour {username} non trouvé.'
            }
        }), 404
    
    return jsonify({
        'success': True,
        'data': user
    }), 200

