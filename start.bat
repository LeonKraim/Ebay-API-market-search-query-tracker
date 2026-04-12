@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo  eBay Market Intelligence Platform  --  START
echo ============================================================
echo.

:: ── 1. Check Docker is available ──────────────────────────────
where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not found on PATH.
    echo         Install Docker Desktop: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

:: ── 2. Check .env exists (copy example if missing) ────────────
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [WARN] .env was missing -- copied from .env.example
        echo        Please open .env and set your secrets before continuing.
        echo.
        pause
    ) else (
        echo [ERROR] Neither .env nor .env.example found.
        echo         Create a .env file in the project root.
        echo.
        pause
        exit /b 1
    )
)

:: ── 3. Build and start all services in detached mode ──────────
echo [INFO] Building images and starting services (this may take a moment)...
docker compose up --build -d
if errorlevel 1 (
    echo [ERROR] docker compose up failed. Check the output above.
    pause
    exit /b 1
)
echo.

:: ── 4. Wait for backend health (max 60 s, poll every 2 s) ─────
echo [INFO] Waiting for backend to become healthy...
set /a ATTEMPTS=0
set /a MAX=30

:HEALTH_LOOP
if !ATTEMPTS! geq !MAX! (
    echo [WARN] Backend health check timed out after 60 s.
    echo        The stack is still starting -- try http://localhost:3000 in a moment.
    goto DONE
)
set /a ATTEMPTS+=1

:: Use PowerShell to do a silent HTTP GET (curl not always available on Windows)
powershell -NoProfile -Command "try { $r=(Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop).StatusCode; if($r -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    <nul set /p "=."
    timeout /t 2 /nobreak >nul
    goto HEALTH_LOOP
)

echo.
echo [OK]  Backend is healthy.

:DONE
echo.
echo ============================================================
echo  Stack is up!
echo.
echo   Frontend  ->  http://localhost:3000
echo   Backend   ->  http://localhost:8000
echo   API docs  ->  http://localhost:8000/docs
echo ============================================================
echo.
pause
endlocal
