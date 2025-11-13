"""
Création et configuration de l'application Flask avec Redis
"""
from flask import Flask
import redis
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Initialisation de la connexion Redis
redis_client = None

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration de la clé secrète pour les sessions
    app.config['SECRET_KEY'] = 'votre-cle-secrete-super-secure-2024'
    
    # Configuration Redis
    app.config['REDIS_HOST'] = os.getenv('REDIS_HOST', 'localhost')
    app.config['REDIS_PORT'] = int(os.getenv('REDIS_PORT', 6379))
    app.config['REDIS_PASSWORD'] = os.getenv('REDIS_PASSWORD', None)
    app.config['REDIS_USERNAME'] = os.getenv('REDIS_USERNAME', None)
    app.config['REDIS_DB'] = int(os.getenv('REDIS_DB', 0))
    
    # Initialisation de Redis
    global redis_client
    try:
        # Configuration pour Redis Cloud ou Redis local
        redis_config = {
            'host': app.config['REDIS_HOST'],
            'port': app.config['REDIS_PORT'],
            'db': app.config['REDIS_DB'],
            'decode_responses': True,  # Pour récupérer des strings au lieu de bytes
            'socket_connect_timeout': 5,
            'socket_timeout': 5
        }
        
        # Ajouter l'authentification si fournie (pour Redis Cloud)
        if app.config['REDIS_PASSWORD']:
            redis_config['password'] = app.config['REDIS_PASSWORD']
        
        if app.config['REDIS_USERNAME']:
            redis_config['username'] = app.config['REDIS_USERNAME']
        
        redis_client = redis.Redis(**redis_config)
        
        # Test de connexion
        redis_client.ping()
        print(f"[OK] Connexion a Redis reussie! (Host: {app.config['REDIS_HOST']})")
    except redis.ConnectionError as e:
        print(f"[ATTENTION] Impossible de se connecter a Redis: {e}")
        print("Verifiez vos credentials dans le fichier .env")
        redis_client = None
    except Exception as e:
        print(f"[ERREUR] Erreur Redis: {e}")
        redis_client = None
    
    # Initialiser la base de données SQLite
    from app.database import init_db
    init_db()
    print("[OK] Base de donnees SQLite initialisee")
    
    # Enregistrer les routes
    with app.app_context():
        from app import routes
        app.register_blueprint(routes.bp)
    
    return app

def get_redis():
    """Retourne le client Redis"""
    return redis_client

