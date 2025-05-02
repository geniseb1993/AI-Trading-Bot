@echo off
echo Installing Dual Bot notification packages...

echo Installing discord-webhook package...
pip install discord-webhook>=1.3.0

echo Installing python-telegram-bot package...
pip install python-telegram-bot>=22.0

echo Notification packages installed successfully!
pause 