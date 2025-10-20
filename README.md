# 🏥 Sistema de Gestión de Historias Clínicas

Sistema web de escritorio para gestión de historias clínicas de un consultorio médico individual.

## 🚀 Stack Tecnológico

- **Python:** 3.13+
- **Framework:** Reflex
- **Base de Datos:** PostgreSQL 16 (Docker)
- **ORM:** SQLModel
- **Gestor de Paquetes:** UV (Astral)

## 📋 Requisitos Previos

- Python 3.13+
- Docker y Docker Compose
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
git clone https://github.com/lucianofcabral/historias-clinicas.git
cd hc

# UV instalará Python 3.13 automáticamente si no lo tienes
uv sync
```

### 3. Configurar Base de Datos con Docker

```bash
# Iniciar PostgreSQL y pgAdmin con Docker
docker-compose up -d

# Verificar que los contenedores estén corriendo
docker-compose ps
```

### 4. Configurar Variables de Entorno

```bash
# Copiar variables de entorno de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env  # o el editor de tu preferencia
```

Configurar las siguientes variables en `.env`:
- `ADMIN_PASSWORD_HASH`: Hash de tu contraseña de admin (ver paso 5)
- `DATABASE_URL`: Ya configurado para Docker (no cambiar en desarrollo)
- `SECRET_KEY`: Cambiar en producción

### 5. Generar Contraseña de Admin

```bash
uv run python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('tu_password_aqui'))"
```

Copiar el hash generado a `.env` en `ADMIN_PASSWORD_HASH`

### 6. Inicializar Reflex

```bash
uv run reflex init
```

### 7. Aplicar Migraciones

```bash
uv run alembic upgrade head
```

### 8. Poblar Base de Datos (Opcional - Datos de Prueba)

```bash
uv run python populate_db.py
```

### 9. Ejecutar la Aplicación

```bash
uv run reflex run
```

Abre tu navegador en: http://localhost:3000

## � Comandos Docker

```bash
# Iniciar contenedores
docker-compose up -d

# Detener contenedores
docker-compose down

# Ver logs
docker-compose logs -f postgres

# Backup manual de PostgreSQL
docker exec hc_postgres pg_dump -U hc_user -d historia_clinica -F c > backup.dump

# Restaurar backup
docker exec -i hc_postgres pg_restore -U hc_user -d historia_clinica -c < backup.dump

# Acceder a PostgreSQL CLI
docker exec -it hc_postgres psql -U hc_user -d historia_clinica
```

## 🌐 pgAdmin (Interfaz Web para PostgreSQL)

Acceder a http://localhost:5050

**Credenciales de Login:**
- Email: `admin@example.com`
- Password: `admin`

**Configurar conexión al servidor PostgreSQL:**
1. Click derecho en "Servers" → "Register" → "Server"
2. En pestaña "General": Name = `HC Database`
3. En pestaña "Connection":
   - Host: `postgres` (nombre del servicio Docker)
   - Port: `5432`
   - Database: `historia_clinica`
   - Username: `hc_user`
   - Password: `hc_password_dev_2025`

## �📦 Comandos Útiles

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
├── docker-compose.yml   # Configuración Docker
└── pyproject.toml       # Configuración del proyecto
```

## 🔐 Seguridad

- Sistema de usuario único con contraseña hasheada
- Validación de inputs
- Backups automáticos (compatible con Docker)
- Soft delete (no se borran datos físicamente)
- Base de datos en contenedor Docker con volúmenes persistentes

## 📚 Documentación

- Ver `INSTRUCTIONS.md` para documentación detallada del desarrollo
- Ver `POSTGRESQL_SETUP_GUIDE.md` para configuración de PostgreSQL con Docker
- Ver `PYTHONANYWHERE_DEPLOYMENT_GUIDE.md` para desplegar en PythonAnywhere (GRATIS PERMANENTE, sin tarjeta) ⭐
- Ver `RENDER_DEPLOYMENT_GUIDE.md` para desplegar en Render.com (GRATIS, sin tarjeta, expira 90 días)
- Ver `FLY_DEPLOYMENT_GUIDE.md` para desplegar en Fly.io (requiere tarjeta)

## 🚀 Despliegue en Producción

### Opción 1: PythonAnywhere (RECOMENDADA - Gratis Permanente) ⭐

**✅ La mejor opción para consultorio con poco tráfico**

- ✅ Gratis permanentemente sin tarjeta de crédito
- ✅ MySQL incluido (512MB) - suficiente
- ✅ App siempre activa (no duerme)
- ✅ Sin renovaciones cada 90 días
- ✅ Muy estable

Ver la guía completa en [`PYTHONANYWHERE_DEPLOYMENT_GUIDE.md`](PYTHONANYWHERE_DEPLOYMENT_GUIDE.md)

**Tu app estará en:** `https://tu-usuario.pythonanywhere.com`

---

### Opción 2: Render.com (Gratis, expira 90 días)

**✅ Completamente gratis sin tarjeta de crédito**

Ver la guía completa en [`RENDER_DEPLOYMENT_GUIDE.md`](RENDER_DEPLOYMENT_GUIDE.md)

**Resumen rápido:**
1. Crear cuenta en https://render.com (sin tarjeta)
2. Crear PostgreSQL database (1GB gratis)
3. Crear Web Service desde GitHub
4. Configurar variables de entorno
5. Deploy automático!

**Tu app estará en:** `https://tu-app.onrender.com`

⚠️ **Nota:** En tier gratis, la app "duerme" después de 15 min de inactividad. Primera carga tarda ~1 minuto.

---

### Opción 2: Fly.io (Requiere Tarjeta)

Ver la guía completa en [`FLY_DEPLOYMENT_GUIDE.md`](FLY_DEPLOYMENT_GUIDE.md)

**Resumen rápido:**
```bash
# Instalar Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Crear app y PostgreSQL
fly launch
fly postgres create
fly postgres attach <nombre-postgres>

# Configurar secrets
fly secrets set ADMIN_PASSWORD_HASH="tu_hash"

# Desplegar
fly deploy
```

## 👨‍💻 Desarrollador

@lucianofcabral

## 📄 Licencia

Proyecto privado de uso personal.
