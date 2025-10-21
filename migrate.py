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

# Si la URL contiene $ (común en bases de datos de PythonAnywhere),
# lo convertimos al encoding URL correcto (%24)
# y luego escapamos el % para ConfigParser (%%)
if '$' in database_url:
    # Primero convertir $ a %24 (URL encoding)
    database_url_encoded = database_url.replace('$', '%24')
    # Luego escapar % como %% para ConfigParser
    database_url_escaped = database_url_encoded.replace('%', '%%')
else:
    # Si no hay $, solo escapar % si existe
    database_url_escaped = database_url.replace('%', '%%')

# Establecer la URL directamente (escapada para ConfigParser)
alembic_cfg.set_main_option("sqlalchemy.url", database_url_escaped)

print("🔍 Conectando a la base de datos...")
print("📦 Ejecutando migraciones...")

try:
    # Ejecutar upgrade head
    command.upgrade(alembic_cfg, "head")
    print("✅ Migraciones ejecutadas exitosamente!")
except Exception as e:
    print(f"❌ Error al ejecutar migraciones: {e}")
    raise
