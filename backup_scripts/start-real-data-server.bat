@echo off
echo Starting AI Trading Bot with REAL DATA enabled...
echo.

:: Set Production Environment
set APP_ENV=production

:: Kill any existing processes on port 5000
for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000" ^| find "LISTENING"') do (
    echo Stopping existing process %%a on port 5000...
    taskkill /F /PID %%a 2>nul
)

:: Start the API server
echo Starting API server...
start /B python run_api.py

:: Wait for the server to start
echo Waiting for API server to start...
timeout /t 5 /nobreak > nul

:: Run the data marker script
echo Setting up real data markers...
python fix_real_data_flag.py

echo.
echo API server started successfully with REAL market data!
echo Please restart the frontend to see the changes.
echo Press any key to exit this window...
pause > nul

python fixed_server.py 