"""Página de Login"""

import reflex as rx

from app.config import APP_NAME, COLORS
from app.state.auth_state import AuthState


class LoginPageState(rx.State):
    """Estado local de la página de login"""

    password: str = ""


def login_page() -> rx.Component:
    """Página de login con diseño oscuro"""
    return rx.center(
        rx.vstack(
            # Logo/Header
            rx.heading(
                "🏥 " + APP_NAME,
                size="9",
                color=COLORS["primary"],
                margin_bottom="1rem",
            ),
            rx.text(
                "Sistema de Gestión de Historias Clínicas",
                color=COLORS["text_secondary"],
                margin_bottom="2rem",
            ),
            # Card de login
            rx.card(
                rx.vstack(
                    rx.heading("Iniciar Sesión", size="7", margin_bottom="1rem"),
                    # Campo de contraseña
                    rx.vstack(
                        rx.text(
                            "Contraseña",
                            color=COLORS["text"],
                            font_weight="500",
                        ),
                        rx.input(
                            type="password",
                            placeholder="Ingrese su contraseña",
                            value=LoginPageState.password,
                            on_change=LoginPageState.set_password,
                            on_blur=AuthState.set_login_error(""),
                            width="100%",
                            size="3",
                        ),
                        width="100%",
                        spacing="2",
                    ),
                    # Mensaje de error
                    rx.cond(
                        AuthState.login_error != "",
                        rx.callout(
                            AuthState.login_error,
                            icon="triangle_alert",
                            color_scheme="red",
                            size="1",
                            width="100%",
                        ),
                    ),
                    # Botón de login
                    rx.button(
                        rx.cond(
                            AuthState.is_loading,
                            rx.hstack(
                                rx.spinner(size="2"),
                                rx.text("Verificando..."),
                                spacing="2",
                            ),
                            rx.text("Ingresar"),
                        ),
                        on_click=AuthState.login(LoginPageState.password),
                        width="100%",
                        size="3",
                        disabled=AuthState.is_loading,
                    ),
                    spacing="4",
                    width="100%",
                ),
                width="400px",
                padding="2rem",
            ),
            # Footer
            rx.text(
                "Versión 0.1.0 - 2025",
                color=COLORS["text_secondary"],
                font_size="0.875rem",
                margin_top="2rem",
            ),
            spacing="4",
            align="center",
        ),
        height="100vh",
        background=COLORS["background"],
    )
