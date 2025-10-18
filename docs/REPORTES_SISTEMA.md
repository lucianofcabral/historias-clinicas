# Sistema de Reportes y Exportación

## 📋 Descripción

Sistema completo de generación de reportes médicos en formato PDF y Excel, con exportación directa desde la interfaz.

## ✨ Características Implementadas

### 1. **Servicio de Reportes** (`app/services/report_service.py`)

#### Historial Completo de Paciente
- **PDF:** Documento profesional con:
  - Datos personales del paciente
  - Antecedentes médicos (alergias, condiciones crónicas, historia familiar)
  - Lista completa de consultas con signos vitales
  - Estudios médicos realizados
  - Formato con colores y tablas profesionales
  
- **Excel:** Libro con 3 hojas:
  - **Hoja 1:** Datos del paciente
  - **Hoja 2:** Todas las consultas con detalles
  - **Hoja 3:** Estudios médicos (estudios críticos resaltados en rojo)

#### Reporte de Consultas
- **PDF:** Lista de consultas con filtro por fechas
  - Tabla con fecha, paciente, motivo y diagnóstico
  - Estadísticas (total de consultas)
  - Formato limpio para impresión

#### Reporte de Estudios Médicos
- **Excel:** Reporte completo de estudios
  - Filtros por tipo de estudio
  - Filtros por rango de fechas
  - Estudios críticos resaltados
  - Columnas: Fecha, Paciente, Tipo, Nombre, Institución, Médico, Resultados, Diagnóstico, Estado

### 2. **Interfaz de Usuario** (`app/pages/reports.py`)

#### Página de Reportes
- **3 Tarjetas Principales:**

1. **Historial Completo:**
   - Selector de paciente (lista completa con DNI)
   - Opción PDF o Excel
   - Botón de generación inmediata
   
2. **Reporte de Consultas:**
   - Filtros de fecha (inicio y fin)
   - Formato PDF
   - Genera tabla de consultas del período
   
3. **Reporte de Estudios:**
   - Selector de tipo de estudio (Laboratorio, Radiología, etc.)
   - Filtros de fecha
   - Formato Excel
   - Estudios críticos resaltados

#### Exportación Rápida
- **Botones en Detalle de Paciente:**
  - "Exportar PDF" → Descarga inmediata del historial en PDF
  - "Exportar Excel" → Descarga inmediata en formato Excel
  - Ubicados en la barra superior junto al botón "Volver"

### 3. **Estado y Lógica** (`app/state/report_state.py`)

- Manejo de filtros y parámetros
- Validación de datos
- Generación asíncrona
- Manejo de errores
- Descarga automática de archivos

## 🎨 Diseño

### Colores y Estilos en PDF
- **Azul (#2563eb):** Títulos y encabezados
- **Gris claro:** Fondos alternados para mejor lectura
- **Rojo claro:** Alertas y estudios críticos
- **Amarillo claro:** Antecedentes médicos
- Tablas con bordes y padding para legibilidad

### Colores en Excel
- **Azul fuerte:** Encabezados de tablas
- **Azul claro:** Subtítulos de secciones
- **Rojo claro:** Estudios críticos
- Bordes en todas las celdas
- Auto-ajuste de columnas
- Text wrap activado

## 📄 Tipos de Reportes

### Historial Completo de Paciente

**Contenido:**
```
┌─────────────────────────────────────┐
│   HISTORIA CLÍNICA COMPLETA         │
├─────────────────────────────────────┤
│ DATOS DEL PACIENTE                  │
│ - Nombre, DNI, Fecha Nacimiento     │
│ - Género, Tipo de Sangre            │
│ - Contacto (Tel, Email, Dirección)  │
├─────────────────────────────────────┤
│ ANTECEDENTES MÉDICOS                │
│ - Alergias                          │
│ - Condiciones Crónicas              │
│ - Antecedentes Familiares           │
├─────────────────────────────────────┤
│ CONSULTAS (con paginación)          │
│ Para cada consulta:                 │
│ - Fecha, Motivo, Síntomas           │
│ - Diagnóstico, Tratamiento          │
│ - Signos Vitales                    │
│ - Próxima Visita                    │
├─────────────────────────────────────┤
│ ESTUDIOS MÉDICOS (con paginación)   │
│ Para cada estudio:                  │
│ - Tipo, Nombre, Fecha               │
│ - Institución, Médico               │
│ - Resultados, Observaciones         │
│ - Estado (Pendiente/Crítico/etc)    │
└─────────────────────────────────────┘
```

### Reporte de Consultas

**Contenido:**
```
┌─────────────────────────────────────┐
│   REPORTE DE CONSULTAS              │
│   01/10/2025 - 18/10/2025          │
├─────────────────────────────────────┤
│ Total de Consultas: 25              │
├─────────────────────────────────────┤
│ TABLA:                              │
│ Fecha | Paciente | Motivo | Diagnóstico
│ ────────────────────────────────────│
│ (Lista de todas las consultas)      │
└─────────────────────────────────────┘
```

### Reporte de Estudios

**Contenido Excel:**
```
┌─────────────────────────────────────┐
│ REPORTE DE ESTUDIOS MÉDICOS         │
│ Tipo: Laboratorio | Desde: 01/10   │
├─────────────────────────────────────┤
│ Fecha | Paciente | Tipo | Nombre |  │
│ Institución | Médico | Resultados |  │
│ Diagnóstico | Estado                │
├─────────────────────────────────────┤
│ (Lista con estudios críticos        │
│  resaltados en rojo)                │
└─────────────────────────────────────┘
```

## 🚀 Uso

### Desde la Página de Reportes

1. Ir a **Reportes** en el menú de navegación
2. Seleccionar el tipo de reporte deseado
3. Configurar filtros (paciente, fechas, tipo de estudio)
4. Elegir formato (PDF o Excel según disponibilidad)
5. Hacer clic en "Generar Reporte"
6. El archivo se descargará automáticamente

### Exportación Rápida desde Detalle de Paciente

1. Ir al detalle de cualquier paciente
2. En la barra superior, junto a "Volver":
   - Hacer clic en **"Exportar PDF"** para PDF inmediato
   - Hacer clic en **"Exportar Excel"** para Excel inmediato
3. El archivo se descarga con el nombre `historial_paciente_{id}.pdf` o `.xlsx`

## 📦 Dependencias

### Instaladas:
```bash
reportlab    # Generación de PDFs
openpyxl     # Generación de Excel
```

### Uso en el Código:
```python
# Generar PDF de historial
from app.services import ReportService

content = ReportService.generate_patient_history_pdf(patient_id)
filename = f"historial_paciente_{patient_id}.pdf"

return rx.download(data=content, filename=filename)
```

## 🔧 Arquitectura

### Flujo de Generación

```
Usuario
  ↓
[UI - reports.py] 
  ↓
[State - report_state.py]
  ↓ (valida y procesa)
[Service - report_service.py]
  ↓ (consulta DB y genera)
[Database]
  ↓
[ReportLab / OpenPyXL]
  ↓ (genera bytes)
[rx.download()]
  ↓
Usuario recibe archivo
```

### Métodos del Servicio

```python
ReportService.generate_patient_history_pdf(patient_id: int) -> bytes
ReportService.generate_patient_history_excel(patient_id: int) -> bytes
ReportService.generate_consultations_report_pdf(start_date, end_date) -> bytes
ReportService.generate_studies_report_excel(study_type, start_date, end_date) -> bytes
```

## 📱 Responsive

- Grid de 3 columnas en pantallas grandes
- Se adapta a pantallas pequeñas
- Botones de exportación responsivos
- Formularios con campos apilados en móviles

## 🎯 Casos de Uso

### Para Médicos
1. **Imprimir historial para paciente:** Exportar PDF del historial completo
2. **Análisis de consultas:** Reporte Excel de consultas del mes
3. **Revisión de estudios:** Filtrar por tipo y exportar a Excel

### Para Administración
1. **Estadísticas mensuales:** Reporte de todas las consultas del mes
2. **Auditoría de estudios:** Reporte completo con filtros
3. **Archivo físico:** Imprimir PDFs para archivo

### Para Pacientes
1. **Historial personal:** Exportar PDF completo para llevar a otros profesionales
2. **Segunda opinión:** PDF con todos los estudios y diagnósticos

## ⚠️ Consideraciones

### Performance
- Los reportes de historiales completos pueden ser grandes si hay muchas consultas/estudios
- Se usa paginación automática en PDFs para manejar contenido extenso
- Los archivos se generan en memoria (BytesIO) para mejor performance

### Seguridad
- Los reportes respetan los permisos de usuario (requieren autenticación)
- No se guardan archivos temporales en disco
- Los bytes se generan y descargan directamente

### Limitaciones Actuales
- Reporte de consultas solo en PDF (no Excel)
- Reporte de estudios solo en Excel (no PDF)
- No hay previsualización antes de descargar
- Sin programación de reportes automáticos

## 🔮 Mejoras Futuras

- [ ] Previsualización de reportes antes de descargar
- [ ] Reportes programados (envío automático por email)
- [ ] Gráficos y estadísticas visuales en los reportes
- [ ] Plantillas personalizables
- [ ] Firma digital de médicos en PDFs
- [ ] Watermarks en reportes
- [ ] Compresión de archivos grandes
- [ ] Historial de reportes generados
- [ ] Exportación a otros formatos (CSV, JSON)
- [ ] Reportes batch (múltiples pacientes)

## 📊 Formatos Disponibles

| Tipo de Reporte | PDF | Excel |
|-----------------|-----|-------|
| Historial Completo | ✅ | ✅ |
| Consultas por Fecha | ✅ | ❌ |
| Estudios Médicos | ❌ | ✅ |

## 🗂️ Archivos del Sistema

```
app/
├── services/
│   └── report_service.py       # 700+ líneas - Generación de reportes
├── state/
│   └── report_state.py         # 170+ líneas - Lógica UI
├── pages/
│   └── reports.py              # 330+ líneas - Interfaz
└── app.py                      # Ruta agregada: /reports
```

## 🎉 Características Destacadas

- ✅ **Generación Inmediata:** Sin esperas, descarga directa
- ✅ **Diseño Profesional:** PDFs y Excel con formato corporativo
- ✅ **Filtros Flexibles:** Por fecha, tipo, paciente
- ✅ **Exportación Rápida:** Botones directos en detalle de paciente
- ✅ **Estudios Críticos Resaltados:** Visual importante
- ✅ **Información Completa:** Todos los datos relevantes incluidos
- ✅ **Sin Archivos Temporales:** Todo en memoria
- ✅ **Fácil de Usar:** Interface intuitiva y clara

## 💡 Tips de Uso

1. **Para reportes rápidos:** Usa los botones de exportación en el detalle del paciente
2. **Para análisis:** Usa la página de Reportes con filtros específicos
3. **Para imprimir:** Los PDFs están optimizados para impresión en papel carta
4. **Para compartir:** Los Excel son fáciles de enviar por email y editar
5. **Estudios críticos:** Siempre aparecen resaltados para rápida identificación
