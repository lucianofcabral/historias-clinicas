#!/bin/bash
set -e

echo "🚀 Iniciando aplicación..."

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando PostgreSQL..."
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "PostgreSQL no está listo - esperando..."
  sleep 2
done

echo "✅ PostgreSQL está listo!"

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones de Alembic..."
uv run alembic upgrade head

echo "📦 Inicializando Reflex..."
uv run reflex init

# Iniciar la aplicación
echo "🌐 Iniciando servidor Reflex..."
uv run reflex run --env prod --loglevel info --backend-only
