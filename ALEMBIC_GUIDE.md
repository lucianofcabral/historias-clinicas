# 📚 Guía de Comandos de Alembic

## 🔧 Comandos Básicos

### Ver estado actual de las migraciones
```bash
uv run alembic current
```

### Ver historial de migraciones
```bash
uv run alembic history --verbose
```

### Crear una nueva migración (autogenerar desde modelos)
```bash
uv run alembic revision --autogenerate -m "descripción del cambio"
```

### Aplicar todas las migraciones pendientes
```bash
uv run alembic upgrade head
```

### Revertir última migración
```bash
uv run alembic downgrade -1
```

### Revertir a una migración específica
```bash
uv run alembic downgrade <revision_id>
```

### Revertir todas las migraciones
```bash
uv run alembic downgrade base
```

## 🎯 Flujo de Trabajo Típico

### 1. Modificar un modelo
Edita archivos en `app/models/`

### 2. Crear migración
```bash
uv run alembic revision --autogenerate -m "add email field to patients"
```

### 3. Revisar la migración generada
Verifica el archivo en `alembic/versions/`

### 4. Aplicar la migración
```bash
uv run alembic upgrade head
```

## 📝 Ejemplos de Mensajes de Migración

```bash
# Agregar campo
uv run alembic revision --autogenerate -m "add emergency_contact to patients"

# Modificar campo
uv run alembic revision --autogenerate -m "change phone field length"

# Agregar tabla
uv run alembic revision --autogenerate -m "add appointments table"

# Agregar índice
uv run alembic revision --autogenerate -m "add index on consultation_date"
```

## ⚠️ Notas Importantes

- **Siempre revisa** las migraciones autogeneradas antes de aplicarlas
- **Haz backup** de la BD antes de migraciones grandes en producción
- **No modifiques** migraciones ya aplicadas, crea una nueva
- **Commitea** las migraciones junto con los cambios en los modelos

## 🔄 Cambiar de SQLite a PostgreSQL

### 1. Actualizar .env
```env
DATABASE_URL=postgresql://user:password@localhost:5432/medical_records_db
```

### 2. Crear la base de datos en PostgreSQL
```bash
createdb medical_records_db
```

### 3. Aplicar migraciones
```bash
uv run alembic upgrade head
```

## 🐛 Solución de Problemas

### Error: "Target database is not up to date"
```bash
uv run alembic upgrade head
```

### Ver SQL generado sin aplicar
```bash
uv run alembic upgrade head --sql
```

### Marcar como aplicada sin ejecutar (usar con cuidado)
```bash
uv run alembic stamp head
```
