@echo off
echo ============================================
echo      AI Trading Bot Unified Startup
echo ============================================

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python and try again.
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js not found. Please install Node.js and try again.
    pause
    exit /b 1
)

echo.
echo Step 1: Checking and starting the Dual Bot API server...
REM Run the fix script to ensure the API server is running
python fix-dual-bot-api.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start Dual Bot API server.
    echo Please check the fix-dual-bot-api.log file for details.
    pause
    exit /b 1
)

echo.
echo Step 2: Verifying API connectivity...
node test_dual_bot_connectivity.js

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: API connectivity test showed issues.
    echo You can run the connectivity fixer to diagnose and fix problems:
    echo node fix-api-connectivity.js
    echo.
    echo Press any key to continue anyway, or Ctrl+C to exit.
    pause >nul
)

echo.
echo Step 3: Starting frontend application on port 3001...

REM Check if we're in the correct directory
if not exist "frontend\package.json" (
    echo ERROR: frontend directory not found or missing package.json
    echo Make sure you're running this script from the main project directory.
    pause
    exit /b 1
)

REM Start the frontend on port 3001
cd frontend
start cmd /k "echo Starting frontend application on port 3001... && set PORT=3001 && npm start"
cd ..

echo.
echo ============================================
echo AI Trading Bot system started successfully!
echo.
echo API Server: http://localhost:5001/api/health
echo Frontend: http://localhost:3001
echo.
echo NOTE: The system is now running in separate windows.
echo To stop the system, close all terminal windows.
echo.
echo For API connectivity issues, run: node fix-api-connectivity.js
echo For more information, see: API_CONNECTIVITY_README.md
echo ============================================

pause 