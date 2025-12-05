@echo off
REM ============================================
REM COMPILADOR Y LANZADOR - Catan Blockchain
REM ============================================

echo.
echo ============================================
echo  COMPILADOR Y LANZADOR - CATAN BLOCKCHAIN
echo ============================================
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado
    echo Instala Python desde: https://www.python.org
    pause
    exit /b 1
)

echo [1] Compilando y verificando proyecto...
python compile_and_run.py

if errorlevel 1 (
    echo.
    echo ERROR: Compilacion fallida
    pause
    exit /b 1
)

echo.
echo ============================================
echo  SELECCIONA UNA OPCION
echo ============================================
echo.
echo [A] Ejecutar TODO automaticamente (RECOMENDADO)
echo [B] Ver instrucciones para dos terminales
echo [S] Salir
echo.

set /p choice="Elige (A/B/S): "

if /i "%choice%"=="A" (
    echo.
    echo Levantando demo automaticamente...
    cd models_venv
    python launch_demo.py
    pause
) else if /i "%choice%"=="B" (
    echo.
    echo Terminal 1 (API):
    echo   cd api
    echo   uvicorn main:app --reload --port 8000
    echo.
    echo Terminal 2 (Demo):
    echo   cd models_venv
    echo   python demo_game_blockchain.py
    echo.
    pause
) else (
    echo Saliendo...
    exit /b 0
)
