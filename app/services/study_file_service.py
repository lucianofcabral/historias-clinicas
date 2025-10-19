"""Servicio para gestionar archivos adjuntos de estudios médicos"""

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

from sqlmodel import Session, select

from app.config import STUDIES_PATH
from app.models.study_file import StudyFile


class StudyFileService:
    """Servicio para operaciones CRUD de archivos de estudios"""

    @staticmethod
    def create_file(
        session: Session,
        study_id: int,
        file_content: BytesIO,
        file_name: str,
        file_type: str,
        description: Optional[str] = None,
    ) -> StudyFile:
        """
        Guarda un archivo adjunto para un estudio médico.

        Args:
            session: Sesión de base de datos
            study_id: ID del estudio al que pertenece el archivo
            file_content: Contenido del archivo (BytesIO)
            file_name: Nombre original del archivo
            file_type: Tipo MIME del archivo
            description: Descripción opcional del archivo

        Returns:
            StudyFile creado y guardado
        """
        from app.models import MedicalStudy

        # Verificar que el estudio existe
        study = session.get(MedicalStudy, study_id)
        if not study:
            raise ValueError(f"Estudio {study_id} no encontrado")

        # Obtener el tamaño del archivo
        file_content.seek(0, 2)  # Ir al final
        file_size = file_content.tell()
        file_content.seek(0)  # Volver al inicio

        # Generar nombre único para el archivo
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        safe_filename = file_name.replace(" ", "_")
        unique_filename = f"study_{study_id}_{timestamp}_{safe_filename}"

        # Crear directorio del paciente si no existe
        patient_dir = STUDIES_PATH / f"patient_{study.patient_id}"
        patient_dir.mkdir(parents=True, exist_ok=True)

        # Ruta completa del archivo
        file_absolute_path = patient_dir / unique_filename
        file_relative_path = f"patient_{study.patient_id}/{unique_filename}"

        # Guardar archivo físico
        with open(file_absolute_path, "wb") as f:
            f.write(file_content.read())

        # Crear registro en la base de datos
        study_file = StudyFile(
            study_id=study_id,
            file_path=file_relative_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            description=description,
        )

        session.add(study_file)
        session.commit()
        session.refresh(study_file)

        return study_file

    @staticmethod
    def get_files_by_study(session: Session, study_id: int) -> list[StudyFile]:
        """Obtiene todos los archivos de un estudio específico"""
        statement = select(StudyFile).where(StudyFile.study_id == study_id).order_by(StudyFile.uploaded_at)
        return list(session.exec(statement).all())

    @staticmethod
    def get_file(session: Session, file_id: int) -> Optional[StudyFile]:
        """Obtiene un archivo por su ID"""
        return session.get(StudyFile, file_id)

    @staticmethod
    def download_file(session: Session, file_id: int) -> Optional[tuple[Path, str]]:
        """
        Obtiene la ruta absoluta y nombre de un archivo para descarga.

        Returns:
            Tupla (ruta_absoluta, nombre_archivo) o None si no existe
        """
        study_file = session.get(StudyFile, file_id)
        if not study_file:
            return None

        file_path = study_file.file_path_absolute
        if not file_path.exists():
            return None

        return file_path, study_file.file_name

    @staticmethod
    def delete_file(session: Session, file_id: int) -> bool:
        """
        Elimina un archivo (registro en DB y archivo físico).

        Returns:
            True si se eliminó correctamente, False si no existe
        """
        study_file = session.get(StudyFile, file_id)
        if not study_file:
            return False

        # Eliminar archivo físico si existe
        file_path = study_file.file_path_absolute
        if file_path.exists():
            file_path.unlink()

        # Eliminar registro de la base de datos
        session.delete(study_file)
        session.commit()

        return True

    @staticmethod
    def get_files_by_patient(session: Session, patient_id: int) -> list[StudyFile]:
        """Obtiene todos los archivos de estudios de un paciente"""
        from app.models import MedicalStudy

        statement = (
            select(StudyFile)
            .join(MedicalStudy, StudyFile.study_id == MedicalStudy.id)
            .where(MedicalStudy.patient_id == patient_id)
            .order_by(StudyFile.uploaded_at.desc())
        )
        return list(session.exec(statement).all())

    @staticmethod
    def get_total_size_by_patient(session: Session, patient_id: int) -> int:
        """Calcula el tamaño total de archivos de estudios de un paciente (en bytes)"""
        files = StudyFileService.get_files_by_patient(session, patient_id)
        return sum(f.file_size for f in files)
