"""Componente para mostrar archivos unificados del paciente"""

import reflex as rx
from app.config import COLORS
from app.state.patient_files_state import PatientFilesState


def file_icon(file_type: str) -> rx.Component:
    """Icono según el tipo MIME del archivo"""
    return rx.cond(
        file_type.contains("pdf"),
        rx.icon("file-text", size=20, color=COLORS["danger"]),
        rx.cond(
            file_type.contains("image"),
            rx.icon("image", size=20, color=COLORS["success"]),
            rx.cond(
                file_type.contains("word") | file_type.contains("document"),
                rx.icon("file-text", size=20, color=COLORS["info"]),
                rx.icon("file", size=20, color=COLORS["text_secondary"]),
            ),
        ),
    )


def file_item(file: rx.Var) -> rx.Component:
    """Item individual de archivo con botón de descarga"""
    return rx.box(
        rx.hstack(
            # Icono del archivo
            file_icon(file.file_type),
            # Información del archivo
            rx.vstack(
                rx.text(
                    file.file_name,
                    size="3",
                    weight="medium",
                    color=COLORS["text"],
                ),
                rx.hstack(
                    rx.text(
                        file.source_name,
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    rx.text("•", size="2", color=COLORS["text_secondary"]),
                    rx.text(
                        (file.file_size / 1024).to(int).to_string() + " KB",
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    rx.text("•", size="2", color=COLORS["text_secondary"]),
                    rx.text(
                        file.uploaded_at,
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="2",
                ),
                rx.cond(
                    file.description.is_not_none(),
                    rx.text(
                        file.description,
                        size="2",
                        color=COLORS["text_secondary"],
                        font_style="italic",
                    ),
                    rx.box(),
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            # Botón de descarga
            rx.button(
                rx.icon("download", size=16),
                "Descargar",
                size="2",
                variant="soft",
                color_scheme="blue",
                on_click=PatientFilesState.download_file(file.file_id, file.category),
            ),
            width="100%",
            align="center",
            spacing="3",
        ),
        padding="4",
        border_radius="8px",
        border=f"1px solid {COLORS['border']}",
        background=COLORS["surface"],
        width="100%",
        _hover={
            "background": COLORS["surface_hover"],
            "border_color": COLORS["primary"],
        },
    )


def category_tab(category: str, label: str, count: int) -> rx.Component:
    """Tab para filtrar por categoría"""
    is_active = PatientFilesState.selected_category == category

    return rx.button(
        rx.hstack(
            rx.text(label, size="2", weight="medium"),
            rx.badge(
                count.to_string(),
                variant="soft",
                color_scheme=rx.cond(is_active, "blue", "gray"),
            ),
            spacing="2",
        ),
        variant=rx.cond(is_active, "solid", "soft"),
        color_scheme=rx.cond(is_active, "blue", "gray"),
        size="2",
        on_click=PatientFilesState.set_category_filter(category),
    )


def patient_files_section() -> rx.Component:
    """Sección completa de archivos del paciente"""
    return rx.box(
        rx.vstack(
            # Header con título y estadísticas
            rx.hstack(
                rx.heading(
                    "📎 Archivos Adjuntos",
                    size="6",
                    color=COLORS["text"],
                ),
                rx.spacer(),
                rx.hstack(
                    rx.badge(
                        rx.hstack(
                            rx.icon("files", size=14),
                            PatientFilesState.total_files.to_string() + " archivos",
                            spacing="1",
                        ),
                        variant="soft",
                        color_scheme="blue",
                    ),
                    rx.badge(
                        rx.hstack(
                            rx.icon("hard-drive", size=14),
                            PatientFilesState.total_size_mb.to_string() + " MB",
                            spacing="1",
                        ),
                        variant="soft",
                        color_scheme="green",
                    ),
                    rx.button(
                        rx.icon("upload", size=16),
                        "Subir Archivos",
                        size="2",
                        on_click=PatientFilesState.open_upload_modal,
                    ),
                    spacing="2",
                ),
                width="100%",
                align="center",
            ),
            # Tabs de categorías
            rx.hstack(
                category_tab("all", "Todos", PatientFilesState.total_files),
                category_tab(
                    "patient", "Documentos del Paciente", PatientFilesState.patient_files.length()
                ),
                category_tab("study", "Estudios Médicos", PatientFilesState.study_files.length()),
                category_tab(
                    "consultation", "Consultas", PatientFilesState.consultation_files.length()
                ),
                spacing="2",
                wrap="wrap",
            ),
            # Lista de archivos
            rx.cond(
                PatientFilesState.total_files > 0,
                rx.vstack(
                    rx.foreach(
                        PatientFilesState.filtered_files,
                        file_item,
                    ),
                    spacing="3",
                    width="100%",
                ),
                # Estado vacío
                rx.center(
                    rx.vstack(
                        rx.icon("folder-open", size=48, color=COLORS["text_secondary"]),
                        rx.text(
                            "No hay archivos adjuntos",
                            size="4",
                            color=COLORS["text_secondary"],
                            weight="medium",
                        ),
                        rx.text(
                            "Los archivos subidos aparecerán aquí organizados por categoría",
                            size="2",
                            color=COLORS["text_secondary"],
                        ),
                        spacing="3",
                        align="center",
                    ),
                    padding="8",
                ),
            ),
            spacing="4",
            width="100%",
        ),
        padding="6",
        border_radius="12px",
        border=f"1px solid {COLORS['border']}",
        background=COLORS["surface"],
        width="100%",
    )


def upload_modal() -> rx.Component:
    """Modal para subir archivos múltiples"""
    from app.models.patient_file import FileCategory

    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Subir Archivos del Paciente"),
            rx.dialog.description(
                "Sube uno o varios archivos relacionados con el paciente",
                margin_bottom="1rem",
            ),
            rx.vstack(
                # Selector de categoría
                rx.text("Categoría *", size="2", weight="bold"),
                rx.select(
                    [category.value for category in FileCategory],
                    value=PatientFilesState.upload_category,
                    on_change=PatientFilesState.set_upload_category,
                ),
                # Descripción
                rx.text("Descripción (opcional)", size="2", weight="bold"),
                rx.text_area(
                    placeholder="Descripción del archivo...",
                    value=PatientFilesState.upload_description,
                    on_change=PatientFilesState.set_upload_description,
                    rows="3",
                ),
                # Upload de archivos
                rx.text("Archivos *", size="2", weight="bold"),
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
                    id="upload_patient_file",
                    multiple=True,
                    accept={
                        "application/pdf": [".pdf"],
                        "image/*": [".png", ".jpg", ".jpeg"],
                        "application/msword": [".doc", ".docx"],
                    },
                    max_files=10,
                    max_size=50 * 1024 * 1024,
                    on_drop=PatientFilesState.handle_upload(
                        rx.upload_files(upload_id="upload_patient_file")
                    ),
                ),
                # Lista de archivos subidos
                rx.cond(
                    PatientFilesState.uploaded_files.length() > 0,
                    rx.vstack(
                        rx.text("Archivos listos para subir:", size="2", weight="bold"),
                        rx.foreach(
                            PatientFilesState.uploaded_files,
                            lambda file_info, idx: rx.card(
                                rx.hstack(
                                    rx.icon("paperclip", size=18, color=COLORS["primary"]),
                                    rx.vstack(
                                        rx.text(
                                            file_info["name"],
                                            size="2",
                                            weight="bold",
                                        ),
                                        rx.text(
                                            file_info["type"],
                                            size="1",
                                            color=COLORS["text_secondary"],
                                        ),
                                        spacing="1",
                                        align="start",
                                    ),
                                    rx.spacer(),
                                    rx.button(
                                        rx.icon("x", size=16),
                                        on_click=PatientFilesState.remove_uploaded_file(idx),
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
                # Mensajes
                rx.cond(
                    PatientFilesState.upload_message != "",
                    rx.callout(
                        PatientFilesState.upload_message,
                        color_scheme=rx.cond(
                            PatientFilesState.upload_message_type == "success",
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
            # Botones
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.button(
                    rx.icon("upload", size=16),
                    "Subir Archivos",
                    on_click=PatientFilesState.save_uploaded_files,
                    disabled=PatientFilesState.uploaded_files.length() == 0,
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
        open=PatientFilesState.show_upload_modal,
        on_open_change=PatientFilesState.close_upload_modal,
    )
