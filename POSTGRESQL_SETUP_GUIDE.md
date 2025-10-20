# 🐘 Guía de Migración a PostgreSQL

**Proyecto**: Sistema de Historia Clínica  
**Estado**: Pendiente - Para próxima sesión  
**Fecha**: 20 de octubre de 2025

---

## 🎯 Objetivo

Migrar la base de datos de **SQLite** (desarrollo) a **PostgreSQL** (producción), manteniendo toda la funcionalidad existente y los datos actuales.

---

## 📋 Opciones de Implementación

### Opción 1: PostgreSQL en Docker (✅ Recomendado)

**Ventajas:**
- ✅ Configuración rápida y reproducible
- ✅ Aislamiento completo del sistema
- ✅ Fácil de resetear/destruir
- ✅ Mismo ambiente que producción
- ✅ No contamina el sistema local
- ✅ Incluye pgAdmin para gestión visual

**Desventajas:**
- ❌ Requiere Docker instalado
- ❌ Consume más recursos

---

### Opción 2: PostgreSQL Local en Ubuntu

**Ventajas:**
- ✅ Más rápido (sin overhead de Docker)
- ✅ Integración directa con el sistema
- ✅ Menor consumo de memoria

**Desventajas:**
- ❌ Configuración manual más compleja
- ❌ Afecta el sistema global
- ❌ Más difícil de limpiar/resetear

---

## 🐳 Opción 1: Setup con Docker

### Paso 1: Crear `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: hc_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: historia_clinica
      POSTGRES_USER: hc_user
      POSTGRES_PASSWORD: hc_password_dev_2025
      POSTGRES_HOST_AUTH_METHOD: scram-sha-256
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hc_user -d historia_clinica"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: hc_pgadmin
    restart: unless-stopped
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@historiaclinica.local
      PGADMIN_DEFAULT_PASSWORD: admin
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    ports:
      - "5050:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    depends_on:
      - postgres

volumes:
  postgres_data:
    name: hc_postgres_data
  pgadmin_data:
    name: hc_pgadmin_data
```

### Paso 2: Comandos Docker

```bash
# Iniciar contenedores
docker-compose up -d

# Ver logs
docker-compose logs -f postgres

# Verificar estado
docker-compose ps

# Detener contenedores
docker-compose down

# Destruir TODO (incluyendo datos)
docker-compose down -v

# Acceder a psql
docker exec -it hc_postgres psql -U hc_user -d historia_clinica

# Backup
docker exec hc_postgres pg_dump -U hc_user historia_clinica > backup.sql

# Restore
cat backup.sql | docker exec -i hc_postgres psql -U hc_user historia_clinica
```

### Paso 3: Acceso a pgAdmin

1. Abrir navegador: `http://localhost:5050`
2. Login: `admin@historiaclinica.local` / `admin`
3. Agregar servidor:
   - Host: `postgres` (nombre del servicio)
   - Port: `5432`
   - Database: `historia_clinica`
   - Username: `hc_user`
   - Password: `hc_password_dev_2025`

---

## 💻 Opción 2: Setup Local en Ubuntu

### Paso 1: Instalación

```bash
# Actualizar repositorios
sudo apt update

# Instalar PostgreSQL 16
sudo apt install postgresql-16 postgresql-contrib-16

# Verificar instalación
psql --version

# Verificar servicio
sudo systemctl status postgresql
```

### Paso 2: Configuración de Usuario y Base de Datos

```bash
# Cambiar a usuario postgres
sudo -u postgres psql

# En psql:
CREATE DATABASE historia_clinica;
CREATE USER hc_user WITH PASSWORD 'hc_password_dev_2025';
GRANT ALL PRIVILEGES ON DATABASE historia_clinica TO hc_user;
ALTER DATABASE historia_clinica OWNER TO hc_user;

# PostgreSQL 15+ requiere permisos adicionales:
\c historia_clinica
GRANT ALL ON SCHEMA public TO hc_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hc_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hc_user;

# Salir
\q
```

### Paso 3: Configuración de Acceso

```bash
# Editar pg_hba.conf para permitir acceso local
sudo nano /etc/postgresql/16/main/pg_hba.conf

# Agregar/modificar línea:
# local   all             hc_user                                 scram-sha-256

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

### Paso 4: Testing de Conexión

```bash
# Probar conexión
psql -U hc_user -d historia_clinica -h localhost

# Verificar que funcione
\dt  # Listar tablas (debería estar vacío inicialmente)
\q   # Salir
```

---

## 🔧 Cambios en el Código

### 1. Instalar Dependencias

```bash
# Activar entorno virtual
uv venv
source .venv/bin/activate  # o como esté configurado

# Instalar driver de PostgreSQL
uv pip install psycopg2-binary

# O agregar a pyproject.toml:
# psycopg2-binary = "^2.9.9"
```

### 2. Actualizar `app/config.py`

```python
import os
from pathlib import Path

# ... código existente ...

# Base de datos
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")  # sqlite o postgresql

if DATABASE_TYPE == "postgresql":
    # PostgreSQL
    DB_USER = os.getenv("DB_USER", "hc_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "hc_password_dev_2025")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "historia_clinica")
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # SQLite (default)
    DATABASE_URL = f"sqlite:///{BASE_DIR}/historia_clinica.db"
```

### 3. Crear `.env` (Opcional)

```bash
# .env
DATABASE_TYPE=postgresql
DB_USER=hc_user
DB_PASSWORD=hc_password_dev_2025
DB_HOST=localhost
DB_PORT=5432
DB_NAME=historia_clinica
```

### 4. Actualizar `app/database.py` (si es necesario)

```python
from sqlmodel import create_engine, Session
from app.config import DATABASE_URL

# Agregar configuraciones específicas para PostgreSQL
engine_args = {}

if "postgresql" in DATABASE_URL:
    engine_args = {
        "pool_pre_ping": True,  # Verifica conexiones antes de usar
        "pool_size": 10,        # Pool de conexiones
        "max_overflow": 20,     # Máximo overflow
        "echo": False,          # Logs SQL (True para debug)
    }
else:
    engine_args = {
        "connect_args": {"check_same_thread": False},
        "echo": False,
    }

engine = create_engine(DATABASE_URL, **engine_args)
```

---

## 📦 Migración de Datos

### Opción A: Script Python para Migración

```python
# migrate_to_postgresql.py
"""
Script para migrar datos de SQLite a PostgreSQL
"""
from sqlmodel import create_engine, Session, select
from app.models.patient import Patient
from app.models.consultation import Consultation
from app.models.medical_study import MedicalStudy
# ... importar todos los modelos

# Conexiones
sqlite_engine = create_engine("sqlite:///historia_clinica.db")
postgres_engine = create_engine("postgresql://hc_user:hc_password_dev_2025@localhost/historia_clinica")

def migrate_table(model_class, sqlite_session, postgres_session):
    """Migra una tabla específica"""
    print(f"Migrando {model_class.__tablename__}...")
    
    # Leer de SQLite
    records = sqlite_session.exec(select(model_class)).all()
    
    # Escribir a PostgreSQL
    for record in records:
        postgres_session.add(record)
    
    postgres_session.commit()
    print(f"✅ {len(records)} registros migrados")

def main():
    with Session(sqlite_engine) as sqlite_session:
        with Session(postgres_engine) as postgres_session:
            # Migrar en orden (respetando foreign keys)
            migrate_table(Patient, sqlite_session, postgres_session)
            migrate_table(Consultation, sqlite_session, postgres_session)
            migrate_table(MedicalStudy, sqlite_session, postgres_session)
            # ... resto de tablas

if __name__ == "__main__":
    main()
```

### Opción B: Usar Alembic (Recomendado)

```bash
# 1. Asegurarse de que las migraciones estén al día en SQLite
alembic upgrade head

# 2. Cambiar a PostgreSQL en config.py o .env
export DATABASE_TYPE=postgresql

# 3. Ejecutar migraciones en PostgreSQL
alembic upgrade head

# 4. Usar script de migración de datos (opción A)
python migrate_to_postgresql.py
```

---

## ✅ Checklist de Migración

### Preparación
- [ ] Decidir: Docker o Local
- [ ] Instalar PostgreSQL (según opción)
- [ ] Crear base de datos y usuario
- [ ] Probar conexión manual

### Configuración
- [ ] Instalar `psycopg2-binary`
- [ ] Actualizar `app/config.py`
- [ ] Crear `.env` (opcional)
- [ ] Actualizar `app/database.py`

### Migración
- [ ] Backup de SQLite actual
- [ ] Ejecutar migraciones Alembic en PostgreSQL
- [ ] Crear script de migración de datos
- [ ] Ejecutar migración de datos
- [ ] Verificar integridad de datos

### Testing
- [ ] Probar login
- [ ] Probar CRUD de pacientes
- [ ] Probar CRUD de consultas
- [ ] Probar CRUD de estudios
- [ ] Probar upload de archivos
- [ ] Probar descarga de archivos
- [ ] Probar reportes
- [ ] Probar backup

### Documentación
- [ ] Actualizar README.md con instrucciones de PostgreSQL
- [ ] Documentar proceso de migración
- [ ] Agregar troubleshooting común
- [ ] Actualizar docker-compose si aplica

---

## 🚨 Diferencias SQLite vs PostgreSQL

### Tipos de Datos
| SQLite | PostgreSQL |
|--------|------------|
| INTEGER | INTEGER, SERIAL |
| TEXT | VARCHAR, TEXT |
| REAL | REAL, DOUBLE PRECISION |
| BLOB | BYTEA |
| DATETIME | TIMESTAMP |

### Características
| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Concurrencia | ❌ Limitada | ✅ Excelente |
| Transacciones | ✅ Básicas | ✅ ACID completo |
| Constraints | ✅ Básicos | ✅ Avanzados |
| Full-text search | ❌ No | ✅ Sí |
| JSON support | ✅ Básico | ✅ Completo |
| Performance | ✅ Rápido lectura | ✅ Rápido escritura |

---

## 🔍 Testing Post-Migración

```bash
# 1. Verificar tablas creadas
psql -U hc_user -d historia_clinica -c "\dt"

# 2. Verificar datos migrados
psql -U hc_user -d historia_clinica -c "SELECT COUNT(*) FROM patients;"
psql -U hc_user -d historia_clinica -c "SELECT COUNT(*) FROM consultations;"
psql -U hc_user -d historia_clinica -c "SELECT COUNT(*) FROM medical_studies;"

# 3. Verificar integridad referencial
psql -U hc_user -d historia_clinica -c "
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'public';
"

# 4. Iniciar aplicación y probar
python -m reflex run
```

---

## 📚 Recursos Útiles

### Docker
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [pgAdmin Docker Hub](https://hub.docker.com/r/dpage/pgadmin4)

### PostgreSQL
- [Documentación oficial](https://www.postgresql.org/docs/)
- [SQLModel con PostgreSQL](https://sqlmodel.tiangolo.com/)
- [Alembic con PostgreSQL](https://alembic.sqlalchemy.org/)

### Troubleshooting
- [Common PostgreSQL Errors](https://wiki.postgresql.org/wiki/Common_Errors)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

---

## 💡 Recomendaciones

1. **Empezar con Docker**: Es más fácil y seguro
2. **Backup primero**: Siempre hacer backup de SQLite antes
3. **Testing incremental**: Probar cada módulo después de migrar
4. **Mantener SQLite**: Dejar opción de cambiar entre DBs
5. **Variables de entorno**: Usar `.env` para configuración
6. **pgAdmin**: Muy útil para visualizar y debuggear
7. **Logging**: Activar `echo=True` durante migración para debug

---

## 🎯 Próximos Pasos Después de PostgreSQL

1. **Optimización de queries** con índices
2. **Full-text search** en consultas y estudios
3. **Backup automatizado** a S3 o similar
4. **Replicación** para alta disponibilidad
5. **Monitoring** con pgBadger o similar

---

**Creado**: 20 de octubre de 2025  
**Para**: Próxima sesión de desarrollo  
**Prioridad**: Alta - Preparación para producción
