@echo off
echo Starting Dual Bot API Server...
echo.
echo This server provides the following endpoints:
echo - /api/health - API health check endpoint
echo - /api/status - Get the status of the dual bot
echo - /api/dual-bot/status - Dedicated dual bot status endpoint
echo - /api/market-data/:symbol - Get market data for a specific symbol
echo - /api/options-data/:symbol - Get options data for a specific symbol
echo - /api/news/:symbol - Get news for a specific symbol
echo - /api/dual-bot/signals - Get trading signals from the dual bot
echo.
echo Press Ctrl+C to stop the server
echo.

python dual_bot_api_server.py 