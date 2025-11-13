# RESUME JWT & ARCHITECTURE MICROSERVICES

## Objectif de l'exercice
- Mettre en place une API Flask exposant un endpoint `POST /login`.
- Authentifier un utilisateur, générer un JWT signé et limité à une heure.
- Proposer un décorateur `@token_required` réutilisable pour sécuriser les routes.
- Vérifier les flux via curl/Postman pour les scénarios succès/échec.

## Flux fonctionnel
1. **Login** : l'utilisateur envoie `username`/`password` au service d'authentification.
2. **Vérification** : Flask valide les identifiants (base SQLite, Redis ou autre backend de session).
3. **Émission du JWT** : création d'un token `HS256` avec payload `sub` et `exp = now + 1h`.
4. **Protection des routes** : les endpoints sensibles appliquent `@token_required` qui vérifie l'en-tête `Authorization: Bearer <token>`.
5. **Expiration stricte** : aucun mécanisme de refresh ; un token expiré impose un nouveau login.
6. **Clients** : curl/Postman consomment l'API en deux temps (login puis requêtes protégées).

## Schéma d'architecture microservices
```
+------------------+           +------------------+           +-------------------+
|  Client (curl /  |  HTTPS    |  API Gateway /   |  JWT auth |  Services métiers |
|  Postman / SPA)  +---------->+  Flask App       +---------->+  (articles, bank) |
|                  |           |  - /login        |           |  - routes protégées|
+------------------+           |  - routes HTTP   |           +-------------------+
                               |                  |                     |
                               |  Decorator       |                     |
                               |  @token_required |                     v
                               +--------+---------+           +-------------------+
                                        |                     |  Backend persistant|
                                        |  Validations JWT    |  (SQLite / Redis)  |
                                        +-------------------->+  - Identifiants    |
                                                              |  - Sessions/états  |
                                                              +-------------------+
```

- Le **client** récupère un jeton après authentification.
- Le **gateway Flask** centralise l'émission du JWT et la protection des routes via le décorateur.
- Les **services métiers** consomment l'identité décodée (ex. `g.current_user`) pour appliquer la logique métier.
- Les **backends persistants** fournissent la source de vérité pour les identifiants ou les données métiers.

## Points clés de mise en œuvre
- Utiliser `jwt.encode(payload, SECRET_KEY, algorithm="HS256")`.
- Configurer `SECRET_KEY` et la durée (`timedelta(hours=1)`) dans la config Flask.
- Gérer `ExpiredSignatureError` et `InvalidTokenError` dans le décorateur.
- Retourner des réponses HTTP cohérentes (401 pour token absent ou expiré).
- Documenter dans la collection Postman les deux étapes : login puis requête protégée avec en-tête `Bearer`.

POINTS CLES DE MISE EN OEUVRE
• Utiliser la fonction jwt.encode(payload, SECRET_KEY, algorithm="HS256").
• Configurer SECRET_KEY et la durée (timedelta(hours=1)) dans la configuration Flask.
• Gérer ExpiredSignatureError et InvalidTokenError dans le décorateur.
• Retourner des réponses HTTP cohérentes (401 pour token absent ou expiré).
• Documenter dans Postman les deux étapes : login puis requête protégée avec l'en-tête Bearer.

