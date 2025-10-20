# 🚀 Guía de Despliegue en Fly.io

Esta guía te ayudará a desplegar la aplicación de Historias Clínicas en Fly.io completamente **gratis**.

## 📋 Requisitos Previos

- Cuenta en Fly.io (gratis)
- Tarjeta de crédito para verificación (no se cobra, es solo validación)
- flyctl CLI instalado

## 🔧 Instalación de Fly CLI

### Linux/macOS
```bash
curl -L https://fly.io/install.sh | sh
```

### Windows (PowerShell)
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

Agrega Fly a tu PATH:
```bash
# Linux/macOS (agregar a ~/.bashrc o ~/.zshrc)
export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

## 🚀 Paso a Paso del Despliegue

### 1. Autenticación

```bash
# Crear cuenta o hacer login
fly auth signup  # Para nueva cuenta
# O
fly auth login   # Si ya tienes cuenta
```

### 2. Crear Aplicación

```bash
cd /ruta/a/tu/proyecto/hc

# Lanzar aplicación (seguir prompts interactivos)
fly launch

# Respuestas sugeridas:
# - App Name: hc-app (o el que prefieras)
# - Region: gru (São Paulo - más cercano)
# - PostgreSQL: NO (lo crearemos después)
# - Redis: NO
# - Deploy now: NO (configuraremos primero)
```

### 3. Crear Base de Datos PostgreSQL

```bash
# Crear PostgreSQL (GRATIS - 3GB)
fly postgres create

# Respuestas sugeridas:
# - App Name: hc-postgres
# - Region: gru (misma que la app)
# - Configuration: Development (gratis)
# - Scale: 1 (gratis)
```

**Guarda las credenciales que aparecen en pantalla:**
- Username
- Password
- Hostname
- Database name

### 4. Conectar PostgreSQL a la App

```bash
# Adjuntar PostgreSQL a la aplicación
fly postgres attach hc-postgres -a hc-app

# Esto creará automáticamente la variable DATABASE_URL
```

### 5. Configurar Variables de Entorno (Secrets)

```bash
# Generar hash de contraseña de admin
python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('TU_PASSWORD_AQUI'))"

# Configurar secrets
fly secrets set ADMIN_USERNAME=admin -a hc-app
fly secrets set ADMIN_PASSWORD_HASH="EL_HASH_GENERADO" -a hc-app
fly secrets set SECRET_KEY="$(openssl rand -hex 32)" -a hc-app
fly secrets set APP_ENV=production -a hc-app

# Verificar secrets
fly secrets list -a hc-app
```

### 6. Desplegar

```bash
# Desplegar aplicación
fly deploy

# Ver logs en tiempo real
fly logs -a hc-app
```

### 7. Abrir Aplicación

```bash
# Abrir en el navegador
fly open -a hc-app

# O ver la URL
fly status -a hc-app
```

## 🔍 Comandos Útiles

### Logs
```bash
# Ver logs en tiempo real
fly logs -a hc-app

# Ver últimos logs
fly logs -a hc-app --limit 100
```

### SSH a la Aplicación
```bash
# Conectar por SSH
fly ssh console -a hc-app

# Ejecutar migraciones manualmente
fly ssh console -a hc-app -C "uv run alembic upgrade head"
```

### PostgreSQL
```bash
# Conectar a PostgreSQL
fly postgres connect -a hc-postgres

# Ver info de PostgreSQL
fly postgres db list -a hc-postgres

# Backup de PostgreSQL
fly postgres backup create -a hc-postgres
fly postgres backup list -a hc-postgres
```

### Escalar (Cambiar Recursos)
```bash
# Ver configuración actual
fly scale show -a hc-app

# Cambiar memoria (opciones gratis: 256mb)
fly scale memory 256 -a hc-app

# Cambiar cantidad de VMs (máximo 3 gratis)
fly scale count 1 -a hc-app
```

### Actualizar Aplicación
```bash
# Después de hacer cambios en el código
git add .
git commit -m "Actualización"
git push

# Redesplegar
fly deploy -a hc-app
```

### Detener/Reiniciar
```bash
# Detener aplicación (ahorra recursos)
fly apps stop hc-app

# Reiniciar
fly apps restart hc-app

# Ver estado
fly status -a hc-app
```

## 🐛 Troubleshooting

### La app no inicia
```bash
# Ver logs detallados
fly logs -a hc-app

# Verificar health checks
fly checks list -a hc-app

# Reiniciar
fly apps restart hc-app
```

### Error de conexión a PostgreSQL
```bash
# Verificar que PostgreSQL está adjunto
fly postgres attach hc-postgres -a hc-app

# Verificar variable DATABASE_URL
fly secrets list -a hc-app

# Conectar manualmente para probar
fly postgres connect -a hc-postgres
```

### Migraciones no se ejecutan
```bash
# Ejecutar manualmente
fly ssh console -a hc-app -C "uv run alembic upgrade head"

# Ver historial de migraciones
fly ssh console -a hc-app -C "uv run alembic current"
```

## 💰 Límites del Tier Gratuito

- **Compute:** 3 VMs compartidas (256MB RAM cada una)
- **PostgreSQL:** 3GB de almacenamiento, 1 base de datos
- **Ancho de banda:** 100GB/mes saliente
- **Certificados SSL:** Incluidos gratis

**Perfecto para tu consultorio con tráfico bajo!**

## 🔐 Seguridad en Producción

1. **Cambiar contraseñas:**
   - Generar nuevo `ADMIN_PASSWORD_HASH` diferente al de desarrollo
   - Usar contraseña fuerte para PostgreSQL

2. **HTTPS automático:**
   - Fly.io proporciona certificados SSL gratis
   - Se configura automáticamente

3. **Backups:**
   ```bash
   # Configurar backups automáticos de PostgreSQL
   fly postgres backup create -a hc-postgres
   ```

4. **Monitoreo:**
   ```bash
   # Ver métricas
   fly dashboard -a hc-app
   ```

## 📚 Documentación Oficial

- [Fly.io Docs](https://fly.io/docs/)
- [PostgreSQL en Fly.io](https://fly.io/docs/postgres/)
- [CLI Reference](https://fly.io/docs/flyctl/)

## 🆘 Soporte

Si tienes problemas:
1. Revisar logs: `fly logs -a hc-app`
2. Consultar [Fly.io Community](https://community.fly.io/)
3. Documentación de Reflex: https://reflex.dev/docs/hosting/self-hosting/

---

**¡Listo!** Tu aplicación estará disponible en `https://hc-app.fly.dev` (o el nombre que elegiste).
