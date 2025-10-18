# 📝 Estrategia de Git - Historia Clínica

## 📊 Estado Actual

**Rama actual:** `main`
**Último commit:** `c840d0b - feat: dashboard mejorado con estadísticas completas`

**Cambios pendientes:**
- ✅ Sistema de backup/restore (completado)
- ✅ Sistema de reportes PDF/Excel (completado)
- ✅ Fixes de UI y deprecations (completado)
- 🔄 Mejoras de UX pendientes (archivos, selectores)

---

## 🎯 Estrategia Propuesta

### Opción A: Commits Directos en Main (Recomendado para proyectos pequeños)

**Ventajas:**
- ✅ Simple y directo
- ✅ No hay overhead de merge
- ✅ Historial lineal
- ✅ Perfecto para desarrollo individual

**Commits propuestos:**

1. **feat: sistema de backup y restore de base de datos**
   - app/services/backup_service.py
   - app/state/settings_state.py
   - app/pages/settings.py
   - backups/.gitkeep

2. **feat: generación de reportes PDF y Excel**
   - app/services/report_service.py
   - app/state/report_state.py
   - app/pages/reports.py
   - app/app.py (agregar ruta)

3. **fix: actualizar Node.js y corregir deprecations**
   - app/state/*_state.py (agregar setters explícitos)
   - pyproject.toml, uv.lock (dependencias)

4. **fix: corregir iconos inválidos y mejorar layout responsive**
   - app/pages/dashboard.py (iconos)
   - app/pages/settings.py (iconos)
   - app/pages/patient_detail.py (iconos)
   - app/pages/reports.py (layout con rx.grid)

5. **docs: agregar guía de pruebas de reportes**
   - REPORT_TESTING_GUIDE.md
   - test_reports.py

6. **chore: actualizar INSTRUCTIONS.md con estado del proyecto**
   - INSTRUCTIONS.md

---

### Opción B: Feature Branches (Recomendado para equipos o features grandes)

**Ventajas:**
- ✅ Revisión de código más fácil
- ✅ Trabajo paralelo en múltiples features
- ✅ Rollback más simple
- ✅ CI/CD por rama

**Estructura de ramas:**

```
main
├── feature/file-management          (archivos adjuntos)
├── feature/improved-selectors        (reemplazar IDs por selects)
└── feature/ux-improvements           (mejoras generales UX)
```

**Workflow:**
```bash
# Crear rama para feature
git checkout -b feature/file-management

# Hacer commits
git add <files>
git commit -m "feat: agregar descarga de archivos adjuntos"

# Merge a main
git checkout main
git merge feature/file-management
git branch -d feature/file-management
```

---

## 🚀 Plan de Acción Inmediato

### PASO 1: Commitear trabajo actual (main)

```bash
# Agregar archivos de backup
git add app/services/backup_service.py
git add app/state/settings_state.py
git add app/pages/settings.py
git add backups/.gitkeep
git commit -m "feat: sistema de backup y restore SQLite/PostgreSQL

- Implementar BackupService con soporte SQLite y PostgreSQL
- Crear UI para gestión de backups en settings
- Agregar funciones de crear, restaurar y eliminar backups
- Incluir validación y manejo de errores"

# Agregar sistema de reportes
git add app/services/report_service.py
git add app/state/report_state.py
git add app/pages/reports.py
git add REPORT_TESTING_GUIDE.md
git add test_reports.py
git commit -m "feat: generación de reportes PDF y Excel

- Implementar ReportService con reportlab y openpyxl
- Crear reportes de historial de paciente (PDF/Excel)
- Crear reporte de consultas por fechas (PDF)
- Crear reporte de estudios médicos (Excel)
- Agregar UI de reportes con selectores de formato
- Incluir script de pruebas automatizadas"

# Agregar fixes y mejoras
git add app/state/*.py
git add app/pages/dashboard.py
git add app/pages/settings.py
git add app/pages/patient_detail.py
git add app/pages/reports.py
git add app/pages/login.py
git add app/state/auth_state.py
git add pyproject.toml uv.lock
git commit -m "fix: deprecations, iconos y mejoras de layout

- Agregar setters explícitos en todos los States
- Actualizar iconos a formato válido (underscore)
- Mejorar layout responsive con rx.grid
- Aumentar ancho de contenedores a 1400px
- Actualizar dependencias de Node.js"

# Agregar documentación
git add INSTRUCTIONS.md
git add .gitignore
git commit -m "docs: actualizar documentación del proyecto

- Actualizar INSTRUCTIONS.md con estado completo
- Mejorar .gitignore para archivos de prueba"

# Agregar cambios menores
git add app/app.py
git add app/components/navbar.py
git add app/services/__init__.py
git commit -m "chore: actualizar imports y configuración

- Agregar rutas de reports y settings
- Actualizar exports de servicios
- Mejorar navbar con nuevas secciones"
```

### PASO 2: Limpiar archivos de prueba

```bash
# Eliminar archivos de test generados
rm test_*.pdf test_*.xlsx
git add -u
```

### PASO 3: Crear rama para nuevas features

```bash
# Feature: Gestión de archivos
git checkout -b feature/file-management

# Feature: Selectores mejorados (después)
git checkout main
git checkout -b feature/improved-selectors
```

---

## 📋 Próximos Commits Planeados

### En `feature/file-management`:
1. `feat: endpoint seguro para descarga de archivos`
2. `feat: visualización de archivos en vista de paciente`
3. `feat: visualización de archivos en vista de consulta`
4. `feat: componente de lista de archivos adjuntos`

### En `feature/improved-selectors`:
1. `feat: componente select de pacientes con búsqueda`
2. `refactor: reemplazar input ID por select en consultas`
3. `refactor: reemplazar input ID por select en estudios`
4. `refactor: reemplazar input ID por select en reportes`

---

## 🎨 Convenciones de Commits

**Formato:**
```
<tipo>(<scope>): <descripción corta>

<descripción detallada>
<razón del cambio>
<impacto>
```

**Tipos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `refactor`: Cambio de código sin modificar funcionalidad
- `docs`: Cambios en documentación
- `style`: Cambios de formato (espacios, comas, etc)
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento

**Ejemplos:**
```bash
feat(reports): agregar exportación a Excel
fix(patients): corregir validación de DNI
refactor(ui): reemplazar IDs por selectores descriptivos
docs(readme): actualizar instrucciones de instalación
```

---

## 🤔 Recomendación Final

**Para este proyecto (desarrollo individual):**

✅ **Usar Opción A (commits directos en main)** PERO:
- Hacer commits atómicos y descriptivos
- Commitear features completas, no trabajo a medias
- Usar branches solo para experimentos o features grandes

**Workflow recomendado:**
1. Commitear todo el trabajo actual en 4-5 commits lógicos
2. Push a main
3. Crear rama `feature/file-management` para archivos
4. Crear rama `feature/improved-selectors` para UX
5. Merge a main cuando estén completas

