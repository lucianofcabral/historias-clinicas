"""Estado para gestión de pacientes"""

from datetime import date
from typing import Optional

import reflex as rx

from app.database import get_session
from app.models import Patient
from app.services import PatientService


class PatientState(rx.State):
    """Estado para gestión de la lista de pacientes"""

    # Lista de pacientes
    patients: list[Patient] = []
    current_patient: Optional[Patient] = None

    # Filtros y búsqueda
    search_query: str = ""
    filter_gender: str = "Todos"
    show_inactive: bool = False

    # Estadísticas
    total_patients: int = 0
    active_patients: int = 0

    # Modal de nuevo paciente
    show_new_patient_modal: bool = False

    # Formulario de nuevo paciente
    form_first_name: str = ""
    form_last_name: str = ""
    form_dni: str = ""
    form_birth_date: str = ""
    form_gender: str = "M"
    form_blood_type: str = ""
    form_phone: str = ""
    form_email: str = ""
    form_address: str = ""
    form_allergies: str = ""
    form_chronic_conditions: str = ""
    form_family_history: str = ""
    form_notes: str = ""

    # Mensajes
    message: str = ""
    message_type: str = ""  # "success" o "error"

    def load_patients(self):
        """Carga todos los pacientes"""
        session = next(get_session())
        try:
            self.patients = PatientService.get_all_patients(
                session, include_inactive=self.show_inactive
            )
            self.total_patients = PatientService.get_patient_count(session, include_inactive=True)
            self.active_patients = PatientService.get_patient_count(session, include_inactive=False)
        finally:
            session.close()

    def search_patients(self):
        """Busca pacientes por nombre o DNI"""
        session = next(get_session())
        try:
            if self.search_query.strip():
                # Buscar por término
                results = PatientService.search_patients(session, self.search_query)

                # Aplicar filtros adicionales
                if self.filter_gender != "Todos":
                    results = [p for p in results if p.gender == self.filter_gender]

                if not self.show_inactive:
                    results = [p for p in results if p.is_active]

                self.patients = results
            else:
                # Sin búsqueda, cargar todos con filtros
                self.load_patients()
        finally:
            session.close()

    def filter_by_gender(self, gender: str):
        """Filtra pacientes por género"""
        self.filter_gender = gender
        self.search_patients()

    def toggle_show_inactive(self):
        """Alterna mostrar/ocultar pacientes inactivos"""
        self.show_inactive = not self.show_inactive
        self.search_patients()

    def open_new_patient_modal(self):
        """Abre el modal para crear nuevo paciente"""
        self.show_new_patient_modal = True
        self.clear_form()

    def close_new_patient_modal(self):
        """Cierra el modal de nuevo paciente"""
        self.show_new_patient_modal = False
        self.clear_form()

    def clear_form(self):
        """Limpia el formulario"""
        self.form_first_name = ""
        self.form_last_name = ""
        self.form_dni = ""
        self.form_birth_date = ""
        self.form_gender = "M"
        self.form_blood_type = ""
        self.form_phone = ""
        self.form_email = ""
        self.form_address = ""
        self.form_allergies = ""
        self.form_chronic_conditions = ""
        self.form_family_history = ""
        self.form_notes = ""
        self.message = ""

    def create_patient(self):
        """Crea un nuevo paciente"""
        try:
            # Validar campos requeridos
            if not self.form_first_name or not self.form_last_name or not self.form_dni:
                self.message = "Complete los campos requeridos: Nombre, Apellido y DNI"
                self.message_type = "error"
                return

            if not self.form_birth_date:
                self.message = "Complete la fecha de nacimiento"
                self.message_type = "error"
                return

            session = next(get_session())
            try:
                # Verificar que el DNI no exista
                existing = PatientService.get_patient_by_dni(session, self.form_dni)
                if existing:
                    self.message = f"Ya existe un paciente con DNI {self.form_dni}"
                    self.message_type = "error"
                    return

                # Crear diccionario con datos del paciente
                patient_data = {
                    "first_name": self.form_first_name,
                    "last_name": self.form_last_name,
                    "dni": self.form_dni,
                    "birth_date": date.fromisoformat(self.form_birth_date),
                    "gender": self.form_gender,
                    "blood_type": self.form_blood_type or None,
                    "phone": self.form_phone or None,
                    "email": self.form_email or None,
                    "address": self.form_address or None,
                    "allergies": self.form_allergies or None,
                    "chronic_conditions": self.form_chronic_conditions or None,
                    "family_history": self.form_family_history or None,
                    "notes": self.form_notes or None,
                }

                patient = PatientService.create_patient(session, patient_data)

                self.message = f"Paciente {patient.full_name} creado exitosamente"
                self.message_type = "success"
                self.close_new_patient_modal()
                self.load_patients()

            finally:
                session.close()

        except Exception as e:
            self.message = f"Error al crear paciente: {str(e)}"
            self.message_type = "error"

    def delete_patient(self, patient_id: int):
        """Elimina (desactiva) un paciente"""
        try:
            session = next(get_session())
            try:
                PatientService.delete_patient(session, patient_id)
                self.message = "Paciente desactivado exitosamente"
                self.message_type = "success"
                self.load_patients()
            finally:
                session.close()
        except Exception as e:
            self.message = f"Error al desactivar paciente: {str(e)}"
            self.message_type = "error"

    def view_patient(self, patient_id: int):
        """Ver detalles de un paciente"""
        session = next(get_session())
        try:
            self.current_patient = session.get(Patient, patient_id)
        finally:
            session.close()
