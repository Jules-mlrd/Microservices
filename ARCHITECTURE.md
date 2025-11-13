# Architecture Microservices

## 📐 Schéma Global de l'Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ARCHITECTURE MICROSERVICES                      │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │   CLIENT (Browser)   │
                    └──────────┬───────────┘
                               │
                               │ HTTP/HTTPS
                               │
                    ┌──────────▼───────────┐
                    │                     │
                    │    API GATEWAY      │
                    │   Port: 8000        │
                    │                     │
                    │  - Routing          │
                    │  - Token Validation │
                    │  - Load Balancing   │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        │                      │                      │
┌───────▼────────┐   ┌─────────▼─────────┐   ┌───────▼────────┐
│                │   │                   │   │                │
│  AUTH SERVICE  │   │  USER SERVICE    │   │ ORDERS SERVICE │
│  Port: 8001    │   │  Port: 8002      │   │  Port: 8003    │
│                │   │                   │   │                │
│ - /auth/login  │   │ - /users         │   │ - /orders      │
│ - /auth/refresh│   │ - /users/{id}    │   │ - /orders/{id} │
│ - /auth/verify │   │ - /users/profile │   │ - /products    │
│                │   │                   │   │                │
└───────┬────────┘   └─────────┬─────────┘   └───────┬────────┘
        │                      │                      │
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │                     │
                    │   SHARED DATABASE   │
                    │                     │
                    │  - SQLite (users)   │
                    │  - Redis (cache)    │
                    │                     │
                    └─────────────────────┘
```

## 🔄 Flux de Communication

### 1. Authentification
```
Client → API Gateway → Auth Service → Database
         (validate)    (generate JWT)
```

### 2. Requête Protégée
```
Client → API Gateway → (validate JWT) → User/Orders Service → Database
         (token check)                    (business logic)
```

### 3. Refresh Token
```
Client → API Gateway → Auth Service → Database
         (pass through)  (verify & rotate)
```

## 🏗️ Structure des Services

### Auth Service (Port 8001)
**Responsabilité** : Authentification et gestion des tokens JWT

**Endpoints** :
- `POST /auth/login` - Connexion et génération de tokens
- `POST /auth/refresh` - Renouvellement des tokens
- `POST /auth/logout` - Déconnexion et révocation
- `POST /auth/verify` - Vérification d'un token

**Base de données** :
- Table `users` (credentials)
- Table `refresh_tokens`

### User Service (Port 8002)
**Responsabilité** : Gestion des profils utilisateurs

**Endpoints** :
- `GET /users` - Liste des utilisateurs
- `GET /users/{id}` - Détails d'un utilisateur
- `POST /users` - Création d'utilisateur
- `PUT /users/{id}` - Mise à jour d'utilisateur
- `DELETE /users/{id}` - Suppression d'utilisateur
- `GET /users/profile` - Profil de l'utilisateur connecté

**Base de données** :
- Table `users` (profiles)

### Orders Service (Port 8003)
**Responsabilité** : Gestion des produits et commandes

**Endpoints** :
- `GET /products` - Liste des produits
- `GET /products/{id}` - Détails d'un produit
- `GET /orders` - Liste des commandes
- `GET /orders/{id}` - Détails d'une commande
- `POST /orders` - Création d'une commande
- `PUT /orders/{id}` - Mise à jour d'une commande

**Base de données** :
- Table `products`
- Table `orders`
- Table `order_items`

### API Gateway (Port 8000)
**Responsabilité** : Point d'entrée unique, routage et validation

**Fonctionnalités** :
- Routage des requêtes vers les services appropriés
- Validation des tokens JWT avant forwarding
- Gestion des erreurs et timeouts
- Logging des requêtes

**Routes** :
- `/auth/*` → Auth Service
- `/users/*` → User Service (protégé)
- `/orders/*` → Orders Service (protégé)
- `/products/*` → Orders Service (public)

## 🔐 Exemple de JWT

### Structure d'un Access Token JWT

**Header** :
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload** :
```json
{
  "sub": "admin",
  "iat": 1704067200,
  "exp": 1704070800,
  "type": "access"
}
```

**Signature** : `HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)`

### Token Complet (exemple)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImlhdCI6MTcwNDA2NzIwMCwiZXhwIjoxNzA0MDcwODAwLCJ0eXBlIjoiYWNjZXNzIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Refresh Token
- Format : Token aléatoire sécurisé (secrets.token_urlsafe(64))
- Stockage : Base de données SQLite
- Durée : 30 jours
- Rotation : Nouveau token généré à chaque refresh

## 📁 Organisation des Dossiers

```
microservices/
├── ARCHITECTURE.md              # Ce fichier
├── docker-compose.yml           # Orchestration des services
├── README.md                    # Documentation principale
│
├── auth-service/               # Service d'authentification
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Point d'entrée Flask
│   │   ├── routes.py          # Routes /auth/*
│   │   ├── jwt_utils.py        # Utilitaires JWT
│   │   └── database.py         # Gestion DB (users, refresh_tokens)
│   ├── requirements.txt
│   └── Dockerfile
│
├── api-gateway/                # Passerelle API
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Point d'entrée Flask
│   │   ├── routes.py          # Routage vers les services
│   │   ├── auth_middleware.py # Validation JWT
│   │   └── service_client.py  # Clients HTTP vers services
│   ├── requirements.txt
│   └── Dockerfile
│
├── user-service/               # Service utilisateurs
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Point d'entrée Flask
│   │   ├── routes.py          # Routes /users/*
│   │   └── database.py         # Gestion DB (users profiles)
│   ├── requirements.txt
│   └── Dockerfile
│
├── orders-service/             # Service commandes/produits
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Point d'entrée Flask
│   │   ├── routes.py          # Routes /orders/*, /products/*
│   │   └── database.py         # Gestion DB (products, orders)
│   ├── requirements.txt
│   └── Dockerfile
│
└── shared/                     # Ressources partagées
    ├── database/
    │   └── init.sql            # Schéma de base de données
    └── config/
        └── config.py           # Configuration partagée
```

## 🔌 Communication Inter-Services

### Format des Requêtes

**Requête vers API Gateway** :
```http
GET /users/profile HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**API Gateway → User Service** :
```http
GET /users/profile HTTP/1.1
Host: user-service:8002
X-User-Id: admin
X-Original-Path: /users/profile
```

### Format des Réponses

**Succès** :
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

**Erreur** :
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Token invalide ou expiré"
  }
}
```

## 🚀 Déploiement

### Développement Local
```bash
# Lancer tous les services
docker-compose up

# Ou individuellement
cd auth-service && python -m app.main
cd api-gateway && python -m app.main
cd user-service && python -m app.main
cd orders-service && python -m app.main
```

### Ports par Service
- **API Gateway** : 8000
- **Auth Service** : 8001
- **User Service** : 8002
- **Orders Service** : 8003
- **Redis** : 6379
- **SQLite** : Fichiers locaux

## 🔒 Sécurité

1. **JWT Signing** : Secret key partagée entre Auth Service et API Gateway
2. **HTTPS** : Recommandé en production
3. **CORS** : Configuration appropriée pour les clients web
4. **Rate Limiting** : Implémenté au niveau de l'API Gateway
5. **Token Rotation** : Refresh tokens régénérés à chaque utilisation

## 📊 Monitoring et Logging

- **Logs** : Chaque service log ses requêtes
- **Health Checks** : Endpoint `/health` sur chaque service
- **Metrics** : Compteurs de requêtes et erreurs

## 🔄 Workflow Complet

1. **Client se connecte** → `POST /auth/login` via API Gateway
2. **API Gateway** → Forward vers Auth Service
3. **Auth Service** → Vérifie credentials, génère tokens
4. **Client reçoit** → `access_token` + `refresh_token`
5. **Client fait requête** → `GET /users/profile` avec `access_token`
6. **API Gateway** → Valide token, forward vers User Service
7. **User Service** → Traite la requête, retourne données
8. **Client reçoit** → Données utilisateur

## 🛠️ Technologies

- **Flask** : Framework web Python
- **PyJWT** : Gestion JWT
- **SQLite** : Base de données
- **Redis** : Cache et sessions
- **Docker** : Containerisation
- **Requests** : Communication HTTP inter-services

