"""Modelo de Consulta Médica"""

from datetime import UTC, date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Consultation(SQLModel, table=True):
    """
    Modelo de Consulta Médica.

    Registra cada visita del paciente al consultorio con todos los
    detalles de la consulta, signos vitales, diagnóstico y tratamiento.
    """

    __tablename__ = "consultations"

    # ID y relación con paciente
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id", index=True)

    # Datos de la consulta
    consultation_date: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    reason: str = Field(description="Motivo de consulta")
    symptoms: Optional[str] = Field(default=None, description="Síntomas del paciente")
    diagnosis: Optional[str] = Field(default=None, description="Diagnóstico médico")
    treatment: Optional[str] = Field(default=None, description="Tratamiento indicado")
    notes: Optional[str] = Field(default=None, description="Notas adicionales")

    # Signos vitales
    blood_pressure: Optional[str] = Field(
        default=None, max_length=20, description="Presión arterial (ej: 120/80)"
    )
    heart_rate: Optional[int] = Field(
        default=None, description="Frecuencia cardíaca (pulsaciones por minuto)"
    )
    temperature: Optional[float] = Field(default=None, description="Temperatura corporal (°C)")
    weight: Optional[float] = Field(default=None, description="Peso (kg)")
    height: Optional[float] = Field(default=None, description="Altura (cm)")

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Próxima visita
    next_visit: Optional[date] = Field(
        default=None, description="Fecha programada para próxima visita"
    )

    @property
    def bmi(self) -> Optional[float]:
        """
        Calcula el Índice de Masa Corporal (IMC/BMI)

        Returns:
            float: IMC calculado o None si no hay datos suficientes
        """
        if self.weight and self.height:
            height_m = self.height / 100  # Convertir cm a metros
            return round(self.weight / (height_m**2), 2)
        return None

    @property
    def bmi_category(self) -> Optional[str]:
        """
        Categoriza el IMC según estándares de la OMS

        Returns:
            str: Categoría del IMC o None
        """
        bmi = self.bmi
        if bmi is None:
            return None

        if bmi < 18.5:
            return "Bajo peso"
        elif 18.5 <= bmi < 25:
            return "Peso normal"
        elif 25 <= bmi < 30:
            return "Sobrepeso"
        else:
            return "Obesidad"

    @property
    def has_vital_signs(self) -> bool:
        """Verifica si tiene al menos un signo vital registrado"""
        return any(
            [
                self.blood_pressure,
                self.heart_rate,
                self.temperature,
                self.weight,
                self.height,
            ]
        )

    def __repr__(self) -> str:
        return (
            f"<Consultation {self.id}: Patient {self.patient_id} - {self.consultation_date.date()}>"
        )

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": 1,
                "reason": "Control de rutina",
                "symptoms": "Dolor de cabeza ocasional",
                "diagnosis": "Cefalea tensional",
                "treatment": "Paracetamol 500mg cada 8 horas por 5 días",
                "blood_pressure": "120/80",
                "heart_rate": 72,
                "temperature": 36.5,
                "weight": 70.5,
                "height": 175.0,
                "notes": "Paciente estable, recomendar ejercicio regular",
                "next_visit": "2025-11-17",
            }
        }
    }
