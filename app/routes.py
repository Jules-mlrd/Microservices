"""
Contient toutes les routes web et API de l'application
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app, g
from app import get_redis
from app.database import (
    verify_user, 
    get_all_users, 
    add_user, 
    delete_user,
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_user_tokens
)
import json
import time
import random
import pybreaker
from datetime import datetime, timedelta
from functools import wraps
import jwt  # type: ignore

bp = Blueprint('main', __name__)

# Base de données simple des articles (normalement ce serait dans une vraie DB)
ARTICLES = [
    {"id": 1, "nom": "Laptop Dell XPS 13", "prix": "1299€", "description": "Ordinateur portable haute performance"},
    {"id": 2, "nom": "iPhone 15 Pro", "prix": "1199€", "description": "Smartphone Apple dernière génération"},
    {"id": 3, "nom": "Sony WH-1000XM5", "prix": "399€", "description": "Casque audio à réduction de bruit"},
    {"id": 4, "nom": "iPad Air", "prix": "699€", "description": "Tablette Apple 10.9 pouces"},
    {"id": 5, "nom": "Samsung Galaxy Watch", "prix": "349€", "description": "Montre connectée Samsung"}
]

# Base de données des utilisateurs avec leurs informations
USERS_DATA = {
    "admin": {
        "password": "admin",
        "email": "admin@example.com",
        "commandes": []
    }
}

# Dictionnaire simplifié pour compatibilité
USERS = {username: data["password"] for username, data in USERS_DATA.items()}

# ========== Circuit Breaker pour la banque ==========
# Configure le circuit breaker avec pybreaker
bank_breaker = pybreaker.CircuitBreaker(
    fail_max=3,  # Nombre d'échecs avant ouverture
    reset_timeout=60  # Durée en secondes avant réessai
)

@bank_breaker
def call_bank_api(amount, transaction_id):
    """
    Simule un appel à une API bancaire externe
    Mode SUCCESS - Les paiements réussissent toujours
    """
    time.sleep(0.5)
    
    # Retourne un succès
    return {
        "success": True,
        "transaction_id": transaction_id,
        "amount": amount,
        "status": "completed"
    }

def is_logged_in():
    """Vérifie si l'utilisateur est connecté via Redis"""
    redis_client = get_redis()
    if redis_client and 'username' in session:
        username = session['username']
        # Vérifier si la session existe dans Redis
        session_key = f"session:{username}"
        return redis_client.exists(session_key)
    return False

def get_cart():
    """Récupère le panier de l'utilisateur depuis Redis"""
    if not is_logged_in():
        return []
    
    redis_client = get_redis()
    if redis_client and 'username' in session:
        cart_key = f"cart:{session['username']}"
        cart_data = redis_client.get(cart_key)
        if cart_data:
            return json.loads(cart_data)
    return []

def save_cart(cart):
    """Sauvegarde le panier dans Redis"""
    if not is_logged_in():
        return False
    
    redis_client = get_redis()
    if redis_client and 'username' in session:
        cart_key = f"cart:{session['username']}"
        # Stocker pour 24h
        redis_client.setex(cart_key, 86400, json.dumps(cart))
        return True
    return False

def get_cart_count():
    """Retourne le nombre d'articles dans le panier"""
    cart = get_cart()
    return sum(item.get('quantity', 1) for item in cart)


def generate_jwt(username):
    """Génère un token JWT valable une heure pour l'utilisateur donné."""
    current_time = int(time.time())
    payload = {
        'sub': username,
        'iat': current_time,
        'exp': current_time + 3600  # Date actuelle + 3600 secondes
    }
    secret = current_app.config.get('SECRET_KEY', 'change-me')
    return jwt.encode(payload, secret, algorithm='HS256')


def generate_token_pair(username):
    """
    Génère une paire de tokens (access + refresh)
    Retourne: (access_token, refresh_token, expires_at)
    """
    # Générer l'access token (court terme)
    access_token = generate_jwt(username)
    
    # Générer le refresh token (long terme) - 30 jours
    refresh_token, expires_at = create_refresh_token(username, expiration_days=30)
    
    return access_token, refresh_token, expires_at


def token_required(view_func):
    """
    Décorateur pour protéger les routes avec un JWT.
    Vérifie la présence du header Authorization Bearer et valide le token.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = None

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
        else:
            token = request.args.get('token')

        if not token:
            return jsonify({
                'success': False,
                'message': 'Token manquant. Ajoutez un header Authorization: Bearer <token>.'
            }), 401

        try:
            secret = current_app.config.get('SECRET_KEY', 'change-me')
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            g.current_user = payload.get('sub')
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expiré. Veuillez vous authentifier à nouveau.'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Token invalide. Vérifiez votre clé ou reconnectez-vous.'
            }), 401

        return view_func(*args, **kwargs)
    return wrapper

@bp.route('/')
def index():
    """Page d'accueil - redirige vers login ou articles"""
    if is_logged_in():
        return redirect(url_for('main.articles'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    # Si déjà connecté, rediriger vers articles
    if is_logged_in():
        return redirect(url_for('main.articles'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"[LOGIN] Tentative de connexion pour l'utilisateur: '{username}'")
        
        if not username or not password:
            return render_template('login.html', error="Veuillez remplir tous les champs")
        
        # Vérifier les identifiants dans SQLite
        if verify_user(username, password):
            # Stocker la session dans Redis
            redis_client = get_redis()
            if redis_client:
                session_key = f"session:{username}"
                session_data = {
                    'username': username,
                    'logged_in': 'true'
                }
                # Stocker pour 1 heure (3600 secondes)
                redis_client.setex(session_key, 3600, json.dumps(session_data))
            
            # Stocker dans la session Flask
            session['username'] = username
            
            return redirect(url_for('main.articles'))
        else:
            print(f"[ERREUR] Echec de la connexion pour l'utilisateur: '{username}'")
            return render_template('login.html', error="Identifiants incorrects")
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Déconnexion"""
    if 'username' in session:
        username = session['username']
        redis_client = get_redis()
        if redis_client:
            session_key = f"session:{username}"
            redis_client.delete(session_key)
        session.pop('username', None)
    return redirect(url_for('main.login'))

@bp.route('/articles')
def articles():
    """Page listant tous les articles"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    username = session.get('username', 'Invité')
    cart_count = get_cart_count()
    
    # Récupérer et supprimer le message d'erreur de paiement s'il existe
    payment_error = session.pop('payment_error', None)
    
    return render_template('articles.html', 
                         articles=ARTICLES, 
                         username=username, 
                         cart_count=cart_count,
                         payment_error=payment_error)

@bp.route('/form/<int:article_id>')
def form(article_id):
    """Achat direct d'un article - redirige vers la page bancaire"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    # Trouver l'article
    article = next((a for a in ARTICLES if a['id'] == article_id), None)
    if not article:
        return "Article non trouvé", 404
    
    # Extraire le prix numérique
    prix_str = article['prix'].replace('€', '').strip()
    prix_num = int(prix_str)
    
    # Stocker l'article acheté et le montant dans la session
    session['last_purchase'] = article['nom']
    session['payment_amount'] = prix_num
    
    # Rediriger directement vers la page bancaire
    return redirect(url_for('main.bank'))

@bp.route('/bank')
def bank():
    """Fausse page bancaire avec chargement de 15 secondes - toujours en échec"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    # Récupérer le montant total depuis la session
    total = session.get('payment_amount', 0)
    
    # Générer un ID de transaction unique
    transaction_id = f"TRX{random.randint(100000, 999999)}"
    
    # Appeler l'API bancaire via le circuit breaker
    try:
        bank_response = call_bank_api(total, transaction_id)
        print(f"✅ Appel bancaire réussi: {bank_response}")
    except pybreaker.CircuitBreakerError:
        print("⚠️ Circuit breaker ouvert - Trop d'erreurs bancaires")
        transaction_id += "-RETRY"
    except Exception as e:
        print(f"❌ Erreur bancaire: {e}")
        transaction_id += "-ERROR"
    
    # URL de succès (paiement réussi)
    success_url = url_for('main.success')
    
    return render_template('bank.html', 
                         total=total, 
                         transaction_id=transaction_id,
                         error_url=success_url)

@bp.route('/payment-failed')
def payment_failed():
    """Gère l'échec du paiement et redirige vers la page précédente"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    # Stocker un message d'erreur dans la session
    session['payment_error'] = "Erreur de paiement : Transaction refusée par la banque. Veuillez réessayer."
    
    # Rediriger vers la page des articles
    return redirect(url_for('main.articles'))

@bp.route('/success')
def success():
    """Page de confirmation d'achat"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    article_name = session.get('last_purchase', 'un article')
    cart_count = get_cart_count()
    return render_template('success.html', article_name=article_name, cart_count=cart_count)

# ========== GESTION DES UTILISATEURS (SQLite) ==========

@bp.route('/admin/users')
def admin_users():
    """Page de gestion des utilisateurs (SQLite)"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    username = session.get('username', 'Invité')
    users = get_all_users()
    message = session.pop('admin_message', None)
    
    return render_template('admin_users.html', 
                         username=username, 
                         users=users,
                         message=message)

@bp.route('/admin/users/add', methods=['POST'])
def add_user_admin():
    """Ajoute un nouvel utilisateur dans SQLite"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email', '')
    
    success, message = add_user(username, password, email)
    session['admin_message'] = message
    
    return redirect(url_for('main.admin_users'))

@bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user_admin(user_id):
    """Supprime un utilisateur de SQLite"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    success, message = delete_user(user_id)
    session['admin_message'] = message
    
    return redirect(url_for('main.admin_users'))

# ========== PANIER ==========

@bp.route('/cart')
def cart():
    """Page du panier"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    cart_items = get_cart()
    username = session.get('username', 'Invité')
    cart_count = get_cart_count()
    
    # Calculer le total
    total = 0
    for item in cart_items:
        # Extraire le prix numérique (enlever le € et convertir)
        prix_str = item['prix'].replace('€', '').strip()
        prix_num = int(prix_str)
        total += prix_num * item.get('quantity', 1)
    
    return render_template('cart.html', cart_items=cart_items, username=username, 
                         cart_count=cart_count, total=total)

@bp.route('/cart/add/<int:article_id>', methods=['POST'])
def add_to_cart(article_id):
    """Ajouter un article au panier"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    # Trouver l'article
    article = next((a for a in ARTICLES if a['id'] == article_id), None)
    if not article:
        return "Article non trouvé", 404
    
    # Récupérer le panier actuel
    cart = get_cart()
    
    # Vérifier si l'article est déjà dans le panier
    found = False
    for item in cart:
        if item['id'] == article_id:
            item['quantity'] = item.get('quantity', 1) + 1
            found = True
            break
    
    # Si pas trouvé, ajouter un nouvel item
    if not found:
        cart.append({
            'id': article['id'],
            'nom': article['nom'],
            'prix': article['prix'],
            'description': article['description'],
            'quantity': 1
        })
    
    # Sauvegarder le panier
    save_cart(cart)
    
    return redirect(url_for('main.articles'))

@bp.route('/cart/remove/<int:article_id>', methods=['POST'])
def remove_from_cart(article_id):
    """Retirer un article du panier"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    cart = get_cart()
    cart = [item for item in cart if item['id'] != article_id]
    save_cart(cart)
    
    return redirect(url_for('main.cart'))

@bp.route('/cart/update/<int:article_id>', methods=['POST'])
def update_cart_quantity(article_id):
    """Mettre à jour la quantité d'un article dans le panier"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    quantity = int(request.form.get('quantity', 1))
    
    if quantity <= 0:
        return remove_from_cart(article_id)
    
    cart = get_cart()
    for item in cart:
        if item['id'] == article_id:
            item['quantity'] = quantity
            break
    
    save_cart(cart)
    return redirect(url_for('main.cart'))

@bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    """Vider le panier"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    save_cart([])
    return redirect(url_for('main.cart'))

@bp.route('/cart/checkout')
def checkout():
    """Passer commande depuis le panier - redirige vers la page bancaire"""
    if not is_logged_in():
        return redirect(url_for('main.login'))
    
    cart = get_cart()
    if not cart:
        return redirect(url_for('main.cart'))
    
    # Calculer le total du panier
    total = 0
    for item in cart:
        prix_str = item['prix'].replace('€', '').strip()
        prix_num = int(prix_str)
        total += prix_num * item.get('quantity', 1)
    
    # Compter les articles
    total_items = sum(item.get('quantity', 1) for item in cart)
    session['last_purchase'] = f"{total_items} article(s)"
    session['payment_amount'] = total
    
    # Vider le panier
    save_cart([])
    
    # Rediriger directement vers la page bancaire
    return redirect(url_for('main.bank'))

# ========== API JSON ==========

@bp.route('/api/articles', methods=['GET'])
def api_articles():
    """API: Retourne la liste des articles en JSON"""
    return jsonify({
        'success': True,
        'count': len(ARTICLES),
        'articles': ARTICLES
    })

@bp.route('/api/login', methods=['POST'])
def api_login():
    """API: Vérifie l'utilisateur et stocke la session en cache Redis"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': 'Username et password requis'
        }), 400
    
    username = data['username']
    password = data['password']
    
    # Vérifier les identifiants dans SQLite (avec hash)
    if verify_user(username, password):
        # Stocker la session dans Redis
        redis_client = get_redis()
        if redis_client:
            session_key = f"session:{username}"
            session_data = {
                'username': username,
                'logged_in': 'true'
            }
            redis_client.setex(session_key, 3600, json.dumps(session_data))
        
        return jsonify({
            'success': True,
            'message': 'Connexion réussie',
            'username': username
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Identifiants incorrects'
        }), 401


@bp.route('/auth/login', methods=['POST'])
def auth_login():
    """API: authentifie l'utilisateur et renvoie une paire de tokens."""
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            'success': False,
            'message': 'Les champs username et password sont requis.'
        }), 400

    if not verify_user(username, password):
        return jsonify({
            'success': False,
            'message': 'Identifiants incorrects.'
        }), 401

    # Générer la paire de tokens
    access_token, refresh_token, refresh_expires_at = generate_token_pair(username)
    
    return jsonify({
        'success': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': 3600,  # Access token expire dans 1h
        'refresh_expires_at': refresh_expires_at  # Timestamp d'expiration du refresh token
    })


@bp.route('/auth/profile', methods=['GET'])
@token_required
def auth_profile():
    """Route protégée par JWT, renvoie l'utilisateur courant."""
    return jsonify({
        'success': True,
        'message': 'Accès autorisé.',
        'user': g.get('current_user')
    })


@bp.route('/auth/refresh', methods=['POST'])
def auth_refresh():
    """
    Endpoint pour renouveler l'access token avec un refresh token.
    """
    data = request.get_json(silent=True) or {}
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({
            'success': False,
            'message': 'Le refresh_token est requis.'
        }), 400

    # Vérifier le refresh token
    username = verify_refresh_token(refresh_token)
    
    if not username:
        return jsonify({
            'success': False,
            'message': 'Refresh token invalide ou expiré.'
        }), 401

    # Révoquer l'ancien refresh token (rotation)
    revoke_refresh_token(refresh_token)
    
    # Générer une nouvelle paire de tokens
    access_token, new_refresh_token, refresh_expires_at = generate_token_pair(username)
    
    return jsonify({
        'success': True,
        'access_token': access_token,
        'refresh_token': new_refresh_token,
        'token_type': 'Bearer',
        'expires_in': 3600,
        'refresh_expires_at': refresh_expires_at
    })


@bp.route('/auth/logout', methods=['POST'])
@token_required
def auth_logout():
    """
    Déconnexion: révoque le refresh token actuel.
    """
    data = request.get_json(silent=True) or {}
    refresh_token = data.get('refresh_token')
    
    if refresh_token:
        revoke_refresh_token(refresh_token)
    
    return jsonify({
        'success': True,
        'message': 'Déconnexion réussie.'
    })

@bp.route('/api/session/<username>', methods=['GET'])
def api_check_session(username):
    """API: Vérifie si une session existe dans Redis"""
    redis_client = get_redis()
    if redis_client:
        session_key = f"session:{username}"
        if redis_client.exists(session_key):
            session_data = redis_client.get(session_key)
            return jsonify({
                'success': True,
                'session_exists': True,
                'data': json.loads(session_data)
            })
    
    return jsonify({
        'success': True,
        'session_exists': False
    })

@bp.route('/api/users', methods=['GET'])
def api_users():
    """API: Retourne les informations de tous les utilisateurs en JSON"""
    # Ne pas exposer les mots de passe
    users_safe = {}
    for username, data in USERS_DATA.items():
        users_safe[username] = {
            "email": data["email"],
            "nombre_commandes": len(data["commandes"]),
            "commandes": data["commandes"]
        }
    
    return jsonify({
        'success': True,
        'count': len(users_safe),
        'users': users_safe
    })

