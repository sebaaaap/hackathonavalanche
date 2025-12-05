# 🏦 Catan Blockchain - Guía de Setup Rápido

**Propósito:** Conectar la simulación Catan con contratos ERC-1155 en Avalanche a través de FastAPI.

---

## ⚡ Setup en 3 minutos

### 1. Instalar dependencias

```powershell
# Opción A: Ejecutar script automatizado
.\setup.bat

# Opción B: Manual
cd api
pip install -r requirements.txt
cd ../models_venv
pip install requests
```

### 2. Levantar la API

```powershell
cd api
uvicorn main:app --reload --port 8000
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 3. Usar en tus modelos

```python
# En models_venv o en tu código:
from trade_client import enviar_trade, obtener_balance

# Ejemplo: MODELO_A envía 5 maderas a MODELO_B
resultado = enviar_trade(
    origen="MODELO_A",
    destino="MODELO_B",
    recursos=[{"id": 1, "cantidad": 5}]
)

if resultado["status"] == "success":
    print(f"✅ Trade exitoso: {resultado['hash_tx']}")
```

---

## 📊 Archivos Creados

```
hackathonavalanche/
├── api/
│   ├── main.py                 ✨ NUEVA API FastAPI
│   ├── requirements.txt         ✨ Dependencias
│   └── README.md                ✨ Docs completas
│
├── models_venv/
│   ├── trade_client.py          ✨ Cliente HTTP
│   ├── ejemplo_integracion.py   ✨ Ejemplos de uso
│   ├── README_API.md            ✨ Docs para modelos
│   └── requirements_api.txt     ✨ Dependencias
│
├── setup.bat                     ✨ Setup automatizado
├── BLOCKCHAIN_INTEGRATION.md     ← TÚ ESTÁS AQUÍ

Archivos NO modificados:
├── contract/                     ✅ Intacto
├── models_venv/                  ✅ Intacto (solo added)
└── Client/                       ✅ Intacto
```

---

## 🚀 Comandos Principales

### Terminal 1: Levantar API
```powershell
cd api
uvicorn main:app --reload --port 8000
```

### Terminal 2: Usar desde modelos
```powershell
cd models_venv

# Ejecutar ejemplos:
python ejemplo_integracion.py

# O integrar en tu código:
# from trade_client import enviar_trade
# resultado = enviar_trade(...)
```

---

## 📡 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/trade` | Enviar recursos |
| GET | `/balance/{modelo}` | Consultar saldo |
| GET | `/health` | Verifica disponibilidad |
| GET | `/info` | Configuración |

### Ejemplo: POST /trade

```bash
curl -X POST http://localhost:8000/trade \
  -H "Content-Type: application/json" \
  -d '{
    "origen": "BANCO",
    "destino": "MODELO_A",
    "recursos": [{"id": 1, "cantidad": 10}]
  }'
```

### Ejemplo: GET /balance/{modelo}

```bash
curl http://localhost:8000/balance/MODELO_A
```

---

## 💻 Ejemplos Prácticos

### 1. Enviar recursos del BANCO

```python
from trade_client import enviar_trade

# BANCO crea y envía 20 maderas a MODELO_A
enviar_trade("BANCO", "MODELO_A", [{"id": 1, "cantidad": 20}])
```

### 2. Transferencia entre modelos

```python
from trade_client import enviar_trade

# MODELO_A envía a MODELO_B
enviar_trade("MODELO_A", "MODELO_B", [{"id": 1, "cantidad": 5}])
```

### 3. Múltiples recursos

```python
from trade_client import enviar_trade

# MODELO_A envía: 5 maderas + 3 ovejas
enviar_trade(
    "MODELO_A",
    "MODELO_B",
    [
        {"id": 1, "cantidad": 5},   # Madera
        {"id": 3, "cantidad": 3}    # Oveja
    ]
)
```

### 4. Consultar balance

```python
from trade_client import obtener_balance

balance = obtener_balance("MODELO_A")
if balance["status"] == "success":
    print(balance["recursos"])
    # Output: {"MADERA": 15, "ARCILLA": 8, "OVEJA": 10, ...}
```

---

## 🎯 Flujo Completo

```
Tu código (modelo)
    │
    ├─ from trade_client import enviar_trade
    ├─ enviar_trade("MODELO_A", "MODELO_B", [{"id": 1, "cantidad": 5}])
    │
    └─► HTTP POST → API FastAPI (http://127.0.0.1:8000)
         │
         └─► subprocess → Scripts Python en /contract
              │
              └─► Web3 → Contrato ERC-1155 en Avalanche
                   │
                   └─► ✅ Blockchain actualizado
                       (emisión, transferencia, balance)
```

---

## 🔑 IDs de Recursos

| ID | Recurso |
|----|---------|
| 1 | MADERA |
| 2 | ARCILLA |
| 3 | OVEJA |
| 4 | TRIGO |
| 5 | MINERAL |

---

## ✅ Requisitos Previos

Antes de correr la API, asegúrate de que:

1. **`.env` en `/contract`** contiene:
   ```
   PRIVATE_KEY_ADMIN_L1=...
   PRIVATE_KEY_MODELO_A=...
   PRIVATE_KEY_MODELO_B=...
   CATAN_ADDRESS=0x...
   ```

2. **Contrato deployado** en Avalanche Testnet

3. **Python 3.8+** instalado

4. **Dependencias instaladas:**
   ```bash
   pip install -r api/requirements.txt
   pip install requests
   ```

---

## 📚 Documentación Completa

- **API**: Leer `api/README.md`
- **Modelos**: Leer `models_venv/README_API.md`
- **Ejemplos**: Ver `models_venv/ejemplo_integracion.py`

---

## 🐛 Troubleshooting

### "Connection refused"
```
Error: No se pudo conectar a la API
Solución: uvicorn main:app --reload --port 8000
```

### "Module not found: fastapi"
```
Solución: pip install -r api/requirements.txt
```

### "Module not found: requests"
```
Solución: pip install requests
```

### "Error 422 - Validación"
```
Verifica que:
- origen y destino sean válidos (MODELO_A, MODELO_B, BANCO)
- recursos sea un array con "id" y "cantidad"
- origen ≠ destino
```

---

## 🎓 Próximos Pasos

1. ✅ Instalar: `pip install -r api/requirements.txt && pip install requests`
2. ✅ Levantar API: `uvicorn main:app --reload`
3. ✅ Probar: `python ejemplo_integracion.py`
4. ✅ Integrar: Usar `trade_client` en tus modelos
5. ✅ Simular: Catan con blockchain real

---

## 📞 URLs Útiles

- API FastAPI: `http://localhost:8000`
- API Docs (Swagger): `http://localhost:8000/docs`
- API Docs (ReDoc): `http://localhost:8000/redoc`

---

## ⚡ Cheat Sheet

```python
# Importar
from trade_client import enviar_trade, obtener_balance

# Enviar recursos
enviar_trade("MODELO_A", "MODELO_B", [{"id": 1, "cantidad": 5}])

# Consultar balance
obtener_balance("MODELO_A")

# Verificar API
import requests
requests.get("http://127.0.0.1:8000")

# Ejecutar ejemplo completo
# cd models_venv && python ejemplo_integracion.py
```

---

**¡Listo! La integración está lista para usar.** 🚀
