"""Modelos de base de datos"""

from app.models.consultation import Consultation
from app.models.consultation_file import ConsultationFile
from app.models.medical_study import MedicalStudy, StudyType
from app.models.medication import Medication
from app.models.patient import Patient
from app.models.patient_file import FileCategory, PatientFile
from app.models.study_file import StudyFile

__all__ = [
    "Patient",
    "Consultation",
    "Medication",
    "MedicalStudy",
    "StudyType",
    "PatientFile",
    "StudyFile",
    "ConsultationFile",
    "FileCategory",
]
