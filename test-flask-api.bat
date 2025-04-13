@echo off
echo Testing Flask API Server...
echo.

cd api
echo Installing required packages...
pip install flask flask-cors pandas
echo.

echo Starting Flask server in debug mode...
python -u app.py
echo.

pause 