@echo off
echo Starting AI Trading Bot API Server Directly...

REM Set the Python path to include the necessary directories
set PYTHONPATH=%CD%;%CD%\api;%CD%\execution_model

REM Change to the API directory
cd api

REM Run the Flask application directly 
python app.py

REM If the application exits with an error, pause to see the error
if %ERRORLEVEL% NEQ 0 (
    echo Flask application exited with error code: %ERRORLEVEL%
    echo Press any key to exit...
    pause > nul
) 