#!/bin/bash
# Script de despliegue para PythonAnywhere

echo "🚀 Desplegando aplicación en PythonAnywhere..."

# 1. Actualizar código
echo "📦 Actualizando código desde Git..."
cd ~/hc
git pull origin main

# 2. Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source .venv/bin/activate

# 3. Instalar/actualizar dependencias
echo "📚 Instalando dependencias..."
uv pip install -r pyproject.toml

# 4. Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
python migrate.py

# 5. Los assets deben ser compilados localmente y subidos via Git
echo "ℹ️ Assets compilados localmente (carpeta .web/)"

# 6. Recargar la aplicación web
echo "♻️ Recargando aplicación..."
touch /var/www/fexa_pythonanywhere_com_wsgi.py

echo "✅ Despliegue completado!"
echo "🌐 Tu app está en: https://fexa.pythonanywhere.com"
