# Dual Bot Troubleshooting Guide

## Overview
This document provides solutions for common Dual Bot connectivity issues and explains the improvements made to ensure reliable operation.

## Quick Fix
Run the `fix-dual-bot.bat` script to automatically fix connection issues:

```
.\fix-dual-bot.bat
```

This script will:
1. Check your Python environment
2. Install required dependencies
3. Start or restart the Dual Bot API server
4. Launch the frontend application
5. Open the Dual Bot page in your browser

## Common Issues and Solutions

### 1. Connection Refused Errors
**Symptoms:**
- Console shows `ERR_CONNECTION_REFUSED` errors
- API requests fail with "No response received"

**Solutions:**
- Ensure the Dual Bot API server is running on port 5001
- Run `python check_dual_bot_server.py` to check and restart the server
- Verify no other application is using port 5001

### 2. CORS Errors
**Symptoms:**
- Console shows "CORS connection failed" errors
- API requests are blocked by CORS policy

**Solutions:**
- The CORS configuration has been updated in the API server
- Ensure the origins match between client and server
- Use the `fix-dual-bot.bat` script to reset everything

### 3. Slow Loading Times
**Symptoms:**
- Dual Bot page takes a long time to load
- Console shows many repeated request attempts

**Solutions:**
- The application now uses a faster fallback to mock data
- Connection timeouts have been reduced
- Retry mechanism has been improved

## Technical Improvements Made

1. **Enhanced Frontend Robustness**:
   - Auto-fallback to mock data when API is unavailable
   - Reduced timeout from 15s to 5s for faster response
   - More intelligent retry mechanism
   - Added comprehensive mock data for all endpoints

2. **Improved Backend Stability**:
   - Enhanced server startup process
   - Better process management
   - Dependency checking and auto-installation
   - Improved CORS configuration

3. **Better UI Experience**:
   - Added connection status indicator
   - Clear error messages
   - Retry button for reconnection
   - Regular connection status checks

## Troubleshooting Steps

If you continue to experience issues:

1. Check the log files:
   - `dual_bot_server_check.log` - Server startup information
   - `dual_bot_api_server.log` - API server logs

2. Verify dependencies:
   ```
   pip install flask flask-cors requests
   ```

3. Check for port conflicts:
   ```
   netstat -ano | findstr :5001
   ```

4. Ensure your firewall isn't blocking connections to localhost

5. Try using mock data mode if the API server cannot be started:
   - The application will automatically use mock data when the API is unavailable
   - You can force mock data mode by setting `USE_MOCK_DATA = true` in dualBotService.js

## Contact Support
If you need further assistance, please create an issue with:
1. The exact error messages from the console
2. Log file contents
3. Steps to reproduce the issue

## Issue: Frontend Connection Errors

When accessing the dual bot dashboard, the following errors occurred:

```
Failed to fetch market data for QQQ: Error: Failed to get market data for QQQ from any endpoint
[DualBot API Error] 404 /status: Object
[DualBot] Health endpoint works but status endpoint failed
```

## Root Causes

1. **Missing API Endpoints**: The dual bot API server was missing several critical endpoints needed by the frontend:
   - `/api/status` - For getting the bot status
   - `/api/market-data/:symbol` - For fetching market data
   - `/api/options-data/:symbol` - For fetching options data
   - `/api/news/:symbol` - For fetching news
   - `/api/dual-bot/signals` - For fetching trading signals

2. **Port Configuration**: The frontend expected the dual bot API server to be available on port 5001.

## Solutions Applied

1. **Added Missing Endpoints**: The following endpoints were added to `dual_bot_api_server.py`:

   - **Status Endpoint**:
     ```python
     @app.route('/api/status', methods=['GET', 'OPTIONS'])
     def get_status():
         # Returns the status of the dual bot
     ```
   
   - **Dual Bot Status Endpoint**:
     ```python
     @app.route('/api/dual-bot/status', methods=['GET', 'OPTIONS'])
     def get_dual_bot_status():
         # Returns the status via the general status endpoint
     ```
   
   - **Market Data Endpoint**:
     ```python
     @app.route('/api/market-data/<symbol>', methods=['GET', 'OPTIONS'])
     def get_market_data(symbol):
         # Returns market data for the specified symbol
     ```
   
   - **Options Data Endpoint**:
     ```python
     @app.route('/api/options-data/<symbol>', methods=['GET', 'OPTIONS'])
     def get_options_data(symbol):
         # Returns options data for the specified symbol
     ```
   
   - **News Endpoint**:
     ```python
     @app.route('/api/news/<symbol>', methods=['GET', 'OPTIONS'])
     def get_news(symbol):
         # Returns news articles for the specified symbol
     ```
   
   - **Signals Endpoint**:
     ```python
     @app.route('/api/dual-bot/signals', methods=['GET', 'OPTIONS'])
     def get_dual_bot_signals():
         # Returns trading signals from the dual bot
     ```

2. **Created Helper Scripts**:

   - `start_dual_bot_api.bat` - Batch file to easily start the dual bot API server
   - `test_dual_bot_api.py` - Python script to test all API endpoints
   - `test_dual_bot_api.bat` - Batch file to run the test script

## Testing

The API can be tested using the included `test_dual_bot_api.py` script, which verifies that all endpoints are working correctly:

```bash
python test_dual_bot_api.py
```

Or simply run the batch file:

```bash
test_dual_bot_api.bat
```

## Starting the Dual Bot API Server

To start the dual bot API server, use the included batch file:

```bash
start_dual_bot_api.bat
```

This will start the server on port 5001, making it available to the frontend.

## Verification

After implementing these changes, the dual bot dashboard should load correctly without errors. The frontend should be able to:

1. Connect to the API health endpoint
2. Fetch the bot status
3. Retrieve market data for symbols
4. Display options data
5. Show news and signals

If issues persist, check the console logs in your browser's developer tools and verify that all endpoints are returning data with status code 200.

## Additional Notes

- The implementation uses mock data for demonstration purposes. In a production environment, these endpoints would connect to real data sources.
- The API includes CORS headers to allow cross-origin requests from the frontend.
- The server runs on port 5001 by default, which matches the frontend's expected configuration. 