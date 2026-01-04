@echo off
title Stonks by KG
color 0B

echo.
echo  ====================================
echo    Stonks by KG - Starting...
echo  ====================================
echo.

:: Start backend in new window
echo Starting Backend Server...
start "Stonks Backend" cmd /k "cd backend && python main.py"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend in new window
echo Starting Frontend...
start "Stonks Frontend" cmd /k "npm run dev"

:: Wait and open browser
timeout /t 5 /nobreak >nul

echo.
echo  Opening browser...
start http://localhost:5173

echo.
echo  ====================================
echo    Stonks by KG is running!
echo  ====================================
echo.
echo  Frontend: http://localhost:5173
echo  Backend:  http://localhost:5000
echo.
echo  Close this window to keep running.
echo  To stop, close the Backend and Frontend windows.
echo.

pause
