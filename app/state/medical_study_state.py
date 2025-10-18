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

    # Vista de detalle
    show_detail_modal: bool = False
    detail_study: Optional[MedicalStudy] = None

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

    # Archivo existente (para modo edición)
    existing_file_name: str = ""
    existing_file_path: str = ""

    # Mensajes
    message: str = ""
    message_type: str = ""  # "success" o "error"

    # Setters explícitos
    def set_show_new_study_modal(self, value: bool):
        """Setter para show_new_study_modal"""
        self.show_new_study_modal = value

    def set_show_detail_modal(self, value: bool):
        """Setter para show_detail_modal"""
        self.show_detail_modal = value

    def set_form_patient_id(self, value: str):
        """Setter para form_patient_id"""
        self.form_patient_id = value

    def set_form_study_type(self, value: str):
        """Setter para form_study_type"""
        self.form_study_type = value

    def set_form_study_name(self, value: str):
        """Setter para form_study_name"""
        self.form_study_name = value

    def set_form_study_date(self, value: str):
        """Setter para form_study_date"""
        self.form_study_date = value

    def set_form_institution(self, value: str):
        """Setter para form_institution"""
        self.form_institution = value

    def set_form_requesting_doctor(self, value: str):
        """Setter para form_requesting_doctor"""
        self.form_requesting_doctor = value

    def set_form_results(self, value: str):
        """Setter para form_results"""
        self.form_results = value

    def set_form_observations(self, value: str):
        """Setter para form_observations"""
        self.form_observations = value

    def set_form_diagnosis(self, value: str):
        """Setter para form_diagnosis"""
        self.form_diagnosis = value

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

    def view_study(self, study_id: int):
        """Abre el modal de detalle del estudio"""
        session = next(get_session())
        try:
            study = session.get(MedicalStudy, study_id)
            if study:
                self.detail_study = study
                self.show_detail_modal = True
        finally:
            session.close()

    def close_detail_modal(self):
        """Cierra el modal de detalle"""
        self.show_detail_modal = False
        self.detail_study = None

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
        """
        Maneja la información de archivos seleccionados.
        NOTA: El archivo físico NO se copia hasta que rx.upload_files() se ejecuta.
        Aquí solo guardamos la metadata para mostrar en la UI.
        """
        print("📁 DEBUG UPLOAD: handle_upload llamado")
        print(f"📁 DEBUG UPLOAD: files recibidos: {len(files)} archivo(s)")

        # rx.upload_files devuelve una lista con información de archivos
        if not files:
            print("⚠️ DEBUG UPLOAD: No hay archivos en la lista")
            return

        # Obtener el primer archivo
        file = files[0]
        print(f"📁 DEBUG UPLOAD: Archivo seleccionado: {file.filename}")
        print(f"📁 DEBUG UPLOAD: Tamaño: {file.size} bytes")
        print(f"📁 DEBUG UPLOAD: Tipo: {file.content_type}")

        # Guardar solo la información del archivo
        # El archivo físico se copiará automáticamente al directorio uploaded_files/
        # cuando se ejecute rx.upload_files() (que ocurre ANTES de este handler)
        self.uploaded_files = [file.filename]  # Guardar solo el nombre/ruta relativa
        self.file_name = file.filename
        self.file_size = file.size
        self.file_type = file.content_type or "application/octet-stream"

        print("✅ DEBUG UPLOAD: Información guardada")
        print("✅ DEBUG UPLOAD: Se copiará a uploaded_files/ al guardar el estudio")

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

                    # El archivo fue guardado por rx.upload_files()
                    # file_path puede ser solo el nombre o incluir "uploaded_files/"
                    file_path = self.uploaded_files[0]

                    # Probar diferentes ubicaciones
                    cwd = Path.cwd()

                    # Opción 1: Ruta directa desde CWD (si incluye uploaded_files/)
                    option1 = cwd / file_path
                    # Opción 2: Dentro del directorio de uploads
                    option2 = cwd / rx.get_upload_dir() / file_path
                    # Opción 3: Solo el nombre del archivo en uploads
                    option3 = cwd / rx.get_upload_dir() / Path(file_path).name

                    print("🔍 DEBUG: Intentando ubicar archivo...")
                    print(f"🔍 DEBUG: CWD: {cwd}")
                    print(f"🔍 DEBUG: Upload dir: {rx.get_upload_dir()}")
                    print(f"🔍 DEBUG: File path original: {file_path}")
                    print(f"🔍 DEBUG: Opción 1: {option1} - Existe: {option1.exists()}")
                    print(f"🔍 DEBUG: Opción 2: {option2} - Existe: {option2.exists()}")
                    print(f"🔍 DEBUG: Opción 3: {option3} - Existe: {option3.exists()}")

                    # Encontrar el archivo
                    upload_file = None
                    if option1.exists():
                        upload_file = option1
                        print("✅ DEBUG: Usando opción 1")
                    elif option2.exists():
                        upload_file = option2
                        print("✅ DEBUG: Usando opción 2")
                    elif option3.exists():
                        upload_file = option3
                        print("✅ DEBUG: Usando opción 3")

                    if upload_file:
                        with open(upload_file, "rb") as f:
                            result = MedicalStudyService.upload_file(
                                session=session,
                                study_id=study.id,
                                file_content=f,
                                file_name=self.file_name,
                                file_type=self.file_type,
                            )
                            print(f"✅ DEBUG: Archivo guardado en: {result.file_path}")
                            self.message = f"Estudio '{self.form_study_name}' creado exitosamente con archivo adjunto"
                    else:
                        print("⚠️ DEBUG: Archivo NO encontrado - guardando estudio sin archivo")
                        # Listar archivos en el directorio de uploads para debug
                        upload_dir = cwd / rx.get_upload_dir()
                        if upload_dir.exists():
                            files_in_dir = list(upload_dir.iterdir())
                            print(
                                f"📂 DEBUG: Archivos en {upload_dir}: {len(files_in_dir)} archivos"
                            )
                            for f in files_in_dir[:5]:
                                print(f"  - {f.name}")
                        self.message = f"Estudio '{self.form_study_name}' creado exitosamente (sin archivo adjunto - funcionalidad en desarrollo)"
                else:
                    print("ℹ️ DEBUG: No hay archivos para subir")
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

                    # El archivo fue guardado por rx.upload_files() en el directorio de uploads
                    file_path = self.uploaded_files[0]
                    upload_dir = Path.cwd() / rx.get_upload_dir()
                    upload_file = upload_dir / file_path

                    print(f"🔍 DEBUG UPDATE: Buscando archivo en: {upload_file}")
                    print(f"🔍 DEBUG UPDATE: Upload dir: {upload_dir}")
                    print(f"🔍 DEBUG UPDATE: ¿Archivo existe?: {upload_file.exists()}")

                    if upload_file.exists():
                        with open(upload_file, "rb") as f:
                            result = MedicalStudyService.upload_file(
                                session=session,
                                study_id=study.id,
                                file_content=f,
                                file_name=self.file_name,
                                file_type=self.file_type,
                            )
                            print(f"✅ DEBUG UPDATE: Archivo guardado en: {result.file_path}")
                            self.message = f"Estudio '{self.form_study_name}' actualizado exitosamente con nuevo archivo"
                    else:
                        print(
                            "⚠️ DEBUG UPDATE: Archivo NO encontrado - guardando estudio sin nuevo archivo"
                        )
                        # Listar archivos en el directorio de uploads para debug
                        if upload_dir.exists():
                            files_in_dir = list(upload_dir.iterdir())
                            print(
                                f"📂 DEBUG UPDATE: Archivos en {upload_dir}: {len(files_in_dir)} archivos"
                            )
                            for f in files_in_dir[:5]:
                                print(f"  - {f.name}")
                        self.message = f"Estudio '{self.form_study_name}' actualizado exitosamente (sin archivo nuevo - funcionalidad en desarrollo)"
                else:
                    print("ℹ️ DEBUG UPDATE: No hay archivos para subir (uploaded_files está vacío)")
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
