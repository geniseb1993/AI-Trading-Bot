@echo off
echo Starting AI Trading Bot servers...
echo.

echo Starting Flask backend server...
start "Flask Backend" cmd /k "cd api && python app.py"

echo Starting React frontend server...
start "React Frontend" cmd /k "cd frontend && npm start"

echo.
echo Servers are starting in separate windows.
echo - Flask backend: http://localhost:5000
echo - React frontend: http://localhost:3000
echo.
echo The servers are running in their own windows.
echo To stop the servers, close their respective command windows.
echo.
echo Press any key to exit this script...
pause > nul 