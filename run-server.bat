@echo off
echo Starting AI Trading Bot API Server...

rem Install any required packages
pip install flask flask_cors > nul 2>&1

rem Ensure we're using the minimal, reliable server
echo Starting minimal Flask server on port 5000...
python minimal_flask_server.py

rem If the server stops, keep the window open
pause 