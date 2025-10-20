#!/usr/bin/env python3
"""Script temporal para generar hash de contraseña"""

import sys

try:
    from passlib.context import CryptContext
    
    if len(sys.argv) < 2:
        print("Uso: python generate_hash.py 'tu_password'")
        sys.exit(1)
    
    password = sys.argv[1]
    
    if len(password) > 72:
        print(f"⚠️  Contraseña muy larga ({len(password)} caracteres). Truncando a 72...")
        password = password[:72]
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash_result = pwd_context.hash(password)
    
    print(f"\n✅ Hash generado para la contraseña: '{password[:10]}...'")
    print(f"\nCopia este hash:\n{hash_result}\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nIntenta con una contraseña más corta (máximo 72 caracteres)")
