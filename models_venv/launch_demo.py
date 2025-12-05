#!/usr/bin/env python3
"""
Script de lanzamiento rápido para la DEMO completa.
Ejecuta la API y la demo en paralelo en una sola terminal.

USO:
  python launch_demo.py

Requisitos:
  - Python 3.8+
  - Dependencias instaladas: pip install -r api/requirements.txt && pip install requests
"""

import subprocess
import time
import sys
import os
from pathlib import Path

# Colores
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(numero, texto):
    print(f"\n{Colors.BOLD}{Colors.CYAN}[{numero}/5] {texto}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*70}{Colors.ENDC}")

def print_ok(texto):
    print(f"{Colors.GREEN}✅ {texto}{Colors.ENDC}")

def print_error(texto):
    print(f"{Colors.RED}❌ {texto}{Colors.ENDC}")

def print_info(texto):
    print(f"{Colors.BLUE}ℹ️  {texto}{Colors.ENDC}")

def main():
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("="*70)
    print("   🎮 LANZADOR DE DEMO - CATAN CON BLOCKCHAIN 🎮")
    print("="*70)
    print(f"{Colors.ENDC}")
    
    # Paso 1: Verificar directorios
    print_step(1, "Verificando estructura de directorios")
    
    base_dir = Path(__file__).parent.parent
    api_dir = base_dir / "api"
    models_dir = base_dir / "models_venv"
    
    if not api_dir.exists():
        print_error(f"Carpeta /api no encontrada en {api_dir}")
        return False
    
    if not models_dir.exists():
        print_error(f"Carpeta /models_venv no encontrada en {models_dir}")
        return False
    
    print_ok(f"Directorio API: {api_dir}")
    print_ok(f"Directorio modelos: {models_dir}")
    
    # Paso 2: Verificar archivos
    print_step(2, "Verificando archivos necesarios")
    
    archivos_requeridos = {
        api_dir / "main.py": "API FastAPI",
        api_dir / "requirements.txt": "Dependencias API",
        models_dir / "trade_client.py": "Cliente HTTP",
        models_dir / "demo_game_blockchain.py": "Demo del juego",
    }
    
    for archivo, desc in archivos_requeridos.items():
        if not archivo.exists():
            print_error(f"{desc} no encontrado: {archivo}")
            return False
        print_ok(f"{desc}: {archivo.name}")
    
    # Paso 3: Lanzar API
    print_step(3, "Iniciando API FastAPI")
    
    print_info("Lanzando: uvicorn main:app --reload --port 8000")
    print_info("Espera a que se inicie completamente...")
    
    try:
        api_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
            cwd=str(api_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar a que la API esté lista
        time.sleep(3)
        
        if api_process.poll() is not None:
            # El proceso terminó, hay un error
            _, stderr = api_process.communicate()
            print_error(f"Error iniciando API: {stderr}")
            return False
        
        print_ok("✓ API iniciada en http://127.0.0.1:8000")
        
    except Exception as e:
        print_error(f"Error lanzando API: {str(e)}")
        return False
    
    # Paso 4: Pequeña pausa
    print_step(4, "Esperando a que la API esté lista")
    
    print_info("Esperando 3 segundos...")
    for i in range(3, 0, -1):
        print_info(f"   {i}...")
        time.sleep(1)
    
    print_ok("API lista para recibir requests")
    
    # Paso 5: Lanzar demo
    print_step(5, "Iniciando demo del juego")
    
    print_info("Lanzando: python demo_game_blockchain.py")
    print_info("")
    print(f"{Colors.YELLOW}{'='*70}{Colors.ENDC}")
    print()
    
    try:
        demo_process = subprocess.Popen(
            ["python", "demo_game_blockchain.py"],
            cwd=str(models_dir)
        )
        
        # Esperar a que la demo termine
        demo_process.wait()
        
        if demo_process.returncode == 0:
            print()
            print(f"{Colors.YELLOW}{'='*70}{Colors.ENDC}")
            print_ok("Demo completada exitosamente!")
        else:
            print_error(f"Demo terminó con código {demo_process.returncode}")
        
    except Exception as e:
        print_error(f"Error ejecutando demo: {str(e)}")
    
    finally:
        # Terminar API
        print_info("Limpiando recursos...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
        print_ok("API detenida")
    
    print()
    print(f"{Colors.BOLD}{Colors.GREEN}")
    print("="*70)
    print("   ✅ DEMO COMPLETADA")
    print("="*70)
    print(f"{Colors.ENDC}")
    print()
    print_info("Puedes verificar las transacciones en:")
    print(f"   {Colors.CYAN}https://testnet.snowtrace.io{Colors.ENDC}")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Programa interrumpido por el usuario{Colors.ENDC}")
        sys.exit(1)
