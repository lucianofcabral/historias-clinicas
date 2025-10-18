"""Página de configuración y backups"""

import reflex as rx

from app.components.navbar import navbar
from app.config import COLORS
from app.state.settings_state import SettingsState


def backup_card(backup: dict) -> rx.Component:
    """Tarjeta de backup individual"""
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.icon("database", size=20, color=COLORS["primary"]),
                    rx.text(
                        backup["filename"],
                        font_weight="600",
                        color=COLORS["text"],
                        size="3",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.text(
                        backup["date"],
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    rx.text("•", color=COLORS["text_secondary"]),
                    rx.text(
                        f"{backup['size_kb']} KB",
                        size="2",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="2",
                ),
                spacing="2",
                align="start",
                flex="1",
            ),
            rx.spacer(),
            rx.hstack(
                rx.button(
                    rx.icon("download", size=16),
                    "Restaurar",
                    variant="soft",
                    color_scheme="blue",
                    size="2",
                    on_click=lambda: SettingsState.restore_backup(backup["filename"]),
                ),
                rx.button(
                    rx.icon("trash-2", size=16),
                    variant="soft",
                    color_scheme="red",
                    size="2",
                    on_click=lambda: SettingsState.delete_backup(backup["filename"]),
                ),
                spacing="2",
            ),
            width="100%",
            align="center",
        ),
    )


def settings_page() -> rx.Component:
    """Página de configuración y backups"""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                # Título
                rx.heading(
                    "⚙️ Configuración y Backups",
                    size="8",
                    color=COLORS["text"],
                    margin_bottom="1.5rem",
                ),
                # Mensaje de feedback
                rx.cond(
                    SettingsState.message != "",
                    rx.callout(
                        SettingsState.message,
                        icon=rx.cond(
                            SettingsState.message_type == "success",
                            "circle_check",
                            "triangle_alert",
                        ),
                        color_scheme=rx.cond(
                            SettingsState.message_type == "success",
                            "green",
                            "red",
                        ),
                        margin_bottom="1rem",
                    ),
                    rx.box(),
                ),
                # Estadísticas de backups
                rx.card(
                    rx.vstack(
                        rx.heading(
                            "📊 Estadísticas de Backups",
                            size="5",
                            color=COLORS["text"],
                        ),
                        rx.grid(
                            rx.vstack(
                                rx.text(
                                    "Total de Backups",
                                    size="2",
                                    weight="bold",
                                    color=COLORS["text_secondary"],
                                ),
                                rx.heading(
                                    SettingsState.backup_stats["total_backups"].to_string(),
                                    size="6",
                                    color=COLORS["primary"],
                                ),
                                spacing="1",
                                align="start",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Espacio Utilizado",
                                    size="2",
                                    weight="bold",
                                    color=COLORS["text_secondary"],
                                ),
                                rx.heading(
                                    SettingsState.backup_stats["total_size_mb"].to_string() + " MB",
                                    size="6",
                                    color=COLORS["success"],
                                ),
                                spacing="1",
                                align="start",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Directorio",
                                    size="2",
                                    weight="bold",
                                    color=COLORS["text_secondary"],
                                ),
                                rx.text(
                                    SettingsState.backup_stats["backup_dir"].to_string(),
                                    size="2",
                                    color=COLORS["text"],
                                    word_break="break-all",
                                ),
                                spacing="1",
                                align="start",
                                width="100%",
                            ),
                            columns="3",
                            spacing="4",
                            width="100%",
                        ),
                        spacing="4",
                        align="start",
                        width="100%",
                    ),
                    margin_bottom="2rem",
                ),
                # Crear nuevo backup
                rx.card(
                    rx.vstack(
                        rx.heading(
                            "💾 Crear Nuevo Backup",
                            size="5",
                            color=COLORS["text"],
                        ),
                        rx.text(
                            "Crea una copia de seguridad completa de la base de datos. El backup se guardará comprimido en formato ZIP.",
                            size="2",
                            color=COLORS["text_secondary"],
                        ),
                        rx.button(
                            rx.icon("database", size=20),
                            "Crear Backup Ahora",
                            size="3",
                            color_scheme="blue",
                            on_click=SettingsState.create_backup,
                            loading=SettingsState.is_loading,
                        ),
                        spacing="3",
                        align="start",
                        width="100%",
                    ),
                    margin_bottom="2rem",
                ),
                # Lista de backups
                rx.heading(
                    "📂 Backups Disponibles",
                    size="5",
                    color=COLORS["text"],
                    margin_bottom="1rem",
                ),
                rx.cond(
                    SettingsState.backups.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            SettingsState.backups,
                            backup_card,
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.callout(
                        "No hay backups disponibles. Crea tu primer backup usando el botón de arriba.",
                        icon="info",
                        color_scheme="blue",
                    ),
                ),
                # Advertencias importantes
                rx.card(
                    rx.vstack(
                        rx.heading(
                            "⚠️ Información Importante",
                            size="4",
                            color=COLORS["warning"],
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.icon("triangle_alert", size=16, color=COLORS["warning"]),
                                rx.text(
                                    "Al restaurar un backup, la base de datos actual se reemplazará completamente.",
                                    size="2",
                                ),
                                spacing="2",
                                align="start",
                            ),
                            rx.hstack(
                                rx.icon("info", size=16, color=COLORS["info"]),
                                rx.text(
                                    "Se crea automáticamente un backup de seguridad antes de restaurar.",
                                    size="2",
                                ),
                                spacing="2",
                                align="start",
                            ),
                            rx.hstack(
                                rx.icon("rotate-ccw", size=16, color=COLORS["info"]),
                                rx.text(
                                    "Después de restaurar un backup, es necesario reiniciar la aplicación.",
                                    size="2",
                                ),
                                spacing="2",
                                align="start",
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        spacing="3",
                        align="start",
                        width="100%",
                    ),
                    style={"border_left": f"4px solid {COLORS['warning']}"},
                    margin_top="2rem",
                ),
                spacing="4",
                padding_y="2rem",
            ),
            max_width="1400px",
            padding_x="2rem",
        ),
        background=COLORS["background"],
        min_height="100vh",
        width="100%",
        on_mount=SettingsState.load_backups,
    )
