#!/usr/bin/env python3
"""Script para generar hash de contraseña compatible"""

import sys
import getpass

# Usar bcrypt directamente sin passlib
try:
    import bcrypt
    
    if len(sys.argv) < 2:
        password = getpass.getpass("Ingresa tu contraseña: ")
    else:
        password = sys.argv[1]
    
    # Convertir a bytes
    password_bytes = password.encode('utf-8')
    
    # Generar salt y hash
    salt = bcrypt.gensalt()
    hash_result = bcrypt.hashpw(password_bytes, salt)
    
    # Convertir a string
    hash_str = hash_result.decode('utf-8')
    
    print(f"\n✅ Hash generado exitosamente!")
    print(f"\nCopia este hash para tu .env:\n")
    print(hash_str)
    print()
    
except ImportError:
    print("❌ Error: bcrypt no está instalado")
    print("Instala con: uv pip install bcrypt")
except Exception as e:
    print(f"❌ Error: {e}")
