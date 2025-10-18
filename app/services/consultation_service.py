"""
Servicio para gestionar consultas médicas.
"""

from datetime import date, datetime
from typing import Optional

from sqlmodel import Session, select

from app.models import Consultation
from app.utils.text_utils import normalize_search_term


class ConsultationService:
    """Servicio para operaciones CRUD de consultas médicas."""

    @staticmethod
    def create_consultation(
        session: Session,
        patient_id: int,
        reason: str,
        symptoms: Optional[str] = None,
        diagnosis: Optional[str] = None,
        treatment: Optional[str] = None,
        notes: Optional[str] = None,
        blood_pressure: Optional[str] = None,
        heart_rate: Optional[int] = None,
        temperature: Optional[float] = None,
        weight: Optional[float] = None,
        height: Optional[float] = None,
        next_visit: Optional[date] = None,
        consultation_date: Optional[datetime] = None,
    ) -> Consultation:
        """
        Crea una nueva consulta médica.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente
            reason: Motivo de la consulta
            symptoms: Síntomas reportados
            diagnosis: Diagnóstico médico
            treatment: Tratamiento indicado
            notes: Notas adicionales
            blood_pressure: Presión arterial (ej: "120/80")
            heart_rate: Frecuencia cardíaca (ppm)
            temperature: Temperatura corporal (°C)
            weight: Peso en kg
            height: Altura en cm
            next_visit: Fecha de próxima visita
            consultation_date: Fecha de la consulta (default: ahora)

        Returns:
            Consultation: Consulta creada
        """
        consultation = Consultation(
            patient_id=patient_id,
            reason=reason,
            symptoms=symptoms,
            diagnosis=diagnosis,
            treatment=treatment,
            notes=notes,
            blood_pressure=blood_pressure,
            heart_rate=heart_rate,
            temperature=temperature,
            weight=weight,
            height=height,
            next_visit=next_visit,
        )

        if consultation_date:
            consultation.consultation_date = consultation_date

        session.add(consultation)
        session.commit()
        session.refresh(consultation)
        return consultation

    @staticmethod
    def get_consultation_by_id(session: Session, consultation_id: int) -> Optional[Consultation]:
        """
        Obtiene una consulta por su ID.

        Args:
            session: Sesión de base de datos
            consultation_id: ID de la consulta

        Returns:
            Consultation: Consulta encontrada o None
        """
        return session.get(Consultation, consultation_id)

    @staticmethod
    def get_consultations_by_patient(
        session: Session, patient_id: int, limit: Optional[int] = None
    ) -> list[Consultation]:
        """
        Obtiene todas las consultas de un paciente.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente
            limit: Número máximo de consultas (None = todas)

        Returns:
            list[Consultation]: Lista de consultas ordenadas por fecha descendente
        """
        query = (
            select(Consultation)
            .where(Consultation.patient_id == patient_id)
            .order_by(Consultation.consultation_date.desc())
        )

        if limit:
            query = query.limit(limit)

        return list(session.exec(query).all())

    @staticmethod
    def get_all_consultations(session: Session, limit: Optional[int] = None) -> list[Consultation]:
        """
        Obtiene todas las consultas del sistema.

        Args:
            session: Sesión de base de datos
            limit: Número máximo de consultas (None = todas)

        Returns:
            list[Consultation]: Lista de consultas ordenadas por fecha descendente
        """
        query = select(Consultation).order_by(Consultation.consultation_date.desc())

        if limit:
            query = query.limit(limit)

        return list(session.exec(query).all())

    @staticmethod
    def search_consultations(
        session: Session, search_term: str, limit: Optional[int] = None
    ) -> list[Consultation]:
        """
        Busca consultas por motivo, síntomas, diagnóstico o tratamiento.

        Nota: SQLite no soporta comparación sin acentos nativamente,
        por lo que filtramos en Python después de obtener los resultados.

        Args:
            session: Sesión de base de datos
            search_term: Término de búsqueda
            limit: Número máximo de resultados

        Returns:
            list[Consultation]: Lista de consultas que coinciden con la búsqueda
        """
        # Normalizar término de búsqueda (sin acentos, minúsculas)
        normalized_search = normalize_search_term(search_term)

        # Obtener todas las consultas (o más de las que necesitamos para filtrar)
        query = select(Consultation).order_by(Consultation.consultation_date.desc())

        # Obtener más resultados de los necesarios para poder filtrar
        all_consultations = list(session.exec(query).all())

        # Filtrar en Python comparando sin acentos
        filtered = []
        for consultation in all_consultations:
            # Normalizar campos y buscar
            reason_norm = normalize_search_term(consultation.reason or "")
            symptoms_norm = normalize_search_term(consultation.symptoms or "")
            diagnosis_norm = normalize_search_term(consultation.diagnosis or "")
            treatment_norm = normalize_search_term(consultation.treatment or "")

            if (
                normalized_search in reason_norm
                or normalized_search in symptoms_norm
                or normalized_search in diagnosis_norm
                or normalized_search in treatment_norm
            ):
                filtered.append(consultation)

                # Aplicar límite si está definido
                if limit and len(filtered) >= limit:
                    break

        return filtered

    @staticmethod
    def get_recent_consultations(session: Session, days: int = 30) -> list[Consultation]:
        """
        Obtiene consultas recientes.

        Args:
            session: Sesión de base de datos
            days: Número de días hacia atrás (default: 30)

        Returns:
            list[Consultation]: Lista de consultas recientes
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        return list(
            session.exec(
                select(Consultation)
                .where(Consultation.consultation_date >= cutoff_date)
                .order_by(Consultation.consultation_date.desc())
            ).all()
        )

    @staticmethod
    def update_consultation(
        session: Session,
        consultation_id: int,
        **kwargs,
    ) -> Optional[Consultation]:
        """
        Actualiza una consulta existente.

        Args:
            session: Sesión de base de datos
            consultation_id: ID de la consulta
            **kwargs: Campos a actualizar

        Returns:
            Consultation: Consulta actualizada o None si no existe
        """
        consultation = session.get(Consultation, consultation_id)
        if not consultation:
            return None

        for key, value in kwargs.items():
            if hasattr(consultation, key):
                setattr(consultation, key, value)

        consultation.updated_at = datetime.now()
        session.add(consultation)
        session.commit()
        session.refresh(consultation)
        return consultation

    @staticmethod
    def delete_consultation(session: Session, consultation_id: int) -> bool:
        """
        Elimina una consulta.

        Args:
            session: Sesión de base de datos
            consultation_id: ID de la consulta

        Returns:
            bool: True si se eliminó, False si no existe
        """
        consultation = session.get(Consultation, consultation_id)
        if not consultation:
            return False

        session.delete(consultation)
        session.commit()
        return True

    @staticmethod
    def get_consultation_count(session: Session, patient_id: Optional[int] = None) -> int:
        """
        Cuenta las consultas totales o de un paciente específico.

        Args:
            session: Sesión de base de datos
            patient_id: ID del paciente (None = todas las consultas)

        Returns:
            int: Número de consultas
        """
        from sqlmodel import func

        query = select(func.count(Consultation.id))

        if patient_id:
            query = query.where(Consultation.patient_id == patient_id)

        return session.exec(query).one()
