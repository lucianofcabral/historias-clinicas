"""
Estado para la página de reportes
"""

import reflex as rx
from datetime import date, datetime
from typing import Optional
import base64

from app.services.report_service import ReportService
from sqlmodel import Session, select
from app.database import engine
from app.models.patient import Patient


class ReportState(rx.State):
    """Estado para gestionar reportes y exportaciones"""

    # Filtros
    selected_patient_id: int = 0
    selected_report_type: str = "patient_history"
    selected_format: str = "pdf"
    start_date: str = ""
    end_date: str = ""
    selected_study_type: str = ""

    # UI
    is_loading: bool = False
    message: str = ""
    message_type: str = "info"

    # Pacientes para el selector
    patients: list[dict] = []
    patients_list: list[dict] = []  # Alias para compatibilidad con selector
    patients_options: list[str] = []  # Lista de labels para el selector
    patients_map: dict = {}  # mapa label -> id

    # Setters explícitos
    def set_selected_report_type(self, value: str):
        """Setter para selected_report_type"""
        self.selected_report_type = value

    def set_selected_format(self, value: str):
        """Setter para selected_format"""
        self.selected_format = value

    def set_start_date(self, value: str):
        """Setter para start_date"""
        self.start_date = value

    def set_end_date(self, value: str):
        """Setter para end_date"""
        self.end_date = value

    def set_patient_id_from_string(self, value: str):
        """Convierte el string del input a int para selected_patient_id"""
        # El selector puede entregar la etiqueta (label) en vez de un número.
        # Intentamos resolverla buscando en patients_options.
        val = (value or "").strip()
        if not val:
            self.selected_patient_id = 0
            return

        # Buscar en patients_map
        if val in self.patients_map:
            try:
                self.selected_patient_id = int(self.patients_map[val])
                return
            except ValueError:
                pass

        # Fallback: intentar parsear número en la cadena
        import re

        m = re.search(r"(\d+)", val)
        if m:
            try:
                self.selected_patient_id = int(m.group(1))
                return
            except ValueError:
                self.selected_patient_id = 0
                return

        self.selected_patient_id = 0

    def set_study_type_from_select(self, value: str):
        """Maneja el cambio de tipo de estudio, convirtiendo 'Todos' a cadena vacía"""
        self.selected_study_type = "" if value == "Todos" else value

    def set_format_from_radio(self, value: str):
        """Convierte el valor del radio (PDF/Excel) a minúsculas"""
        self.selected_format = value.lower()

    def load_patients(self):
        """Carga la lista de pacientes activos"""
        with Session(engine) as session:
            patients_db = session.exec(
                select(Patient)
                .where(Patient.is_active == True)
                .order_by(Patient.last_name, Patient.first_name)
            ).all()

            self.patients = [
                {
                    "id": p.id,
                    "name": f"{p.last_name}, {p.first_name}",
                    "dni": p.dni or "Sin DNI",
                }
                for p in patients_db
            ]

            # Sincronizar con patients_list para el selector
            self.patients_list = [
                {
                    "id": p.id,
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                    "dni": p.dni or "",
                }
                for p in patients_db
            ]

            # Generar opciones formateadas para el selector
            opts = []
            pmap = {}
            for p in patients_db:
                label = (
                    f"{p.first_name} {p.last_name} (DNI: {p.dni})"
                    if p.dni
                    else f"{p.first_name} {p.last_name}"
                )
                opts.append(label)
                pmap[label] = p.id

            self.patients_options = opts
            self.patients_map = pmap

    def generate_report(self):
        """Genera el reporte según los parámetros seleccionados"""
        self.is_loading = True
        self.message = ""

        try:
            # Validaciones
            if self.selected_report_type == "patient_history" and not self.selected_patient_id:
                self.message = "Selecciona un paciente"
                self.message_type = "error"
                self.is_loading = False
                return

            # Convertir fechas si existen
            start_date_obj = None
            end_date_obj = None

            if self.start_date:
                start_date_obj = datetime.strptime(self.start_date, "%Y-%m-%d").date()

            if self.end_date:
                end_date_obj = datetime.strptime(self.end_date, "%Y-%m-%d").date()

            # Generar reporte
            if self.selected_report_type == "patient_history":
                if self.selected_format == "pdf":
                    content = ReportService.generate_patient_history_pdf(self.selected_patient_id)
                    filename = f"historial_paciente_{self.selected_patient_id}.pdf"
                    mime_type = "application/pdf"
                else:
                    content = ReportService.generate_patient_history_excel(self.selected_patient_id)
                    filename = f"historial_paciente_{self.selected_patient_id}.xlsx"
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            elif self.selected_report_type == "consultations":
                if self.selected_format == "pdf":
                    content = ReportService.generate_consultations_report_pdf(
                        start_date=start_date_obj, end_date=end_date_obj
                    )
                    filename = f"reporte_consultas_{datetime.now().strftime('%Y%m%d')}.pdf"
                    mime_type = "application/pdf"
                else:
                    # Por ahora solo PDF para consultas
                    self.message = "Formato Excel no disponible para este reporte"
                    self.message_type = "warning"
                    self.is_loading = False
                    return

            elif self.selected_report_type == "studies":
                if self.selected_format == "excel":
                    content = ReportService.generate_studies_report_excel(
                        study_type=self.selected_study_type if self.selected_study_type else None,
                        start_date=start_date_obj,
                        end_date=end_date_obj,
                    )
                    filename = f"reporte_estudios_{datetime.now().strftime('%Y%m%d')}.xlsx"
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                else:
                    # Por ahora solo Excel para estudios
                    self.message = "Formato PDF no disponible para este reporte"
                    self.message_type = "warning"
                    self.is_loading = False
                    return

            # Descargar archivo
            return rx.download(
                data=content,
                filename=filename,
            )

        except Exception as e:
            self.message = f"Error al generar reporte: {str(e)}"
            self.message_type = "error"

        finally:
            self.is_loading = False

    def export_patient_pdf(self, patient_id: int):
        """Exporta el historial de un paciente a PDF (acción rápida)"""
        self.is_loading = True

        try:
            content = ReportService.generate_patient_history_pdf(patient_id)
            filename = f"historial_paciente_{patient_id}.pdf"

            return rx.download(
                data=content,
                filename=filename,
            )

        except Exception as e:
            self.message = f"Error al exportar: {str(e)}"
            self.message_type = "error"

        finally:
            self.is_loading = False

    def export_patient_excel(self, patient_id: int):
        """Exporta el historial de un paciente a Excel (acción rápida)"""
        self.is_loading = True

        try:
            content = ReportService.generate_patient_history_excel(patient_id)
            filename = f"historial_paciente_{patient_id}.xlsx"

            return rx.download(
                data=content,
                filename=filename,
            )

        except Exception as e:
            self.message = f"Error al exportar: {str(e)}"
            self.message_type = "error"

        finally:
            self.is_loading = False
