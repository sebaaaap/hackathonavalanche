# 🎮 API CATAN BLOCKCHAIN - GUÍA FRONTEND

API REST para integrar Catan con blockchain Avalanche.

## 🚀 URL Base
```
http://127.0.0.1:8000
```

---

## 📡 ENDPOINTS

### 1. **POST /trade** - Enviar Recursos
Transfiere recursos entre jugadores o desde el banco.

**Request:**
```json
{
  "origen": "BANCO",
  "destino": "MODELO_A",
  "recursos": [
    {"id": 1, "cantidad": 5},
    {"id": 2, "cantidad": 3}
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "mensaje": "Trade ejecutado: BANCO → MODELO_A",
  "hash_tx": "0x095bd92243867aaf...",
  "origen": "BANCO",
  "destino": "MODELO_A",
  "recursos": [
    {"id": 1, "cantidad": 5},
    {"id": 2, "cantidad": 3}
  ]
}
```

---

### 2. **GET /balance/{modelo}** - Consultar Balance
Obtiene los recursos de un jugador.

**Request:**
```
GET /balance/MODELO_A
```

**Response:**
```json
{
  "modelo": "MODELO_A",
  "recursos": {
    "MADERA": 257,
    "ARCILLA": 3,
    "OVEJA": 14,
    "TRIGO": 14,
    "MINERAL": 45
  }
}
```

---

### 3. **POST /robber/attack** - Atacar con Ladrón
Un jugador roba 1 recurso a otro mediante el ladrón.

**Request:**
```json
{
  "atacante": "MODELO_A",
  "victima": "MODELO_B",
  "recurso_id": 1
}
```

**Response:**
```json
{
  "status": "success",
  "mensaje": "Ladrón: MODELO_A robó recurso 1 de MODELO_B",
  "hash_tx": "0x29f91d320f96a47e...",
  "atacante": "MODELO_A",
  "victima": "MODELO_B",
  "recurso_robado": 1
}
```

---

## 🎴 IDs de Recursos

| ID | Recurso   |
|----|-----------|
| 1  | MADERA    |
| 2  | ARCILLA   |
| 3  | OVEJA     |
| 4  | TRIGO     |
| 5  | MINERAL   |

---

## 🏦 Modelos Disponibles

- `BANCO` - Crea recursos (mint)
- `MODELO_A` - Jugador Alice
- `MODELO_B` - Jugador Bob

---

## 🔥 Ejemplo de Uso en JavaScript

```javascript
// Enviar recursos desde banco
async function distribuirRecursos() {
  const response = await fetch('http://127.0.0.1:8000/trade', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      origen: "BANCO",
      destino: "MODELO_A",
      recursos: [
        { id: 1, cantidad: 5 },  // 5 Maderas
        { id: 2, cantidad: 3 }   // 3 Arcillas
      ]
    })
  });
  
  const data = await response.json();
  console.log('Trade exitoso:', data.hash_tx);
}

// Consultar balance
async function verBalance() {
  const response = await fetch('http://127.0.0.1:8000/balance/MODELO_A');
  const data = await response.json();
  console.log('Recursos:', data.recursos);
}

// Atacar con ladrón
async function atacarConLadron() {
  const response = await fetch('http://127.0.0.1:8000/robber/attack', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      atacante: "MODELO_A",
      victima: "MODELO_B",
      recurso_id: 1  // Robar 1 madera
    })
  });
  
  const data = await response.json();
  console.log('Robo exitoso:', data.hash_tx);
}
```

---

## ⚠️ IMPORTANTE: Recargar AVAX

Si ves error `insufficient funds for gas`, la wallet del BANCO no tiene AVAX.

**Solución:**
1. Ve a https://faucet.avax.network/
2. Ingresa la dirección del BANCO (desde `.env`)
3. Solicita AVAX de prueba en Fuji Testnet

---

## 🔍 Logs Reducidos

La API ahora muestra logs limpios:
```
🏦 MINT: BANCO → MODELO_A (5 recursos)
🔄 TRANSFER: MODELO_A → MODELO_B (2 recursos)
💰 BALANCE: MODELO_A
🎲 LADRÓN: MODELO_A ataca MODELO_B (ID:1)
```

---

## 📊 Verificar Transacciones

Todas las transacciones se registran en **Avalanche Fuji Testnet**.

Ver en explorador:
```
https://testnet.snowtrace.io/tx/{hash_tx}
```

---

## 🚦 Health Check

```bash
GET /health
GET /info
```

Retorna información del sistema y scripts disponibles.
