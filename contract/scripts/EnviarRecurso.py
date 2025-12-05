import os
import json
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware
from solcx import compile_source, install_solc

app = Flask(__name__)

# --- CONFIGURACIÓN ---
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY_ADMIN_L1")
CONTRACT_ADDRESS = os.getenv("CATAN_ADDRESS") # ¡Debe existir en tu .env!
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"

# Rutas para compilar y obtener el ABI
BASE_DIR = os.path.abspath(os.getcwd())
CONTRACT_PATH = os.path.join(BASE_DIR, '../', 'contracts', 'RecursosCatan.sol')
NODE_MODULES_PATH = os.path.join(BASE_DIR, '../', 'node_modules')

# Diccionario para traducir texto a IDs de Blockchain
RECURSOS_IDS = {
    "MADERA": 1,
    "ARCILLA": 2,
    "OVEJA": 3,
    "TRIGO": 4,
    "MINERAL": 5
}

# --- PREPARACIÓN (Se ejecuta al iniciar) ---
if not CONTRACT_ADDRESS:
    raise ValueError("❌ No tienes CATAN_ADDRESS en el .env. ¡Ejecuta el deploy primero!")

print("⚙️  Conectando a Avalanche...")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
account = w3.eth.account.from_key(PRIVATE_KEY)

print("⚙️  Cargando contrato (Compilando para obtener ABI)...")
install_solc('0.8.20')
with open(CONTRACT_PATH, 'r') as f:
    source = f.read()

compiled = compile_source(
    source,
    output_values=['abi'],
    solc_version='0.8.20',
    import_remappings={'@openzeppelin': NODE_MODULES_PATH + '/@openzeppelin'}
)
contract_interface = next((v for k, v in compiled.items() if ':RecursosCatan' in k))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_interface['abi'])

print(f"✅ Servidor listo. Controlando contrato en: {CONTRACT_ADDRESS}")

# --- EL ENDPOINT (LA LÓGICA) ---
@app.route('/enviar-recursos', methods=['POST'])
def enviar_recursos():
    try:
        # 1. Leer el JSON
        data = request.json
        destino = data.get('wallet_destino')
        nombre_recurso = data.get('recurso', '').upper()
        cantidad = data.get('cantidad')

        # 2. Validaciones
        if not destino or not Web3.is_address(destino):
            return jsonify({"error": "Dirección de wallet inválida"}), 400
        
        if nombre_recurso not in RECURSOS_IDS:
            return jsonify({"error": f"Recurso '{nombre_recurso}' no existe. Usa: {list(RECURSOS_IDS.keys())}"}), 400
        
        if not isinstance(cantidad, int) or cantidad <= 0:
            return jsonify({"error": "La cantidad debe ser un número positivo"}), 400

        id_recurso = RECURSOS_IDS[nombre_recurso]
        
        print(f"🤖 Solicitud: Enviar {cantidad} de {nombre_recurso} a {destino}...")

        # 3. Construir la Transacción (Llamada a 'mint')
        # Función: mint(address account, uint256 id, uint256 amount, bytes data)
        tx = contract.functions.mint(
            destino,
            id_recurso,
            cantidad,
            b"" # Data vacía
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': w3.to_wei('30', 'gwei'),
            'chainId': 43113
        })

        # 4. Firmar y Enviar
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"🚀 Enviado! Hash: {tx_hash.hex()}")

        # 5. Esperar confirmación (Opcional, hace la respuesta más lenta pero segura)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "status": "success",
            "mensaje": f"Se enviaron {cantidad} {nombre_recurso} exitosamente",
            "hash": tx_hash.hex(),
            "bloque": tx_receipt.blockNumber,
            "explorer": f"https://testnet.snowtrace.io/tx/{tx_hash.hex()}"
        }), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) # Usamos puerto 5001 para no chocar con el otro