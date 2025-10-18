"""Lógica de negocio y servicios"""

from app.services.consultation_service import ConsultationService
from app.services.medical_study_service import MedicalStudyService
from app.services.patient_service import PatientService

__all__ = ["ConsultationService", "MedicalStudyService", "PatientService"]
