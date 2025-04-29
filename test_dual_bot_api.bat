@echo off
echo Running Dual Bot API Tests...
echo.
echo This script will test the following endpoints:
echo - /api/health
echo - /api/status
echo - /api/dual-bot/status
echo - /api/market-data/:symbol
echo - /api/options-data/:symbol
echo - /api/news/:symbol
echo - /api/dual-bot/signals
echo.
echo Make sure the dual bot API server is running!
echo.

python test_dual_bot_api.py

echo.
echo Test completed!
pause 