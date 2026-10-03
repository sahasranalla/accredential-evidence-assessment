@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title ACCREDIA - AI-Powered Accreditation Evidence Assistant

echo ========================================================
echo   ACCREDIA - Accreditation Evidence OS
echo   Vidyapath Institute of Technology (VITEC)
echo ========================================================
echo Project: %CD%
echo.

REM 1. Python Check
python --version >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python is not installed or not in PATH. Install Python 3.10+ and try again.
  pause
  exit /b 1
)
echo [1/4] Python verified.

REM 2. Backend Packages
echo [2/4] Verifying backend dependencies...
python -c "import uvicorn,fastapi,fitz,docx,faiss" >nul 2>&1
if errorlevel 1 (
  echo Installing required packages (fastapi, uvicorn, pymupdf, python-docx, faiss-cpu, etc.)...
  python -m pip install -r requirements.txt
) else (
  echo Backend packages ready.
)

REM 3. Frontend Packages
if not exist "frontend\node_modules" (
  echo [3/4] Installing frontend dependencies (Vite, React, Lucide, React Flow)...
  pushd frontend
  call npm install
  popd
) else (
  echo [3/4] Frontend packages ready.
)

REM 4. Launch Backend
echo [4/4] Starting ACCREDIA Backend: http://127.0.0.1:8000
start "ACCREDIA Backend" "%ComSpec%" /k "cd /d ""%~dp0"" && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo Waiting for backend to initialize...
set BACKEND_READY=
for /l %%i in (1,1,30) do (
  powershell -NoProfile -Command "try {$r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/health -TimeoutSec 1;if($r.StatusCode -eq 200){exit 0}else{exit 1}}catch{exit 1}" >nul 2>&1
  if not errorlevel 1 set BACKEND_READY=1&goto backend_ok
  timeout /t 1 /nobreak >nul
)
:backend_ok
if defined BACKEND_READY (echo Backend operational.) else echo WARNING: Backend took longer to start. Check ACCREDIA Backend terminal.

REM 5. Launch Frontend
start "ACCREDIA Frontend" "%ComSpec%" /k "cd /d ""%~dp0frontend"" && npm run dev -- --host 127.0.0.1"

echo Waiting for frontend...
set FRONT_READY=
for /l %%i in (1,1,30) do (
  powershell -NoProfile -Command "try {$r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173 -TimeoutSec 1;if($r.StatusCode -eq 200){exit 0}else{exit 1}}catch{exit 1}" >nul 2>&1
  if not errorlevel 1 set FRONT_READY=1&goto frontend_ok
  timeout /t 1 /nobreak >nul
)
:frontend_ok
if defined FRONT_READY (
  echo Frontend ready. Opening browser...
  start "" "http://127.0.0.1:5173"
) else (
  echo Starting browser...
  start "" "http://127.0.0.1:5173"
)

echo.
echo ========================================================
echo   ACCREDIA is running!
echo   Frontend : http://127.0.0.1:5173
echo   Backend  : http://127.0.0.1:8000
echo   Swagger  : http://127.0.0.1:8000/docs
echo ========================================================
echo Keep the Backend and Frontend windows open while running.
endlocal
