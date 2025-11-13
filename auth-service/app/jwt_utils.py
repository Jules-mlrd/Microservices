"""
Utilitaires pour la gestion des tokens JWT
"""
import jwt
import time
from flask import current_app

SECRET_KEY = 'votre-cle-secrete-super-secure-2024-microservices'

def generate_access_token(username):
    """Génère un access token JWT valable une heure"""
    current_time = int(time.time())
    payload = {
        'sub': username,
        'iat': current_time,
        'exp': current_time + 3600,  # 1 heure
        'type': 'access'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Vérifie et décode un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_token_pair(username):
    """
    Génère une paire de tokens (access + refresh)
    Retourne: (access_token, refresh_token, expires_at)
    """
    from .database import create_refresh_token
    
    access_token = generate_access_token(username)
    refresh_token, expires_at = create_refresh_token(username, expiration_days=30)
    
    return access_token, refresh_token, expires_at

