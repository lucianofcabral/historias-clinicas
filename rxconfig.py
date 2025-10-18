"""Configuración de Reflex"""

import reflex as rx

config = rx.Config(
    app_name="app",  # Apunta a la carpeta app
    db_url="sqlite:///./medical_records.db",
    env=rx.Env.DEV,
)
