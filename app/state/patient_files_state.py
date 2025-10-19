"""Estado para gestionar archivos unificados de un paciente"""

import reflex as rx
from typing import Optional

from app.database import get_session
from app.models import ConsultationFile, PatientFile, StudyFile
from app.services import ConsultationFileService, PatientFileService, StudyFileService


class UnifiedFile(rx.Base):
    """Estructura unificada para representar cualquier tipo de archivo"""

    file_id: int
    file_name: str
    file_size: int
    file_type: str
    uploaded_at: str
    description: Optional[str] = None
    category: str  # "patient", "study", "consultation"
    source_id: int  # ID del paciente/estudio/consulta
    source_name: str  # Nombre descriptivo del origen


class PatientFilesState(rx.State):
    """Estado para gestionar vista unificada de archivos del paciente"""

    # ID del paciente actual
    current_patient_id: Optional[int] = None

    # Archivos por categoría
    patient_files: list[UnifiedFile] = []
    study_files: list[UnifiedFile] = []
    consultation_files: list[UnifiedFile] = []

    # Estadísticas
    total_files: int = 0
    total_size_mb: float = 0.0

    # Filtros
    selected_category: str = "all"  # "all", "patient", "study", "consultation"

    @rx.var
    def filtered_files(self) -> list[UnifiedFile]:
        """Retorna archivos filtrados por categoría seleccionada"""
        if self.selected_category == "all":
            return self.patient_files + self.study_files + self.consultation_files
        elif self.selected_category == "patient":
            return self.patient_files
        elif self.selected_category == "study":
            return self.study_files
        elif self.selected_category == "consultation":
            return self.consultation_files
        return []

    def load_all_files(self, patient_id: int):
        """Carga todos los archivos del paciente de todas las fuentes"""
        self.current_patient_id = patient_id
        session = next(get_session())

        try:
            # 1. Cargar archivos directos del paciente
            patient_files_raw = PatientFileService.get_files_by_patient(session, patient_id)
            self.patient_files = [
                UnifiedFile(
                    file_id=f.id,
                    file_name=f.file_name,
                    file_size=f.file_size,
                    file_type=f.file_type,
                    uploaded_at=f.uploaded_at.strftime("%Y-%m-%d %H:%M"),
                    description=f.description,
                    category="patient",
                    source_id=f.patient_id,
                    source_name=f.file_category,
                )
                for f in patient_files_raw
            ]

            # 2. Cargar archivos de estudios médicos
            study_files_raw = StudyFileService.get_files_by_patient(session, patient_id)
            # Necesitamos obtener el nombre del estudio para cada archivo
            from app.models import MedicalStudy

            self.study_files = []
            for f in study_files_raw:
                study = session.get(MedicalStudy, f.study_id)
                study_name = study.study_name if study else f"Estudio #{f.study_id}"

                self.study_files.append(
                    UnifiedFile(
                        file_id=f.id,
                        file_name=f.file_name,
                        file_size=f.file_size,
                        file_type=f.file_type,
                        uploaded_at=f.uploaded_at.strftime("%Y-%m-%d %H:%M"),
                        description=f.description,
                        category="study",
                        source_id=f.study_id,
                        source_name=study_name,
                    )
                )

            # 3. Cargar archivos de consultas
            consultation_files_raw = ConsultationFileService.get_files_by_patient(
                session, patient_id
            )
            from app.models import Consultation

            self.consultation_files = []
            for f in consultation_files_raw:
                consultation = session.get(Consultation, f.consultation_id)
                consultation_name = (
                    f"Consulta {consultation.consultation_date.strftime('%Y-%m-%d')}"
                    if consultation
                    else f"Consulta #{f.consultation_id}"
                )

                self.consultation_files.append(
                    UnifiedFile(
                        file_id=f.id,
                        file_name=f.file_name,
                        file_size=f.file_size,
                        file_type=f.file_type,
                        uploaded_at=f.uploaded_at.strftime("%Y-%m-%d %H:%M"),
                        description=f.description,
                        category="consultation",
                        source_id=f.consultation_id,
                        source_name=consultation_name,
                    )
                )

            # Calcular estadísticas
            all_files = self.patient_files + self.study_files + self.consultation_files
            self.total_files = len(all_files)
            total_size_bytes = sum(f.file_size for f in all_files)
            self.total_size_mb = round(total_size_bytes / (1024 * 1024), 2)

        finally:
            session.close()

    def get_filtered_files(self) -> list[UnifiedFile]:
        """Retorna archivos filtrados por categoría seleccionada"""
        if self.selected_category == "all":
            return self.patient_files + self.study_files + self.consultation_files
        elif self.selected_category == "patient":
            return self.patient_files
        elif self.selected_category == "study":
            return self.study_files
        elif self.selected_category == "consultation":
            return self.consultation_files
        return []

    def set_category_filter(self, category: str):
        """Cambia el filtro de categoría"""
        self.selected_category = category

    def download_file(self, file_id: int, category: str):
        """Descarga un archivo según su categoría"""
        session = next(get_session())

        try:
            if category == "patient":
                result = PatientFileService.download_file(session, file_id)
            elif category == "study":
                result = StudyFileService.download_file(session, file_id)
            elif category == "consultation":
                result = ConsultationFileService.download_file(session, file_id)
            else:
                print(f"❌ Categoría inválida: {category}")
                return

            if result:
                file_path, file_name = result
                with open(file_path, "rb") as f:
                    file_data = f.read()

                print(f"🚀 Descargando: {file_name} ({len(file_data)} bytes)")
                return rx.download(data=file_data, filename=file_name)
            else:
                print(f"❌ Archivo no encontrado: ID={file_id}, category={category}")

        except Exception as e:
            print(f"❌ Error al descargar archivo: {e}")
            import traceback

            traceback.print_exc()
        finally:
            session.close()
