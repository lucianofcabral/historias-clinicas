"""Página de gestión de estudios médicos"""

import reflex as rx

from app.components.navbar import navbar
from app.config import COLORS
from app.models import StudyType
from app.state.medical_study_state import MedicalStudyState


def study_type_badge(study_type: str) -> rx.Component:
    """Badge para el tipo de estudio"""
    color_map = {
        StudyType.LABORATORY.value: "blue",
        StudyType.RADIOLOGY.value: "purple",
        StudyType.ULTRASOUND.value: "green",
        StudyType.TOMOGRAPHY.value: "orange",
        StudyType.RESONANCE.value: "red",
        StudyType.ELECTROCARDIOGRAM.value: "pink",
        StudyType.ENDOSCOPY.value: "cyan",
        StudyType.BIOPSY.value: "yellow",
        StudyType.OTHER.value: "gray",
    }

    return rx.badge(
        study_type,
        color_scheme=color_map.get(study_type, "gray"),
    )


def study_card(study) -> rx.Component:
    """Tarjeta de estudio médico"""
    return rx.card(
        rx.vstack(
            # Header con tipo y fecha
            rx.hstack(
                study_type_badge(study.study_type),
                rx.spacer(),
                rx.text(
                    study.study_date.to_string(),
                    size="2",
                    color=COLORS["text_secondary"],
                ),
                width="100%",
            ),
            # Nombre del estudio
            rx.heading(study.study_name, size="4", margin_top="0.5rem"),
            # Información adicional
            rx.vstack(
                rx.cond(
                    study.institution,
                    rx.hstack(
                        rx.icon("building-2", size=16),
                        rx.text(study.institution, size="2"),
                    ),
                    rx.box(),
                ),
                rx.cond(
                    study.requesting_doctor,
                    rx.hstack(
                        rx.icon("user-round", size=16),
                        rx.text(
                            f"Dr/a. {study.requesting_doctor}",
                            size="2",
                        ),
                    ),
                    rx.box(),
                ),
                rx.cond(
                    study.file_path,
                    rx.hstack(
                        rx.icon("paperclip", size=16),
                        rx.text(study.file_name, size="2", color=COLORS["primary"]),
                    ),
                    rx.box(),
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            # Resultados (preview)
            rx.cond(
                study.results,
                rx.box(
                    rx.text(
                        "Resultados:",
                        size="2",
                        weight="bold",
                        color=COLORS["text_secondary"],
                    ),
                    rx.text(
                        rx.cond(
                            study.results.length() > 150,
                            study.results[:150] + "...",
                            study.results,
                        ),
                        size="2",
                    ),
                    padding_top="0.5rem",
                ),
                rx.box(),
            ),
            # Acciones
            rx.hstack(
                rx.button(
                    rx.icon("eye", size=16),
                    "Ver detalles",
                    variant="soft",
                    size="2",
                    on_click=lambda: MedicalStudyState.view_study(study.id),
                ),
                rx.button(
                    rx.icon("pencil", size=16),
                    variant="soft",
                    color_scheme="blue",
                    size="2",
                    on_click=lambda: MedicalStudyState.open_edit_study_modal(study.id),
                ),
                rx.cond(
                    study.file_path,
                    rx.button(
                        rx.icon("download", size=16),
                        "Descargar",
                        variant="soft",
                        color_scheme="green",
                        size="2",
                        on_click=lambda: MedicalStudyState.download_file(study.id),
                    ),
                    rx.box(),
                ),
                rx.button(
                    rx.icon("trash-2", size=16),
                    variant="soft",
                    color_scheme="red",
                    size="2",
                    on_click=lambda: MedicalStudyState.delete_study(study.id),
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


def new_study_modal() -> rx.Component:
    """Modal para crear nuevo estudio"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    MedicalStudyState.editing_study_id,
                    "Editar Estudio Médico",
                    "Nuevo Estudio Médico",
                )
            ),
            rx.dialog.description(
                "Complete la información del estudio",
                margin_bottom="1rem",
            ),
            rx.vstack(
                # ID del Paciente
                rx.text("ID del Paciente *", size="2", weight="bold"),
                rx.input(
                    placeholder="Ej: 1",
                    value=MedicalStudyState.form_patient_id,
                    on_change=MedicalStudyState.set_form_patient_id,
                    type="number",
                ),
                # Tipo de estudio
                rx.text("Tipo de Estudio *", size="2", weight="bold"),
                rx.select(
                    [study_type.value for study_type in StudyType],
                    value=MedicalStudyState.form_study_type,
                    on_change=MedicalStudyState.set_form_study_type,
                ),
                # Nombre del estudio
                rx.text("Nombre del Estudio *", size="2", weight="bold"),
                rx.input(
                    placeholder="Ej: Hemograma completo",
                    value=MedicalStudyState.form_study_name,
                    on_change=MedicalStudyState.set_form_study_name,
                ),
                # Fecha
                rx.text("Fecha del Estudio *", size="2", weight="bold"),
                rx.input(
                    type="date",
                    value=MedicalStudyState.form_study_date,
                    on_change=MedicalStudyState.set_form_study_date,
                ),
                # Institución
                rx.text("Institución", size="2", weight="bold"),
                rx.input(
                    placeholder="Ej: Laboratorio Central",
                    value=MedicalStudyState.form_institution,
                    on_change=MedicalStudyState.set_form_institution,
                ),
                # Médico solicitante
                rx.text("Médico Solicitante", size="2", weight="bold"),
                rx.input(
                    placeholder="Ej: Dr. García",
                    value=MedicalStudyState.form_requesting_doctor,
                    on_change=MedicalStudyState.set_form_requesting_doctor,
                ),
                # Resultados
                rx.text("Resultados", size="2", weight="bold"),
                rx.text_area(
                    placeholder="Resultados del estudio...",
                    value=MedicalStudyState.form_results,
                    on_change=MedicalStudyState.set_form_results,
                    rows="4",
                ),
                # Observaciones
                rx.text("Observaciones", size="2", weight="bold"),
                rx.text_area(
                    placeholder="Observaciones adicionales...",
                    value=MedicalStudyState.form_observations,
                    on_change=MedicalStudyState.set_form_observations,
                    rows="3",
                ),
                # Diagnóstico
                rx.text("Diagnóstico", size="2", weight="bold"),
                rx.text_area(
                    placeholder="Diagnóstico derivado...",
                    value=MedicalStudyState.form_diagnosis,
                    on_change=MedicalStudyState.set_form_diagnosis,
                    rows="3",
                ),
                # Archivo adjunto
                rx.text("Archivo Adjunto", size="2", weight="bold"),
                rx.upload(
                    rx.vstack(
                        rx.button(
                            rx.icon("upload", size=20),
                            "Seleccionar Archivo",
                            variant="soft",
                            color_scheme="blue",
                        ),
                        rx.text(
                            "PDF, imágenes, documentos (máx 50MB)",
                            size="1",
                            color=COLORS["text_secondary"],
                        ),
                        spacing="2",
                    ),
                    id="upload_study_file",
                    multiple=False,
                    accept={
                        "application/pdf": [".pdf"],
                        "image/*": [".png", ".jpg", ".jpeg"],
                        "application/msword": [".doc", ".docx"],
                    },
                    max_files=1,
                    max_size=50 * 1024 * 1024,  # 50MB
                    on_drop=MedicalStudyState.handle_upload(
                        rx.upload_files(upload_id="upload_study_file")
                    ),
                ),
                # Vista previa del archivo subido
                rx.cond(
                    MedicalStudyState.file_name != "",
                    rx.card(
                        rx.hstack(
                            rx.icon("paperclip", size=18, color=COLORS["primary"]),
                            rx.vstack(
                                rx.text(
                                    MedicalStudyState.file_name,
                                    size="2",
                                    weight="bold",
                                ),
                                rx.text(
                                    f"{(MedicalStudyState.file_size / 1024).to_string()} KB",
                                    size="1",
                                    color=COLORS["text_secondary"],
                                ),
                                spacing="1",
                                align="start",
                            ),
                            rx.spacer(),
                            rx.button(
                                rx.icon("x", size=16),
                                on_click=MedicalStudyState.remove_uploaded_file,
                                variant="ghost",
                                color_scheme="red",
                                size="1",
                            ),
                            width="100%",
                            align="center",
                        ),
                        style={
                            "background": COLORS["surface"],
                            "padding": "0.5rem",
                        },
                    ),
                    rx.box(),
                ),
                # Mensaje de error/éxito
                rx.cond(
                    MedicalStudyState.message != "",
                    rx.callout(
                        MedicalStudyState.message,
                        color_scheme=rx.cond(
                            MedicalStudyState.message_type == "success",
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
                        MedicalStudyState.editing_study_id,
                        "Guardar Cambios",
                        "Crear Estudio",
                    ),
                    on_click=MedicalStudyState.save_study,
                ),
                spacing="3",
                margin_top="1rem",
                justify="end",
            ),
            style={
                "max_width": "600px",
                "background": COLORS["background"],
            },
        ),
        open=MedicalStudyState.show_new_study_modal,
        on_open_change=MedicalStudyState.set_show_new_study_modal,
    )


def medical_studies_page() -> rx.Component:
    """Página principal de estudios médicos"""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                # Header
                rx.heading("Estudios Médicos", size="8"),
                rx.text(
                    "Gestión de análisis y estudios complementarios",
                    size="3",
                    color=COLORS["text_secondary"],
                ),
                # Stats y acciones
                rx.hstack(
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("file-text", size=24, color=COLORS["primary"]),
                                rx.text(
                                    "Total de Estudios",
                                    size="2",
                                    color=COLORS["text_secondary"],
                                ),
                            ),
                            rx.heading(
                                MedicalStudyState.studies.length(),
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
                                rx.icon("hard-drive", size=24, color=COLORS["primary"]),
                                rx.text(
                                    "Almacenamiento Usado",
                                    size="2",
                                    color=COLORS["text_secondary"],
                                ),
                            ),
                            rx.heading(
                                f"{MedicalStudyState.storage_size_mb} MB",
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
                        "Nuevo Estudio",
                        size="3",
                        on_click=MedicalStudyState.open_new_study_modal,
                    ),
                    width="100%",
                    spacing="4",
                ),
                # Filtros
                rx.hstack(
                    rx.text("Filtrar por tipo:", size="2", weight="bold"),
                    rx.select(
                        [
                            "Todos",
                            "Laboratorio",
                            "Radiología",
                            "Ecografía",
                            "Tomografía",
                            "Resonancia",
                            "Electrocardiograma",
                            "Endoscopía",
                            "Biopsia",
                            "Otro",
                        ],
                        placeholder="Todos",
                        on_change=MedicalStudyState.load_studies_by_type,
                    ),
                    width="100%",
                    spacing="3",
                ),
                # Lista de estudios
                rx.cond(
                    MedicalStudyState.studies.length() > 0,
                    rx.box(
                        rx.foreach(
                            MedicalStudyState.studies,
                            study_card,
                        ),
                        width="100%",
                    ),
                    rx.callout(
                        "No hay estudios médicos registrados",
                        icon="info",
                        color_scheme="blue",
                    ),
                ),
                spacing="6",
                width="100%",
                padding="2rem",
            ),
            max_width="1200px",
        ),
        new_study_modal(),
        on_mount=MedicalStudyState.load_studies,
        background=COLORS["background"],
        min_height="100vh",
    )
