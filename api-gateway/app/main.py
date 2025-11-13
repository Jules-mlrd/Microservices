"""
Point d'entrée principal de l'API Gateway
"""
from flask import Flask, send_from_directory, render_template
import os
from .routes import bp

def create_app():
    """Factory pour créer l'application Flask"""
    # Chemin absolu vers le dossier frontend
    # Depuis api-gateway/app/main.py -> api-gateway -> racine du projet
    current_file = os.path.abspath(__file__)  # api-gateway/app/main.py
    app_dir = os.path.dirname(current_file)    # api-gateway/app
    gateway_dir = os.path.dirname(app_dir)     # api-gateway
    base_dir = os.path.dirname(gateway_dir)    # racine du projet (Exo_Flask)
    frontend_static = os.path.join(base_dir, 'frontend', 'static')
    frontend_templates = os.path.join(base_dir, 'frontend', 'templates')
    
    # Debug: afficher les chemins
    print(f"[API Gateway] Base directory: {base_dir}")
    print(f"[API Gateway] Frontend static: {frontend_static}")
    print(f"[API Gateway] Frontend templates: {frontend_templates}")
    print(f"[API Gateway] Login.html exists: {os.path.exists(os.path.join(frontend_templates, 'login.html'))}")
    
    app = Flask(__name__, 
                static_folder=frontend_static,
                template_folder=frontend_templates)
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
        return render_template('login.html')
    
    @app.route('/articles.html')
    def articles_page():
        """Page des articles"""
        return render_template('articles.html')
    
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

