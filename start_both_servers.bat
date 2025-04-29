@echo off
echo Starting AI Trading Bot Servers...

:: Start the bot management server (in a new window)
start "Bot Management Server" cmd /c "python simple_bot_management_server.py"

:: Wait a moment to ensure the bot management server is up
timeout /t 3

:: Start the main dual bot API server
start "Main API Server" cmd /c "python dual_bot_api_server.py"

echo Both servers started successfully!
echo Main API Server: http://localhost:5001
echo Bot Management Server: http://localhost:5002

echo You can now access the Bot Management interfaces without timeout errors.
pause 