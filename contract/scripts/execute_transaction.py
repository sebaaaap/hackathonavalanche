#!/usr/bin/env python3
"""
Script para ejecutar transacciones en blockchain desde la línea de comandos.
Usado por la API FastAPI.

Uso:
  python execute_transaction.py ORIGEN DESTINO RECURSOS_JSON
  
Ejemplo:
  python execute_transaction.py BANCO MODELO_A '[{"id":1,"cantidad":5}]'
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

from solcx import compile_source, install_solc, set_solc_version

# Cargar variables de entorno
load_dotenv()

# Configuración
CONTRACT_ADDRESS = os.getenv("CATAN_ADDRESS")
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"

# Rutas para compilación
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONTRACT_PATH = os.path.join(os.path.dirname(BASE_DIR), 'contracts', 'RecursosCatan.sol')
NODE_MODULES_PATH = os.path.join(os.path.dirname(BASE_DIR), 'node_modules')


def get_account_details(private_key):
    """Obtiene dirección desde clave privada"""
    try:
        w3_temp = Web3()
        # Limpiar el prefijo 0x si existe
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        account = w3_temp.eth.account.from_key(private_key)
        return {
            "private_key": private_key,
            "address": Web3.to_checksum_address(account.address)
        }
    except Exception as e:
        print(f"Error obteniendo cuenta: {str(e)}", file=sys.stderr)
        return None


def main():
    """Función principal"""
    
    # Validar argumentos
    if len(sys.argv) < 4:
        print("Error: Argumentos insuficientes", file=sys.stderr)
        print("Uso: python execute_transaction.py ORIGEN DESTINO RECURSOS_JSON", file=sys.stderr)
        sys.exit(1)
    
    origen_name = sys.argv[1].upper()
    destino_name = sys.argv[2].upper()
    recursos_json = sys.argv[3]
    
    # Parsear recursos
    try:
        recursos_list = json.loads(recursos_json)
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON de recursos: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # Validar .env
    if not CONTRACT_ADDRESS:
        print("Error: CATAN_ADDRESS no está en .env", file=sys.stderr)
        sys.exit(1)
    
    # Mapeo de cuentas
    ACCOUNT_MAP = {
        "BANCO": get_account_details(os.getenv("PRIVATE_KEY_ADMIN_L1")),
        "MODELO_A": get_account_details(os.getenv("PRIVATE_KEY_MODELO_A")),
        "MODELO_B": get_account_details(os.getenv("PRIVATE_KEY_MODELO_B")),
    }
    
    # Validar cuentas
    for name, details in ACCOUNT_MAP.items():
        if details is None:
            print(f"Error: Clave privada para {name} es inválida", file=sys.stderr)
            sys.exit(1)
    
    # Validar origen y destino
    if origen_name not in ACCOUNT_MAP:
        print(f"Error: Origen '{origen_name}' no válido", file=sys.stderr)
        sys.exit(1)
    
    if destino_name not in ACCOUNT_MAP:
        print(f"Error: Destino '{destino_name}' no válido", file=sys.stderr)
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
    
    # Compilar contrato para obtener ABI
    try:
        install_solc('0.8.20')
        set_solc_version('0.8.20')
        
        with open(CONTRACT_PATH, 'r', encoding='utf-8') as f:
            source = f.read()
        
        REMAPS = [f"@openzeppelin/={NODE_MODULES_PATH}/@openzeppelin/"]
        
        compiled = compile_source(
            source,
            output_values=['abi'],
            solc_version='0.8.20',
            import_remappings=REMAPS,
            allow_paths=[NODE_MODULES_PATH]
        )
        
        contract_interface = next((v for k, v in compiled.items() if ':RecursosCatan' in k))
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_interface['abi'])
    
    except Exception as e:
        print(f"Error compilando contrato: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # Obtener detalles de las cuentas
    origen_details = ACCOUNT_MAP[origen_name]
    destino_details = ACCOUNT_MAP[destino_name]
    owner_details = ACCOUNT_MAP["BANCO"]
    
    # Ejecutar transacciones
    hashes = []
    
    try:
        for recurso in recursos_list:
            token_id = recurso.get('id')
            cantidad = recurso.get('cantidad', 0)
            
            if not token_id or cantidad <= 0:
                print(f"Error: Recurso inválido {recurso}", file=sys.stderr)
                continue
            
            # Determinar tipo de transacción
            if origen_name == "BANCO":
                # MINT: El banco crea recursos
                print(f"Minteando {cantidad} tokens ID {token_id} para {destino_name}...")
                
                # Construir transacción de mint
                mint_txn = contract.functions.mint(
                    destino_details["address"],
                    token_id,
                    cantidad,
                    b''
                ).build_transaction({
                    'from': owner_details["address"],
                    'nonce': w3.eth.get_transaction_count(owner_details["address"]),
                    'gas': 200000,
                    'gasPrice': w3.eth.gas_price
                })
                
                # Firmar transacción
                signed_txn = w3.eth.account.sign_transaction(
                    mint_txn,
                    private_key=owner_details["private_key"]
                )
                
                # Enviar transacción
                tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                hashes.append({
                    "tipo": "mint",
                    "hash": tx_hash.hex(),
                    "status": receipt['status']
                })
                
                print(f"[OK] Mint exitoso: {tx_hash.hex()}")
            
            else:
                # TRANSFER: Transferencia entre modelos
                print(f"Transfiriendo {cantidad} tokens ID {token_id} de {origen_name} a {destino_name}...")
                
                # Construir transacción de transferencia
                transfer_txn = contract.functions.safeTransferFrom(
                    origen_details["address"],
                    destino_details["address"],
                    token_id,
                    cantidad,
                    b''
                ).build_transaction({
                    'from': origen_details["address"],
                    'nonce': w3.eth.get_transaction_count(origen_details["address"]),
                    'gas': 200000,
                    'gasPrice': w3.eth.gas_price
                })
                
                # Firmar transacción
                signed_txn = w3.eth.account.sign_transaction(
                    transfer_txn,
                    private_key=origen_details["private_key"]
                )
                
                # Enviar transacción
                tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                
                hashes.append({
                    "tipo": "transfer",
                    "hash": tx_hash.hex(),
                    "status": receipt['status']
                })
                
                print(f"[OK] Transferencia exitosa: {tx_hash.hex()}")
    
    except Exception as e:
        print(f"Error ejecutando transacción: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # Retornar resultado en JSON
    result = {
        "status": "success",
        "origen": origen_name,
        "destino": destino_name,
        "transacciones": hashes
    }
    
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
