"""
Point d'entrée principal du User Service
"""
from flask import Flask
from .routes import bp
from .database import init_db

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'user-service-secret-key'
    
    # Initialiser la base de données
    init_db()
    print("[User Service] Base de données initialisée")
    
    # Enregistrer les routes
    app.register_blueprint(bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("[User Service] Démarrage sur le port 8002")
    print("[User Service] Endpoints disponibles:")
    print("  - GET    /users")
    print("  - GET    /users/{id}")
    print("  - POST   /users")
    print("  - PUT    /users/{id}")
    print("  - DELETE /users/{id}")
    print("  - GET    /users/profile")
    print("  - GET    /health")
    app.run(debug=True, host='0.0.0.0', port=8002)

