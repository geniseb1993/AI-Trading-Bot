# Bot Management System

This system provides a complete interface for managing multiple trading bots, including real-time data integration with Alpaca, Polygon, and other data providers.

## Setup

1. Ensure your `.env` file in the project root contains the following keys:
   ```
   ALPACA_API_KEY=your_alpaca_key
   ALPACA_API_SECRET=your_alpaca_secret
   POLYGON_API_KEY=your_polygon_key
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the system:
   ```
   python start_bot_management.py
   ```

## Components

The system includes the following components:

1. **API Server**: A Flask-based API server that provides endpoints for bot control and data access.
2. **Bot Managers**:
   - **Autonomous Bot**: A trading bot that makes autonomous decisions based on technical analysis.
   - **RSI Strategy Bot**: A bot that trades based on RSI signals.
   - **Dual Bot**: A new bot that implements a dual-strategy approach.
3. **Frontend**: A React-based interface for controlling bots and viewing trading activity.

## API Endpoints

- `GET /api/bot/status`: Get the status of all bots.
- `POST /api/bot/start/{bot_type}`: Start a specific bot (autonomous, rsi, or dual).
- `POST /api/bot/stop/{bot_type}`: Stop a specific bot.
- `GET /api/bot/data/{bot_type}`: Get real-time data for a specific bot.

## Troubleshooting

1. **Bot Activation Errors**:
   - Check the logs for specific error messages.
   - Verify API keys are correctly set in the `.env` file.
   - Make sure all required directories exist.

2. **Real Data Issues**:
   - Confirm API keys are valid and have necessary permissions.
   - Check if you have exceeded API rate limits.
   - Verify network connectivity to the API providers.

3. **Button Functionality**:
   - If buttons don't trigger the right action, check browser console for API errors.
   - Clear browser cache and reload the page.

## Logs

Logs are stored in the `data/logs` directory and can be useful for diagnosing issues.

# Bot Management Fixes

## Issues Fixed

1. **Missing Blueprint Registration**
   - The bot_routes blueprint from api/routes/bot_routes.py was not being registered in app.py
   - Added proper registration code with fallback to alternative import paths

2. **CORS Headers**
   - Added CORS headers to frontend API requests to ensure proper cross-origin communication
   - Set proper Content-Type and Accept headers

3. **Enhanced Error Handling and Logging**
   - Added detailed logging in frontend to help diagnose connection issues
   - Improved error extraction from API responses
   - Added debug panel that appears when connection issues are detected

4. **Improved UI for Dual Bot Status**
   - Added visual indicators when a bot component is missing
   - Enhanced bot card display with warning when dual bot is not available

5. **Connection Debugging Endpoint**
   - Added new `/api/bot/connection-check` endpoint that verifies all bot components
   - Helps diagnose component availability issues

## How to Check Bot Status

1. Start the API server by running:
   ```
   cd api
   python app.py
   ```

2. Test the API connection with:
   ```
   python test_api_connection.py
   ```

3. Access the bot management interface in the frontend

## Troubleshooting

If the bot management page doesn't show all three bots:

1. Check API connection with the debug tool
2. Verify that all three bot components are registered in the API:
   - AlpacaBroker (autonomous_bot)
   - RSIStrategy (rsi_bot)
   - DualBotManager (dual_bot)
3. Look for error messages in the API logs
4. Check browser console for frontend errors

## Common Error Patterns

1. **Missing Dual Bot**: If the dual bot doesn't appear, ensure DualBotManager is properly initialized in bot_routes.py

2. **Start/Stop Button Failures**: 
   - Check that bot_routes blueprint is registered with the correct URL prefix
   - Verify that bot components have proper start/stop methods

3. **Connection Issues**:
   - Verify CORS is properly configured
   - Check network tab in browser tools for failed requests
   - Ensure API server is running on the expected port 