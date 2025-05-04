#!/bin/bash
# Mac-specific startup script for AI Trading Bot

echo "==============================================="
echo "  AI Trading Bot - Mac Startup Script"
echo "==============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    echo "Please install Python 3 from https://www.python.org/downloads/mac-osx/"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Flask with compatible version for Mac/Safari
echo "Installing compatible Flask versions..."
pip install flask==2.0.1 werkzeug==2.0.1 flask-cors==3.0.10 markupsafe==2.0.1 jinja2==3.0.3 itsdangerous==2.0.1

# Create required directories
echo "Creating required directories..."
mkdir -p data/dashboard data/broker data/logs data/signals data/market_data instance

# Kill existing processes on the required ports
echo "Checking for processes on required ports..."
for PORT in 5001 5002 5003 3001; do
    # Find process using port and kill it
    PID=$(lsof -t -i:$PORT)
    if [ ! -z "$PID" ]; then
        echo "Killing process $PID using port $PORT..."
        kill -9 $PID
    fi
done

# Set environment variables for Safari compatibility
export FLASK_APP=dual_bot_api_server.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Special environment variable for Safari compatibility
export SAFARI_COMPATIBLE=1

# Start the servers
echo "Starting API server..."
python start_unified.py

echo "All servers should now be running."
echo "Access the application at: http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop all servers." 