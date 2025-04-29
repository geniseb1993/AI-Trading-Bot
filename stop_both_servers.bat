@echo off
echo Stopping AI Trading Bot Servers...

:: Find and kill the Python processes for our servers
:: This finds Python processes with the specific server names in their command line
for /f "tokens=2" %%p in ('tasklist /fi "imagename eq python.exe" /fo csv /nh') do (
    wmic process where "ProcessId=%%p" get CommandLine | findstr "simple_bot_management_server.py" > nul
    if not errorlevel 1 (
        echo Stopping Bot Management Server (PID: %%p)
        taskkill /pid %%p /f
    )
    
    wmic process where "ProcessId=%%p" get CommandLine | findstr "dual_bot_api_server.py" > nul
    if not errorlevel 1 (
        echo Stopping Main API Server (PID: %%p)
        taskkill /pid %%p /f
    )
)

echo Servers stopped successfully!
pause 