"""Modelo para archivos adjuntos directamente relacionados con pacientes"""

from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class FileCategory(str, Enum):
    """Categorías de archivos de paciente"""

    DOCUMENT = "Documento"
    IMAGE = "Imagen"
    LAB_RESULT = "Resultado de Laboratorio"
    PRESCRIPTION = "Receta"
    INSURANCE = "Obra Social/Seguro"
    CONSENT = "Consentimiento"
    OTHER = "Otro"


class PatientFile(SQLModel, table=True):
    """Archivos adjuntos asociados directamente a un paciente"""

    __tablename__ = "patient_files"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Key
    patient_id: int = Field(foreign_key="patients.id", index=True)

    # Categoría del archivo
    file_category: str = Field(default=FileCategory.DOCUMENT.value, index=True)

    # Información del archivo
    file_path: str = Field(index=True)  # Ruta relativa desde PATIENTS_PATH
    file_name: str  # Nombre original del archivo
    file_type: str  # Tipo MIME (application/pdf, image/jpeg, etc.)
    file_size: int  # Tamaño en bytes

    # Metadatos
    description: Optional[str] = Field(default=None)  # Descripción opcional
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationship (opcional, si quieres acceso bidireccional)
    # patient: Optional["Patient"] = Relationship(back_populates="files")

    @property
    def file_path_absolute(self) -> Path:
        """Retorna la ruta absoluta del archivo"""
        from app.config import PATIENTS_PATH

        return PATIENTS_PATH / self.file_path

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
        return f"<PatientFile {self.file_name} ({self.file_category})>"

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": 1,
                "file_category": "Documento",
                "file_path": "patient_1/consent_form_20250118.pdf",
                "file_name": "consentimiento_informado.pdf",
                "file_type": "application/pdf",
                "file_size": 245678,
                "description": "Consentimiento informado firmado",
            }
        }
    }
