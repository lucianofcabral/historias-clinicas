# 🎨 Indicadores Visuales - Sistema de Historia Clínica

**Fecha**: 20 de octubre de 2025  
**Versión**: v1.2.0  
**Estado**: ✅ Implementado y Funcional

---

## 📊 Descripción General

Sistema completo de indicadores visuales que proporciona feedback inmediato al usuario durante las operaciones de carga de archivos y muestra información sobre la cantidad de archivos adjuntos en las listas.

---

## 🎯 Características Implementadas

### 1. 📎 Badges de Conteo de Archivos

#### **Estudios Médicos**
- **Ubicación**: Lista de estudios médicos
- **Visualización**: Badge azul con ícono de clip
- **Texto**: "N archivo(s)"
- **Comportamiento**: Solo se muestra si el estudio tiene archivos (N > 0)
- **Implementación**:
  - Estado: `_studies_file_count` dict en `MedicalStudyState`
  - Se carga automáticamente en `load_studies()` y `load_studies_by_type()`
  - Componente: `file_count_badge(study)` en `medical_studies.py`

#### **Consultas**
- **Ubicación**: Lista de consultas
- **Visualización**: Badge azul con ícono de clip
- **Texto**: "N archivo(s)"
- **Comportamiento**: Solo se muestra si la consulta tiene archivos
- **Implementación**:
  - Estado: `_consultations_file_count` dict en `ConsultationState`
  - Campos adicionales: `file_count`, `file_count_text`, `has_files`
  - Se carga automáticamente en `load_consultations()`

---

### 2. 🔄 Indicadores de Progreso Durante Uploads

#### **Componentes Comunes**
Todos los módulos implementan:
- ✅ Spinner animado (tamaño 3)
- ✅ Texto de progreso dinámico
- ✅ Botón deshabilitado durante la operación
- ✅ Loading state en el botón
- ✅ Caja destacada con fondo y bordes redondeados
- ✅ Desactivación automática al completar
- ✅ Manejo de errores que limpia indicadores

#### **Estudios Médicos**

**Estado** (`app/state/medical_study_state.py`):
```python
is_uploading: bool = False
upload_progress: str = ""
```

**Flujos de Progreso**:
- `create_study()`:
  1. "Creando estudio..."
  2. "Subiendo archivo..." (si hay archivo)
  
- `update_study()`:
  1. "Actualizando estudio..."
  2. "Subiendo archivo X de Y..." (por cada archivo)

**UI** (`app/pages/medical_studies.py`):
```python
rx.cond(
    MedicalStudyState.is_uploading,
    rx.vstack(
        rx.hstack(
            rx.spinner(size="3"),
            rx.text(MedicalStudyState.upload_progress, ...),
        ),
        padding="1rem",
        background=COLORS["surface"],
        border_radius="0.5rem",
    ),
    rx.fragment(),
)
```

#### **Consultas**

**Estado** (`app/state/consultation_state.py`):
```python
is_uploading: bool = False
upload_progress: str = ""
```

**Flujos de Progreso**:
- `create_consultation()`:
  1. "Creando consulta..."
  2. "Subiendo archivo X de Y..." (por cada archivo)
  
- `update_consultation()`:
  1. "Actualizando consulta..."
  2. "Subiendo archivo X de Y..." (por cada archivo)

**UI** (`app/pages/consultations.py`):
- Implementación idéntica a estudios médicos

#### **Archivos de Pacientes**

**Estado** (`app/state/patient_files_state.py`):
```python
is_uploading: bool = False
upload_progress: str = ""
```

**Flujo de Progreso**:
- `save_uploaded_files()`:
  1. "Preparando archivos..."
  2. "Subiendo archivo X de Y..." (por cada archivo)

**UI** (`app/components/patient_files.py`):
- Implementación idéntica a estudios médicos
- Condición adicional: `disabled=(length == 0) | is_uploading`

---

## 📋 Tabla Comparativa de Características

| Característica | Estudios | Consultas | Pacientes |
|---|:---:|:---:|:---:|
| Badge de cantidad de archivos | ✅ | ✅ | N/A* |
| Spinner durante upload | ✅ | ✅ | ✅ |
| Progreso "X de Y archivos" | ✅ | ✅ | ✅ |
| Botón deshabilitado | ✅ | ✅ | ✅ |
| Loading state en botón | ✅ | ✅ | ✅ |
| Manejo de errores | ✅ | ✅ | ✅ |
| Texto dinámico | ✅ | ✅ | ✅ |

*Los archivos de pacientes se muestran en una vista de detalle, no en lista

---

## 🎨 Estilos Visuales

### Badges
```python
rx.badge(
    rx.icon("paperclip", size=14),
    file_count_text,
    color_scheme="blue",
    variant="soft",
)
```

### Indicador de Progreso
```python
rx.vstack(
    rx.hstack(
        rx.spinner(size="3"),
        rx.text(upload_progress, size="2", weight="medium"),
        spacing="3",
        align="center",
    ),
    padding="1rem",
    background=COLORS["surface"],
    border_radius="0.5rem",
    width="100%",
)
```

### Botón con Loading
```python
rx.button(
    "Guardar",
    on_click=State.save,
    disabled=State.is_uploading,
    loading=State.is_uploading,
)
```

---

## 🔧 Implementación Técnica

### Patrón de Estado

**Campos requeridos**:
```python
is_uploading: bool = False
upload_progress: str = ""
```

**Activación al inicio**:
```python
self.is_uploading = True
self.upload_progress = "Iniciando..."
```

**Actualización durante proceso**:
```python
for idx, file in enumerate(files):
    self.upload_progress = f"Subiendo archivo {idx + 1} de {len(files)}..."
    # ... procesar archivo
```

**Desactivación al finalizar**:
```python
# En bloque try
self.is_uploading = False
self.upload_progress = ""

# En bloque except
self.is_uploading = False
self.upload_progress = ""
```

### Patrón de UI

**Estructura completa**:
```python
# Antes de los botones del modal/formulario
rx.cond(
    State.is_uploading,
    rx.vstack(
        rx.hstack(
            rx.spinner(size="3"),
            rx.text(State.upload_progress, size="2", weight="medium"),
            spacing="3",
            align="center",
        ),
        padding="1rem",
        background=COLORS["surface"],
        border_radius="0.5rem",
        width="100%",
    ),
    rx.fragment(),
),
# Botones
rx.flex(
    rx.button(
        "Guardar",
        on_click=State.save,
        disabled=State.is_uploading,
        loading=State.is_uploading,
    ),
)
```

---

## 🎯 Beneficios de UX

### Antes de la Implementación
- ❌ No había indicación de cantidad de archivos en listas
- ❌ Sin feedback visual durante uploads
- ❌ Riesgo de múltiples clicks accidentales
- ❌ Usuario no sabía si la operación estaba en progreso
- ❌ No había indicación de progreso en uploads múltiples

### Después de la Implementación
- ✅ Badges visuales muestran cantidad de archivos en listas
- ✅ Spinner animado + texto informan el progreso real
- ✅ Botón bloqueado previene errores de múltiples submissions
- ✅ Contador dinámico "Subiendo 2 de 5 archivos..."
- ✅ Feedback profesional e inmediato
- ✅ Usuario siempre sabe qué está pasando

---

## 📁 Archivos Modificados

### Estados
- `app/state/medical_study_state.py`
  - Agregado: `is_uploading`, `upload_progress`
  - Modificado: `create_study()`, `update_study()`

- `app/state/consultation_state.py`
  - Agregado: `is_uploading`, `upload_progress`
  - Modificado: `create_consultation()`, `update_consultation()`

- `app/state/patient_files_state.py`
  - Agregado: `is_uploading`, `upload_progress`
  - Modificado: `save_uploaded_files()`

### Páginas/Componentes
- `app/pages/medical_studies.py`
  - Agregado: Indicador de progreso en modal
  - Modificado: Botón con `disabled` y `loading`
  - Agregado: Función `file_count_badge()`

- `app/pages/consultations.py`
  - Agregado: Indicador de progreso en modal
  - Modificado: Botón con `disabled` y `loading`

- `app/components/patient_files.py`
  - Agregado: Indicador de progreso en modal de upload
  - Modificado: Botón con `disabled` y `loading`

---

## 🧪 Testing Recomendado

### Badges de Cantidad
1. ✅ Verificar que se muestre solo cuando hay archivos
2. ✅ Verificar conteo correcto (1, 5, 10 archivos)
3. ✅ Verificar que no se muestre cuando no hay archivos

### Indicadores de Progreso
1. ✅ Crear/actualizar con 1 archivo → ver progreso
2. ✅ Crear/actualizar con múltiples archivos → ver contador
3. ✅ Verificar deshabilitación de botón
4. ✅ Verificar que se desactive al completar
5. ✅ Verificar que se desactive al ocurrir error

---

## 🚀 Próximas Mejoras Posibles

- [ ] Progress bar visual (porcentaje)
- [ ] Estimación de tiempo restante
- [ ] Cancelación de upload en progreso
- [ ] Reintentos automáticos en caso de error
- [ ] Toast notifications al completar

---

## 📝 Notas de Implementación

- Los indicadores se manejan completamente en el estado de Reflex
- Las comparaciones deben hacerse en el estado, no en componentes
- Siempre desactivar indicadores en bloques `except`
- Usar `rx.fragment()` como alternativa vacía en `rx.cond()`
- El spinner de Reflex es `rx.spinner(size="3")`
- La propiedad `loading` en botones muestra un spinner automático

---

**Documentado por**: Claude (Copilot)  
**Fecha**: 20 de octubre de 2025
