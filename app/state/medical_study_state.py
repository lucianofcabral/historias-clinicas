"""Estado para gestión de estudios médicos"""

from datetime import date
from typing import Any, Optional

import reflex as rx
from sqlmodel import select

from app.database import get_session
from app.models import MedicalStudy, Patient, StudyType
from app.services import MedicalStudyService
from app.services.study_file_service import StudyFileService


class MedicalStudyState(rx.State):
    """Estado para gestión de estudios médicos"""

    # Lista de estudios
    studies: list[MedicalStudy] = []
    current_study: Optional[MedicalStudy] = None

    # Información de pacientes para cada estudio (cache)
    _studies_patient_info: dict[int, dict[str, str]] = {}

    # Conteo de archivos por estudio (cache)
    _studies_file_count: dict[int, int] = {}

    # Vista de detalle
    show_detail_modal: bool = False
    detail_study: Optional[dict] = None
    study_files: list[dict] = []

    # Estadísticas
    storage_size_mb: float = 0.0

    # Filtros
    selected_patient_id: Optional[int] = None
    selected_study_type: Optional[str] = None

    # Lista de pacientes para el selector
    patients_list: list[dict] = []
    patients_options: list[str] = []  # Lista de labels para el selector
    patients_map: dict = {}  # map label -> id

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

    # Archivos adjuntos (múltiples)
    uploaded_files: list[
        dict
    ] = []  # Lista de archivos: [{"data": base64, "name": str, "size": int, "type": str}]

    # Archivos del estudio en detalle
    study_files: list[
        dict
    ] = []  # Lista de archivos del estudio: [{"id": int, "file_name": str, "file_size": int, "file_type": str, "created_at": str}]

    # Indicador de carga
    is_uploading: bool = False
    upload_progress: str = ""  # Texto de progreso como "Subiendo 2 de 5 archivos..."

    # Mensajes
    message: str = ""
    message_type: str = ""  # "success" o "error"

    @rx.var
    def studies_patient_info(self) -> dict[int, dict[str, str]]:
        """Retorna el diccionario de información de pacientes"""
        return self._studies_patient_info

    @rx.var
    def studies_file_count(self) -> dict[int, int]:
        """Retorna el diccionario de conteo de archivos por estudio"""
        return self._studies_file_count
    
    def get_file_count_text(self, study_id: int) -> str:
        """Retorna el texto formateado del conteo de archivos para un estudio"""
        count = self._studies_file_count.get(study_id, 0)
        return f"{count} archivo(s)" if count > 0 else ""
    
    def has_files(self, study_id: int) -> bool:
        """Retorna si un estudio tiene archivos adjuntos"""
        return self._studies_file_count.get(study_id, 0) > 0

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

    def _resolve_patient_id_from_form(self) -> int:
        """Resuelve el ID numérico desde la etiqueta seleccionada en el selector.

        Si el valor de form_patient_id coincide con alguna etiqueta en patients_options,
        devuelve el id correspondiente. Si el valor es numérico, lo parsea. Si falla,
        devuelve 0.
        """
        val = (self.form_patient_id or "").strip()
        if not val:
            return 0

        # Verificar en patients_map
        if val in self.patients_map:
            try:
                return int(self.patients_map[val])
            except ValueError:
                return 0

        # Intentar parsear un número dentro de la cadena
        import re

        m = re.search(r"(\d+)", val)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                return 0

        return 0

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
                studies = MedicalStudyService.get_studies_by_patient(session, patient_id)
                self.selected_patient_id = patient_id
            else:
                # Cargar todos los estudios
                statement = select(MedicalStudy).order_by(MedicalStudy.study_date.desc())
                studies = list(session.exec(statement).all())

            # Limpiar cache anterior
            self._studies_patient_info = {}
            self._studies_file_count = {}

            # Cachear información del paciente y conteo de archivos para cada estudio
            for study in studies:
                patient = session.get(Patient, study.patient_id)
                if patient:
                    self._studies_patient_info[study.id] = {
                        "name": f"{patient.first_name} {patient.last_name}",
                        "dni": patient.dni,
                    }

                # Obtener conteo de archivos
                files = StudyFileService.get_files_by_study(session, study.id)
                self._studies_file_count[study.id] = len(files)

            self.studies = studies

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
            studies = list(session.exec(statement).all())

            # Limpiar cache anterior
            self._studies_patient_info = {}
            self._studies_file_count = {}

            # Cachear información del paciente y conteo de archivos para cada estudio
            for study in studies:
                patient = session.get(Patient, study.patient_id)
                if patient:
                    self._studies_patient_info[study.id] = {
                        "name": f"{patient.first_name} {patient.last_name}",
                        "dni": patient.dni,
                    }

                # Obtener conteo de archivos
                files = StudyFileService.get_files_by_study(session, study.id)
                self._studies_file_count[study.id] = len(files)

            self.studies = studies
        finally:
            session.close()

    def load_patients(self):
        """Carga lista de pacientes activos para el selector"""
        session = next(get_session())
        try:
            statement = (
                select(Patient)
                .where(Patient.is_active)
                .order_by(Patient.last_name, Patient.first_name)
            )
            patients = session.exec(statement).all()
            self.patients_list = [
                {
                    "id": p.id,
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                    "dni": p.dni or "",
                }
                for p in patients
            ]

            # Generar labels y mapa label->id
            opts = []
            pmap = {}
            for p in patients:
                label = (
                    f"{p.first_name} {p.last_name} (DNI: {p.dni})"
                    if p.dni
                    else f"{p.first_name} {p.last_name}"
                )
                opts.append(label)
                pmap[label] = p.id

            self.patients_options = opts
            self.patients_map = pmap
        finally:
            session.close()

    def open_new_study_modal(self):
        """Abre el modal para crear nuevo estudio"""
        # Asegurar que las opciones del selector estén cargadas
        self.load_patients()
        self.editing_study_id = None
        self.show_new_study_modal = True
        self.clear_form()

    def open_edit_study_modal(self, study_id: int):
        """Abre el modal para editar un estudio existente"""
        self.load_patients()
        session = next(get_session())
        try:
            study = session.get(MedicalStudy, study_id)
            if not study:
                self.message = f"Estudio con ID {study_id} no encontrado"
                self.message_type = "error"
                return

            # Cargar datos del estudio en el formulario
            self.editing_study_id = study_id
            # Convertir patient_id a label si está en el mapa
            matched_label = None
            for p in self.patients_list:
                if p.get("id") == study.patient_id:
                    matched_label = (
                        f"{p.get('first_name')} {p.get('last_name')} (DNI: {p.get('dni')})"
                        if p.get("dni")
                        else f"{p.get('first_name')} {p.get('last_name')}"
                    )
                    break

            self.form_patient_id = matched_label or str(study.patient_id)
            self.form_study_type = study.study_type
            self.form_study_name = study.study_name
            self.form_study_date = str(study.study_date)
            self.form_institution = study.institution or ""
            self.form_requesting_doctor = study.requesting_doctor or ""
            self.form_results = study.results or ""
            self.form_observations = study.observations or ""
            self.form_diagnosis = study.diagnosis or ""

            # No cargamos los archivos existentes para edición
            self.uploaded_files = []

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
                # Obtener datos del paciente
                patient = session.get(Patient, study.patient_id)

                # Convertir a diccionario con datos del paciente
                self.detail_study = {
                    "id": study.id,
                    "patient_id": study.patient_id,
                    "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "",
                    "patient_dni": patient.dni if patient else "",
                    "study_type": study.study_type
                    if isinstance(study.study_type, str)
                    else study.study_type.value,
                    "study_name": study.study_name,
                    "study_date": study.study_date.strftime("%d/%m/%Y") if study.study_date else "",
                    "institution": study.institution or "",
                    "requesting_doctor": study.requesting_doctor or "",
                    "results": study.results or "",
                    "diagnosis": study.diagnosis or "",
                    "observations": study.observations or "",
                    "file_path": study.file_path or "",
                    "file_name": study.file_name or "",
                }

                self.show_detail_modal = True

                # Cargar archivos del estudio
                from app.services import StudyFileService

                files = StudyFileService.get_files_by_study(session, study_id)
                self.study_files = [
                    {
                        "id": f.id,
                        "file_name": f.file_name,
                        "file_size_kb": f"{(f.file_size / 1024):.1f} KB",
                        "file_type": f.file_type,
                        "created_at": f.uploaded_at.strftime("%d/%m/%Y %H:%M")
                        if f.uploaded_at
                        else "",
                    }
                    for f in files
                ]
        finally:
            session.close()

    def close_detail_modal(self):
        """Cierra el modal de detalle"""
        self.show_detail_modal = False
        self.detail_study = None
        self.study_files = []  # Limpiar archivos al cerrar

    def download_study_file(self, file_id: int):
        """Descarga un archivo individual del estudio"""
        session = next(get_session())
        try:
            from app.services import StudyFileService

            file_path, file_name = StudyFileService.download_file(session, file_id)
            print(f"🚀 Descargando archivo de estudio: {file_name} ({file_path})")

            # Leer archivo y enviar bytes directamente
            with open(file_path, "rb") as f:
                file_data = f.read()

            return rx.download(data=file_data, filename=file_name)
        except Exception as e:
            print(f"❌ Error al descargar archivo: {e}")
            return rx.window_alert(f"Error al descargar archivo: {str(e)}")

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
        self.message = ""

    async def handle_upload(self, files: list[rx.UploadFile]):
        """
        Maneja la carga de múltiples archivos seleccionados.
        Lee el contenido de cada archivo y lo guarda temporalmente en memoria.
        """
        print("📁 DEBUG UPLOAD: handle_upload llamado")
        print(f"📁 DEBUG UPLOAD: files recibidos: {len(files)} archivo(s)")

        if not files:
            print("⚠️ DEBUG UPLOAD: No hay archivos en la lista")
            return

        import base64

        # Procesar todos los archivos
        uploaded_list = []
        for idx, file in enumerate(files):
            print(f"📁 DEBUG UPLOAD [{idx + 1}/{len(files)}]: Procesando {file.filename}")
            print(f"📁 DEBUG UPLOAD: Tamaño: {file.size} bytes")
            print(f"📁 DEBUG UPLOAD: Tipo: {file.content_type}")

            try:
                file_data = await file.read()
                print(f"✅ DEBUG UPLOAD: Contenido leído: {len(file_data)} bytes")

                uploaded_list.append(
                    {
                        "data": base64.b64encode(file_data).decode("utf-8"),
                        "name": file.filename,
                        "size": file.size or len(file_data),
                        "type": file.content_type or "application/octet-stream",
                    }
                )
                print(f"✅ DEBUG UPLOAD: Archivo {file.filename} cargado correctamente")
            except Exception as e:
                print(f"❌ DEBUG UPLOAD: Error al leer archivo {file.filename}: {e}")
                self.message = f"Error al cargar archivo {file.filename}: {str(e)}"
                self.message_type = "error"

        self.uploaded_files = uploaded_list
        print(f"✅ DEBUG UPLOAD: Total {len(uploaded_list)} archivos listos para guardar")

    def remove_uploaded_file(self, index: int):
        """Elimina un archivo subido por índice"""
        if 0 <= index < len(self.uploaded_files):
            removed = self.uploaded_files.pop(index)
            print(f"🗑️ Archivo eliminado: {removed['name']}")

    def create_study(self):
        """Crea un nuevo estudio médico"""
        try:
            if not self.form_patient_id or not self.form_study_name:
                self.message = "Complete los campos requeridos"
                self.message_type = "error"
                return

            # Activar indicador de carga
            self.is_uploading = True
            self.upload_progress = "Creando estudio..."

            session = next(get_session())
            try:
                # Validar que el paciente existe (resolver label a id si aplica)
                resolved_id = self._resolve_patient_id_from_form() or int(self.form_patient_id)
                patient = session.get(Patient, resolved_id)
                if not patient:
                    self.message = f"Paciente con ID {self.form_patient_id} no encontrado"
                    self.message_type = "error"
                    return

                # Crear el estudio en la base de datos
                study = MedicalStudyService.create_study(
                    session=session,
                    patient_id=resolved_id,
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
                if self.uploaded_files and self.uploaded_files[0]:
                    import base64
                    from io import BytesIO

                    self.upload_progress = "Subiendo archivo..."
                    print("📤 DEBUG CREATE: Procesando archivo cargado...")

                    try:
                        # Decodificar el contenido desde base64
                        file_data = base64.b64decode(self.uploaded_files[0])
                        file_io = BytesIO(file_data)

                        print(f"✅ DEBUG CREATE: Contenido decodificado: {len(file_data)} bytes")

                        result = MedicalStudyService.upload_file(
                            session=session,
                            study_id=study.id,
                            file_content=file_io,
                            file_name=self.file_name,
                            file_type=self.file_type,
                        )
                        print(f"✅ DEBUG CREATE: Archivo guardado en: {result.file_path}")
                        self.message = f"Estudio '{self.form_study_name}' creado exitosamente con archivo adjunto"
                    except Exception as e:
                        print(f"❌ DEBUG CREATE: Error al procesar archivo: {e}")
                        self.message = f"Estudio creado pero error al guardar archivo: {str(e)}"
                else:
                    print("ℹ️ DEBUG CREATE: No hay archivos para subir")
                    self.message = f"Estudio '{self.form_study_name}' creado exitosamente"

                self.message_type = "success"
                
                # Desactivar indicador de carga
                self.is_uploading = False
                self.upload_progress = ""
                
                self.close_new_study_modal()
                self.load_studies(self.selected_patient_id)
            finally:
                session.close()

        except Exception as e:
            self.is_uploading = False
            self.upload_progress = ""
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

            # Activar indicador de carga
            self.is_uploading = True
            self.upload_progress = "Actualizando estudio..."

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

                # Subir nuevos archivos si existen (soporte para múltiples archivos)
                if self.uploaded_files:
                    import base64
                    from io import BytesIO

                    total_files = len(self.uploaded_files)
                    print(f"📤 DEBUG UPDATE: Procesando {total_files} archivo(s)...")

                    files_saved = 0
                    for idx, file_info in enumerate(self.uploaded_files):
                        # Actualizar progreso
                        self.upload_progress = f"Subiendo archivo {idx + 1} de {total_files}..."
                        
                        try:
                            # Decodificar el contenido desde base64
                            file_data = base64.b64decode(file_info["data"])
                            file_io = BytesIO(file_data)

                            print(
                                f"✅ DEBUG UPDATE [{idx + 1}/{total_files}]: Guardando {file_info['name']} ({len(file_data)} bytes)"
                            )

                            result = MedicalStudyService.upload_file(
                                session=session,
                                study_id=study.id,
                                file_content=file_io,
                                file_name=file_info["name"],
                                file_type=file_info["type"],
                            )
                            print(f"✅ DEBUG UPDATE: Archivo guardado en: {result.file_path}")
                            files_saved += 1
                        except Exception as e:
                            print(f"❌ DEBUG UPDATE: Error al procesar {file_info['name']}: {e}")

                    if files_saved == total_files:
                        self.message = f"Estudio '{self.form_study_name}' actualizado exitosamente con {files_saved} archivo(s) nuevo(s)"
                    elif files_saved > 0:
                        self.message = f"Estudio actualizado con {files_saved}/{total_files} archivos guardados"
                    else:
                        self.message = "Estudio actualizado pero error al guardar archivos"
                else:
                    print("ℹ️ DEBUG UPDATE: No hay archivos para subir")
                    self.message = f"Estudio '{self.form_study_name}' actualizado exitosamente"

                self.message_type = "success"
                
                # Desactivar indicador de carga
                self.is_uploading = False
                self.upload_progress = ""
                
                self.close_new_study_modal()
                self.load_studies(self.selected_patient_id)
            finally:
                session.close()

        except Exception as e:
            self.is_uploading = False
            self.upload_progress = ""
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
        print(f"🔽 DEBUG: download_file llamado con study_id={study_id}")
        session = next(get_session())
        try:
            result = MedicalStudyService.download_file(session, study_id)

            if result:
                file_path, file_name = result
                print(f"✓ Archivo encontrado: {file_name}")
                print(f"✓ Ruta: {file_path}")
                print(f"✓ Existe: {file_path.exists()}")

                # Leer archivo y enviar bytes directamente (funciona sin endpoint HTTP)
                with open(file_path, "rb") as f:
                    file_data = f.read()

                print(f"✓ Leídos {len(file_data)} bytes")
                print(f"🚀 Descargando: {file_name}")

                return rx.download(data=file_data, filename=file_name)
            else:
                print(f"❌ No se encontró archivo para estudio {study_id}")

        except Exception as e:
            self.message = f"Error al descargar archivo: {str(e)}"
            self.message_type = "error"
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            session.close()
