"""
Gestion de la base de données SQLite pour les produits et commandes
"""
import sqlite3
import time

DB_PATH = 'orders_service.db'

def init_db():
    """Initialise la base de données avec les tables products, orders et order_items"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            stock INTEGER DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table orders
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table order_items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Insérer des produits par défaut
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        default_products = [
            ("Laptop Dell XPS 13", 1299.0, "Ordinateur portable haute performance", 10),
            ("iPhone 15 Pro", 1199.0, "Smartphone Apple dernière génération", 15),
            ("Sony WH-1000XM5", 399.0, "Casque audio à réduction de bruit", 20),
            ("iPad Air", 699.0, "Tablette Apple 10.9 pouces", 12),
            ("Samsung Galaxy Watch", 349.0, "Montre connectée Samsung", 18)
        ]
        cursor.executemany('''
            INSERT INTO products (name, price, description, stock)
            VALUES (?, ?, ?, ?)
        ''', default_products)
        print("[Orders Service] Produits par défaut créés")
    
    conn.commit()
    conn.close()

def get_all_products():
    """Récupère tous les produits"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY id')
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

def get_product_by_id(product_id):
    """Récupère un produit par son ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return dict(product) if product else None

def get_orders_by_user(user_id):
    """Récupère toutes les commandes d'un utilisateur"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY date_creation DESC', (user_id,))
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders

def get_order_by_id(order_id, user_id=None):
    """Récupère une commande par son ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute('SELECT * FROM orders WHERE id = ? AND user_id = ?', (order_id, user_id))
    else:
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    
    order = cursor.fetchone()
    
    if order:
        order_dict = dict(order)
        # Récupérer les items de la commande
        cursor.execute('''
            SELECT oi.*, p.name as product_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order_id,))
        items = [dict(row) for row in cursor.fetchall()]
        order_dict['items'] = items
    
    conn.close()
    return dict(order) if order else None

def create_order(user_id, items):
    """Crée une nouvelle commande"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Calculer le total
        total = 0
        for item in items:
            product = get_product_by_id(item['product_id'])
            if not product:
                conn.close()
                return False, None, f"Produit {item['product_id']} non trouvé"
            if product['stock'] < item['quantity']:
                conn.close()
                return False, None, f"Stock insuffisant pour {product['name']}"
            total += product['price'] * item['quantity']
        
        # Créer la commande
        cursor.execute('''
            INSERT INTO orders (user_id, total, status)
            VALUES (?, ?, ?)
        ''', (user_id, total, 'pending'))
        order_id = cursor.lastrowid
        
        # Créer les items de commande
        for item in items:
            product = get_product_by_id(item['product_id'])
            cursor.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (order_id, item['product_id'], item['quantity'], product['price']))
            
            # Mettre à jour le stock
            cursor.execute('''
                UPDATE products SET stock = stock - ? WHERE id = ?
            ''', (item['quantity'], item['product_id']))
        
        conn.commit()
        conn.close()
        return True, order_id, None
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, None, f"Erreur: {str(e)}"

def update_order_status(order_id, status, user_id=None):
    """Met à jour le statut d'une commande"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute('''
            UPDATE orders SET status = ? WHERE id = ? AND user_id = ?
        ''', (status, order_id, user_id))
    else:
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

