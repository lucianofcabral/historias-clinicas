"""
Script para probar el servicio de backup con PostgreSQL en Docker
"""

from app.services.backup_service import BackupService

print("🔧 Probando servicio de backup con PostgreSQL...")
print("=" * 60)

# Probar creación de backup
print("\n📦 Creando backup...")
result = BackupService.create_backup()

if result["success"]:
    print(f"✅ {result['message']}")
    print(f"   📄 Archivo: {result['filename']}")
    print(f"   💾 Tamaño: {result['size_kb']} KB")
    print(f"   📁 Ruta: {result['path']}")
else:
    print(f"❌ Error: {result['message']}")

print("\n" + "=" * 60)
