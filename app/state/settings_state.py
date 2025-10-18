"""Estado para la página de configuración y backups"""

import reflex as rx

from app.services.backup_service import BackupService


class SettingsState(rx.State):
    """Estado para configuración y backups"""

    # Backups
    backups: list[dict] = []
    backup_stats: dict = {}

    # Mensajes
    message: str = ""
    message_type: str = ""  # "success" o "error"

    # Loading
    is_loading: bool = False

    def load_backups(self):
        """Carga la lista de backups"""
        self.backups = BackupService.list_backups()
        self.backup_stats = BackupService.get_backup_stats()

    def create_backup(self):
        """Crea un nuevo backup"""
        self.is_loading = True
        yield

        result = BackupService.create_backup()

        if result["success"]:
            self.message = f"{result['message']} - {result['filename']} ({result['size_kb']} KB)"
            self.message_type = "success"
            # Recargar la lista
            self.load_backups()
        else:
            self.message = result["message"]
            self.message_type = "error"

        self.is_loading = False

    def restore_backup(self, filename: str):
        """Restaura un backup"""
        self.is_loading = True
        yield

        result = BackupService.restore_backup(filename)

        self.message = result["message"]
        self.message_type = "success" if result["success"] else "error"

        self.is_loading = False

    def delete_backup(self, filename: str):
        """Elimina un backup"""
        result = BackupService.delete_backup(filename)

        self.message = result["message"]
        self.message_type = "success" if result["success"] else "error"

        if result["success"]:
            self.load_backups()
