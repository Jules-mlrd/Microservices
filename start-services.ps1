# Script PowerShell pour démarrer tous les microservices

Write-Host "🚀 Démarrage des microservices..." -ForegroundColor Green

# Démarrer Auth Service
Write-Host "📦 Démarrage Auth Service (port 8001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd auth-service; python -m app.main" -WindowStyle Minimized

Start-Sleep -Seconds 2

# Démarrer User Service
Write-Host "📦 Démarrage User Service (port 8002)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd user-service; python -m app.main" -WindowStyle Minimized

Start-Sleep -Seconds 2

# Démarrer Orders Service
Write-Host "📦 Démarrage Orders Service (port 8003)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd orders-service; python -m app.main" -WindowStyle Minimized

Start-Sleep -Seconds 2

# Démarrer API Gateway
Write-Host "📦 Démarrage API Gateway (port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd api-gateway; python -m app.main" -WindowStyle Minimized

Write-Host ""
Write-Host "✅ Tous les services sont démarrés!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Endpoints disponibles:" -ForegroundColor Cyan
Write-Host "   - API Gateway:    http://localhost:8000"
Write-Host "   - Auth Service:   http://localhost:8001"
Write-Host "   - User Service:   http://localhost:8002"
Write-Host "   - Orders Service: http://localhost:8003"
Write-Host ""
Write-Host "Fermez les fenêtres PowerShell pour arrêter les services" -ForegroundColor Yellow

