# Semester OS PowerShell Launcher
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "          Starting Semester OS Services" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$pythonExe = "C:\Users\akm45\AppData\Local\Programs\Python\Python311\python.exe"
$scriptDir = $PSScriptRoot

Write-Host "[1/2] Launching Backend on Port 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\backend'; & '$pythonExe' -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 2

Write-Host "[2/2] Launching Frontend on Port 5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\frontend'; npm run dev"

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Semester OS running at http://localhost:5173" -ForegroundColor Yellow
Start-Process "http://localhost:5173"
