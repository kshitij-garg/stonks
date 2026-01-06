@echo off
title Stonks by KG
color 0B
setlocal enabledelayedexpansion

echo.
echo  ====================================
echo    Stonks by KG - Starting...
echo  ====================================
echo.

:: Check if Python is available
echo [1/4] Checking Python...
py -3 --version >nul 2>&1
if %errorlevel% neq 0 (
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        color 0C
        echo [ERROR] Python not found!
        echo Please install Python 3.8+ from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py -3
)
echo       Python found: !PYTHON_CMD!

:: Check if Node.js is available
echo [2/4] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Node.js not found!
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)
echo       Node.js found!

:: Check if backend folder exists
if not exist "backend\main.py" (
    color 0C
    echo [ERROR] backend\main.py not found!
    echo Please run this script from the Stonks project root folder.
    pause
    exit /b 1
)

:: Check if port 5000 is already in use
netstat -an | findstr ":5000.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARN] Port 5000 is already in use. Backend may already be running.
) else (
    echo [3/4] Starting Backend Server...
    start "Stonks Backend" cmd /k "cd backend && !PYTHON_CMD! main.py"
    timeout /t 4 /nobreak >nul
)

:: Check if port 5173 is already in use
netstat -an | findstr ":5173.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARN] Port 5173 is already in use. Frontend may already be running.
) else (
    echo [4/4] Starting Frontend...
    start "Stonks Frontend" cmd /k "npm run dev"
    timeout /t 5 /nobreak >nul
)

:: Verify backend is responding
echo.
echo Verifying backend connection...
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -TimeoutSec 5 -ErrorAction Stop } catch { exit 1 }" >nul 2>&1
)
if %errorlevel% neq 0 (
    color 0E
    echo [WARN] Backend may still be starting up. Wait a few seconds...
) else (
    echo       Backend is responding!
)

:: Open browser
echo.
echo Opening browser...
start http://localhost:5173

echo.
color 0A
echo  ====================================
echo    Stonks by KG is running!
echo  ====================================
echo.
echo  Frontend: http://localhost:5173
echo  Backend:  http://localhost:5000
echo.
echo  Closing launcher in 3 seconds...
echo.

timeout /t 3 /nobreak >nul
exit
