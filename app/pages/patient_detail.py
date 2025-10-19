"""Página de detalle de paciente con historial completo"""

import reflex as rx

from app.components.attachments import attachments_list_component
from app.components.patient_files import patient_files_section
from app.config import COLORS
from app.state.patient_detail_state import PatientDetailState


def patient_header() -> rx.Component:
    """Header con información del paciente"""
    return rx.cond(
        PatientDetailState.patient.is_none(),
        rx.box(),
        rx.card(
            rx.vstack(
                # Nombre y estado
                rx.hstack(
                    rx.heading(
                        PatientDetailState.patient_full_name,
                        size="7",
                    ),
                    rx.spacer(),
                    rx.badge(
                        rx.cond(
                            PatientDetailState.patient.is_active,
                            "Activo",
                            "Inactivo",
                        ),
                        color_scheme=rx.cond(
                            PatientDetailState.patient.is_active,
                            "green",
                            "gray",
                        ),
                    ),
                    width="100%",
                    align="center",
                ),
                # Información básica en grid
                rx.grid(
                    # DNI
                    rx.vstack(
                        rx.text("DNI", size="2", color=COLORS["text_secondary"]),
                        rx.text(PatientDetailState.patient.dni, size="3", weight="bold"),
                        spacing="1",
                        align="start",
                    ),
                    # Edad
                    rx.vstack(
                        rx.text("Edad", size="2", color=COLORS["text_secondary"]),
                        rx.text(
                            f"{PatientDetailState.patient_age} años",
                            size="3",
                            weight="bold",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    # Fecha de nacimiento
                    rx.vstack(
                        rx.text("Fecha de Nacimiento", size="2", color=COLORS["text_secondary"]),
                        rx.text(
                            PatientDetailState.patient_birth_date_str,
                            size="3",
                            weight="bold",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    # Género
                    rx.vstack(
                        rx.text("Género", size="2", color=COLORS["text_secondary"]),
                        rx.text(
                            rx.cond(
                                PatientDetailState.patient.gender == "M",
                                "Masculino",
                                "Femenino",
                            ),
                            size="3",
                            weight="bold",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    # Grupo sanguíneo
                    rx.cond(
                        PatientDetailState.patient.blood_type,
                        rx.vstack(
                            rx.text("Grupo Sanguíneo", size="2", color=COLORS["text_secondary"]),
                            rx.text(
                                PatientDetailState.patient.blood_type,
                                size="3",
                                weight="bold",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.box(),
                    ),
                    columns="5",
                    spacing="4",
                    width="100%",
                ),
                # Contacto
                rx.divider(),
                rx.grid(
                    rx.cond(
                        PatientDetailState.patient.phone,
                        rx.hstack(
                            rx.icon("phone", size=18, color=COLORS["primary"]),
                            rx.text(PatientDetailState.patient.phone, size="3"),
                            spacing="2",
                        ),
                        rx.box(),
                    ),
                    rx.cond(
                        PatientDetailState.patient.email,
                        rx.hstack(
                            rx.icon("mail", size=18, color=COLORS["primary"]),
                            rx.text(PatientDetailState.patient.email, size="3"),
                            spacing="2",
                        ),
                        rx.box(),
                    ),
                    rx.cond(
                        PatientDetailState.patient.address,
                        rx.hstack(
                            rx.icon("map-pin", size=18, color=COLORS["primary"]),
                            rx.text(PatientDetailState.patient.address, size="3"),
                            spacing="2",
                        ),
                        rx.box(),
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
        ),
    )


def medical_info_card() -> rx.Component:
    """Card con información médica del paciente"""
    return rx.card(
        rx.vstack(
            rx.heading("Información Médica", size="5"),
            # Alergias
            rx.cond(
                PatientDetailState.patient.allergies,
                rx.vstack(
                    rx.hstack(
                        rx.icon("circle_alert", size=18, color="red"),
                        rx.text("Alergias", size="3", weight="bold"),
                        spacing="2",
                    ),
                    rx.text(
                        PatientDetailState.patient.allergies,
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.box(),
            ),
            # Condiciones crónicas
            rx.cond(
                PatientDetailState.patient.chronic_conditions,
                rx.vstack(
                    rx.hstack(
                        rx.icon("activity", size=18, color=COLORS["primary"]),
                        rx.text("Condiciones Crónicas", size="3", weight="bold"),
                        spacing="2",
                    ),
                    rx.text(
                        PatientDetailState.patient.chronic_conditions,
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.box(),
            ),
            # Antecedentes familiares
            rx.cond(
                PatientDetailState.patient.family_history,
                rx.vstack(
                    rx.hstack(
                        rx.icon("users", size=18, color=COLORS["primary"]),
                        rx.text("Antecedentes Familiares", size="3", weight="bold"),
                        spacing="2",
                    ),
                    rx.text(
                        PatientDetailState.patient.family_history,
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.box(),
            ),
            # Notas
            rx.cond(
                PatientDetailState.patient.notes,
                rx.vstack(
                    rx.hstack(
                        rx.icon("file-text", size=18, color=COLORS["primary"]),
                        rx.text("Notas", size="3", weight="bold"),
                        spacing="2",
                    ),
                    rx.text(
                        PatientDetailState.patient.notes,
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.box(),
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
    )


def consultation_item(consultation) -> rx.Component:
    """Item de consulta en el timeline"""
    return rx.card(
        rx.vstack(
            # Fecha y motivo
            rx.hstack(
                rx.icon("calendar", size=16, color=COLORS["primary"]),
                rx.text(
                    consultation.consultation_date,
                    size="2",
                    weight="bold",
                ),
                rx.spacer(),
                rx.badge(consultation.reason, color_scheme="blue", variant="soft"),
                width="100%",
                align="center",
            ),
            # Diagnóstico
            rx.cond(
                consultation.diagnosis,
                rx.vstack(
                    rx.text("Diagnóstico:", size="2", weight="bold"),
                    rx.text(consultation.diagnosis, size="2", color=COLORS["text_secondary"]),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.box(),
            ),
            # Tratamiento
            rx.cond(
                consultation.treatment,
                rx.vstack(
                    rx.text("Tratamiento:", size="2", weight="bold"),
                    rx.text(consultation.treatment, size="2", color=COLORS["text_secondary"]),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.box(),
            ),
            # Signos vitales si existen
            rx.cond(
                consultation.has_vital_signs,
                rx.hstack(
                    rx.cond(
                        consultation.blood_pressure,
                        rx.badge(
                            f"PA: {consultation.blood_pressure}",
                            variant="soft",
                            color_scheme="red",
                        ),
                        rx.box(),
                    ),
                    rx.cond(
                        consultation.temperature,
                        rx.badge(
                            f"T: {consultation.temperature}°C",
                            variant="soft",
                            color_scheme="orange",
                        ),
                        rx.box(),
                    ),
                    rx.cond(
                        consultation.bmi,
                        rx.badge(
                            f"IMC: {consultation.bmi}",
                            variant="soft",
                            color_scheme="green",
                        ),
                        rx.box(),
                    ),
                    spacing="2",
                    wrap="wrap",
                ),
                rx.box(),
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        variant="surface",
    )


def consultations_timeline() -> rx.Component:
    """Timeline con historial de consultas"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Historial de Consultas", size="5"),
                rx.spacer(),
                rx.badge(
                    f"{PatientDetailState.consultations.length()} consultas",
                    color_scheme="blue",
                ),
                width="100%",
                align="center",
            ),
            rx.divider(),
            rx.cond(
                PatientDetailState.consultations.length() > 0,
                rx.vstack(
                    rx.foreach(PatientDetailState.consultations, consultation_item),
                    spacing="3",
                    width="100%",
                ),
                rx.text(
                    "No hay consultas registradas",
                    size="3",
                    color=COLORS["text_secondary"],
                ),
            ),
            spacing="3",
            width="100%",
        ),
    )


def study_item(study) -> rx.Component:
    """Item de estudio médico"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("file-text", size=16, color=COLORS["primary"]),
                rx.vstack(
                    rx.text(study.study_name, size="3", weight="bold"),
                    rx.text(
                        study.study_date,
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.badge(study.study_type, color_scheme="purple", variant="soft"),
                # Botón de descarga visible si hay archivo
                rx.cond(
                    study.file_name.is_not_none(),
                    rx.button(
                        rx.icon("download", size=16),
                        "Descargar archivo",
                        size="2",
                        variant="soft",
                        color_scheme="green",
                        on_click=PatientDetailState.download_study_file(study.id),
                    ),
                    rx.box(),
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                study.results,
                rx.text(
                    study.results,
                    size="2",
                    color=COLORS["text_secondary"],
                ),
                rx.box(),
            ),
            # Mostrar información del archivo si existe
            rx.cond(
                study.file_name.is_not_none(),
                rx.hstack(
                    rx.icon("paperclip", size=14, color=COLORS["primary"]),
                    rx.text(
                        study.file_name,
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    rx.text(
                        "•",
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    rx.text(
                        rx.cond(
                            study.file_size,
                            (study.file_size / 1024).to_string() + " KB",
                            "Tamaño desconocido",
                        ),
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="2",
                ),
                rx.box(),
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        variant="surface",
    )


def study_item_with_attachments(study) -> rx.Component:
    """Item de estudio que incluye archivos adjuntos si existen (versión reactiva)."""

    # Crear attachments Var como lista reactiva si el estudio tiene file_path
    # Usar una lista de listas en vez de dicts para evitar problemas con TypedDict en el compilador
    attachments_var = rx.cond(
        (study.file_path.is_not_none()) | (study.file_name.is_not_none()),
        [[study.file_name, study.file_path, study.file_type, study.file_size]],
        [],
    )

    # Handler que llama al State para descargar
    def on_download(path):
        # path puede ser Var; el State descarga usando el id del estudio
        return PatientDetailState.download_study_file(study.id)

    return rx.vstack(
        study_item(study),
        rx.cond(
            attachments_var.length() > 0,
            rx.card(
                rx.vstack(
                    rx.text("Archivos adjuntos", size="2", weight="bold"),
                    attachments_list_component(attachments_var, on_download=on_download),
                    spacing="2",
                    width="100%",
                ),
                style={"background": "#fbfbff"},
            ),
            rx.box(),
        ),
        spacing="2",
        width="100%",
    )


def medical_studies_section() -> rx.Component:
    """Sección de estudios médicos"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Estudios Médicos", size="5"),
                rx.spacer(),
                rx.badge(
                    f"{PatientDetailState.studies.length()} estudios",
                    color_scheme="purple",
                ),
                width="100%",
                align="center",
            ),
            rx.divider(),
                rx.cond(
                PatientDetailState.studies.length() > 0,
                rx.vstack(
                    rx.foreach(PatientDetailState.studies, study_item_with_attachments),
                    spacing="3",
                    width="100%",
                ),
                rx.text(
                    "No hay estudios médicos registrados",
                    size="3",
                    color=COLORS["text_secondary"],
                ),
            ),
            spacing="3",
            width="100%",
        ),
    )


def patient_detail_page() -> rx.Component:
    """Página de detalle del paciente"""
    return rx.box(
        rx.container(
            rx.vstack(
                # Botones de acción
                rx.hstack(
                    rx.button(
                        rx.icon("arrow-left", size=18),
                        "Volver",
                        on_click=rx.call_script("window.history.back()"),
                        variant="soft",
                        size="2",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("file_text", size=18),
                        "Exportar PDF",
                        on_click=lambda: PatientDetailState.export_patient_pdf(),
                        variant="outline",
                        size="2",
                        color_scheme="red",
                    ),
                    rx.button(
                        rx.icon("file_spreadsheet", size=18),
                        "Exportar Excel",
                        on_click=lambda: PatientDetailState.export_patient_excel(),
                        variant="outline",
                        size="2",
                        color_scheme="green",
                    ),
                    width="100%",
                    align="center",
                ),
                # Header del paciente
                patient_header(),
                # Grid con información médica y estadísticas
                rx.grid(
                    medical_info_card(),
                    rx.card(
                        rx.vstack(
                            rx.heading("Estadísticas", size="5"),
                            rx.divider(),
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Total Consultas:", size="3"),
                                    rx.spacer(),
                                    rx.text(
                                        PatientDetailState.total_consultations,
                                        size="4",
                                        weight="bold",
                                        color=COLORS["primary"],
                                    ),
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.text("Total Estudios:", size="3"),
                                    rx.spacer(),
                                    rx.text(
                                        PatientDetailState.total_studies,
                                        size="4",
                                        weight="bold",
                                        color=COLORS["primary"],
                                    ),
                                    width="100%",
                                ),
                                rx.cond(
                                    PatientDetailState.last_consultation_date,
                                    rx.hstack(
                                        rx.text("Última Consulta:", size="3"),
                                        rx.spacer(),
                                        rx.text(
                                            PatientDetailState.last_consultation_date,
                                            size="3",
                                            weight="bold",
                                        ),
                                        width="100%",
                                    ),
                                    rx.box(),
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                # Timeline y estudios
                rx.grid(
                    consultations_timeline(),
                    medical_studies_section(),
                    columns="1",
                    spacing="4",
                    width="100%",
                ),
                # Sección de archivos unificada
                patient_files_section(),
                spacing="4",
                width="100%",
                padding_y="2rem",
            ),
            size="4",
        ),
        background=COLORS["background"],
        min_height="100vh",
        on_mount=PatientDetailState.load_patient_detail,
    )
