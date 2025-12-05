@echo off
REM ============================================
REM RESUMEN FINAL - Catan Blockchain
REM ============================================

cls
echo.
echo ============================================
echo  CATAN + BLOCKCHAIN - RESUMEN FINAL
echo ============================================
echo.

python RESUMEN_FINAL.py

echo.
echo ============================================
echo  PROXIMOS PASOS
echo ============================================
echo.
echo 1. Verifica requisitos:
echo    - Python 3.8+
echo    - /contract/.env configurado
echo    - Contrato deployado en Avalanche
echo.
echo 2. Ejecuta:
echo    python compile_and_run.py
echo.
echo 3. Luego:
echo    cd models_venv
echo    python launch_demo.py
echo.
echo ============================================
pause
