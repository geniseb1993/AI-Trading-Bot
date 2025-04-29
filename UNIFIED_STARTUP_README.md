# AI Trading Bot Unified Startup Guide

This document explains the new unified startup process for the AI Trading Bot system. We've streamlined the startup process to make it more efficient and reliable.

## Unified Startup Approach

The new system uses a single startup script that handles both the backend API server and the frontend application with fixed port assignments:

- Backend API Server: Port 5001
- Frontend Application: Port 3001

## Data Loading Fix

Recent updates have addressed data loading issues by:

1. Ensuring consistent port usage (5001 for API, 3001 for frontend)
2. Updating CORS configurations to allow communication between these ports
3. Fixing API connectivity issues in the frontend services
4. Testing and verifying all API endpoints are working properly

These changes ensure dashboards and data visualizations load correctly without the infinite loading issue.

## Quick Start

### Windows

Simply run:
```
start-app-unified.bat
```

### Linux/macOS

Simply run:
```
chmod +x start-app-unified.sh
./start-app-unified.sh
```

## What the Unified Startup Does

1. Checks for required dependencies (Python and Node.js)
2. Ensures the Dual Bot API server is running on port 5001
3. Starts the frontend application on port 3001
4. Provides feedback on the startup process

## Accessing the System

After starting the system:

- Frontend Dashboard: http://localhost:3001
- API Health Check: http://localhost:5001/api/health

## Troubleshooting

If you encounter issues with the unified startup:

1. Check the log files:
   - `fix-dual-bot-api.log` - For API server issues
   - Check the terminal output for frontend issues

2. Try running the components separately:
   - API Server: `fix-dual-bot-api.bat` (Windows) or `python fix-dual-bot-api.py` (Linux/macOS)
   - Frontend: `cd frontend && npm start`

3. Ensure ports 5001 and 3001 are available:
   - Use `netstat -ano | findstr :5001` (Windows) or `lsof -i :5001` (Linux/macOS) to check

## Stopping the System

### Windows
Close the terminal windows that were opened by the startup script.

### Linux/macOS
Use these commands:
```
pkill -f "node.*start"
pkill -f "python.*dual_bot_api_server.py"
```

## Understanding the Cleanup Process

The unified approach has consolidated multiple startup scripts into a single, streamlined solution. The following scripts have been replaced by the unified startup:

- `start-app.bat` / `start-app.sh`
- `start-dual-bot.bat` / `start-dual-bot.sh`
- `start-dual-bot-with-frontend.bat`
- Other various startup scripts

The new unified approach:
- Ensures consistent port usage
- Provides better error handling
- Works cross-platform
- Simplifies the startup process

## For Developers

If you need to modify the startup process:

- `fix-dual-bot-api.py` - Core script that ensures the API server is running
- `start-app-unified.bat` / `start-app-unified.sh` - Main startup scripts 