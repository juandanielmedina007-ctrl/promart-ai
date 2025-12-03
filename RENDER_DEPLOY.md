# Despliegue en Render.com (GRATIS, sin tarjeta)

## Pasos para Desplegar

### 1. Crea una cuenta en Render
- Ve a: https://render.com
- Regístrate con tu cuenta de GitHub o email

### 2. Sube tu código a GitHub
Si no tienes el código en GitHub:
```bash
# Inicializar git (si no lo has hecho)
git init
git add .
git commit -m "Initial commit"

# Crear repositorio en GitHub y conectarlo
git remote add origin https://github.com/TU_USUARIO/promart-ai.git
git push -u origin main
```

### 3. Crear Web Service en Render
1. En Render Dashboard, clic en "New +" → "Web Service"
2. Conecta tu repositorio de GitHub
3. Configura:
   - **Name**: `promart-ai`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 app:app`

### 4. Variables de Entorno
En la sección "Environment Variables", agrega:
- **Key**: `GOOGLE_API_KEY`
- **Value**: `AIzaSyDKb6EkcM0FZNgdrImPt6EOHjtTQoFshb4`

### 5. Plan
- Selecciona el plan **Free** (gratis)

### 6. Despliega
- Clic en "Create Web Service"
- Espera 5-10 minutos mientras se construye

### 7. ¡Listo!
Tu app estará disponible en: `https://promart-ai.onrender.com`

## Limitaciones del Plan Gratuito
- La app se "duerme" después de 15 minutos sin uso
- Tarda ~30 segundos en "despertar" cuando alguien la visita
- 750 horas gratis al mes (suficiente para uso personal)

## Ventajas
✅ No requiere tarjeta de crédito
✅ Despliegue automático desde GitHub
✅ SSL/HTTPS incluido
✅ Fácil de usar
