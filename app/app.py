"""Aplicación principal de Reflex"""

import reflex as rx

from app.pages.consultation_detail import consultation_detail_page
from app.pages.consultations import consultations_page
from app.pages.dashboard import dashboard_page
from app.pages.login import login_page
from app.pages.medical_studies import medical_studies_page
from app.pages.patient_detail import patient_detail_page
from app.pages.patients import patients_page
from app.pages.reports import reports_page
from app.pages.settings import settings_page

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

# Página de detalle de paciente
app.add_page(
    patient_detail_page,
    route="/patients/[patient_id]",
    title="Detalle Paciente - Historias Clínicas",
)

# Página de consultas médicas
app.add_page(
    consultations_page,
    route="/consultations",
    title="Consultas Médicas - Historias Clínicas",
)

# Página de detalle de consulta
app.add_page(
    consultation_detail_page,
    route="/consultations/[consultation_id]",
    title="Detalle Consulta - Historias Clínicas",
)

# Página de reportes y exportación
app.add_page(
    reports_page,
    route="/reports",
    title="Reportes - Historias Clínicas",
)

# Página de configuración y backups
app.add_page(
    settings_page,
    route="/settings",
    title="Configuración - Historias Clínicas",
)

# Página de estudios médicos
