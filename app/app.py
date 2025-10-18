"""Aplicación principal de Reflex"""

import reflex as rx

from app.config import COLORS
from app.pages.dashboard import dashboard_page
from app.pages.login import login_page

# Crear la aplicación
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="blue",
        gray_color="slate",
        radius="medium",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)

# Agregar páginas
app.add_page(login_page, route="/", title="Login - Historias Clínicas")

app.add_page(
    dashboard_page,
    route="/dashboard",
    title="Dashboard - Historias Clínicas",
)


# Página de pacientes (placeholder por ahora)
@rx.page(route="/patients", title="Pacientes - Historias Clínicas")
def patients_page() -> rx.Component:
    """Página de lista de pacientes (placeholder)"""
    from app.components.navbar import navbar

    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Pacientes", size="8", color=COLORS["text"]),
                rx.text(
                    "Lista de pacientes - En construcción",
                    color=COLORS["text_secondary"],
                ),
                spacing="4",
                padding_y="2rem",
            ),
            max_width="1200px",
        ),
        background=COLORS["background"],
        min_height="100vh",
    )
