"""
API router para operaciones relacionadas con estudios médicos (descarga de archivos).

Este módulo expone un endpoint GET /api/studies/{study_id}/download que valida
la existencia del estudio y sirve el archivo con StreamingResponse y encabezados
adecuados. Usa la sesión de la DB desde app.database.get_db_session().
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.database import get_session
from app.services import MedicalStudyService

router = APIRouter(prefix="/api/studies", tags=["studies"])


@router.get("/{study_id}/download")
def download_study(study_id: int, session=Depends(get_session)):
    """Descarga segura del archivo asociado a un estudio.

    - Valida que el estudio exista
    - Obtiene la ruta absoluta del archivo desde MedicalStudyService
    - Devuelve un StreamingResponse con Content-Disposition attachment
    """
    try:
        res = MedicalStudyService.download_file(session, study_id)
        if not res:
            raise HTTPException(status_code=404, detail="No hay archivo para este estudio")

        file_path, file_name = res
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Archivo no encontrado en disco")

        # Abrir el archivo en modo binario y devolver streaming
        def iterfile():
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(1024 * 64), b""):
                    yield chunk

        content_type = "application/octet-stream"
        # Intentar inferir desde la extensión sencilla
        suffix = file_path.suffix.lower()
        if suffix in [".pdf"]:
            content_type = "application/pdf"
        elif suffix in [".png", ".jpg", ".jpeg", ".gif"]:
            content_type = f"image/{suffix.lstrip('.')}"

        headers = {"Content-Disposition": f'attachment; filename="{file_name}"'}

        return StreamingResponse(iterfile(), media_type=content_type, headers=headers)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
