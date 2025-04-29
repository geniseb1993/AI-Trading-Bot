@echo off
echo Starting Dual Bot System...

REM Start the API server in a new window
start cmd /k "echo Starting Dual Bot API Server... && python dual_bot_api_server.py"

REM Give the API server a moment to start
timeout /t 3 /nobreak > nul

REM Start the frontend application in a new window
start cmd /k "echo Starting Frontend... && cd frontend && npm start"

echo Both services have been started. You can access the dashboard at:
echo http://localhost:3000/dual-bot
echo.
echo Note: If the API server fails to start, the frontend will use mock data automatically.
echo.
echo Press any key to exit this window...
pause > nul 