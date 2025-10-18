"""Estado de Reflex para vista detallada de consulta"""

import reflex as rx

from app.database import get_session
from app.services import ConsultationService, PatientService


class ConsultationDetailState(rx.State):
    """Estado para vista detallada de consulta"""

    # Consulta actual
    current_consultation_id: int = 0
    consultation: dict = {}

    # Datos del paciente
    patient_name: str = ""
    patient_dni: str = ""
    patient_age: int = 0

    # Datos extraídos de la consulta
    consultation_date_str: str = ""
    has_vital_signs: bool = False
    bmi_value: str = ""
    bmi_category: str = ""

    def load_consultation_detail(self):
        """Carga los detalles de una consulta desde el ID en la URL"""
        # Obtener ID de la URL
        consultation_id_str = self.router.page.params.get("consultation_id", "0")

        try:
            self.current_consultation_id = int(consultation_id_str)
        except (ValueError, TypeError):
            self.current_consultation_id = 0
            return

        if self.current_consultation_id <= 0:
            return

        session = next(get_session())

        # Cargar consulta
        consultation = ConsultationService.get_consultation_by_id(
            session, self.current_consultation_id
        )

        if not consultation:
            self.consultation = {}
            return

        # Cargar paciente
        patient = PatientService.get_patient_by_id(session, consultation.patient_id)

        if patient:
            self.patient_name = patient.full_name
            self.patient_dni = patient.dni or ""
            self.patient_age = patient.age

        # Extraer datos de la consulta
        self.consultation_date_str = consultation.consultation_date.strftime("%d/%m/%Y %H:%M")
        self.has_vital_signs = consultation.has_vital_signs
        self.bmi_value = str(consultation.bmi) if consultation.bmi else ""
        self.bmi_category = consultation.bmi_category or ""

        # Guardar consulta como dict
        self.consultation = {
            "id": consultation.id,
            "patient_id": consultation.patient_id,
            "consultation_date": consultation.consultation_date.strftime("%Y-%m-%d %H:%M"),
            "reason": consultation.reason or "",
            "symptoms": consultation.symptoms or "",
            "diagnosis": consultation.diagnosis or "",
            "treatment": consultation.treatment or "",
            "notes": consultation.notes or "",
            "blood_pressure": consultation.blood_pressure or "",
            "heart_rate": str(consultation.heart_rate) if consultation.heart_rate else "",
            "temperature": str(consultation.temperature) if consultation.temperature else "",
            "weight": str(consultation.weight) if consultation.weight else "",
            "height": str(consultation.height) if consultation.height else "",
            "next_visit": (
                consultation.next_visit.strftime("%d/%m/%Y") if consultation.next_visit else ""
            ),
        }
