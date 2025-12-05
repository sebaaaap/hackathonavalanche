# 🎮 GUÍA RÁPIDA: CATAN BLOCKCHAIN COMPLETO

## 🚀 INICIO RÁPIDO

### 1️⃣ Iniciar Servidores (Ejecutar Primero)

**Opción A - Automático (Windows):**
```bash
# Doble clic en:
START_SERVERS.bat
```

**Opción B - Manual:**
```bash
# Terminal 1: FastAPI (blockchain)
cd api
uvicorn main:app --reload --port 8000

# Terminal 2: Flask API (frontend)
cd contract/scripts
python API.py
```

**Verificar:**
- FastAPI: http://127.0.0.1:8000
- Flask: http://127.0.0.1:5001

---

### 2️⃣ Ejecutar Demo (1 Turno)

```bash
cd models_venv
python demo_game_blockchain.py
```

**¿Qué hace?**
- ✅ Ejecuta **1 turno completo** de Catan
- ✅ Alice juega contra blockchain
- ✅ Envía metadata a Flask API
- ✅ Registra todo en Avalanche Fuji

---

## 📡 FLUJO DE DATOS

```
┌─────────────────┐
│  demo_game_     │  Simula partida Catan
│  blockchain.py  │  (Alice vs Bob)
└────────┬────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼                                     ▼
┌──────────────────┐                  ┌──────────────────┐
│  FastAPI         │                  │  Flask API       │
│  (puerto 8000)   │                  │  (puerto 5001)   │
│                  │                  │                  │
│  /trade          │                  │  /game-state     │
│  /balance        │                  │  (POST/GET)      │
│  /robber/attack  │                  │                  │
└────────┬─────────┘                  └──────────────────┘
         │                                     ▲
         │                                     │
         ▼                                     │
┌──────────────────┐                           │
│  Avalanche Fuji  │                           │
│  Blockchain      │                           │
│  (Web3)          │                           │
└──────────────────┘                           │
         │                                     │
         └─────────────────────────────────────┘
              Metadata del juego enviada aquí
```

---

## 📊 DATOS ENVIADOS A FLASK

Cada turno envía este JSON a `POST /game-state`:

```json
{
  "turno": 1,
  "jugador_actual": "MODELO_A",
  "jugador_nombre": "Alice",
  "dados": [3, 4],
  "total_dados": 7,
  "recursos_generados": {
    "MODELO_A": [
      {"recurso": "MADERA", "id": 1, "cantidad": 2},
      {"recurso": "TRIGO", "id": 4, "cantidad": 1}
    ]
  },
  "construcciones": [
    {
      "tipo": "pueblo",
      "costo": {"MADERA": 1, "ARCILLA": 1, "OVEJA": 1, "TRIGO": 1},
      "hash_tx": "0x095bd922..."
    }
  ],
  "comercios": [
    {
      "de": "MODELO_A",
      "para": "MODELO_B",
      "recurso": "MADERA",
      "cantidad": 2,
      "hash_tx": "0x29f91d32..."
    }
  ],
  "balances": {
    "MODELO_A": {
      "MADERA": 257,
      "ARCILLA": 3,
      "OVEJA": 14,
      "TRIGO": 14,
      "MINERAL": 45
    },
    "MODELO_B": {
      "MADERA": 12,
      "ARCILLA": 1,
      "OVEJA": 6,
      "TRIGO": 8,
      "MINERAL": 8
    }
  },
  "hashes_tx": [
    "0x095bd92243867aaf...",
    "0x29f91d320f96a47e..."
  ]
}
```

---

## 🌐 ENDPOINTS PARA FRONTEND

### Flask API (localhost:5001)

#### 1. **GET /game-state** - Consultar Estado Actual
```javascript
// Obtener último turno
fetch('http://127.0.0.1:5001/game-state?ultimo=true')
  .then(res => res.json())
  .then(data => console.log(data.turno_actual));

// Obtener todos los turnos
fetch('http://127.0.0.1:5001/game-state')
  .then(res => res.json())
  .then(data => console.log(data.turnos));
```

#### 2. **POST /game-state** - Recibir Turno (Automático desde demo)
No necesitas llamar esto manualmente, el demo lo hace.

#### 3. **GET /consultar-saldos** - Balances desde Blockchain
```javascript
fetch('http://127.0.0.1:5001/consultar-saldos')
  .then(res => res.json())
  .then(data => console.log(data.saldos));
```

---

## ⚠️ SOLUCIÓN DE PROBLEMAS

### Error: `insufficient funds for gas`
**Causa:** Wallet del BANCO sin AVAX

**Solución:**
1. Ve a https://faucet.avax.network/
2. Ingresa dirección del BANCO (desde `.env`)
3. Solicita AVAX de prueba

### Error: `API no disponible (puerto 5001)`
**Causa:** Flask API no está corriendo

**Solución:**
```bash
cd contract/scripts
python API.py
```

### Error: `Connection refused (puerto 8000)`
**Causa:** FastAPI no está corriendo

**Solución:**
```bash
cd api
uvicorn main:app --reload --port 8000
```

---

## 🔧 PERSONALIZACIÓN

### Cambiar Cantidad de Turnos
Edita `demo_game_blockchain.py` línea 114:
```python
self.max_turnos = 1  # Cambiar a 5, 10, etc.
```

### Agregar Más Jugadores
Edita `.env` y agrega:
```bash
PRIVATE_KEY_MODELO_C=0x...
```

Luego modifica `MODELOS_MAP` en las APIs.

---

## 📝 VERIFICAR TRANSACCIONES

Todas las transacciones se pueden ver en:
```
https://testnet.snowtrace.io/tx/{hash_tx}
```

Copia el `hash_tx` de la metadata y pégalo en el explorador.

---

## 🎯 RESUMEN DE ARCHIVOS CLAVE

| Archivo | Función |
|---------|---------|
| `demo_game_blockchain.py` | Simula partida Catan (1 turno) |
| `api/main.py` | FastAPI - Blockchain |
| `contract/scripts/API.py` | Flask API - Frontend |
| `trade_client.py` | Cliente HTTP para trades |
| `START_SERVERS.bat` | Inicia ambas APIs |

---

## ✅ CHECKLIST DE EJECUCIÓN

- [ ] Recargar AVAX en wallet BANCO (faucet)
- [ ] Iniciar FastAPI (puerto 8000)
- [ ] Iniciar Flask API (puerto 5001)
- [ ] Ejecutar demo: `python demo_game_blockchain.py`
- [ ] Verificar metadata en Flask: `GET /game-state`
- [ ] Consultar balances: `GET /consultar-saldos`

---

## 🎮 ¡TODO LISTO!

Tu sistema ahora:
- ✅ Ejecuta 1 turno de Catan
- ✅ Registra transacciones en blockchain
- ✅ Envía metadata a Flask API
- ✅ Frontend puede consultar estado del juego
- ✅ Balances, dados, construcciones y comercios rastreados

**Para frontend React/Next.js:**
Consulta `GET http://127.0.0.1:5001/game-state?ultimo=true` cada segundo para actualizar UI en tiempo real.
