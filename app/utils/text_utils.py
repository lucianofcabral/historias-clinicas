"""Utilidades para manejo de texto"""

import unicodedata


def remove_accents(text: str) -> str:
    """
    Remueve acentos y diacríticos de un texto.

    Convierte 'á' -> 'a', 'é' -> 'e', 'ñ' -> 'n', etc.

    Args:
        text: Texto con posibles acentos

    Returns:
        Texto sin acentos

    Examples:
        >>> remove_accents("José García")
        'Jose Garcia'
        >>> remove_accents("María Pérez")
        'Maria Perez'
    """
    if not text:
        return text

    # NFD = Canonical Decomposition (separa caracteres base de diacríticos)
    nfd_form = unicodedata.normalize("NFD", text)

    # Filtra solo los caracteres que NO son marcas diacríticas
    # Category Mn = Mark, Nonspacing (acentos, tildes, etc.)
    without_accents = "".join(char for char in nfd_form if unicodedata.category(char) != "Mn")

    return without_accents


def normalize_search_term(text: str) -> str:
    """
    Normaliza un término de búsqueda removiendo acentos y convirtiendo a minúsculas.

    Args:
        text: Término de búsqueda

    Returns:
        Término normalizado

    Examples:
        >>> normalize_search_term("José García")
        'jose garcia'
    """
    if not text:
        return ""

    return remove_accents(text.strip()).lower()
