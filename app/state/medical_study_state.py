"""Estado para gestión de estudios médicos"""

from datetime import date
from typing import Optional

import reflex as rx
from sqlmodel import select

from app.database import get_session
from app.models import MedicalStudy, Patient, StudyType
from app.services import MedicalStudyService


class MedicalStudyState(rx.State):
    """Estado para gestión de estudios médicos"""

    # Lista de estudios
    studies: list[MedicalStudy] = []
    current_study: Optional[MedicalStudy] = None

    # Estadísticas
    storage_size_mb: float = 0.0

    # Filtros
    selected_patient_id: Optional[int] = None
    selected_study_type: Optional[str] = None

    # Edición de estudio
    editing_study_id: Optional[int] = None

    # Formulario de nuevo estudio
    show_new_study_modal: bool = False
    form_patient_id: str = ""
    form_study_type: str = StudyType.LABORATORY.value
    form_study_name: str = ""
    form_study_date: str = str(date.today())
    form_institution: str = ""
    form_requesting_doctor: str = ""
    form_results: str = ""
    form_observations: str = ""
    form_diagnosis: str = ""

    # Archivo adjunto
    uploaded_files: list[str] = []  # Lista de archivos subidos (rx.upload devuelve lista)
    file_name: str = ""
    file_size: int = 0
    file_type: str = ""

    # Mensajes
    message: str = ""
    message_type: str = ""  # "success" o "error"

    def load_studies(self, patient_id: Optional[int] = None):
        """Carga los estudios médicos"""
        session = next(get_session())
        try:
            if patient_id:
                self.studies = MedicalStudyService.get_studies_by_patient(session, patient_id)
                self.selected_patient_id = patient_id
            else:
                # Cargar todos los estudios
                statement = select(MedicalStudy).order_by(MedicalStudy.study_date.desc())
                self.studies = list(session.exec(statement).all())

            # Cargar estadísticas de almacenamiento
            bytes_used = MedicalStudyService.get_total_storage_size(session, patient_id)
            self.storage_size_mb = round(bytes_used / (1024 * 1024), 2)
        finally:
            session.close()

    def load_studies_by_type(self, study_type: str):
        """Filtra estudios por tipo"""
        # Manejar "Todos" como caso especial
        if study_type == "Todos":
            self.selected_study_type = None
        else:
            self.selected_study_type = study_type

        session = next(get_session())
        try:
            statement = select(MedicalStudy)

            if self.selected_patient_id:
                statement = statement.where(MedicalStudy.patient_id == self.selected_patient_id)

            if self.selected_study_type:
                statement = statement.where(MedicalStudy.study_type == self.selected_study_type)

            statement = statement.order_by(MedicalStudy.study_date.desc())
            self.studies = list(session.exec(statement).all())
        finally:
            session.close()

    def open_new_study_modal(self):
        """Abre el modal para crear nuevo estudio"""
        self.editing_study_id = None
        self.show_new_study_modal = True
        self.clear_form()

    def open_edit_study_modal(self, study_id: int):
        """Abre el modal para editar un estudio existente"""
        session = next(get_session())
        try:
            study = session.get(MedicalStudy, study_id)
            if not study:
                self.message = f"Estudio con ID {study_id} no encontrado"
                self.message_type = "error"
                return

            # Cargar datos del estudio en el formulario
            self.editing_study_id = study_id
            self.form_patient_id = str(study.patient_id)
            self.form_study_type = study.study_type
            self.form_study_name = study.study_name
            self.form_study_date = str(study.study_date)
            self.form_institution = study.institution or ""
            self.form_requesting_doctor = study.requesting_doctor or ""
            self.form_results = study.results or ""
            self.form_observations = study.observations or ""
            self.form_diagnosis = study.diagnosis or ""

            # No cargamos el archivo existente para edición
            self.uploaded_files = []
            self.file_name = ""
            self.file_size = 0
            self.file_type = ""

            self.show_new_study_modal = True
        finally:
            session.close()

    def close_new_study_modal(self):
        """Cierra el modal de nuevo estudio"""
        self.show_new_study_modal = False
        self.clear_form()

    def clear_form(self):
        """Limpia el formulario"""
        self.form_patient_id = ""
        self.form_study_type = StudyType.LABORATORY.value
        self.form_study_name = ""
        self.form_study_date = str(date.today())
        self.form_institution = ""
        self.form_requesting_doctor = ""
        self.form_results = ""
        self.form_observations = ""
        self.form_diagnosis = ""
        self.uploaded_files = []
        self.file_name = ""
        self.file_size = 0
        self.file_type = ""
        self.message = ""

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Maneja la carga de archivos"""
        if not files:
            return

        # Reflex upload devuelve una lista, tomamos el primer archivo
        file = files[0]

        # Guardar información del archivo en el estado
        self.uploaded_files = [file.filename]
        self.file_name = file.filename or "archivo_sin_nombre"
        self.file_size = file.size or 0
        self.file_type = file.content_type or "application/octet-stream"

    def remove_uploaded_file(self):
        """Elimina el archivo subido antes de guardar"""
        self.uploaded_files = []
        self.file_name = ""
        self.file_size = 0
        self.file_type = ""

    def create_study(self):
        """Crea un nuevo estudio médico"""
        try:
            if not self.form_patient_id or not self.form_study_name:
                self.message = "Complete los campos requeridos"
                self.message_type = "error"
                return

            session = next(get_session())
            try:
                # Validar que el paciente existe
                patient = session.get(Patient, int(self.form_patient_id))
                if not patient:
                    self.message = f"Paciente con ID {self.form_patient_id} no encontrado"
                    self.message_type = "error"
                    return

                study = MedicalStudyService.create_study(
                    session=session,
                    patient_id=int(self.form_patient_id),
                    study_type=StudyType(self.form_study_type),
                    study_name=self.form_study_name,
                    study_date=date.fromisoformat(self.form_study_date),
                    institution=self.form_institution or None,
                    results=self.form_results or None,
                )

                # Actualizar campos adicionales si se proporcionaron
                if self.form_requesting_doctor:
                    study.requesting_doctor = self.form_requesting_doctor
                if self.form_observations:
                    study.observations = self.form_observations
                if self.form_diagnosis:
                    study.diagnosis = self.form_diagnosis

                session.add(study)
                session.commit()
                session.refresh(study)

                # Subir archivo si existe
                if self.uploaded_files:
                    from pathlib import Path

                    upload_file = Path(self.uploaded_files[0])

                    if upload_file.exists():
                        with open(upload_file, "rb") as f:
                            MedicalStudyService.upload_file(
                                session=session,
                                study_id=study.id,
                                file_content=f,
                                file_name=self.file_name,
                                file_type=self.file_type,
                            )

                self.message = f"Estudio '{self.form_study_name}' creado exitosamente"
                self.message_type = "success"
                self.close_new_study_modal()
                self.load_studies(self.selected_patient_id)
            finally:
                session.close()

        except Exception as e:
            self.message = f"Error al crear estudio: {str(e)}"
            self.message_type = "error"

    def update_study(self):
        """Actualiza un estudio médico existente"""
        try:
            if not self.editing_study_id:
                self.message = "No hay estudio en edición"
                self.message_type = "error"
                return

            if not self.form_study_name:
                self.message = "El nombre del estudio es requerido"
                self.message_type = "error"
                return

            session = next(get_session())
            try:
                # Convertir y validar fecha
                try:
                    study_date = date.fromisoformat(self.form_study_date)
                except ValueError:
                    self.message = "Formato de fecha inválido"
                    self.message_type = "error"
                    return

                # Actualizar estudio usando el servicio
                study = MedicalStudyService.update_study(
                    session=session,
                    study_id=self.editing_study_id,
                    study_name=self.form_study_name,
                    study_date=study_date,
                    institution=self.form_institution if self.form_institution else None,
                    results=self.form_results if self.form_results else None,
                    study_type=StudyType(self.form_study_type),
                )

                # Actualizar campos adicionales directamente
                study.requesting_doctor = (
                    self.form_requesting_doctor if self.form_requesting_doctor else None
                )
                study.observations = self.form_observations if self.form_observations else None
                study.diagnosis = self.form_diagnosis if self.form_diagnosis else None

                session.add(study)
                session.commit()

                # Subir nuevo archivo si existe
                if self.uploaded_files:
                    from pathlib import Path

                    upload_file = Path(self.uploaded_files[0])

                    if upload_file.exists():
                        with open(upload_file, "rb") as f:
                            MedicalStudyService.upload_file(
                                session=session,
                                study_id=study.id,
                                file_content=f,
                                file_name=self.file_name,
                                file_type=self.file_type,
                            )

                self.message = f"Estudio '{self.form_study_name}' actualizado exitosamente"
                self.message_type = "success"
                self.close_new_study_modal()
                self.load_studies(self.selected_patient_id)
            finally:
                session.close()

        except Exception as e:
            self.message = f"Error al actualizar estudio: {str(e)}"
            self.message_type = "error"

    def save_study(self):
        """Guarda el estudio (crea o actualiza según el modo)"""
        if self.editing_study_id:
            self.update_study()
        else:
            self.create_study()

    def delete_study(self, study_id: int):
        """Elimina un estudio médico"""
        try:
            session = next(get_session())
            try:
                MedicalStudyService.delete_study(session, study_id)
                self.message = "Estudio eliminado exitosamente"
                self.message_type = "success"
                self.load_studies(self.selected_patient_id)
            finally:
                session.close()
        except Exception as e:
            self.message = f"Error al eliminar estudio: {str(e)}"
            self.message_type = "error"

    def view_study(self, study_id: int):
        """Ver detalles de un estudio"""
        session = next(get_session())
        try:
            self.current_study = session.get(MedicalStudy, study_id)
        finally:
            session.close()

    def get_patient_name(self, patient_id: int) -> str:
        """Obtiene el nombre del paciente"""
        session = next(get_session())
        try:
            patient = session.get(Patient, patient_id)
            return patient.full_name if patient else "Desconocido"
        finally:
            session.close()

    def download_file(self, study_id: int):
        """Descarga el archivo de un estudio"""
        session = next(get_session())
        try:
            result = MedicalStudyService.download_file(session, study_id)

            if result:
                file_path, file_name = result
                # Usar rx.download para descargar el archivo
                return rx.download(url=str(file_path), filename=file_name)

        except Exception as e:
            self.message = f"Error al descargar archivo: {str(e)}"
            self.message_type = "error"
        finally:
            session.close()
