@echo off
echo Cleaning up redundant startup scripts...
echo.

REM Create backup directory if it doesn't exist
if not exist backup_scripts mkdir backup_scripts

REM Move redundant scripts to backup directory
if exist start_all_servers.py move start_all_servers.py backup_scripts\
if exist start_server_debug.py move start_server_debug.py backup_scripts\
if exist start_servers_simplified.py move start_servers_simplified.py backup_scripts\
if exist run-app.py move run-app.py backup_scripts\
if exist start-app-unified.bat move start-app-unified.bat backup_scripts\
if exist fix-dual-bot-api.py move fix-dual-bot-api.py backup_scripts\
if exist start-cron-server.js move start-cron-server.js backup_scripts\
if exist run-api-direct.bat move run-api-direct.bat backup_scripts\
if exist run-api-server.bat move run-api-server.bat backup_scripts\
if exist run-flask.bat move run-flask.bat backup_scripts\
if exist run-react.bat move run-react.bat backup_scripts\
if exist run-server.bat move run-server.bat backup_scripts\

echo Redundant startup scripts have been moved to backup_scripts/
echo All servers can now be started using start_unified.py or start-app.bat
echo.
pause 