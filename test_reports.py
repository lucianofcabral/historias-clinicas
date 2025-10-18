"""
Script de prueba para generar reportes
"""
from datetime import date
from app.services.report_service import ReportService


def test_patient_history_pdf():
    """Prueba generar historial de paciente en PDF"""
    print("🔍 Probando: Historial de Paciente (PDF)...")

    try:
        pdf_bytes = ReportService.generate_patient_history_pdf(patient_id=1)

        # Guardar archivo de prueba
        output_path = "test_patient_1_history.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

        print(f"✅ PDF generado exitosamente: {output_path}")
        print(f"   Tamaño: {len(pdf_bytes)} bytes")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_patient_history_excel():
    """Prueba generar historial de paciente en Excel"""
    print("\n🔍 Probando: Historial de Paciente (Excel)...")

    try:
        excel_bytes = ReportService.generate_patient_history_excel(patient_id=1)

        # Guardar archivo de prueba
        output_path = "test_patient_1_history.xlsx"
        with open(output_path, "wb") as f:
            f.write(excel_bytes)

        print(f"✅ Excel generado exitosamente: {output_path}")
        print(f"   Tamaño: {len(excel_bytes)} bytes")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_consultations_report():
    """Prueba generar reporte de consultas"""
    print("\n🔍 Probando: Reporte de Consultas (PDF)...")

    try:
        # Últimos 3 meses
        start_date = date(2025, 8, 1)
        end_date = date(2025, 10, 18)

        pdf_bytes = ReportService.generate_consultations_report_pdf(
            start_date=start_date,
            end_date=end_date
        )

        # Guardar archivo de prueba
        output_path = "test_consultations_report.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

        print(f"✅ Reporte generado exitosamente: {output_path}")
        print(f"   Período: {start_date} a {end_date}")
        print(f"   Tamaño: {len(pdf_bytes)} bytes")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_studies_report():
    """Prueba generar reporte de estudios"""
    print("\n🔍 Probando: Reporte de Estudios (Excel)...")

    try:
        # Últimos 3 meses
        start_date = date(2025, 8, 1)
        end_date = date(2025, 10, 18)

        excel_bytes = ReportService.generate_studies_report_excel(
            study_type=None,  # Todos los tipos
            start_date=start_date,
            end_date=end_date
        )

        # Guardar archivo de prueba
        output_path = "test_studies_report.xlsx"
        with open(output_path, "wb") as f:
            f.write(excel_bytes)

        print(f"✅ Reporte generado exitosamente: {output_path}")
        print(f"   Período: {start_date} a {end_date}")
        print(f"   Tamaño: {len(excel_bytes)} bytes")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBAS DE GENERACIÓN DE REPORTES")
    print("=" * 60)

    results = []

    # Ejecutar todas las pruebas
    results.append(("Historial PDF", test_patient_history_pdf()))
    results.append(("Historial Excel", test_patient_history_excel()))
    results.append(("Consultas PDF", test_consultations_report()))
    results.append(("Estudios Excel", test_studies_report()))

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(1 for _, s in results if s)

    print(f"\nTotal: {passed}/{total} pruebas pasaron")
    print("=" * 60)

