@echo off
setlocal
title Hermes - Marcador Financiero

set "SCRIPT_DIR=%~dp0"
set "PORTABLE_PYTHON=%SCRIPT_DIR%python_portable\python.exe"

if not exist "%PORTABLE_PYTHON%" (
    echo ======================================================================
    echo  [AVISO] No se ha encontrado el entorno portable de Python.
    echo ======================================================================
    echo.
    echo Por favor, ejecuta primero el archivo "preparar_portable.bat" para
    echo descargar y configurar los componentes portables automaticamente.
    echo.
    pause
    exit /b 1
)

echo Iniciando aplicacion Hermes Marcador Financiero...
echo Abriendo en tu navegador...
echo (Para cerrar la aplicacion, simplemente cierra esta ventana de comandos)
echo.

"%PORTABLE_PYTHON%" -m streamlit run "%SCRIPT_DIR%proyecto.py" --server.headless=false --browser.gatherUsageStats=false

if errorlevel 1 (
    echo.
    echo [ERROR] La aplicacion se cerro inesperadamente.
    pause
)
