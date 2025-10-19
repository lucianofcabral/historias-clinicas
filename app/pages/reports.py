"""
Página de reportes y exportaciones
"""

import reflex as rx
from app.components.navbar import navbar
from app.components.patient_selector import patient_selector_with_label
from app.state.report_state import ReportState


def reports_page() -> rx.Component:
    """Página principal de reportes"""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                # Encabezado
                rx.heading(
                    "Reportes y Exportación",
                    size="8",
                    margin_bottom="1rem",
                ),
                rx.text(
                    "Genera reportes en PDF o Excel de historias clínicas, consultas y estudios médicos",
                    color="gray",
                    margin_bottom="2rem",
                ),
                # Mensaje de feedback
                rx.cond(
                    ReportState.message != "",
                    rx.callout(
                        ReportState.message,
                        icon=rx.cond(
                            ReportState.message_type == "info",
                            "info",
                            rx.cond(
                                ReportState.message_type == "warning",
                                "triangle_alert",
                                "circle_x",
                            ),
                        ),
                        color_scheme=rx.cond(
                            ReportState.message_type == "info",
                            "blue",
                            rx.cond(
                                ReportState.message_type == "warning",
                                "orange",
                                "red",
                            ),
                        ),
                        margin_bottom="1.5rem",
                    ),
                ),
                # Tarjetas de tipos de reportes
                rx.grid(
                    # Historial Completo de Paciente
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("user", size=32, color="blue"),
                                rx.vstack(
                                    rx.heading("Historial Completo", size="5"),
                                    rx.text(
                                        "Genera el historial clínico completo de un paciente",
                                        size="2",
                                        color="gray",
                                    ),
                                    align_items="start",
                                    spacing="0",
                                ),
                                align="center",
                                width="100%",
                                margin_bottom="1rem",
                            ),
                            rx.divider(),
                            # Selector de paciente
                            patient_selector_with_label(
                                label="Seleccionar Paciente",
                                patients_options=ReportState.patients_options,
                                value="",
                                on_change=ReportState.set_patient_id_from_string,
                                placeholder="Seleccione un paciente...",
                                required=True,
                                help_text="Seleccione el paciente para generar su historial",
                            ),
                            # Selector de formato
                            rx.vstack(
                                rx.text("Formato:", size="2", weight="bold"),
                                rx.radio(
                                    ["PDF", "Excel"],
                                    default_value="PDF",
                                    on_change=ReportState.set_format_from_radio,
                                ),
                                width="100%",
                                spacing="1",
                            ),
                            # Botón de generación
                            rx.button(
                                rx.icon("download", size=18),
                                "Generar Historial",
                                on_click=[
                                    ReportState.set_selected_report_type("patient_history"),
                                    ReportState.generate_report,
                                ],
                                color_scheme="blue",
                                size="3",
                                width="100%",
                                loading=ReportState.is_loading,
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        size="3",
                    ),
                    # Reporte de Consultas
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("clipboard-list", size=32, color="green"),
                                rx.vstack(
                                    rx.heading("Reporte de Consultas", size="5"),
                                    rx.text(
                                        "Genera reporte de consultas por rango de fechas",
                                        size="2",
                                        color="gray",
                                    ),
                                    align_items="start",
                                    spacing="0",
                                ),
                                align="center",
                                width="100%",
                                margin_bottom="1rem",
                            ),
                            rx.divider(),
                            # Filtros de fecha
                            rx.vstack(
                                rx.grid(
                                    rx.vstack(
                                        rx.text("Fecha Inicio:", size="2", weight="bold"),
                                        rx.input(
                                            type="date",
                                            on_change=ReportState.set_start_date,
                                            width="100%",
                                        ),
                                        spacing="1",
                                        align_items="start",
                                    ),
                                    rx.vstack(
                                        rx.text("Fecha Fin:", size="2", weight="bold"),
                                        rx.input(
                                            type="date",
                                            on_change=ReportState.set_end_date,
                                            width="100%",
                                        ),
                                        spacing="1",
                                        align_items="start",
                                    ),
                                    columns="2",
                                    spacing="3",
                                    width="100%",
                                ),
                                rx.text(
                                    "Deja las fechas vacías para incluir todas las consultas",
                                    size="1",
                                    color="gray",
                                ),
                                width="100%",
                                spacing="2",
                            ),
                            # Formato (solo PDF disponible)
                            rx.vstack(
                                rx.text("Formato:", size="2", weight="bold"),
                                rx.text("PDF", size="2", color="gray"),
                                width="100%",
                                spacing="1",
                            ),
                            # Botón de generación
                            rx.button(
                                rx.icon("download", size=18),
                                "Generar Reporte",
                                on_click=[
                                    ReportState.set_selected_report_type("consultations"),
                                    ReportState.set_selected_format("pdf"),
                                    ReportState.generate_report,
                                ],
                                color_scheme="green",
                                size="3",
                                width="100%",
                                loading=ReportState.is_loading,
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        size="3",
                    ),
                    # Reporte de Estudios Médicos
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("activity", size=32, color="purple"),
                                rx.vstack(
                                    rx.heading("Reporte de Estudios", size="5"),
                                    rx.text(
                                        "Genera reporte de estudios médicos filtrados",
                                        size="2",
                                        color="gray",
                                    ),
                                    align_items="start",
                                    spacing="0",
                                ),
                                align="center",
                                width="100%",
                                margin_bottom="1rem",
                            ),
                            rx.divider(),
                            # Tipo de estudio
                            rx.vstack(
                                rx.text("Tipo de Estudio:", size="2", weight="bold"),
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
                                    placeholder="Selecciona tipo (opcional)...",
                                    on_change=ReportState.set_study_type_from_select,
                                    width="100%",
                                ),
                                width="100%",
                                spacing="1",
                            ),
                            # Filtros de fecha
                            rx.vstack(
                                rx.grid(
                                    rx.vstack(
                                        rx.text("Fecha Inicio:", size="2", weight="bold"),
                                        rx.input(
                                            type="date",
                                            on_change=ReportState.set_start_date,
                                            width="100%",
                                        ),
                                        spacing="1",
                                        align_items="start",
                                    ),
                                    rx.vstack(
                                        rx.text("Fecha Fin:", size="2", weight="bold"),
                                        rx.input(
                                            type="date",
                                            on_change=ReportState.set_end_date,
                                            width="100%",
                                        ),
                                        spacing="1",
                                        align_items="start",
                                    ),
                                    columns="2",
                                    spacing="3",
                                    width="100%",
                                ),
                                width="100%",
                                spacing="2",
                            ),
                            # Formato (solo Excel disponible)
                            rx.vstack(
                                rx.text("Formato:", size="2", weight="bold"),
                                rx.text("Excel", size="2", color="gray"),
                                width="100%",
                                spacing="1",
                            ),
                            # Botón de generación
                            rx.button(
                                rx.icon("download", size=18),
                                "Generar Reporte",
                                on_click=[
                                    ReportState.set_selected_report_type("studies"),
                                    ReportState.set_selected_format("excel"),
                                    ReportState.generate_report,
                                ],
                                color_scheme="purple",
                                size="3",
                                width="100%",
                                loading=ReportState.is_loading,
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        size="3",
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                # Información adicional
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("info", size=20, color="blue"),
                            rx.heading("Información sobre Reportes", size="4"),
                            align="center",
                            spacing="2",
                        ),
                        rx.divider(),
                        rx.unordered_list(
                            rx.list_item(
                                rx.text(
                                    rx.text("Historial Completo:", weight="bold", as_="span"),
                                    " Incluye datos del paciente, antecedentes, consultas y estudios médicos",
                                ),
                            ),
                            rx.list_item(
                                rx.text(
                                    rx.text("Reporte de Consultas:", weight="bold", as_="span"),
                                    " Lista todas las consultas en el período seleccionado con motivos y diagnósticos",
                                ),
                            ),
                            rx.list_item(
                                rx.text(
                                    rx.text("Reporte de Estudios:", weight="bold", as_="span"),
                                    " Lista estudios médicos con opción de filtrar por tipo. Los estudios críticos se resaltan",
                                ),
                            ),
                            rx.list_item(
                                rx.text(
                                    rx.text("Formatos:", weight="bold", as_="span"),
                                    " PDF ideal para impresión, Excel para análisis de datos",
                                ),
                            ),
                        ),
                        spacing="3",
                        align_items="start",
                    ),
                    size="2",
                    margin_top="2rem",
                ),
                spacing="5",
                width="100%",
                padding="2rem",
            ),
            max_width="1400px",
            padding_x="2rem",
        ),
        width="100%",
        on_mount=ReportState.load_patients,
    )
