@echo off
echo Starting AI Trading Bot V2.0 (Quick Start)...

REM Install required packages silently
echo Installing required packages...
pip install flask flask_cors python-dotenv requests > nul 2>&1

REM Start the enhanced API server
echo Starting API server...
start cmd /k "title API Server && python minimal_flask_server.py"

REM Wait for the API to start
echo Waiting for API to start...
timeout /t 10 /nobreak

REM Start the React frontend
echo Starting React frontend...
cd frontend
start cmd /k "npm start"

echo.
echo Servers are starting up! You can access the application at:
echo - Frontend: http://localhost:3000
echo - API: http://localhost:5000
echo.
echo If you encounter connection errors, try running:
echo   .\verify_api_connections.py
echo   .\start-all.bat
echo.
echo Press any key to stop all servers...
pause > nul

REM Kill servers when user presses a key
taskkill /f /im node.exe > nul 2>&1
taskkill /f /im python.exe > nul 2>&1
echo Servers stopped. 