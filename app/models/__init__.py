"""Modelos de base de datos"""

from app.models.consultation import Consultation
from app.models.medication import Medication
from app.models.patient import Patient

__all__ = ["Patient", "Consultation", "Medication"]
