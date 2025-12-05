from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import os
from typing import List
from pathlib import Path

# ============================================
# CONFIGURACIÓN
# ============================================
app = FastAPI(title="Catan Blockchain API", version="1.0")

# CORS para conectar modelos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
BASE_DIR = Path(__file__).resolve().parent.parent
CONTRACT_SCRIPTS_DIR = BASE_DIR / "contract" / "scripts"

# Python del entorno virtual (para ejecutar scripts)
VENV_PYTHON = BASE_DIR / "models_venv" / "Scripts" / "python.exe"
if not VENV_PYTHON.exists():
    # Intentar path de Linux/Mac
    VENV_PYTHON = BASE_DIR / "models_venv" / "bin" / "python"
if not VENV_PYTHON.exists():
    # Fallback al python del sistema
    VENV_PYTHON = "python"
else:
    VENV_PYTHON = str(VENV_PYTHON)

# Diccionario de modelos a direcciones
MODELOS_MAP = {
    "MODELO_A": "PRIVATE_KEY_MODELO_A",
    "MODELO_B": "PRIVATE_KEY_MODELO_B",
    "BANCO": "PRIVATE_KEY_ADMIN_L1"
}

# ============================================
# MODELOS PYDANTIC
# ============================================
class Recurso(BaseModel):
    id: int
    cantidad: int

class TradeRequest(BaseModel):
    origen: str
    destino: str
    recursos: List[Recurso]

class TradeResponse(BaseModel):
    status: str
    mensaje: str
    hash_tx: str | None = None
    origen: str
    destino: str
    recursos: List[Recurso]

class BalanceResponse(BaseModel):
    modelo: str
    recursos: dict

class RobberAttackRequest(BaseModel):
    atacante: str  # Modelo que mueve el ladrón
    victima: str   # Modelo que pierde recursos
    recurso_id: int  # ID del recurso a robar (1-5)

class RobberAttackResponse(BaseModel):
    status: str
    mensaje: str
    hash_tx: str | None = None
    atacante: str
    victima: str
    recurso_robado: int

# ============================================
# HELPER FUNCTIONS
# ============================================
def ejecutar_script(script_name: str, args: list = None, silent: bool = False) -> dict:
    """
    Ejecuta un script Python desde /contract/scripts
    Retorna el output parseado como JSON o el texto
    """
    script_path = CONTRACT_SCRIPTS_DIR / f"{script_name}.py"
    
    if not script_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Script no encontrado: {script_name}"
        )
    
    try:
        cmd = [VENV_PYTHON, str(script_path)]
        if args:
            cmd.extend(args)
        
        if not silent:
            print(f"🔧 {script_name}: {args[0] if args else ''} → {args[1] if len(args) > 1 else ''}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(CONTRACT_SCRIPTS_DIR)
        )
        
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Error ejecutando {script_name}: {result.stderr}"
            )
        
        # Intentar parsear como JSON
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"output": result.stdout}
    
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail=f"Script {script_name} excedió timeout"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando script: {str(e)}"
        )

def validar_modelo(modelo: str):
    """Valida que el modelo existe"""
    if modelo not in MODELOS_MAP and modelo != "BANCO":
        raise HTTPException(
            status_code=400,
            detail=f"Modelo inválido: {modelo}. Debe ser MODELO_A, MODELO_B o BANCO"
        )

# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
def read_root():
    """Health check"""
    return {
        "status": "✅ API Catan Blockchain activa",
        "version": "1.0",
        "endpoints": {
            "POST /trade": "Enviar recursos",
            "GET /balance/{modelo}": "Consultar saldo"
        }
    }

@app.post("/trade", response_model=TradeResponse)
def trade(request: TradeRequest):
    """
    Endpoint principal para enviar recursos entre modelos y banco.
    
    Si origen == "BANCO": ejecuta mint (crear recursos)
    Si origen == "MODELO_A" o "MODELO_B": ejecuta transfer
    
    Args:
        request: TradeRequest con origen, destino y recursos
    
    Returns:
        TradeResponse con estado y hash de transacción
    """
    try:
        # Validaciones
        validar_modelo(request.origen)
        validar_modelo(request.destino)
        
        if request.origen == request.destino:
            raise HTTPException(
                status_code=400,
                detail="Origen y destino no pueden ser iguales"
            )
        
        if not request.recursos or len(request.recursos) == 0:
            raise HTTPException(
                status_code=400,
                detail="Debe especificar al menos un recurso"
            )
        
        tipo = "🏦 MINT" if request.origen == "BANCO" else "🔄 TRANSFER"
        print(f"{tipo}: {request.origen} → {request.destino} ({len(request.recursos)} recursos)")
        
        # Preparar argumentos para el script
        recursos_json = json.dumps([{"id": r.id, "cantidad": r.cantidad} for r in request.recursos])
        args = [request.origen, request.destino, recursos_json]
        
        # Ejecutar transacción usando el nuevo script
        result = ejecutar_script("execute_transaction", args)
        
        # Extraer hash de TX desde la respuesta
        # El script retorna: {"status": "success", "transacciones": [{"hash": "0x..."}, ...]}
        hash_tx = None
        if result.get("transacciones") and len(result.get("transacciones", [])) > 0:
            # Tomar el hash de la primera transacción
            hash_tx = result["transacciones"][0].get("hash")
        
        return TradeResponse(
            status="success",
            mensaje=f"Trade ejecutado: {request.origen} → {request.destino}",
            hash_tx=hash_tx,
            origen=request.origen,
            destino=request.destino,
            recursos=request.recursos
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en /trade: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando trade: {str(e)}"
        )

@app.get("/balance/{modelo}", response_model=BalanceResponse)
def get_balance(modelo: str):
    """
    Consulta el saldo de recursos de un modelo.
    
    Args:
        modelo: MODELO_A, MODELO_B o BANCO
    
    Returns:
        BalanceResponse con los saldos por recurso
    """
    try:
        validar_modelo(modelo)
        
        print(f"💰 BALANCE: {modelo}")
        
        # Ejecutar script de balance
        result = ejecutar_script("get_balance_simple", [modelo])
        
        # Formatear respuesta
        recursos = result.get("recursos", {})
        
        return BalanceResponse(
            modelo=modelo,
            recursos=recursos
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en /balance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error consultando balance: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Verifica que la API esté funcionando"""
    return {
        "status": "healthy",
        "contract_scripts_dir": str(CONTRACT_SCRIPTS_DIR),
        "scripts_available": [f.stem for f in CONTRACT_SCRIPTS_DIR.glob("*.py") if f.is_file()]
    }

@app.post("/robber/attack", response_model=RobberAttackResponse)
def robber_attack(request: RobberAttackRequest):
    """
    Endpoint para atacar con el ladrón (robber).
    El atacante roba 1 recurso de la víctima mediante transferencia blockchain.
    
    Args:
        request: RobberAttackRequest con atacante, victima y recurso_id
    
    Returns:
        RobberAttackResponse con estado y hash de transacción
    """
    try:
        # Validaciones
        validar_modelo(request.atacante)
        validar_modelo(request.victima)
        
        if request.atacante == request.victima:
            raise HTTPException(
                status_code=400,
                detail="El atacante no puede robarse a sí mismo"
            )
        
        if request.recurso_id < 1 or request.recurso_id > 5:
            raise HTTPException(
                status_code=400,
                detail="Recurso inválido. Debe ser entre 1 y 5"
            )
        
        print(f"\n🎲 LADRÓN: {request.atacante} ataca {request.victima} (ID:{request.recurso_id})")
        
        # Preparar transferencia: victima → atacante (1 unidad)
        recursos_json = json.dumps([{"id": request.recurso_id, "cantidad": 1}])
        args = [request.victima, request.atacante, recursos_json]
        
        # Ejecutar transferencia
        result = ejecutar_script("execute_transaction", args)
        
        # Extraer hash
        hash_tx = None
        if result.get("transacciones") and len(result.get("transacciones", [])) > 0:
            hash_tx = result["transacciones"][0].get("hash")
        
        return RobberAttackResponse(
            status="success",
            mensaje=f"Ladrón: {request.atacante} robó recurso {request.recurso_id} de {request.victima}",
            hash_tx=hash_tx,
            atacante=request.atacante,
            victima=request.victima,
            recurso_robado=request.recurso_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en /robber/attack: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando ataque del ladrón: {str(e)}"
        )

# ============================================
# MANEJO DE ERRORES GLOBAL
# ============================================
@app.get("/info")
def info():
    """Info sobre la configuración"""
    return {
        "api_version": "1.0",
        "base_dir": str(BASE_DIR),
        "contract_scripts": str(CONTRACT_SCRIPTS_DIR),
        "modelos_soportados": list(MODELOS_MAP.keys()),
        "recursos_soportados": {
            1: "MADERA",
            2: "ARCILLA",
            3: "OVEJA",
            4: "TRIGO",
            5: "MINERAL"
        }
    }
