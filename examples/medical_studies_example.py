"""
Script de ejemplo para demostrar el uso de MedicalStudyService

Este script muestra cómo:
1. Crear estudios médicos
2. Subir archivos
3. Consultar estudios
4. Eliminar archivos/estudios
"""

from datetime import date
from pathlib import Path

from app.database import get_session
from app.models import StudyType
from app.services import MedicalStudyService


def ejemplo_crear_estudios():
    """Ejemplo: Crear estudios médicos para un paciente"""
    print("\n=== CREANDO ESTUDIOS MÉDICOS ===\n")

    with get_session() as session:
        # Crear un análisis de laboratorio
        estudio1 = MedicalStudyService.create_study(
            session=session,
            patient_id=1,  # ID del paciente
            study_type=StudyType.LABORATORY,
            study_name="Hemograma Completo",
            study_date=date(2024, 10, 15),
            institution="Laboratorio Central",
            results="""
            Glóbulos rojos: 4.5 millones/μL (Normal)
            Hemoglobina: 14.2 g/dL (Normal)
            Hematocrito: 42% (Normal)
            Leucocitos: 7200/μL (Normal)
            Plaquetas: 250,000/μL (Normal)
            """,
        )
        print(f"✅ Estudio creado: {estudio1.study_name} (ID: {estudio1.id})")

        # Crear una radiografía
        estudio2 = MedicalStudyService.create_study(
            session=session,
            patient_id=1,
            study_type=StudyType.RADIOLOGY,
            study_name="Radiografía de Tórax",
            study_date=date(2024, 10, 18),
            institution="Centro de Diagnóstico por Imágenes",
            results="Sin hallazgos patológicos. Campos pulmonares despejados.",
        )
        print(f"✅ Estudio creado: {estudio2.study_name} (ID: {estudio2.id})")

        return estudio1.id, estudio2.id


def ejemplo_subir_archivo(study_id: int):
    """Ejemplo: Subir un archivo a un estudio"""
    print("\n=== SUBIENDO ARCHIVO ===\n")

    # Crear un archivo de ejemplo (en la práctica vendría del formulario)
    ejemplo_texto = "Este es un archivo de ejemplo de resultados de laboratorio"
    archivo_temp = Path("/tmp/ejemplo_estudio.txt")
    archivo_temp.write_text(ejemplo_texto)

    with get_session() as session:
        with open(archivo_temp, "rb") as file:
            estudio = MedicalStudyService.upload_file(
                session=session,
                study_id=study_id,
                file_content=file,
                file_name="resultados_laboratorio.txt",
                file_type="text/plain",
            )

        print(f"✅ Archivo subido: {estudio.file_name}")
        print(f"   Ruta: {estudio.file_path}")
        print(f"   Tamaño: {estudio.file_size_mb} MB")

    # Limpiar
    archivo_temp.unlink()


def ejemplo_consultar_estudios(patient_id: int):
    """Ejemplo: Consultar estudios de un paciente"""
    print("\n=== CONSULTANDO ESTUDIOS ===\n")

    with get_session() as session:
        # Todos los estudios del paciente
        estudios = MedicalStudyService.get_studies_by_patient(session, patient_id)
        print(f"Total de estudios: {len(estudios)}")

        for estudio in estudios:
            print(f"\n📄 {estudio.study_name}")
            print(f"   Tipo: {estudio.study_type}")
            print(f"   Fecha: {estudio.study_date}")
            print(f"   Hace {estudio.days_since_study} días")
            print(f"   Reciente: {'Sí' if estudio.is_recent() else 'No'}")
            print(f"   Tiene archivos: {'Sí' if estudio.has_files else 'No'}")

        # Solo estudios de laboratorio
        print("\n--- Estudios de Laboratorio ---")
        labs = MedicalStudyService.get_studies_by_patient(
            session, patient_id, study_type=StudyType.LABORATORY
        )
        print(f"Total: {len(labs)}")

        # Estudios recientes (últimos 90 días)
        print("\n--- Estudios Recientes (90 días) ---")
        recientes = MedicalStudyService.get_recent_studies(session, patient_id, days=90)
        print(f"Total: {len(recientes)}")


def ejemplo_almacenamiento(patient_id: int):
    """Ejemplo: Consultar almacenamiento usado"""
    print("\n=== ALMACENAMIENTO ===\n")

    with get_session() as session:
        # Por paciente
        size_patient = MedicalStudyService.get_total_storage_size(session, patient_id)
        print(f"Espacio usado por paciente {patient_id}: {size_patient / 1024:.2f} KB")

        # Total
        size_total = MedicalStudyService.get_total_storage_size(session)
        print(f"Espacio total usado: {size_total / 1024:.2f} KB")


def ejemplo_eliminar(study_id: int):
    """Ejemplo: Eliminar archivo y estudio"""
    print("\n=== ELIMINACIÓN ===\n")

    with get_session() as session:
        # Solo eliminar el archivo (mantener el registro)
        estudio = MedicalStudyService.delete_study_file(session, study_id)
        print(f"✅ Archivo eliminado del estudio: {estudio.study_name}")
        print(f"   El registro del estudio aún existe (ID: {estudio.id})")

        # Eliminar el estudio completo
        # MedicalStudyService.delete_study(session, study_id)
        # print(f"✅ Estudio eliminado completamente")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("EJEMPLO DE USO: MedicalStudyService")
    print("=" * 50)

    # 1. Crear estudios
    estudio1_id, estudio2_id = ejemplo_crear_estudios()

    # 2. Subir archivo al primer estudio
    ejemplo_subir_archivo(estudio1_id)

    # 3. Consultar estudios
    ejemplo_consultar_estudios(patient_id=1)

    # 4. Ver almacenamiento
    ejemplo_almacenamiento(patient_id=1)

    # 5. Eliminar archivo (opcional - comentado para no alterar datos)
    # ejemplo_eliminar(estudio1_id)

    print("\n" + "=" * 50)
    print("FIN DEL EJEMPLO")
    print("=" * 50 + "\n")
