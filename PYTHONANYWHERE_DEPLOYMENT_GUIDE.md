# 🐍 Guía de Despliegue en PythonAnywhere

Esta guía te ayudará a desplegar la aplicación de Historias Clínicas en PythonAnywhere **GRATIS PERMANENTEMENTE** sin tarjeta de crédito.

## ✨ ¿Por qué PythonAnywhere?

- ✅ **Completamente gratis sin tarjeta de crédito**
- ✅ **Gratis PERMANENTEMENTE** (sin renovaciones cada 90 días)
- ✅ **MySQL incluido** (512MB - suficiente para consultorio)
- ✅ **App siempre activa** (no duerme como Render)
- ✅ **SSL/HTTPS gratuito**
- ✅ **Dominio incluido:** `tu-usuario.pythonanywhere.com`
- ✅ **Muy estable** (usado por miles de apps Python)

## 📋 Limitaciones del Tier Gratuito

- CPU: 100 segundos/día (suficiente para consultorio)
- MySQL: 512MB
- Almacenamiento: 512MB
- Ancho de banda: Ilimitado
- Solo Python 3.10 (no 3.13, pero funciona perfecto)

---

## 🚀 Paso a Paso del Despliegue

### 1. Crear Cuenta en PythonAnywhere

1. Ir a https://www.pythonanywhere.com
2. Click en **"Pricing & signup"**
3. Seleccionar **"Create a Beginner account"** (GRATIS)
4. Registrarse con email (sin tarjeta de crédito)
5. Verificar email
6. Login en https://www.pythonanywhere.com

---

### 2. Crear Base de Datos MySQL

1. En el dashboard, ir a pestaña **"Databases"**
2. En la sección **"MySQL"**:
   - Ver tu **MySQL hostname** (algo como `tu-usuario.mysql.pythonanywhere-services.com`)
   - Crear una **contraseña para MySQL** (guardarla)
3. En **"Create database"**:
   - Database name: `tu-usuario$historia_clinica`
   - Click **"Create"**
4. **Guardar estas credenciales:**
   ```
   Host: tu-usuario.mysql.pythonanywhere-services.com
   Database: tu-usuario$historia_clinica
   User: tu-usuario
   Password: [la que acabas de crear]
   ```

---

### 3. Clonar Repositorio

1. En el dashboard, ir a pestaña **"Consoles"**
2. Click en **"Bash"** para abrir una consola
3. En la consola, ejecutar:

```bash
# Clonar tu repositorio
git clone https://github.com/lucianofcabral/historias-clinicas.git
cd historias-clinicas

# Verificar que se clonó correctamente
ls -la
```

---

### 4. Crear Virtualenv e Instalar Dependencias

```bash
# Crear virtualenv con Python 3.10
mkvirtualenv --python=/usr/bin/python3.10 hc-env

# Activar virtualenv (si no está activado)
workon hc-env

# Instalar UV
pip install uv

# Instalar dependencias
uv sync

# Instalar mysqlclient (driver de MySQL)
pip install mysqlclient
```

---

### 5. Configurar Variables de Entorno

```bash
# Crear archivo .env
nano .env
```

Pegar este contenido (reemplaza con tus datos):

```bash
# Database MySQL en PythonAnywhere
DATABASE_TYPE=mysql
DB_HOST=tu-usuario.mysql.pythonanywhere-services.com
DB_PORT=3306
DB_NAME=tu-usuario$historia_clinica
DB_USER=tu-usuario
DB_PASSWORD=tu-mysql-password
DATABASE_URL=mysql://tu-usuario:tu-mysql-password@tu-usuario.mysql.pythonanywhere-services.com/tu-usuario$historia_clinica

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=hash-generado-aqui

# App
APP_ENV=production
PORT=8000
SECRET_KEY=secret-key-generado-aqui

# Backup
BACKUP_DIR=backups
```

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### 6. Generar Contraseña de Admin

En la consola bash:

```bash
# Activar virtualenv
workon hc-env

# Generar hash
python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('TU_PASSWORD_AQUI'))"
```

Copiar el hash y actualizar `.env`:

```bash
nano .env
# Pegar el hash en ADMIN_PASSWORD_HASH
# Guardar: Ctrl+O, Enter, Ctrl+X
```

---

### 7. Generar Secret Key

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copiar y actualizar `SECRET_KEY` en `.env`

---

### 8. Ejecutar Migraciones

```bash
# Asegurar que virtualenv está activo
workon hc-env

# Ejecutar migraciones
uv run alembic upgrade head

# Verificar que las tablas se crearon
mysql -u tu-usuario -h tu-usuario.mysql.pythonanywhere-services.com -p tu-usuario\$historia_clinica

# En MySQL prompt:
SHOW TABLES;
# Deberías ver: patients, consultations, medical_studies, etc.
# Salir: exit
```

---

### 9. Configurar Web App

1. Ir a pestaña **"Web"** en PythonAnywhere dashboard
2. Click en **"Add a new web app"**
3. Seleccionar **"Manual configuration"**
4. Seleccionar **"Python 3.10"**
5. Click **"Next"**

---

### 10. Configurar WSGI

1. En la página de configuración de tu web app
2. En la sección **"Code"**, click en el link del **WSGI configuration file**
3. **Borrar todo** el contenido del archivo
4. Pegar este código:

```python
import sys
import os

# Agregar el directorio del proyecto al path
path = '/home/tu-usuario/historias-clinicas'
if path not in sys.path:
    sys.path.insert(0, path)

# Cargar variables de entorno
from dotenv import load_dotenv
env_path = os.path.join(path, '.env')
load_dotenv(env_path)

# Importar la app de Reflex
from app.app import app as application
```

**Reemplaza `tu-usuario`** con tu username de PythonAnywhere.

**Guardar:** Click en botón verde "Save"

---

### 11. Configurar Virtualenv

1. Volver a la página de configuración de tu web app
2. En la sección **"Virtualenv"**:
3. En **"Enter path to a virtualenv"**, pegar:
   ```
   /home/tu-usuario/.virtualenvs/hc-env
   ```
   (reemplaza `tu-usuario`)
4. Click en el ✓ (check) para guardar

---

### 12. Configurar Archivos Estáticos

En la sección **"Static files"**, agregar:

| URL | Directory |
|-----|-----------|
| `/assets/` | `/home/tu-usuario/historias-clinicas/assets/` |
| `/.web/` | `/home/tu-usuario/historias-clinicas/.web/` |

(reemplaza `tu-usuario`)

---

### 13. Inicializar Reflex

Volver a la consola Bash:

```bash
cd ~/historias-clinicas
workon hc-env

# Inicializar Reflex (genera archivos estáticos)
uv run reflex init

# Exportar frontend
uv run reflex export --frontend-only
```

---

### 14. Recargar Web App

1. Volver a la pestaña **"Web"**
2. Scroll hasta arriba
3. Click en el botón verde **"Reload tu-usuario.pythonanywhere.com"**
4. Esperar 10-20 segundos

---

### 15. ¡Acceder a tu App!

Tu app estará disponible en:
```
https://tu-usuario.pythonanywhere.com
```

**Login:**
- Username: `admin`
- Password: [la que configuraste]

---

## 🔧 Comandos Útiles

### Ver Logs de Errores

```bash
# Logs de error de la web app
less /var/log/tu-usuario.pythonanywhere.com.error.log

# Logs de acceso
less /var/log/tu-usuario.pythonanywhere.com.access.log

# Ver últimas líneas
tail -50 /var/log/tu-usuario.pythonanywhere.com.error.log
```

### Actualizar la Aplicación

```bash
cd ~/historias-clinicas
workon hc-env

# Pull de GitHub
git pull origin main

# Instalar nuevas dependencias (si las hay)
uv sync

# Ejecutar nuevas migraciones (si las hay)
uv run alembic upgrade head

# Re-exportar frontend (si hay cambios en UI)
uv run reflex export --frontend-only

# Recargar web app desde la consola
touch /var/www/tu-usuario_pythonanywhere_com_wsgi.py
```

O ir a pestaña "Web" y click en "Reload"

### Ejecutar Migraciones

```bash
cd ~/historias-clinicas
workon hc-env
uv run alembic upgrade head
```

### Conectar a MySQL

```bash
mysql -u tu-usuario -h tu-usuario.mysql.pythonanywhere-services.com -p
# Ingresar password
# USE tu-usuario$historia_clinica;
# SHOW TABLES;
```

---

## 🐛 Troubleshooting

### Error 502 Bad Gateway

1. Ver logs de error:
   ```bash
   tail -50 /var/log/tu-usuario.pythonanywhere.com.error.log
   ```
2. Verificar que virtualenv esté configurado correctamente
3. Verificar que WSGI apunte al directorio correcto
4. Recargar web app

### Error de importación

1. Verificar que todas las dependencias estén instaladas:
   ```bash
   workon hc-env
   pip list
   ```
2. Reinstalar si es necesario:
   ```bash
   uv sync
   ```

### Error de conexión a MySQL

1. Verificar credenciales en `.env`
2. Verificar que DATABASE_URL tenga formato:
   ```
   mysql://usuario:pass@host/base$datos
   ```
3. Probar conexión:
   ```bash
   mysql -u tu-usuario -h host -p
   ```

### Cambios no se reflejan

1. Recargar web app en pestaña "Web"
2. O tocar el WSGI file:
   ```bash
   touch /var/www/tu-usuario_pythonanywhere_com_wsgi.py
   ```
3. Limpiar cache del navegador (Ctrl+Shift+R)

---

## 📊 Monitoreo

### CPU Usage

- Pestaña "Account" → Ver "CPU seconds used today"
- Límite: 100 segundos/día
- Para consultorio con poco tráfico: suficiente

### Database Size

```bash
mysql -u tu-usuario -h host -p

# En MySQL:
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.TABLES
WHERE table_schema = 'tu-usuario$historia_clinica'
GROUP BY table_schema;
```

---

## 🔐 Seguridad

### 1. Contraseñas Fuertes

- MySQL password: usar contraseña segura
- ADMIN_PASSWORD_HASH: contraseña fuerte diferente a desarrollo

### 2. HTTPS

PythonAnywhere proporciona HTTPS automáticamente en:
```
https://tu-usuario.pythonanywhere.com
```

### 3. Backups

**Backup de MySQL:**

```bash
# Desde consola bash
mysqldump -u tu-usuario -h host -p tu-usuario\$historia_clinica > backup_$(date +%Y%m%d).sql

# Comprimir
gzip backup_*.sql

# Descargar desde "Files" tab
```

**Restaurar backup:**

```bash
mysql -u tu-usuario -h host -p tu-usuario\$historia_clinica < backup.sql
```

---

## 💡 Tips

### 1. Mantener App Activa

PythonAnywhere no "duerme" apps en tier gratuito, siempre están activas.

### 2. Dominio Personalizado

Tier gratuito no soporta dominio personalizado. Necesitas actualizar a plan pago ($5/mes) para:
- Dominio propio
- Más CPU
- Más almacenamiento

### 3. Consolas

Puedes tener hasta 2 consolas Bash abiertas simultáneamente en tier gratuito.

### 4. Tareas Programadas

Tier gratuito no soporta scheduled tasks. Para backups automáticos necesitas plan pago.

---

## 📚 Recursos

- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [PythonAnywhere Forums](https://www.pythonanywhere.com/forums/)
- [Deploying Web Apps Guide](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)

---

## 🎯 Checklist Final

Antes de considerar el deploy completo:

- [ ] MySQL database creada
- [ ] Repositorio clonado
- [ ] Virtualenv creado e instalado dependencias
- [ ] Archivo `.env` configurado con credenciales correctas
- [ ] Migraciones ejecutadas (tablas creadas)
- [ ] WSGI configurado correctamente
- [ ] Virtualenv configurado en web app
- [ ] Archivos estáticos configurados
- [ ] Reflex inicializado y exportado
- [ ] Web app recargada
- [ ] Puedes acceder a la app
- [ ] Puedes hacer login con admin

---

**¡Listo!** Tu app estará disponible en `https://tu-usuario.pythonanywhere.com` **permanentemente gratis**.
