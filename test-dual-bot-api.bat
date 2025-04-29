@echo off
echo Starting Dual Bot API Comprehensive Test...
python test_dual_bot_comprehensive.py
if %ERRORLEVEL% EQU 0 (
    echo Test completed successfully!
) else (
    echo Test completed with errors. Check the log file for details.
)
pause 