# 🏥 Sistema de Gestión de Historias Clínicas

Sistema web de escritorio para gestión de historias clínicas de un consultorio médico individual.

## 🚀 Stack Tecnológico

- **Python:** 3.13+
- **Framework:** Reflex
- **Base de Datos:** PostgreSQL
- **ORM:** SQLModel
- **Gestor de Paquetes:** UV (Astral)

## 📋 Requisitos Previos

- Python 3.13+
- PostgreSQL 14+
- UV (instalador rápido de paquetes Python)

## 🔧 Instalación

### 1. Instalar UV

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clonar y Configurar

```bash
git clone <tu-repo>
cd hc

# UV instalará Python 3.13 automáticamente si no lo tienes
uv sync
```

### 3. Configurar Base de Datos

```bash
# Crear base de datos PostgreSQL
createdb medical_records_db

# Copiar variables de entorno
cp .env.example .env

# Editar .env con tus credenciales
```

### 4. Generar Contraseña de Admin

```bash
uv run python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('tu_password_aqui'))"
```

Copiar el hash generado a `.env` en `ADMIN_PASSWORD_HASH`

### 5. Inicializar Reflex

```bash
uv run reflex init
```

### 6. Aplicar Migraciones

```bash
uv run alembic upgrade head
```

### 7. Ejecutar la Aplicación

```bash
uv run reflex run
```

Abre tu navegador en: http://localhost:3000

## 📦 Comandos Útiles

```bash
# Agregar nueva dependencia
uv add nombre-paquete

# Ejecutar app
uv run reflex run

# Crear migración
uv run alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
uv run alembic upgrade head

# Formatear código
uv run ruff format .

# Linter
uv run ruff check .
```

## 📁 Estructura del Proyecto

```
hc/
├── app/
│   ├── models/          # Modelos SQLModel
│   ├── pages/           # Páginas Reflex
│   ├── components/      # Componentes UI
│   ├── services/        # Lógica de negocio
│   ├── utils/           # Utilidades
│   └── state/           # Estados Reflex
├── alembic/             # Migraciones
├── backups/             # Backups automáticos
└── pyproject.toml       # Configuración del proyecto
```

## 🔐 Seguridad

- Sistema de usuario único con contraseña hasheada
- Validación de inputs
- Backups automáticos
- Soft delete (no se borran datos físicamente)

## 📚 Documentación

Ver `INSTRUCTIONS.md` para documentación detallada del desarrollo.

## 👨‍💻 Desarrollador

@lucianofcabral

## 📄 Licencia

Proyecto privado de uso personal.
