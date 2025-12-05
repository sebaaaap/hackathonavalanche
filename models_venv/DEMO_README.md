# 🎮 DEMO DE JUEGO COMPLETO - Catan con Blockchain

Archivo ejecutable que muestra una **partida completa** de Catan donde dos modelos (Alice y Bob) juegan y comercian usando blockchain en Avalanche.

---

## ⚡ Inicio Rápido (3 pasos)

### Paso 1: Abre DOS terminales

**Terminal 1 - Levanta la API:**
```powershell
cd api
uvicorn main:app --reload --port 8000
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 - Ejecuta la demo:**
```powershell
cd models_venv
python demo_game_blockchain.py
```

### Paso 2: Observa la partida

Verás algo como:

```
======================================================================
                🎮 CATAN CON BLOCKCHAIN - DEMO COMPLETA 🎮
======================================================================

ℹ️  Este programa simula una partida de Catan donde:
  - Alice (MODELO_A) y Bob (MODELO_B) juegan
  - El BANCO distribuye recursos desde blockchain
  - Cada acción se registra en Avalanche
  - Los datos son reales en blockchain, no simulados
```

### Paso 3: Verifica las transacciones

Todas las transacciones se guardan en blockchain. Puedes verificarlas en:
```
https://testnet.snowtrace.io
```

---

## 🎮 ¿Qué hace la demo?

### 1. Inicialización
- El BANCO distribuye recursos iniciales a Alice y Bob
- 5 Maderas, 3 Arcillas, 4 Ovejas, 4 Trigos, 2 Minerales (cada uno)
- Todo registrado en blockchain

### 2. Turnos (10 turnos)

Cada turno tiene 4 fases:

**Fase 1: 🎲 Tirar dados**
- Simula lanzamiento de dos dados
- Resultado determina recursos generados

**Fase 2: 🌾 Generar recursos**
- Basado en los dados, el BANCO envía recursos
- Transacción registrada en blockchain

**Fase 3: 🏗️ Construcción**
- El jugador intenta construir pueblos o carreteras
- Envía recursos al BANCO como pago
- Registrado en blockchain

**Fase 4: 💼 Comercio**
- El jugador comercia recursos con otro jugador
- Transacción blockchain entre modelos

### 3. Resultados

Al final, muestra:
- Balance final de cada jugador
- Puntos obtenidos
- Resumen de eventos
- URLs para verificar en blockchain

---

## 📊 Flujo de Datos Visualizado

```
ALICE (MODELO_A)
    │
    ├─ Tira dados → API → Blockchain
    │
    ├─ Recibe recursos → Transacción del BANCO
    │
    ├─ Construye pueblo → Envía recursos al BANCO
    │
    └─ Comercia con Bob → Transacción directa
         │
         └─► Blockchain actualiza balances


BOB (MODELO_B)
    │
    ├─ Tira dados → API → Blockchain
    │
    ├─ Recibe recursos → Transacción del BANCO
    │
    ├─ Construye pueblo → Envía recursos al BANCO
    │
    └─ Comercia con Alice → Transacción directa
         │
         └─► Blockchain actualiza balances


BANCO
    │
    ├─ Distribuye recursos iniciales
    │
    ├─ Envía recursos generados por dados
    │
    ├─ Recibe pagos por construcciones
    │
    └─ Todo registrado permanentemente en blockchain
```

---

## 🎯 Recursos en el Juego

| ID | Recurso | Cantidad Inicial |
|----|---------|-----------------|
| 1 | 🌳 MADERA | 5 |
| 2 | 🧱 ARCILLA | 3 |
| 3 | 🐑 OVEJA | 4 |
| 4 | 🌾 TRIGO | 4 |
| 5 | 🔨 MINERAL | 2 |

---

## 💰 Costos de Construcción

| Construcción | Costo |
|--------------|-------|
| 🏘️ Pueblo | 1 Madera + 1 Arcilla + 1 Oveja + 1 Trigo |
| 🏰 Castillo | 3 Trigo + 2 Mineral |
| 🛣️ Carretera | 1 Madera + 1 Arcilla |
| 📚 Carta Desarrollo | 1 Oveja + 1 Trigo + 1 Mineral |

---

## 📡 Endpoints Usados

La demo usa estos endpoints de la API:

### 1. POST /trade - Enviar recursos
```python
# El BANCO distribuye recursos a los modelos
enviar_trade(
    origen="BANCO",
    destino="MODELO_A",
    recursos=[{"id": 1, "cantidad": 5}]
)

# Los modelos comercian entre ellos
enviar_trade(
    origen="MODELO_A",
    destino="MODELO_B",
    recursos=[{"id": 1, "cantidad": 2}]
)
```

### 2. GET /balance/{modelo} - Consultar saldo
```python
# Obtener balance actual de un modelo
balance = obtener_balance("MODELO_A")
# Retorna: {"MADERA": 5, "ARCILLA": 3, ...}
```

---

## 🔍 Verificar Transacciones

### Durante la ejecución
La demo muestra en tiempo real:
- Hash de cada transacción
- Estado (✅ éxito o ❌ error)
- Recursos enviados/recibidos

### Después de la ejecución
Puedes verificar en blockchain:
```
https://testnet.snowtrace.io
```

1. Copia un hash de transacción (ej: `0x123abc...`)
2. Pégalo en la búsqueda de Snowtrace
3. Verás todos los detalles en blockchain

---

## 📝 Ejemplo de Salida

```
======================================================================
                💰 INICIALIZANDO BANCO Y DISTRIBUYENDO RECURSOS
======================================================================

ℹ️  Distribuyendo recursos iniciales a Alice...
   - 5 Maderas
   - 3 Arcillas
   - 4 Ovejas
   - 4 Trigos
   - 2 Minerales
✅ Recursos distribuidos a Alice
   TX Hash: 0xabc123def456...

ℹ️  Distribuyendo recursos iniciales a Bob...
   [similar]

----------------------------------------------------------------------
                      📊 BALANCE ACTUAL (desde Blockchain)
----------------------------------------------------------------------

👤 Alice:
    MADERA         : 5
    ARCILLA        : 3
    OVEJA          : 4
    TRIGO          : 4
    MINERAL        : 2
    TOTAL          : 18

👤 Bob:
    [similar]

======================================================================
                       🎮 TURNO 1 - Alice
======================================================================

----------------------------------------------------------------------
                         🎲 FASE 1: TIRAR DADOS
----------------------------------------------------------------------

ℹ️  🎲 Dados: 3 + 4 = 7

----------------------------------------------------------------------
                      🌾 FASE 2: GENERAR RECURSOS
----------------------------------------------------------------------

ℹ️  Recursos generados por la tirada:
   MADERA: 2
   ARCILLA: 1
   OVEJA: 3

ℹ️  El BANCO envía 2 MADERA...
✅ Recursos enviados!

[continúa...]
```

---

## 🐛 Troubleshooting

### "Connection refused"
```
Error: No se pudo conectar a la API
Solución:
  1. Asegúrate de que Terminal 1 tiene API levantada
  2. Verifica: http://localhost:8000
```

### "Module not found: trade_client"
```
Error: No module named 'trade_client'
Solución:
  1. Asegúrate de estar en /models_venv
  2. Verifica que trade_client.py está en el mismo directorio
```

### "Modelo inválido"
```
Error: Modelo inválido
Solución:
  - Solo usa: MODELO_A, MODELO_B, BANCO
  - Verifica ortografía exacta
```

### Las transacciones fallan
```
Error: Error ejecutando script
Solución:
  1. Verifica que .env en /contract tiene variables correctas
  2. Verifica que el contrato está deployado
  3. Verifica que las claves privadas son válidas
```

---

## 🚀 Variaciones

### 1. Más turnos
```python
# En demo_game_blockchain.py, línea ~400
self.max_turnos = 20  # Cambiar a más turnos
```

### 2. Diferentes recursos iniciales
```python
# En inicializar_recursos(), edita:
recursos_iniciales = [
    {"id": 1, "cantidad": 10},  # Más maderas
    ...
]
```

### 3. Agregar más modelos
```python
# Extender MODELO_A y MODELO_B a MODELO_C, etc.
modelos_orden = [MODELO_A, MODELO_B, MODELO_C]
```

---

## 📚 Archivos Relacionados

- `trade_client.py` - Cliente HTTP que usa la demo
- `api/main.py` - API FastAPI que procesa las transacciones
- `contract/scripts/API.py` - Script que ejecuta las TX en blockchain
- `BLOCKCHAIN_INTEGRATION.md` - Documentación general

---

## 🎓 Aprendizaje

Esta demo te muestra:
1. ✅ Cómo usar `trade_client` en un juego real
2. ✅ Integración entre simulación y blockchain
3. ✅ Manejo de transacciones en tiempo real
4. ✅ Verificación de datos en blockchain
5. ✅ Escalabilidad a múltiples jugadores

---

## 🎮 Próximos Pasos

1. ✅ Ejecutar la demo: `python demo_game_blockchain.py`
2. ✅ Verificar transacciones en blockchain
3. ✅ Integrar tu lógica de IA en lugar de simulación aleatoria
4. ✅ Agregar más jugadores
5. ✅ Implementar lógica de Catan real (ladrones, cartas de desarrollo, etc)

---

## 📞 Contacto

Si tienes dudas sobre:
- La API: ver `api/README.md`
- El cliente: ver `models_venv/README_API.md`
- Blockchain: ver `BLOCKCHAIN_INTEGRATION.md`

¡Que disfrutes viendo tu juego en blockchain! 🚀
