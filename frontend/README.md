# Frontend - Interface Web

Interface web simple pour interagir avec les microservices.

## Structure

- `templates/` - Pages HTML
  - `login.html` - Page de connexion
  - `articles.html` - Page des articles
  
- `static/` - Fichiers statiques
  - `api.js` - Client API pour communiquer avec l'API Gateway
  - `style.css` - Styles CSS

## Accès

Une fois l'API Gateway démarré, accédez à :

- **Page de login** : http://localhost:8000/login.html
- **Page des articles** : http://localhost:8000/articles.html

## Fonctionnalités

- Connexion avec authentification JWT
- Affichage des produits depuis l'API
- Ajout au panier (création de commande)
- Achat direct
- Gestion automatique des tokens

## Utilisation

1. Démarrer l'API Gateway (et tous les autres services)
2. Ouvrir http://localhost:8000/login.html dans votre navigateur
3. Se connecter avec `admin` / `admin`
4. Naviguer vers la page des articles

