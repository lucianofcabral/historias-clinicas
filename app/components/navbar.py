"""Componente de barra de navegación"""

import reflex as rx

from app.config import APP_NAME, COLORS
from app.state.auth_state import AuthState


def navbar() -> rx.Component:
    """Barra de navegación superior con tema oscuro"""
    return rx.box(
        rx.hstack(
            # Logo y nombre
            rx.hstack(
                rx.icon("heart-pulse", size=28, color=COLORS["primary"]),
                rx.heading(APP_NAME, size="6", color=COLORS["text"]),
                spacing="3",
            ),
            # Navegación
            rx.hstack(
                rx.link(
                    rx.button(
                        rx.icon("layout-dashboard", size=18),
                        "Dashboard",
                        variant="ghost",
                        color_scheme="gray",
                    ),
                    href="/dashboard",
                ),
                rx.link(
                    rx.button(
                        rx.icon("users", size=18),
                        "Pacientes",
                        variant="ghost",
                        color_scheme="gray",
                    ),
                    href="/patients",
                ),
                rx.link(
                    rx.button(
                        rx.icon("file-text", size=18),
                        "Estudios",
                        variant="ghost",
                        color_scheme="gray",
                    ),
                    href="/studies",
                ),
                spacing="2",
            ),
            # Usuario y logout
            rx.hstack(
                rx.button(
                    rx.icon("log-out", size=18),
                    "Cerrar Sesión",
                    on_click=AuthState.logout,
                    variant="outline",
                    color_scheme="red",
                    size="2",
                ),
                spacing="3",
            ),
            justify="between",
            align="center",
            width="100%",
            padding_x="2rem",
        ),
        background=COLORS["navbar"],
        padding_y="1rem",
        border_bottom=f"1px solid {COLORS['border']}",
        width="100%",
        position="sticky",
        top="0",
        z_index="1000",
    )
