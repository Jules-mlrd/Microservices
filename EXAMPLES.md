# Exemples d'Utilisation des Microservices

## 🔐 Authentification

### 1. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'
```

**Réponse** :
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "xYz123AbC456...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_expires_at": 1704153600
  }
}
```

### 2. Vérifier un token
```bash
curl -X POST http://localhost:8000/auth/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

### 3. Refresh token
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "xYz123AbC456..."
  }'
```

## 👤 Gestion des Utilisateurs

### 1. Récupérer le profil (protégé)
```bash
curl -X GET http://localhost:8000/users/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2. Liste des utilisateurs (protégé)
```bash
curl -X GET http://localhost:8000/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Créer un utilisateur (protégé)
```bash
curl -X POST http://localhost:8000/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 4. Mettre à jour un utilisateur (protégé)
```bash
curl -X PUT http://localhost:8000/users/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "phone": "+33123456789"
  }'
```

## 🛒 Produits et Commandes

### 1. Liste des produits (public)
```bash
curl -X GET http://localhost:8000/products
```

### 2. Détails d'un produit (public)
```bash
curl -X GET http://localhost:8000/products/1
```

### 3. Créer une commande (protégé)
```bash
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      },
      {
        "product_id": 3,
        "quantity": 1
      }
    ]
  }'
```

### 4. Liste des commandes (protégé)
```bash
curl -X GET http://localhost:8000/orders \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 5. Détails d'une commande (protégé)
```bash
curl -X GET http://localhost:8000/orders/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 📋 Exemple de JWT Token

### Structure du Token
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "admin",
    "iat": 1704067200,
    "exp": 1704070800,
    "type": "access"
  },
  "signature": "HMACSHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), secret)"
}
```

### Token Complet (exemple)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImlhdCI6MTcwNDA2NzIwMCwiZXhwIjoxNzA0MDcwODAwLCJ0eXBlIjoiYWNjZXNzIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Décodage du Payload (Base64)
```json
{
  "sub": "admin",
  "iat": 1704067200,
  "exp": 1704070800,
  "type": "access"
}
```

## 🔄 Workflow Complet

### Scénario : Achat d'un produit

1. **Login**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r '.data.access_token')
```

2. **Voir les produits**
```bash
curl -X GET http://localhost:8000/products
```

3. **Créer une commande**
```bash
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"product_id":1,"quantity":1}]}'
```

4. **Voir mes commandes**
```bash
curl -X GET http://localhost:8000/orders \
  -H "Authorization: Bearer $TOKEN"
```

## 🧪 Tests avec Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin"
})
token = response.json()['data']['access_token']

# Headers avec token
headers = {"Authorization": f"Bearer {token}"}

# Récupérer le profil
profile = requests.get(f"{BASE_URL}/users/profile", headers=headers)
print(profile.json())

# Liste des produits
products = requests.get(f"{BASE_URL}/products")
print(products.json())

# Créer une commande
order = requests.post(f"{BASE_URL}/orders", headers=headers, json={
    "items": [{"product_id": 1, "quantity": 2}]
})
print(order.json())
```

## 📊 Health Checks

Vérifier l'état de tous les services :

```bash
# API Gateway
curl http://localhost:8000/health

# Auth Service
curl http://localhost:8001/auth/health

# User Service
curl http://localhost:8002/health

# Orders Service
curl http://localhost:8003/health
```

