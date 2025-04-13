@echo off
echo Starting AI Trading Bot servers...

rem Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo Python not found! Please install Python and try again.
  pause
  exit /b 1
)

rem Check if Node.js is installed
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo Node.js not found! Please install Node.js and try again.
  pause
  exit /b 1
)

echo.
echo Starting Flask backend server...
echo.

rem Open a new command prompt window for the Flask backend with verbose output
start cmd /k "cd api && echo Installing required Python packages... && pip install flask flask-cors pandas && echo. && echo Starting Flask server... && python -u app.py"

rem Wait 5 seconds for Flask to start
echo Waiting for Flask server to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting React frontend server...
echo.

rem Open a new command prompt window for the React frontend
start cmd /k "cd frontend && echo Installing required npm packages... && npm install && echo. && echo Starting React app... && npm start"

echo.
echo Servers starting. Check the new command prompt windows for details.
echo - Flask backend: http://localhost:5000
echo - React frontend: http://localhost:3000
echo.
echo If you encounter API connection errors:
echo 1. Make sure Flask started successfully in its window
echo 2. Try running Flask directly: cd api && python app.py
echo 3. Check for any Python import errors in the Flask window
echo.

rem Keep this window open for easy shutdown
echo Press any key to shut down both servers...
pause > nul

rem Kill the servers when the user presses a key
taskkill /f /im node.exe > nul 2>&1
taskkill /f /im python.exe > nul 2>&1

echo Servers shut down.
timeout /t 2 > nul 