"""Página principal del Dashboard"""

import reflex as rx
from sqlmodel import func, select

from app.components.navbar import navbar
from app.config import COLORS
from app.database import get_session
from app.models import MedicalStudy, Patient


class DashboardState(rx.State):
    """Estado del dashboard"""

    # Estadísticas principales
    total_patients: int = 0
    active_patients: int = 0
    pending_studies: int = 0
    critical_studies: int = 0
    total_consultations: int = 0
    consultations_this_month: int = 0
    
    # Listas
    recent_patients: list[dict] = []
    recent_consultations: list[dict] = []
    critical_studies_list: list[dict] = []
    
    # Gráficos
    studies_by_type: list[dict] = []

    def on_load(self):
        """Se ejecuta al cargar la página"""
        from datetime import datetime

        session = next(get_session())
        try:
            # ===== ESTADÍSTICAS PRINCIPALES =====
            
            # Total de pacientes
            self.total_patients = session.exec(select(func.count(Patient.id))).one()

            # Pacientes activos
            self.active_patients = session.exec(
                select(func.count(Patient.id)).where(Patient.is_active)
            ).one()

            # Estudios pendientes
            self.pending_studies = session.exec(
                select(func.count(MedicalStudy.id)).where(MedicalStudy.is_pending)
            ).one()

            # Estudios críticos
            self.critical_studies = session.exec(
                select(func.count(MedicalStudy.id)).where(MedicalStudy.is_critical)
            ).one()

            # Total de consultas
            from app.models import Consultation
            self.total_consultations = session.exec(select(func.count(Consultation.id))).one()

            # Consultas de este mes
            first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            self.consultations_this_month = session.exec(
                select(func.count(Consultation.id)).where(
                    Consultation.consultation_date >= first_day_of_month
                )
            ).one()

            # ===== ÚLTIMOS PACIENTES REGISTRADOS =====
            recent = session.exec(
                select(Patient).where(Patient.is_active).order_by(Patient.created_at.desc()).limit(5)
            ).all()

            self.recent_patients = [
                {
                    "id": p.id,
                    "name": f"{p.first_name} {p.last_name}",
                    "dni": p.dni,
                    "created_at": p.created_at.strftime("%Y-%m-%d"),
                }
                for p in recent
            ]

            # ===== ÚLTIMAS CONSULTAS =====
            recent_consults = session.exec(
                select(Consultation).order_by(Consultation.consultation_date.desc()).limit(5)
            ).all()

            self.recent_consultations = [
                {
                    "id": c.id,
                    "patient_id": c.patient_id,
                    "patient_name": self._get_patient_name(session, c.patient_id),
                    "reason": c.reason,
                    "date": c.consultation_date.strftime("%Y-%m-%d"),
                }
                for c in recent_consults
            ]

            # ===== ESTUDIOS CRÍTICOS =====
            critical = session.exec(
                select(MedicalStudy)
                .where(MedicalStudy.is_critical)
                .order_by(MedicalStudy.study_date.desc())
                .limit(5)
            ).all()

            self.critical_studies_list = [
                {
                    "id": s.id,
                    "patient_id": s.patient_id,
                    "patient_name": self._get_patient_name(session, s.patient_id),
                    "study_name": s.study_name,
                    "study_type": s.study_type,
                    "date": s.study_date.strftime("%Y-%m-%d"),
                }
                for s in critical
            ]

            # ===== DISTRIBUCIÓN DE ESTUDIOS POR TIPO =====
            from app.models import StudyType
            study_counts = []
            for study_type in StudyType:
                count = session.exec(
                    select(func.count(MedicalStudy.id)).where(
                        MedicalStudy.study_type == study_type.value
                    )
                ).one()
                if count > 0:
                    study_counts.append({
                        "type": study_type.value,
                        "count": count,
                    })
            
            self.studies_by_type = sorted(study_counts, key=lambda x: x["count"], reverse=True)

        finally:
            session.close()

    def _get_patient_name(self, session, patient_id: int) -> str:
        """Obtiene el nombre del paciente"""
        patient = session.get(Patient, patient_id)
        return f"{patient.first_name} {patient.last_name}" if patient else "Desconocido"


def stat_card(title: str, value: str, icon: str, color: str) -> rx.Component:
    """Tarjeta de estadística"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=32, color=color),
                rx.vstack(
                    rx.text(
                        title,
                        color=COLORS["text_secondary"],
                        font_size="0.875rem",
                        font_weight="500",
                    ),
                    rx.heading(value, size="7", color=COLORS["text"]),
                    spacing="1",
                    align_items="start",
                ),
                justify="between",
                width="100%",
            ),
            spacing="3",
        ),
        width="100%",
    )


def dashboard_page() -> rx.Component:
    """Página principal del dashboard con tema oscuro"""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                # Título
                rx.heading(
                    "Dashboard",
                    size="8",
                    color=COLORS["text"],
                    margin_bottom="1.5rem",
                ),
                # Estadísticas principales - Fila 1
                rx.grid(
                    stat_card(
                        "Total de Pacientes",
                        DashboardState.total_patients.to_string(),
                        "users",
                        COLORS["primary"],
                    ),
                    stat_card(
                        "Pacientes Activos",
                        DashboardState.active_patients.to_string(),
                        "user-check",
                        COLORS["success"],
                    ),
                    stat_card(
                        "Total Consultas",
                        DashboardState.total_consultations.to_string(),
                        "stethoscope",
                        COLORS["info"],
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                # Estadísticas secundarias - Fila 2
                rx.grid(
                    stat_card(
                        "Consultas Este Mes",
                        DashboardState.consultations_this_month.to_string(),
                        "calendar",
                        COLORS["primary"],
                    ),
                    stat_card(
                        "Estudios Pendientes",
                        DashboardState.pending_studies.to_string(),
                        "flask-conical",
                        COLORS["warning"],
                    ),
                    stat_card(
                        "Estudios Críticos",
                        DashboardState.critical_studies.to_string(),
                        "alert-triangle",
                        COLORS["danger"],
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                    margin_top="0.5rem",
                ),
                # Grid con 2 columnas: Alertas y Actividad Reciente
                rx.grid(
                    # Columna izquierda: Estudios Críticos
                    rx.vstack(
                        rx.heading(
                            "🚨 Estudios Críticos",
                            size="5",
                            color=COLORS["danger"],
                            margin_bottom="1rem",
                        ),
                        rx.cond(
                            DashboardState.critical_studies_list.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    DashboardState.critical_studies_list,
                                    lambda study: rx.card(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("alert-triangle", size=20, color=COLORS["danger"]),
                                                rx.text(
                                                    study["patient_name"],
                                                    font_weight="600",
                                                    color=COLORS["text"],
                                                ),
                                                rx.spacer(),
                                                rx.badge(study["study_type"], color_scheme="red"),
                                                width="100%",
                                                align="center",
                                            ),
                                            rx.text(
                                                study["study_name"],
                                                color=COLORS["text_secondary"],
                                                size="2",
                                            ),
                                            rx.text(
                                                study["date"],
                                                size="1",
                                                color=COLORS["text_secondary"],
                                            ),
                                            spacing="2",
                                            align="start",
                                            width="100%",
                                        ),
                                        style={"border_left": f"4px solid {COLORS['danger']}"},
                                    ),
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            rx.callout(
                                "No hay estudios críticos",
                                icon="check-circle",
                                color_scheme="green",
                            ),
                        ),
                        spacing="3",
                        align="start",
                        width="100%",
                    ),
                    # Columna derecha: Últimas Consultas
                    rx.vstack(
                        rx.heading(
                            "📋 Últimas Consultas",
                            size="5",
                            color=COLORS["text"],
                            margin_bottom="1rem",
                        ),
                        rx.cond(
                            DashboardState.recent_consultations.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    DashboardState.recent_consultations,
                                    lambda consult: rx.card(
                                        rx.hstack(
                                            rx.icon("stethoscope", size=20, color=COLORS["info"]),
                                            rx.vstack(
                                                rx.text(
                                                    consult["patient_name"],
                                                    font_weight="600",
                                                    color=COLORS["text"],
                                                ),
                                                rx.text(
                                                    consult["reason"],
                                                    color=COLORS["text_secondary"],
                                                    size="2",
                                                ),
                                                rx.text(
                                                    consult["date"],
                                                    size="1",
                                                    color=COLORS["text_secondary"],
                                                ),
                                                spacing="1",
                                                align="start",
                                            ),
                                            width="100%",
                                            align="start",
                                        ),
                                    ),
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            rx.callout(
                                "No hay consultas registradas",
                                icon="info",
                                color_scheme="blue",
                            ),
                        ),
                        spacing="3",
                        align="start",
                        width="100%",
                    ),
                    columns="2",
                    spacing="6",
                    width="100%",
                    margin_top="2rem",
                ),
                # Distribución de Estudios por Tipo
                rx.heading(
                    "📊 Distribución de Estudios por Tipo",
                    size="5",
                    color=COLORS["text"],
                    margin_top="2rem",
                    margin_bottom="1rem",
                ),
                rx.cond(
                    DashboardState.studies_by_type.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            DashboardState.studies_by_type,
                            lambda item: rx.card(
                                rx.hstack(
                                    rx.vstack(
                                        rx.text(
                                            item["type"],
                                            font_weight="600",
                                            color=COLORS["text"],
                                            size="3",
                                        ),
                                        rx.text(
                                            item["count"].to_string() + " estudios",
                                            color=COLORS["text_secondary"],
                                            size="2",
                                        ),
                                        spacing="1",
                                        align="start",
                                        flex="1",
                                    ),
                                    rx.spacer(),
                                    rx.heading(
                                        item["count"].to_string(),
                                        size="7",
                                        color=COLORS["primary"],
                                    ),
                                    width="100%",
                                    align="center",
                                ),
                            ),
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.callout(
                        "No hay estudios registrados",
                        icon="info",
                        color_scheme="blue",
                    ),
                ),
                # Últimos pacientes registrados
                rx.heading(
                    "👥 Pacientes Registrados Recientemente",
                    size="5",
                    color=COLORS["text"],
                    margin_top="2rem",
                    margin_bottom="1rem",
                ),
                rx.cond(
                    DashboardState.recent_patients.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            DashboardState.recent_patients,
                            lambda patient: rx.card(
                                rx.hstack(
                                    rx.icon(
                                        "user",
                                        size=24,
                                        color=COLORS["primary"],
                                    ),
                                    rx.vstack(
                                        rx.text(
                                            patient["name"],
                                            font_weight="600",
                                            color=COLORS["text"],
                                        ),
                                        rx.text(
                                            f"DNI: {patient['dni']} • Registrado: {patient['created_at']}",
                                            font_size="0.875rem",
                                            color=COLORS["text_secondary"],
                                        ),
                                        spacing="1",
                                        align_items="start",
                                    ),
                                    rx.spacer(),
                                    rx.link(
                                        rx.button(
                                            rx.icon("eye", size=16),
                                            size="2",
                                            variant="soft",
                                        ),
                                        href=f"/patients/{patient['id']}",
                                    ),
                                    width="100%",
                                    align="center",
                                ),
                            ),
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.callout(
                        "No hay pacientes registrados",
                        icon="info",
                        color_scheme="blue",
                    ),
                ),
                spacing="4",
                padding_y="2rem",
                padding_bottom="4rem",
            ),
            max_width="1400px",
        ),
        background=COLORS["background"],
        min_height="100vh",
        on_mount=DashboardState.on_load,
    )
