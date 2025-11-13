"""
Gestion de la base de données SQLite pour les profils utilisateurs
"""
import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = 'user_service.db'

def init_db():
    """Initialise la base de données avec la table users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            address TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Créer l'utilisateur admin par défaut
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (username, email, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', 'Admin', 'User'))
        print("[User Service] Utilisateur 'admin' créé")
    
    conn.commit()
    conn.close()

def get_all_users():
    """Récupère tous les utilisateurs"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY id')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def get_user_by_id(user_id):
    """Récupère un utilisateur par son ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_username(username):
    """Récupère un utilisateur par son username"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(username, email=None, first_name=None, last_name=None, phone=None, address=None):
    """Crée un nouvel utilisateur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, email, first_name, last_name, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, email, first_name, last_name, phone, address))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return True, user_id, None
    except sqlite3.IntegrityError:
        conn.close()
        return False, None, "Cet utilisateur existe déjà"
    except Exception as e:
        conn.close()
        return False, None, f"Erreur: {str(e)}"

def update_user(user_id, email=None, first_name=None, last_name=None, phone=None, address=None):
    """Met à jour un utilisateur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if email is not None:
        updates.append('email = ?')
        params.append(email)
    if first_name is not None:
        updates.append('first_name = ?')
        params.append(first_name)
    if last_name is not None:
        updates.append('last_name = ?')
        params.append(last_name)
    if phone is not None:
        updates.append('phone = ?')
        params.append(phone)
    if address is not None:
        updates.append('address = ?')
        params.append(address)
    
    if not updates:
        conn.close()
        return False, "Aucune donnée à mettre à jour"
    
    updates.append('date_update = CURRENT_TIMESTAMP')
    params.append(user_id)
    
    cursor.execute(f'UPDATE users SET {", ".join(updates)} WHERE id = ?', params)
    conn.commit()
    conn.close()
    return True, None

def delete_user(user_id):
    """Supprime un utilisateur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

