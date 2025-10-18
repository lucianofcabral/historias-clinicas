# Sistema de Backups

## Descripción

El sistema de backups es compatible con **SQLite** (desarrollo) y **PostgreSQL** (producción), detectando automáticamente qué base de datos está en uso.

## Características

### Detección Automática
El sistema detecta automáticamente el tipo de base de datos:
- Lee `DATABASE_URL` desde `app/config.py`
- Si comienza con `postgresql://`, usa estrategia PostgreSQL
- En caso contrario, usa estrategia SQLite

### SQLite (Desarrollo)
**Backup:**
- Copia el archivo `medical_records.db`
- Comprime en formato ZIP
- Almacena en `backups/backup_YYYYMMDD_HHMMSS.zip`

**Restore:**
- Crea backup de seguridad de la DB actual
- Extrae el archivo `.db` del ZIP
- Reemplaza la base de datos actual
- Requiere reinicio de la aplicación

### PostgreSQL (Producción)
**Backup:**
- Usa `pg_dump` con formato custom (comprimido)
- Genera archivo `.sql`
- Comprime en formato ZIP
- Almacena en `backups/backup_YYYYMMDD_HHMMSS.zip`

**Restore:**
- Usa `pg_restore` para restaurar el dump
- DROP y CREATE de la base de datos
- Restauración completa con `-c` (clean)
- Requiere reinicio de la aplicación

## Requisitos

### SQLite
- Python con módulo `sqlite3` (incluido por defecto)
- Permisos de lectura/escritura en el directorio del proyecto

### PostgreSQL
Debe tener instalados en el servidor:
- `pg_dump` (incluido en instalación de PostgreSQL)
- `pg_restore` (incluido en instalación de PostgreSQL)
- `psql` (para operaciones DROP/CREATE)

**Instalación en Ubuntu/Debian:**
```bash
sudo apt-get install postgresql-client
```

**Instalación en CentOS/RHEL:**
```bash
sudo yum install postgresql
```

## Configuración

### Variables de Entorno

Asegúrate de configurar correctamente `DATABASE_URL` en tu archivo `.env`:

**Desarrollo (SQLite):**
```env
# Dejar vacío o comentado para usar SQLite
# DATABASE_URL=
```

**Producción (PostgreSQL):**
```env
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_db
```

Ejemplo:
```env
DATABASE_URL=postgresql://medical_user:SecurePass123@localhost:5432/medical_records_db
```

## Uso desde la Interfaz

1. Ve a **Configuración** desde el menú de navegación
2. En la sección de **Backups**:
   - **Crear Backup:** Haz clic en "Crear Backup Ahora"
   - **Restaurar:** Haz clic en el botón "Restaurar" del backup deseado
   - **Eliminar:** Haz clic en el botón "Eliminar" del backup que quieras borrar

### Estadísticas

La página muestra:
- Número total de backups
- Espacio total ocupado
- Ruta del directorio de backups

## Seguridad

### Permisos
- El directorio `backups/` debe tener permisos de lectura/escritura
- Los archivos de backup son comprimidos en formato ZIP
- **NO** commitear backups al repositorio (`.gitignore` configurado)

### Backup de Seguridad (SQLite)
Antes de restaurar, se crea automáticamente un backup de seguridad:
- Formato: `pre_restore_YYYYMMDD_HHMMSS.db`
- Permite recuperación en caso de problemas

### PostgreSQL - Credenciales
- La contraseña se pasa mediante variable de entorno `PGPASSWORD`
- No queda registrada en logs ni historial de comandos

## Estructura de Archivos

```
backups/
├── .gitkeep                    # Para versionar el directorio vacío
├── backup_20251018_120000.zip # Backup ejemplo
└── pre_restore_*.db            # Backups de seguridad automáticos (SQLite)
```

### Formato ZIP
Cada ZIP contiene:
- **SQLite:** `backup_YYYYMMDD_HHMMSS.db`
- **PostgreSQL:** `backup_YYYYMMDD_HHMMSS.sql`

## Limitaciones Conocidas

### SQLite
- La aplicación debe reiniciarse después de restaurar
- No soporta restauración en caliente
- Backup mientras la app está corriendo puede causar inconsistencias (considerar usar `PRAGMA wal_checkpoint`)

### PostgreSQL
- Requiere herramientas PostgreSQL instaladas en el servidor
- El usuario de PostgreSQL debe tener permisos para DROP/CREATE database
- La restauración desconecta todas las conexiones activas
- Requiere reinicio de la aplicación

## Mejoras Futuras

- [ ] Backups automáticos programados (cron/scheduler)
- [ ] Retención de backups (eliminar automáticamente backups antiguos)
- [ ] Notificaciones por email al crear/restaurar backups
- [ ] Verificación de integridad de backups
- [ ] Backups incrementales
- [ ] Cifrado de backups
- [ ] Subida automática a cloud storage (S3, Google Cloud Storage)

## Troubleshooting

### Error: "La base de datos no existe" (SQLite)
- Verifica que existe el archivo `medical_records.db` en el directorio raíz
- Revisa permisos de lectura en el archivo

### Error: "pg_dump: command not found"
- Instala PostgreSQL client tools
- Verifica que `pg_dump` esté en el PATH

### Error: "Error en pg_dump: FATAL: password authentication failed"
- Verifica credenciales en `DATABASE_URL`
- Asegúrate que el usuario tiene permisos en la base de datos
- Revisa configuración de `pg_hba.conf` en el servidor PostgreSQL

### Error: "Cannot restore backup" (PostgreSQL)
- Verifica que el usuario tenga permisos CREATEDB
- Asegúrate que no hay conexiones activas a la base de datos
- Revisa logs de PostgreSQL: `/var/log/postgresql/`

## Código Relevante

### Archivos del Sistema
- `app/services/backup_service.py` - Lógica principal
- `app/state/settings_state.py` - Estado UI
- `app/pages/settings.py` - Interfaz de usuario
- `backups/` - Directorio de almacenamiento

### Métodos Principales

```python
BackupService.get_db_type()          # Detecta SQLite o PostgreSQL
BackupService.create_backup()        # Crea backup
BackupService.restore_backup(file)   # Restaura backup
BackupService.list_backups()         # Lista backups disponibles
BackupService.delete_backup(file)    # Elimina backup
BackupService.get_backup_stats()     # Estadísticas
```

## Contacto

Para reportar bugs o sugerencias relacionadas con el sistema de backups, crea un issue en el repositorio.
