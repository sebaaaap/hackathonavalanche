@echo off
echo ========================================
echo   CATAN BLOCKCHAIN - INICIAR SERVIDORES
echo ========================================
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

echo [1/2] Iniciando FastAPI (puerto 8000)...
start "FastAPI - Blockchain" cmd /k "cd api && uvicorn main:app --reload --port 8000"
timeout /t 2 /nobreak >nul

echo [2/2] Iniciando Flask API (puerto 5001)...
start "Flask API - Frontend" cmd /k "cd contract\scripts && python API.py"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   SERVIDORES INICIADOS
echo ========================================
echo.
echo FastAPI (blockchain):  http://127.0.0.1:8000
echo Flask API (frontend):  http://127.0.0.1:5001
echo.
echo Para ejecutar el demo:
echo   cd models_venv
echo   python demo_game_blockchain.py
echo.
echo Presiona cualquier tecla para salir...
pause >nul
