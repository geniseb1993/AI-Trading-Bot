@echo off
echo Bot Management API Test Suite
echo ============================
echo.

:menu
echo Select a test to run:
echo 1. Simple status check (simple_test_bot_status.py)
echo 2. Bot control test (test_bot_control.py)
echo 3. Full API test (test_bot_management_api.py)
echo 4. Exit
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto status
if "%choice%"=="2" goto control
if "%choice%"=="3" goto fulltest
if "%choice%"=="4" goto end

echo Invalid choice. Please try again.
echo.
goto menu

:status
echo.
echo Running bot status check...
python simple_test_bot_status.py
echo.
echo Test complete!
pause
goto menu

:control
echo.
echo Running bot control test...
python test_bot_control.py
echo.
echo Test complete!
pause
goto menu

:fulltest
echo.
echo Running full API test...
echo.
echo Select test mode:
echo 1. Test all bots
echo 2. Test specific bot
echo 3. Verbose mode (all bots)
echo 4. Back to main menu
echo.

set /p test_mode=Enter test mode (1-4): 

if "%test_mode%"=="1" (
    python test_bot_management_api.py
    echo.
    echo Test complete!
    pause
    goto menu
)

if "%test_mode%"=="2" (
    echo.
    echo Available bot types: autonomous_bot, rsi_bot, dual_bot
    set /p bot_type=Enter bot type to test: 
    python test_bot_management_api.py --bot %bot_type%
    echo.
    echo Test complete!
    pause
    goto menu
)

if "%test_mode%"=="3" (
    python test_bot_management_api.py --verbose
    echo.
    echo Test complete!
    pause
    goto menu
)

if "%test_mode%"=="4" (
    goto menu
)

echo Invalid choice. Please try again.
goto fulltest

:end
echo Exiting test suite...
exit 