import os
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware

# --- CONFIGURACIÓN ---
load_dotenv()
# Cuenta emisora de la TX: Modelo B (la que tiene los tokens)
PRIVATE_KEY_B = os.getenv("PRIVATE_KEY_MODELO_B") 
# Cuenta receptora de los tokens: Modelo A
PRIVATE_KEY_A = os.getenv("PRIVATE_KEY_ADMIN_L1") 
CONTRACT_ADDRESS = os.getenv("CATAN_ADDRESS") 
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"

# 1 es MADERA, según tu diccionario
TOKEN_ID = 1 
AMOUNT = 10 # Cantidad a devolver (ajusta a lo que enviaste)

# ABI Mínimo para transferir (safeTransferFrom)
ABI_MINIMAL = [{"constant": False, "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_id", "type": "uint256"}, {"name": "_amount", "type": "uint256"}, {"name": "_data", "type": "bytes"}], "name": "safeTransferFrom", "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"}]


def transfer_b_to_a():
    print("⚙️  Iniciando transferencia B -> A en Fuji...")
    
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Obtener direcciones a partir de las claves (Modelo B firma, Modelo A recibe)
    account_b = w3.eth.account.from_key(PRIVATE_KEY_B)
    account_a = w3.eth.account.from_key(PRIVATE_KEY_A)
    
    ADDRESS_MODELO_B = account_b.address
    ADDRESS_MODELO_A = account_a.address
    
    print(f"👤 Remitente (B): {ADDRESS_MODELO_B}")
    print(f"🎯 Destinatario (A): {ADDRESS_MODELO_A}")
    
    catan_contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI_MINIMAL)
    
    # 1. Preparar Transacción (safeTransferFrom)
    print(f"⏳ Creando TX: {AMOUNT} Maderas (ID {TOKEN_ID}) de B a A...")
    
    transfer_txn = catan_contract.functions.safeTransferFrom(
        ADDRESS_MODELO_B,  # _from: La dirección que posee los tokens (B)
        ADDRESS_MODELO_A,  # _to: La dirección que recibirá los tokens (A)
        TOKEN_ID,          
        AMOUNT,            
        b''                
    ).build_transaction({
        'from': ADDRESS_MODELO_B, # La cuenta que firma la TX (B)
        'nonce': w3.eth.get_transaction_count(ADDRESS_MODELO_B),
        'gas': 300000, 
        'gasPrice': w3.to_wei('30', 'gwei'),
        'chainId': 43113
    })
    
    # 2. Firmar y Enviar con la clave de Modelo B
    signed_txn = w3.eth.account.sign_transaction(transfer_txn, private_key=PRIVATE_KEY_B)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    print(f"🚀 Transacción enviada! Hash: {tx_hash.hex()}")
    print("⏳ Esperando confirmación...")
    
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print("\n" + "="*50)
    print(f"✅ TRANSFERENCIA EXITOSA (B -> A)")
    print(f"Token ID {TOKEN_ID} ({AMOUNT} unidades) devueltos.")
    print(f"🔗 Explorador: https://testnet.snowtrace.io/tx/{tx_hash.hex()}")
    print("="*50)

if __name__ == "__main__":
    transfer_b_to_a()