#!/bin/bash
echo "Stopping AI Trading Bot V2.0..."
echo "This script will terminate all application components."

python3 app-cleanup.py

echo ""
echo "If any processes are still running, you may need to close them manually."
echo "" 