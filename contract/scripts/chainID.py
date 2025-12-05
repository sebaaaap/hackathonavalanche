import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
RPC_URL = os.getenv("RPC_URL") 
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if w3.is_connected():
    # ¡Aquí está la respuesta!
    numeric_id = w3.eth.chain_id
    print(f"✅ Conectado. El Chain ID NUMÉRICO es: {numeric_id}")
else:
    print("❌ No se pudo conectar. Verifica que tu L1 esté encendida.")