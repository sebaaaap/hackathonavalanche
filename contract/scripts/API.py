import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from web3 import Web3
from solcx import install_solc, set_solc_version, compile_source

# Importar middleware para redes PoA (Avalanche/BSC/Polygon)
try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
load_dotenv()

# --- CONSTANTES Y RUTAS ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Ajusta esta ruta si tu contrato está en otra carpeta
CONTRACT_PATH = os.path.join(os.path.dirname(BASE_DIR), 'contracts', 'RecursosCatan.sol')
NODE_MODULES_PATH = os.path.join(os.path.dirname(BASE_DIR), 'node_modules')
GAME_STATE_FILE = os.path.join(BASE_DIR, 'game_state.json')

CONTRACT_ADDRESS = os.getenv("CATAN_ADDRESS")
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"

RECURSOS_IDS = {"MADERA": 1, "ARCILLA": 2, "OVEJA": 3, "TRIGO": 4, "MINERAL": 5}
TODOS_LOS_IDS = list(RECURSOS_IDS.values())
ID_A_NOMBRE = {v: k for k, v in RECURSOS_IDS.items()}

# --- GESTIÓN DE CUENTAS ---
def get_account_details(private_key):
    if not private_key: return None
    try:
        w3_temp = Web3()
        account = w3_temp.eth.account.from_key(private_key)
        return {"private_key": private_key, "address": Web3.to_checksum_address(account.address)}
    except Exception:
        return None

ACCOUNT_MAP = {
    "BANCO": get_account_details(os.getenv("PRIVATE_KEY_ADMIN_L1")),
    "MODELO_A": get_account_details(os.getenv("PRIVATE_KEY_MODELO_A")),
    "MODELO_B": get_account_details(os.getenv("PRIVATE_KEY_MODELO_B")),
}

# Validar que existan las claves críticas
if not ACCOUNT_MAP["MODELO_A"] or not ACCOUNT_MAP["MODELO_B"]:
    raise ValueError("❌ Error: Faltan las claves privadas de MODELO_A o MODELO_B en el .env")

OWNER_DETAILS = ACCOUNT_MAP.get("BANCO")
OWNER_ADDRESS = OWNER_DETAILS["address"] if OWNER_DETAILS else None
PRIVATE_KEY_OWNER = OWNER_DETAILS["private_key"] if OWNER_DETAILS else None

# --- WEB3 Y CONTRATO ---
if not CONTRACT_ADDRESS:
    raise ValueError("❌ Error: Verifica CATAN_ADDRESS en el .env")

print("⚙️  Conectando a Avalanche C-Chain...")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Inyectar middleware
try:
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
except TypeError:
    w3.middleware_onion.inject(geth_poa_middleware(), layer=0)

print("⚙️  Compilando contrato (esto puede tardar un poco)...")
install_solc('0.8.20')
set_solc_version('0.8.20')

try:
    with open(CONTRACT_PATH, 'r') as f:
        source = f.read()
    
    compiled = compile_source(
        source,
        output_values=['abi'],
        solc_version='0.8.20',
        import_remappings=[f"@openzeppelin/={NODE_MODULES_PATH}/@openzeppelin/"],
        allow_paths=[NODE_MODULES_PATH]
    )
    contract_interface = next((v for k, v in compiled.items() if ':RecursosCatan' in k))
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_interface['abi'])
    print(f"✅ Contrato cargado exitosamente: {CONTRACT_ADDRESS}")
except Exception as e:
    print(f"❌ Error compilando contrato: {e}")
    # Aquí podrías cargar un ABI.json precompilado como fallback
    raise e

# --- SISTEMA DE NONCE (SOLUCIÓN A RACE CONDITIONS) ---
# Diccionario en memoria para rastrear el último nonce usado por cada dirección
NONCE_TRACKER = {}

def get_next_nonce(address):
    """
    Calcula el nonce correcto, considerando transacciones pendientes
    que aún no han sido minadas pero que ya enviamos.
    """
    # 1. Obtenemos el nonce oficial de la red (transacciones confirmadas)
    chain_nonce = w3.eth.get_transaction_count(address, 'pending')
    
    # 2. Obtenemos el último nonce que nosotros registramos localmente
    local_nonce = NONCE_TRACKER.get(address, -1)
    
    # 3. Determinamos cuál usar:
    # Si nuestro local es mayor o igual al de la cadena, significa que tenemos TXs en vuelo.
    # Incrementamos el local.
    if local_nonce >= chain_nonce:
        next_nonce = local_nonce + 1
    else:
        # Si la cadena dice algo mayor (o igual) y no tenemos nada pendiente, usamos el de la cadena.
        next_nonce = chain_nonce
        
    # 4. Actualizamos el tracker
    NONCE_TRACKER[address] = next_nonce
    return next_nonce

# --- SISTEMA DE PERSISTENCIA (JSON) ---
def load_game_history():
    if not os.path.exists(GAME_STATE_FILE):
        return []
    try:
        with open(GAME_STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_game_turn(turn_data):
    history = load_game_history()
    history.append(turn_data)
    # Guardamos solo los últimos 100 turnos para no llenar el disco infinitamente
    if len(history) > 100:
        history = history[-100:]
    
    with open(GAME_STATE_FILE, 'w') as f:
        json.dump(history, f, indent=4)
    return history

# ================= RUTAS =================

@app.route('/enviar-recursos', methods=['POST'])
def enviar_recursos():
    try:
        data = request.json
        origen_name = data.get('origen', '').upper()
        destino_name = data.get('destino', '').upper()
        recursos_list = data.get('recursos')

        # 1. Validaciones Básicas
        if not origen_name or not destino_name or not recursos_list:
            return jsonify({"error": "Faltan parámetros: origen, destino, recursos"}), 400
        
        if origen_name == destino_name:
            return jsonify({"error": "Origen y destino no pueden ser iguales"}), 400

        sender_details = ACCOUNT_MAP.get(origen_name)
        receiver_details = ACCOUNT_MAP.get(destino_name)

        if not sender_details:
            return jsonify({"error": f"Origen '{origen_name}' no configurado o sin clave"}), 400
        if not receiver_details:
            return jsonify({"error": f"Destino '{destino_name}' no configurado"}), 400

        # 2. Preparar Datos
        sender_addr = sender_details["address"]
        sender_pk = sender_details["private_key"]
        receiver_addr = receiver_details["address"]
        
        ids_to_send = []
        amounts_to_send = []
        
        for item in recursos_list:
            ids_to_send.append(int(item.get('id')))
            amounts_to_send.append(int(item.get('cantidad')))

        # 3. Construir Transacción
        is_owner_minting = (sender_addr == OWNER_ADDRESS)
        
        if is_owner_minting:
            print(f"🤖 Minting de {origen_name} -> {destino_name}")
            fn_call = contract.functions.mintBatch(receiver_addr, ids_to_send, amounts_to_send, b"")
            action_type = "MINT"
        else:
            print(f"🤖 Transferencia de {origen_name} -> {destino_name}")
            fn_call = contract.functions.safeBatchTransferFrom(sender_addr, receiver_addr, ids_to_send, amounts_to_send, b"")
            action_type = "TRANSFER"

        # 4. Obtener Nonce Seguro (FIX CRÍTICO)
        nonce = get_next_nonce(sender_addr)
        
        # 5. Estimar Gas y Construir
        gas_estimate = fn_call.estimate_gas({'from': sender_addr})
        
        tx_build = fn_call.build_transaction({
            'from': sender_addr,
            'nonce': nonce,
            'gas': int(gas_estimate * 1.2), # Buffer del 20%
            'gasPrice': w3.to_wei('30', 'gwei'),
            'chainId': 43113
        })

        # 6. Firmar y Enviar
        signed_tx = w3.eth.account.sign_transaction(tx_build, private_key=sender_pk)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"🚀 TX Enviada: {tx_hash.hex()} (Nonce: {nonce})")
        
        # Esperar confirmación (Opcional: Si quieres que la UI espere, descomenta esto)
        # tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "status": "success",
            "tipo_accion": action_type,
            "hash": tx_hash.hex(),
            "explorer": f"https://testnet.snowtrace.io/tx/{tx_hash.hex()}"
        }), 200

    except Exception as e:
        print(f"❌ Error en transacción: {e}")
        # Si falla, intentamos "liberar" el nonce local reduciéndolo (opcional, pero ayuda a recuperar)
        # En este caso simple, dejaremos que el next_nonce se corrija solo con get_transaction_count
        return jsonify({"status": "error", "mensaje": str(e)}), 500

@app.route('/consultar-saldos', methods=['GET'])
def consultar_saldos():
    try:
        # Consultamos saldos solo de los modelos A y B
        accounts_names = ["MODELO_A", "MODELO_B"]
        addresses = [ACCOUNT_MAP[name]["address"] for name in accounts_names]
        
        # Crear arrays gigantes para una sola llamada RPC (Batch)
        batch_addrs = []
        batch_ids = []
        
        for addr in addresses:
            batch_addrs.extend([addr] * len(TODOS_LOS_IDS))
            batch_ids.extend(TODOS_LOS_IDS)
            
        # Llamada única a la blockchain
        balances = contract.functions.balanceOfBatch(batch_addrs, batch_ids).call()
        
        # Formatear respuesta
        response = {}
        idx = 0
        for name in accounts_names:
            response[name] = {"recursos": {}}
            for token_id in TODOS_LOS_IDS:
                r_name = ID_A_NOMBRE.get(token_id, f"ID_{token_id}")
                response[name]["recursos"][r_name] = balances[idx]
                idx += 1
                
        return jsonify({"status": "success", "saldos": response}), 200

    except Exception as e:
        print(f"❌ Error consultando saldos: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500

@app.route('/game-state', methods=['POST'])
def receive_game_state():
    """Recibe y guarda el estado del juego en archivo JSON."""
    try:
        data = request.json
        if not data: return jsonify({"error": "Sin datos"}), 400
        
        # Guardar en archivo
        save_game_turn(data)
        
        print(f"💾 Estado guardado: Turno {data.get('turno')}")
        return jsonify({"status": "success", "mensaje": "Estado guardado"}), 200
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500

@app.route('/game-state', methods=['GET'])
def get_game_state():
    """Lee el estado del juego desde el archivo JSON."""
    try:
        history = load_game_history()
        ultimo = request.args.get('ultimo', 'false').lower() == 'true'
        
        if not history:
            return jsonify({"status": "success", "mensaje": "Sin historial", "turnos": []}), 200
            
        if ultimo:
            return jsonify({"status": "success", "turno_actual": history[-1]}), 200
        else:
            return jsonify({"status": "success", "turnos": history}), 200
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500

# --- INICIO ---
if __name__ == '__main__':
    # Usar threaded=True ayuda a manejar peticiones concurrentes en desarrollo
    app.run(debug=True, port=5001, threaded=True)