#!/bin/bash
echo "Starting Dual Bot System..."

# Start the API server in a new terminal window
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  osascript -e 'tell app "Terminal" to do script "cd \"$(pwd)\" && echo Starting Dual Bot API Server... && python dual_bot_api_server.py"'
else
  # Linux
  gnome-terminal -- bash -c "cd \"$(pwd)\" && echo Starting Dual Bot API Server... && python dual_bot_api_server.py; exec bash" || xterm -e "cd \"$(pwd)\" && echo Starting Dual Bot API Server... && python dual_bot_api_server.py; exec bash" || konsole -e "cd \"$(pwd)\" && echo Starting Dual Bot API Server... && python dual_bot_api_server.py; exec bash" || echo "Could not find a terminal emulator. Please start the API server manually."
fi

# Give the API server a moment to start
sleep 3

# Start the frontend application in a new terminal window
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  osascript -e 'tell app "Terminal" to do script "cd \"$(pwd)/frontend\" && echo Starting Frontend... && npm start"'
else
  # Linux
  gnome-terminal -- bash -c "cd \"$(pwd)/frontend\" && echo Starting Frontend... && npm start; exec bash" || xterm -e "cd \"$(pwd)/frontend\" && echo Starting Frontend... && npm start; exec bash" || konsole -e "cd \"$(pwd)/frontend\" && echo Starting Frontend... && npm start; exec bash" || echo "Could not find a terminal emulator. Please start the frontend manually."
fi

echo "Both services have been started. You can access the dashboard at:"
echo "http://localhost:3000/dual-bot"
echo ""
echo "Note: If the API server fails to start, the frontend will use mock data automatically."
echo ""
echo "Press any key to exit this script..."
read -n 1 -s 
