"""Página principal del Dashboard"""

import reflex as rx
from sqlmodel import func, select

from app.components.navbar import navbar
from app.config import COLORS
from app.database import get_session
from app.models import MedicalStudy, Patient


class DashboardState(rx.State):
    """Estado del dashboard"""

    total_patients: int = 0
    active_patients: int = 0
    pending_studies: int = 0
    recent_patients: list[dict] = []

    def on_load(self):
        """Se ejecuta al cargar la página"""
        session = next(get_session())

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

        # Últimos 5 pacientes registrados
        recent = session.exec(
            select(Patient).where(Patient.is_active).order_by(Patient.created_at.desc()).limit(5)
        ).all()

        self.recent_patients = [
            {
                "id": p.id,
                "name": f"{p.first_name} {p.last_name}",
                "dni": p.dni,
                "created_at": p.created_at.strftime("%d/%m/%Y"),
            }
            for p in recent
        ]


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
                    margin_bottom="1rem",
                ),
                # Estadísticas
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
                        "user_check",
                        COLORS["success"],
                    ),
                    stat_card(
                        "Estudios Pendientes",
                        DashboardState.pending_studies.to_string(),
                        "flask_conical",
                        COLORS["warning"],
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                # Últimos pacientes registrados
                rx.heading(
                    "Pacientes Registrados Recientemente",
                    size="6",
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
                    rx.text(
                        "No hay pacientes registrados aún",
                        color=COLORS["text_secondary"],
                    ),
                ),
                # Acciones rápidas
                rx.heading(
                    "Acciones Rápidas",
                    size="6",
                    color=COLORS["text"],
                    margin_top="2rem",
                    margin_bottom="1rem",
                ),
                rx.hstack(
                    rx.link(
                        rx.button(
                            rx.icon("user-plus", size=20),
                            "Nuevo Paciente",
                            size="3",
                            color_scheme="blue",
                        ),
                        href="/patients",
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("flask_conical", size=20),
                            "Nuevo Estudio",
                            size="3",
                            color_scheme="green",
                        ),
                        href="/medical_studies",
                    ),
                    spacing="3",
                ),
                spacing="4",
                padding_y="2rem",
            ),
            max_width="1200px",
        ),
        background=COLORS["background"],
        min_height="100vh",
        on_mount=DashboardState.on_load,
    )
