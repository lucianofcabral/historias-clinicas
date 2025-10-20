"""Configuración de Reflex"""

import os

import reflex as rx

# Detectar entorno
is_production = os.getenv("APP_ENV") == "production"

# Configuración de base de datos
db_url = os.getenv("DATABASE_URL", "sqlite:///./medical_records.db")

# Render usa postgresql:// pero SQLAlchemy necesita postgresql+psycopg2://
if is_production and db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# MySQL necesita mysqlclient driver
if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+mysqldb://", 1)

config = rx.Config(
    app_name="app",
    db_url=db_url,
    env=rx.Env.PROD if is_production else rx.Env.DEV,
    backend_port=int(os.getenv("PORT", 8000)),
    backend_host="0.0.0.0" if is_production else "0.0.0.0",
)
