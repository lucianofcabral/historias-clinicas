"""Servicio de gestión de pacientes"""

from datetime import UTC, datetime
from typing import Optional

from sqlmodel import Session, or_, select

from app.models import Patient
from app.utils.validators import (
    normalize_dni,
    normalize_phone,
    normalize_text,
    validate_dni,
    validate_email,
)


class PatientService:
    """
    Servicio para gestionar operaciones CRUD de pacientes.

    Proporciona métodos para crear, leer, actualizar y eliminar (soft delete)
    pacientes en el sistema.
    """

    @staticmethod
    def create_patient(session: Session, patient_data: dict) -> Patient:
        """
        Crea un nuevo paciente en la base de datos.

        Args:
            session: Sesión de base de datos
            patient_data: Diccionario con los datos del paciente

        Returns:
            Patient: Paciente creado

        Raises:
            ValueError: Si el DNI ya existe o los datos son inválidos
        """
        # Normalizar y validar DNI
        dni = patient_data.get("dni", "")
        normalized_dni = normalize_dni(dni)

        if not validate_dni(normalized_dni):
            raise ValueError(f"DNI inválido: {dni}")

        # Verificar si el DNI ya existe
        existing = session.exec(select(Patient).where(Patient.dni == normalized_dni)).first()

        if existing:
            raise ValueError(f"Ya existe un paciente con DNI {dni}")

        # Normalizar otros campos
        patient_data["dni"] = normalized_dni

        if "first_name" in patient_data:
            patient_data["first_name"] = normalize_text(patient_data["first_name"])

        if "last_name" in patient_data:
            patient_data["last_name"] = normalize_text(patient_data["last_name"])

        if "phone" in patient_data and patient_data["phone"]:
            patient_data["phone"] = normalize_phone(patient_data["phone"])

        # Validar email si existe
        if "email" in patient_data and patient_data["email"]:
            if not validate_email(patient_data["email"]):
                raise ValueError(f"Email inválido: {patient_data['email']}")

        # Crear nuevo paciente
        patient = Patient(**patient_data)
        session.add(patient)
        session.commit()
        session.refresh(patient)

        return patient

    @staticmethod
    def get_patient_by_id(session: Session, patient_id: int) -> Optional[Patient]:
        """
        Obtiene un paciente por su ID.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente

        Returns:
            Patient o None si no existe
        """
        return session.get(Patient, patient_id)

    @staticmethod
    def get_patient_by_dni(session: Session, dni: str) -> Optional[Patient]:
        """
        Obtiene un paciente por su DNI (normaliza antes de buscar).

        Args:
            session: Sesión de base de datos
            dni: DNI del paciente (puede tener puntos, guiones, etc.)

        Returns:
            Patient o None si no existe
        """
        normalized_dni = normalize_dni(dni)
        return session.exec(select(Patient).where(Patient.dni == normalized_dni)).first()

    @staticmethod
    def get_all_patients(session: Session, include_inactive: bool = False) -> list[Patient]:
        """
        Obtiene todos los pacientes.

        Args:
            session: Sesión de base de datos
            include_inactive: Si incluir pacientes inactivos

        Returns:
            Lista de pacientes
        """
        query = select(Patient)

        if not include_inactive:
            query = query.where(Patient.is_active == True)  # noqa: E712

        query = query.order_by(Patient.last_name, Patient.first_name)

        return list(session.exec(query).all())

    @staticmethod
    def search_patients(session: Session, search_term: str) -> list[Patient]:
        """
        Busca pacientes por nombre, apellido o DNI.
        Normaliza el DNI antes de buscar para encontrar coincidencias
        incluso si se busca con puntos o guiones.

        Args:
            session: Sesión de base de datos
            search_term: Término de búsqueda

        Returns:
            Lista de pacientes que coinciden
        """
        search_pattern = f"%{search_term}%"

        # También buscar por DNI normalizado
        normalized_dni = normalize_dni(search_term)
        dni_pattern = f"%{normalized_dni}%"

        query = (
            select(Patient)
            .where(
                or_(
                    Patient.first_name.ilike(search_pattern),
                    Patient.last_name.ilike(search_pattern),
                    Patient.dni.ilike(search_pattern),
                    Patient.dni.ilike(dni_pattern),  # Buscar por DNI normalizado
                )
            )
            .where(Patient.is_active == True)  # noqa: E712
            .order_by(Patient.last_name, Patient.first_name)
        )

        return list(session.exec(query).all())

    @staticmethod
    def update_patient(session: Session, patient_id: int, update_data: dict) -> Optional[Patient]:
        """
        Actualiza los datos de un paciente.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente
            update_data: Diccionario con los datos a actualizar

        Returns:
            Patient actualizado o None si no existe

        Raises:
            ValueError: Si intenta cambiar DNI a uno ya existente o datos inválidos
        """
        patient = session.get(Patient, patient_id)

        if not patient:
            return None

        # Normalizar y validar DNI si se está actualizando
        if "dni" in update_data:
            dni = update_data["dni"]
            normalized_dni = normalize_dni(dni)

            if not validate_dni(normalized_dni):
                raise ValueError(f"DNI inválido: {dni}")

            # Verificar que no exista otro paciente con ese DNI
            if normalized_dni != patient.dni:
                existing = session.exec(
                    select(Patient).where(Patient.dni == normalized_dni)
                ).first()

                if existing:
                    raise ValueError(f"Ya existe un paciente con DNI {dni}")

            update_data["dni"] = normalized_dni

        # Normalizar nombres si se están actualizando
        if "first_name" in update_data:
            update_data["first_name"] = normalize_text(update_data["first_name"])

        if "last_name" in update_data:
            update_data["last_name"] = normalize_text(update_data["last_name"])

        # Normalizar teléfono si se está actualizando
        if "phone" in update_data and update_data["phone"]:
            update_data["phone"] = normalize_phone(update_data["phone"])

        # Validar email si se está actualizando
        if "email" in update_data and update_data["email"]:
            if not validate_email(update_data["email"]):
                raise ValueError(f"Email inválido: {update_data['email']}")

        # Actualizar campos
        for key, value in update_data.items():
            if hasattr(patient, key) and key not in ["id", "created_at"]:
                setattr(patient, key, value)

        # Actualizar timestamp
        patient.updated_at = datetime.now(UTC)

        session.add(patient)
        session.commit()
        session.refresh(patient)

        return patient

    @staticmethod
    def delete_patient(session: Session, patient_id: int) -> bool:
        """
        Elimina (soft delete) un paciente.

        No borra físicamente el paciente, solo lo marca como inactivo.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente

        Returns:
            True si se eliminó correctamente, False si no existe
        """
        patient = session.get(Patient, patient_id)

        if not patient:
            return False

        patient.is_active = False
        patient.updated_at = datetime.now(UTC)

        session.add(patient)
        session.commit()

        return True

    @staticmethod
    def restore_patient(session: Session, patient_id: int) -> bool:
        """
        Restaura un paciente previamente eliminado.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente

        Returns:
            True si se restauró correctamente, False si no existe
        """
        patient = session.get(Patient, patient_id)

        if not patient:
            return False

        patient.is_active = True
        patient.updated_at = datetime.now(UTC)

        session.add(patient)
        session.commit()

        return True

    @staticmethod
    def get_patient_count(session: Session, include_inactive: bool = False) -> int:
        """
        Obtiene el total de pacientes.

        Args:
            session: Sesión de base de datos
            include_inactive: Si incluir pacientes inactivos

        Returns:
            Número total de pacientes
        """
        query = select(Patient)

        if not include_inactive:
            query = query.where(Patient.is_active == True)  # noqa: E712

        return len(list(session.exec(query).all()))
