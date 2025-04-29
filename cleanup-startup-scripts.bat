@echo off
echo ============================================
echo    Cleaning up redundant startup scripts
echo ============================================

echo.
echo The following files will be removed:
echo - start-app.bat
echo - start-app.sh
echo - start-dual-bot.bat
echo - start-dual-bot.sh
echo - start-dual-bot-with-frontend.bat
echo - start-real-data-server.bat
echo - start-real-data-server.sh
echo - start-ui-with-api.js
echo - start-cron-server.js
echo - start-api.py

echo.
set /p CONFIRM=Are you sure you want to continue (Y/N)? 
if /i "%CONFIRM%" NEQ "Y" (
    echo Cleanup aborted.
    exit /b 0
)

echo.
echo Creating backup directory...
if not exist "backup_scripts" mkdir backup_scripts

echo Moving redundant scripts to backup directory...

REM Move each file if it exists
if exist "start-app.bat" move "start-app.bat" "backup_scripts\"
if exist "start-app.sh" move "start-app.sh" "backup_scripts\"
if exist "start-dual-bot.bat" move "start-dual-bot.bat" "backup_scripts\"
if exist "start-dual-bot.sh" move "start-dual-bot.sh" "backup_scripts\"
if exist "start-dual-bot-with-frontend.bat" move "start-dual-bot-with-frontend.bat" "backup_scripts\"
if exist "start-real-data-server.bat" move "start-real-data-server.bat" "backup_scripts\"
if exist "start-real-data-server.sh" move "start-real-data-server.sh" "backup_scripts\"
if exist "start-ui-with-api.js" move "start-ui-with-api.js" "backup_scripts\"
if exist "start-cron-server.js" move "start-cron-server.js" "backup_scripts\"
if exist "start-api.py" move "start-api.py" "backup_scripts\"

echo.
echo ============================================
echo Redundant startup scripts have been moved to backup_scripts directory.
echo Please use the new unified startup scripts:
echo - start-app-unified.bat (Windows)
echo - start-app-unified.sh (Linux/macOS)
echo.
echo See UNIFIED_STARTUP_README.md for details.
echo ============================================

pause 