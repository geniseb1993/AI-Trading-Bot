#!/bin/bash

echo "============================================"
echo "      AI TRADING BOT - UNIFIED STARTUP"
echo "============================================"
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "ERROR: Python not found. Please install Python and try again."
    echo "Recommended version: Python 3.8 or higher"
    exit 1
fi

# Make the script executable if it isn't already
chmod +x start_all_servers.py

# Execute the unified server startup script
echo "Starting all servers using unified server script..."
echo ""
python start_all_servers.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Unified server startup failed. Check logs for details."
    exit 1
fi

# Note: The Python script keeps running and handles the server processes
# We should never reach here unless the Python script exits on its own
echo ""
echo "All servers should now be running."
echo "Press Ctrl+C in the Python script window to shut down all servers."
echo "" 