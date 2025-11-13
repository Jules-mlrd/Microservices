"""
Point d'entrée principal du Auth Service
"""
from flask import Flask
from .routes import bp
from .database import init_db

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'auth-service-secret-key'
    
    # Initialiser la base de données
    init_db()
    print("[Auth Service] Base de données initialisée")
    
    # Enregistrer les routes
    app.register_blueprint(bp, url_prefix='/auth')
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("[Auth Service] Démarrage sur le port 8001")
    print("[Auth Service] Endpoints disponibles:")
    print("  - POST /auth/login")
    print("  - POST /auth/refresh")
    print("  - POST /auth/verify")
    print("  - POST /auth/logout")
    print("  - GET  /auth/health")
    app.run(debug=True, host='0.0.0.0', port=8001)

