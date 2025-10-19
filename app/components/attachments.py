"""
Componente para mostrar archivos adjuntos (lista) con botones de vista previa y descarga.

Interfaz pública:
- attachments_list: lista de dicts con keys: file_name, file_path, file_type, file_size
- on_download: callback (file_path)
- preview_enabled: bool (si se permite vista previa)

Este componente solo construye la UI; la descarga real se hace mediante rx.download
o mediante un endpoint que implementaremos en `app/services`.
"""
import reflex as rx

from app.config import COLORS


def attachments_list_component(attachments, on_download, preview_enabled: bool = True):
    """Renderiza una lista de archivos adjuntos.

    attachments: lista (o Var) de objetos con: file_name, file_path, file_type, file_size
    on_download: callback que recibe file_path
    preview_enabled: si True muestra botón de vista previa para PDF/imagenes
    """

    def render_item(a):
        # Work reactively: assume 'a' provides Vars for fields.
        # a puede ser un mapping o una lista. Intentar acceso por clave, si falla usar índices.
        try:
            name = a["file_name"]
            fpath = a["file_path"]
            fsize = a["file_size"]
        except Exception:
            name = a[0]
            fpath = a[1]
            fsize = a[3]

        # Mostrar tamaño en bytes si existe (usar to_string para Vars)
        readable_size = rx.cond(
            fsize,
            fsize.to_string() + " bytes",
            "",
        )

        # Botón de descarga (llama al callback con la ruta)
        download_btn = rx.button(
            rx.icon("download", size=14),
            "Descargar",
            size="1",
            variant="ghost",
            color_scheme="green",
            on_click=lambda: on_download(fpath),
        )

        # Botón de vista previa solo si preview_enabled y tipo permitido
        # Mostrar vista previa si existe ruta del archivo (evitamos operaciones complejas sobre ftype)
        # Usar un enlace para abrir la ruta en una nueva pestaña (evitamos llamadas inexistentes a rx.open_url)
        # Usar un botón que ejecuta window.open(v) a través de call_script para evitar validaciones de tipos
        preview_btn = rx.cond(
            fpath.is_not_none(),
            rx.button(
                rx.icon("eye", size=14),
                "Vista previa",
                size="1",
                variant="soft",
                on_click=lambda: rx.call_script(f"window.open('{fpath}', '_blank')"),
            ),
            rx.box(),
        )

        return rx.hstack(
            rx.icon("paperclip", size=18, color=COLORS["primary"]),
            rx.vstack(
                rx.text(name, weight="bold"),
                rx.text(readable_size, size="2", color=COLORS["text_secondary"]),
                spacing="0",
                align_items="start",
            ),
            rx.spacer(),
            rx.hstack(preview_btn, download_btn, spacing="2"),
            spacing="3",
            align="center",
            width="100%",
        )

    # Usar rx.foreach para soportar Vars
    return rx.vstack(
        rx.foreach(attachments, render_item),
        spacing="3",
        width="100%",
    )
