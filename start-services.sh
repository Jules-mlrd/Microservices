#!/bin/bash

# Script pour démarrer tous les microservices

echo "🚀 Démarrage des microservices..."

# Démarrer Auth Service
echo "📦 Démarrage Auth Service (port 8001)..."
cd auth-service && python -m app.main &
AUTH_PID=$!

# Attendre que Auth Service soit prêt
sleep 2

# Démarrer User Service
echo "📦 Démarrage User Service (port 8002)..."
cd ../user-service && python -m app.main &
USER_PID=$!

# Attendre que User Service soit prêt
sleep 2

# Démarrer Orders Service
echo "📦 Démarrage Orders Service (port 8003)..."
cd ../orders-service && python -m app.main &
ORDERS_PID=$!

# Attendre que Orders Service soit prêt
sleep 2

# Démarrer API Gateway
echo "📦 Démarrage API Gateway (port 8000)..."
cd ../api-gateway && python -m app.main &
GATEWAY_PID=$!

echo ""
echo "✅ Tous les services sont démarrés!"
echo ""
echo "📍 Endpoints disponibles:"
echo "   - API Gateway:    http://localhost:8000"
echo "   - Auth Service:   http://localhost:8001"
echo "   - User Service:   http://localhost:8002"
echo "   - Orders Service: http://localhost:8003"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter tous les services"

# Fonction pour nettoyer les processus à l'arrêt
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    kill $AUTH_PID $USER_PID $ORDERS_PID $GATEWAY_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Attendre indéfiniment
wait

