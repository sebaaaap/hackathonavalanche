# 🏦 Catan Blockchain API - Documentación

## 📋 Resumen

API FastAPI que actúa como **BANCO** y puente entre los modelos LLM (Simulación Catan) y los contratos ERC-1155 en Avalanche.

**Flujo completo:**
```
MODELO → API (FastAPI) → Scripts Python → Web3 → Contrato Blockchain → Avalanche
```

---

## 🚀 Instalación Rápida

### 1. Instalar dependencias

```bash
# Navega a la carpeta /api
cd api

# Crear entorno virtual (opcional pero recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows PowerShell:
.\venv\Scripts\Activate.ps1
# En CMD:
venv\Scripts\activate.bat
# En Linux/Mac:
source venv/bin/activate

# Instalar paquetes
pip install -r requirements.txt
```

### 2. Levantar la API

```bash
# Desde la carpeta /api
uvicorn main:app --reload --port 8000
```

Deberías ver algo como:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ La API está **activa** en: `http://localhost:8000`

---

## 📡 Endpoints

### 1. Health Check
```
GET http://localhost:8000/
```

**Response:**
```json
{
  "status": "✅ API Catan Blockchain activa",
  "version": "1.0",
  "endpoints": {
    "POST /trade": "Enviar recursos",
    "GET /balance/{modelo}": "Consultar saldo"
  }
}
```

---

### 2. POST /trade - Enviar Recursos

**Endpoint:** `POST http://localhost:8000/trade`

**Body (JSON):**
```json
{
  "origen": "BANCO",
  "destino": "MODELO_A",
  "recursos": [
    {"id": 1, "cantidad": 10},
    {"id": 3, "cantidad": 5}
  ]
}
```

**Parámetros:**
- `origen`: `"BANCO"` | `"MODELO_A"` | `"MODELO_B"`
- `destino`: `"BANCO"` | `"MODELO_A"` | `"MODELO_B"`
- `recursos`: Array de objetos con:
  - `id`: ID del recurso (1-5)
  - `cantidad`: Cantidad a transferir

**IDs de Recursos:**
```
1 = MADERA
2 = ARCILLA
3 = OVEJA
4 = TRIGO
5 = MINERAL
```

**Response (200 OK):**
```json
{
  "status": "success",
  "mensaje": "Trade ejecutado: BANCO → MODELO_A",
  "hash_tx": "0x123abc...",
  "origen": "BANCO",
  "destino": "MODELO_A",
  "recursos": [
    {"id": 1, "cantidad": 10},
    {"id": 3, "cantidad": 5}
  ]
}
```

**Errores:**
```json
{
  "detail": "Modelo inválido: INVALID_MODELO"
}
```

---

### 3. GET /balance/{modelo} - Consultar Saldo

**Endpoint:** `GET http://localhost:8000/balance/MODELO_A`

**Response:**
```json
{
  "modelo": "MODELO_A",
  "recursos": {
    "MADERA": 45,
    "ARCILLA": 12,
    "OVEJA": 8,
    "TRIGO": 20,
    "MINERAL": 5
  }
}
```

---

## 🤖 Integración desde los Modelos

### Instalar requests en el entorno de modelos

```bash
# En la carpeta /models_venv
pip install requests
```

### Usar en los modelos (Alice, Bob, etc)

```python
from trade_client import enviar_trade, obtener_balance

# Enviar trade: MODELO_A da 5 maderas a MODELO_B
resultado = enviar_trade(
    origen="MODELO_A",
    destino="MODELO_B",
    recursos=[
        {"id": 1, "cantidad": 5}
    ]
)

if resultado["status"] == "success":
    print(f"✅ Trade exitoso")
    print(f"Hash TX: {resultado['hash_tx']}")
else:
    print(f"❌ Error: {resultado['mensaje']}")

# Consultar balance
balance = obtener_balance("MODELO_A")
if balance["status"] == "success":
    print(f"Balance de MODELO_A:")
    for recurso, cantidad in balance["recursos"].items():
        print(f"  {recurso}: {cantidad}")
```

---

## 📝 Ejemplos con cURL

### Ejemplo 1: Banco minting recursos a MODELO_A

```bash
curl -X POST http://localhost:8000/trade \
  -H "Content-Type: application/json" \
  -d '{
    "origen": "BANCO",
    "destino": "MODELO_A",
    "recursos": [
      {"id": 1, "cantidad": 20},
      {"id": 4, "cantidad": 10}
    ]
  }'
```

### Ejemplo 2: Transferencia entre modelos

```bash
curl -X POST http://localhost:8000/trade \
  -H "Content-Type: application/json" \
  -d '{
    "origen": "MODELO_A",
    "destino": "MODELO_B",
    "recursos": [
      {"id": 1, "cantidad": 3}
    ]
  }'
```

### Ejemplo 3: Consultar balance

```bash
curl http://localhost:8000/balance/MODELO_A
```

---

## 🔗 Conexión con Contratos

La API llama automáticamente a los scripts en `/contract/scripts/`:

| Operación | Script | Función |
|-----------|--------|---------|
| Mintear recursos | `API.py` | Crea recursos desde BANCO |
| Transferir | `API.py` | Transfiere entre modelos |
| Consultar balance | `get_balance.py` | Lee blockchain |

**No necesitas modificar estos scripts**, la API los llama con los parámetros correctos.

---

## 🧪 Testing

### Test local sin blockchain

```python
# En Python:
from trade_client import enviar_trade

# Esto llamará a la API en localhost:8000
resultado = enviar_trade(
    origen="BANCO",
    destino="MODELO_A",
    recursos=[{"id": 1, "cantidad": 10}]
)

print(resultado)
```

---

## 📊 Arquitectura

```
┌─────────────┐
│  MODELO_A   │
│  (Alice)    │
└──────┬──────┘
       │ HTTP POST
       ▼
┌─────────────────────────┐
│  FastAPI (puerto 8000)  │
│  /trade, /balance       │
└──────┬──────────────────┘
       │ subprocess
       ▼
┌─────────────────────────┐
│  Scripts Python         │
│  API.py                 │
│  get_balance.py         │
└──────┬──────────────────┘
       │ Web3.py
       ▼
┌─────────────────────────┐
│  Avalanche Testnet      │
│  ContratoCatan (ERC1155)│
└─────────────────────────┘
```

---

## ⚠️ Requisitos Previos

1. **Variables de entorno (.env en /contract):**
   ```
   PRIVATE_KEY_ADMIN_L1=...
   PRIVATE_KEY_MODELO_A=...
   PRIVATE_KEY_MODELO_B=...
   CATAN_ADDRESS=0x...
   ```

2. **Contrato deployado** en Avalanche Testnet

3. **Python 3.8+**

4. **Paquetes instalados:**
   - api: `pip install -r api/requirements.txt`
   - modelos: `pip install requests`

---

## 🐛 Troubleshooting

### "Connection refused" al conectar desde modelos

```
❌ No se pudo conectar a la API. ¿Está levantada en http://127.0.0.1:8000?
```

**Solución:**
```bash
# Asegúrate de que la API está corriendo:
cd api
uvicorn main:app --reload --port 8000
```

### Error 422 - Validación

```
❌ Error 422: Validation error
```

**Verifica:**
- `origen` y `destino` son válidos
- `recursos` es un array con `id` y `cantidad` numéricos
- Origen ≠ Destino

### Error 500 - Script no ejecuta

```
❌ Error executing script: ...
```

**Verifica:**
- `.env` en `/contract` tiene las variables correctas
- El contrato está deployado (`CATAN_ADDRESS`)
- Las claves privadas son válidas

---

## 📞 Endpoints Adicionales

### GET /health
Verifica que la API esté viva:
```bash
curl http://localhost:8000/health
```

### GET /info
Muestra configuración:
```bash
curl http://localhost:8000/info
```

---

## 🎯 Próximos pasos

1. ✅ Levantar API: `uvicorn main:app --reload`
2. ✅ Instalar requests: `pip install requests`
3. ✅ Usar `trade_client.py` desde los modelos
4. ✅ Integrar en la simulación de Catan

¡Listo! 🚀
