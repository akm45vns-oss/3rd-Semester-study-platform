@echo off
title Semester OS Launcher
echo ===================================================
echo           Starting Semester OS Services
echo ===================================================
echo.

set PYTHON_EXE=C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe

echo [1/2] Launching Backend (FastAPI on Port 8000)...
start "Semester OS - Backend" cmd /c "cd /d ""%~dp0backend"" && ""%PYTHON_EXE%"" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Launching Frontend (Vite on Port 5173)...
timeout /t 2 /nobreak >nul
start "Semester OS - Frontend" cmd /c "cd /d ""%~dp0frontend"" && npm run dev"

echo.
echo ===================================================
echo   Services are running!
echo   Frontend : http://localhost:5173
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo ===================================================
echo.
timeout /t 3 /nobreak >nul
start http://localhost:5173
