"""
Servicio para gestionar estudios médicos y archivos adjuntos.
"""

import shutil
from datetime import date, datetime
from pathlib import Path
from typing import BinaryIO

from sqlmodel import Session, select

from app.config import STUDIES_PATH
from app.models import MedicalStudy, StudyType


class MedicalStudyService:
    """Servicio para operaciones CRUD de estudios médicos."""

    @staticmethod
    def create_study(
        session: Session,
        patient_id: int,
        study_type: StudyType,
        study_name: str,
        study_date: date,
        institution: str | None = None,
        results: str | None = None,
        consultation_id: int | None = None,
    ) -> MedicalStudy:
        """
        Crea un nuevo estudio médico.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente
            study_type: Tipo de estudio (StudyType enum)
            study_name: Nombre del estudio
            study_date: Fecha del estudio
            institution: Institución donde se realizó
            results: Resultados del estudio
            consultation_id: ID de la consulta relacionada (opcional)

        Returns:
            Estudio médico creado
        """
        study = MedicalStudy(
            patient_id=patient_id,
            study_type=study_type,
            study_name=study_name,
            study_date=study_date,
            institution=institution,
            results=results,
            consultation_id=consultation_id,
        )

        session.add(study)
        session.commit()
        session.refresh(study)

        return study

    @staticmethod
    def upload_file(
        session: Session,
        study_id: int,
        file_content: BinaryIO,
        file_name: str,
        file_type: str | None = None,
    ) -> MedicalStudy:
        """
        Sube un archivo al estudio médico usando StudyFileService.

        NOTA: Este método mantiene compatibilidad con código legacy.
        También actualiza campos legacy en MedicalStudy para retrocompatibilidad.

        Args:
            session: Sesión de base de datos
            study_id: ID del estudio
            file_content: Contenido del archivo (file object)
            file_name: Nombre del archivo
            file_type: Tipo MIME del archivo (opcional)

        Returns:
            Estudio médico actualizado

        Raises:
            ValueError: Si el estudio no existe
        """
        from app.services.study_file_service import StudyFileService
        from io import BytesIO

        study = session.get(MedicalStudy, study_id)
        if not study:
            raise ValueError(f"Estudio con ID {study_id} no encontrado")

        # Leer contenido en BytesIO para pasarlo al servicio
        content = file_content.read()
        file_io = BytesIO(content)

        # Crear archivo usando el nuevo servicio
        study_file = StudyFileService.create_file(
            session=session,
            study_id=study_id,
            file_content=file_io,
            file_name=file_name,
            file_type=file_type or "application/octet-stream",
        )

        # Actualizar campos legacy en MedicalStudy para compatibilidad
        study.file_name = study_file.file_name
        study.file_path = study_file.file_path
        study.file_type = study_file.file_type
        study.file_size = study_file.file_size

        session.add(study)
        session.commit()
        session.refresh(study)

        return study

    @staticmethod
    def get_study_by_id(session: Session, study_id: int) -> MedicalStudy | None:
        """
        Obtiene un estudio médico por ID.

        Args:
            session: Sesión de base de datos
            study_id: ID del estudio

        Returns:
            Estudio médico o None si no existe
        """
        return session.get(MedicalStudy, study_id)

    @staticmethod
    def get_studies_by_patient(
        session: Session,
        patient_id: int,
        study_type: StudyType | None = None,
        limit: int | None = None,
    ) -> list[MedicalStudy]:
        """
        Obtiene todos los estudios de un paciente.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente
            study_type: Filtrar por tipo de estudio (opcional)
            limit: Límite de resultados (opcional)

        Returns:
            Lista de estudios médicos ordenados por fecha descendente
        """
        statement = select(MedicalStudy).where(MedicalStudy.patient_id == patient_id)

        if study_type:
            statement = statement.where(MedicalStudy.study_type == study_type)

        statement = statement.order_by(MedicalStudy.study_date.desc())

        if limit:
            statement = statement.limit(limit)

        return list(session.exec(statement).all())

    @staticmethod
    def get_studies_by_consultation(session: Session, consultation_id: int) -> list[MedicalStudy]:
        """
        Obtiene todos los estudios relacionados a una consulta.

        Args:
            session: Sesión de base de datos
            consultation_id: ID de la consulta

        Returns:
            Lista de estudios médicos
        """
        statement = (
            select(MedicalStudy)
            .where(MedicalStudy.consultation_id == consultation_id)
            .order_by(MedicalStudy.study_date.desc())
        )

        return list(session.exec(statement).all())

    @staticmethod
    def get_recent_studies(session: Session, patient_id: int, days: int = 90) -> list[MedicalStudy]:
        """
        Obtiene estudios recientes de un paciente.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente
            days: Número de días hacia atrás (default: 90)

        Returns:
            Lista de estudios recientes
        """
        studies = MedicalStudyService.get_studies_by_patient(session, patient_id)
        return [study for study in studies if study.is_recent(days)]

    @staticmethod
    def download_file(session: Session, study_id: int) -> tuple[Path, str] | None:
        """
        Obtiene la ruta del archivo para descarga.

        NOTA: Prioriza archivos de StudyFile (nueva tabla).
        Si no hay, intenta usar campos legacy de MedicalStudy.

        Args:
            session: Sesión de base de datos
            study_id: ID del estudio

        Returns:
            Tupla (ruta_absoluta, nombre_archivo) o None si no hay archivo

        Raises:
            ValueError: Si el estudio no existe
            FileNotFoundError: Si el archivo no existe en disco
        """
        from app.services.study_file_service import StudyFileService

        study = session.get(MedicalStudy, study_id)
        if not study:
            raise ValueError(f"Estudio con ID {study_id} no encontrado")

        # Prioridad 1: Buscar en StudyFile (nueva tabla)
        files = StudyFileService.get_files_by_study(session, study_id)
        if files:
            # Retornar el primer archivo (o el más reciente)
            first_file = files[0]
            return StudyFileService.download_file(session, first_file.id)

        # Prioridad 2: Fallback a campos legacy en MedicalStudy
        if not study.has_files:
            return None

        file_path = study.file_path_absolute
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo {study.file_name} no encontrado en {file_path}")

        return file_path, study.file_name

    @staticmethod
    def delete_study_file(session: Session, study_id: int) -> MedicalStudy:
        """
        Elimina el archivo asociado a un estudio (mantiene el registro del estudio).

        Args:
            session: Sesión de base de datos
            study_id: ID del estudio

        Returns:
            Estudio médico actualizado

        Raises:
            ValueError: Si el estudio no existe
        """
        study = session.get(MedicalStudy, study_id)
        if not study:
            raise ValueError(f"Estudio con ID {study_id} no encontrado")

        if study.has_files:
            file_path = study.file_path_absolute
            if file_path.exists():
                file_path.unlink()  # Eliminar archivo físico

            # Limpiar campos del archivo en la base de datos
            study.file_name = None
            study.file_path = None
            study.file_type = None
            study.file_size = None

            session.add(study)
            session.commit()
            session.refresh(study)

        return study

    @staticmethod
    def delete_study(session: Session, study_id: int) -> bool:
        """
        Elimina completamente un estudio médico y su archivo.

        Args:
            session: Sesión de base de datos
            study_id: ID del estudio

        Returns:
            True si se eliminó correctamente

        Raises:
            ValueError: Si el estudio no existe
        """
        study = session.get(MedicalStudy, study_id)
        if not study:
            raise ValueError(f"Estudio con ID {study_id} no encontrado")

        # Eliminar archivo si existe
        if study.has_files:
            file_path = study.file_path_absolute
            if file_path.exists():
                file_path.unlink()

        # Eliminar registro de la base de datos
        session.delete(study)
        session.commit()

        return True

    @staticmethod
    def update_study(
        session: Session,
        study_id: int,
        study_name: str | None = None,
        study_date: date | None = None,
        institution: str | None = None,
        results: str | None = None,
        study_type: StudyType | None = None,
    ) -> MedicalStudy:
        """
        Actualiza la información de un estudio médico.

        Args:
            session: Sesión de base de datos
            study_id: ID del estudio
            study_name: Nuevo nombre del estudio
            study_date: Nueva fecha del estudio
            institution: Nueva institución
            results: Nuevos resultados
            study_type: Nuevo tipo de estudio

        Returns:
            Estudio médico actualizado

        Raises:
            ValueError: Si el estudio no existe
        """
        study = session.get(MedicalStudy, study_id)
        if not study:
            raise ValueError(f"Estudio con ID {study_id} no encontrado")

        if study_name is not None:
            study.study_name = study_name
        if study_date is not None:
            study.study_date = study_date
        if institution is not None:
            study.institution = institution
        if results is not None:
            study.results = results
        if study_type is not None:
            study.study_type = study_type

        session.add(study)
        session.commit()
        session.refresh(study)

        return study

    @staticmethod
    def get_studies_with_files(session: Session, patient_id: int) -> list[MedicalStudy]:
        """
        Obtiene solo los estudios que tienen archivos adjuntos.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente

        Returns:
            Lista de estudios con archivos
        """
        statement = (
            select(MedicalStudy)
            .where(MedicalStudy.patient_id == patient_id)
            .where(MedicalStudy.file_path.isnot(None))
            .order_by(MedicalStudy.study_date.desc())
        )

        return list(session.exec(statement).all())

    @staticmethod
    def get_total_storage_size(session: Session, patient_id: int | None = None) -> int:
        """
        Calcula el tamaño total de almacenamiento usado.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente (opcional, None para todos los pacientes)

        Returns:
            Tamaño total en bytes
        """
        statement = select(MedicalStudy).where(MedicalStudy.file_size.isnot(None))

        if patient_id:
            statement = statement.where(MedicalStudy.patient_id == patient_id)

        studies = session.exec(statement).all()
        return sum(study.file_size or 0 for study in studies)
