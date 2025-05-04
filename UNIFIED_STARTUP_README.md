# Unified Server Startup for AI Trading Bot

This document provides instructions on how to start all components of the AI Trading Bot system using the unified startup script.

## Overview

The `start_unified.py` script is the **single, unified way** to start all components of the trading bot system:

1. API Server (simple_api_server.py or alternatives)
2. Bot Management Server (if available)
3. TradingView Integration Server (if available)
4. Frontend Application (React)

## Quick Start

To start all components with a single command:

```
python start_unified.py
```

This will:
1. Start the API server on port 5001
2. Start the Bot Management Server on port 5002 (if available)
3. Start the TradingView Server on port 5003 (if available)
4. Start the Frontend on port 3001

## Accessing the Services

After starting the services, you can access them at:

- API Server: http://localhost:5001/api/health
- Bot Management Server: http://localhost:5002/api/health
- TradingView Server: http://localhost:5003/api/test
- Frontend: http://localhost:3001

## Troubleshooting

### Port Already in Use

If a port is already in use, the script will ask if you want to kill the process using that port. Answer 'y' to kill the process and continue, or 'n' to skip starting that component.

### Server Not Starting

Check the logs in `server_startup.log` for details on any errors. Common issues include:

- Missing dependencies: Make sure all required packages are installed
- Port conflicts: Ensure no other applications are using the required ports
- Configuration issues: Verify that the environment variables are set correctly

## Stopping the Services

To stop all services, press `Ctrl+C` in the terminal where you started the script. The script will gracefully shut down all running services.

## For Render Deployment

When deploying to Render, the service will use the appropriate startup command from `render.yaml` or the build configuration. The unified script is designed to work in both local and deployed environments.

## Note

This unified script replaces all previous startup scripts. For simplicity and maintenance, please use this script instead of any other startup scripts in the codebase. 