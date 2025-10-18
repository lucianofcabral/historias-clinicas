"""Estado para la página de detalle de paciente"""

from typing import Optional

import reflex as rx

from app.database import get_session
from app.models import Consultation, MedicalStudy, Patient
from app.services import ConsultationService, MedicalStudyService


class PatientDetailState(rx.State):
    """Estado para la vista detallada de un paciente"""

    # Datos del paciente
    current_patient_id: Optional[int] = None
    patient: Optional[Patient] = None
    patient_age: int = 0
    patient_full_name: str = ""
    patient_birth_date_str: str = ""

    # Historial
    consultations: list[Consultation] = []
    studies: list[MedicalStudy] = []

    # Estadísticas
    total_consultations: int = 0
    total_studies: int = 0
    last_consultation_date: str = ""

    def load_patient_detail(self):
        """Carga todos los datos del paciente"""
        # Obtener patient_id de la URL
        router_data = self.router.page.params
        patient_id = router_data.get("patient_id")

        if not patient_id:
            return

        try:
            self.current_patient_id = int(patient_id)
        except (ValueError, TypeError):
            return

        session = next(get_session())
        try:
            # Cargar paciente
            self.patient = session.get(Patient, self.current_patient_id)

            if not self.patient:
                return

            # Extraer datos computados del paciente
            self.patient_age = self.patient.age
            self.patient_full_name = self.patient.full_name
            self.patient_birth_date_str = self.patient.birth_date.strftime("%Y-%m-%d")

            # Cargar consultas del paciente
            self.consultations = ConsultationService.get_consultations_by_patient(
                session, self.current_patient_id
            )
            self.total_consultations = len(self.consultations)

            # Obtener fecha de última consulta
            if self.consultations:
                self.last_consultation_date = self.consultations[0].consultation_date.strftime(
                    "%Y-%m-%d"
                )

            # Cargar estudios del paciente
            self.studies = MedicalStudyService.get_studies_by_patient(
                session, self.current_patient_id
            )
            self.total_studies = len(self.studies)

        finally:
            session.close()
