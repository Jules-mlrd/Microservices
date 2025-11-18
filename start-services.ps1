# Script PowerShell pour demarrer tous les microservices

Write-Host "Demarrage des microservices..." -ForegroundColor Green

# Demarrer Auth Service
Write-Host "Demarrage Auth Service (port 8001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd auth-service; python -m app.main" -WindowStyle Minimized

Start-Sleep -Seconds 2

# Demarrer User Service
Write-Host "Demarrage User Service (port 8002)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd user-service; python -m app.main" -WindowStyle Minimized

Start-Sleep -Seconds 2

# Demarrer Orders Service
Write-Host "Demarrage Orders Service (port 8003)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd orders-service; python -m app.main" -WindowStyle Minimized

Start-Sleep -Seconds 2

# Demarrer API Gateway
Write-Host "Demarrage API Gateway (port 5000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd api-gateway; python -m app.main" -WindowStyle Minimized

Write-Host ""
Write-Host "Tous les services sont demarres!" -ForegroundColor Green
Write-Host ""
Write-Host "Endpoints disponibles:" -ForegroundColor Cyan
Write-Host "   - API Gateway:    http://localhost:5000"
Write-Host "   - Auth Service:   http://localhost:8001"
Write-Host "   - User Service:   http://localhost:8002"
Write-Host "   - Orders Service: http://localhost:8003"
Write-Host ""
Write-Host "Fermez les fenetres PowerShell pour arreter les services" -ForegroundColor Yellow
