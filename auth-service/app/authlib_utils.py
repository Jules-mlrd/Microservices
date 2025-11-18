"""
Utilitaires pour la gestion des tokens Authlib
"""
import time
from authlib.jose import jwt, JoseError

SECRET_KEY = 'votre-cle-secrete-super-secure-2024-microservices'
JWT_HEADER = {'alg': 'HS256', 'typ': 'JWT'}

def generate_access_token(username):
    """Génère un access token JWT valable une heure"""
    current_time = int(time.time())
    payload = {
        'sub': username,
        'iat': current_time,
        'exp': current_time + 3600,  # 1 heure
        'type': 'access'
    }
    token = jwt.encode(JWT_HEADER, payload, SECRET_KEY)
    return token.decode('utf-8') if isinstance(token, bytes) else token

def verify_token(token):
    """Vérifie et décode un token JWT"""
    try:
        claims = jwt.decode(token, SECRET_KEY)
        claims.validate()
        return claims
    except JoseError:
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

