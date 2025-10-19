"""
Componente reutilizable para seleccionar pacientes
"""
import reflex as rx


def patient_selector(
    patients_options,
    value: str,
    on_change: callable,
    placeholder: str = "Seleccione un paciente...",
    required: bool = True,
    width: str = "100%",
):
    """
    Componente selector de pacientes con formato amigable
    
    Las opciones deben tener formato: "ID: 1 - Nombre Apellido (DNI: 12345678)"
    El valor seleccionado será el string completo, y el callback debe parsear el ID.

    Args:
        patients_options: Lista de strings con formato "ID: X - Nombre..."
        value: Valor actual seleccionado (ID como string)
        on_change: Función callback al cambiar selección
        placeholder: Texto placeholder
        required: Si es campo requerido
        width: Ancho del componente

    Returns:
        Componente rx.select configurado
    """
    # patients_options should be a list of label strings or a Var that resolves to such a list.
    # rx.select accepts a list (or Var) of strings directly.
    return rx.select(
        patients_options,
        placeholder=placeholder,
        value=value,
        on_change=on_change,
        width=width,
        required=required,
    )





def patient_selector_with_label(
    label: str,
    patients_options,
    value: str,
    on_change: callable,
    placeholder: str = "Seleccione un paciente...",
    required: bool = True,
    help_text: str | None = None,
):
    """
    Componente completo con label, selector y texto de ayuda

    Args:
        label: Etiqueta del campo
        patients_options: Lista de opciones (tuplas de id y label)
        value: Valor seleccionado
        on_change: Callback
        placeholder: Texto placeholder
        required: Si es requerido
        help_text: Texto de ayuda opcional

    Returns:
        Componente rx.vstack con label y selector
    """
    label_color = "#64748b"  # text_secondary

    components = [
        rx.text(
            label + (" *" if required else ""),
            font_weight="500",
            color=label_color,
        ),
        patient_selector(
            patients_options=patients_options,
            value=value,
            on_change=on_change,
            placeholder=placeholder,
            required=required,
            width="100%",
        ),
    ]

    # Agregar texto de ayuda si existe
    if help_text:
        components.append(
            rx.text(
                help_text,
                font_size="12px",
                color="#94a3b8",
                margin_top="4px",
            )
        )

    return rx.vstack(
        *components,
        spacing="2",
        align_items="stretch",
        width="100%",
    )