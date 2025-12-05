# 🤖 Integración Blockchain en Modelos Catan

Archivo cliente para conectar los modelos LLM (Alice, Bob) con la API FastAPI y blockchain.

---

## 📁 Archivos incluidos

| Archivo | Descripción |
|---------|-------------|
| `trade_client.py` | Cliente HTTP - Envía requests a la API |
| `ejemplo_integracion.py` | Ejemplos prácticos de cómo usar trade_client |
| `requirements_api.txt` | Dependencias adicionales (requests) |

---

## 🚀 Setup

### 1. Instalar requests

```bash
# Opción A: Instalar solo requests
pip install requests

# Opción B: Instalar con requirements
pip install -r requirements_api.txt
```

### 2. Verificar que la API esté levantada

```bash
# En otra terminal, desde /api:
cd api
uvicorn main:app --reload --port 8000
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 📚 API de trade_client

### Función: `enviar_trade()`

Envía recursos de un modelo a otro.

```python
from trade_client import enviar_trade

resultado = enviar_trade(
    origen="MODELO_A",
    destino="MODELO_B",
    recursos=[
        {"id": 1, "cantidad": 5},  # 5 Maderas
        {"id": 3, "cantidad": 2}   # 2 Ovejas
    ]
)

# Resultado:
# {
#     "status": "success",
#     "mensaje": "Trade ejecutado: MODELO_A → MODELO_B",
#     "hash_tx": "0x123abc...",
#     "recursos": [...]
# }
```

**Parámetros:**
- `origen` (str): "MODELO_A", "MODELO_B" o "BANCO"
- `destino` (str): "MODELO_A", "MODELO_B" o "BANCO"
- `recursos` (list): Array de dicts con "id" y "cantidad"
- `timeout` (int, optional): Timeout en segundos (default: 30)

**Returns:**
- Dict con "status", "mensaje", "hash_tx", "recursos"

---

### Función: `obtener_balance()`

Consulta el saldo de recursos de un modelo desde blockchain.

```python
from trade_client import obtener_balance

balance = obtener_balance("MODELO_A")

# Resultado:
# {
#     "status": "success",
#     "modelo": "MODELO_A",
#     "recursos": {
#         "MADERA": 45,
#         "ARCILLA": 12,
#         "OVEJA": 8,
#         "TRIGO": 20,
#         "MINERAL": 5
#     }
# }
```

**Parámetros:**
- `modelo` (str): "MODELO_A", "MODELO_B" o "BANCO"
- `timeout` (int, optional): Timeout en segundos (default: 30)

**Returns:**
- Dict con "status", "modelo", "recursos" o "mensaje" (en caso de error)

---

## 💡 Ejemplos

### Ejemplo 1: Enviar 10 maderas del BANCO a MODELO_A

```python
from trade_client import enviar_trade

resultado = enviar_trade(
    origen="BANCO",
    destino="MODELO_A",
    recursos=[{"id": 1, "cantidad": 10}]
)

if resultado["status"] == "success":
    print(f"✅ Hash: {resultado['hash_tx']}")
else:
    print(f"❌ Error: {resultado['mensaje']}")
```

### Ejemplo 2: Consultar balance de un modelo

```python
from trade_client import obtener_balance

balance = obtener_balance("MODELO_A")

if balance["status"] == "success":
    print("Balance de MODELO_A:")
    for recurso, cantidad in balance["recursos"].items():
        print(f"  {recurso}: {cantidad}")
```

### Ejemplo 3: Múltiples recursos

```python
from trade_client import enviar_trade

# MODELO_A envía a MODELO_B:
# - 3 Maderas
# - 2 Ovejas
# - 1 Mineral

resultado = enviar_trade(
    origen="MODELO_A",
    destino="MODELO_B",
    recursos=[
        {"id": 1, "cantidad": 3},   # Madera
        {"id": 3, "cantidad": 2},   # Oveja
        {"id": 5, "cantidad": 1}    # Mineral
    ]
)
```

### Ejemplo 4: Integración en clase Player

```python
from trade_client import enviar_trade, obtener_balance

class PlayerConBlockchain:
    def __init__(self, nombre, modelo_id):
        self.nombre = nombre
        self.modelo_id = modelo_id
        self.recursos = {}
    
    def enviar_a(self, otro_jugador, recurso_id, cantidad):
        """Envía recursos a otro jugador"""
        return enviar_trade(
            self.modelo_id,
            otro_jugador.modelo_id,
            [{"id": recurso_id, "cantidad": cantidad}]
        )
    
    def actualizar_balance(self):
        """Obtiene balance actual desde blockchain"""
        balance = obtener_balance(self.modelo_id)
        if balance["status"] == "success":
            self.recursos = balance["recursos"]
        return balance["status"] == "success"

# Uso:
alice = PlayerConBlockchain("Alice", "MODELO_A")
bob = PlayerConBlockchain("Bob", "MODELO_B")

alice.enviar_a(bob, 1, 5)  # Alice envía 5 maderas a Bob
alice.actualizar_balance()  # Sincroniza con blockchain
print(alice.recursos)
```

---

## 🔑 IDs de Recursos

| ID | Recurso | Descripción |
|----|---------|-------------|
| 1 | MADERA | Madera |
| 2 | ARCILLA | Arcilla/Barro |
| 3 | OVEJA | Ovejas/Lana |
| 4 | TRIGO | Trigo/Grano |
| 5 | MINERAL | Mineral/Piedra |

---

## ⚠️ Manejo de Errores

```python
from trade_client import enviar_trade

resultado = enviar_trade("MODELO_A", "MODELO_B", [{"id": 1, "cantidad": 5}])

# Verificar estado
if resultado["status"] == "success":
    print(f"✅ Transacción exitosa")
    print(f"Hash: {resultado['hash_tx']}")
else:
    print(f"❌ Error: {resultado['mensaje']}")
    # Posibles errores:
    # - "Origen y destino no pueden ser iguales"
    # - "Modelo inválido: ..."
    # - "Debe especificar al menos un recurso"
    # - "API no disponible"
    # - Otros errores de conexión
```

---

## 🧪 Testing

### Ejecutar ejemplos

```bash
# Desde models_venv
python ejemplo_integracion.py
```

Deberías ver:
```
============================================================
  EJEMPLOS DE INTEGRACIÓN BLOCKCHAIN
============================================================

[EJEMPLO 1] Transferencia simple
📤 Enviando trade: BANCO → MODELO_A (MADERA x20)
✅ Trade exitoso: 0x123abc...

💰 Balance de MODELO_A:
   MADERA: 20
   ...
```

---

## 🔗 Flujo Completo

```
┌──────────────────────────────┐
│  Mi código (modelo/jugador)  │
│                              │
│  from trade_client import... │
│  enviar_trade(...)           │
└──────────────┬───────────────┘
               │
               │ HTTP POST
               ▼
┌──────────────────────────────┐
│  FastAPI (/api/main.py)      │
│  - POST /trade               │
│  - GET /balance/{modelo}     │
└──────────────┬───────────────┘
               │
               │ subprocess
               ▼
┌──────────────────────────────┐
│  Scripts blockchain          │
│  - API.py (mint/transfer)    │
│  - get_balance.py            │
└──────────────┬───────────────┘
               │
               │ Web3
               ▼
┌──────────────────────────────┐
│  Avalanche Blockchain        │
│  - Contrato ERC-1155         │
└──────────────────────────────┘
```

---

## 📝 Casos de Uso

### 1. Comercio entre modelos en simulación

```python
# Durante la simulación de Catan
# Alice decide comerciar con Bob

from trade_client import enviar_trade

# Alice ofrece 2 maderas
resultado = enviar_trade(
    "MODELO_A",
    "MODELO_B",
    [{"id": 1, "cantidad": 2}]
)

if resultado["status"] == "success":
    # Bob acepta y envía ovejas
    enviar_trade(
        "MODELO_B",
        "MODELO_A",
        [{"id": 3, "cantidad": 1}]
    )
```

### 2. Verificar que los recursos están en blockchain

```python
# Verificar que el trade se completó
balance = obtener_balance("MODELO_A")
print(f"Balance actualizado: {balance['recursos']}")
```

### 3. Mint inicial del banco

```python
# Distribuir recursos iniciales a todos los modelos
from trade_client import enviar_trade

for modelo in ["MODELO_A", "MODELO_B"]:
    # Cada modelo obtiene recursos iniciales
    enviar_trade(
        "BANCO",
        modelo,
        [
            {"id": 1, "cantidad": 2},  # 2 Maderas
            {"id": 2, "cantidad": 1},  # 1 Arcilla
            {"id": 3, "cantidad": 2},  # 2 Ovejas
            {"id": 4, "cantidad": 1},  # 1 Trigo
            {"id": 5, "cantidad": 1}   # 1 Mineral
        ]
    )
```

---

## 🐛 Troubleshooting

### "No se pudo conectar a la API"

```python
# Error:
# ❌ No se pudo conectar a la API. ¿Está levantada en http://127.0.0.1:8000?
```

**Solución:**
1. Verifica que la API esté corriendo: `uvicorn main:app --reload`
2. Verifica que está en puerto 8000
3. Intenta acceder a `http://localhost:8000` en el navegador

### "Timeout"

```python
# Error:
# ❌ Timeout: La API no respondió en 30s
```

**Solución:**
1. El script blockchain está tardando mucho
2. Intenta aumentar el timeout: `enviar_trade(..., timeout=60)`
3. Verifica variables de entorno en `/contract/.env`

### "Modelo inválido"

```python
# Error:
# Modelo inválido: ALICE
```

**Solución:**
- Usa solo: `MODELO_A`, `MODELO_B`, `BANCO`

---

## 📚 Recursos

- FastAPI docs: `http://localhost:8000/docs`
- Swagger UI: `http://localhost:8000/swagger`
- Archivo API: `/api/main.py`
- Ejemplos: `ejemplo_integracion.py`

¡Listo! 🚀
