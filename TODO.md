# 📝 TODO - Sistema de Historia Clínica

## ✅ Completadas

### v1.2.0 - Visual Indicators (20 Oct 2025)
- [x] **Badges de cantidad de archivos**
  - Badges en lista de estudios mostrando cantidad de archivos adjuntos
  - Badges en lista de consultas mostrando cantidad de archivos adjuntos
  - Solo visible cuando hay archivos (N > 0)
  
- [x] **Indicadores de progreso en uploads**
  - Spinner animado durante operaciones de carga
  - Texto dinámico "Subiendo archivo X de Y..."
  - Botones deshabilitados durante uploads
  - Implementado en: Estudios, Consultas, Archivos de Pacientes
  
- [x] **Documentación de indicadores visuales**
  - Creado VISUAL_INDICATORS.md con guía completa
  - Actualizado SESSION_SUMMARY.md y NEXT_SESSION.md

### v1.1.0 - Arquitectura Multi-Archivo (19 Oct 2025)
- [x] **Múltiples archivos en estudios médicos**
  - Soporte para hasta 10 archivos por estudio
  - Upload, preview, eliminación implementados
  - Archivos en `uploads/studies/study_{id}/`
  
- [x] **Múltiples archivos en consultas**
  - Soporte para hasta 10 archivos por consulta
  - Upload modal con preview y gestión
  - Archivos en `uploads/consultations/consultation_{id}/`
  
- [x] **Múltiples archivos en pacientes (archivos directos)**
  - Sistema completo con categorías (Documento, Imagen, Laboratorio, Receta, Seguro, Consentimiento, Otro)
  - Modal de upload con selector de categoría y descripción
  - Archivos en `uploads/patients/patient_{id}/`
  
- [x] **Vista unificada de archivos del paciente**
  - Muestra archivos directos + archivos de estudios + archivos de consultas
  - Ordenado por fecha con iconos por tipo
  
- [x] **Mostrar nombre/DNI del paciente en lista de estudios**
  - Cache de información de paciente optimizado
  - Una sola query para cargar todos los datos

---

## 🔴 Prioridad Alta

### ⭐ Migración a PostgreSQL (Próxima Sesión)
- [ ] **Setup de PostgreSQL**
  - [ ] Decidir: Docker (recomendado) o Local
  - [ ] Configurar PostgreSQL según opción elegida
  - [ ] Crear base de datos y usuario
  - [ ] Probar conexión manual
  
- [ ] **Configuración del proyecto**
  - [ ] Instalar `psycopg2-binary`
  - [ ] Actualizar `app/config.py` con soporte multi-DB
  - [ ] Crear `.env` para variables de entorno
  - [ ] Actualizar `app/database.py` con pool de conexiones
  
- [ ] **Migración de datos**
  - [ ] Backup completo de SQLite actual
  - [ ] Ejecutar migraciones Alembic en PostgreSQL
  - [ ] Crear script de migración de datos
  - [ ] Migrar datos de SQLite → PostgreSQL
  - [ ] Verificar integridad de datos
  
- [ ] **Testing completo**
  - [ ] Probar todos los módulos (CRUD completo)
  - [ ] Verificar upload/download de archivos
  - [ ] Probar reportes y backups
  - [ ] Benchmarking de performance
  
- [ ] **Documentación**
  - [ ] Actualizar README.md con instrucciones PostgreSQL
  - [ ] Documentar proceso de setup (Docker/Local)
  - [ ] Crear troubleshooting guide

**Ver**: `POSTGRESQL_SETUP_GUIDE.md` para guía completa

---

## 🟡 Prioridad Media

### Testing End-to-End
- [ ] Crear paciente de prueba completo
- [ ] Probar upload de 1, 5, 10 archivos en estudios
- [ ] Probar upload de 1, 5, 10 archivos en consultas
- [ ] Probar upload de 1, 5, 10 archivos directos (con diferentes categorías)
- [ ] Verificar archivos guardados en disco correcto:
  - [ ] `uploads/studies/study_{id}/`
  - [ ] `uploads/consultations/consultation_{id}/`
  - [ ] `uploads/patients/patient_{id}/`
- [ ] Verificar registros en base de datos
- [ ] Probar descarga de archivos desde vista unificada
- [ ] Probar eliminación de archivos (debe borrar archivo físico + registro BD)
- [ ] Edge cases:
  - [ ] Archivos con nombres especiales (espacios, tildes, caracteres raros)
  - [ ] Archivos grandes (cerca de 50MB)
  - [ ] Múltiples uploads simultáneos
  - [ ] Cancelar upload a mitad

---

## 🟡 Prioridad Media

### Indicadores Visuales (Quick Win - 15-20 min)
- [ ] Badges con cantidad de archivos en:
  - [ ] Lista de estudios médicos ("Estudio #8 📎 3 archivos")
  - [ ] Lista de consultas ("Consulta 15/10 📎 2 archivos")
  - [ ] Detalle de paciente ("5 archivos directos")
- [ ] Progress bar durante uploads grandes
- [ ] Tooltips con info de archivo al hacer hover

### Merge y Release
- [ ] Merge `feature/multi-file-architecture` → `main`
- [ ] Crear tag `v1.1.0`
- [ ] Push a repositorio remoto
- [ ] Documentar cambios en CHANGELOG.md

---

## ⚪ Backlog (Mejoras Futuras)

### Gestión de Archivos Avanzada
- [ ] Preview de PDFs inline (sin descargar)
- [ ] Búsqueda/filtrado de archivos por nombre, tipo, fecha
- [ ] Compresión automática de imágenes grandes
- [ ] Edición de metadata (cambiar categoría, descripción)
- [ ] Mover archivos entre categorías
- [ ] Duplicar/copiar archivos

### Compartir y Colaboración
- [ ] Compartir archivos específicos entre pacientes
- [ ] Exportar conjunto de archivos (ZIP)
- [ ] Enviar archivos por email al paciente
- [ ] QR code para acceso rápido a archivos

### Historial y Versiones
- [ ] Historial de versiones de archivos
- [ ] Rollback a versión anterior
- [ ] Marcar archivos como "obsoletos" sin eliminar

### Procesamiento Inteligente
- [ ] OCR para extraer texto de PDFs/imágenes
- [ ] Detección automática de tipo de documento
- [ ] Sugerencias de categoría basadas en contenido
- [ ] Extracción automática de datos de laboratorios

### Performance
- [ ] Lazy loading de archivos grandes
- [ ] Paginación en vista unificada
- [ ] Thumbnails para imágenes
- [ ] Caché de previews

---

## 🐛 Bugs Conocidos

*(Ninguno reportado actualmente)*

---

## 📋 Notas de Desarrollo

### Estructura Actual
```
uploads/
├── studies/study_{id}/
├── consultations/consultation_{id}/
└── patients/patient_{id}/
```

### Límites
- Max 10 archivos por upload
- 50MB por archivo
- Formatos: PDF, imágenes (PNG, JPG, JPEG), documentos (DOC, DOCX)

### Stack Técnico
- **Framework**: Reflex (Python)
- **Base de Datos**: SQLite + SQLModel
- **Upload**: rx.upload() con multiple=True
- **Encoding**: Base64 para transmisión
- **Storage**: BytesIO → archivos binarios

---

*Última actualización: 19 de octubre de 2025*
