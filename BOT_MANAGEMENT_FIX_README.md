# Bot Management Timeout Fix

## Problem Description

The Bot Management page was experiencing frequent timeouts and connection errors, including:

- 504 Gateway Timeout errors
- Connection timeouts for `/api/bot/status` endpoints
- Connection timeouts for `/api/ai-activity/logs` and `/api/ai-activity/activity-types` endpoints

These issues were caused by potential performance bottlenecks in the original implementation, where the main API server was handling too many endpoints and complex operations simultaneously.

## Solution

We've created a separate, lightweight server specifically to handle bot management and AI activity endpoints. This server:

1. Runs on port 5002 (while the main API server continues to run on port 5001)
2. Provides fast, reliable responses for bot status, start/stop operations, and AI activity logs
3. Uses in-memory storage with file persistence to maintain state
4. Implements the same API interface but with simplified, more reliable implementations

This approach allows us to separate these critical, frequently-accessed endpoints from the more complex operations in the main API server.

## Files Overview

- `simple_bot_management_server.py` - The standalone server for bot management endpoints
- `start_bot_management_server.bat` - Script to start just the bot management server
- `test_bot_management_server.py` - Script to test the bot management server endpoints
- `test_bot_server.bat` - Script to run the tests
- `api_proxy_config.js` - Configuration for routing API requests to the appropriate server
- `start_both_servers.bat` - Script to start both the main API and bot management servers
- `stop_both_servers.bat` - Script to stop both servers

## How to Use

### Starting the Servers

1. Run `start_both_servers.bat` to start both the main API server and the bot management server
2. The main API server will run on port 5001 as before
3. The bot management server will run on port 5002
4. The servers will run in separate command windows

### Testing the Bot Management Server

1. Run `test_bot_server.bat` to verify the bot management server is working correctly
2. This will test all endpoints and show their responses

### Stopping the Servers

1. Run `stop_both_servers.bat` to properly shut down both servers
2. Alternatively, you can close the command windows

## Frontend Integration

For proper frontend integration, update your proxy configuration or API service to route bot management-related requests to port 5002 instead of 5001. The `api_proxy_config.js` file contains the routing logic that should be integrated into your frontend's API request handling.

The following endpoints should be routed to the bot management server (port 5002):

- `/api/bot/status`
- `/api/bot/start/*`
- `/api/bot/stop/*` 
- `/api/status` (for compatibility)
- `/api/dual-bot/status` (for compatibility)
- `/api/ai-activity/logs`
- `/api/ai-activity/activity-types`

All other endpoints should continue to be directed to the main API server (port 5001).

## Troubleshooting

If you continue to experience timeout issues:

1. Make sure both servers are running (check both command windows)
2. Verify that the bot management server is responding by accessing `http://localhost:5002/api/health` in your browser
3. Check the log files (`bot_management_server.log` and `dual_bot_api_server.log`) for any errors
4. Ensure your frontend is correctly routing requests to the appropriate server

## Additional Notes

- The bot management server stores its state in a file called `bot_status.json` to persist between restarts
- The server automatically updates and saves the status every 30 seconds
- For production deployment, consider implementing proper authentication and HTTPS 