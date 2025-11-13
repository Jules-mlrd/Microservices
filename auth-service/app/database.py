"""
Gestion de la base de données SQLite pour l'authentification
"""
import sqlite3
import secrets
import time
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = 'auth_service.db'

def init_db():
    """Initialise la base de données avec les tables users et refresh_tokens"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Créer la table users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Créer la table refresh_tokens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            expires_at INTEGER NOT NULL,
            created_at INTEGER NOT NULL,
            revoked BOOLEAN DEFAULT 0
        )
    ''')
    
    # Index pour améliorer les performances
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_token ON refresh_tokens(token)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON refresh_tokens(username)')
    
    # Créer l'utilisateur admin par défaut
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        password_hash = generate_password_hash('admin')
        cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                     ('admin', password_hash, 'admin@example.com'))
        print("[Auth Service] Utilisateur 'admin' créé avec le mot de passe 'admin'")
    
    conn.commit()
    conn.close()

def verify_user(username, password):
    """Vérifie les identifiants d'un utilisateur"""
    if not username or not password:
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user is None:
        return False
    
    return check_password_hash(user[0], password)

def create_refresh_token(username, expiration_days=30):
    """Crée un refresh token pour un utilisateur"""
    token = secrets.token_urlsafe(64)
    current_time = int(time.time())
    expires_at = current_time + (expiration_days * 24 * 3600)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO refresh_tokens (token, username, expires_at, created_at)
        VALUES (?, ?, ?, ?)
    ''', (token, username, expires_at, current_time))
    conn.commit()
    conn.close()
    
    return token, expires_at

def verify_refresh_token(token):
    """Vérifie si un refresh token est valide"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    current_time = int(time.time())
    
    cursor.execute('''
        SELECT username, expires_at, revoked
        FROM refresh_tokens
        WHERE token = ? AND revoked = 0
    ''', (token,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    username, expires_at, revoked = result
    
    if current_time > expires_at:
        return None
    
    return username

def revoke_refresh_token(token):
    """Révoque un refresh token"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE refresh_tokens SET revoked = 1 WHERE token = ?', (token,))
    conn.commit()
    conn.close()

