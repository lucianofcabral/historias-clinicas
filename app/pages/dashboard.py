"""Página principal del Dashboard"""

import reflex as rx

from app.components.navbar import navbar
from app.config import COLORS


class DashboardState(rx.State):
    """Estado del dashboard"""

    total_patients: int = 0
    consultations_today: int = 0
    active_medications: int = 0

    def on_load(self):
        """Se ejecuta al cargar la página"""
        # TODO: Cargar estadísticas reales desde la BD
        self.total_patients = 1000
        self.consultations_today = 5
        self.active_medications = 10


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
                        "Consultas Hoy",
                        DashboardState.consultations_today.to_string(),
                        "calendar_check",
                        COLORS["success"],
                    ),
                    stat_card(
                        "Medicaciones Activas",
                        DashboardState.active_medications.to_string(),
                        "pill",
                        COLORS["warning"],
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
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
                        href="/patients/new",
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("file-text", size=20),
                            "Nueva Consulta",
                            size="3",
                            color_scheme="green",
                        ),
                        href="/consultations/new",
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
