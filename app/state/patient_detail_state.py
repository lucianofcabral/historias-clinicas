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

        # Cargar archivos unificados del paciente
        from app.state.patient_files_state import PatientFilesState

        yield PatientFilesState.load_all_files(self.current_patient_id)

    def export_patient_pdf(self):
        """Exporta el historial del paciente a PDF"""
        if not self.current_patient_id:
            return

        from app.services import ReportService

        try:
            content = ReportService.generate_patient_history_pdf(self.current_patient_id)
            filename = f"historial_paciente_{self.current_patient_id}.pdf"

            return rx.download(
                data=content,
                filename=filename,
            )

        except Exception as e:
            print(f"Error al exportar PDF: {str(e)}")

    def export_patient_excel(self):
        """Exporta el historial del paciente a Excel"""
        if not self.current_patient_id:
            return

        from app.services import ReportService

        try:
            content = ReportService.generate_patient_history_excel(self.current_patient_id)
            filename = f"historial_paciente_{self.current_patient_id}.xlsx"

            return rx.download(
                data=content,
                filename=filename,
            )

        except Exception as e:
            print(f"Error al exportar Excel: {str(e)}")

    def download_study_file(self, study_id: int):
        """Descarga el archivo adjunto asociado a un estudio.

        Busca el estudio en la base de datos, lee el archivo y lo envía al navegador.
        """
        print(f"🔽 DEBUG: download_study_file llamado con study_id={study_id}")
        session = next(get_session())
        try:
            study = session.get(MedicalStudy, study_id)
            if not study:
                print(f"❌ Estudio {study_id} no encontrado")
                return

            print(f"✓ Estudio encontrado: {study.study_name}")
            print(f"✓ Archivo: {study.file_name}")

            # Usar el servicio para obtener la ruta y nombre del archivo
            from app.services import MedicalStudyService

            result = MedicalStudyService.download_file(session, study_id)

            if not result:
                print(f"❌ Estudio {study_id} sin archivo adjunto")
                return

            file_path, file_name = result
            print(f"✓ Ruta del archivo: {file_path}")
            print(f"✓ Archivo existe: {file_path.exists()}")

            # Leer archivo y enviar bytes directamente
            with open(file_path, "rb") as f:
                file_data = f.read()

            print(f"✓ Archivo leído: {len(file_data)} bytes")
            print(f"🚀 Iniciando descarga de: {file_name}")

            return rx.download(data=file_data, filename=file_name)

        except Exception as e:
            print(f"❌ Error en download_study_file: {e}")
            import traceback

            traceback.print_exc()
        finally:
            session.close()
