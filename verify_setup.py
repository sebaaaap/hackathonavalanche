#!/usr/bin/env python3
"""
Verificador de setup - Ejecuta este archivo para confirmar que todo está instalado correctamente
"""

import sys
import subprocess
from pathlib import Path

def check_module(module_name: str) -> bool:
    """Verifica si un módulo está instalado"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def check_file(path: str) -> bool:
    """Verifica si un archivo existe"""
    return Path(path).exists()

def main():
    print("=" * 70)
    print("  ✓ VERIFICADOR DE SETUP - CATAN BLOCKCHAIN")
    print("=" * 70)
    
    # Base path
    base = Path(__file__).parent
    
    # ============================================
    # 1. Verificar archivos creados
    # ============================================
    print("\n📁 Verificando archivos...")
    
    files_to_check = {
        "api/main.py": "API FastAPI",
        "api/requirements.txt": "Dependencias API",
        "api/README.md": "Docs API",
        "models_venv/trade_client.py": "Cliente HTTP",
        "models_venv/ejemplo_integracion.py": "Ejemplos",
        "models_venv/README_API.md": "Docs Modelos",
        "models_venv/requirements_api.txt": "Dependencias Modelos",
        "BLOCKCHAIN_INTEGRATION.md": "Guía General",
        "setup.bat": "Script Setup",
    }
    
    missing_files = []
    for file_path, desc in files_to_check.items():
        full_path = base / file_path
        if check_file(str(full_path)):
            print(f"   ✅ {desc:30} {file_path}")
        else:
            print(f"   ❌ {desc:30} {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Faltan {len(missing_files)} archivo(s)")
        return False
    
    # ============================================
    # 2. Verificar módulos Python
    # ============================================
    print("\n📦 Verificando módulos Python...")
    
    modules_to_check = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "pydantic": "Pydantic",
        "requests": "Requests",
    }
    
    missing_modules = []
    for module, desc in modules_to_check.items():
        if check_module(module):
            print(f"   ✅ {desc:20} ({module})")
        else:
            print(f"   ❌ {desc:20} ({module}) - NO INSTALADO")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  Faltan {len(missing_modules)} módulo(s).")
        print(f"   Instala con: pip install {' '.join(missing_modules)}")
    
    # ============================================
    # 3. Verificar estructura de directorios
    # ============================================
    print("\n📂 Verificando estructura...")
    
    dirs_to_check = {
        "api": "Carpeta API",
        "models_venv": "Carpeta Modelos",
        "contract": "Carpeta Contratos",
        "contract/scripts": "Scripts Blockchain",
    }
    
    for dir_name, desc in dirs_to_check.items():
        dir_path = base / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"   ✅ {desc:25} /{dir_name}")
        else:
            print(f"   ❌ {desc:25} /{dir_name}")
    
    # ============================================
    # 4. Información final
    # ============================================
    print("\n" + "=" * 70)
    
    if missing_files or missing_modules:
        print("❌ SETUP INCOMPLETO")
        print("\nPróximos pasos:")
        if missing_modules:
            print(f"  1. Instalar módulos: pip install {' '.join(missing_modules)}")
        print("  2. Leer: BLOCKCHAIN_INTEGRATION.md")
        print("  3. Ejecutar: .\\setup.bat")
        return False
    else:
        print("✅ SETUP COMPLETADO CORRECTAMENTE")
        print("\n🚀 Próximos pasos:")
        print("  1. Levantar API:")
        print("     $ cd api")
        print("     $ uvicorn main:app --reload --port 8000")
        print()
        print("  2. En otra terminal, usar desde modelos:")
        print("     $ cd models_venv")
        print("     $ python ejemplo_integracion.py")
        print()
        print("  3. O importar en tu código:")
        print("     from trade_client import enviar_trade")
        print("     resultado = enviar_trade('MODELO_A', 'MODELO_B', [{'id': 1, 'cantidad': 5}])")
        print()
        print("📚 Documentación:")
        print("  - api/README.md (docs técnicas)")
        print("  - models_venv/README_API.md (guía para modelos)")
        print("  - BLOCKCHAIN_INTEGRATION.md (guía general)")
        print()
        print("=" * 70)
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
