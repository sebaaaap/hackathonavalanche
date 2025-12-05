"""
EJEMPLO: Cómo integrar trade_client en la simulación de Catan

Este archivo muestra ejemplos prácticos de cómo hacer que Alice y Bob
usen la API para comerciar recursos con blockchain.
"""

# ============================================
# OPCIÓN 1: Integración simple en simulación
# ============================================

from trade_client import enviar_trade, obtener_balance


def comerciar_recurso(modelo_origen: str, modelo_destino: str, recurso_id: int, cantidad: int):
    """
    Función auxiliar para comerciar un recurso entre modelos.
    
    Uso en simulación:
        comerciar_recurso("MODELO_A", "MODELO_B", 1, 5)  # 5 maderas de A a B
    """
    print(f"\n🤝 {modelo_origen} quiere enviar {cantidad} recursos (ID {recurso_id}) a {modelo_destino}")
    
    resultado = enviar_trade(
        origen=modelo_origen,
        destino=modelo_destino,
        recursos=[{"id": recurso_id, "cantidad": cantidad}]
    )
    
    if resultado["status"] == "success":
        print(f"✅ Transacción exitosa: {resultado['hash_tx']}")
        return True
    else:
        print(f"❌ Transacción fallida: {resultado['mensaje']}")
        return False


def mostrar_balance_modelo(modelo: str):
    """Muestra el balance de recursos de un modelo"""
    print(f"\n💰 Balance de {modelo}:")
    
    balance = obtener_balance(modelo)
    
    if balance["status"] == "success":
        for recurso, cantidad in balance["recursos"].items():
            print(f"   {recurso}: {cantidad}")
    else:
        print(f"   ❌ Error: {balance['mensaje']}")


# ============================================
# OPCIÓN 2: Integración con clase Player
# ============================================

class PlayerConBlockchain:
    """Extensión del Player para usar blockchain"""
    
    def __init__(self, nombre: str, modelo_id: str):
        self.nombre = nombre
        self.modelo_id = modelo_id  # "MODELO_A", "MODELO_B"
        self.recursos = {}
    
    def enviar_recurso_a(self, otro_jugador: 'PlayerConBlockchain', recurso_id: int, cantidad: int):
        """
        Envía un recurso a otro jugador usando blockchain.
        
        Ejemplo:
            alice.enviar_recurso_a(bob, 1, 5)  # Alice envía 5 maderas a Bob
        """
        print(f"\n🤝 {self.nombre} ({self.modelo_id}) envía a {otro_jugador.nombre}")
        
        resultado = enviar_trade(
            origen=self.modelo_id,
            destino=otro_jugador.modelo_id,
            recursos=[{"id": recurso_id, "cantidad": cantidad}]
        )
        
        return resultado["status"] == "success"
    
    def sincronizar_balance(self):
        """Obtiene el balance actual desde blockchain"""
        balance = obtener_balance(self.modelo_id)
        
        if balance["status"] == "success":
            self.recursos = balance["recursos"]
            print(f"✅ {self.nombre} balance actualizado desde blockchain")
            return True
        else:
            print(f"❌ Error actualizando balance: {balance['mensaje']}")
            return False
    
    def mostrar_balance(self):
        """Imprime el balance actual"""
        self.sincronizar_balance()
        print(f"\n📊 Recursos de {self.nombre}:")
        for recurso, cantidad in self.recursos.items():
            print(f"   {recurso}: {cantidad}")


# ============================================
# OPCIÓN 3: Trade entre modelos (multi-recurso)
# ============================================

def negociar_multiples_recursos(
    modelo_a: str,
    modelo_b: str,
    recursos_a: list,  # Lo que A envía a B
    recursos_b: list   # Lo que B envía a A
):
    """
    Simula una negociación donde ambos modelos intercambian recursos.
    
    Uso:
        negociar_multiples_recursos(
            "MODELO_A",
            "MODELO_B",
            recursos_a=[{"id": 1, "cantidad": 5}],      # A da 5 maderas
            recursos_b=[{"id": 4, "cantidad": 3}]       # B da 3 trigos
        )
    """
    print(f"\n📋 Negociación: {modelo_a} ↔ {modelo_b}")
    print(f"   {modelo_a} da: {recursos_a}")
    print(f"   {modelo_b} da: {recursos_b}")
    
    # Transacción 1: A → B
    print(f"\n   → Ejecutando transferencia {modelo_a} → {modelo_b}...")
    tx1 = enviar_trade(modelo_a, modelo_b, recursos_a)
    
    if tx1["status"] != "success":
        print(f"   ❌ Transacción 1 falló, cancelando...")
        return False
    
    # Transacción 2: B → A
    print(f"\n   → Ejecutando transferencia {modelo_b} → {modelo_a}...")
    tx2 = enviar_trade(modelo_b, modelo_a, recursos_b)
    
    if tx2["status"] != "success":
        print(f"   ❌ Transacción 2 falló, pero transacción 1 ya se ejecutó!")
        return False
    
    print(f"\n✅ Negociación completada exitosamente")
    return True


# ============================================
# EJEMPLO DE USO COMPLETO
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("  EJEMPLOS DE INTEGRACIÓN BLOCKCHAIN")
    print("=" * 60)
    
    # Ejemplo 1: Función simple
    print("\n[EJEMPLO 1] Transferencia simple")
    comerciar_recurso("BANCO", "MODELO_A", 1, 20)
    mostrar_balance_modelo("MODELO_A")
    
    # Ejemplo 2: Usar clases
    print("\n" + "=" * 60)
    print("[EJEMPLO 2] Usando clases PlayerConBlockchain")
    
    alice = PlayerConBlockchain("Alice", "MODELO_A")
    bob = PlayerConBlockchain("Bob", "MODELO_B")
    
    # Alice sincroniza balance
    alice.sincronizar_balance()
    alice.mostrar_balance()
    
    # Alice envía a Bob
    alice.enviar_recurso_a(bob, 1, 3)
    
    # Bob sincroniza y muestra
    bob.sincronizar_balance()
    bob.mostrar_balance()
    
    # Ejemplo 3: Negociación
    print("\n" + "=" * 60)
    print("[EJEMPLO 3] Negociación multi-recurso")
    
    negociar_multiples_recursos(
        "MODELO_A",
        "MODELO_B",
        recursos_a=[{"id": 1, "cantidad": 2}],      # A da 2 maderas
        recursos_b=[{"id": 3, "cantidad": 1}]       # B da 1 oveja
    )
    
    print("\n" + "=" * 60)
    print("✅ Todos los ejemplos completados")
    print("=" * 60)
