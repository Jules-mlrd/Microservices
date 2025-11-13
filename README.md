# Architecture Microservices Flask

Application microservices moderne avec authentification JWT, gestion d'utilisateurs et système de commandes.

## 🏗️ Architecture

Cette application est structurée en **4 microservices indépendants** :

- **API Gateway** (Port 8000) - Point d'entrée unique, routage et validation des tokens
- **Auth Service** (Port 8001) - Authentification et gestion des tokens JWT
- **User Service** (Port 8002) - Gestion des profils utilisateurs
- **Orders Service** (Port 8003) - Gestion des produits et commandes

Voir [ARCHITECTURE.md](ARCHITECTURE.md) pour les détails complets de l'architecture.

## 🚀 Démarrage Rapide

### Option 1 : Script de démarrage (Recommandé)

**Windows (PowerShell)** :
```powershell
.\start-services.ps1
```

**Linux/Mac** :
```bash
chmod +x start-services.sh
./start-services.sh
```

### Option 2 : Démarrage manuel

Dans 4 terminaux séparés :

```bash
# Terminal 1 - Auth Service
cd auth-service
python -m app.main

# Terminal 2 - User Service
cd user-service
python -m app.main

# Terminal 3 - Orders Service
cd orders-service
python -m app.main

# Terminal 4 - API Gateway
cd api-gateway
python -m app.main
```

### Option 3 : Docker Compose

```bash
docker-compose up --build
```

## 📋 Prérequis

- Python 3.8+
- pip
- (Optionnel) Docker et Docker Compose

## 🔧 Installation

1. **Cloner le dépôt**
```bash
git clone https://github.com/Jules-mlrd/Microservices.git
cd Microservices
```

2. **Installer les dépendances pour chaque service**
```bash
cd auth-service && pip install -r requirements.txt && cd ..
cd api-gateway && pip install -r requirements.txt && cd ..
cd user-service && pip install -r requirements.txt && cd ..
cd orders-service && pip install -r requirements.txt && cd ..
```

## 🔐 Authentification

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

**Réponse** :
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "xYz123AbC456...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### Utiliser le token
```bash
TOKEN="votre_access_token"
curl -X GET http://localhost:8000/users/profile \
  -H "Authorization: Bearer $TOKEN"
```

Voir [EXAMPLES.md](EXAMPLES.md) pour plus d'exemples.

## 📁 Structure du Projet

```
microservices/
├── ARCHITECTURE.md          # Documentation de l'architecture
├── EXAMPLES.md              # Exemples d'utilisation
├── README.md                # Ce fichier
├── docker-compose.yml       # Orchestration Docker
│
├── auth-service/           # Service d'authentification
│   ├── app/
│   │   ├── main.py         # Point d'entrée
│   │   ├── routes.py       # Routes /auth/*
│   │   ├── jwt_utils.py    # Utilitaires JWT
│   │   └── database.py     # Gestion DB
│   └── requirements.txt
│
├── api-gateway/            # Passerelle API
│   ├── app/
│   │   ├── main.py         # Point d'entrée
│   │   ├── routes.py        # Routage
│   │   ├── auth_middleware.py  # Validation JWT
│   │   └── service_client.py   # Clients HTTP
│   └── requirements.txt
│
├── user-service/           # Service utilisateurs
│   ├── app/
│   │   ├── main.py
│   │   ├── routes.py        # Routes /users/*
│   │   └── database.py
│   └── requirements.txt
│
└── orders-service/         # Service commandes
    ├── app/
    │   ├── main.py
    │   ├── routes.py        # Routes /orders/*, /products/*
    │   └── database.py
    └── requirements.txt
```

## 🔌 Endpoints API

### Auth Service (via API Gateway)
- `POST /auth/login` - Connexion
- `POST /auth/refresh` - Renouvellement des tokens
- `POST /auth/verify` - Vérification d'un token
- `POST /auth/logout` - Déconnexion

### User Service (via API Gateway, protégé)
- `GET /users` - Liste des utilisateurs
- `GET /users/{id}` - Détails d'un utilisateur
- `POST /users` - Création d'utilisateur
- `PUT /users/{id}` - Mise à jour
- `DELETE /users/{id}` - Suppression
- `GET /users/profile` - Profil de l'utilisateur connecté

### Orders Service (via API Gateway)
- `GET /products` - Liste des produits (public)
- `GET /products/{id}` - Détails d'un produit (public)
- `GET /orders` - Liste des commandes (protégé)
- `POST /orders` - Création d'une commande (protégé)
- `GET /orders/{id}` - Détails d'une commande (protégé)
- `PUT /orders/{id}` - Mise à jour d'une commande (protégé)

## 🔒 Sécurité

- **JWT Signing** : Tokens signés avec secret key partagée
- **Token Rotation** : Refresh tokens régénérés à chaque utilisation
- **Validation** : API Gateway valide tous les tokens avant forwarding
- **Mots de passe** : Hashés avec Werkzeug (pbkdf2)

## 🗄️ Bases de Données

Chaque service utilise sa propre base SQLite :
- `auth-service/auth_service.db` - Users et refresh tokens
- `user-service/user_service.db` - Profils utilisateurs
- `orders-service/orders_service.db` - Produits et commandes

## 🧪 Tests

### Health Checks
```bash
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8001/auth/health  # Auth Service
curl http://localhost:8002/health  # User Service
curl http://localhost:8003/health  # Orders Service
```

### Test Complet
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r '.data.access_token')

# 2. Profil
curl -X GET http://localhost:8000/users/profile \
  -H "Authorization: Bearer $TOKEN"

# 3. Produits
curl http://localhost:8000/products

# 4. Créer commande
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"product_id":1,"quantity":2}]}'
```

## 📊 Monitoring

Chaque service expose un endpoint `/health` pour vérifier son état.

## 🛠️ Technologies

- **Flask** - Framework web Python
- **PyJWT** - Gestion des tokens JWT
- **SQLite** - Bases de données
- **Docker** - Containerisation
- **Requests** - Communication HTTP inter-services

## 📄 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture détaillée avec schémas
- [EXAMPLES.md](EXAMPLES.md) - Exemples d'utilisation de l'API

## 📝 Notes

- Les services communiquent via HTTP
- L'API Gateway valide les tokens avant de forwarder les requêtes
- Chaque service est indépendant et peut être déployé séparément
- Les bases de données sont locales (SQLite) pour simplifier le développement

## 👤 Auteur

Jules-mlrd

## 🔗 Liens

- [Dépôt GitHub](https://github.com/Jules-mlrd/Microservices)
