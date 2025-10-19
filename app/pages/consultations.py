"""Página de gestión de consultas médicas"""

import reflex as rx

from app.components.navbar import navbar
from app.components.patient_selector import patient_selector_with_label
from app.config import COLORS
from app.state.consultation_state import ConsultationState


def consultation_card(consultation: dict) -> rx.Component:
    """Tarjeta de consulta médica"""
    return rx.card(
        rx.vstack(
            # Header con fecha y paciente
            rx.hstack(
                rx.icon("calendar_check", size=24, color=COLORS["primary"]),
                rx.vstack(
                    rx.text(
                        consultation["consultation_date"],
                        font_weight="600",
                        color=COLORS["text"],
                    ),
                    rx.text(
                        f"Paciente ID: {consultation['patient_id']}",
                        font_size="0.875rem",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="1",
                    align_items="start",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.button(
                        rx.icon("eye", size=16),
                        size="2",
                        variant="soft",
                        on_click=lambda: ConsultationState.view_consultation(consultation["id"]),
                    ),
                    rx.button(
                        rx.icon("pencil", size=16),
                        size="2",
                        variant="soft",
                        color_scheme="blue",
                        on_click=lambda: ConsultationState.open_edit_consultation_modal(
                            consultation["id"]
                        ),
                    ),
                    rx.button(
                        rx.icon("trash_2", size=16),
                        size="2",
                        variant="soft",
                        color_scheme="red",
                        on_click=lambda: ConsultationState.delete_consultation(consultation["id"]),
                    ),
                    spacing="2",
                ),
                width="100%",
                align="center",
            ),
            # Motivo de consulta
            rx.box(
                rx.text(
                    "Motivo:",
                    font_weight="600",
                    color=COLORS["text_secondary"],
                    font_size="0.875rem",
                ),
                rx.text(
                    consultation["reason"],
                    color=COLORS["text"],
                ),
                padding_y="0.5rem",
            ),
            # Diagnóstico si existe
            rx.cond(
                consultation["diagnosis"] != "",
                rx.box(
                    rx.text(
                        "Diagnóstico:",
                        font_weight="600",
                        color=COLORS["text_secondary"],
                        font_size="0.875rem",
                    ),
                    rx.text(
                        consultation["diagnosis"],
                        color=COLORS["text"],
                    ),
                    padding_y="0.5rem",
                ),
            ),
            # Signos vitales badge
            rx.cond(
                consultation["has_vital_signs"],
                rx.hstack(
                    rx.badge(
                        rx.icon("heart_pulse", size=14),
                        "Signos Vitales",
                        color_scheme="green",
                    ),
                    rx.cond(
                        consultation["bmi"] != "",
                        rx.badge(
                            f"IMC: {consultation['bmi']} - {consultation['bmi_category']}",
                            color_scheme="blue",
                        ),
                    ),
                    spacing="2",
                ),
            ),
            # Próxima visita si existe
            rx.cond(
                consultation["next_visit"] != "",
                rx.box(
                    rx.text(
                        f"Próxima visita: {consultation['next_visit']}",
                        font_size="0.875rem",
                        color=COLORS["warning"],
                        font_weight="500",
                    ),
                    padding_top="0.5rem",
                ),
            ),
            spacing="3",
            align_items="start",
        ),
        width="100%",
    )


def new_consultation_modal() -> rx.Component:
    """Modal para crear/editar consulta"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("file_text", size=24),
                    rx.cond(
                        ConsultationState.editing_consultation_id,
                        "Editar Consulta Médica",
                        "Nueva Consulta Médica",
                    ),
                    spacing="2",
                ),
            ),
            rx.dialog.description(
                "Complete los datos de la consulta médica",
                size="2",
                margin_bottom="1rem",
            ),
            # Mensajes de error/éxito
            rx.cond(
                ConsultationState.error_message != "",
                rx.callout(
                    ConsultationState.error_message,
                    icon="triangle_alert",
                    color_scheme="red",
                    role="alert",
                    margin_bottom="1rem",
                ),
            ),
            rx.scroll_area(
                rx.vstack(
                    # Sección: Datos Básicos
                    rx.heading("Datos Básicos", size="5", margin_bottom="0.5rem"),
                    # Paciente
                    patient_selector_with_label(
                        label="Paciente",
                        patients_options=ConsultationState.patients_options,
                        value=ConsultationState.form_patient_id,
                        on_change=ConsultationState.set_form_patient_id,
                        placeholder="Seleccione un paciente...",
                        required=True,
                        help_text="Seleccione el paciente para esta consulta",
                    ),
                    # Motivo
                    rx.vstack(
                        rx.text(
                            "Motivo de Consulta *",
                            font_weight="500",
                            color=COLORS["text_secondary"],
                        ),
                        rx.input(
                            placeholder="Ej: Control de rutina, dolor de cabeza...",
                            value=ConsultationState.form_reason,
                            on_change=ConsultationState.set_form_reason,
                            width="100%",
                        ),
                        spacing="1",
                        align_items="start",
                        width="100%",
                    ),
                    # Síntomas
                    rx.vstack(
                        rx.text(
                            "Síntomas",
                            font_weight="500",
                            color=COLORS["text_secondary"],
                        ),
                        rx.text_area(
                            placeholder="Describa los síntomas del paciente...",
                            value=ConsultationState.form_symptoms,
                            on_change=ConsultationState.set_form_symptoms,
                            rows="3",
                            width="100%",
                        ),
                        spacing="1",
                        align_items="start",
                        width="100%",
                    ),
                    rx.divider(margin_y="1rem"),
                    # Sección: Signos Vitales
                    rx.heading("Signos Vitales", size="5", margin_bottom="0.5rem"),
                    rx.grid(
                        # Presión arterial
                        rx.vstack(
                            rx.text(
                                "Presión Arterial",
                                font_weight="500",
                                color=COLORS["text_secondary"],
                                font_size="0.875rem",
                            ),
                            rx.input(
                                placeholder="120/80",
                                value=ConsultationState.form_blood_pressure,
                                on_change=ConsultationState.set_form_blood_pressure,
                                width="100%",
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%",
                        ),
                        # Frecuencia cardíaca
                        rx.vstack(
                            rx.text(
                                "Frecuencia Cardíaca (ppm)",
                                font_weight="500",
                                color=COLORS["text_secondary"],
                                font_size="0.875rem",
                            ),
                            rx.input(
                                placeholder="72",
                                type="number",
                                value=ConsultationState.form_heart_rate,
                                on_change=ConsultationState.set_form_heart_rate,
                                width="100%",
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%",
                        ),
                        # Temperatura
                        rx.vstack(
                            rx.text(
                                "Temperatura (°C)",
                                font_weight="500",
                                color=COLORS["text_secondary"],
                                font_size="0.875rem",
                            ),
                            rx.input(
                                placeholder="36.5",
                                type="number",
                                step="0.1",
                                value=ConsultationState.form_temperature,
                                on_change=ConsultationState.set_form_temperature,
                                width="100%",
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%",
                        ),
                        # Peso
                        rx.vstack(
                            rx.text(
                                "Peso (kg)",
                                font_weight="500",
                                color=COLORS["text_secondary"],
                                font_size="0.875rem",
                            ),
                            rx.input(
                                placeholder="70.5",
                                type="number",
                                step="0.1",
                                value=ConsultationState.form_weight,
                                on_change=ConsultationState.set_form_weight,
                                width="100%",
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%",
                        ),
                        # Altura
                        rx.vstack(
                            rx.text(
                                "Altura (cm)",
                                font_weight="500",
                                color=COLORS["text_secondary"],
                                font_size="0.875rem",
                            ),
                            rx.input(
                                placeholder="175",
                                type="number",
                                step="0.1",
                                value=ConsultationState.form_height,
                                on_change=ConsultationState.set_form_height,
                                width="100%",
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%",
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    rx.divider(margin_y="1rem"),
                    # Sección: Diagnóstico y Tratamiento
                    rx.heading("Diagnóstico y Tratamiento", size="5", margin_bottom="0.5rem"),
                    # Diagnóstico
                    rx.vstack(
                        rx.text(
                            "Diagnóstico",
                            font_weight="500",
                            color=COLORS["text_secondary"],
                        ),
                        rx.text_area(
                            placeholder="Diagnóstico médico...",
                            value=ConsultationState.form_diagnosis,
                            on_change=ConsultationState.set_form_diagnosis,
                            rows="3",
                            width="100%",
                        ),
                        spacing="1",
                        align_items="start",
                        width="100%",
                    ),
                    # Tratamiento
                    rx.vstack(
                        rx.text(
                            "Tratamiento",
                            font_weight="500",
                            color=COLORS["text_secondary"],
                        ),
                        rx.text_area(
                            placeholder="Tratamiento indicado, medicación, dosis...",
                            value=ConsultationState.form_treatment,
                            on_change=ConsultationState.set_form_treatment,
                            rows="3",
                            width="100%",
                        ),
                        spacing="1",
                        align_items="start",
                        width="100%",
                    ),
                    # Notas
                    rx.vstack(
                        rx.text(
                            "Notas Adicionales",
                            font_weight="500",
                            color=COLORS["text_secondary"],
                        ),
                        rx.text_area(
                            placeholder="Observaciones, recomendaciones...",
                            value=ConsultationState.form_notes,
                            on_change=ConsultationState.set_form_notes,
                            rows="2",
                            width="100%",
                        ),
                        spacing="1",
                        align_items="start",
                        width="100%",
                    ),
                    # Próxima visita
                    rx.vstack(
                        rx.text(
                            "Próxima Visita",
                            font_weight="500",
                            color=COLORS["text_secondary"],
                        ),
                        rx.input(
                            type="date",
                            value=ConsultationState.form_next_visit,
                            on_change=ConsultationState.set_form_next_visit,
                            width="100%",
                        ),
                        spacing="1",
                        align_items="start",
                        width="100%",
                    ),
                    rx.divider(margin_y="1rem"),
                    # Archivos Adjuntos
                    rx.heading("Archivos Adjuntos", size="5", margin_bottom="0.5rem"),
                    rx.upload(
                        rx.vstack(
                            rx.button(
                                rx.icon("upload", size=20),
                                "Seleccionar Archivos",
                                variant="soft",
                                color_scheme="blue",
                            ),
                            rx.text(
                                "PDF, imágenes, documentos (máx 50MB por archivo)",
                                size="1",
                                color=COLORS["text_secondary"],
                            ),
                            spacing="2",
                        ),
                        id="upload_consultation_files",
                        multiple=True,
                        accept={
                            "application/pdf": [".pdf"],
                            "image/*": [".png", ".jpg", ".jpeg"],
                            "application/msword": [".doc", ".docx"],
                        },
                        max_files=10,
                        max_size=50 * 1024 * 1024,
                        on_drop=ConsultationState.handle_upload(
                            rx.upload_files(upload_id="upload_consultation_files")
                        ),
                    ),
                    # Vista previa de archivos
                    rx.cond(
                        ConsultationState.uploaded_files.length() > 0,
                        rx.vstack(
                            rx.text("Archivos listos para subir:", size="2", weight="bold"),
                            rx.foreach(
                                ConsultationState.uploaded_files,
                                lambda file_info, idx: rx.card(
                                    rx.hstack(
                                        rx.icon("paperclip", size=18, color=COLORS["primary"]),
                                        rx.vstack(
                                            rx.text(file_info["name"], size="2", weight="bold"),
                                            rx.text(file_info["type"], size="1", color=COLORS["text_secondary"]),
                                            spacing="1",
                                            align="start",
                                        ),
                                        rx.spacer(),
                                        rx.button(
                                            rx.icon("x", size=16),
                                            on_click=ConsultationState.remove_uploaded_file(idx),
                                            variant="ghost",
                                            color_scheme="red",
                                            size="1",
                                        ),
                                        width="100%",
                                        align="center",
                                    ),
                                    size="1",
                                    variant="surface",
                                ),
                            ),
                            spacing="2",
                            width="100%",
                        ),
                    ),
                    spacing="4",
                    width="100%",
                ),
                height="60vh",
                scrollbars="vertical",
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
                        ConsultationState.editing_consultation_id,
                        "Guardar Cambios",
                        "Crear Consulta",
                    ),
                    on_click=ConsultationState.save_consultation,
                ),
                spacing="3",
                margin_top="1rem",
                justify="end",
            ),
            max_width="800px",
            padding="1.5rem",
        ),
        open=ConsultationState.show_new_consultation_modal,
        on_open_change=ConsultationState.set_show_new_consultation_modal,
    )


def consultations_page() -> rx.Component:
    """Página principal de consultas médicas"""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.heading(
                        "Consultas Médicas",
                        size="8",
                        color=COLORS["text"],
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("plus", size=20),
                        "Nueva Consulta",
                        on_click=ConsultationState.open_new_consultation_modal,
                        size="3",
                    ),
                    width="100%",
                    align="center",
                    margin_bottom="2rem",
                ),
                # Estadísticas
                rx.grid(
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("file_text", size=24, color=COLORS["primary"]),
                                rx.text(
                                    "Total Consultas",
                                    font_weight="600",
                                    color=COLORS["text_secondary"],
                                ),
                                spacing="2",
                            ),
                            rx.heading(
                                ConsultationState.consultations.length().to_string(),
                                size="7",
                                color=COLORS["text"],
                            ),
                            spacing="2",
                            align_items="start",
                        ),
                    ),
                    columns="1",
                    spacing="4",
                    width="100%",
                    margin_bottom="2rem",
                ),
                # Filtros
                rx.hstack(
                    rx.input(
                        placeholder="🔍 Buscar en motivo, síntomas, diagnóstico, tratamiento...",
                        value=ConsultationState.search_query,
                        on_change=ConsultationState.handle_search_change,
                        width="400px",
                    ),
                    rx.button(
                        "Limpiar",
                        on_click=lambda: ConsultationState.handle_search_change(""),
                        variant="outline",
                        color_scheme="gray",
                    ),
                    spacing="3",
                    margin_bottom="1.5rem",
                ),
                # Lista de consultas
                rx.cond(
                    ConsultationState.consultations.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            ConsultationState.consultations,
                            consultation_card,
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.icon("file_text", size=48, color=COLORS["text_secondary"]),
                            rx.heading(
                                "No hay consultas registradas",
                                size="6",
                                color=COLORS["text"],
                            ),
                            rx.text(
                                "Comienza agregando una nueva consulta médica",
                                color=COLORS["text_secondary"],
                            ),
                            rx.button(
                                rx.icon("plus", size=20),
                                "Nueva Consulta",
                                on_click=ConsultationState.open_new_consultation_modal,
                                size="3",
                            ),
                            spacing="4",
                            align_items="center",
                        ),
                        padding="4rem",
                        text_align="center",
                    ),
                ),
                spacing="4",
                padding_y="2rem",
                width="100%",
            ),
            max_width="1000px",
        ),
        new_consultation_modal(),
        background=COLORS["background"],
        min_height="100vh",
        on_mount=ConsultationState.load_consultations,
    )
