"""Configuración de Reflex"""

import os

import reflex as rx

# Detectar entorno
is_production = os.getenv("APP_ENV") == "production"

# Configuración de base de datos
db_url = os.getenv("DATABASE_URL", "sqlite:///./medical_records.db")

config = rx.Config(
    app_name="app",
    db_url=db_url,
    env=rx.Env.PROD if is_production else rx.Env.DEV,
    backend_port=int(os.getenv("PORT", 8000)),
)
