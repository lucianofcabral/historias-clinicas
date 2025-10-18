"""Modelo de Paciente"""

from datetime import UTC, date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Patient(SQLModel, table=True):
    """
    Modelo de Paciente para el sistema de historias clínicas.

    Contiene toda la información personal y médica básica del paciente.
    """

    __tablename__ = "patients"

    # ID y datos principales
    id: Optional[int] = Field(default=None, primary_key=True)

    # Datos personales
    first_name: str = Field(max_length=100, index=True)
    last_name: str = Field(max_length=100, index=True)
    dni: str = Field(unique=True, index=True, max_length=20)
    birth_date: date
    gender: str = Field(max_length=10)  # M, F, Otro
    blood_type: Optional[str] = Field(default=None, max_length=5)

    # Contacto
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None)

    # Información médica básica
    allergies: Optional[str] = Field(default=None)  # Texto libre
    chronic_conditions: Optional[str] = Field(default=None)  # Texto libre
    family_history: Optional[str] = Field(default=None)  # Texto libre

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = Field(default=True)  # Para "eliminar" sin borrar

    # Notas generales
    notes: Optional[str] = Field(default=None)

    @property
    def full_name(self) -> str:
        """Retorna el nombre completo del paciente"""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        """Calcula la edad actual del paciente"""
        today = date.today()
        age = today.year - self.birth_date.year
        # Ajustar si no ha cumplido años este año
        if (today.month, today.day) < (
            self.birth_date.month,
            self.birth_date.day,
        ):
            age -= 1
        return age

    def __repr__(self) -> str:
        return f"<Patient {self.dni}: {self.full_name}>"

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Juan",
                "last_name": "Pérez",
                "dni": "12345678",
                "birth_date": "1990-01-15",
                "gender": "M",
                "blood_type": "O+",
                "phone": "+54 11 1234-5678",
                "email": "juan.perez@example.com",
                "address": "Av. Corrientes 1234, CABA",
                "allergies": "Penicilina",
                "chronic_conditions": "Hipertensión",
                "family_history": "Padre con diabetes tipo 2",
                "notes": "Paciente regular, buena adherencia al tratamiento",
            }
        }
    }
