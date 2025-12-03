# Script de Despliegue para Promart AI en Google Cloud Run
# Ejecuta este script en una NUEVA terminal PowerShell

Write-Host "=== Promart AI - Despliegue a Cloud Run ===" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Verificar gcloud
Write-Host "Paso 1: Verificando instalación de gcloud..." -ForegroundColor Yellow
try {
    $version = gcloud --version
    Write-Host "✓ gcloud instalado correctamente" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: gcloud no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Por favor, reinicia tu terminal PowerShell" -ForegroundColor Red
    exit 1
}

# Paso 2: Verificar proyecto
Write-Host ""
Write-Host "Paso 2: Verificando proyecto..." -ForegroundColor Yellow
$project = gcloud config get-value project 2>$null

if ([string]::IsNullOrEmpty($project)) {
    Write-Host "No hay proyecto configurado. Creando uno nuevo..." -ForegroundColor Yellow
    $projectId = "promart-ai-" + (Get-Random -Minimum 1000 -Maximum 9999)
    
    Write-Host "Creando proyecto: $projectId" -ForegroundColor Cyan
    gcloud projects create $projectId --name="Promart AI"
    gcloud config set project $projectId
    
    Write-Host "✓ Proyecto creado: $projectId" -ForegroundColor Green
} else {
    Write-Host "✓ Usando proyecto: $project" -ForegroundColor Green
}

# Paso 3: Habilitar APIs
Write-Host ""
Write-Host "Paso 3: Habilitando APIs necesarias..." -ForegroundColor Yellow
Write-Host "Esto puede tomar 1-2 minutos..." -ForegroundColor Gray

gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet

Write-Host "✓ APIs habilitadas" -ForegroundColor Green

# Paso 4: Desplegar
Write-Host ""
Write-Host "Paso 4: Desplegando aplicación..." -ForegroundColor Yellow
Write-Host "Esto puede tomar 5-10 minutos..." -ForegroundColor Gray
Write-Host ""

gcloud run deploy promart-ai `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars GOOGLE_API_KEY=AIzaSyDKb6EkcM0FZNgdrImPt6EOHjtTQoFshb4 `
  --memory 2Gi `
  --cpu 2 `
  --timeout 300

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ ¡DESPLIEGUE EXITOSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Tu aplicación está disponible en la URL que aparece arriba" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "✗ Error en el despliegue" -ForegroundColor Red
    Write-Host "Revisa los mensajes de error arriba" -ForegroundColor Red
}
