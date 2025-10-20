"""
Servicio de gestión de backups de la base de datos
Compatible con SQLite (desarrollo) y PostgreSQL (producción)
"""

from pathlib import Path
from datetime import datetime
import shutil
import zipfile
import subprocess
import os


class BackupService:
    """Servicio para crear y restaurar backups"""

    @staticmethod
    def get_backup_dir() -> Path:
        """Obtiene el directorio de backups"""
        backup_dir = Path.cwd() / "backups"
        backup_dir.mkdir(exist_ok=True)
        return backup_dir

    @staticmethod
    def get_db_type() -> str:
        """Detecta el tipo de base de datos en uso"""
        try:
            from app.config import DATABASE_URL

            if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
                return "postgresql"
        except:
            pass
        return "sqlite"

    @staticmethod
    def get_db_path() -> Path:
        """Obtiene la ruta del archivo de la base de datos SQLite"""
        return Path.cwd() / "medical_records.db"

    @staticmethod
    def get_postgres_config() -> dict:
        """Obtiene la configuración de PostgreSQL desde DATABASE_URL"""
        try:
            from app.config import DATABASE_URL

            # Parsear: postgresql://user:password@host:port/database
            url = DATABASE_URL.replace("postgresql://", "")
            user_pass, host_db = url.split("@")
            user, password = user_pass.split(":")
            host_port, database = host_db.split("/")
            host, port = host_port.split(":") if ":" in host_port else (host_port, "5432")

            return {
                "user": user,
                "password": password,
                "host": host,
                "port": port,
                "database": database,
            }
        except Exception as e:
            return {}

    @staticmethod
    def create_backup() -> dict:
        """
        Crea un backup de la base de datos (SQLite o PostgreSQL)

        Returns:
            dict con información del backup creado
        """
        try:
            db_type = BackupService.get_db_type()
            backup_dir = BackupService.get_backup_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if db_type == "sqlite":
                # Backup de SQLite
                db_path = BackupService.get_db_path()

                if not db_path.exists():
                    return {
                        "success": False,
                        "message": "La base de datos SQLite no existe",
                    }

                backup_name = f"backup_{timestamp}.db"
                backup_path = backup_dir / backup_name

                # Copiar la base de datos
                shutil.copy2(db_path, backup_path)

                # Crear archivo ZIP comprimido
                zip_name = f"backup_{timestamp}.zip"
                zip_path = backup_dir / zip_name

                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(backup_path, backup_name)

                # Eliminar el archivo .db sin comprimir
                backup_path.unlink()

                file_size = zip_path.stat().st_size / 1024  # KB

                return {
                    "success": True,
                    "message": "Backup SQLite creado exitosamente",
                    "filename": zip_name,
                    "path": str(zip_path),
                    "size_kb": round(file_size, 2),
                    "timestamp": timestamp,
                }

            else:
                # Backup de PostgreSQL con pg_dump
                pg_config = BackupService.get_postgres_config()

                if not pg_config:
                    return {
                        "success": False,
                        "message": "No se pudo obtener la configuración de PostgreSQL",
                    }

                backup_name = f"backup_{timestamp}.sql"
                backup_path = backup_dir / backup_name

                # Detectar si PostgreSQL está en Docker
                is_docker = pg_config["host"] == "localhost" or pg_config["host"] == "127.0.0.1"

                if is_docker:
                    # Usar docker exec para ejecutar pg_dump dentro del contenedor
                    cmd = [
                        "docker",
                        "exec",
                        "hc_postgres",  # Nombre del contenedor
                        "pg_dump",
                        "-U",
                        pg_config["user"],
                        "-d",
                        pg_config["database"],
                        "-F",
                        "c",  # Custom format (comprimido)
                    ]

                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                    )

                    if result.returncode == 0:
                        # Guardar el output en el archivo
                        backup_path.write_bytes(result.stdout)

                else:
                    # Comando pg_dump directo (PostgreSQL local)
                    env = os.environ.copy()
                    env["PGPASSWORD"] = pg_config["password"]

                    cmd = [
                        "pg_dump",
                        "-h",
                        pg_config["host"],
                        "-p",
                        pg_config["port"],
                        "-U",
                        pg_config["user"],
                        "-d",
                        pg_config["database"],
                        "-F",
                        "c",  # Custom format (comprimido)
                        "-f",
                        str(backup_path),
                    ]

                    result = subprocess.run(
                        cmd,
                        env=env,
                        capture_output=True,
                        text=True,
                    )

                if result.returncode != 0:
                    return {
                        "success": False,
                        "message": f"Error en pg_dump: {result.stderr}",
                    }

                # Crear ZIP del dump
                zip_name = f"backup_{timestamp}.zip"
                zip_path = backup_dir / zip_name

                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(backup_path, backup_name)

                # Eliminar el archivo .sql sin comprimir
                backup_path.unlink()

                file_size = zip_path.stat().st_size / 1024  # KB

                return {
                    "success": True,
                    "message": "Backup PostgreSQL creado exitosamente",
                    "filename": zip_name,
                    "path": str(zip_path),
                    "size_kb": round(file_size, 2),
                    "timestamp": timestamp,
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error al crear backup: {str(e)}",
            }

    @staticmethod
    def restore_backup(backup_filename: str) -> dict:
        """
        Restaura un backup de la base de datos (SQLite o PostgreSQL)

        Args:
            backup_filename: Nombre del archivo de backup

        Returns:
            dict con el resultado de la operación
        """
        try:
            db_type = BackupService.get_db_type()
            backup_dir = BackupService.get_backup_dir()
            backup_path = backup_dir / backup_filename

            if not backup_path.exists():
                return {
                    "success": False,
                    "message": "El archivo de backup no existe",
                }

            if db_type == "sqlite":
                # Restaurar SQLite
                db_path = BackupService.get_db_path()

                # Crear backup de seguridad de la base actual
                if db_path.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safety_backup = backup_dir / f"pre_restore_{timestamp}.db"
                    shutil.copy2(db_path, safety_backup)

                # Extraer y restaurar
                with zipfile.ZipFile(backup_path, "r") as zipf:
                    # Extraer el primer archivo .db del ZIP
                    db_files = [f for f in zipf.namelist() if f.endswith(".db")]
                    if not db_files:
                        return {
                            "success": False,
                            "message": "El archivo ZIP no contiene una base de datos SQLite",
                        }

                    # Extraer a un archivo temporal
                    temp_path = backup_dir / "temp_restore.db"
                    with (
                        zipf.open(db_files[0]) as source,
                        open(temp_path, "wb") as target,
                    ):
                        shutil.copyfileobj(source, target)

                    # Reemplazar la base de datos actual
                    shutil.move(str(temp_path), str(db_path))

                return {
                    "success": True,
                    "message": "Backup SQLite restaurado exitosamente. Reinicia la aplicación para ver los cambios.",
                }

            else:
                # Restaurar PostgreSQL
                pg_config = BackupService.get_postgres_config()

                if not pg_config:
                    return {
                        "success": False,
                        "message": "No se pudo obtener la configuración de PostgreSQL",
                    }

                # Extraer el dump del ZIP
                temp_path = backup_dir / "temp_restore.sql"
                with zipfile.ZipFile(backup_path, "r") as zipf:
                    sql_files = [f for f in zipf.namelist() if f.endswith(".sql")]
                    if not sql_files:
                        return {
                            "success": False,
                            "message": "El archivo ZIP no contiene un dump de PostgreSQL",
                        }

                    with (
                        zipf.open(sql_files[0]) as source,
                        open(temp_path, "wb") as target,
                    ):
                        shutil.copyfileobj(source, target)

                # Detectar si PostgreSQL está en Docker
                is_docker = pg_config["host"] == "localhost" or pg_config["host"] == "127.0.0.1"

                if is_docker:
                    # Copiar el archivo al contenedor
                    copy_cmd = ["docker", "cp", str(temp_path), "hc_postgres:/tmp/restore.sql"]
                    subprocess.run(copy_cmd, capture_output=True)

                    # Restaurar con pg_restore desde el contenedor
                    restore_cmd = [
                        "docker",
                        "exec",
                        "hc_postgres",
                        "pg_restore",
                        "-U",
                        pg_config["user"],
                        "-d",
                        pg_config["database"],
                        "-c",  # Clean (drop) database objects before recreating
                        "--if-exists",
                        "/tmp/restore.sql",
                    ]

                    result = subprocess.run(
                        restore_cmd,
                        capture_output=True,
                        text=True,
                    )

                    # Limpiar archivo temporal del contenedor
                    subprocess.run(
                        ["docker", "exec", "hc_postgres", "rm", "/tmp/restore.sql"],
                        capture_output=True,
                    )

                else:
                    # Restaurar con pg_restore directo (PostgreSQL local)
                    env = os.environ.copy()
                    env["PGPASSWORD"] = pg_config["password"]

                    # Restaurar el dump
                    restore_cmd = [
                        "pg_restore",
                        "-h",
                        pg_config["host"],
                        "-p",
                        pg_config["port"],
                        "-U",
                        pg_config["user"],
                        "-d",
                        pg_config["database"],
                        "-c",  # Clean (drop) database objects before recreating
                        str(temp_path),
                    ]

                    result = subprocess.run(
                        restore_cmd,
                        env=env,
                        capture_output=True,
                        text=True,
                    )

                # Eliminar archivo temporal
                temp_path.unlink()

                if result.returncode != 0:
                    return {
                        "success": False,
                        "message": f"Error en pg_restore: {result.stderr}",
                    }

                return {
                    "success": True,
                    "message": "Backup PostgreSQL restaurado exitosamente. Reinicia la aplicación para ver los cambios.",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error al restaurar backup: {str(e)}",
            }

    @staticmethod
    def list_backups() -> list[dict]:
        """
        Lista todos los backups disponibles

        Returns:
            Lista de diccionarios con información de cada backup
        """
        try:
            backup_dir = BackupService.get_backup_dir()
            backups = []

            for backup_file in sorted(backup_dir.glob("backup_*.zip"), reverse=True):
                stat = backup_file.stat()
                size_kb = stat.st_size / 1024

                # Extraer timestamp del nombre del archivo
                filename = backup_file.name
                timestamp_str = filename.replace("backup_", "").replace(".zip", "")

                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    formatted_date = timestamp.strftime("%d/%m/%Y %H:%M:%S")
                except ValueError:
                    formatted_date = "Fecha desconocida"

                backups.append(
                    {
                        "filename": filename,
                        "size_kb": round(size_kb, 2),
                        "date": formatted_date,
                        "timestamp": timestamp_str,
                    }
                )

            return backups

        except Exception as e:
            print(f"Error al listar backups: {e}")
            return []

    @staticmethod
    def delete_backup(backup_filename: str) -> dict:
        """
        Elimina un backup

        Args:
            backup_filename: Nombre del archivo de backup

        Returns:
            dict con el resultado de la operación
        """
        try:
            backup_dir = BackupService.get_backup_dir()
            backup_path = backup_dir / backup_filename

            if not backup_path.exists():
                return {
                    "success": False,
                    "message": "El archivo de backup no existe",
                }

            backup_path.unlink()

            return {
                "success": True,
                "message": "Backup eliminado exitosamente",
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error al eliminar backup: {str(e)}",
            }

    @staticmethod
    def get_backup_stats() -> dict:
        """
        Obtiene estadísticas de los backups

        Returns:
            dict con estadísticas
        """
        try:
            backup_dir = BackupService.get_backup_dir()
            backups = list(backup_dir.glob("backup_*.zip"))

            total_size = sum(f.stat().st_size for f in backups)
            total_size_mb = total_size / (1024 * 1024)

            return {
                "total_backups": len(backups),
                "total_size_mb": round(total_size_mb, 2),
                "backup_dir": str(backup_dir),
            }

        except Exception as e:
            return {
                "total_backups": 0,
                "total_size_mb": 0.0,
                "backup_dir": "Error",
                "error": str(e),
            }
