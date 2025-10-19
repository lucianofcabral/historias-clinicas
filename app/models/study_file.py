"""Modelo para archivos adjuntos relacionados con estudios médicos"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class StudyFile(SQLModel, table=True):
    """Archivos adjuntos asociados a estudios médicos (relación 1:N)"""

    __tablename__ = "study_files"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Key
    study_id: int = Field(foreign_key="medical_studies.id", index=True)

    # Información del archivo
    file_path: str = Field(index=True)  # Ruta relativa desde STUDIES_PATH
    file_name: str  # Nombre original del archivo
    file_type: str  # Tipo MIME (application/pdf, image/jpeg, etc.)
    file_size: int  # Tamaño en bytes

    # Metadatos
    description: Optional[str] = Field(default=None)  # Descripción opcional del archivo
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationship (opcional)
    # study: Optional["MedicalStudy"] = Relationship(back_populates="files")

    @property
    def file_path_absolute(self) -> Path:
        """Retorna la ruta absoluta del archivo"""
        from app.config import STUDIES_PATH

        return STUDIES_PATH / self.file_path

    @property
    def file_size_kb(self) -> float:
        """Tamaño del archivo en KB"""
        return round(self.file_size / 1024, 2)

    @property
    def file_size_mb(self) -> float:
        """Tamaño del archivo en MB"""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def file_extension(self) -> str:
        """Extensión del archivo"""
        return Path(self.file_name).suffix.lower()

    @property
    def is_image(self) -> bool:
        """Verifica si es una imagen"""
        return self.file_type.startswith("image/")

    @property
    def is_pdf(self) -> bool:
        """Verifica si es un PDF"""
        return self.file_type == "application/pdf"

    def __repr__(self) -> str:
        return f"<StudyFile {self.file_name} (Study #{self.study_id})>"

    model_config = {
        "json_schema_extra": {
            "example": {
                "study_id": 5,
                "file_path": "patient_1/study_5_20250118_124530_radiografia_torax.jpg",
                "file_name": "radiografia_torax.jpg",
                "file_type": "image/jpeg",
                "file_size": 1234567,
                "description": "Radiografía de tórax - proyección frontal",
            }
        }
    }
