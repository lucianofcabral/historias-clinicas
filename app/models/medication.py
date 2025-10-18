"""Modelo de Medicación"""

from datetime import UTC, date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Medication(SQLModel, table=True):
    """
    Modelo de Medicación prescrita.

    Registra los medicamentos prescritos a cada paciente, con dosificación,
    frecuencia y duración del tratamiento.
    """

    __tablename__ = "medications"

    # ID y relaciones
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id", index=True)
    consultation_id: Optional[int] = Field(default=None, foreign_key="consultations.id", index=True)

    # Información del medicamento
    name: str = Field(max_length=200, description="Nombre del medicamento")
    dosage: str = Field(max_length=100, description="Dosificación (ej: 500mg)")
    frequency: str = Field(max_length=100, description="Frecuencia de toma (ej: cada 8 horas)")
    duration: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Duración del tratamiento (ej: 7 días)",
    )

    # Fechas del tratamiento
    start_date: date = Field(default_factory=date.today, description="Fecha de inicio")
    end_date: Optional[date] = Field(default=None, description="Fecha de finalización")

    # Información adicional
    notes: Optional[str] = Field(default=None, description="Notas adicionales sobre el medicamento")
    is_chronic: bool = Field(default=False, description="Indica si es medicación crónica")
    is_active: bool = Field(default=True, description="Medicamento activo")

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_ongoing(self) -> bool:
        """
        Verifica si el medicamento está en curso

        Returns:
            bool: True si está activo y no ha finalizado
        """
        if not self.is_active:
            return False

        if self.is_chronic:
            return True

        if self.end_date is None:
            return True

        return date.today() <= self.end_date

    @property
    def days_remaining(self) -> Optional[int]:
        """
        Calcula los días restantes del tratamiento

        Returns:
            int: Días restantes o None si no tiene fecha de fin
        """
        if self.end_date is None or self.is_chronic:
            return None

        remaining = (self.end_date - date.today()).days
        return max(0, remaining)

    @property
    def treatment_duration_days(self) -> Optional[int]:
        """
        Calcula la duración total del tratamiento en días

        Returns:
            int: Duración en días o None si no tiene fecha de fin
        """
        if self.end_date is None:
            return None

        return (self.end_date - self.start_date).days

    def __repr__(self) -> str:
        return f"<Medication {self.id}: {self.name} - Patient {self.patient_id}>"

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": 1,
                "consultation_id": 5,
                "name": "Paracetamol",
                "dosage": "500mg",
                "frequency": "Cada 8 horas",
                "duration": "7 días",
                "start_date": "2025-10-17",
                "end_date": "2025-10-24",
                "notes": "Tomar con las comidas",
                "is_chronic": False,
                "is_active": True,
            }
        }
    }
