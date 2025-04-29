@echo off
echo ============================================
echo       AI TRADING BOT - UNIFIED STARTUP
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python and try again.
    echo Recommended version: Python 3.8 or higher
    pause
    exit /b 1
)

REM Execute the unified server startup script
echo Starting all servers using unified server script...
echo.
python start_all_servers.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Unified server startup failed. Check logs for details.
    pause
    exit /b 1
)

echo.
echo All servers should now be running.
echo Press Ctrl+C in the Python script window to shut down all servers.
echo.
pause 