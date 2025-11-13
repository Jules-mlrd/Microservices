"""
Point d'entrée principal de l'application Flask
Lance le serveur de développement
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("[DEMARRAGE] Demarrage du serveur Flask...")
    print("[INFO] Accedez a l'application sur: http://localhost:5000")
    print("[INFO] Page de login: http://localhost:5000/login")
    app.run(debug=True, host='0.0.0.0', port=5000)

