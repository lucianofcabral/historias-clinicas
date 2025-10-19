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


def download_consultation_file(file_id: int):
    """
    Endpoint para descargar archivos de consultas médicas

    Args:
        file_id: ID del archivo de consulta

    Returns:
        dict con la ruta del archivo

    Raises:
        ValueError: Si el archivo no existe
    """
    from app.database import get_session
    from app.services import ConsultationFileService

    session = next(get_session())
    try:
        result = ConsultationFileService.download_file(session, file_id)

        if not result:
            raise ValueError("El archivo no existe")

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
