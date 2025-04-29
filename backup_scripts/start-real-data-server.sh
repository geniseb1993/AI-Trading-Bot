#!/bin/bash

echo "Starting AI Trading Bot API with REAL market data..."
echo ""

# Set Production Environment
export APP_ENV=production

# Kill any existing processes on port 5000
echo "Checking for existing processes on port 5000..."
PID=$(lsof -ti:5000)
if [ ! -z "$PID" ]; then
    echo "Stopping existing process $PID on port 5000..."
    kill -9 $PID
fi

# Start the API server
echo "Starting API server..."
python run_api.py > api_server.log 2>&1 &
API_PID=$!
echo "API server started with PID: $API_PID"

# Wait for the server to start
echo "Waiting for API server to start..."
sleep 5

# Run the data marker script
echo "Setting up real data markers..."
python fix_real_data_flag.py

echo ""
echo "API server started successfully with REAL market data!"
echo "Please restart the frontend to see the changes."
echo "API server is running with PID: $API_PID"
echo "Check api_server.log for server output" 