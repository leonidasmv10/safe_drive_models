@echo off
REM ===================================================================
REM Script de instalación para Safe Drive Models
REM Este script configura un entorno virtual de Python 3.11 y 
REM instala todas las dependencias necesarias para ejecutar los modelos
REM ===================================================================

echo [INFO] Iniciando configuración del entorno para Safe Drive Models...

REM Actualizar pip a la última versión
echo [1/5] Actualizando pip a la última versión...
py -3.11 -m pip install --upgrade pip

REM Instalar virtualenv si no está disponible
echo [2/5] Instalando virtualenv...
py -3.11 -m pip install virtualenv

REM Crear un entorno virtual llamado 'env'
echo [3/5] Creando entorno virtual...
py -3.11 -m venv env

REM Activar el entorno virtual
echo [4/5] Activando entorno virtual...
call .\env\Scripts\activate

REM Instalar las dependencias desde requirements.txt
echo [5/5] Instalando dependencias del proyecto...
pip install -r requirements.txt

echo [SUCCESS] Instalación completada correctamente!
echo.
pause