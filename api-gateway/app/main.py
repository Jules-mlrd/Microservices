"""
Point d'entrée principal de l'API Gateway
"""
from flask import Flask
from .routes import bp

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'api-gateway-secret-key'
    
    # Enregistrer les routes
    app.register_blueprint(bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("[API Gateway] Démarrage sur le port 8000")
    print("[API Gateway] Point d'entrée unique pour tous les microservices")
    print("[API Gateway] Routes disponibles:")
    print("  - POST /auth/login")
    print("  - POST /auth/refresh")
    print("  - GET  /users (protégé)")
    print("  - GET  /users/profile (protégé)")
    print("  - GET  /products (public)")
    print("  - GET  /orders (protégé)")
    app.run(debug=True, host='0.0.0.0', port=8000)

