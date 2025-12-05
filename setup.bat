@echo off
REM Script de setup rápido para la integración API + Blockchain

echo.
echo ============================================
echo  Catan Blockchain - Setup Integración
echo ============================================
echo.

REM 1. Setup API
echo [1/4] Instalando dependencias de API...
cd api
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias de API
    exit /b 1
)
cd ..

REM 2. Setup Models
echo.
echo [2/4] Instalando requests en models_venv...
cd models_venv
pip install requests
if %errorlevel% neq 0 (
    echo ❌ Error instalando requests
    exit /b 1
)
cd ..

REM 3. Verificar estructura
echo.
echo [3/4] Verificando archivos...
if not exist "api\main.py" (
    echo ❌ api\main.py no encontrado
    exit /b 1
)
if not exist "models_venv\trade_client.py" (
    echo ❌ models_venv\trade_client.py no encontrado
    exit /b 1
)
if not exist "contract\scripts\API.py" (
    echo ❌ contract\scripts\API.py no encontrado
    exit /b 1
)

echo ✅ Archivos verificados

REM 4. Resumen
echo.
echo [4/4] Setup completado!
echo.
echo ============================================
echo  PRÓXIMOS PASOS
echo ============================================
echo.
echo 1. Abre DOS TERMINALES:
echo.
echo    TERMINAL 1 (levanta la API):
echo    $ cd api
echo    $ uvicorn main:app --reload --port 8000
echo.
echo    TERMINAL 2 (simula los modelos):
echo    $ cd models_venv
echo    $ python trade_client.py
echo.
echo 2. Usa trade_client.py en tus modelos:
echo    from trade_client import enviar_trade
echo    resultado = enviar_trade("MODELO_A", "MODELO_B", [{"id": 1, "cantidad": 5}])
echo.
echo ============================================
echo.
pause
