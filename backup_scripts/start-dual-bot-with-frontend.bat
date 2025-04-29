@echo off
echo ============================================
echo Starting Dual Bot System with Frontend
echo ============================================

REM First, run the fix script to ensure the dual bot API server is running
echo Step 1: Checking and starting the Dual Bot API server...
python fix-dual-bot-api.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start Dual Bot API server.
    echo Please check the fix-dual-bot-api.log file for details.
    pause
    exit /b 1
)

echo.
echo Step 2: Starting frontend application...

REM Check if we're in the correct directory
if not exist "frontend\package.json" (
    echo ERROR: frontend directory not found or missing package.json
    echo Make sure you're running this script from the main project directory.
    pause
    exit /b 1
)

REM Start the frontend (use start to open a new command window)
cd frontend
start cmd /k "echo Starting frontend application... && npm start"
cd ..

echo.
echo ============================================
echo Dual Bot System with Frontend is starting...
echo.
echo API Server: http://localhost:5001/api/health
echo Frontend: http://localhost:3000
echo.
echo If you experience any issues, try running fix-dual-bot-api.bat first.
echo ============================================

pause 