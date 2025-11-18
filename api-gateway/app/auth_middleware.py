"""
Middleware pour la validation des tokens Authlib
"""
from authlib.jose import jwt, JoseError
import requests
from functools import wraps
from flask import request, jsonify, g

# Secret key partagée avec Auth Service
SECRET_KEY = 'votre-cle-secrete-super-secure-2024-microservices'

# URLs des services
AUTH_SERVICE_URL = 'http://localhost:8001'
USER_SERVICE_URL = 'http://localhost:8002'
ORDERS_SERVICE_URL = 'http://localhost:8003'

def verify_token(token):
    """Vérifie et décode un token JWT"""
    try:
        claims = jwt.decode(token, SECRET_KEY)
        claims.validate()
        return claims
    except JoseError:
        return None

def token_required(f):
    """Décorateur pour protéger les routes nécessitant une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Récupérer le token depuis le header Authorization
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
        
        if not token:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_TOKEN',
                    'message': 'Token manquant. Ajoutez un header Authorization: Bearer <token>.'
                }
            }), 401
        
        # Vérifier le token
        payload = verify_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Token invalide ou expiré.'
                }
            }), 401
        
        # Stocker les informations de l'utilisateur dans g pour utilisation dans les routes
        g.current_user = payload.get('sub')
        g.token_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated_function

