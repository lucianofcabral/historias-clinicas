"""Endpoint para descarga de archivos de estudios médicos"""


def download_study_file(study_id: int):
    """
    Endpoint para descargar archivos de estudios médicos

    Args:
        study_id: ID del estudio

    Returns:
        dict con la ruta del archivo

    Raises:
        ValueError: Si el estudio no existe o no tiene archivo
    """
    from app.database import get_session
    from app.services import MedicalStudyService

    session = next(get_session())
    try:
        result = MedicalStudyService.download_file(session, study_id)

        if not result:
            raise ValueError("El estudio no tiene archivo adjunto")

        file_path, file_name = result

        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_name}")

        # Retornar info del archivo
        return {
            "file_path": str(file_path),
            "file_name": file_name,
        }

    finally:
        session.close()
