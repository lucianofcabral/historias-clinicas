"""Script para ejecutar migraciones de Alembic programáticamente"""

from pathlib import Path

from alembic import command
from alembic.config import Config

from app.config import DATABASE_URL

# Obtener el directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Crear configuración de Alembic
alembic_cfg = Config(str(BASE_DIR / "alembic.ini"))

# Establecer la ruta del script de migraciones
alembic_cfg.set_main_option("script_location", str(BASE_DIR / "alembic"))

# Obtener la URL de la base de datos (ya construida correctamente en app.config)
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no pudo ser construida")

# Escapar % como %% para ConfigParser
database_url_escaped = DATABASE_URL.replace('%', '%%')

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
