#!/bin/bash

echo "Cleaning up redundant startup scripts..."
echo

# Create backup directory if it doesn't exist
mkdir -p backup_scripts

# Move redundant scripts to backup directory
[ -f start_all_servers.py ] && mv start_all_servers.py backup_scripts/
[ -f start_server_debug.py ] && mv start_server_debug.py backup_scripts/
[ -f start_servers_simplified.py ] && mv start_servers_simplified.py backup_scripts/
[ -f run-app.py ] && mv run-app.py backup_scripts/
[ -f fix-dual-bot-api.py ] && mv fix-dual-bot-api.py backup_scripts/
[ -f start-cron-server.js ] && mv start-cron-server.js backup_scripts/
[ -f start-app-unified.sh ] && mv start-app-unified.sh backup_scripts/
[ -f run-api-direct.sh ] && mv run-api-direct.sh backup_scripts/
[ -f run-api-server.sh ] && mv run-api-server.sh backup_scripts/
[ -f run-flask.sh ] && mv run-flask.sh backup_scripts/
[ -f run-react.sh ] && mv run-react.sh backup_scripts/
[ -f run-server.sh ] && mv run-server.sh backup_scripts/

echo "Redundant startup scripts have been moved to backup_scripts/"
echo "All servers can now be started using start_unified.py or start-app.sh"
echo

# Make the new script executable
chmod +x start-app.sh

echo "Done!" 