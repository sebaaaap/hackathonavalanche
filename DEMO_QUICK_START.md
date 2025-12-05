# 🎮 EJECUTAR DEMO COMPLETA - Guía Rápida

## ⚡ OPCIÓN A: Una sola línea de comando (RECOMENDADO)

Si todo está instalado, simplemente ejecuta:

```powershell
cd models_venv
python launch_demo.py
```

**¡Eso es todo!** El script:
1. ✅ Levanta la API automáticamente
2. ✅ Ejecuta la demo
3. ✅ Muestra la partida en tiempo real
4. ✅ Limpia recursos al terminar

---

## 📋 OPCIÓN B: Dos terminales (si prefieres control manual)

### Terminal 1: Levanta la API

```powershell
cd api
uvicorn main:app --reload --port 8000
```

Espera a ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2: Ejecuta la demo

```powershell
cd models_venv
python demo_game_blockchain.py
```

---

## 🎯 Lo que verás

Una partida completa donde:

1. **Inicialización**
   - BANCO distribuye recursos a Alice y Bob
   - Cada transferencia registrada en blockchain

2. **10 Turnos**
   - Cada jugador: tira dados → recibe recursos → construye → comercia
   - Todas las acciones en blockchain (real, no simulado)

3. **Resultados**
   - Balance final de cada jugador
   - Puntos obtenidos
   - Hashes de transacciones para verificar en blockchain

---

## 🔍 Verificar Transacciones

Después de ejecutar la demo, puedes verificar las transacciones en:

```
https://testnet.snowtrace.io
```

Copia uno de los hashes que aparece en la ejecución (ej: `0xabc123...`) y búscalo.

---

## ⚠️ Requisitos Previos

### 1. Instalar dependencias

```powershell
cd api
pip install -r requirements.txt

cd ../models_venv
pip install requests
```

### 2. .env configurado

Asegúrate de que `/contract/.env` tiene:
```
PRIVATE_KEY_ADMIN_L1=...
PRIVATE_KEY_MODELO_A=...
PRIVATE_KEY_MODELO_B=...
CATAN_ADDRESS=0x...
```

### 3. Contrato deployado

El contrato ERC-1155 debe estar deployado en Avalanche Testnet.

---

## 🎮 ¿Qué es lo que ves?

```
======================================================================
                🎮 CATAN CON BLOCKCHAIN - DEMO COMPLETA 🎮
======================================================================

ℹ️  Este programa simula una partida de Catan donde:
  - Alice (MODELO_A) y Bob (MODELO_B) juegan
  - El BANCO distribuye recursos desde blockchain
  - Cada acción se registra en Avalanche

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

[Continúa con Alice y Bob...]

📊 BALANCE ACTUAL (desde Blockchain)
======================================================================

👤 Alice:
    MADERA         : 5
    ARCILLA        : 3
    OVEJA          : 4
    TRIGO          : 4
    MINERAL        : 2
    TOTAL          : 18

[Continúa con 10 turnos...]

🏁 FIN DE LA PARTIDA - RESUMEN FINAL
======================================================================

📊 BALANCE ACTUAL (desde Blockchain)

👤 Alice:
    MADERA         : 8
    ARCILLA        : 2
    OVEJA          : 5
    TRIGO          : 2
    MINERAL        : 1
    TOTAL          : 18

🏆 PUNTOS FINALES

👤 Alice: 2 puntos
👤 Bob: 1 puntos

✅ DEMO COMPLETADA EXITOSAMENTE
```

---

## 📊 Flujo de Datos

```
┌─────────────────────────────────────────────┐
│ launch_demo.py o Terminal 1                 │
│ - Levanta API en puerto 8000                │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ demo_game_blockchain.py o Terminal 2        │
│ - Ejecuta partida                           │
│ - Usa trade_client.py                       │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ api/main.py (FastAPI)                       │
│ - Procesa requests POST /trade              │
│ - Procesa requests GET /balance             │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ contract/scripts/API.py                     │
│ - Ejecuta Web3 transactions                 │
│ - Mint, transfer, balance queries           │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ Avalanche Blockchain (Testnet)              │
│ - ERC-1155 Contract                         │
│ - Datos permanentes                         │
└─────────────────────────────────────────────┘
```

---

## 🎯 Comandos Rápidos

| Acción | Comando |
|--------|---------|
| Demo (automático) | `cd models_venv && python launch_demo.py` |
| API sola | `cd api && uvicorn main:app --reload` |
| Demo sola | `cd models_venv && python demo_game_blockchain.py` |
| Ejemplos básicos | `cd models_venv && python ejemplo_integracion.py` |
| Verificar setup | `cd . && python verify_setup.py` |

---

## 🐛 Solución de Problemas

### "Connection refused"
```
❌ Error: No se pudo conectar a la API
✅ Solución: Asegúrate de que la API está en Terminal 1
```

### "Module not found"
```
❌ Error: No module named 'fastapi'
✅ Solución: pip install -r api/requirements.txt
```

### Las transacciones fallan
```
❌ Error: Error ejecutando script
✅ Solución: Verifica .env en /contract con variables correctas
```

---

## 📚 Documentación Completa

- **Demo**: Ver `models_venv/DEMO_README.md`
- **API**: Ver `api/README.md`
- **Cliente**: Ver `models_venv/README_API.md`
- **General**: Ver `BLOCKCHAIN_INTEGRATION.md`

---

## 🚀 Próximos Pasos

1. ✅ Ejecutar: `python launch_demo.py`
2. ✅ Observar partida en tiempo real
3. ✅ Verificar transacciones en Snowtrace
4. ✅ Integrar tu propia lógica de IA
5. ✅ Agregar más jugadores

---

## 🎓 Aprenderás

- ✅ Cómo integrar IA con blockchain
- ✅ Transacciones en tiempo real
- ✅ Verificación de datos en blockchain
- ✅ Arquitectura completa de un juego descentralizado

---

**¡Disfruta tu juego en blockchain! 🚀**

```powershell
cd models_venv
python launch_demo.py
```
