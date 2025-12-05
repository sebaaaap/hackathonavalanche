"""
Cliente HTTP para enviar trades a la API FastAPI del BANCO.
Los modelos (Alice y Bob) usan esta función para comunicarse con blockchain.

Uso:
    from trade_client import enviar_trade
    
    resultado = enviar_trade(
        origen="MODELO_A",
        destino="BANCO",
        recursos=[
            {"id": 1, "cantidad": 5},   # 5 Maderas
            {"id": 3, "cantidad": 3}    # 3 Ovejas
        ]
    )
    
    if resultado["status"] == "success":
        print(f"✅ Trade exitoso: {resultado['hash_tx']}")
    else:
        print(f"❌ Error: {resultado['mensaje']}")
"""

import requests
import json
from typing import List, Dict

# URL de la API
API_URL = "http://127.0.0.1:8000"

# Diccionarios de mapeo
RECURSOS_NOMBRES = {
    1: "MADERA",
    2: "ARCILLA",
    3: "OVEJA",
    4: "TRIGO",
    5: "MINERAL"
}

RECURSOS_IDS = {v: k for k, v in RECURSOS_NOMBRES.items()}


def enviar_trade(
    origen: str,
    destino: str,
    recursos: List[Dict[str, int]],
    timeout: int = 30
) -> Dict:
    """
    Envía una solicitud de trade a la API del BANCO.
    
    Args:
        origen: "MODELO_A", "MODELO_B" o "BANCO"
        destino: "MODELO_A", "MODELO_B" o "BANCO"
        recursos: Lista de dicts con "id" y "cantidad"
                  ej: [{"id": 1, "cantidad": 5}]
        timeout: Timeout en segundos para la request
    
    Returns:
        Dict con:
            - status: "success" o "error"
            - mensaje: Descripción de lo que pasó
            - hash_tx: Hash de la transacción (si existe)
            - recursos: Los recursos que se enviaron
    """
    
    # Validar parámetros
    modelos_validos = ["MODELO_A", "MODELO_B", "BANCO"]
    
    if origen not in modelos_validos:
        return {
            "status": "error",
            "mensaje": f"Origen inválido: {origen}. Debe ser uno de {modelos_validos}"
        }
    
    if destino not in modelos_validos:
        return {
            "status": "error",
            "mensaje": f"Destino inválido: {destino}. Debe ser uno de {modelos_validos}"
        }
    
    if origen == destino:
        return {
            "status": "error",
            "mensaje": "Origen y destino no pueden ser iguales"
        }
    
    if not recursos or len(recursos) == 0:
        return {
            "status": "error",
            "mensaje": "Debe especificar al menos un recurso"
        }
    
    # Construir payload
    payload = {
        "origen": origen,
        "destino": destino,
        "recursos": recursos
    }
    
    # Log
    recursos_parts = []
    for r in recursos:
        nombre = RECURSOS_NOMBRES.get(r['id'], f"ID{r['id']}")
        recursos_parts.append(f"{nombre} x{r['cantidad']}")
    recursos_str = ", ".join(recursos_parts)
    print(f"📤 Enviando trade: {origen} → {destino} ({recursos_str})")
    
    try:
        # POST request a /trade
        response = requests.post(
            f"{API_URL}/trade",
            json=payload,
            timeout=timeout
        )
        
        # Parsear respuesta
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Trade exitoso: {data.get('hash_tx', 'N/A')}")
            return {
                "status": "success",
                "mensaje": data.get("mensaje", "Trade completado"),
                "hash_tx": data.get("hash_tx"),
                "recursos": data.get("recursos", recursos)
            }
        else:
            error = response.json().get("detail", "Error desconocido")
            print(f"❌ Error {response.status_code}: {error}")
            return {
                "status": "error",
                "mensaje": f"Error {response.status_code}: {error}"
            }
    
    except requests.exceptions.ConnectionError:
        msg = "❌ No se pudo conectar a la API. ¿Está levantada en http://127.0.0.1:8000?"
        print(msg)
        return {
            "status": "error",
            "mensaje": msg
        }
    
    except requests.exceptions.Timeout:
        msg = f"❌ Timeout: La API no respondió en {timeout}s"
        print(msg)
        return {
            "status": "error",
            "mensaje": msg
        }
    
    except Exception as e:
        msg = f"❌ Error inesperado: {str(e)}"
        print(msg)
        return {
            "status": "error",
            "mensaje": msg
        }


def obtener_balance(modelo: str, timeout: int = 30) -> Dict:
    """
    Obtiene el balance de un modelo desde la API.
    
    Args:
        modelo: "MODELO_A", "MODELO_B" o "BANCO"
        timeout: Timeout en segundos
    
    Returns:
        Dict con:
            - status: "success" o "error"
            - modelo: El modelo consultado
            - recursos: Dict con {nombre_recurso: cantidad}
    """
    
    modelos_validos = ["MODELO_A", "MODELO_B", "BANCO"]
    
    if modelo not in modelos_validos:
        return {
            "status": "error",
            "mensaje": f"Modelo inválido: {modelo}"
        }
    
    print(f"💰 Consultando balance de {modelo}...")
    
    try:
        response = requests.get(
            f"{API_URL}/balance/{modelo}",
            timeout=timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Balance obtenido")
            return {
                "status": "success",
                "modelo": modelo,
                "recursos": data.get("recursos", {})
            }
        else:
            error = response.json().get("detail", "Error desconocido")
            print(f"❌ Error {response.status_code}: {error}")
            return {
                "status": "error",
                "modelo": modelo,
                "mensaje": error
            }
    
    except requests.exceptions.ConnectionError:
        msg = "API no disponible"
        print(f"❌ {msg}")
        return {
            "status": "error",
            "modelo": modelo,
            "mensaje": msg
        }
    
    except Exception as e:
        msg = f"Error: {str(e)}"
        print(f"❌ {msg}")
        return {
            "status": "error",
            "modelo": modelo,
            "mensaje": msg
        }


def atacar_con_ladron(
    atacante: str,
    victima: str,
    recurso_id: int,
    timeout: int = 30
) -> Dict:
    """
    Ataca con el ladrón para robar 1 recurso de otro jugador.
    
    Args:
        atacante: Modelo que ataca (ej: "MODELO_A")
        victima: Modelo que pierde recurso (ej: "MODELO_B")
        recurso_id: ID del recurso a robar (1-5)
        timeout: Timeout en segundos
    
    Returns:
        Dict con status, mensaje y hash_tx
    
    Ejemplo:
        resultado = atacar_con_ladron(
            atacante="MODELO_A",
            victima="MODELO_B",
            recurso_id=1  # Robar 1 madera
        )
    """
    try:
        # Preparar payload
        payload = {
            "atacante": atacante,
            "victima": victima,
            "recurso_id": recurso_id
        }
        
        recurso_nombre = RECURSOS_NOMBRES.get(recurso_id, f"ID {recurso_id}")
        print(f"🎲 Atacando con ladrón: {atacante} → {victima} ({recurso_nombre})")
        
        # Enviar request
        response = requests.post(
            f"{API_URL}/robber/attack",
            json=payload,
            timeout=timeout
        )
        
        # Procesar respuesta
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ataque exitoso: {data.get('hash_tx', 'N/A')}")
            return data
        else:
            error = response.json().get("detail", "Error desconocido")
            print(f"❌ Error {response.status_code}: {error}")
            return {
                "status": "error",
                "atacante": atacante,
                "victima": victima,
                "mensaje": error
            }
    
    except requests.exceptions.ConnectionError:
        msg = "API no disponible"
        print(f"❌ {msg}")
        return {
            "status": "error",
            "atacante": atacante,
            "victima": victima,
            "mensaje": msg
        }
    
    except Exception as e:
        msg = f"Error: {str(e)}"
        print(f"❌ {msg}")
        return {
            "status": "error",
            "atacante": atacante,
            "victima": victima,
            "mensaje": msg
        }


# ============================================
# EJEMPLO DE USO
# ============================================
if __name__ == "__main__":
    print("🧪 TEST: Cliente de Trade")
    print("=" * 60)
    
    # Ejemplo 1: Enviar trade
    print("\n1️⃣ Enviando trade desde BANCO a MODELO_A...")
    resultado = enviar_trade(
        origen="BANCO",
        destino="MODELO_A",
        recursos=[
            {"id": 1, "cantidad": 10},  # 10 Maderas
            {"id": 4, "cantidad": 5}    # 5 Trigo
        ]
    )
    print(f"   Resultado: {resultado}")
    
    # Ejemplo 2: Obtener balance
    print("\n2️⃣ Consultando balance de MODELO_A...")
    balance = obtener_balance("MODELO_A")
    print(f"   Balance: {balance}")
    
    # Ejemplo 3: Transferencia entre modelos
    print("\n3️⃣ Transferencia MODELO_A → MODELO_B...")
    resultado = enviar_trade(
        origen="MODELO_A",
        destino="MODELO_B",
        recursos=[
            {"id": 1, "cantidad": 3}
        ]
    )
    print(f"   Resultado: {resultado}")
