import os
from eth_account import Account

# Habilitar funciones para derivar cuentas desde frases semilla
Account.enable_unaudited_hdwallet_features()

def generar_identidades():
    # 1. Crear una frase semilla maestra nueva
    acct, mnemonic = Account.create_with_mnemonic()
    
    print("="*60)
    print("🔐  FRASE SEMILLA MAESTRA (¡GUÁRDALA SOLO TÚ!):")
    print(f"    {mnemonic}")
    print("="*60)
    print("\nGenerando wallets para tus Modelos en Avalanche...\n")

    # Estructura para guardar en .env
    env_content = f"# CONFIGURACION AVALANCHE FUJI\nMNEMONIC='{mnemonic}'\n\n"

    # 2. Derivar 4 cuentas (Ruta estándar de derivación)
    nombres = ["MODELO_A", "MODELO_B"]
    
    for i, nombre in enumerate(nombres):
        # La ruta de derivación estándar cambia el último número para crear cuentas distintas
        # m/44'/60'/0'/0/0 -> Cuenta 1
        # m/44'/60'/0'/0/1 -> Cuenta 2, etc.
        path = f"m/44'/60'/0'/0/{i}"
        account = Account.from_mnemonic(mnemonic, account_path=path)
        
        print(f"🤖 {nombre}:")
        print(f"   Dirección (Address): {account.address}")
        print(f"   Ruta Derivación:     {path}")
        print("-" * 30)

        # Agregar al contenido del archivo .env
        env_content += f"ADDRESS_{nombre}={account.address}\n"
        env_content += f"PRIVATE_KEY_{nombre}={account.key.hex()}\n"

    # 3. Guardar en archivo .env
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("\n✅ Archivo .env generado exitosamente con las llaves privadas.")
    print("   Tus agentes ya tienen bolsillos, pero están vacíos.")

if __name__ == "__main__":
    generar_identidades()