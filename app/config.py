"""Configuración general de la aplicación"""

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Directorios
BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_PATH = BASE_DIR / "backups"
STUDIES_PATH = BASE_DIR / "studies"  # Archivos de estudios médicos
PATIENTS_PATH = BASE_DIR / "patients"  # Archivos directos de pacientes

# Base de Datos
# Si DATABASE_URL está definida, la usamos directamente
# Si no, construimos la URL desde las partes individuales
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Construir URL desde componentes individuales
    db_type = os.getenv("DATABASE_TYPE", "postgresql")
    db_user = os.getenv("DB_USER", "user")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "medical_records_db")
    
    # Encodear la contraseña si tiene caracteres especiales
    db_password_encoded = quote_plus(db_password)
    
    # Construir la URL según el tipo de base de datos
    if db_type == "mysql":
        # Para MySQL, el nombre de la base de datos NO se debe encodear
        # PyMySQL lo maneja directamente
        DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password_encoded}@{db_host}:{db_port}/{db_name}"
    elif db_type == "postgresql":
        DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    elif db_type == "sqlite":
        DATABASE_URL = f"sqlite:///./{db_name}.db"
    else:
        DATABASE_URL = "postgresql://user:password@localhost:5432/medical_records_db"

# Autenticación
ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH",
    "",  # Debe ser configurado en .env
)

# Aplicación
APP_NAME = os.getenv("APP_NAME", "Historias Clínicas")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Backups
BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "True").lower() in (
    "true",
    "1",
    "yes",
)
BACKUP_FREQUENCY_DAYS = int(os.getenv("BACKUP_FREQUENCY_DAYS", "7"))

# Constantes de la aplicación
GENDERS = ["M", "F", "Otro"]
BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# Colores del tema médico oscuro
COLORS = {
    "primary": "#3B82F6",  # Azul médico brillante
    "secondary": "#10B981",  # Verde salud brillante
    "danger": "#EF4444",  # Rojo alerta
    "warning": "#F59E0B",  # Amarillo advertencia
    "success": "#22C55E",  # Verde éxito
    "info": "#06B6D4",  # Cyan información
    "background": "#0F172A",  # Fondo oscuro principal (slate-900)
    "surface": "#1E293B",  # Tarjetas/superficie (slate-800)
    "surface_hover": "#334155",  # Hover en tarjetas (slate-700)
    "text": "#F1F5F9",  # Texto principal claro (slate-100)
    "text_secondary": "#94A3B8",  # Texto secundario (slate-400)
    "border": "#334155",  # Bordes (slate-700)
    "input_bg": "#1E293B",  # Fondo de inputs
    "navbar": "#0F172A",  # Navbar
}

# Validación
if not ADMIN_PASSWORD_HASH and ENVIRONMENT == "production":
    raise ValueError(
        "ADMIN_PASSWORD_HASH no está configurado. "
        'Genera uno con: uv run python -c "from passlib.context import CryptContext; '
        "print(CryptContext(schemes=['argon2']).hash('tu_password'))\""
    )

# Formatos y Localización Argentina 🇦🇷
LOCALE = "es_AR.UTF-8"
DATE_FORMAT = "%Y-%m-%d"  # ISO 8601: YYYY-MM-DD
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def format_ar_number(number: float, decimals: int = 2) -> str:
    """
    Formatea números con estándar argentino.

    Args:
        number: Número a formatear
        decimals: Cantidad de decimales (default: 2)

    Returns:
        String formateado con separador de miles (.) y decimal (,)
        Ejemplo: 1234.56 -> "1.234,56"
    """
    formatted = f"{number:,.{decimals}f}"
    # Intercambiar separadores: coma por punto y viceversa
    return formatted.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")


def format_ar_currency(amount: float) -> str:
    """
    Formatea moneda en pesos argentinos.

    Args:
        amount: Monto a formatear

    Returns:
        String formateado con símbolo $ y formato argentino
        Ejemplo: 1234.56 -> "$ 1.234,56"
    """
    return f"$ {format_ar_number(amount, 2)}"


# Crear carpeta de backups si no existe
BACKUP_PATH.mkdir(parents=True, exist_ok=True)
STUDIES_PATH.mkdir(parents=True, exist_ok=True)
