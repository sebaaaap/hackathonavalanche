#!/usr/bin/env python3
"""
Script para transferir AVAX entre wallets en Fuji Testnet
Uso: python transfer_avax.py <cantidad_en_avax> <desde_wallet> <hacia_wallet>
Ejemplo: python transfer_avax.py 2.0 MODELO_A BANCO
"""

import sys
import os
from web3 import Web3
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"
CHAIN_ID = 43113  # Fuji Testnet

try:
    from web3.middleware import ExtraDataToPOAMiddleware
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware(), layer=0)
except ImportError:
    from web3.middleware import geth_poa_middleware
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Mapeo de wallets
WALLETS = {
    "BANCO": os.getenv("PRIVATE_KEY_ADMIN_L1"),
    "MODELO_A": os.getenv("PRIVATE_KEY_MODELO_A"),
    "MODELO_B": os.getenv("PRIVATE_KEY_MODELO_B"),
}

def get_address_from_key(private_key):
    """Obtiene dirección desde clave privada"""
    if not private_key:
        return None
    try:
        account = w3.eth.account.from_key(private_key)
        return Web3.to_checksum_address(account.address)
    except:
        return None

def transfer_avax(cantidad_avax, de_wallet, hacia_wallet):
    """
    Transfiere AVAX de una wallet a otra
    """
    # Validar wallets
    if de_wallet not in WALLETS:
        print(f"❌ Wallet '{de_wallet}' no reconocida. Opciones: {list(WALLETS.keys())}")
        return False
    
    if hacia_wallet not in WALLETS:
        print(f"❌ Wallet '{hacia_wallet}' no reconocida. Opciones: {list(WALLETS.keys())}")
        return False
    
    # Obtener direcciones
    private_key_from = WALLETS[de_wallet]
    address_to = get_address_from_key(WALLETS[hacia_wallet])
    
    if not private_key_from or not address_to:
        print("❌ No se pudieron obtener las direcciones")
        return False
    
    account_from = w3.eth.account.from_key(private_key_from)
    address_from = Web3.to_checksum_address(account_from.address)
    
    print(f"\n💸 TRANSFERENCIA DE AVAX")
    print(f"   De: {de_wallet} ({address_from})")
    print(f"   Para: {hacia_wallet} ({address_to})")
    print(f"   Cantidad: {cantidad_avax} AVAX")
    print()
    
    # Verificar balance
    balance_wei = w3.eth.get_balance(address_from)
    balance_avax = w3.from_wei(balance_wei, 'ether')
    
    print(f"   Balance actual de {de_wallet}: {balance_avax} AVAX")
    
    if float(balance_avax) < float(cantidad_avax):
        print(f"   ❌ Saldo insuficiente. Necesitas {cantidad_avax} AVAX pero tienes {balance_avax}")
        return False
    
    # Preparar transacción
    try:
        amount_wei = w3.to_wei(cantidad_avax, 'ether')
        nonce = w3.eth.get_transaction_count(address_from)
        
        # Estimar gas
        gas_estimate = w3.eth.estimate_gas({
            'from': address_from,
            'to': address_to,
            'value': amount_wei
        })
        
        gas_price = w3.eth.gas_price
        
        print(f"\n   Gas estimado: {gas_estimate}")
        print(f"   Gas price: {w3.from_wei(gas_price, 'gwei')} Gwei")
        print(f"   Costo total de gas: {w3.from_wei(gas_estimate * gas_price, 'ether')} AVAX")
        
        # Construir transacción
        tx = {
            'from': address_from,
            'to': address_to,
            'value': amount_wei,
            'nonce': nonce,
            'gas': gas_estimate,
            'gasPrice': gas_price,
            'chainId': CHAIN_ID
        }
        
        # Firmar
        print("\n   Firmando transacción...")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key_from)
        
        # Enviar
        print("   Enviando transacción...")
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash_hex = tx_hash.hex()
        
        print(f"\n✅ Transacción enviada!")
        print(f"   Hash: {tx_hash_hex}")
        print()
        print(f"   Ver en explorador:")
        print(f"   https://testnet.snowtrace.io/tx/{tx_hash_hex}")
        print()
        
        # Esperar confirmación
        print("   Esperando confirmación...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        
        if receipt['status'] == 1:
            print(f"\n✅ Transacción confirmada!")
            print(f"   {cantidad_avax} AVAX transferidos correctamente")
            return True
        else:
            print(f"\n❌ Transacción fallida")
            return False
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python transfer_avax.py <cantidad_avax> <desde_wallet> <hacia_wallet>")
        print()
        print("Ejemplo:")
        print("  python transfer_avax.py 2.0 MODELO_A BANCO")
        print()
        print("Wallets disponibles:")
        print("  - BANCO")
        print("  - MODELO_A")
        print("  - MODELO_B")
        sys.exit(1)
    
    cantidad = float(sys.argv[1])
    de = sys.argv[2]
    hacia = sys.argv[3]
    
    transfer_avax(cantidad, de, hacia)
