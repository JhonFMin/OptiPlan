@echo off
title OptiPlan
cd /d "%~dp0"
echo.
echo  Iniciando OptiPlan...
echo.
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERROR: Asegurate de tener Python instalado.
    echo  Descargalo en: https://www.python.org/downloads/
    echo  (Marca "Add Python to PATH" durante la instalacion)
    pause
)
