#!/usr/bin/env python3
"""
Script para ver direcciones y balances de AVAX en Fuji Testnet
Ayuda a diagnosticar problemas de gas
"""

import os
from web3 import Web3
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Verificar conexión
if w3.is_connected():
    print("✅ Conectado a Avalanche Fuji Testnet\n")
else:
    print("❌ No se pudo conectar a Avalanche")
    exit(1)

# Obtener direcciones
def get_address_from_key(private_key):
    """Obtiene la dirección desde una clave privada"""
    if not private_key:
        return None
    try:
        account = w3.eth.account.from_key(private_key)
        return Web3.to_checksum_address(account.address)
    except:
        return None

# Claves privadas desde .env
PRIVATE_KEY_ADMIN = os.getenv("PRIVATE_KEY_ADMIN_L1")
PRIVATE_KEY_MODELO_A = os.getenv("PRIVATE_KEY_MODELO_A")
PRIVATE_KEY_MODELO_B = os.getenv("PRIVATE_KEY_MODELO_B")

# Obtener direcciones
BANCO_ADDRESS = get_address_from_key(PRIVATE_KEY_ADMIN)
MODELO_A_ADDRESS = get_address_from_key(PRIVATE_KEY_MODELO_A)
MODELO_B_ADDRESS = get_address_from_key(PRIVATE_KEY_MODELO_B)

print("=" * 70)
print("📍 DIRECCIONES Y BALANCES DE AVAX")
print("=" * 70)
print()

# Mostrar direcciones
print("🏦 BANCO (Admin):")
if BANCO_ADDRESS:
    print(f"   Dirección: {BANCO_ADDRESS}")
    balance_wei = w3.eth.get_balance(BANCO_ADDRESS)
    balance_avax = w3.from_wei(balance_wei, 'ether')
    print(f"   Balance: {balance_avax} AVAX")
    print(f"   Balance (wei): {balance_wei}")
else:
    print("   ❌ Clave privada no encontrada en .env")

print()

print("👤 MODELO_A (Alice):")
if MODELO_A_ADDRESS:
    print(f"   Dirección: {MODELO_A_ADDRESS}")
    balance_wei = w3.eth.get_balance(MODELO_A_ADDRESS)
    balance_avax = w3.from_wei(balance_wei, 'ether')
    print(f"   Balance: {balance_avax} AVAX")
    print(f"   Balance (wei): {balance_wei}")
else:
    print("   ❌ Clave privada no encontrada en .env")

print()

print("👤 MODELO_B (Bob):")
if MODELO_B_ADDRESS:
    print(f"   Dirección: {MODELO_B_ADDRESS}")
    balance_wei = w3.eth.get_balance(MODELO_B_ADDRESS)
    balance_avax = w3.from_wei(balance_wei, 'ether')
    print(f"   Balance: {balance_avax} AVAX")
    print(f"   Balance (wei): {balance_wei}")
else:
    print("   ❌ Clave privada no encontrada en .env")

print()
print("=" * 70)
print()

# Información útil
print("💡 PARA RECARGAR AVAX DE PRUEBA:")
print()
print("   Dirección BANCO:")
print(f"   {BANCO_ADDRESS}")
print()
print("   Dirección MODELO_A:")
print(f"   {MODELO_A_ADDRESS}")
print()
print("   Dirección MODELO_B:")
print(f"   {MODELO_B_ADDRESS}")
print()
print("   1. Ve a: https://faucet.avax.network/")
print("   2. Pega una de las direcciones arriba")
print("   3. Selecciona 'Avalanche C-Chain' y 'Testnet'")
print("   4. Solicita 2 AVAX (pueden tomar algunos minutos)")
print()
print("⚠️  IMPORTANTE:")
print("   - Carga AVAX en BANCO (PRIVATE_KEY_ADMIN_L1)")
print("   - Es quien pagará el gas de todas las transacciones")
print("   - Recomendado: 5-10 AVAX para pruebas")
print()
print("=" * 70)
