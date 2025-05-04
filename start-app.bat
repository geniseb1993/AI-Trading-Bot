@echo off
echo Starting AI Trading Bot...
echo.

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not found. Please install Python and try again.
    pause
    exit /b 1
)

REM Try to run using the virtual environment first
if exist .venv\Scripts\python.exe (
    echo Using virtual environment...
    .venv\Scripts\python start_unified.py
) else (
    echo Virtual environment not found. Using system Python...
    python start_unified.py
)

pause 