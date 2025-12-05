#!/usr/bin/env python3
"""
Script para obtener balance desde blockchain.
Usado por la API FastAPI.

Uso:
  python get_balance_simple.py MODELO_NAME
  
Ejemplo:
  python get_balance_simple.py MODELO_A
"""

import os
import sys
import json
from dotenv import load_dotenv
from web3 import Web3

# Importar geth_poa_middleware de forma compatible con web3.py >= 6.0
try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware

# Cargar variables de entorno
load_dotenv()

# Configuración
CONTRACT_ADDRESS = os.getenv("CATAN_ADDRESS")
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"

# Diccionario de recursos
RECURSOS_IDS = {
    1: "MADERA",
    2: "ARCILLA",
    3: "OVEJA",
    4: "TRIGO",
    5: "MINERAL"
}

# ABI mínimo para balanceOf
ABI_MINIMAL = [{
    "constant": True,
    "inputs": [
        {"name": "account", "type": "address"},
        {"name": "id", "type": "uint256"}
    ],
    "name": "balanceOf",
    "outputs": [{"name": "", "type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
}]


def get_account_address(private_key):
    """Obtiene dirección desde clave privada"""
    try:
        w3_temp = Web3()
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        account = w3_temp.eth.account.from_key(private_key)
        return Web3.to_checksum_address(account.address)
    except Exception as e:
        print(f"Error obteniendo dirección: {str(e)}", file=sys.stderr)
        return None


def main():
    """Función principal"""
    
    # Validar argumentos
    if len(sys.argv) < 2:
        print("Error: Falta argumento MODELO_NAME", file=sys.stderr)
        print("Uso: python get_balance_simple.py MODELO_NAME", file=sys.stderr)
        sys.exit(1)
    
    modelo_name = sys.argv[1].upper()
    
    # Validar .env
    if not CONTRACT_ADDRESS:
        print("Error: CATAN_ADDRESS no está en .env", file=sys.stderr)
        sys.exit(1)
    
    # Mapeo de modelos a claves privadas
    MODELO_KEYS = {
        "BANCO": os.getenv("PRIVATE_KEY_ADMIN_L1"),
        "MODELO_A": os.getenv("PRIVATE_KEY_MODELO_A"),
        "MODELO_B": os.getenv("PRIVATE_KEY_MODELO_B"),
    }
    
    if modelo_name not in MODELO_KEYS:
        print(f"Error: Modelo '{modelo_name}' no válido", file=sys.stderr)
        sys.exit(1)
    
    private_key = MODELO_KEYS[modelo_name]
    if not private_key:
        print(f"Error: Clave privada para {modelo_name} no está en .env", file=sys.stderr)
        sys.exit(1)
    
    # Obtener dirección
    address = get_account_address(private_key)
    if not address:
        print(f"Error: No se pudo obtener dirección para {modelo_name}", file=sys.stderr)
        sys.exit(1)
    
    # Conectar a blockchain
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    # Inyectar middleware compatible con web3.py v6+
    try:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    except:
        # Para web3.py v6+
        w3.middleware_onion.inject(geth_poa_middleware(), layer=0)
    
    if not w3.is_connected():
        print("Error: No se pudo conectar a Avalanche", file=sys.stderr)
        sys.exit(1)
    
    # Crear instancia del contrato
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI_MINIMAL)
    
    # Consultar balance de cada recurso
    recursos = {}
    
    try:
        for resource_id, resource_name in RECURSOS_IDS.items():
            balance = contract.functions.balanceOf(address, resource_id).call()
            recursos[resource_name] = balance
    
    except Exception as e:
        print(f"Error consultando balance: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # Retornar resultado en JSON
    result = {
        "status": "success",
        "modelo": modelo_name,
        "address": address,
        "recursos": recursos
    }
    
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
