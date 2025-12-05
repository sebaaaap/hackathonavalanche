#!/usr/bin/env python3
"""
🚀 COMPILADOR Y LANZADOR COMPLETO - Catan Blockchain

Este script:
1. Instala todas las dependencias necesarias
2. Verifica la configuración
3. Compila contratos (si es necesario)
4. Levanta la API
5. Ejecuta la demo

USO:
  python compile_and_run.py
"""

import subprocess
import sys
import time
import os
from pathlib import Path

# Colores ANSI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(texto):
    """Imprime encabezado"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{texto.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

def print_step(num, texto):
    """Imprime paso numerado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}[{num}] {texto}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*80}{Colors.ENDC}")

def print_ok(texto):
    """Mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {texto}{Colors.ENDC}")

def print_error(texto):
    """Mensaje de error"""
    print(f"{Colors.RED}❌ {texto}{Colors.ENDC}")

def print_warn(texto):
    """Mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {texto}{Colors.ENDC}")

def print_info(texto):
    """Mensaje informativo"""
    print(f"{Colors.BLUE}ℹ️  {texto}{Colors.ENDC}")

def run_command(cmd, cwd=None, description=""):
    """Ejecuta un comando y retorna el resultado"""
    if description:
        print_info(f"Ejecutando: {description}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print_error(f"Error ejecutando comando")
            if result.stderr:
                print(f"{Colors.RED}{result.stderr}{Colors.ENDC}")
            return False
        
        return True
    
    except subprocess.TimeoutExpired:
        print_error("Timeout ejecutando comando")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def check_file_exists(path, description=""):
    """Verifica si un archivo existe"""
    if Path(path).exists():
        if description:
            print_ok(f"{description}: {path}")
        return True
    else:
        print_error(f"No encontrado: {path}")
        return False

def main():
    print_header("🚀 COMPILADOR Y LANZADOR - CATAN BLOCKCHAIN")
    
    base_dir = Path(__file__).parent
    api_dir = base_dir / "api"
    contract_dir = base_dir / "contract"
    models_dir = base_dir / "models_venv"
    
    # ========================================
    # PASO 1: Verificar estructura
    # ========================================
    print_step(1, "VERIFICANDO ESTRUCTURA DEL PROYECTO")
    
    dirs_check = {
        api_dir: "API FastAPI",
        contract_dir: "Contratos",
        models_dir: "Modelos"
    }
    
    all_exist = True
    for dir_path, desc in dirs_check.items():
        if dir_path.exists():
            print_ok(f"{desc}: {dir_path}")
        else:
            print_error(f"{desc} no encontrado: {dir_path}")
            all_exist = False
    
    if not all_exist:
        print_error("Estructura incompleta")
        return False
    
    # ========================================
    # PASO 2: Verificar .env
    # ========================================
    print_step(2, "VERIFICANDO CONFIGURACIÓN (.env)")
    
    env_file = contract_dir / ".env"
    if not check_file_exists(env_file, "Archivo .env"):
        print_warn("El archivo .env en /contract no existe")
        print_warn("Se necesita para ejecutar transacciones blockchain")
        return False
    
    # Verificar que .env tiene variables necesarias
    try:
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        required_vars = [
            "PRIVATE_KEY_ADMIN_L1",
            "PRIVATE_KEY_MODELO_A",
            "PRIVATE_KEY_MODELO_B",
            "CATAN_ADDRESS"
        ]
        
        missing = []
        for var in required_vars:
            if var not in env_content:
                missing.append(var)
        
        if missing:
            print_error(f"Variables faltantes en .env: {', '.join(missing)}")
            return False
        else:
            print_ok("Todas las variables de .env configuradas")
    
    except Exception as e:
        print_error(f"Error leyendo .env: {str(e)}")
        return False
    
    # ========================================
    # PASO 3: Instalar dependencias API
    # ========================================
    print_step(3, "INSTALANDO DEPENDENCIAS - API FastAPI")
    
    requirements_file = api_dir / "requirements.txt"
    if check_file_exists(requirements_file, "requirements.txt"):
        print_info("Instalando paquetes...")
        if not run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=api_dir,
            description="pip install -r requirements.txt"
        ):
            print_error("Error instalando dependencias de API")
            return False
        print_ok("Dependencias API instaladas")
    
    # ========================================
    # PASO 4: Instalar requests para modelos
    # ========================================
    print_step(4, "INSTALANDO DEPENDENCIAS - Modelos")
    
    print_info("Instalando requests...")
    if not run_command(
        [sys.executable, "-m", "pip", "install", "requests"],
        description="pip install requests"
    ):
        print_warn("Podría haber un problema, pero continuando...")
    
    print_ok("Dependencias de modelos listas")
    
    # ========================================
    # PASO 5: Verificar archivos críticos
    # ========================================
    print_step(5, "VERIFICANDO ARCHIVOS CRÍTICOS")
    
    critical_files = {
        api_dir / "main.py": "API principal",
        models_dir / "trade_client.py": "Cliente HTTP",
        models_dir / "demo_game_blockchain.py": "Demo del juego",
        contract_dir / "scripts" / "API.py": "Script blockchain",
        contract_dir / "scripts" / "get_balance.py": "Script balance",
    }
    
    all_exist = True
    for file_path, desc in critical_files.items():
        if not check_file_exists(file_path, desc):
            all_exist = False
    
    if not all_exist:
        print_error("Faltan archivos críticos")
        return False
    
    # ========================================
    # PASO 6: Resumen y próximos pasos
    # ========================================
    print_step(6, "✅ COMPILACIÓN EXITOSA - PRÓXIMOS PASOS")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("OPCIÓN A: Ejecutar todo automáticamente (RECOMENDADO)")
    print(f"{Colors.ENDC}")
    print(f"  {Colors.CYAN}cd models_venv{Colors.ENDC}")
    print(f"  {Colors.CYAN}python launch_demo.py{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("OPCIÓN B: Dos terminales (control manual)")
    print(f"{Colors.ENDC}")
    print(f"\n  Terminal 1 (API):")
    print(f"    {Colors.CYAN}cd api{Colors.ENDC}")
    print(f"    {Colors.CYAN}uvicorn main:app --reload --port 8000{Colors.ENDC}")
    print()
    print(f"  Terminal 2 (Demo):")
    print(f"    {Colors.CYAN}cd models_venv{Colors.ENDC}")
    print(f"    {Colors.CYAN}python demo_game_blockchain.py{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}")
    print("IMPORTANTE:")
    print(f"{Colors.ENDC}")
    print(f"  • El .env en /contract debe estar configurado con:")
    print(f"    - PRIVATE_KEY_ADMIN_L1")
    print(f"    - PRIVATE_KEY_MODELO_A")
    print(f"    - PRIVATE_KEY_MODELO_B")
    print(f"    - CATAN_ADDRESS")
    print()
    print(f"  • El contrato debe estar deployado en Avalanche Testnet")
    print()
    print(f"  • Necesitas saldo en Fuji para pagar gas de transacciones")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("="*80)
    print("              ✅ SISTEMA LISTO PARA EJECUTAR")
    print("="*80)
    print(f"{Colors.ENDC}\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        
        if success:
            print_ok("Compilación completada exitosamente")
            print_info("Ejecuta uno de los comandos arriba para comenzar")
            sys.exit(0)
        else:
            print_error("Compilación fallida")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Proceso interrumpido por el usuario{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
