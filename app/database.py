"""
Gestion de la base de données SQLite pour les utilisateurs
"""
import sqlite3
import os
import secrets
import time
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = 'users.db'

def init_db():
    """Initialise la base de données avec les tables users et refresh_tokens"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Créer la table users si elle n'existe pas
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
            revoked BOOLEAN DEFAULT 0,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    
    # Index pour améliorer les performances
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_token ON refresh_tokens(token)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON refresh_tokens(username)')
    
    # Supprimer les anciens comptes de démonstration
    cursor.execute(
        'DELETE FROM users WHERE username IN (?, ?, ?, ?)',
        ('test', 'user', 'demo', 'admin')
    )
    
    # Créer l'utilisateur admin avec le mot de passe "admin"
    password_hash = generate_password_hash('admin')
    cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                 ('admin', password_hash, 'admin@example.com'))
    print("[OK] Utilisateur 'admin' cree avec le mot de passe 'admin'")
    
    conn.commit()
    conn.close()

def get_all_users():
    """Récupère tous les utilisateurs"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, date_creation FROM users ORDER BY id')
    users = cursor.fetchall()
    conn.close()
    return users

def add_user(username, password, email=''):
    """Ajoute un nouvel utilisateur avec mot de passe hashé"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Hasher le mot de passe avant de l'insérer
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                     (username, password_hash, email))
        conn.commit()
        conn.close()
        return True, "Utilisateur ajouté avec succès"
    except sqlite3.IntegrityError:
        return False, "Cet utilisateur existe déjà"
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def delete_user(user_id):
    """Supprime un utilisateur par son ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True, "Utilisateur supprimé"
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def verify_user(username, password):
    """Vérifie les identifiants d'un utilisateur en comparant le hash du mot de passe"""
    if not username or not password:
        print(f"[ERREUR] Username ou password vide")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Récupérer l'utilisateur et son mot de passe hashé
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user is None:
        print(f"[ERREUR] Utilisateur '{username}' non trouve dans la base de donnees")
        return False
    
    stored_password_hash = user[0]
    
    # Vérifier que le hash stocké est valide
    if not stored_password_hash or not isinstance(stored_password_hash, str) or len(stored_password_hash) < 10:
        print(f"[ERREUR] Hash de mot de passe invalide pour l'utilisateur '{username}'")
        return False
    
    # Utiliser check_password_hash pour vérifier le mot de passe
    # Cette fonction gère automatiquement tous les formats de hash (pbkdf2, sha256, etc.)
    try:
        result = check_password_hash(stored_password_hash, password)
        if result:
            print(f"[OK] Connexion reussie pour l'utilisateur '{username}'")
        else:
            print(f"[ERREUR] Mot de passe incorrect pour l'utilisateur '{username}'")
        return result
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la verification du mot de passe: {e}")
        # En cas d'erreur, refuser la connexion par sécurité
        return False

def create_refresh_token(username, expiration_days=30):
    """
    Crée un refresh token pour un utilisateur
    expiration_days: Durée de vie en jours (par défaut 30 jours)
    Retourne: (token, expires_at)
    """
    # Générer un token aléatoire sécurisé
    token = secrets.token_urlsafe(64)
    current_time = int(time.time())
    expires_at = current_time + (expiration_days * 24 * 3600)  # 30 jours en secondes
    
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
    """
    Vérifie si un refresh token est valide
    Retourne le username si valide, None sinon
    """
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
    
    # Vérifier si le token est expiré
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

def revoke_all_user_tokens(username):
    """Révoque tous les refresh tokens d'un utilisateur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE refresh_tokens SET revoked = 1 WHERE username = ?', (username,))
    conn.commit()
    conn.close()

def cleanup_expired_tokens():
    """Nettoie les tokens expirés de la base de données"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    current_time = int(time.time())
    cursor.execute('DELETE FROM refresh_tokens WHERE expires_at < ?', (current_time,))
    conn.commit()
    conn.close()

