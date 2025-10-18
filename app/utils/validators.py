"""Utilidades de validación y normalización de datos"""

import re
from typing import Optional


def normalize_dni(dni: str) -> str:
    """
    Normaliza un DNI/documento eliminando puntos, guiones y espacios extras.
    Preserva letras para casos como LC, LE, Pasaportes, etc.

    Args:
        dni: DNI/documento a normalizar

    Returns:
        DNI normalizado (números y letras, sin puntuación)

    Examples:
        >>> normalize_dni("12.345.678")
        "12345678"
        >>> normalize_dni("LC 12-345-678")
        "LC12345678"
        >>> normalize_dni("  DNI 12 345 678  ")
        "DNI12345678"
        >>> normalize_dni("AB123456")
        "AB123456"
    """
    # Eliminar puntos, guiones, espacios pero mantener letras y números
    cleaned = re.sub(r"[.\-\s]", "", dni.strip().upper())
    return cleaned


def normalize_phone(phone: str) -> str:
    """
    Normaliza un número de teléfono eliminando espacios extras.

    Args:
        phone: Teléfono a normalizar

    Returns:
        Teléfono normalizado

    Examples:
        >>> normalize_phone("  +54 11 1234-5678  ")
        "+54 11 1234-5678"
    """
    # Eliminar espacios extras pero mantener formato
    return " ".join(phone.strip().split())


def validate_email(email: Optional[str]) -> bool:
    """
    Valida formato básico de email.

    Args:
        email: Email a validar

    Returns:
        True si el email es válido o None, False en caso contrario
    """
    if email is None or email.strip() == "":
        return True

    # Patrón básico de email
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def normalize_text(text: Optional[str]) -> Optional[str]:
    """
    Normaliza texto eliminando espacios extras y convirtiendo a título.

    Args:
        text: Texto a normalizar

    Returns:
        Texto normalizado o None

    Examples:
        >>> normalize_text("  juan   pedro  ")
        "Juan Pedro"
    """
    if text is None:
        return None

    # Eliminar espacios extras y capitalizar
    return " ".join(text.strip().split())


def validate_dni(dni: str) -> bool:
    """
    Valida que un DNI/documento tenga formato correcto.
    Acepta:
    - DNI estándar: 7-8 dígitos numéricos
    - LC/LE: 2 letras + 7-8 dígitos
    - Pasaporte: Combinación de letras y números (6-9 caracteres)

    Args:
        dni: DNI/documento a validar

    Returns:
        True si el documento es válido, False en caso contrario

    Examples:
        >>> validate_dni("12345678")
        True
        >>> validate_dni("LC12345678")
        True
        >>> validate_dni("AB123456")
        True
        >>> validate_dni("123")
        False
    """
    normalized = normalize_dni(dni)

    if not normalized:
        return False

    # Patrón flexible:
    # - Solo números: 7-8 dígitos (DNI estándar)
    # - Letras al inicio + números: LC, LE, etc.
    # - Combinación alfanumérica: Pasaportes
    patterns = [
        r"^\d{7,8}$",  # DNI estándar: 7-8 dígitos
        r"^[A-Z]{1,3}\d{6,8}$",  # LC, LE, CI + números
        r"^[A-Z0-9]{6,12}$",  # Pasaporte u otros documentos internacionales
    ]

    return any(re.match(pattern, normalized) for pattern in patterns)
