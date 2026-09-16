@echo off
title QuantRebalance - Institutional Portfolio Rebalancer
color 0B
setlocal enabledelayedexpansion

echo.
echo  =============================================================
echo    QuantRebalance - Institutional Portfolio Engine
echo  =============================================================
echo.

:: Detect Python
echo [1/3] Detecting Python environment...
py -3.14 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.14
    goto :PYTHON_FOUND
)

py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3
    goto :PYTHON_FOUND
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :PYTHON_FOUND
)

color 0C
echo [ERROR] Python not found! Please install Python 3.8+ from https://www.python.org/
pause
exit /b 1

:PYTHON_FOUND
echo       Found Python: !PYTHON_CMD!

:: Check if port 5000 is already running
netstat -an | findstr ":5000.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [2/3] Server already running on port 5000.
) else (
    echo [2/3] Starting QuantRebalance Backend on http://127.0.0.1:5000...
    start "QuantRebalance Server" cmd /k "!PYTHON_CMD! app.py"
    timeout /t 3 /nobreak >nul
)

:: Open Browser
echo [3/3] Opening QuantRebalance Terminal in your browser...
start http://127.0.0.1:5000

echo.
color 0A
echo  =============================================================
echo    QuantRebalance is live!
echo    URL: http://127.0.0.1:5000
echo  =============================================================
echo.
timeout /t 3 /nobreak >nul
exit
