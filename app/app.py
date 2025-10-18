"""Aplicación principal de Reflex"""

import reflex as rx

from app.pages.dashboard import dashboard_page
from app.pages.login import login_page
from app.pages.medical_studies import medical_studies_page
from app.pages.patients import patients_page

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

app.add_page(
    medical_studies_page,
    route="/studies",
    title="Estudios Médicos - Historias Clínicas",
)

# Página de pacientes
app.add_page(
    patients_page,
    route="/patients",
    title="Pacientes - Historias Clínicas",
)
