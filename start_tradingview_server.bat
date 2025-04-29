@echo off
REM Start TradingView Integration Server on port 5003

echo Starting TradingView Integration Server...
set TRADINGVIEW_PORT=5003
python tradingview_server.py

if %ERRORLEVEL% NEQ 0 (
    echo Failed to start TradingView Integration Server
    exit /b %ERRORLEVEL%
)

echo TradingView Integration Server running on port 5003
echo Press Ctrl+C to stop the server...

echo Test endpoints:
echo - http://localhost:5003/api/test
echo - http://localhost:5003/api/tradingview/alerts
echo - http://localhost:5003/api/tradingview/symbols/technical-data?symbol=SPY
echo - http://localhost:5003/api/tradingview/market/analysis 