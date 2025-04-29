# Unified Server Startup Guide

This document provides detailed information about the unified server startup solution for the AI Trading Bot system.

## Overview

The unified server startup solution orchestrates the boot-up of all existing servers within the application, including both frontend and backend services. This approach eliminates fragmented server startups, ensures seamless API communication across all modules, and prevents 404 errors and data synchronization issues.

## Components

The unified server startup consists of the following components:

1. **Main Python Script** (`start_all_servers.py`): Orchestrates the startup process, checks dependencies, and monitors server health.
2. **Windows Batch File** (`start_all_servers.bat`): Wrapper for the Python script on Windows systems.
3. **Shell Script** (`start_all_servers.sh`): Wrapper for the Python script on Unix/Linux/macOS systems.

## Servers Started

The unified startup process starts the following servers in the correct order:

1. **Dual Bot API Server** (Port 5001): Main backend API server.
2. **Bot Management Server** (Port 5002): Controls trading bot status and operations.
3. **TradingView Integration Server** (Port 5003): Handles TradingView webhook alerts and technical analysis.
4. **Frontend Application** (Port 3001): React-based user interface.

## Prerequisites

- Python 3.8 or higher
- Node.js 14.0 or higher and npm
- Required Python packages (installed automatically if missing):
  - flask
  - flask-cors
  - requests
  - python-dotenv
  - pandas
  - numpy
  - yfinance
- Frontend dependencies (managed by npm)

## Usage

### Windows

```batch
start_all_servers.bat
```

### Unix/Linux/macOS

```bash
chmod +x start_all_servers.sh  # Make executable (first time only)
./start_all_servers.sh
```

### Manual Python Execution

```bash
python start_all_servers.py
```

## Features

### Environment Variable Management

- Automatically loads environment variables from `.env` file
- Creates `.env` from `.env.example` if not present
- Provides clear error messages for missing configuration

### Dependency Management

- Checks for required Python packages and offers to install missing ones
- Verifies Node.js installation and frontend dependencies
- Validates that all necessary server scripts exist

### Health Checks

- Performs health checks for each server after startup
- Verifies API connectivity
- Provides detailed error messages for failed services

### Process Management

- Proper startup order based on dependencies
- Graceful shutdown of all processes on interrupt (Ctrl+C)
- Handles Windows and Unix/Linux process management differences

### Port Conflict Resolution

- Checks for port availability before starting each server
- Provides clear error messages for port conflicts

## Troubleshooting

### Server Startup Issues

If any server fails to start, check:

1. **Port Conflicts**: Ensure ports 5001, 5002, 5003, and 3001 are available.
2. **Missing Files**: Verify all server script files exist.
3. **Dependency Issues**: Check that all required packages are installed.
4. **Environment Variables**: Ensure `.env` file contains all required API keys.

### API Connectivity Issues

If you see API connectivity issues after startup:

1. Check server logs in the relevant server's console window.
2. Verify that all servers started successfully.
3. Check the `server_startup.log` file for detailed error messages.

### 404 Errors

If you encounter 404 errors:

1. Ensure the Dual Bot API Server started successfully.
2. Check the API endpoint URL in your frontend code.
3. Verify CORS settings in the server configurations.

## Configuration

### Port Configuration

Port settings are defined in the `start_all_servers.py` file:

```python
# PORT CONFIGURATION
DUAL_BOT_API_PORT = 5001
BOT_MANAGEMENT_PORT = 5002
TRADINGVIEW_PORT = 5003
FRONTEND_PORT = 3001
```

To modify these settings, update the appropriate values in the script.

### Environment Variables

Required environment variables are specified in the `.env.example` file. Copy this file to `.env` and update the values as needed.

## Extending the System

To add new servers to the unified startup process:

1. Add a new function in `start_all_servers.py` following the pattern of existing server startup functions.
2. Add the new server to the `main()` function in the appropriate startup order.
3. Update the port configuration section if the new server requires a specific port.
4. Add any new required dependencies to the `REQUIRED_PACKAGES` list.

## Logging

The unified server startup script logs information to both the console and a log file named `server_startup.log`. This file contains detailed information about the startup process, including:

- Environment variable loading
- Dependency checks
- Server startup attempts
- Health check results
- Error messages

Review this log file when troubleshooting startup issues.

## Best Practices

- Always run the unified startup script from the project root directory.
- Ensure all required API keys are set in the `.env` file before starting.
- Stop all servers using Ctrl+C in the script's terminal window rather than closing individual server windows.
- Check the server logs if any issues occur during operation.

## Security Considerations

- The `.env` file contains sensitive API keys and should not be committed to version control.
- The default ports used by the servers should be firewalled appropriately in production environments.
- API keys should be rotated regularly according to your security policy.

## Additional Resources

- [API_CONNECTIVITY_README.md](API_CONNECTIVITY_README.md): Information about API connectivity
- [TRADINGVIEW_INTEGRATION.md](TRADINGVIEW_INTEGRATION.md): TradingView integration documentation
- [BOT_MANAGEMENT_README.md](BOT_MANAGEMENT_README.md): Bot management documentation 