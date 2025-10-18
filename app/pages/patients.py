"""Página de lista y gestión de pacientes"""

import reflex as rx

from app.config import BLOOD_TYPES, COLORS, GENDERS
from app.state.patient_state import PatientState


def patient_card(patient) -> rx.Component:
    """Tarjeta de paciente con información resumida"""
    return rx.card(
        rx.vstack(
            # Header con nombre y estado
            rx.hstack(
                rx.vstack(
                    rx.heading(patient.full_name, size="5"),
                    rx.text(
                        f"DNI: {patient.dni}",
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.cond(
                    patient.is_active,
                    rx.badge("Activo", color_scheme="green"),
                    rx.badge("Inactivo", color_scheme="gray"),
                ),
                width="100%",
                align="center",
            ),
            # Información básica
            rx.vstack(
                rx.hstack(
                    rx.icon("calendar", size=16, color=COLORS["text_secondary"]),
                    rx.text(
                        patient.birth_date,
                        size="2",
                    ),
                    spacing="2",
                ),
                rx.cond(
                    patient.phone,
                    rx.hstack(
                        rx.icon("phone", size=16, color=COLORS["text_secondary"]),
                        rx.text(patient.phone, size="2"),
                        spacing="2",
                    ),
                    rx.box(),
                ),
                rx.cond(
                    patient.email,
                    rx.hstack(
                        rx.icon("mail", size=16, color=COLORS["text_secondary"]),
                        rx.text(patient.email, size="2"),
                        spacing="2",
                    ),
                    rx.box(),
                ),
                rx.cond(
                    patient.blood_type,
                    rx.hstack(
                        rx.icon("droplet", size=16, color=COLORS["text_secondary"]),
                        rx.text(f"Grupo: {patient.blood_type}", size="2"),
                        spacing="2",
                    ),
                    rx.box(),
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            # Acciones
            rx.hstack(
                rx.button(
                    rx.icon("eye", size=16),
                    "Ver Historial",
                    variant="soft",
                    size="2",
                    on_click=rx.redirect(f"/patients/{patient.id}"),
                ),
                rx.button(
                    rx.icon("pen", size=16),
                    "Editar",
                    variant="soft",
                    color_scheme="blue",
                    size="2",
                    on_click=lambda: PatientState.open_edit_patient_modal(patient.id),
                ),
                rx.button(
                    rx.icon("trash-2", size=16),
                    variant="soft",
                    color_scheme="red",
                    size="2",
                    on_click=lambda: PatientState.delete_patient(patient.id),
                ),
                spacing="2",
                width="100%",
                margin_top="0.5rem",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        style={
            "background": COLORS["surface"],
            "border": f"1px solid {COLORS['border']}",
            "width": "100%",
        },
    )


def new_patient_modal() -> rx.Component:
    """Modal para crear/editar paciente"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    PatientState.editing_patient_id.is_none(),
                    "Nuevo Paciente",
                    "Editar Paciente",
                )
            ),
            rx.dialog.description(
                "Complete la información del paciente",
                margin_bottom="1rem",
            ),
            rx.vstack(
                # Datos personales
                rx.text("DATOS PERSONALES", size="3", weight="bold", color=COLORS["primary"]),
                rx.grid(
                    # Nombre
                    rx.vstack(
                        rx.text("Nombre *", size="2", weight="bold"),
                        rx.input(
                            placeholder="Juan",
                            value=PatientState.form_first_name,
                            on_change=PatientState.set_form_first_name,
                        ),
                        spacing="1",
                        align="start",
                    ),
                    # Apellido
                    rx.vstack(
                        rx.text("Apellido *", size="2", weight="bold"),
                        rx.input(
                            placeholder="Pérez",
                            value=PatientState.form_last_name,
                            on_change=PatientState.set_form_last_name,
                        ),
                        spacing="1",
                        align="start",
                    ),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),
                rx.grid(
                    # DNI
                    rx.vstack(
                        rx.text("DNI *", size="2", weight="bold"),
                        rx.input(
                            placeholder="12345678",
                            value=PatientState.form_dni,
                            on_change=PatientState.set_form_dni,
                            type="text",
                            max_length=8,
                        ),
                        spacing="1",
                        align="start",
                    ),
                    # Fecha de nacimiento
                    rx.vstack(
                        rx.text("Fecha de Nacimiento *", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=PatientState.form_birth_date,
                            on_change=PatientState.set_form_birth_date,
                        ),
                        spacing="1",
                        align="start",
                    ),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),
                rx.grid(
                    # Género
                    rx.vstack(
                        rx.text("Género *", size="2", weight="bold"),
                        rx.select(
                            GENDERS,
                            value=PatientState.form_gender,
                            on_change=PatientState.set_form_gender,
                        ),
                        spacing="1",
                        align="start",
                    ),
                    # Grupo sanguíneo
                    rx.vstack(
                        rx.text("Grupo Sanguíneo", size="2", weight="bold"),
                        rx.select(
                            BLOOD_TYPES,
                            placeholder="Seleccionar",
                            value=PatientState.form_blood_type,
                            on_change=PatientState.set_form_blood_type,
                        ),
                        spacing="1",
                        align="start",
                    ),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),
                # Contacto
                rx.text("CONTACTO", size="3", weight="bold", color=COLORS["primary"]),
                rx.grid(
                    # Teléfono
                    rx.vstack(
                        rx.text("Teléfono", size="2", weight="bold"),
                        rx.input(
                            placeholder="011-1234-5678",
                            value=PatientState.form_phone,
                            on_change=PatientState.set_form_phone,
                            type="tel",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    # Email
                    rx.vstack(
                        rx.text("Email", size="2", weight="bold"),
                        rx.input(
                            placeholder="paciente@email.com",
                            value=PatientState.form_email,
                            on_change=PatientState.set_form_email,
                            type="email",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),
                # Dirección
                rx.vstack(
                    rx.text("Dirección", size="2", weight="bold"),
                    rx.input(
                        placeholder="Calle 123, Ciudad",
                        value=PatientState.form_address,
                        on_change=PatientState.set_form_address,
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                # Información médica
                rx.text("INFORMACIÓN MÉDICA", size="3", weight="bold", color=COLORS["primary"]),
                rx.vstack(
                    rx.text("Alergias", size="2", weight="bold"),
                    rx.text_area(
                        placeholder="Describir alergias conocidas...",
                        value=PatientState.form_allergies,
                        on_change=PatientState.set_form_allergies,
                        rows="2",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Condiciones Crónicas", size="2", weight="bold"),
                    rx.text_area(
                        placeholder="Diabetes, hipertensión, etc...",
                        value=PatientState.form_chronic_conditions,
                        on_change=PatientState.set_form_chronic_conditions,
                        rows="2",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Antecedentes Familiares", size="2", weight="bold"),
                    rx.text_area(
                        placeholder="Enfermedades hereditarias...",
                        value=PatientState.form_family_history,
                        on_change=PatientState.set_form_family_history,
                        rows="2",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Notas Adicionales", size="2", weight="bold"),
                    rx.text_area(
                        placeholder="Información adicional...",
                        value=PatientState.form_notes,
                        on_change=PatientState.set_form_notes,
                        rows="2",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                # Mensaje de error/éxito
                rx.cond(
                    PatientState.message != "",
                    rx.callout(
                        PatientState.message,
                        color_scheme=rx.cond(
                            PatientState.message_type == "success",
                            "green",
                            "red",
                        ),
                        size="2",
                    ),
                    rx.box(),
                ),
                spacing="3",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.button(
                    rx.cond(
                        PatientState.editing_patient_id.is_none(),
                        "Crear Paciente",
                        "Guardar Cambios",
                    ),
                    on_click=PatientState.save_patient,
                ),
                spacing="3",
                margin_top="1rem",
                justify="end",
            ),
            style={
                "max_width": "700px",
                "max_height": "80vh",
                "overflow_y": "auto",
                "background": COLORS["background"],
            },
        ),
        open=PatientState.show_new_patient_modal,
        on_open_change=PatientState.set_show_new_patient_modal,
    )


def patients_page() -> rx.Component:
    """Página principal de lista de pacientes"""
    from app.components.navbar import navbar

    return rx.box(
        new_patient_modal(),
        navbar(),
        rx.container(
            rx.vstack(
                # Header
                rx.heading("Pacientes", size="8"),
                rx.text(
                    "Gestión de pacientes del consultorio",
                    size="3",
                    color=COLORS["text_secondary"],
                ),
                # Stats
                rx.hstack(
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("users", size=24, color=COLORS["primary"]),
                                rx.text(
                                    "Total de Pacientes",
                                    size="2",
                                    color=COLORS["text_secondary"],
                                ),
                            ),
                            rx.heading(
                                PatientState.total_patients,
                                size="6",
                            ),
                            spacing="2",
                            align="start",
                        ),
                        style={"background": COLORS["surface"]},
                    ),
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("user-check", size=24, color=COLORS["success"]),
                                rx.text(
                                    "Pacientes Activos",
                                    size="2",
                                    color=COLORS["text_secondary"],
                                ),
                            ),
                            rx.heading(
                                PatientState.active_patients,
                                size="6",
                            ),
                            spacing="2",
                            align="start",
                        ),
                        style={"background": COLORS["surface"]},
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("plus", size=20),
                        "Nuevo Paciente",
                        size="3",
                        on_click=PatientState.open_new_patient_modal,
                    ),
                    width="100%",
                    spacing="4",
                ),
                # Búsqueda y filtros
                rx.hstack(
                    rx.input(
                        placeholder="Buscar por nombre o DNI...",
                        value=PatientState.search_query,
                        on_change=PatientState.set_search_query,
                        on_blur=PatientState.search_patients,
                        width="100%",
                        size="3",
                    ),
                    rx.select(
                        ["Todos", "M", "F", "Otro"],
                        placeholder="Género",
                        value=PatientState.filter_gender,
                        on_change=PatientState.filter_by_gender,
                        size="3",
                    ),
                    rx.button(
                        rx.icon("filter", size=18),
                        rx.cond(
                            PatientState.show_inactive,
                            "Ocultar Inactivos",
                            "Mostrar Inactivos",
                        ),
                        variant="soft",
                        size="3",
                        on_click=PatientState.toggle_show_inactive,
                    ),
                    width="100%",
                    spacing="3",
                ),
                # Lista de pacientes
                rx.cond(
                    PatientState.patients.length() > 0,
                    rx.grid(
                        rx.foreach(
                            PatientState.patients,
                            patient_card,
                        ),
                        columns="3",
                        spacing="4",
                        width="100%",
                    ),
                    rx.callout(
                        "No se encontraron pacientes",
                        icon="info",
                        color_scheme="blue",
                    ),
                ),
                spacing="6",
                width="100%",
                padding_y="2rem",
            ),
            max_width="1400px",
        ),
        on_mount=PatientState.load_patients,
        style={
            "background": COLORS["background"],
            "min_height": "100vh",
        },
    )
