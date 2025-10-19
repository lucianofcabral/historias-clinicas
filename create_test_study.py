#!/usr/bin/env python3
"""
Script para crear un estudio médico de prueba con archivo adjunto.
Úsalo para probar la funcionalidad de descarga de archivos.
"""

import sys
from pathlib import Path
from datetime import date

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import get_session
from app.models import MedicalStudy, Patient, StudyType
from app.services import MedicalStudyService


def create_test_study_with_file():
    """Crea un estudio de prueba con un archivo PDF de ejemplo"""
    
    session = next(get_session())
    
    try:
        # 1. Obtener el primer paciente activo
        from sqlmodel import select
        statement = select(Patient).where(Patient.is_active == True).limit(1)
        patient = session.exec(statement).first()
        
        if not patient:
            print("❌ No hay pacientes en la base de datos. Crea un paciente primero.")
            return
        
        print(f"✓ Usando paciente: {patient.full_name} (ID: {patient.id})")
        
        # 2. Crear un estudio de prueba
        study = MedicalStudyService.create_study(
            session=session,
            patient_id=patient.id,
            study_type=StudyType.LABORATORY,
            study_name="Análisis de sangre completo (PRUEBA)",
            study_date=date.today(),
            institution="Hospital Central",
            results="Hemoglobina: 14.5 g/dL\nGlucosa: 95 mg/dL\nColesterol: 180 mg/dL",
        )
        
        print(f"✓ Estudio creado: {study.study_name} (ID: {study.id})")
        
        # 3. Crear un archivo PDF de prueba
        test_file_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 55
>>
stream
BT
/F1 24 Tf
100 700 Td
(Estudio Medico de Prueba) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
421
%%EOF"""
        
        # 4. Guardar el archivo usando el servicio
        from io import BytesIO
        file_io = BytesIO(test_file_content)
        
        study = MedicalStudyService.upload_file(
            session=session,
            study_id=study.id,
            file_content=file_io,
            file_name="analisis_sangre_prueba.pdf",
            file_type="application/pdf",
        )
        
        print(f"✓ Archivo adjuntado: {study.file_name}")
        print(f"✓ Ruta: {study.file_path}")
        print(f"✓ Tamaño: {study.file_size} bytes")
        print(f"\n✅ LISTO! Ahora puedes probar la descarga desde la interfaz:")
        print(f"   1. Ve a http://localhost:3000/patients/{patient.id}")
        print(f"   2. Busca el estudio '{study.study_name}'")
        print(f"   3. Haz clic en 'Descargar archivo'")
        print(f"\n   O ve a http://localhost:3000/studies y busca el estudio")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 60)
    print("CREADOR DE ESTUDIO DE PRUEBA CON ARCHIVO")
    print("=" * 60)
    create_test_study_with_file()
    print("=" * 60)
