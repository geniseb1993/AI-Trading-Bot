@echo off
echo Stopping AI Trading Bot server...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    echo Found server process with PID: %%a
    taskkill /F /PID %%a
    echo Server stopped.
)
echo Done. 