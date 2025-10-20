#!/usr/bin/env bash
# Script de build para Render.com

set -o errexit  # Exit on error

echo "🔧 Instalando dependencias con UV..."
pip install uv
uv sync

echo "🔄 Ejecutando migraciones de Alembic..."
uv run alembic upgrade head

echo "📦 Inicializando Reflex..."
uv run reflex init

echo "✅ Build completado!"
