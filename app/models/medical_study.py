"""Modelo de Estudios y Análisis Médicos"""

from datetime import UTC, date, datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from sqlmodel import Field, SQLModel


class StudyType(str, Enum):
    """Tipos de estudios médicos"""

    LABORATORY = "Laboratorio"
    RADIOLOGY = "Radiología"
    ULTRASOUND = "Ecografía"
    TOMOGRAPHY = "Tomografía"
    RESONANCE = "Resonancia"
    ELECTROCARDIOGRAM = "Electrocardiograma"
    ENDOSCOPY = "Endoscopía"
    BIOPSY = "Biopsia"
    OTHER = "Otro"


class MedicalStudy(SQLModel, table=True):
    """Modelo para estudios y análisis médicos con archivos adjuntos"""

    __tablename__ = "medical_studies"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relaciones
    patient_id: int = Field(foreign_key="patients.id", index=True)
    consultation_id: Optional[int] = Field(default=None, foreign_key="consultations.id", index=True)

    # Información del estudio
    study_type: str = Field(index=True)  # Tipo de estudio
    study_name: str = Field(index=True)  # Nombre específico
    study_date: date = Field(index=True)  # Fecha de realización
    institution: Optional[str] = Field(default=None)  # Institución
    requesting_doctor: Optional[str] = Field(default=None)  # Médico solicitante

    # Resultados
    results: Optional[str] = Field(default=None)  # Resultados en texto
    observations: Optional[str] = Field(default=None)  # Observaciones
    diagnosis: Optional[str] = Field(default=None)  # Diagnóstico derivado

    # Archivos adjuntos
    file_path: Optional[str] = Field(default=None)  # Ruta al archivo
    file_name: Optional[str] = Field(default=None)  # Nombre original
    file_type: Optional[str] = Field(default=None)  # Tipo MIME
    file_size: Optional[int] = Field(default=None)  # Tamaño en bytes

    # Estado
    is_pending: bool = Field(default=True)  # Pendiente de resultados
    is_critical: bool = Field(default=False)  # Crítico
    requires_followup: bool = Field(default=False)  # Requiere seguimiento

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def days_since_study(self) -> int:
        """Días desde que se realizó el estudio"""
        today = date.today()
        return (today - self.study_date).days

    @property
    def is_recent(self) -> bool:
        """Verifica si el estudio es reciente (menos de 30 días)"""
        return self.days_since_study <= 30

    @property
    def has_files(self) -> bool:
        """Verifica si tiene archivos adjuntos"""
        return self.file_path is not None

    @property
    def file_path_absolute(self) -> Optional[Path]:
        """Retorna la ruta absoluta del archivo"""
        if not self.file_path:
            return None
        from app.config import BASE_DIR

        return BASE_DIR / self.file_path

    @property
    def file_size_mb(self) -> Optional[float]:
        """Tamaño del archivo en MB"""
        if not self.file_size:
            return None
        return round(self.file_size / (1024 * 1024), 2)

    def __repr__(self) -> str:
        return f"<MedicalStudy {self.study_name} ({self.study_date})>"

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": 1,
                "consultation_id": 5,
                "study_type": "Laboratorio",
                "study_name": "Hemograma completo",
                "study_date": "2025-01-15",
                "institution": "Laboratorio Central",
                "results": "Glóbulos rojos: 4.5 millones/mm³",
                "file_path": "studies/patient_1/2025-01-15_hemograma.pdf",
                "file_name": "hemograma.pdf",
                "file_type": "application/pdf",
                "is_pending": False,
            }
        }
    }
