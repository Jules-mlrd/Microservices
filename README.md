# Microservices Flask - Application E-commerce avec JWT

Application Flask microservices avec authentification JWT, refresh tokens, gestion d'utilisateurs et système de panier.

## 🚀 Fonctionnalités

### Authentification
- **Login/Logout** avec sessions Redis
- **JWT Access Tokens** (expiration 1h)
- **Refresh Tokens** (expiration 30 jours) avec rotation
- **Stockage sécurisé** des refresh tokens en base de données SQLite

### Gestion des utilisateurs
- **Ajout d'utilisateurs** via interface web
- **Suppression d'utilisateurs**
- **Liste des utilisateurs** avec informations détaillées
- **Mots de passe hashés** avec Werkzeug

### E-commerce
- **Catalogue d'articles** avec prix et descriptions
- **Panier d'achat** persistant (Redis)
- **Paiement simulé** avec circuit breaker
- **Gestion de commandes**

### API REST
- `POST /auth/login` - Authentification et récupération de tokens
- `POST /auth/refresh` - Renouvellement des tokens
- `POST /auth/logout` - Déconnexion et révocation de tokens
- `GET /auth/profile` - Profil utilisateur (protégé)
- `GET /api/articles` - Liste des articles
- `GET /api/users` - Liste des utilisateurs

## 📋 Prérequis

- Python 3.8+
- Redis (local ou cloud)
- SQLite (inclus avec Python)

## 🔧 Installation

1. **Cloner le dépôt**
```bash
git clone https://github.com/Jules-mlrd/Microservices.git
cd Microservices
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer Redis**
   - Créer un fichier `.env` à la racine :
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_USERNAME=
REDIS_DB=0
```

4. **Lancer l'application**
```bash
python run.py
```

L'application sera accessible sur `http://localhost:5000`

## 📁 Structure du projet

```
Exo_Flask/
├── app/
│   ├── __init__.py          # Configuration Flask et Redis
│   ├── database.py          # Gestion SQLite et refresh tokens
│   ├── routes.py            # Routes web et API
│   ├── static/
│   │   ├── auth.js          # Script de vérification JWT
│   │   └── style.css        # Styles CSS
│   └── templates/
│       ├── admin_users.html  # Gestion des utilisateurs
│       ├── articles.html     # Catalogue
│       ├── cart.html         # Panier
│       ├── login.html        # Connexion
│       └── ...
├── requirements.txt
├── run.py
└── README.md
```

## 🔐 Sécurité

- **Mots de passe hashés** avec Werkzeug (pbkdf2)
- **JWT signés** avec secret key
- **Refresh tokens** stockés en base avec expiration
- **Rotation des tokens** à chaque refresh
- **Révocation** des tokens possible

## 🗄️ Base de données

### Table `users`
- `id` (INTEGER PRIMARY KEY)
- `username` (TEXT UNIQUE)
- `password` (TEXT - hashé)
- `email` (TEXT)
- `date_creation` (TIMESTAMP)

### Table `refresh_tokens`
- `id` (INTEGER PRIMARY KEY)
- `token` (TEXT UNIQUE)
- `username` (TEXT)
- `expires_at` (INTEGER)
- `created_at` (INTEGER)
- `revoked` (BOOLEAN)

## 📝 Utilisation

### Connexion
1. Accéder à `http://localhost:5000/login`
2. Utiliser les identifiants par défaut :
   - Username: `admin`
   - Password: `admin`

### Gestion des utilisateurs
1. Se connecter
2. Cliquer sur "Gérer les utilisateurs" dans le header
3. Ajouter de nouveaux utilisateurs via le formulaire
4. Consulter/supprimer les utilisateurs existants

### API JWT
```bash
# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Utiliser le token
curl -X GET http://localhost:5000/auth/profile \
  -H "Authorization: Bearer <access_token>"

# Refresh token
curl -X POST http://localhost:5000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

## 🛠️ Technologies utilisées

- **Flask** - Framework web Python
- **PyJWT** - Gestion des tokens JWT
- **Redis** - Cache et sessions
- **SQLite** - Base de données
- **Werkzeug** - Hashage des mots de passe
- **PyBreaker** - Circuit breaker pattern

## 📄 Licence

Ce projet est un exercice éducatif.

## 👤 Auteur

Jules-mlrd

## 🔗 Liens

- [Dépôt GitHub](https://github.com/Jules-mlrd/Microservices)

