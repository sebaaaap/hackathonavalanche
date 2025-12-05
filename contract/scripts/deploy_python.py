import os
import json
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware
from solcx import compile_source, install_solc, set_solc_version

# 1. Configuración
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY_ADMIN_L1")
RPC_URL = os.getenv("RPC_URL", "https://api.avax-test.network/ext/bc/C/rpc")

if not PRIVATE_KEY:
    raise ValueError("❌ Error: No se encontró PRIVATE_KEY_ADMIN_L1 en el archivo .env")

# --- Rutas Corregidas ---
# BASE_DIR es la carpeta 'scripts'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# CONTRACT_PATH debe buscar 'contracts' fuera de 'scripts'
CONTRACT_PATH = os.path.join(os.path.dirname(BASE_DIR), 'contracts', 'RecursosCatan.sol')
# NODE_MODULES_PATH debe buscar 'node_modules' en la raíz del proyecto (un nivel arriba de 'scripts')
NODE_MODULES_PATH = os.path.join(os.path.dirname(BASE_DIR), 'node_modules')
# --- Fin Rutas Corregidas ---

def deploy():
    print("⚙️  Conectando a Avalanche Fuji...")
    
    # Configuración Web3
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"👤 Desplegando con la cuenta: {account.address}")
    
    balance = w3.eth.get_balance(account.address)
    print(f"💰 Balance: {w3.from_wei(balance, 'ether')} AVAX")

    # 2. Compilar
    print("🔨 Compilando contrato...")
    
    # ⚠️ Usar set_solc_version si ya está instalado, o install_solc. 
    # Usaremos install_solc por seguridad, pero solo se ejecuta si no existe.
    install_solc('0.8.20')
    set_solc_version('0.8.20')
    
    with open(CONTRACT_PATH, 'r') as f:
        source = f.read()

    # Mapeo de rutas corregido para solcx: 
    # El compilador busca "@openzeppelin/" y lo sustituye por la ruta local
    remappings = {
        "@openzeppelin/": os.path.join(NODE_MODULES_PATH, '@openzeppelin') + "/"
    }
    
    # Mapeo usando la sintaxis de lista de tuplas para mayor compatibilidad con solcx
    remappings_list = [f"{k}={v}" for k, v in remappings.items()]
    
    # El compilador también necesita permiso para acceder a la carpeta node_modules
    allow_paths = [NODE_MODULES_PATH] 

    compiled = compile_source(
        source,
        output_values=['abi', 'bin'],
        solc_version='0.8.20',
        import_remappings=remappings_list,
        allow_paths=allow_paths, # Permite que solc acceda a las carpetas fuera del directorio actual
    )
    
    # Obtener la interfaz del contrato (ABI y Bytecode)
    # Buscamos el nombre del contrato, que es 'RecursosCatan'
    contract_id = next((k for k in compiled.keys() if k.endswith(':RecursosCatan')))
    contract_interface = compiled[contract_id]
    
    abi = contract_interface['abi']
    bytecode = contract_interface['bin']

    # 3. Desplegar
    print("⏳ Enviando transacción de despliegue...")
    RecursosCatan = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    chain_id = w3.eth.chain_id

    # Construir transacción
    # ⚠️ NOTA: El constructor de tu contrato (RecursosCatan) necesita un argumento: account.address
    tx = RecursosCatan.constructor(account.address).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 3000000,
        'gasPrice': w3.to_wei('30', 'gwei')
    })
    
    # Firmar y enviar
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    print(f"🚀 Transacción enviada! Hash: {tx_hash.hex()}")
    print("⏳ Esperando confirmación...")
    
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print("\n" + "="*50)
    print(f"✅ CONTRATO DESPLEGADO EXITOSAMENTE")
    print(f"📍 Dirección: {tx_receipt.contractAddress}")
    print("="*50)
    
    print("\n⚠️  IMPORTANTE: Guarda esta dirección en tu .env:")
    print(f"CATAN_ADDRESS={tx_receipt.contractAddress}")

if __name__ == "__main__":
    deploy()