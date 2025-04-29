@echo off
echo Starting AI Trading Bot V2.0...

REM First, verify all API connections
echo Verifying API connections and environment...
python verify_api_connections.py
if %ERRORLEVEL% NEQ 0 (
  echo API connection verification failed. Please check your setup.
  echo You can still continue, but some features may use mock data.
  echo.
  echo Press any key to continue anyway, or Ctrl+C to abort...
  pause > nul
)

REM Fix the Hume Voice Service issue
echo Fixing Hume Voice Service...
python fix_hume_voice.py
if %ERRORLEVEL% NEQ 0 (
  echo Failed to fix Hume Voice Service. Continuing with limited functionality.
)

REM Ensure the execution_model is copied to the API directory
echo Syncing execution_model to API directory...
robocopy execution_model api\execution_model /E /IS /NP /NDL /NFL

REM Start the enhanced API server
echo Starting API server in a separate window...
start cmd /k "title API Server && python minimal_flask_server.py"

REM Wait for the API to start
echo Waiting for API to start (15 seconds)...
timeout /t 15 /nobreak

REM Test the API connection before continuing
echo Testing API connection...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/test' -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host 'API server is running!' -ForegroundColor Green } else { Write-Host 'API server responded with status:' $response.StatusCode -ForegroundColor Yellow } } catch { Write-Host 'Failed to connect to API server. Starting minimal fallback server...' -ForegroundColor Red; start cmd /k 'title API Fallback Server && python simple_flask_test.py' }"

REM Start the React frontend
echo Starting React frontend...
cd frontend
start cmd /k "npm start"

echo.
echo All servers started. You can access the application at:
echo - Frontend: http://localhost:3000
echo - API: http://localhost:5000
echo.
echo Press any key to stop all servers...
pause > nul

REM Kill servers when user presses a key
taskkill /f /im node.exe > nul 2>&1
taskkill /f /im python.exe > nul 2>&1
echo Servers stopped. 