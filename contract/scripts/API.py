import os
import json
from flask import Flask, jsonify, request
# --- IMPORTA CORS ---
from flask_cors import CORS
# --- (Otras importaciones) ---
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware
from solcx import install_solc, set_solc_version, compile_source
# ...

app = Flask(__name__)
# --- INICIALIZA CORS ---
# Permite solicitudes desde tu frontend React (localhost:3000)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# --- CONFIGURACIÓN DE CLAVES Y ENDPOINTS ---
load_dotenv()
CONTRACT_ADDRESS = os.getenv("CATAN_ADDRESS")
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"

# --- Mapeo de Cuentas (Nombres a Claves/Direcciones) ---
def get_account_details(private_key):
    """Función para obtener la dirección a partir de la clave privada."""
    if not private_key:
        return None
    try:
        w3_temp = Web3()
        account = w3_temp.eth.account.from_key(private_key)
        return {"private_key": private_key, "address": Web3.to_checksum_address(account.address)}
    except Exception:
        return None

# Definimos las claves y obtenemos los detalles de la cuenta.
ACCOUNT_MAP = {
    "BANCO": get_account_details(os.getenv("PRIVATE_KEY_ADMIN_L1")),
    "MODELO_A": get_account_details(os.getenv("PRIVATE_KEY_MODELO_A")),
    "MODELO_B": get_account_details(os.getenv("PRIVATE_KEY_MODELO_B")),
}

# --- VALIDACIÓN Y DEFINICIÓN DEL OWNER ---
for name, details in ACCOUNT_MAP.items():
    if details is None and name != "BANCO": # Permitimos que BANCO pueda ser None si no lo estás usando para firmar
         # Nota: Si PRIVATE_KEY_ADMIN_L1 es vital, usar raise ValueError aquí.
         # Aquí asumimos que los modelos A y B SIEMPRE deben existir.
         if os.getenv(f"PRIVATE_KEY_{name}") is None:
             print(f"⚠️ Advertencia: Clave privada para {name} no encontrada. El modelo no podrá firmar transacciones.")
         else:
             raise ValueError(f"❌ Error: La clave privada para {name} en el .env es inválida.")


OWNER_DETAILS = ACCOUNT_MAP.get("BANCO")
OWNER_ADDRESS = OWNER_DETAILS["address"] if OWNER_DETAILS else None
PRIVATE_KEY_OWNER = OWNER_DETAILS["private_key"] if OWNER_DETAILS else None
# -----------------------------

# Rutas para compilación
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONTRACT_PATH = os.path.join(os.path.dirname(BASE_DIR), 'contracts', 'RecursosCatan.sol')
NODE_MODULES_PATH = os.path.join(os.path.dirname(BASE_DIR), 'node_modules')

# Diccionario de IDs de recursos (se usa para validación si el JSON viniera por nombre)
RECURSOS_IDS = {
    "MADERA": 1, "ARCILLA": 2, "OVEJA": 3, "TRIGO": 4, "MINERAL": 5
}

# ----------------------------------------------------
# --- SOLUCIÓN 1 & 2: DEFINICIÓN DE IDS Y MAPEO ---
# ----------------------------------------------------
# 1. Definimos la lista de IDs (Variable faltante en el prompt anterior)
TODOS_LOS_IDS = list(RECURSOS_IDS.values()) 

# 2. Creamos el mapeo inverso (ID a Nombre) para usar en consultar_saldos
ID_A_NOMBRE = {v: k for k, v in RECURSOS_IDS.items()}
# ----------------------------------------------------

# --- PREPARACIÓN (Carga de ABI y Web3) ---
if not CONTRACT_ADDRESS:
    raise ValueError("❌ Error: Verifica CATAN_ADDRESS en el .env.")

print("⚙️  Conectando a Avalanche...")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
print(f"✅ Owner del contrato: {OWNER_ADDRESS}")

print("⚙️  Cargando contrato (Compilando para obtener ABI)...")
# ... (Código de compilación y carga de contrato)
install_solc('0.8.20')
set_solc_version('0.8.20')

with open(CONTRACT_PATH, 'r') as f:
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

print(f"✅ Servidor listo. Controlando contrato en: {CONTRACT_ADDRESS}")

# --- EL ENDPOINT CON LÓGICA CONDICIONAL ---
@app.route('/enviar-recursos', methods=['POST'])
def enviar_recursos():
    # ... (El código de enviar_recursos se mantiene inalterado)
    try:
        data = request.json
        
        # Parámetros recibidos por nombre del modelo
        origen_name = data.get('origen', '').upper()
        destino_name = data.get('destino', '').upper()
        recursos_list = data.get('recursos')

        # 1. Validaciones
        if not origen_name or not destino_name or not recursos_list:
            return jsonify({"error": "Faltan parámetros requeridos (origen, destino, recursos)"}), 400
        
        # 1.1 Mapear Origen y Destino a Detalles de Cuenta
        if origen_name not in ACCOUNT_MAP or ACCOUNT_MAP[origen_name] is None:
             return jsonify({"error": f"Origen '{origen_name}' no es un modelo configurado o su clave es inválida."}), 400
        if destino_name not in ACCOUNT_MAP or ACCOUNT_MAP[destino_name] is None:
             return jsonify({"error": f"Destino '{destino_name}' no es un modelo configurado o su clave es inválida."}), 400
        
        # Validar que Origen y Destino no sean la misma cuenta
        if origen_name == destino_name:
             return jsonify({"error": "El origen y el destino no pueden ser la misma cuenta."}), 400

        sender_details = ACCOUNT_MAP[origen_name]
        receiver_details = ACCOUNT_MAP[destino_name]

        sender_address = sender_details["address"]
        sender_private_key = sender_details["private_key"]
        receiver_address = receiver_details["address"]
        
        if not recursos_list or not isinstance(recursos_list, list):
            return jsonify({"error": "El campo 'recursos' debe ser una lista no vacía."}), 400

        # 2. Procesar la lista de recursos (IDs y Cantidades)
        ids_to_send = []
        amounts_to_send = []
        
        for item in recursos_list:
            token_id = item.get('id')
            cantidad = item.get('cantidad')
            
            if not isinstance(token_id, int) or token_id <= 0:
                return jsonify({"error": f"ID de recurso inválido: {token_id}"}), 400
            if not isinstance(cantidad, int) or cantidad <= 0:
                return jsonify({"error": f"Cantidad inválida para ID {token_id}: {cantidad}"}), 400
            
            ids_to_send.append(token_id)
            amounts_to_send.append(cantidad)

        # 3. Determinar la OPERACIÓN
        is_owner_minting = sender_address == OWNER_ADDRESS

        if is_owner_minting:
            # --- OPERACIÓN: ACUÑACIÓN EN LOTE (MINT BATCH) ---
            print(f"🤖 Acuñación en lote ({len(ids_to_send)} tipos) a {destino_name} ({receiver_address})")
            
            function_call = contract.functions.mintBatch(
                receiver_address, # to
                ids_to_send,      # ids
                amounts_to_send,  # amounts
                b""               # data
            )
            
            address_to_use = OWNER_ADDRESS
            private_key_to_use = PRIVATE_KEY_OWNER
            action_type = "ACUÑACIÓN EN LOTE"
            
        else:
            # --- OPERACIÓN: TRANSFERENCIA EN LOTE (SAFE BATCH TRANSFER FROM) ---
            print(f"🤖 Transferencia en lote ({len(ids_to_send)} tipos) de {origen_name} a {destino_name}")

            function_call = contract.functions.safeBatchTransferFrom(
                sender_address,   # from
                receiver_address, # to
                ids_to_send,      # ids
                amounts_to_send,  # amounts
                b""               # data
            )
            
            address_to_use = sender_address
            private_key_to_use = sender_private_key
            action_type = "TRANSFERENCIA EN LOTE"


        # 4. Construir, Firmar y Enviar la Transacción
        # Aseguramos que la cuenta que firma la TX (from) tenga suficiente AVAX para gas
        tx = function_call.build_transaction({
            'from': address_to_use,
            'nonce': w3.eth.get_transaction_count(address_to_use),
            'gas': 500000 + (len(ids_to_send) * 50000), 
            'gasPrice': w3.to_wei('30', 'gwei'),
            'chainId': 43113
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key_to_use)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"🚀 Enviado! Hash: {tx_hash.hex()}")

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "status": "success",
            "tipo_accion": action_type,
            "mensaje": f"Se completó la operación de {action_type} con {len(ids_to_send)} tipos de recurso. Origen: {origen_name}, Destino: {destino_name}.",
            "hash": tx_hash.hex(),
            "bloque": tx_receipt.blockNumber,
            "explorer": f"https://testnet.snowtrace.io/tx/{tx_hash.hex()}"
        }), 200

    except Exception as e:
        print(f"❌ Error en la transacción: {e}")
        error_message = str(e)
        if "revert" in error_message.lower() or "transaction failed" in error_message.lower():
             error_message = "Transacción revertida por el contrato inteligente (ej: saldo insuficiente, o falta de permisos)."
        
        return jsonify({"status": "error", "mensaje": f"Error al procesar la transacción. Causa: {error_message}"}), 500
    
# ----------------------------------------------------
# --- FUNCIÓN CORREGIDA PARA CONSULTAR SALDOS ---
# ----------------------------------------------------
@app.route('/consultar-saldos', methods=['GET'])
def consultar_saldos():
    try:
        # Direcciones de las cuentas que queremos consultar (MODELO_A y MODELO_B)
        addresses_to_check = [
            ACCOUNT_MAP["MODELO_A"]["address"],
            ACCOUNT_MAP["MODELO_B"]["address"],
        ]
        
        # 1. Preparar la lista de cuentas y IDs para balanceOfBatch
        all_accounts = []
        for addr in addresses_to_check:
            all_accounts.extend([addr] * len(TODOS_LOS_IDS))

        all_ids = TODOS_LOS_IDS * len(addresses_to_check)
        
        # 2. Llamada a balanceOfBatch (lectura eficiente de la blockchain)
        balances_list = contract.functions.balanceOfBatch(
            all_accounts,
            all_ids
        ).call()

        # 3. Formatear la respuesta
        results = {}
        balance_index = 0
        
        # Iterar sobre las cuentas A y B para reestructurar la respuesta
        for account_name in ["MODELO_A", "MODELO_B"]:
            model_address = ACCOUNT_MAP[account_name]["address"]
            
            results[account_name] = {
                "address": model_address,
                "recursos": {}
            }
            
            # Asignar los saldos obtenidos a cada recurso
            for i in range(len(TODOS_LOS_IDS)):
                token_id = TODOS_LOS_IDS[i]
                balance = balances_list[balance_index]
                
                # --- CORRECCIÓN CLAVE ---
                # Usamos el nuevo diccionario ID_A_NOMBRE (ID a Nombre) en lugar de RECURSOS_IDS
                resource_name = ID_A_NOMBRE.get(token_id, f"ID_{token_id}")
                
                results[account_name]["recursos"][resource_name] = balance
                balance_index += 1
        
        # Retorna el resultado como JSON
        return jsonify({"status": "success", "saldos": results}), 200

    except Exception as e:
        print(f"❌ Error en la consulta de saldos: {e}")
        return jsonify({"status": "error", "mensaje": f"Error al consultar saldos. Causa: {str(e)}"}), 500

if __name__ == '__main__':
    # La API empieza a escuchar
    app.run(debug=True, port=5001)