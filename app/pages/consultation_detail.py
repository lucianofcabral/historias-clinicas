"""Página de vista detallada de consulta médica"""

import reflex as rx

from app.components.navbar import navbar
from app.config import COLORS
from app.state.consultation_detail_state import ConsultationDetailState


def consultation_header() -> rx.Component:
    """Header con información principal de la consulta"""
    return rx.box(
        rx.vstack(
            # Botón volver
            rx.link(
                rx.button(
                    rx.icon("arrow_left", size=18),
                    "Volver a Consultas",
                    variant="soft",
                    size="2",
                ),
                href="/consultations",
            ),
            # Título
            rx.heading(
                "Detalles de la Consulta",
                size="8",
                margin_top="1rem",
                margin_bottom="0.5rem",
            ),
            # Información del paciente y fecha
            rx.hstack(
                rx.badge(
                    rx.icon("user", size=16),
                    f"{ConsultationDetailState.patient_name}",
                    color_scheme="blue",
                    size="2",
                ),
                rx.badge(
                    rx.icon("credit_card", size=16),
                    f"DNI: {ConsultationDetailState.patient_dni}",
                    color_scheme="gray",
                    size="2",
                ),
                rx.badge(
                    rx.icon("calendar", size=16),
                    f"{ConsultationDetailState.patient_age} años",
                    color_scheme="green",
                    size="2",
                ),
                rx.badge(
                    rx.icon("clock", size=16),
                    f"{ConsultationDetailState.consultation_date_str}",
                    color_scheme="purple",
                    size="2",
                ),
                spacing="3",
                wrap="wrap",
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        padding="1.5rem",
        background=rx.color("gray", 2),
        border_radius="0.5rem",
        margin_bottom="1.5rem",
    )


def consultation_info_card() -> rx.Component:
    """Card con información de la consulta"""
    return rx.card(
        rx.vstack(
            rx.heading(
                "Información de la Consulta",
                size="5",
                margin_bottom="1rem",
            ),
            # Motivo
            rx.box(
                rx.text(
                    "Motivo de Consulta",
                    font_weight="600",
                    size="2",
                    margin_bottom="0.25rem",
                ),
                rx.text(
                    ConsultationDetailState.consultation["reason"],
                    size="3",
                ),
                width="100%",
                padding_bottom="1rem",
            ),
            # Síntomas
            rx.cond(
                ConsultationDetailState.consultation["symptoms"] != "",
                rx.box(
                    rx.text(
                        "Síntomas",
                        font_weight="600",
                        size="2",
                        margin_bottom="0.25rem",
                    ),
                    rx.text(
                        ConsultationDetailState.consultation["symptoms"],
                        white_space="pre-wrap",
                    ),
                    width="100%",
                    padding_bottom="1rem",
                ),
            ),
            # Diagnóstico
            rx.cond(
                ConsultationDetailState.consultation["diagnosis"] != "",
                rx.box(
                    rx.text(
                        "Diagnóstico",
                        font_weight="600",
                        size="2",
                        margin_bottom="0.25rem",
                    ),
                    rx.text(
                        ConsultationDetailState.consultation["diagnosis"],
                        white_space="pre-wrap",
                    ),
                    width="100%",
                    padding_bottom="1rem",
                ),
            ),
            # Tratamiento
            rx.cond(
                ConsultationDetailState.consultation["treatment"] != "",
                rx.box(
                    rx.text(
                        "Tratamiento",
                        font_weight="600",
                        size="2",
                        margin_bottom="0.25rem",
                    ),
                    rx.text(
                        ConsultationDetailState.consultation["treatment"],
                        white_space="pre-wrap",
                    ),
                    width="100%",
                    padding_bottom="1rem",
                ),
            ),
            # Notas
            rx.cond(
                ConsultationDetailState.consultation["notes"] != "",
                rx.box(
                    rx.text(
                        "Notas Adicionales",
                        font_weight="600",
                        size="2",
                        margin_bottom="0.25rem",
                    ),
                    rx.text(
                        ConsultationDetailState.consultation["notes"],
                        white_space="pre-wrap",
                    ),
                    width="100%",
                ),
            ),
            spacing="2",
            align_items="start",
            width="100%",
        ),
    )


def vital_signs_card() -> rx.Component:
    """Card con signos vitales"""
    return rx.cond(
        ConsultationDetailState.has_vital_signs,
        rx.card(
            rx.vstack(
                rx.heading(
                    rx.hstack(
                        rx.icon("heart_pulse", size=24),
                        "Signos Vitales",
                        spacing="2",
                    ),
                    size="5",
                    margin_bottom="1rem",
                ),
                # Grid de signos vitales
                rx.grid(
                    # Presión arterial
                    rx.cond(
                        ConsultationDetailState.consultation["blood_pressure"] != "",
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("activity", size=20),
                                    rx.text(
                                        "Presión Arterial",
                                        font_weight="600",
                                        size="2",
                                    ),
                                    spacing="2",
                                ),
                                rx.text(
                                    f"{ConsultationDetailState.consultation['blood_pressure']} mmHg",
                                    size="6",
                                    font_weight="700",
                                ),
                                spacing="1",
                                align_items="start",
                            ),
                            padding="1rem",
                            background=rx.color("gray", 2),
                            border_radius="0.5rem",
                        ),
                    ),
                    # Frecuencia cardíaca
                    rx.cond(
                        ConsultationDetailState.consultation["heart_rate"] != "",
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("heart", size=20),
                                    rx.text(
                                        "Frecuencia Cardíaca",
                                        font_weight="600",
                                        size="2",
                                    ),
                                    spacing="2",
                                ),
                                rx.text(
                                    f"{ConsultationDetailState.consultation['heart_rate']} bpm",
                                    size="6",
                                    font_weight="700",
                                ),
                                spacing="1",
                                align_items="start",
                            ),
                            padding="1rem",
                            background=rx.color("gray", 2),
                            border_radius="0.5rem",
                        ),
                    ),
                    # Temperatura
                    rx.cond(
                        ConsultationDetailState.consultation["temperature"] != "",
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("thermometer", size=20),
                                    rx.text(
                                        "Temperatura",
                                        font_weight="600",
                                        size="2",
                                    ),
                                    spacing="2",
                                ),
                                rx.text(
                                    f"{ConsultationDetailState.consultation['temperature']}°C",
                                    size="6",
                                    font_weight="700",
                                ),
                                spacing="1",
                                align_items="start",
                            ),
                            padding="1rem",
                            background=rx.color("gray", 2),
                            border_radius="0.5rem",
                        ),
                    ),
                    # Peso
                    rx.cond(
                        ConsultationDetailState.consultation["weight"] != "",
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("scale", size=20),
                                    rx.text(
                                        "Peso",
                                        font_weight="600",
                                        size="2",
                                    ),
                                    spacing="2",
                                ),
                                rx.text(
                                    f"{ConsultationDetailState.consultation['weight']} kg",
                                    size="6",
                                    font_weight="700",
                                ),
                                spacing="1",
                                align_items="start",
                            ),
                            padding="1rem",
                            background=rx.color("gray", 2),
                            border_radius="0.5rem",
                        ),
                    ),
                    # Altura
                    rx.cond(
                        ConsultationDetailState.consultation["height"] != "",
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("ruler", size=20),
                                    rx.text(
                                        "Altura",
                                        font_weight="600",
                                        size="2",
                                    ),
                                    spacing="2",
                                ),
                                rx.text(
                                    f"{ConsultationDetailState.consultation['height']} cm",
                                    size="6",
                                    font_weight="700",
                                ),
                                spacing="1",
                                align_items="start",
                            ),
                            padding="1rem",
                            background=rx.color("gray", 2),
                            border_radius="0.5rem",
                        ),
                    ),
                    # IMC
                    rx.cond(
                        ConsultationDetailState.bmi_value != "",
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("gauge", size=20),
                                    rx.text(
                                        "IMC",
                                        font_weight="600",
                                        size="2",
                                    ),
                                    spacing="2",
                                ),
                                rx.text(
                                    ConsultationDetailState.bmi_value,
                                    size="6",
                                    font_weight="700",
                                ),
                                rx.badge(
                                    ConsultationDetailState.bmi_category,
                                    color_scheme="blue",
                                ),
                                spacing="1",
                                align_items="start",
                            ),
                            padding="1rem",
                            background=rx.color("gray", 2),
                            border_radius="0.5rem",
                        ),
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                spacing="3",
                align_items="start",
                width="100%",
            ),
        ),
    )


def next_visit_card() -> rx.Component:
    """Card con próxima visita si existe"""
    return rx.cond(
        ConsultationDetailState.consultation["next_visit"] != "",
        rx.card(
            rx.hstack(
                rx.icon("calendar_clock", size=32, color=COLORS["warning"]),
                rx.vstack(
                    rx.text(
                        "Próxima Visita Programada",
                        font_weight="600",
                        size="2",
                    ),
                    rx.text(
                        ConsultationDetailState.consultation["next_visit"],
                        size="5",
                        font_weight="700",
                        color=COLORS["warning"],
                    ),
                    spacing="1",
                    align_items="start",
                ),
                spacing="4",
                align="center",
                width="100%",
            ),
        ),
    )


def consultation_files_card() -> rx.Component:
    """Card con archivos adjuntos de la consulta"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("paperclip", size=24, color=COLORS["primary"]),
                rx.heading(
                    "Archivos Adjuntos",
                    size="5",
                ),
                rx.spacer(),
                rx.badge(
                    f"{ConsultationDetailState.consultation_files.length()} archivo(s)",
                    color_scheme="blue",
                ),
                width="100%",
                align="center",
            ),
            rx.divider(margin_y="1rem"),
            # Lista de archivos
            rx.cond(
                ConsultationDetailState.consultation_files.length() > 0,
                rx.vstack(
                    rx.foreach(
                        ConsultationDetailState.consultation_files,
                        lambda file: rx.card(
                            rx.hstack(
                                rx.icon(
                                    "paperclip",
                                    size=20,
                                    color=COLORS["primary"],
                                ),
                                rx.vstack(
                                    rx.text(
                                        file["file_name"],
                                        size="3",
                                        weight="bold",
                                    ),
                                    rx.hstack(
                                        rx.text(
                                            file["file_type"],
                                            size="1",
                                            color=COLORS["text_secondary"],
                                        ),
                                        rx.text("•", size="1", color=COLORS["text_secondary"]),
                                        rx.text(
                                            f"{file['file_size_mb']} MB",
                                            size="1",
                                            color=COLORS["text_secondary"],
                                        ),
                                        rx.text("•", size="1", color=COLORS["text_secondary"]),
                                        rx.text(
                                            file["uploaded_at"],
                                            size="1",
                                            color=COLORS["text_secondary"],
                                        ),
                                        spacing="2",
                                    ),
                                    spacing="1",
                                    align="start",
                                ),
                                rx.spacer(),
                                rx.button(
                                    rx.icon("download", size=16),
                                    "Descargar",
                                    size="2",
                                    variant="soft",
                                    on_click=lambda: ConsultationDetailState.download_consultation_file(
                                        file["id"]
                                    ),
                                ),
                                width="100%",
                                align="center",
                            ),
                            size="2",
                            variant="surface",
                        ),
                    ),
                    spacing="2",
                    width="100%",
                ),
                # Mensaje cuando no hay archivos
                rx.box(
                    rx.text(
                        "No hay archivos adjuntos en esta consulta",
                        size="3",
                        color=COLORS["text_secondary"],
                        text_align="center",
                    ),
                    padding="2rem",
                    width="100%",
                ),
            ),
            spacing="3",
            width="100%",
        ),
    )


def consultation_detail_page() -> rx.Component:
    """Página de vista detallada de consulta"""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                consultation_header(),
                # Grid de contenido
                rx.grid(
                    # Columna izquierda: Info de consulta
                    rx.vstack(
                        consultation_info_card(),
                        spacing="4",
                        width="100%",
                    ),
                    # Columna derecha: Signos vitales y próxima visita
                    rx.vstack(
                        vital_signs_card(),
                        next_visit_card(),
                        spacing="4",
                        width="100%",
                    ),
                    columns="2",
                    spacing="6",
                    width="100%",
                ),
                # Archivos adjuntos (full width)
                consultation_files_card(),
                spacing="4",
                width="100%",
                padding_y="2rem",
            ),
            size="4",
        ),
        min_height="100vh",
        on_mount=ConsultationDetailState.load_consultation_detail,
    )
