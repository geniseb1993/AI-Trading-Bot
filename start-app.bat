@echo off
echo Starting AI Trading Bot V2.0...
echo This script will start all necessary servers:
echo 1. Main application (app-starter.py)
echo 2. Dual Bot API server
echo 3. Frontend React app

REM Start the main application in a new window
start "AI Trading Bot Main" cmd /k "python app-starter.py"

REM Start the Dual Bot API server in a new window
start "Dual Bot API" cmd /k "python dual_bot/run_api.py"

echo.
echo All servers have been started. You should see three command windows:
echo 1. Main application window
echo 2. Dual Bot API server window
echo 3. Frontend React app window (started by app-starter.py)
echo.
echo To stop the application, close all command windows or press Ctrl+C in each window.
echo.
pause 