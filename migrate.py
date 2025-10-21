"""Script para ejecutar migraciones de Alembic programáticamente"""

import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener el directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Crear configuración de Alembic
alembic_cfg = Config(str(BASE_DIR / "alembic.ini"))

# Establecer la ruta del script de migraciones
alembic_cfg.set_main_option("script_location", str(BASE_DIR / "alembic"))

# Obtener la URL de la base de datos desde el .env
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL no está definida en el archivo .env")

# Establecer la URL directamente (sin pasar por ConfigParser)
alembic_cfg.set_main_option("sqlalchemy.url", database_url)

print("🔍 Conectando a la base de datos...")
print("📦 Ejecutando migraciones...")

try:
    # Ejecutar upgrade head
    command.upgrade(alembic_cfg, "head")
    print("✅ Migraciones ejecutadas exitosamente!")
except Exception as e:
    print(f"❌ Error al ejecutar migraciones: {e}")
    raise
