"""Configuración de la base de datos con SQLModel"""

from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL

# Motor de base de datos
# echo=True para ver las queries SQL en desarrollo (útil para debugging)
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Cambiar a False en producción
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=5,  # Número de conexiones en el pool
    max_overflow=10,  # Conexiones adicionales si se necesitan
)


def create_db_and_tables() -> None:
    """
    Crea todas las tablas en la base de datos.
    Solo se debe llamar una vez al inicializar la aplicación.

    Nota: En producción, usar Alembic para migraciones en lugar de esto.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Generador de sesiones de base de datos.
    Asegura que la sesión se cierre correctamente después de cada uso.

    Uso:
        with get_session() as session:
            # realizar operaciones con la sesión
            pass

    Yields:
        Session: Sesión de SQLModel para interactuar con la BD
    """
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """
    Inicializa la base de datos.
    Crea las tablas si no existen.

    Llamar esta función al inicio de la aplicación.
    """
    create_db_and_tables()
    print("✅ Base de datos inicializada correctamente")


# Función auxiliar para obtener una sesión directa (sin generador)
def get_db_session() -> Session:
    """
    Obtiene una sesión de base de datos directa.

    IMPORTANTE: Debes cerrar manualmente la sesión con session.close()
    o usar dentro de un context manager.

    Returns:
        Session: Sesión de SQLModel
    """
    return Session(engine)
