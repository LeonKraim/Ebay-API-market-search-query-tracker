@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo  eBay Market Intelligence Platform  --  CLEAR ALL DATA
echo ============================================================
echo.
echo  WARNING: This will permanently delete:
echo    - All PostgreSQL data (tables, rows, schema)
echo    - All application log files
echo.
set /p CONFIRM="  Continue? (y/n): "
if /i not "!CONFIRM!"=="y" (
    echo.
    echo [ABORT] No data was deleted.
    echo.
    pause
    exit /b 0
)

echo.

:: ── 1. Stop containers and remove named volumes ───────────────
echo [INFO] Stopping containers and removing volumes...
docker compose down -v
if errorlevel 1 (
    echo [WARN] docker compose down returned non-zero. Continuing anyway.
)
echo.

:: ── 2. Clear log files (keep the logs\ directory) ─────────────
if exist "logs\" (
    echo [INFO] Clearing logs\ directory...
    for /f "delims=" %%f in ('dir /b /a-d "logs\*" 2^>nul') do (
        del /q "logs\%%f" >nul 2>&1
    )
    echo [OK]  Logs cleared.
) else (
    echo [INFO] logs\ directory not found -- nothing to clear.
)

echo.
echo ============================================================
echo  All data cleared.
echo  Run start.bat to bring the stack back up with a fresh DB.
echo ============================================================
echo.
pause
endlocal
