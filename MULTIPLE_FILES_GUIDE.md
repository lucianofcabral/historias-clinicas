# Guía para Implementar Múltiples Archivos

## ✅ COMPLETADO: Estudios Médicos

Los estudios médicos ya soportan múltiples archivos (commit e95fea0).

### Cambios realizados:
1. **MedicalStudyState** (`app/state/medical_study_state.py`):
   - `uploaded_files: list[dict]` - Lista de archivos con estructura `{"data": base64, "name": str, "size": int, "type": str}`
   - `handle_upload()` - Procesa múltiples archivos y los codifica en base64
   - `create_study()` - Guarda todos los archivos usando un loop
   - `update_study()` - Agrega múltiples archivos a un estudio existente
   - `remove_uploaded_file(index)` - Elimina un archivo por índice

2. **UI** (`app/pages/medical_studies.py`):
   - `rx.upload(multiple=True, max_files=10)`
   - Vista previa con `rx.foreach` mostrando todos los archivos
   - Botón de eliminar por archivo individual

---

## 🔧 PENDIENTE: Consultas Médicas

### Pasos para implementar:

#### 1. Actualizar ConsultationState (`app/state/consultation_state.py`)

Agregar después de la línea ~40:

```python
# Archivos adjuntos (múltiples)
uploaded_files: list[dict] = []  # Lista de archivos: [{"data": base64, "name": str, "size": int, "type": str}]

async def handle_upload(self, files: list[rx.UploadFile]):
    """Maneja la carga de múltiples archivos seleccionados."""
    if not files:
        return

    import base64
    uploaded_list = []
    
    for file in files:
        try:
            file_data = await file.read()
            uploaded_list.append({
                "data": base64.b64encode(file_data).decode("utf-8"),
                "name": file.filename,
                "size": file.size or len(file_data),
                "type": file.content_type or "application/octet-stream",
            })
        except Exception as e:
            print(f"❌ Error al leer archivo {file.filename}: {e}")
    
    self.uploaded_files = uploaded_list

def remove_uploaded_file(self, index: int):
    """Elimina un archivo subido por índice"""
    if 0 <= index < len(self.uploaded_files):
        self.uploaded_files.pop(index)
```

#### 2. Actualizar create_consultation() en ConsultationState

Después de crear la consulta, agregar:

```python
# Subir archivos si existen
if self.uploaded_files:
    import base64
    from io import BytesIO
    from app.services import ConsultationFileService
    
    for file_info in self.uploaded_files:
        try:
            file_data = base64.b64decode(file_info["data"])
            file_io = BytesIO(file_data)
            
            ConsultationFileService.create_file(
                session=session,
                consultation_id=consultation.id,
                file_content=file_io,
                file_name=file_info["name"],
                file_type=file_info["type"],
            )
        except Exception as e:
            print(f"❌ Error al guardar {file_info['name']}: {e}")
```

#### 3. Actualizar UI de consultas (`app/pages/consultations.py`)

Buscar el formulario de consultas y agregar ANTES del rx.divider final (antes de "Diagnóstico y Tratamiento"):

```python
rx.divider(margin_y="1rem"),

# Archivos Adjuntos
rx.heading("Archivos Adjuntos", size="5", margin_bottom="0.5rem"),
rx.upload(
    rx.vstack(
        rx.button(
            rx.icon("upload", size=20),
            "Seleccionar Archivos",
            variant="soft",
            color_scheme="blue",
        ),
        rx.text(
            "PDF, imágenes, documentos (máx 50MB por archivo)",
            size="1",
            color=COLORS["text_secondary"],
        ),
        spacing="2",
    ),
    id="upload_consultation_files",
    multiple=True,
    accept={
        "application/pdf": [".pdf"],
        "image/*": [".png", ".jpg", ".jpeg"],
        "application/msword": [".doc", ".docx"],
    },
    max_files=10,
    max_size=50 * 1024 * 1024,
    on_drop=ConsultationState.handle_upload(
        rx.upload_files(upload_id="upload_consultation_files")
    ),
),

# Vista previa de archivos
rx.cond(
    ConsultationState.uploaded_files.length() > 0,
    rx.vstack(
        rx.text("Archivos listos para subir:", size="2", weight="bold"),
        rx.foreach(
            ConsultationState.uploaded_files,
            lambda file_info, idx: rx.card(
                rx.hstack(
                    rx.icon("paperclip", size=18, color=COLORS["primary"]),
                    rx.vstack(
                        rx.text(file_info["name"], size="2", weight="bold"),
                        rx.text(file_info["type"], size="1", color=COLORS["text_secondary"]),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("x", size=16),
                        on_click=ConsultationState.remove_uploaded_file(idx),
                        variant="ghost",
                        color_scheme="red",
                        size="1",
                    ),
                    width="100%",
                    align="center",
                ),
                size="1",
                variant="surface",
            ),
        ),
        spacing="2",
        width="100%",
    ),
),

rx.divider(margin_y="1rem"),
```

#### 4. Limpiar archivos al cerrar modal

En `clear_form()` o donde limpies el formulario de consultas:

```python
self.uploaded_files = []
```

---

## 🔧 PENDIENTE: Archivos de Paciente

### Opción 1: Agregar a patient_detail.py

Crear una sección nueva en patient_detail.py que permita subir archivos directamente al paciente:

```python
rx.card(
    rx.heading("Subir Archivos del Paciente", size="5"),
    rx.upload(
        # ... similar a los anteriores
    ),
)
```

### Opción 2: Modal dedicado

Crear un modal específico para gestión de archivos del paciente con:
- Selector de categoría (FileCategory enum)
- Upload de archivos
- Lista de archivos actuales con opción de eliminar

---

## 📋 Checklist de Implementación

### Consultas
- [ ] Agregar `uploaded_files` a ConsultationState
- [ ] Implementar `handle_upload()` en ConsultationState
- [ ] Implementar `remove_uploaded_file()` en ConsultationState
- [ ] Actualizar `create_consultation()` para guardar archivos
- [ ] Actualizar `update_consultation()` para agregar archivos (si aplica)
- [ ] Agregar rx.upload en el formulario de consultas
- [ ] Agregar vista previa con rx.foreach
- [ ] Limpiar uploaded_files al cerrar modal
- [ ] Probar: crear consulta con múltiples archivos
- [ ] Probar: eliminar archivo antes de guardar
- [ ] Verificar archivos en consultation_files tabla

### Archivos de Paciente
- [ ] Crear PatientFilesUploadState o agregar a PatientDetailState
- [ ] Implementar handle_upload()
- [ ] Agregar selector de categoría (FileCategory)
- [ ] Implementar guardado con PatientFileService
- [ ] Crear UI (modal o sección en patient_detail)
- [ ] Integrar con vista unificada de archivos
- [ ] Probar upload de diferentes categorías
- [ ] Verificar archivos en patient_files tabla

---

## 🎯 Estructura Común para Todos

### Estado (State):
```python
uploaded_files: list[dict] = []

async def handle_upload(self, files: list[rx.UploadFile]):
    # Leer y codificar cada archivo en base64
    
def remove_uploaded_file(self, index: int):
    # Eliminar de la lista por índice
```

### UI (Component):
```python
rx.upload(
    id="upload_X",
    multiple=True,
    max_files=10,
    on_drop=State.handle_upload(rx.upload_files(upload_id="upload_X")),
)

rx.cond(
    State.uploaded_files.length() > 0,
    rx.foreach(State.uploaded_files, lambda f, idx: card_preview(f, idx)),
)
```

### Servicio (al crear/actualizar):
```python
for file_info in state.uploaded_files:
    file_data = base64.b64decode(file_info["data"])
    file_io = BytesIO(file_data)
    
    XFileService.create_file(
        session=session,
        entity_id=entity.id,
        file_content=file_io,
        file_name=file_info["name"],
        file_type=file_info["type"],
    )
```

---

## 🔍 Verificación Post-Implementación

Para cada entidad, verificar:

1. **Upload funciona**: Seleccionar múltiples archivos y ver preview
2. **Delete funciona**: Eliminar archivos antes de guardar
3. **Save funciona**: Crear entidad y verificar archivos en BD
4. **Display funciona**: Ver archivos en patient_files_section
5. **Download funciona**: Descargar cada archivo individualmente

### Queries de verificación:

```sql
-- Consultas
SELECT * FROM consultation_files WHERE consultation_id = X;

-- Pacientes
SELECT * FROM patient_files WHERE patient_id = X;

-- Estudios (ya verificado)
SELECT * FROM study_files WHERE study_id = X;
```

---

## 📝 Notas Importantes

1. **Base64 en memoria**: Los archivos se mantienen en memoria (encoded en base64) hasta que se guarda la entidad. Esto evita dependencia del sistema de archivos temporal.

2. **Límite de tamaño**: Con `max_size=50MB` y `max_files=10`, el máximo teórico es 500MB en memoria. Considera reducir si hay problemas de performance.

3. **Retrocompatibilidad**: Los servicios ya existentes (StudyFileService, ConsultationFileService, PatientFileService) ya soportan `create_file()` con BytesIO.

4. **Vista unificada**: PatientFilesState ya carga archivos de las 3 fuentes. Al agregar archivos nuevos, aparecerán automáticamente después de refresh.

---

## 🚀 Orden Sugerido de Implementación

1. ✅ **Estudios** (COMPLETADO)
2. 🔜 **Consultas** (siguiente, más simple porque no tiene archivos legacy)
3. 🔜 **Pacientes** (último, requiere decisión de UX: modal vs sección)

Total estimado: 2-3 horas de implementación + testing
