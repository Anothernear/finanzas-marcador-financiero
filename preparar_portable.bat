@echo off
setlocal enabledelayedexpansion
title Preparando Version Portable de Hermes Finanzas

echo ======================================================================
echo    CREANDO ENTORNO PORTABLE DE PYTHON (ZERO-INSTALL PARA WINDOWS)
echo ======================================================================
echo.
echo Este script descargara una copia independiente de Python y todas las
echo librerias necesarias dentro de la carpeta "python_portable".
echo.
echo NOTA: Solo necesitas ejecutar este paso UNA SOLA VEZ con conexion a Internet.
echo Una vez terminado, podras copiar toda la carpeta a una USB y funcionara
echo en cualquier computadora con Windows sin instalar nada ni requerir permisos.
echo.
pause

set "SCRIPT_DIR=%~dp0"
set "PORTABLE_DIR=%SCRIPT_DIR%python_portable"
set "PYTHON_ZIP_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "PYTHON_ZIP_FILE=%SCRIPT_DIR%python_embed.zip"
set "GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py"
set "GET_PIP_FILE=%SCRIPT_DIR%get-pip.py"

if exist "%PORTABLE_DIR%\python.exe" (
    echo.
    echo [*] Ya se detecto una instalacion de Python en "%PORTABLE_DIR%".
    echo Si deseas reinstalarla desde cero, elimina la carpeta "python_portable" y vuelve a ejecutar este script.
    goto INSTALAR_DEPENDENCIAS
)

echo.
echo [1/5] Descargando Python 3.11.9 Embeddable (aprox 25 MB)...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%PYTHON_ZIP_URL%', '%PYTHON_ZIP_FILE%')"
if errorlevel 1 (
    echo [ERROR] No se pudo descargar Python. Verifica tu conexion a internet.
    pause
    exit /b 1
)

echo [2/5] Extrayendo Python en "python_portable"...
if not exist "%PORTABLE_DIR%" mkdir "%PORTABLE_DIR%"
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP_FILE%' -DestinationPath '%PORTABLE_DIR%' -Force"
del "%PYTHON_ZIP_FILE%" >nul 2>&1

echo [3/5] Configurando soporte de modulos y librerias externas...
set "PTH_FILE=%PORTABLE_DIR%\python311._pth"
if exist "%PTH_FILE%" (
    powershell -Command "(Get-Content '%PTH_FILE%') -replace '^#import site', 'import site' | Set-Content '%PTH_FILE%'"
)

echo [4/5] Instalando gestor de paquetes pip...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GET_PIP_URL%', '%GET_PIP_FILE%')"
"%PORTABLE_DIR%\python.exe" "%GET_PIP_FILE%" --no-warn-script-location
del "%GET_PIP_FILE%" >nul 2>&1

:INSTALAR_DEPENDENCIAS
echo [5/5] Instalando librerias del proyecto (Streamlit, Pandas, Plotly, Barcode, etc.)...
"%PORTABLE_DIR%\python.exe" -m pip install --no-warn-script-location -r "%SCRIPT_DIR%requirements.txt"
if errorlevel 1 (
    echo.
    echo [ERROR] Ocurrio un problema al instalar las dependencias.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo    LISTO: TU APLICACION PORTABLE HA SIDO CREADA CON EXITO
echo ======================================================================
echo.
echo Ya puedes iniciar la aplicacion haciendo doble clic en:
echo      EJECUTAR_PROYECTO.bat
echo.
echo Para compartirla o llevarla en una USB:
echo Simplemente copia esta carpeta completa (con su carpeta 'python_portable').
echo En la otra PC solo tendran que abrir "EJECUTAR_PROYECTO.bat".
echo.
pause
