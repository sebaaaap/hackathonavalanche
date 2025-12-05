# 🎮 COMPILAR Y EJECUTAR - GUÍA FINAL

## ⚡ LA FORMA MÁS SIMPLE (3 PASOS)

### Opción 1: Hacer doble click (Windows)
```
1. Navega a la carpeta raíz del proyecto
2. Haz doble click en RUN.bat
3. Elige opción [A]
```

### Opción 2: Línea de comando (Windows PowerShell)
```powershell
python compile_and_run.py
cd models_venv
python launch_demo.py
```

### Opción 3: Línea de comando (Linux/Mac)
```bash
python3 compile_and_run.py
cd models_venv
python3 launch_demo.py
```

---

## 🔧 ¿QUÉ HACE EL COMPILADOR?

El script `compile_and_run.py`:

✅ Verifica que tienes la estructura correcta
✅ Valida que el `.env` en `/contract` está configurado
✅ Instala todas las dependencias (fastapi, uvicorn, requests, etc)
✅ Verifica que todos los archivos críticos existen
✅ Te muestra exactamente qué ejecutar

---

## 🎯 PASOS DETALLES (SI PREFIERES MANUAL)

### 1. Compilar (verificar todo)
```powershell
python compile_and_run.py
```

Verás:
```
[1] VERIFICANDO ESTRUCTURA DEL PROYECTO
    ✅ API FastAPI: C:\...\api
    ✅ Contratos: C:\...\contract
    ✅ Modelos: C:\...\models_venv

[2] VERIFICANDO CONFIGURACIÓN (.env)
    ✅ Archivo .env: C:\...\contract\.env
    ✅ Todas las variables de .env configuradas

[3] INSTALANDO DEPENDENCIAS - API FastAPI
    ✅ Dependencias API instaladas

[4] INSTALANDO DEPENDENCIAS - Modelos
    ✅ Dependencias de modelos listas

[5] VERIFICANDO ARCHIVOS CRÍTICOS
    ✅ API principal: C:\...\api\main.py
    ✅ Cliente HTTP: C:\...\models_venv\trade_client.py
    ✅ Demo del juego: C:\...\models_venv\demo_game_blockchain.py
    ✅ Script blockchain: C:\...\contract\scripts\API.py
    ✅ Script balance: C:\...\contract\scripts\get_balance.py

[6] ✅ COMPILACIÓN EXITOSA - PRÓXIMOS PASOS

OPCIÓN A: Ejecutar todo automáticamente (RECOMENDADO)
  cd models_venv
  python launch_demo.py

OPCIÓN B: Dos terminales (control manual)
  Terminal 1 (API):
    cd api
    uvicorn main:app --reload --port 8000
  
  Terminal 2 (Demo):
    cd models_venv
    python demo_game_blockchain.py
```

### 2. Levanta la API (Terminal 1)
```powershell
cd api
uvicorn main:app --reload --port 8000
```

Espera a ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 3. Ejecuta la demo (Terminal 2)
```powershell
cd models_venv
python demo_game_blockchain.py
```

Verás la partida en vivo:
```
======================================================================
                🎮 CATAN CON BLOCKCHAIN - DEMO COMPLETA 🎮
======================================================================

ℹ️  Este programa simula una partida de Catan donde:
  - Alice (MODELO_A) y Bob (MODELO_B) juegan
  - El BANCO distribuye recursos desde blockchain
  - Cada acción se registra en Avalanche

======================================================================
                💰 INICIALIZANDO BANCO Y DISTRIBUYENDO RECURSOS
======================================================================

ℹ️  Distribuyendo recursos iniciales a Alice...
✅ Recursos distribuidos a Alice
   TX Hash: 0xabc123...

[continúa...]
```

---

## 📋 REQUISITOS PREVIOS

### 1. Python 3.8+
```powershell
python --version
# Output: Python 3.10.5 (o superior)
```

### 2. .env Configurado en /contract

Asegúrate de que `/contract/.env` tiene:

```dotenv
PRIVATE_KEY_ADMIN_L1="0x..."
PRIVATE_KEY_MODELO_A="0x..."
PRIVATE_KEY_MODELO_B="0x..."
CATAN_ADDRESS="0x..."
RPC_URL="https://api.avax-test.network/ext/bc/C/rpc"
```

### 3. Contrato Deployado

El contrato ERC-1155 debe estar deployado en Avalanche Testnet y su dirección debe estar en `CATAN_ADDRESS`.

### 4. Saldo en Fuji Testnet

Necesitas AVAX en tu wallet para pagar gas de transacciones:
- Faucet: https://faucet.avax.network

---

## 🚀 ARCHIVOS CREADOS

| Archivo | Descripción |
|---------|-------------|
| `compile_and_run.py` | Compilador y verificador |
| `RUN.bat` | Lanzador para Windows |
| `api/main.py` | API FastAPI |
| `api/requirements.txt` | Dependencias API |
| `models_venv/trade_client.py` | Cliente HTTP |
| `models_venv/demo_game_blockchain.py` | Demo del juego |
| `models_venv/launch_demo.py` | Lanzador automático |

---

## 🎮 QUÉ VES EN LA EJECUCIÓN

### 1. Inicialización
```
💰 INICIALIZANDO BANCO Y DISTRIBUYENDO RECURSOS
  - Alice recibe: 5 Maderas, 3 Arcillas, 4 Ovejas, 4 Trigos, 2 Minerales
  - Bob recibe: 5 Maderas, 3 Arcillas, 4 Ovejas, 4 Trigos, 2 Minerales
  - Todo registrado en blockchain
```

### 2. Turnos (10 turnos)
```
🎮 TURNO 1 - Alice
  🎲 FASE 1: TIRAR DADOS
    Dados: 3 + 4 = 7
  
  🌾 FASE 2: GENERAR RECURSOS
    El BANCO envía recursos según los dados
  
  🏗️ FASE 3: CONSTRUCCIÓN
    Alice construye pueblo
    Envía recursos al BANCO
    Hash TX: 0x...
  
  💼 FASE 4: COMERCIO
    Alice comercia con Bob
    Transacción registrada
```

### 3. Resultados Finales
```
🏁 FIN DE LA PARTIDA

📊 BALANCE FINAL
  Alice: 18 recursos
  Bob: 18 recursos

🏆 PUNTOS FINALES
  Alice: 2 puntos
  Bob: 1 punto

✅ DEMO COMPLETADA
  Verifica en: https://testnet.snowtrace.io
```

---

## 🔍 VERIFICAR TRANSACCIONES

Después de ejecutar, verás hashes como:
```
TX Hash: 0xabc123def456...
```

### Para verificar en blockchain:

1. Copia un hash
2. Ve a: https://testnet.snowtrace.io
3. Pégalo en la barra de búsqueda
4. Verás todos los detalles de la transacción

---

## ⚠️ ERRORES COMUNES Y SOLUCIONES

### "Connection refused"
```
Error: No se pudo conectar a la API
Solución: Asegúrate de que la API está corriendo en Terminal 1
          http://localhost:8000 debe estar disponible
```

### "Module not found: fastapi"
```
Error: No module named 'fastapi'
Solución: python compile_and_run.py
          Esto instala todas las dependencias
```

### "PRIVATE_KEY_ADMIN_L1 no está configurado"
```
Error: Variables faltantes en .env
Solución: Edita /contract/.env y agrega las claves privadas
```

### "Transaction failed"
```
Error: Error ejecutando script
Soluciones posibles:
  1. Verifica que tienes AVAX en Fuji Testnet (faucet)
  2. Verifica que el contrato está deployado
  3. Verifica que CATAN_ADDRESS es correcto
```

---

## 🎯 COMANDOS RÁPIDOS

| Acción | Comando |
|--------|---------|
| Compilar todo | `python compile_and_run.py` |
| Demo automática | `cd models_venv && python launch_demo.py` |
| Levantar API sola | `cd api && uvicorn main:app --reload` |
| Ejecutar demo sola | `cd models_venv && python demo_game_blockchain.py` |
| Ejemplos básicos | `cd models_venv && python ejemplo_integracion.py` |
| Verificar setup | `python verify_setup.py` |
| Lanzador Windows | `RUN.bat` |

---

## 📚 DOCUMENTACIÓN

| Documento | Para |
|-----------|------|
| `DEMO_QUICK_START.md` | Inicio rápido de la demo |
| `BLOCKCHAIN_INTEGRATION.md` | Documentación técnica completa |
| `api/README.md` | Docs de la API |
| `models_venv/README_API.md` | Guía para modelos |
| `models_venv/DEMO_README.md` | Detalles de la demo |

---

## ✅ CHECKLIST FINAL

Antes de ejecutar, verifica:

- ✅ Python 3.8+ instalado
- ✅ `/contract/.env` tiene todas las variables
- ✅ Contrato deployado en Avalanche Testnet
- ✅ Tienes AVAX para gas fees en Fuji Testnet
- ✅ Ejecutaste `python compile_and_run.py`
- ✅ No hay errores en la compilación

---

## 🚀 AHORA SÍ, EJECUTA:

```powershell
# Opción A: Automático (RECOMENDADO)
python compile_and_run.py
cd models_venv
python launch_demo.py

# Opción B: Windows (doble click)
RUN.bat

# Opción C: Manual en dos terminales
# Terminal 1:
cd api
uvicorn main:app --reload --port 8000

# Terminal 2:
cd models_venv
python demo_game_blockchain.py
```

---

## 📞 ¿TODO LISTO?

Si tienes dudas:
1. Ejecuta: `python compile_and_run.py`
2. Lee el output - te dice exactamente qué falta
3. Consulta la documentación correspondiente

**¡Disfruta tu juego en blockchain! 🎮🚀**
