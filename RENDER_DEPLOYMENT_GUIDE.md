# 🎨 Guía de Despliegue en Render.com

Esta guía te ayudará a desplegar la aplicación de Historias Clínicas en Render.com **GRATIS y SIN tarjeta de crédito**.

## ✨ ¿Por qué Render?

- ✅ **Completamente gratis sin tarjeta de crédito**
- ✅ **PostgreSQL incluido (1GB)**
- ✅ **Deploy automático desde GitHub**
- ✅ **SSL/HTTPS gratuito**
- ✅ **Muy fácil de configurar**

## ⚠️ Limitación del Tier Gratuito

- La app "duerme" después de **15 minutos de inactividad**
- Tarda **~1 minuto en despertar** en la primera petición
- Después funciona normal
- **Solución:** Usar [UptimeRobot](https://uptimerobot.com/) (gratis) para hacer ping cada 5 min

## 🚀 Pasos para Desplegar

### 1. Crear Cuenta en Render

1. Ir a https://render.com
2. Click en **"Get Started for Free"**
3. Registrarse con GitHub (recomendado) o email
4. **NO requiere tarjeta de crédito** ✨

### 2. Crear PostgreSQL Database

1. En el dashboard de Render, click en **"New +"**
2. Seleccionar **"PostgreSQL"**
3. Configurar:
   - **Name:** `hc-postgres`
   - **Database:** `historia_clinica`
   - **User:** `hc_user`
   - **Region:** Oregon (US West) o Frankfurt (EU) - el más cercano
   - **PostgreSQL Version:** 16
   - **Plan:** **Free** (1GB, suficiente para consultorio)
4. Click en **"Create Database"**
5. **Esperar 2-3 minutos** mientras se crea
6. **Guardar las credenciales** que aparecen:
   - Internal Database URL
   - External Database URL
   - Username
   - Password

### 3. Crear Web Service

1. Click en **"New +"** → **"Web Service"**
2. Seleccionar **"Build and deploy from a Git repository"**
3. Click en **"Connect account"** si es primera vez
4. Buscar tu repositorio: **`historias-clinicas`**
5. Click en **"Connect"**

### 4. Configurar Web Service

**Configuración básica:**
- **Name:** `hc-app` (o el que prefieras)
- **Region:** Oregon o Frankfurt (mismo que la DB)
- **Branch:** `main`
- **Runtime:** Python 3
- **Build Command:** `./build.sh`
- **Start Command:** `uv run reflex run --env prod --loglevel info`

**Plan:**
- Seleccionar **"Free"** (750 horas/mes)

### 5. Configurar Variables de Entorno

En la sección **"Environment"**, agregar estas variables:

```bash
# Python
PYTHON_VERSION = 3.13.0

# App Config
APP_ENV = production
PORT = 8000
ADMIN_USERNAME = admin

# Database (copiar desde tu PostgreSQL)
DATABASE_URL = [copiar Internal Database URL de tu PostgreSQL]

# Admin Password - Generar hash primero
ADMIN_PASSWORD_HASH = [ver paso 6]

# Secret Key - Generar uno aleatorio
SECRET_KEY = [generar uno aleatorio]
```

### 6. Generar Hash de Contraseña

**En tu terminal local:**

```bash
python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('TU_PASSWORD_AQUI'))"
```

Copiar el hash generado y pegarlo en `ADMIN_PASSWORD_HASH`

### 7. Generar Secret Key

**Opción 1 - En Linux/Mac:**
```bash
openssl rand -hex 32
```

**Opción 2 - En Python:**
```python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copiar y pegar en `SECRET_KEY`

### 8. Desplegar

1. Click en **"Create Web Service"**
2. Render automáticamente:
   - Clonará tu repositorio
   - Ejecutará `build.sh`
   - Instalará dependencias con UV
   - Ejecutará migraciones de Alembic
   - Iniciará la aplicación

3. **Esperar 5-10 minutos** para el primer deploy

### 9. Verificar Deploy

**Ver logs en tiempo real:**
- En el dashboard, ir a la pestaña **"Logs"**
- Buscar mensajes como:
  ```
  ✅ Build completado!
  🌐 Iniciando servidor Reflex...
  App running at: http://0.0.0.0:8000
  ```

**Verificar estado:**
- En la pestaña **"Events"** debería aparecer "Deploy live"
- Estado: 🟢 **Live**

### 10. Acceder a la Aplicación

Tu app estará disponible en:
```
https://hc-app.onrender.com
```
(o el nombre que elegiste)

**Primera carga puede tardar ~1 minuto** (tier gratis)

---

## 🔧 Configuración Post-Deploy

### Conectar PostgreSQL Manualmente (si no usaste render.yaml)

Si creaste la DB por separado:

1. Ir a tu Web Service
2. **Environment** → **Add Environment Variable**
3. Agregar:
   ```
   DATABASE_URL = [copiar Internal Database URL]
   ```
4. Guardar → Render redesplegará automáticamente

### Configurar Auto-Deploy desde GitHub

1. En tu Web Service, ir a **"Settings"**
2. En **"Build & Deploy"**:
   - ✅ **Auto-Deploy:** Yes
   - **Branch:** main
3. Ahora cada `git push` desplegará automáticamente

---

## 🔄 Actualizar la Aplicación

### Después de hacer cambios:

```bash
git add .
git commit -m "Actualización"
git push origin main
```

Render detectará el cambio y redesplegará automáticamente.

**Ver progreso:**
- Dashboard → "Events"
- Logs en tiempo real

---

## 🛠️ Comandos Útiles

### Ver Logs en Tiempo Real

Dashboard → Tu Service → **"Logs"**

### Ejecutar Migraciones Manualmente

1. Dashboard → Tu Service → **"Shell"**
2. Click en **"Launch Shell"**
3. Ejecutar:
   ```bash
   uv run alembic upgrade head
   ```

### Conectar a PostgreSQL

**Opción 1 - Desde Shell de Render:**
```bash
psql $DATABASE_URL
```

**Opción 2 - Desde tu computadora:**
```bash
# Usar External Database URL
psql [External Database URL copiado del dashboard]
```

### Reiniciar Servicio

Dashboard → Tu Service → **"Manual Deploy"** → **"Clear build cache & deploy"**

---

## 🐛 Troubleshooting

### La app no inicia

1. **Ver logs:** Dashboard → Logs
2. **Buscar errores de:**
   - Dependencias faltantes
   - Error de conexión a DB
   - Variables de entorno incorrectas

### Error de conexión a PostgreSQL

1. Verificar que `DATABASE_URL` esté correctamente configurado
2. Usar **Internal Database URL** (no External)
3. Verificar que empiece con `postgresql://` (Render lo convierte automático)

### Migraciones no se ejecutan

1. Ir a **Shell**
2. Ejecutar manualmente:
   ```bash
   uv run alembic upgrade head
   ```
3. Ver errores en output

### Build falla

1. Verificar que `build.sh` tenga permisos:
   ```bash
   chmod +x build.sh
   git add build.sh
   git commit -m "Add execute permission to build.sh"
   git push
   ```

### App muy lenta al cargar

Es normal en tier gratis:
- Primera carga después de 15 min: **~1 minuto**
- Cargas subsecuentes: **Rápidas**

**Solución - Mantener app despierta:**
1. Ir a https://uptimerobot.com (gratis)
2. Crear cuenta
3. Agregar monitor:
   - Type: HTTP(s)
   - URL: `https://tu-app.onrender.com`
   - Monitoring Interval: 5 minutos
4. La app nunca dormirá (UptimeRobot hace ping cada 5 min)

---

## 🔐 Seguridad en Producción

### 1. Cambiar Contraseñas

En producción, usar contraseñas **diferentes** a desarrollo:
- Nuevo `ADMIN_PASSWORD_HASH`
- Nuevo `SECRET_KEY`

### 2. HTTPS Automático

Render proporciona SSL/HTTPS gratis automáticamente.

### 3. Backups de PostgreSQL

**Render hace backups automáticos**, pero puedes hacer manuales:

1. Dashboard → PostgreSQL → **"Backups"**
2. Click en **"Create Backup"**

**Restaurar backup:**
1. Dashboard → Backups → Seleccionar backup
2. Click en **"Restore"**

### 4. Variables de Entorno Sensibles

- Las variables en Render están encriptadas
- No se muestran en logs
- Solo accesibles por la app

---

## 📊 Monitoreo

### Métricas Disponibles

Dashboard → Tu Service → **"Metrics"**:
- CPU usage
- Memory usage
- Response times
- Request count

### Logs

- Tiempo real en el dashboard
- Se guardan últimas 7 días (tier gratis)

### Notificaciones

Configurar en **Settings** → **"Notifications"**:
- Email cuando deploy falla
- Email cuando servicio está down

---

## 💰 Límites del Tier Gratuito

| Recurso | Límite |
|---------|--------|
| Web Services | 750 horas/mes |
| PostgreSQL | 1GB almacenamiento |
| Bandwidth | 100GB/mes |
| Build Time | Compartido |
| Sleep después de | 15 min inactividad |
| SSL/HTTPS | ✅ Incluido |
| Custom Domain | ✅ Soportado |

**Perfecto para consultorio con poco tráfico!**

---

## 🎯 Checklist Final

Antes de considerarlo "en producción":

- [ ] Web Service desplegado y funcionando
- [ ] PostgreSQL conectado correctamente
- [ ] Puedes hacer login con admin
- [ ] Probaste crear un paciente de prueba
- [ ] Configuraste UptimeRobot para mantenerla despierta
- [ ] Configuraste notificaciones por email
- [ ] Guardaste las credenciales de DB en lugar seguro

---

## 📚 Recursos

- [Render Docs](https://render.com/docs)
- [Render PostgreSQL Docs](https://render.com/docs/databases)
- [Reflex Deployment Guide](https://reflex.dev/docs/hosting/self-hosting/)
- [UptimeRobot](https://uptimerobot.com/)

---

## 🆘 Soporte

Si tienes problemas:
1. Revisar logs en el dashboard
2. Consultar [Render Community](https://community.render.com/)
3. Ver documentación de Render

---

**¡Listo!** Tu aplicación estará disponible en `https://hc-app.onrender.com` (o el nombre que elegiste).

**Primer acceso puede tardar ~1 minuto** (es normal en tier gratis).
