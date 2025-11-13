# Script de test pour l'API Microservices

Write-Host "🧪 Test de l'API Microservices" -ForegroundColor Green
Write-Host ""

# 1. Test Health Checks
Write-Host "1️⃣ Vérification de l'état des services..." -ForegroundColor Yellow
Write-Host "   API Gateway: " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Write-Host "✅ OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur" -ForegroundColor Red
}

# 2. Login
Write-Host ""
Write-Host "2️⃣ Connexion..." -ForegroundColor Yellow
$loginBody = @{
    username = "admin"
    password = "admin"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody
    
    if ($loginResponse.success) {
        Write-Host "   ✅ Connexion réussie!" -ForegroundColor Green
        $token = $loginResponse.data.access_token
        Write-Host "   Token: $($token.Substring(0, 50))..." -ForegroundColor Cyan
        
        # 3. Récupérer le profil
        Write-Host ""
        Write-Host "3️⃣ Récupération du profil..." -ForegroundColor Yellow
        $headers = @{
            "Authorization" = "Bearer $token"
        }
        
        try {
            $profile = Invoke-RestMethod -Uri "http://localhost:8000/users/profile" `
                -Method GET `
                -Headers $headers
            Write-Host "   ✅ Profil récupéré:" -ForegroundColor Green
            $profile.data | ConvertTo-Json | Write-Host
        } catch {
            Write-Host "   ❌ Erreur: $_" -ForegroundColor Red
        }
        
        # 4. Liste des produits
        Write-Host ""
        Write-Host "4️⃣ Liste des produits..." -ForegroundColor Yellow
        try {
            $products = Invoke-RestMethod -Uri "http://localhost:8000/products" -Method GET
            Write-Host "   ✅ $($products.count) produits trouvés" -ForegroundColor Green
            foreach ($product in $products.data) {
                Write-Host "   - $($product.name): $($product.price)€" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "   ❌ Erreur: $_" -ForegroundColor Red
        }
        
        # 5. Créer une commande
        Write-Host ""
        Write-Host "5️⃣ Création d'une commande..." -ForegroundColor Yellow
        $orderBody = @{
            items = @(
                @{
                    product_id = 1
                    quantity = 2
                }
            )
        } | ConvertTo-Json
        
        try {
            $order = Invoke-RestMethod -Uri "http://localhost:8000/orders" `
                -Method POST `
                -ContentType "application/json" `
                -Headers $headers `
                -Body $orderBody
            Write-Host "   ✅ Commande créée!" -ForegroundColor Green
            Write-Host "   ID: $($order.data.id), Total: $($order.data.total)€" -ForegroundColor Cyan
        } catch {
            Write-Host "   ❌ Erreur: $_" -ForegroundColor Red
        }
        
        # 6. Liste des commandes
        Write-Host ""
        Write-Host "6️⃣ Liste de vos commandes..." -ForegroundColor Yellow
        try {
            $orders = Invoke-RestMethod -Uri "http://localhost:8000/orders" `
                -Method GET `
                -Headers $headers
            Write-Host "   ✅ $($orders.count) commande(s) trouvée(s)" -ForegroundColor Green
            foreach ($order in $orders.data) {
                Write-Host "   - Commande #$($order.id): $($order.total)€ - Statut: $($order.status)" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "   ❌ Erreur: $_" -ForegroundColor Red
        }
        
    } else {
        Write-Host "   ❌ Échec de la connexion" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Erreur de connexion: $_" -ForegroundColor Red
    Write-Host "   Assurez-vous que tous les services sont démarrés!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Tests terminés!" -ForegroundColor Green

