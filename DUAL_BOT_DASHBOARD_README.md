# Dual Bot Dashboard User Guide

## Overview

The Dual Bot Dashboard is a web interface that allows you to monitor and interact with the AI-powered trading bot that uses both DeepSeek (for trade scanning) and ChatGPT (for risk assessment). This guide will help you get the dashboard up and running.

## System Components

The Dual Bot system consists of two main components:

1. **Backend API Server**: A Flask server that provides API endpoints for the dashboard
2. **Frontend Dashboard**: A React-based web interface for monitoring and controlling the bot

## Starting the Dual Bot API Server

To start the API server:

```bash
python dual_bot_api_server.py
```

The server will start on port 5001 (http://localhost:5001) and provide the following endpoints:

- `/api/health` - Health check
- `/api/status` - Bot status
- `/api/market-data/<symbol>` - Market data for a symbol
- `/api/options-data/<symbol>` - Options data for a symbol
- `/api/news/<symbol>` - News for a symbol
- `/api/scan` - Scan for trade recommendations (DeepSeek)
- `/api/assess-risk` - Assess risk for a trade (ChatGPT)
- `/api/check-position` - Check if a position should be closed
- `/api/config` - Get current configuration

## Using the Frontend with Mock Data

If you're having issues with the API server, the frontend is designed to work with mock data:

1. Open `frontend/src/services/dualBotService.js`
2. Set the `USE_MOCK_DATA` flag to `true`:
   ```javascript
   const USE_MOCK_DATA = true;
   ```
3. Start the frontend application:
   ```bash
   cd frontend
   npm start
   ```

This will allow you to use the dashboard with simulated data without needing the API server to be running.

## Accessing the Dashboard

The dashboard is part of the main frontend application. To access it:

1. Start the frontend application:
   ```bash
   cd frontend
   npm start
   ```

2. Navigate to the Dual Bot page:
   http://localhost:3000/dual-bot

## Using the Dashboard

The Dual Bot Dashboard provides the following features:

### Bot Status Panel
- Displays if the bot is active
- Shows the number of active positions
- Displays trading statistics (if available)

### Market Data Panel
- Select a symbol from the dropdown
- View current price data for the selected symbol

### DeepSeek Trade Recommendation Panel
1. Click the "Scan for Trades" button to generate a trade recommendation
2. The system will analyze the market and provide a recommended trade
3. Trade details include:
   - Symbol and trade type (BUY_CALL/BUY_PUT)
   - Strike price and expiration
   - Entry price, target price, and stop loss
   - Confidence level and rationale

### ChatGPT Risk Assessment Panel
1. After receiving a trade recommendation, click "Assess Risk with ChatGPT"
2. The system will evaluate the trade recommendation and provide:
   - Approval status (APPROVED/REJECTED)
   - Risk score (1-10)
   - Market conditions assessment
   - Potential concerns
   - Summary of the risk analysis

## Troubleshooting

### API Connectivity Issues
If the dashboard shows "API Disconnected" or "Partial Connection":

1. Verify the Dual Bot API server is running:
   ```bash
   python dual_bot_api_server.py
   ```

2. Check the `dualBotService.js` file in `frontend/src/services` to ensure it's pointing to the correct API URL (default: http://localhost:5001/api)

3. The dashboard includes a fallback to mock data if the API is unavailable. To enable this, set `USE_MOCK_DATA` to `true` in `dualBotService.js`

4. If you continue to have issues with the API server, use the mock data solution described above.

### Common API Server Issues

If the API server fails to start or respond:

1. **Port already in use**: Make sure no other application is using port 5001. You can change the port in `dual_bot_api_server.py` if needed.

2. **Python dependency issues**: Ensure all required packages are installed:
   ```bash
   pip install flask flask-cors
   ```

3. **Error logs**: Check the console output and `dual_bot_api_server.log` for specific error messages.

### OpenAI/Deepseek API Key Issues
If you're using the real AI models and experiencing issues:

1. Verify your API keys are correctly set in the `.env` file
2. Ensure you have sufficient credits/quota on your API accounts
3. Check connectivity to the respective AI services

## Customization

You can customize the available symbols by modifying the `SAMPLE_DATA` list in `dual_bot_api_server.py`

## Note on Demo Mode

The current implementation provides simulated responses for development and testing purposes. In production, the endpoints would connect to the actual DeepSeek and ChatGPT services to provide real trading recommendations and risk assessments. 