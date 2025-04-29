#!/bin/bash

echo "============================================"
echo "      AI Trading Bot Unified Startup"
echo "============================================"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "ERROR: Python not found. Please install Python and try again."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found. Please install Node.js and try again."
    exit 1
fi

echo
echo "Step 1: Checking and starting the Dual Bot API server..."

# Run the fix script to ensure the API server is running
# First check if the fix script exists, if not, use the server directly
if [ -f "fix-dual-bot-api.py" ]; then
    python fix-dual-bot-api.py
else
    # If fix script doesn't exist, try to start the server directly
    echo "fix-dual-bot-api.py not found, starting server directly..."
    python dual_bot_api_server.py &
fi

# Wait a moment for the server to start
sleep 3

# Try to check if the server is running
if ! curl -s http://localhost:5001/api/health > /dev/null; then
    echo "ERROR: Failed to start Dual Bot API server."
    echo "Please check logs for more details."
    exit 1
fi

echo
echo "Step 2: Starting frontend application on port 3001..."

# Check if we're in the correct directory
if [ ! -f "frontend/package.json" ]; then
    echo "ERROR: frontend directory not found or missing package.json"
    echo "Make sure you're running this script from the main project directory."
    exit 1
fi

# Start the frontend on port 3001
cd frontend
PORT=3001 npm start &
cd ..

echo
echo "============================================"
echo "AI Trading Bot system started successfully!"
echo
echo "API Server: http://localhost:5001/api/health"
echo "Frontend: http://localhost:3001"
echo
echo "NOTE: The system is now running in the background."
echo "To stop the system, use 'pkill -f node' and 'pkill -f python'"
echo "============================================" 