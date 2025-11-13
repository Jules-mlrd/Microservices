"""
Point d'entrée principal de l'API Gateway
"""
from flask import Flask, send_from_directory
import os
from .routes import bp

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__, 
                static_folder='../frontend/static',
                template_folder='../frontend/templates')
    app.config['SECRET_KEY'] = 'api-gateway-secret-key'
    
    # Enregistrer les routes API
    app.register_blueprint(bp)
    
    # Routes pour servir les pages HTML
    @app.route('/')
    def index():
        """Redirige vers la page de login"""
        from flask import redirect
        return redirect('/login.html')
    
    @app.route('/login.html')
    def login_page():
        """Page de login"""
        return send_from_directory('../frontend/templates', 'login.html')
    
    @app.route('/articles.html')
    def articles_page():
        """Page des articles"""
        return send_from_directory('../frontend/templates', 'articles.html')
    
    # Route pour servir les fichiers statiques
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Serve les fichiers statiques"""
        return send_from_directory('../frontend/static', filename)
    
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

