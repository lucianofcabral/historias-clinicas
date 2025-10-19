# Guía de Prueba - Sistema de Descarga de Archivos

## Estado Actual (Implementación Funcional)

✅ **Sistema de descarga implementado y funcional**

### Qué funciona:
1. ✅ Carga de archivos al crear/editar estudios médicos
2. ✅ Visualización de archivos adjuntos en la lista de estudios
3. ✅ Descarga de archivos desde:
   - Vista de detalle de paciente (con componente `attachments_list`)
   - Vista de estudios médicos (con botones de descarga)
4. ✅ Vista previa de archivos en nueva pestaña (PDF, imágenes)
5. ✅ Componente reutilizable `attachments_list_component`

### Arquitectura implementada:
- **Sin endpoint HTTP separado**: Las descargas se manejan directamente desde los States de Reflex
- **Método**: `rx.download(data=bytes, filename=...)` lee el archivo y lo envía al navegador
- **Ventajas**:
  - Simple y funcional inmediatamente
  - No requiere configuración adicional de FastAPI
  - Integración nativa con Reflex
- **Limitación**:
  - Archivos grandes se cargan completamente en memoria
  - No hay streaming (para archivos > 100MB considerar endpoint HTTP)

---

## Cómo Probar el Sistema

### 1. Iniciar la aplicación

```bash
cd /home/fexa/Documentos/REPOSTORIOS/hc
reflex run
```

Acceder a: http://localhost:3000

### 2. Crear un estudio con archivo adjunto

1. Ir a "Estudios Médicos" en el menú
2. Clic en "Nuevo Estudio"
3. Completar el formulario:
   - Seleccionar paciente
   - Tipo de estudio: ej. "Laboratorio"
   - Nombre: ej. "Análisis de sangre"
   - Fecha: hoy
4. **Importante**: Usar el widget de carga de archivos (arrastrar o seleccionar)
5. Guardar el estudio

**Logs esperados** en la terminal:
```
📁 DEBUG UPLOAD: handle_upload llamado
📁 DEBUG UPLOAD: files recibidos: 1 archivo(s)
📁 DEBUG UPLOAD: Archivo seleccionado: documento.pdf
📁 DEBUG UPLOAD: Tamaño: 123456 bytes
✅ DEBUG UPLOAD: Información guardada
```

### 3. Verificar que el archivo se guardó

```bash
# Ver estudios con archivos
sqlite3 medical_records.db "SELECT id, study_name, file_name, file_size FROM medical_studies WHERE file_path IS NOT NULL;"

# Ver archivos físicos guardados
ls -lh studies/
ls -lh studies/patient_*/
```

**Ubicación de archivos**: `studies/patient_{id}/study_{study_id}_{timestamp}_{filename}`

### 4. Probar descarga desde vista de paciente

1. Ir a "Pacientes" en el menú
2. Seleccionar un paciente que tenga estudios
3. En la sección "Estudios Médicos", verás los estudios con archivos adjuntos
4. Clic en "Descargar" en cualquier archivo adjunto
5. El navegador descargará el archivo directamente

### 5. Probar vista previa

1. En el mismo listado de archivos adjuntos
2. Clic en "Vista previa"
3. Se abrirá una nueva pestaña con el contenido del archivo (si es PDF o imagen compatible)

---

## Arquitectura Técnica

### Flujo de Carga (Upload)

```
1. Usuario selecciona archivo en modal "Nuevo Estudio"
   ↓
2. rx.upload_files() copia archivo a uploaded_files/
   ↓
3. MedicalStudyState.handle_upload() guarda metadata (nombre, tamaño, tipo)
   ↓
4. MedicalStudyState.create_study() crea registro en DB
   ↓
5. MedicalStudyService.upload_file() mueve archivo a studies/patient_{id}/
   ↓
6. Actualiza DB con file_path, file_name, file_size, file_type
```

### Flujo de Descarga (Download)

```
1. Usuario hace clic en botón "Descargar"
   ↓
2. UI llama a PatientDetailState.download_study_file(study_id)
   ↓
3. State usa MedicalStudyService.download_file() para obtener ruta
   ↓
4. Lee archivo con open(file_path, "rb")
   ↓
5. Retorna rx.download(data=bytes, filename=name)
   ↓
6. Reflex envía bytes al navegador con Content-Disposition
```

### Archivos Clave

- **Componente UI**: `app/components/attachments.py`
  - `attachments_list_component()`: renderiza lista de archivos con botones

- **Estados**:
  - `app/state/medical_study_state.py`: upload y descarga desde estudios
  - `app/state/patient_detail_state.py`: descarga desde detalle de paciente

- **Servicio**: `app/services/medical_study_service.py`
  - `upload_file()`: guarda archivo físico y actualiza DB
  - `download_file()`: obtiene ruta absoluta y nombre

- **Páginas**:
  - `app/pages/patient_detail.py`: usa `study_item_with_attachments()`
  - `app/pages/medical_studies.py`: formulario con rx.upload widget

---

## Mejoras Futuras (Pendientes)

### 1. Endpoint HTTP con Streaming (para archivos grandes)

**Problema actual**: Archivos grandes (>100MB) se cargan completamente en memoria

**Solución propuesta**:
- Crear endpoint FastAPI: `GET /api/studies/{id}/download`
- Usar `StreamingResponse` para servir archivos en chunks
- Registrar router usando lifecycle hook de Reflex (requiere investigación adicional)

**Archivo preparado**: `app/api/studies.py` (ya existe, falta registrar router)

### 2. Descarga por paciente (ZIP)

Implementar endpoint: `GET /api/patients/{id}/download-studies`
- Empaquetar todos los estudios de un paciente en ZIP
- Streaming del ZIP sin escribir a disco
- Botón "Descargar todos los estudios" en vista de paciente

### 3. Vista previa mejorada

- Preview inline para PDFs (iframe en modal)
- Thumbnails para imágenes
- Visor de documentos integrado
- Soporte para más tipos MIME

### 4. Integración en vista de consultas

- Mostrar archivos adjuntos relacionados con cada consulta
- Reutilizar componente `attachments_list_component`

### 5. Tests automatizados

```python
# tests/test_study_service.py
def test_upload_file():
    """Verifica que un archivo se sube y guarda correctamente"""
    pass

def test_download_file():
    """Verifica que un archivo se descarga correctamente"""
    pass
```

---

## Notas de Desarrollo

### Por qué no se usa endpoint HTTP ahora

Reflex no expone la instancia FastAPI (`app.api` o `app._api`) en tiempo de importación del módulo `app/app.py`. Intentar registrar un `APIRouter` con `app.api.include_router()` falla con:

```python
AttributeError: 'App' object has no attribute 'api'
```

**Soluciones evaluadas**:
1. ✅ **Usar `rx.download(data=bytes)`** (implementado) - Simple y funcional
2. ⏳ Registrar router en lifecycle hook (requiere más investigación)
3. ⏳ Usar `rxconfig.py` para modificar FastAPI app en startup
4. ⏳ Acceder a `app._api` después de inicialización (API privada, no recomendado)

### Alternativa: Endpoint HTTP con Lifecycle Hook

```python
# En rxconfig.py o módulo de inicialización
from app.api.studies import router

def register_custom_routes(app):
    """Se ejecuta cuando Reflex inicializa la FastAPI app"""
    fastapi_app = app._api  # o método público si existe
    fastapi_app.include_router(router)
```

**Esto requiere**:
- Investigar hooks de lifecycle de Reflex
- Verificar API pública para acceder a FastAPI app
- Documentación oficial de Reflex para custom endpoints

---

## Comandos Útiles

```bash
# Ver estudios con archivos
sqlite3 medical_records.db "SELECT id, patient_id, study_name, file_name FROM medical_studies WHERE file_path IS NOT NULL;"

# Ver tamaño total de archivos
sqlite3 medical_records.db "SELECT SUM(file_size) FROM medical_studies WHERE file_size IS NOT NULL;"

# Limpiar archivos huérfanos (sin registro en DB)
find studies/ -type f -name "study_*" | while read f; do
    # Verificar si existe en DB
    study_id=$(echo $f | grep -oP 'study_\K\d+')
    exists=$(sqlite3 medical_records.db "SELECT COUNT(*) FROM medical_studies WHERE id=$study_id;")
    if [ "$exists" -eq "0" ]; then
        echo "Huérfano: $f"
        # rm "$f"  # Descomentar para eliminar
    fi
done

# Ver espacio usado por archivos
du -sh studies/
```

---

## Contacto y Soporte

Para problemas o preguntas sobre el sistema de archivos adjuntos:
- Revisar logs del servidor (terminal donde corre `reflex run`)
- Verificar permisos de directorio `studies/`
- Comprobar que `rx.get_upload_dir()` apunta a directorio correcto

**Fecha de implementación**: 2025-10-18  
**Versión**: 1.0.0 (funcional con rx.download)
