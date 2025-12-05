import os
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

# --- CONFIGURACIÓN ---
load_dotenv()
# Se usan las claves solo para obtener las direcciones, no se firma ninguna TX.
PRIVATE_KEY_A = os.getenv("PRIVATE_KEY_MODELO_A")
PRIVATE_KEY_B = os.getenv("PRIVATE_KEY_MODELO_B")
CONTRACT_ADDRESS = os.getenv("CATAN_ADDRESS")
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"

# Diccionario de recursos (IDs y Nombres)
RECURSOS_IDS = {
    1: "MADERA",
    2: "ARCILLA",
    3: "OVEJA",
    4: "TRIGO",
    5: "MINERAL"
}

# ABI Mínimo para consultar (solo necesitamos balanceOf)
ABI_MINIMAL_BALANCE = [{"constant": True, "inputs": [{"name": "account", "type": "address"}, {"name": "id", "type": "uint256"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"}]


def get_addresses(w3):
    """Función auxiliar para obtener las direcciones a consultar."""
    try:
        # Nota: Asumiendo que PRIVATE_KEY_A y PRIVATE_KEY_B ya están definidos y son claves de usuario.
        ADDRESS_MODELO_A = Web3.to_checksum_address(w3.eth.account.from_key(PRIVATE_KEY_A).address)
        ADDRESS_MODELO_B = Web3.to_checksum_address(w3.eth.account.from_key(PRIVATE_KEY_B).address)
        return ADDRESS_MODELO_A, ADDRESS_MODELO_B
    except ValueError as e:
        print(f"❌ Error al obtener direcciones: Verifica que las claves privadas en tu .env estén correctas. {e}")
        exit()


def check_all_balances():
    """Consulta el saldo de todos los recursos para las cuentas Modelo A y Modelo B."""
    print("⚙️  Conectando a Fuji para consulta de saldos...")
    
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    ADDRESS_A, ADDRESS_B = get_addresses(w3)
    
    # Inicialización del contrato con el ABI mínimo
    catan_contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI_MINIMAL_BALANCE)
    
    print("-" * 60)
    print(f"📊 SALDOS ACTUALES DE RECURSOS EN EL CONTRATO ({CONTRACT_ADDRESS[-6:]}...)")
    print("-" * 60)

    # Creamos una lista de tuplas (Nombre, ID)
    recursos_consulta = [(name, id) for id, name in RECURSOS_IDS.items()]

    # Estructura de salida
    results = {
        "MODELO_A": {"address": ADDRESS_A},
        "MODELO_B": {"address": ADDRESS_B}
    }

    # Iterar sobre cada recurso para consultar el saldo
    for name, id in recursos_consulta:
        try:
            # Consulta para la Cuenta Modelo A
            balance_a = catan_contract.functions.balanceOf(
                ADDRESS_A, 
                id
            ).call()
            results["MODELO_A"][name] = balance_a

            # Consulta para la Cuenta Modelo B
            balance_b = catan_contract.functions.balanceOf(
                ADDRESS_B, 
                id
            ).call()
            results["MODELO_B"][name] = balance_b

        except Exception as e:
            print(f"⚠️ Error al consultar {name} (ID: {id}): {e}")
            results["MODELO_A"][name] = "ERROR"
            results["MODELO_B"][name] = "ERROR"
    
    # --- Impresión de Resultados ---
    
    print(f"👤 Modelo A (Address: {ADDRESS_A[-10:]}...)")
    for name, balance in results["MODELO_A"].items():
        if name != "address":
            print(f"  - {name:<10}: {balance}")
    
    print("-" * 60)
    
    print(f"👤 Modelo B (Address: {ADDRESS_B[-10:]}...)")
    for name, balance in results["MODELO_B"].items():
        if name != "address":
            print(f"  - {name:<10}: {balance}")
            
    print("-" * 60)
    
    return results

if __name__ == "__main__":
    check_all_balances()