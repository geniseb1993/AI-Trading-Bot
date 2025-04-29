#!/bin/bash

echo "============================================"
echo "    Cleaning up redundant startup scripts"
echo "============================================"

echo
echo "The following files will be removed:"
echo "- start-app.bat"
echo "- start-app.sh"
echo "- start-dual-bot.bat"
echo "- start-dual-bot.sh"
echo "- start-dual-bot-with-frontend.bat"
echo "- start-real-data-server.bat"
echo "- start-real-data-server.sh"
echo "- start-ui-with-api.js"
echo "- start-cron-server.js"
echo "- start-api.py"

echo
read -p "Are you sure you want to continue (Y/N)? " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Cleanup aborted."
    exit 0
fi

echo
echo "Creating backup directory..."
mkdir -p backup_scripts

echo "Moving redundant scripts to backup directory..."

# Move each file if it exists
for file in \
    "start-app.bat" \
    "start-app.sh" \
    "start-dual-bot.bat" \
    "start-dual-bot.sh" \
    "start-dual-bot-with-frontend.bat" \
    "start-real-data-server.bat" \
    "start-real-data-server.sh" \
    "start-ui-with-api.js" \
    "start-cron-server.js" \
    "start-api.py"
do
    if [ -f "$file" ]; then
        mv "$file" "backup_scripts/"
        echo "Moved $file to backup_scripts/"
    fi
done

echo
echo "============================================"
echo "Redundant startup scripts have been moved to backup_scripts directory."
echo "Please use the new unified startup scripts:"
echo "- start-app-unified.bat (Windows)"
echo "- start-app-unified.sh (Linux/macOS)"
echo
echo "See UNIFIED_STARTUP_README.md for details."
echo "============================================" 