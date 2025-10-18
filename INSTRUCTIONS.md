# Instrucciones para Agente IA - Sistema de Gestión de Historias Clínicas

**Proyecto:** Sistema de Gestión de Historias Clínicas (Usuario Único)
**Desarrollador:** @lucianofcabral
**Fecha de Inicio:** 2025-01-18
**Stack Tecnológico:** Python 3.13 + Reflex + PostgreSQL + SQLModel
**Gestor de Paquetes:** UV (Astral)

---

## 🎯 Objetivo del Proyecto

Desarrollar una aplicación web de escritorio para gestionar historias clínicas de pacientes de un consultorio médico individual, con enfoque en simplicidad, seguridad de datos y usabilidad.

---

## 🐍 Entorno de Desarrollo

### Versiones Requeridas
- **Python:** 3.13+
- **Gestor de Paquetes:** UV (Astral) - https://github.com/astral-sh/uv
- **PostgreSQL:** 14+ 

### ¿Por qué UV?
- ⚡ **Extremadamente rápido** (10-100x más rápido que pip)
- 🔒 **Lock files automáticos** (reproducibilidad garantizada)
- 📦 **Gestión de Python incluida** (instala versiones de Python)
- 🎯 **Compatible con pip/requirements.txt**
- 🚀 **Instalación de dependencias en paralelo**

### Instalación de UV

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verificar instalación
uv --version
```

---

## 📋 Principios de Desarrollo

### Seguridad Esencial
- **OBLIGATORIO** implementar login simple (un solo usuario)
- **CRÍTICO** backup automático de base de datos
- **REQUERIDO** validar y sanitizar todos los inputs
- **IMPORTANTE** proteger con contraseña el acceso a la app

### Código Limpio y Simple
- Type hints en todas las funciones (aprovechar Python 3.13)
- Nombres descriptivos en español para variables de negocio
- Código técnico en inglés
- Máximo 100 caracteres por línea
- Priorizar claridad sobre complejidad

### Base de Datos
- **ORM:** SQLModel (no SQLAlchemy puro)
- **Migraciones:** Usar Alembic para cambios en esquema
- **Nombres:** snake_case para tablas y columnas
- **Índices:** Crear en campos de búsqueda frecuente (dni, nombre)

### Formatos y Localización (Argentina) 🇦🇷
- **Fechas:** SIEMPRE formato ISO 8601 `YYYY-MM-DD` (ej: `2025-10-18`)
  - En base de datos: tipo `date` o `datetime`
  - En inputs HTML: `type="date"` (estándar ISO)
  - En displays: mantener `YYYY-MM-DD` para consistencia
  - NO usar formatos DD/MM/YYYY o MM/DD/YYYY
- **Números:**
  - Separador decimal: coma `,` (ej: `36,5°C`, `1,75 m`)
  - Separador de miles: punto `.` (ej: `1.000`, `10.500`)
  - En código Python: usar `locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')`
  - Para formateo: `f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")`
- **DNI:** Formato argentino sin puntos ni guiones (ej: `12345678`)
  - Validación: 7-8 dígitos numéricos
  - Almacenar como string para preservar ceros iniciales
- **Teléfonos:** Formato flexible argentino
  - Con código de área: `(011) 1234-5678` o `011-1234-5678`
  - Celular: `15-1234-5678` o `011-15-1234-5678`
- **Moneda:** Pesos argentinos
  - Símbolo: `$` o `ARS`
  - Formato: `$ 1.234,56`

---

## 🏗️ Estructura del Proyecto

```
medical_records/
├── .env                      # Variables de entorno (NO commitear)
├── .env.example             # Plantilla de variables
├── .gitignore
├── .python-version          # Versión de Python para UV
├── README.md
├── INSTRUCTIONS.md          # Este archivo
├── pyproject.toml           # Configuración UV y dependencias
├── uv.lock                  # Lock file (commitear, NO editar)
├── alembic.ini
├── alembic/
│   └── versions/            # Migraciones de BD
├── app/
│   ├── __init__.py
│   ├── config.py            # Configuración general
│   ├── database.py          # Conexión DB
│   ├── main.py              # App principal Reflex
│   ├── models/              # Modelos SQLModel
│   │   ├── __init__.py
│   │   ├── patient.py       # Paciente
│   │   ├── consultation.py  # Consulta médica
│   │   ├── medication.py    # Medicamentos
│   │   └── study.py         # Estudios/Análisis
│   ├── pages/               # Páginas Reflex
│   │   ├── __init__.py
│   │   ├── login.py         # Login simple
│   │   ├── dashboard.py     # Página principal
│   │   ├── patients.py      # Lista y gestión de pacientes
│   │   ├── patient_detail.py # Detalle/Historia clínica
│   │   └── settings.py      # Configuración
│   ├── components/          # Componentes reutilizables
│   │   ├── __init__.py
│   │   ├── navbar.py
│   │   ├── patient_card.py
│   │   ├── consultation_form.py
│   │   └── vital_signs.py
│   ├── services/            # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── patient_service.py
│   │   ├── consultation_service.py
│   │   └── backup_service.py
│   ├── utils/               # Utilidades
│   │   ├── __init__.py
│   │   ├── security.py      # Hashing password
│   │   ├── validators.py    # Validaciones
│   │   └── constants.py     # Constantes
│   └── state/               # Estados de Reflex
│       ├── __init__.py
│       ├── auth_state.py
│       └── patient_state.py
└── backups/                 # Backups automáticos (NO commitear)
    └── .gitkeep
```

---

## 📦 Configuración del Proyecto con UV

### Archivo `.python-version`
```
3.13
```

### Archivo `pyproject.toml`

```toml
[project]
name = "medical-records"
version = "0.1.0"
description = "Sistema de Gestión de Historias Clínicas"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "reflex>=0.4.0",
    "sqlmodel>=0.0.14",
    "psycopg2-binary>=2.9.9",
    "alembic>=1.13.0",
    "passlib[bcrypt]>=1.7.4",
    "python-dotenv>=1.0.0",
    "email-validator>=2.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
]
pdf = [
    "reportlab>=4.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Línea demasiado larga (ya configurado en line-length)
```

---

## 🚀 Comandos de UV (En lugar de pip/venv)

### Inicialización del Proyecto

```bash
# Crear nuevo proyecto
uv init medical-records
cd medical-records

# Especificar versión de Python
echo "3.13" > .python-version

# UV instalará Python 3.13 automáticamente si no lo tienes
uv python install 3.13

# Verificar versión
uv python pin 3.13
```

### Gestión de Dependencias

```bash
# Agregar dependencia
uv add reflex
uv add sqlmodel
uv add psycopg2-binary
uv add alembic
uv add "passlib[bcrypt]"
uv add python-dotenv
uv add email-validator

# Agregar dependencias de desarrollo
uv add --dev pytest
uv add --dev ruff

# Agregar dependencias opcionales
uv add --optional pdf reportlab

# Instalar todas las dependencias del proyecto
uv sync

# Actualizar dependencias
uv lock --upgrade

# Remover dependencia
uv remove nombre-paquete
```

### Ejecución de Comandos

```bash
# Ejecutar comando en el entorno
uv run reflex init
uv run reflex run

# Ejecutar script Python
uv run python script.py

# Ejecutar Alembic
uv run alembic revision --autogenerate -m "Initial migration"
uv run alembic upgrade head

# Ejecutar tests
uv run pytest

# Ejecutar linter
uv run ruff check .
uv run ruff format .
```

### Ejecutar Directamente (Sin activar entorno)

```bash
# UV crea un entorno virtual automáticamente en .venv
# No necesitas activarlo manualmente, usa 'uv run'

# Pero si prefieres activarlo:
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Entonces puedes ejecutar directamente
reflex run
```

---

## 🔐 Variables de Entorno (.env)

```bash
# Base de Datos
DATABASE_URL=postgresql://user:password@localhost:5432/medical_records_db

# Usuario único
ADMIN_PASSWORD_HASH=hash-generado-con-bcrypt
# Para generar: uv run python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('tu_password'))"

# App
APP_NAME=Historias Clínicas
DEBUG=True
ENVIRONMENT=development

# Backups
BACKUP_ENABLED=True
BACKUP_FREQUENCY_DAYS=7
BACKUP_PATH=./backups
```

---

## 🗃️ Modelos Principales

### 1. Patient (Paciente)

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date

class Patient(SQLModel, table=True):
    """Información del paciente"""
    __tablename__ = "patients"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Datos personales
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    dni: str = Field(unique=True, index=True, max_length=20)
    birth_date: date
    gender: str = Field(max_length=10)  # M, F, Otro
    blood_type: Optional[str] = Field(default=None, max_length=5)
    
    # Contacto
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = None
    
    # Información médica básica
    allergies: Optional[str] = None  # Texto libre
    chronic_conditions: Optional[str] = None  # Texto libre
    family_history: Optional[str] = None  # Texto libre
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)  # Para "eliminar" sin borrar
    
    # Notas generales
    notes: Optional[str] = None
```

### 2. Consultation (Consulta Médica)

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Consultation(SQLModel, table=True):
    """Consulta o visita médica"""
    __tablename__ = "consultations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    
    # Datos de la consulta
    consultation_date: datetime = Field(default_factory=datetime.utcnow)
    reason: str  # Motivo de consulta
    symptoms: Optional[str] = None  # Síntomas
    diagnosis: Optional[str] = None  # Diagnóstico
    treatment: Optional[str] = None  # Tratamiento indicado
    notes: Optional[str] = None  # Notas adicionales
    
    # Signos vitales
    blood_pressure: Optional[str] = Field(default=None, max_length=20)  # ej: "120/80"
    heart_rate: Optional[int] = None  # pulsaciones por minuto
    temperature: Optional[float] = None  # grados celsius
    weight: Optional[float] = None  # kg
    height: Optional[float] = None  # cm
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Próxima visita
    next_visit: Optional[date] = None
```

### 3. Medication (Medicación)

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date

class Medication(SQLModel, table=True):
    """Medicación prescrita"""
    __tablename__ = "medications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    consultation_id: Optional[int] = Field(default=None, foreign_key="consultations.id")
    
    # Medicamento
    name: str = Field(max_length=200)
    dosage: str = Field(max_length=100)  # ej: "500mg"
    frequency: str = Field(max_length=100)  # ej: "cada 8 horas"
    duration: Optional[str] = Field(default=None, max_length=100)  # ej: "7 días"
    
    # Fechas
    start_date: date = Field(default_factory=date.today)
    end_date: Optional[date] = None
    
    # Info adicional
    notes: Optional[str] = None
    is_chronic: bool = Field(default=False)  # Medicación crónica
    is_active: bool = Field(default=True)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 4. Study (Estudios/Análisis) - OPCIONAL

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date

class Study(SQLModel, table=True):
    """Estudios médicos y análisis"""
    __tablename__ = "studies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    consultation_id: Optional[int] = Field(default=None, foreign_key="consultations.id")
    
    # Estudio
    study_type: str = Field(max_length=100)  # Laboratorio, Rx, Eco, etc.
    name: str = Field(max_length=200)  # Nombre del estudio
    study_date: date
    
    # Resultados
    results: Optional[str] = None  # Texto libre
    file_path: Optional[str] = None  # Ruta al archivo PDF/imagen
    
    # Metadata
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 🔐 Autenticación Simplificada (Usuario Único)

### Implementación sin JWT ni complejidad

```python
# app/utils/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña es correcta"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Genera hash de contraseña"""
    return pwd_context.hash(password)
```

```python
# app/state/auth_state.py
import reflex as rx
from app.config import ADMIN_PASSWORD_HASH
from app.utils.security import verify_password

class AuthState(rx.State):
    """Estado de autenticación simple"""
    is_authenticated: bool = False
    login_error: str = ""
    
    def login(self, password: str):
        """Intenta hacer login"""
        if verify_password(password, ADMIN_PASSWORD_HASH):
            self.is_authenticated = True
            self.login_error = ""
            return rx.redirect("/dashboard")
        else:
            self.login_error = "Contraseña incorrecta"
    
    def logout(self):
        """Cierra sesión"""
        self.is_authenticated = False
        return rx.redirect("/login")
    
    def check_auth(self):
        """Verifica si está autenticado (para proteger páginas)"""
        if not self.is_authenticated:
            return rx.redirect("/login")
```

---

## 🎨 Convenciones de UI con Reflex

### Esquema de Colores Médico

```python
COLORS = {
    "primary": "#0066CC",      # Azul médico principal
    "secondary": "#00A896",    # Verde salud
    "danger": "#DC3545",       # Rojo para alertas
    "warning": "#FFC107",      # Amarillo advertencias
    "success": "#28A745",      # Verde éxito
    "info": "#17A2B8",         # Azul información
    "background": "#F8F9FA",   # Fondo claro
    "surface": "#FFFFFF",      # Tarjetas
    "text": "#212529",         # Texto principal
    "text_secondary": "#6C757D",  # Texto secundario
    "border": "#DEE2E6",       # Bordes
}
```

### Estructura de Páginas

Todas las páginas (excepto login) deben tener:
1. **Navbar superior** con nombre del doctor y botón logout
2. **Contenido principal** con padding consistente
3. **Mensajes de feedback** (success/error)

---

## 📊 Prioridades de Desarrollo (SIMPLIFICADAS)

### Fase 1: Funcionalidad Básica ⭐ PRIORITARIO
- [ ] Configuración inicial del proyecto con UV
- [ ] Conexión a PostgreSQL
- [ ] Modelos: Patient, Consultation
- [ ] Login simple (usuario único)
- [ ] Dashboard con estadísticas básicas
- [ ] CRUD de pacientes (crear, ver, editar)
- [ ] Lista de pacientes con búsqueda

### Fase 2: Historia Clínica
- [ ] Vista de detalle de paciente
- [ ] Crear consulta médica
- [ ] Registro de signos vitales
- [ ] Timeline de consultas del paciente
- [ ] Editar/eliminar consultas

### Fase 3: Medicación
- [ ] Modelo Medication
- [ ] Agregar medicamentos a paciente
- [ ] Lista de medicamentos activos
- [ ] Marcar medicamentos como finalizados

### Fase 4: Mejoras
- [ ] Generación de PDF de historia clínica
- [ ] Modelo Study para estudios/análisis
- [ ] Carga de archivos (PDFs, imágenes)
- [ ] Backup automático de BD
- [ ] Estadísticas en dashboard

### Fase 5: Pulido (Opcional)
- [ ] Exportar datos a Excel
- [ ] Gráficos de evolución de peso/presión
- [ ] Recordatorios de próximas visitas
- [ ] Impresión de recetas

---

## ⚠️ Reglas Críticas de Desarrollo

### NUNCA hacer:
- ❌ Commitear archivo `.env` con la contraseña
- ❌ Editar manualmente `uv.lock` (UV lo genera automáticamente)
- ❌ Usar `pip install` (usar `uv add` en su lugar)
- ❌ Eliminar registros directamente de la BD (usar `is_active=False`)
- ❌ Crear tablas manualmente (usar Alembic)
- ❌ Hardcodear datos sensibles

### SIEMPRE hacer:
- ✅ Usar `uv add` para agregar dependencias
- ✅ Commitear `uv.lock` junto con `pyproject.toml`
- ✅ Usar `uv run` para ejecutar comandos
- ✅ Usar type hints (Python 3.13 tiene mejor soporte)
- ✅ Validar inputs (DNI único, emails válidos, etc.)
- ✅ Crear migración antes de cambiar modelos
- ✅ Hacer backup antes de cambios importantes
- ✅ Commitear frecuentemente con mensajes claros
- ✅ Proteger páginas verificando autenticación

---

## 🚀 Comandos Útiles (con UV)

```bash
# ===== PROYECTO =====
# Iniciar proyecto nuevo
uv init medical-records
cd medical-records
echo "3.13" > .python-version
uv python install 3.13

# Instalar dependencias
uv sync

# Agregar nueva dependencia
uv add nombre-paquete

# Actualizar dependencias
uv lock --upgrade

# ===== REFLEX =====
# Inicializar Reflex
uv run reflex init

# Ejecutar app en desarrollo
uv run reflex run

# Modo producción
uv run reflex run --env prod

# ===== BASE DE DATOS =====
# Crear migración
uv run alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
uv run alembic upgrade head

# Revertir última migración
uv run alembic downgrade -1

# Ver historial
uv run alembic history

# ===== UTILIDADES =====
# Generar hash de contraseña
uv run python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('tu_password_aqui'))"

# Ejecutar script custom
uv run python scripts/backup.py

# Formatear código con Ruff
uv run ruff format .

# Linter
uv run ruff check .

# Tests
uv run pytest

# ===== BACKUP POSTGRESQL =====
# Backup manual
pg_dump -U usuario medical_records_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
psql -U usuario medical_records_db < backup_20250118.sql
```

---

## 📝 Commits Convencionales

```
feat(patients): agregar búsqueda por DNI
fix(consultation): corregir validación de fecha
refactor(ui): simplificar formulario de paciente
docs: actualizar instrucciones de instalación
chore(deps): actualizar reflex a 0.4.1
```

---

## 🎯 MVP (Producto Mínimo Viable)

**Lo mínimo funcional para empezar a usar:**

1. Login con contraseña
2. Crear paciente (nombre, DNI, teléfono, fecha nacimiento)
3. Lista de pacientes con búsqueda
4. Ver detalle de paciente
5. Crear consulta con motivo, diagnóstico y notas
6. Ver historial de consultas del paciente

**Todo lo demás puede agregarse después.**

---

## 💾 Estrategia de Backups (IMPORTANTE)

```python
# app/services/backup_service.py
import os
import subprocess
from datetime import datetime
from app.config import DATABASE_URL, BACKUP_PATH

def create_backup() -> str:
    """Crea backup de la base de datos"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.sql"
    filepath = os.path.join(BACKUP_PATH, filename)
    
    # Extraer info de DATABASE_URL
    # postgresql://user:password@host:port/dbname
    
    cmd = f"pg_dump {DATABASE_URL} > {filepath}"
    subprocess.run(cmd, shell=True, check=True)
    
    return filepath

# Llamar automáticamente cada X días o manualmente desde settings
```

---

## 📚 Características de Python 3.13 Aprovechables

```python
# Mejor manejo de tipos genéricos
from typing import Optional

def get_patient(patient_id: int) -> Patient | None:  # Nueva sintaxis
    """Retorna paciente o None"""
    pass

# Mejor performance en general
# Python 3.13 tiene mejoras significativas de velocidad

# Type hints más claros
patients: list[Patient] = []  # En lugar de List[Patient]
patient_dict: dict[int, Patient] = {}  # En lugar de Dict[int, Patient]
```

---

## ✅ Checklist Inicio de Sesión de Desarrollo

```
[ ] UV instalado (uv --version)
[ ] Python 3.13 instalado (uv python install 3.13)
[ ] PostgreSQL corriendo
[ ] Archivo .python-version creado (echo "3.13" > .python-version)
[ ] Dependencias instaladas (uv sync)
[ ] Variables de entorno configuradas (.env)
[ ] Base de datos creada
[ ] Migraciones aplicadas (uv run alembic upgrade head)
[ ] Reflex inicializado (uv run reflex init)
[ ] App corriendo (uv run reflex run)
[ ] Navegador en http://localhost:3000
```

---

## 🎯 Próximos Pasos Inmediatos

1. ✅ Crear INSTRUCTIONS.md (este archivo)
2. ⏳ Inicializar proyecto con UV
3. ⏳ Crear `.python-version` y `pyproject.toml`
4. ⏳ Crear estructura de carpetas
5. ⏳ Configurar `.env` y `.gitignore`
6. ⏳ Instalar dependencias con UV
7. ⏳ Inicializar Reflex
8. ⏳ Configurar PostgreSQL
9. ⏳ Crear modelo Patient
10. ⏳ Crear página de login
11. ⏳ Crear dashboard simple
12. ⏳ Crear CRUD de pacientes

---

## 🔧 Comparación: pip vs UV

| Tarea                     | pip/venv                          | UV                          |
|---------------------------|-----------------------------------|-----------------------------|
| Crear entorno virtual     | `python -m venv .venv`            | Automático                  |
| Activar entorno           | `source .venv/bin/activate`       | No necesario (uv run)       |
| Instalar paquete          | `pip install paquete`             | `uv add paquete`            |
| Instalar desde archivo    | `pip install -r requirements.txt` | `uv sync`                   |
| Ejecutar comando          | `python script.py`                | `uv run python script.py`   |
| Lock de dependencias      | `pip freeze > requirements.txt`   | Automático (uv.lock)        |
| Velocidad instalación     | Lento (~minutos)                  | Rápido (~segundos) ⚡       |

---

## 💬 Notas del Desarrollador

```
2025-01-18: Proyecto iniciado como sistema de usuario único.
            Stack: Python 3.13 + Reflex + PostgreSQL + SQLModel
            Gestor: UV (Astral) para máximo performance
            Decisión de simplicidad sobre escalabilidad.
            
[Tus notas aquí]
```

---

## ✨ Filosofía del Proyecto

> "Simplicidad primero. Funcionalidad esencial antes que features avanzadas."

> "UV hace el desarrollo más rápido. Úsalo."

> "Un sistema usado es mejor que un sistema perfecto sin terminar."

> "Los datos médicos son valiosos: siempre hacer backup, nunca eliminar."

---

## 📚 Recursos

- **UV Docs:** https://docs.astral.sh/uv/
- **Python 3.13:** https://docs.python.org/3.13/
- **Reflex:** https://reflex.dev/docs
- **SQLModel:** https://sqlmodel.tiangolo.com
- **Alembic:** https://alembic.sqlalchemy.org
- **PostgreSQL:** https://www.postgresql.org/docs

---

**Última actualización:** 2025-01-18
**Mantenido por:** @lucianofcabral
**Versión:** 3.0 (Usuario Único + Python 3.13 + UV)