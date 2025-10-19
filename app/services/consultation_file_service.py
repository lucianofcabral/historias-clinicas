"""Servicio para gestionar archivos adjuntos de consultas médicas"""

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

from sqlmodel import Session, select

from app.config import STUDIES_PATH
from app.models.consultation_file import ConsultationFile


class ConsultationFileService:
    """Servicio para operaciones CRUD de archivos de consultas"""

    @staticmethod
    def create_file(
        session: Session,
        consultation_id: int,
        file_content: BytesIO,
        file_name: str,
        file_type: str,
        description: Optional[str] = None,
    ) -> ConsultationFile:
        """
        Guarda un archivo adjunto para una consulta médica.

        Args:
            session: Sesión de base de datos
            consultation_id: ID de la consulta
            file_content: Contenido del archivo (BytesIO)
            file_name: Nombre original del archivo
            file_type: Tipo MIME del archivo
            description: Descripción opcional del archivo

        Returns:
            ConsultationFile creado y guardado
        """
        from app.models import Consultation

        # Verificar que la consulta existe
        consultation = session.get(Consultation, consultation_id)
        if not consultation:
            raise ValueError(f"Consulta {consultation_id} no encontrada")

        # Obtener el tamaño del archivo
        file_content.seek(0, 2)  # Ir al final
        file_size = file_content.tell()
        file_content.seek(0)  # Volver al inicio

        # Generar nombre único para el archivo
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        safe_filename = file_name.replace(" ", "_")
        unique_filename = f"consultation_{consultation_id}_{timestamp}_{safe_filename}"

        # Crear directorio del paciente si no existe
        patient_dir = STUDIES_PATH / f"patient_{consultation.patient_id}"
        patient_dir.mkdir(parents=True, exist_ok=True)

        # Ruta completa del archivo
        file_absolute_path = patient_dir / unique_filename
        file_relative_path = f"patient_{consultation.patient_id}/{unique_filename}"

        # Guardar archivo físico
        with open(file_absolute_path, "wb") as f:
            f.write(file_content.read())

        # Crear registro en la base de datos
        consultation_file = ConsultationFile(
            consultation_id=consultation_id,
            file_path=file_relative_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            description=description,
        )

        session.add(consultation_file)
        session.commit()
        session.refresh(consultation_file)

        return consultation_file

    @staticmethod
    def get_files_by_consultation(session: Session, consultation_id: int) -> list[ConsultationFile]:
        """Obtiene todos los archivos de una consulta específica"""
        statement = (
            select(ConsultationFile)
            .where(ConsultationFile.consultation_id == consultation_id)
            .order_by(ConsultationFile.uploaded_at)
        )
        return list(session.exec(statement).all())

    @staticmethod
    def get_file(session: Session, file_id: int) -> Optional[ConsultationFile]:
        """Obtiene un archivo por su ID"""
        return session.get(ConsultationFile, file_id)

    @staticmethod
    def download_file(session: Session, file_id: int) -> Optional[tuple[Path, str]]:
        """
        Obtiene la ruta absoluta y nombre de un archivo para descarga.

        Returns:
            Tupla (ruta_absoluta, nombre_archivo) o None si no existe
        """
        consultation_file = session.get(ConsultationFile, file_id)
        if not consultation_file:
            return None

        file_path = consultation_file.file_path_absolute
        if not file_path.exists():
            return None

        return file_path, consultation_file.file_name

    @staticmethod
    def delete_file(session: Session, file_id: int) -> bool:
        """
        Elimina un archivo (registro en DB y archivo físico).

        Returns:
            True si se eliminó correctamente, False si no existe
        """
        consultation_file = session.get(ConsultationFile, file_id)
        if not consultation_file:
            return False

        # Eliminar archivo físico si existe
        file_path = consultation_file.file_path_absolute
        if file_path.exists():
            file_path.unlink()

        # Eliminar registro de la base de datos
        session.delete(consultation_file)
        session.commit()

        return True

    @staticmethod
    def get_files_by_patient(session: Session, patient_id: int) -> list[ConsultationFile]:
        """Obtiene todos los archivos de consultas de un paciente"""
        from app.models import Consultation

        statement = (
            select(ConsultationFile)
            .join(Consultation, ConsultationFile.consultation_id == Consultation.id)
            .where(Consultation.patient_id == patient_id)
            .order_by(ConsultationFile.uploaded_at.desc())
        )
        return list(session.exec(statement).all())

    @staticmethod
    def get_total_size_by_patient(session: Session, patient_id: int) -> int:
        """Calcula el tamaño total de archivos de consultas de un paciente (en bytes)"""
        files = ConsultationFileService.get_files_by_patient(session, patient_id)
        return sum(f.file_size for f in files)
