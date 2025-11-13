"""
Routes pour le service d'authentification
"""
from flask import Blueprint, request, jsonify
from .database import verify_user, verify_refresh_token, revoke_refresh_token
from .jwt_utils import generate_token_pair, verify_token

bp = Blueprint('auth', __name__)

@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'auth-service'}), 200

@bp.route('/login', methods=['POST'])
def login():
    """Authentifie l'utilisateur et renvoie une paire de tokens"""
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_CREDENTIALS',
                'message': 'Les champs username et password sont requis.'
            }
        }), 400

    if not verify_user(username, password):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_CREDENTIALS',
                'message': 'Identifiants incorrects.'
            }
        }), 401

    # Générer la paire de tokens
    access_token, refresh_token, refresh_expires_at = generate_token_pair(username)
    
    return jsonify({
        'success': True,
        'data': {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_expires_at': refresh_expires_at
        }
    }), 200

@bp.route('/refresh', methods=['POST'])
def refresh():
    """Renouvelle l'access token avec un refresh token"""
    data = request.get_json(silent=True) or {}
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_TOKEN',
                'message': 'Le refresh_token est requis.'
            }
        }), 400

    # Vérifier le refresh token
    username = verify_refresh_token(refresh_token)
    
    if not username:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_TOKEN',
                'message': 'Refresh token invalide ou expiré.'
            }
        }), 401

    # Révoquer l'ancien refresh token (rotation)
    revoke_refresh_token(refresh_token)
    
    # Générer une nouvelle paire de tokens
    access_token, new_refresh_token, refresh_expires_at = generate_token_pair(username)
    
    return jsonify({
        'success': True,
        'data': {
            'access_token': access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_expires_at': refresh_expires_at
        }
    }), 200

@bp.route('/verify', methods=['POST'])
def verify():
    """Vérifie la validité d'un token"""
    data = request.get_json(silent=True) or {}
    token = data.get('token')

    if not token:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_TOKEN',
                'message': 'Le token est requis.'
            }
        }), 400

    payload = verify_token(token)
    
    if not payload:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_TOKEN',
                'message': 'Token invalide ou expiré.'
            }
        }), 401

    return jsonify({
        'success': True,
        'data': {
            'username': payload.get('sub'),
            'expires_at': payload.get('exp')
        }
    }), 200

@bp.route('/logout', methods=['POST'])
def logout():
    """Révoque un refresh token"""
    data = request.get_json(silent=True) or {}
    refresh_token = data.get('refresh_token')
    
    if refresh_token:
        revoke_refresh_token(refresh_token)
    
    return jsonify({
        'success': True,
        'message': 'Déconnexion réussie.'
    }), 200

@bp.route('/register', methods=['POST'])
def register():
    """Crée un nouvel utilisateur avec login/password"""
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')

    if not username or not password:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_CREDENTIALS',
                'message': 'Les champs username et password sont requis.'
            }
        }), 400

    from .database import create_user
    success, user_id, error = create_user(username, password, email)
    
    if not success:
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATION_FAILED',
                'message': error
            }
        }), 400

    return jsonify({
        'success': True,
        'message': 'Utilisateur créé avec succès.',
        'data': {'user_id': user_id, 'username': username}
    }), 201

