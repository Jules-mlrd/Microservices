"""
Point d'entrée principal du Orders Service
"""
from flask import Flask
from .routes import bp
from .database import init_db

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'orders-service-secret-key'
    
    # Initialiser la base de données
    init_db()
    print("[Orders Service] Base de données initialisée")
    
    # Enregistrer les routes
    app.register_blueprint(bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("[Orders Service] Démarrage sur le port 8003")
    print("[Orders Service] Endpoints disponibles:")
    print("  - GET    /products (public)")
    print("  - GET    /products/{id} (public)")
    print("  - GET    /orders (protégé)")
    print("  - GET    /orders/{id} (protégé)")
    print("  - POST   /orders (protégé)")
    print("  - PUT    /orders/{id} (protégé)")
    print("  - GET    /health")
    app.run(debug=True, host='0.0.0.0', port=8003)

