@echo off
title Stonks by KG - Setup
color 0A

echo.
echo  ====================================
echo    Stonks by KG - One Click Setup
echo  ====================================
echo.

:: Check Python
echo [1/5] Checking Python...
py -3 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo       Python found!

:: Check Node.js
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found! Please install Node.js 16+
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)
echo       Node.js found!

:: Install Python dependencies
echo [3/5] Installing Python dependencies...
cd backend
py -3 -m pip install -r requirements.txt --quiet
cd ..
echo       Python dependencies installed!

:: Install Node dependencies
echo [4/5] Installing Node.js dependencies...
call npm install --silent
echo       Node.js dependencies installed!

echo.
echo  ====================================
echo    Setup Complete!
echo  ====================================
echo.
echo  To start the application, run: start.bat
echo.

pause
