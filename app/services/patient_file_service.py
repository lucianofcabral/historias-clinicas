"""Servicio para gestionar archivos adjuntos directos de pacientes"""

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

from sqlmodel import Session, select

from app.config import PATIENTS_PATH
from app.models.patient_file import FileCategory, PatientFile


class PatientFileService:
    """Servicio para operaciones CRUD de archivos de pacientes"""

    @staticmethod
    def create_file(
        session: Session,
        patient_id: int,
        file_content: BytesIO,
        file_name: str,
        file_type: str,
        file_category: str = FileCategory.DOCUMENT.value,
        description: Optional[str] = None,
    ) -> PatientFile:
        """
        Guarda un archivo adjunto directamente relacionado con un paciente.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente
            file_content: Contenido del archivo (BytesIO)
            file_name: Nombre original del archivo
            file_type: Tipo MIME del archivo
            file_category: Categoría del archivo (FileCategory)
            description: Descripción opcional del archivo

        Returns:
            PatientFile creado y guardado
        """
        from app.models import Patient

        # Verificar que el paciente existe
        patient = session.get(Patient, patient_id)
        if not patient:
            raise ValueError(f"Paciente {patient_id} no encontrado")

        # Obtener el tamaño del archivo
        file_content.seek(0, 2)  # Ir al final
        file_size = file_content.tell()
        file_content.seek(0)  # Volver al inicio

        # Generar nombre único para el archivo
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        safe_filename = file_name.replace(" ", "_")
        unique_filename = f"patient_{patient_id}_{timestamp}_{safe_filename}"

        # Crear directorio del paciente si no existe
        patient_dir = PATIENTS_PATH / f"patient_{patient_id}"
        patient_dir.mkdir(parents=True, exist_ok=True)

        # Ruta completa del archivo
        file_absolute_path = patient_dir / unique_filename
        file_relative_path = f"patient_{patient_id}/{unique_filename}"

        # Guardar archivo físico
        with open(file_absolute_path, "wb") as f:
            f.write(file_content.read())

        # Crear registro en la base de datos
        patient_file = PatientFile(
            patient_id=patient_id,
            file_category=file_category,
            file_path=file_relative_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            description=description,
        )

        session.add(patient_file)
        session.commit()
        session.refresh(patient_file)

        return patient_file

    @staticmethod
    def get_files_by_patient(
        session: Session, patient_id: int, category: Optional[str] = None
    ) -> list[PatientFile]:
        """
        Obtiene todos los archivos directos de un paciente.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente
            category: Filtrar por categoría (opcional)

        Returns:
            Lista de archivos del paciente
        """
        statement = select(PatientFile).where(PatientFile.patient_id == patient_id)

        if category:
            statement = statement.where(PatientFile.file_category == category)

        statement = statement.order_by(PatientFile.uploaded_at.desc())
        return list(session.exec(statement).all())

    @staticmethod
    def get_file(session: Session, file_id: int) -> Optional[PatientFile]:
        """Obtiene un archivo por su ID"""
        return session.get(PatientFile, file_id)

    @staticmethod
    def download_file(session: Session, file_id: int) -> Optional[tuple[Path, str]]:
        """
        Obtiene la ruta absoluta y nombre de un archivo para descarga.

        Returns:
            Tupla (ruta_absoluta, nombre_archivo) o None si no existe
        """
        patient_file = session.get(PatientFile, file_id)
        if not patient_file:
            return None

        file_path = patient_file.file_path_absolute
        if not file_path.exists():
            return None

        return file_path, patient_file.file_name

    @staticmethod
    def delete_file(session: Session, file_id: int) -> bool:
        """
        Elimina un archivo (registro en DB y archivo físico).

        Returns:
            True si se eliminó correctamente, False si no existe
        """
        patient_file = session.get(PatientFile, file_id)
        if not patient_file:
            return False

        # Eliminar archivo físico si existe
        file_path = patient_file.file_path_absolute
        if file_path.exists():
            file_path.unlink()

        # Eliminar registro de la base de datos
        session.delete(patient_file)
        session.commit()

        return True

    @staticmethod
    def get_total_size_by_patient(session: Session, patient_id: int) -> int:
        """Calcula el tamaño total de archivos directos de un paciente (en bytes)"""
        files = PatientFileService.get_files_by_patient(session, patient_id)
        return sum(f.file_size for f in files)

    @staticmethod
    def get_files_by_category(session: Session, patient_id: int) -> dict[str, list[PatientFile]]:
        """
        Obtiene archivos del paciente organizados por categoría.

        Returns:
            Diccionario {categoria: [archivos]}
        """
        files = PatientFileService.get_files_by_patient(session, patient_id)
        result: dict[str, list[PatientFile]] = {}

        for file in files:
            category = file.file_category
            if category not in result:
                result[category] = []
            result[category].append(file)

        return result
