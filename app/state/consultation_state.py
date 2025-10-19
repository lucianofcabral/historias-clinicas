"""Estado de Reflex para gestión de consultas médicas"""

from datetime import datetime

import reflex as rx

from app.database import get_session
from app.services import ConsultationService, PatientService


class ConsultationState(rx.State):
    """Estado para gestión de consultas médicas"""

    # Lista de consultas
    consultations: list[dict] = []

    # Formulario
    show_new_consultation_modal: bool = False
    editing_consultation_id: int | None = None  # Track if editing vs creating
    form_patient_id: str = ""
    form_reason: str = ""
    form_symptoms: str = ""
    form_diagnosis: str = ""
    form_treatment: str = ""
    form_notes: str = ""

    # Signos vitales
    form_blood_pressure: str = ""
    form_heart_rate: str = ""
    form_temperature: str = ""
    form_weight: str = ""
    form_height: str = ""
    form_next_visit: str = ""

    # Filtros y búsqueda
    search_query: str = ""
    selected_patient_id: int = 0

    # Pacientes disponibles
    patients_list: list[dict] = []
    patients_options: list[str] = []  # Lista de strings formateados (label) para el selector

    # Archivos adjuntos (múltiples)
    uploaded_files: list[dict] = []  # Lista de archivos: [{"data": base64, "name": str, "size": int, "type": str}]

    # Mensajes
    error_message: str = ""
    success_message: str = ""

    # Setters explícitos
    def set_show_new_consultation_modal(self, value: bool):
        """Setter para show_new_consultation_modal"""
        self.show_new_consultation_modal = value

    def set_form_patient_id(self, value: str):
        """Setter para form_patient_id"""
        self.form_patient_id = value

    def _resolve_patient_id_from_form(self) -> int:
        """Intentar resolver el ID numérico a partir del valor mostrado en el selector.

        Busca en patients_list una etiqueta que coincida con el valor actual del formulario.
        Si no la encuentra, intenta extraer el primer número entero presente en la cadena.
        Devuelve 0 si no puede resolver.
        """
        val = (self.form_patient_id or "").strip()
        if not val:
            return 0

        # Buscar en la lista de pacientes por label (coincidencia exacta)
        for p in self.patients_list:
            label = (
                f"{p.get('first_name')} {p.get('last_name')} (DNI: {p.get('dni')})"
                if p.get("dni")
                else f"{p.get('first_name')} {p.get('last_name')}"
            )
            if label == val:
                return int(p.get("id"))

        # Si no se encuentra, intentar extraer dígitos
        import re

        m = re.search(r"(\d+)", val)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                return 0

        return 0

    def set_form_reason(self, value: str):
        """Setter para form_reason"""
        self.form_reason = value

    def set_form_symptoms(self, value: str):
        """Setter para form_symptoms"""
        self.form_symptoms = value

    def set_form_diagnosis(self, value: str):
        """Setter para form_diagnosis"""
        self.form_diagnosis = value

    def set_form_treatment(self, value: str):
        """Setter para form_treatment"""
        self.form_treatment = value

    def set_form_notes(self, value: str):
        """Setter para form_notes"""
        self.form_notes = value

    def set_form_blood_pressure(self, value: str):
        """Setter para form_blood_pressure"""
        self.form_blood_pressure = value

    def set_form_heart_rate(self, value: str):
        """Setter para form_heart_rate"""
        self.form_heart_rate = value

    def set_form_temperature(self, value: str):
        """Setter para form_temperature"""
        self.form_temperature = value

    def set_form_weight(self, value: str):
        """Setter para form_weight"""
        self.form_weight = value

    def set_form_height(self, value: str):
        """Setter para form_height"""
        self.form_height = value

    def set_form_next_visit(self, value: str):
        """Setter para form_next_visit"""
        self.form_next_visit = value

    def load_consultations(self):
        """Carga todas las consultas o filtra por búsqueda/paciente"""
        session = next(get_session())

        # Prioridad 1: Filtrar por paciente específico
        if self.selected_patient_id > 0:
            consultations = ConsultationService.get_consultations_by_patient(
                session, self.selected_patient_id
            )
        # Prioridad 2: Buscar por término de búsqueda
        elif self.search_query.strip():
            consultations = ConsultationService.search_consultations(
                session, self.search_query, limit=50
            )
        # Por defecto: Todas las consultas (limitadas)
        else:
            consultations = ConsultationService.get_all_consultations(session, limit=50)

        self.consultations = [
            {
                "id": c.id,
                "patient_id": c.patient_id,
                "consultation_date": c.consultation_date.strftime("%Y-%m-%d %H:%M"),
                "reason": c.reason,
                "symptoms": c.symptoms or "",
                "diagnosis": c.diagnosis or "",
                "treatment": c.treatment or "",
                "blood_pressure": c.blood_pressure or "",
                "heart_rate": str(c.heart_rate) if c.heart_rate else "",
                "temperature": str(c.temperature) if c.temperature else "",
                "weight": str(c.weight) if c.weight else "",
                "height": str(c.height) if c.height else "",
                "bmi": str(c.bmi) if c.bmi else "",
                "bmi_category": c.bmi_category or "",
                "has_vital_signs": c.has_vital_signs,
                "next_visit": c.next_visit.strftime("%Y-%m-%d") if c.next_visit else "",
            }
            for c in consultations
        ]

    def load_patients(self):
        """Carga lista de pacientes para el selector"""
        session = next(get_session())
        patients = PatientService.get_all_patients(session, include_inactive=False)

        self.patients_list = [
            {
                "id": p.id,
                "name": f"{p.first_name} {p.last_name}",
                "dni": p.dni,
            }
            for p in patients
        ]

        # Generar opciones formateadas para el selector con ID visible
        # Formato: "ID: 1 - Juan Pérez (DNI: 12345678)"
        # Generar etiquetas sin exponer el ID interno
        self.patients_options = [
            f"{p.first_name} {p.last_name} (DNI: {p.dni})"
            if p.dni
            else f"{p.first_name} {p.last_name}"
            for p in patients
        ]

    async def handle_upload(self, files: list[rx.UploadFile]):
        """
        Maneja la carga de múltiples archivos seleccionados.
        Lee el contenido de cada archivo y lo guarda temporalmente en memoria.
        """
        print("📁 DEBUG UPLOAD CONSULTATION: handle_upload llamado")
        print(f"📁 DEBUG UPLOAD: {len(files)} archivo(s) recibidos")

        if not files:
            print("⚠️ DEBUG UPLOAD: No hay archivos en la lista")
            return

        import base64

        uploaded_list = []
        for idx, file in enumerate(files):
            print(f"📁 DEBUG UPLOAD [{idx+1}/{len(files)}]: Procesando {file.filename}")
            
            try:
                file_data = await file.read()
                print(f"✅ DEBUG UPLOAD: Contenido leído: {len(file_data)} bytes")

                uploaded_list.append({
                    "data": base64.b64encode(file_data).decode("utf-8"),
                    "name": file.filename,
                    "size": file.size or len(file_data),
                    "type": file.content_type or "application/octet-stream",
                })
                print(f"✅ DEBUG UPLOAD: Archivo {file.filename} cargado correctamente")
            except Exception as e:
                print(f"❌ DEBUG UPLOAD: Error al leer archivo {file.filename}: {e}")
                self.error_message = f"Error al cargar archivo {file.filename}: {str(e)}"

        self.uploaded_files = uploaded_list
        print(f"✅ DEBUG UPLOAD: Total {len(uploaded_list)} archivos listos para guardar")

    def remove_uploaded_file(self, index: int):
        """Elimina un archivo subido por índice"""
        if 0 <= index < len(self.uploaded_files):
            removed = self.uploaded_files.pop(index)
            print(f"🗑️ Archivo eliminado: {removed['name']}")

    def handle_search_change(self, value: str):
        """Maneja el cambio en el campo de búsqueda y recarga las consultas"""
        self.search_query = value
        # Resetear filtro por paciente al buscar
        if value.strip():
            self.selected_patient_id = 0
        self.load_consultations()

    def open_new_consultation_modal(self):
        """Abre el modal de nueva consulta"""
        self.load_patients()
        self.editing_consultation_id = None  # Reset editing mode
        self.show_new_consultation_modal = True
        self.clear_form()

    def open_edit_consultation_modal(self, consultation_id: int):
        """Abre el modal para editar una consulta existente"""
        session = next(get_session())
        consultation = ConsultationService.get_consultation_by_id(session, consultation_id)

        if not consultation:
            self.error_message = "Consulta no encontrada"
            return

        self.load_patients()
        self.editing_consultation_id = consultation_id

        # Cargar datos de la consulta en el formulario
        # Como el selector muestra labels, convertimos el patient_id a la etiqueta correspondiente
        self.load_patients()
        matched_label = None
        for p in self.patients_list:
            if p.get("id") == consultation.patient_id:
                matched_label = (
                    f"{p.get('first_name')} {p.get('last_name')} (DNI: {p.get('dni')})"
                    if p.get("dni")
                    else f"{p.get('first_name')} {p.get('last_name')}"
                )
                break

        self.form_patient_id = matched_label or str(consultation.patient_id)
        self.form_reason = consultation.reason or ""
        self.form_symptoms = consultation.symptoms or ""
        self.form_diagnosis = consultation.diagnosis or ""
        self.form_treatment = consultation.treatment or ""
        self.form_notes = consultation.notes or ""
        self.form_blood_pressure = consultation.blood_pressure or ""
        self.form_heart_rate = str(consultation.heart_rate) if consultation.heart_rate else ""
        self.form_temperature = str(consultation.temperature) if consultation.temperature else ""
        self.form_weight = str(consultation.weight) if consultation.weight else ""
        self.form_height = str(consultation.height) if consultation.height else ""
        self.form_next_visit = (
            consultation.next_visit.isoformat() if consultation.next_visit else ""
        )

        self.show_new_consultation_modal = True

    def close_new_consultation_modal(self):
        """Cierra el modal de nueva consulta"""
        self.show_new_consultation_modal = False
        self.editing_consultation_id = None
        self.clear_form()

    def clear_form(self):
        """Limpia el formulario"""
        self.form_patient_id = ""
        self.form_reason = ""
        self.form_symptoms = ""
        self.form_diagnosis = ""
        self.form_treatment = ""
        self.form_notes = ""
        self.form_blood_pressure = ""
        self.form_heart_rate = ""
        self.form_temperature = ""
        self.form_weight = ""
        self.form_height = ""
        self.form_next_visit = ""
        self.uploaded_files = []
        self.error_message = ""
        self.success_message = ""

    def save_consultation(self):
        """Guarda una consulta (crea o actualiza según el modo)"""
        if self.editing_consultation_id:
            self.update_consultation()
        else:
            self.create_consultation()

    def create_consultation(self):
        """Crea una nueva consulta"""
        # Validación
        if not self.form_patient_id.strip():
            self.error_message = "Debe ingresar el ID del paciente"
            return

        try:
            # Resolver si el form contiene una etiqueta
            patient_id = self._resolve_patient_id_from_form() or int(self.form_patient_id)
            if patient_id <= 0:
                self.error_message = "El ID del paciente debe ser un número positivo"
                return
        except ValueError:
            self.error_message = "El ID del paciente debe ser un número válido"
            return

        if not self.form_reason.strip():
            self.error_message = "El motivo de consulta es obligatorio"
            return

        # Validar presión arterial si se ingresó
        if self.form_blood_pressure.strip():
            if "/" not in self.form_blood_pressure:
                self.error_message = "Formato de presión arterial inválido. Use formato: 120/80"
                return

        session = next(get_session())

        try:
            # Convertir valores numéricos
            heart_rate = int(self.form_heart_rate) if self.form_heart_rate.strip() else None
            temperature = float(self.form_temperature) if self.form_temperature.strip() else None
            weight = float(self.form_weight) if self.form_weight.strip() else None
            height = float(self.form_height) if self.form_height.strip() else None
            next_visit = (
                datetime.strptime(self.form_next_visit, "%Y-%m-%d").date()
                if self.form_next_visit.strip()
                else None
            )

            consultation = ConsultationService.create_consultation(
                session=session,
                patient_id=patient_id,
                reason=self.form_reason.strip(),
                symptoms=self.form_symptoms.strip() or None,
                diagnosis=self.form_diagnosis.strip() or None,
                treatment=self.form_treatment.strip() or None,
                notes=self.form_notes.strip() or None,
                blood_pressure=self.form_blood_pressure.strip() or None,
                heart_rate=heart_rate,
                temperature=temperature,
                weight=weight,
                height=height,
                next_visit=next_visit,
            )

            # Subir archivos si existen (soporte para múltiples archivos)
            if self.uploaded_files:
                import base64
                from io import BytesIO
                from app.services import ConsultationFileService

                print(f"📎 DEBUG CREATE CONSULTATION: Procesando {len(self.uploaded_files)} archivo(s)...")

                files_saved = 0
                for idx, file_info in enumerate(self.uploaded_files):
                    try:
                        file_data = base64.b64decode(file_info["data"])
                        file_io = BytesIO(file_data)

                        print(f"✅ DEBUG CREATE [{idx+1}/{len(self.uploaded_files)}]: Guardando {file_info['name']}")

                        ConsultationFileService.create_file(
                            session=session,
                            consultation_id=consultation.id,
                            file_content=file_io,
                            file_name=file_info["name"],
                            file_type=file_info["type"],
                        )
                        files_saved += 1
                    except Exception as e:
                        print(f"❌ DEBUG CREATE: Error al guardar {file_info['name']}: {e}")

                if files_saved > 0:
                    print(f"✅ {files_saved} archivo(s) guardado(s) correctamente")

            self.success_message = "Consulta creada exitosamente"
            self.close_new_consultation_modal()
            self.load_consultations()

        except ValueError as e:
            self.error_message = f"Error en los datos ingresados: {str(e)}"
        except Exception as e:
            self.error_message = f"Error al crear la consulta: {str(e)}"

    def update_consultation(self):
        """Actualiza una consulta existente"""
        if not self.editing_consultation_id:
            self.error_message = "No hay consulta en edición"
            return

        # Validación
        if not self.form_patient_id.strip():
            self.error_message = "Debe ingresar el ID del paciente"
            return

        try:
            patient_id = int(self.form_patient_id)
            if patient_id <= 0:
                self.error_message = "El ID del paciente debe ser un número positivo"
                return
        except ValueError:
            self.error_message = "El ID del paciente debe ser un número válido"
            return

        if not self.form_reason.strip():
            self.error_message = "El motivo de consulta es obligatorio"
            return

        # Validar presión arterial si se ingresó
        if self.form_blood_pressure.strip():
            if "/" not in self.form_blood_pressure:
                self.error_message = "Formato de presión arterial inválido. Use formato: 120/80"
                return

        session = next(get_session())

        try:
            # Convertir valores numéricos
            heart_rate = int(self.form_heart_rate) if self.form_heart_rate.strip() else None
            temperature = float(self.form_temperature) if self.form_temperature.strip() else None
            weight = float(self.form_weight) if self.form_weight.strip() else None
            height = float(self.form_height) if self.form_height.strip() else None
            next_visit = (
                datetime.strptime(self.form_next_visit, "%Y-%m-%d").date()
                if self.form_next_visit.strip()
                else None
            )

            # Preparar datos para actualización
            update_data = {
                "patient_id": patient_id,
                "reason": self.form_reason.strip(),
                "symptoms": self.form_symptoms.strip() or None,
                "diagnosis": self.form_diagnosis.strip() or None,
                "treatment": self.form_treatment.strip() or None,
                "notes": self.form_notes.strip() or None,
                "blood_pressure": self.form_blood_pressure.strip() or None,
                "heart_rate": heart_rate,
                "temperature": temperature,
                "weight": weight,
                "height": height,
                "next_visit": next_visit,
            }

            ConsultationService.update_consultation(
                session=session, consultation_id=self.editing_consultation_id, **update_data
            )

            self.success_message = "Consulta actualizada exitosamente"
            self.close_new_consultation_modal()
            self.load_consultations()

        except ValueError as e:
            self.error_message = f"Error en los datos ingresados: {str(e)}"
        except Exception as e:
            self.error_message = f"Error al actualizar la consulta: {str(e)}"

    def filter_by_patient(self, patient_id: str):
        """Filtra consultas por paciente"""
        self.selected_patient_id = int(patient_id) if patient_id else 0
        self.load_consultations()

    def delete_consultation(self, consultation_id: int):
        """Elimina una consulta"""
        session = next(get_session())

        if ConsultationService.delete_consultation(session, consultation_id):
            self.success_message = "Consulta eliminada exitosamente"
            self.load_consultations()
        else:
            self.error_message = "No se pudo eliminar la consulta"

    def view_consultation(self, consultation_id: int):
        """Ver detalle de una consulta"""
        # TODO: Implementar vista detallada
        return rx.redirect(f"/consultations/{consultation_id}")
