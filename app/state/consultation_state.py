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

    # Mensajes
    error_message: str = ""
    success_message: str = ""

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
        self.show_new_consultation_modal = True
        self.clear_form()

    def close_new_consultation_modal(self):
        """Cierra el modal de nueva consulta"""
        self.show_new_consultation_modal = False
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
        self.error_message = ""
        self.success_message = ""

    def create_consultation(self):
        """Crea una nueva consulta"""
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

            ConsultationService.create_consultation(
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

            self.success_message = "Consulta creada exitosamente"
            self.close_new_consultation_modal()
            self.load_consultations()

        except ValueError as e:
            self.error_message = f"Error en los datos ingresados: {str(e)}"
        except Exception as e:
            self.error_message = f"Error al crear la consulta: {str(e)}"

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
