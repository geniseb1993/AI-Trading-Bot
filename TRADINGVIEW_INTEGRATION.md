# TradingView Integration

## Overview

The TradingView integration allows the AI Trading Bot V2.0 to receive and process alerts from TradingView, and to retrieve market data and technical indicators.

## Features

- **Webhook Alerts**: Receive and store alerts from TradingView
- **Technical Indicators**: Calculate and retrieve technical indicators for any symbol
- **Market Analysis**: Get comprehensive market analysis including sentiment indicators
- **Real Data**: Uses real market data when available, with fallback to simulated data

## Getting Started

### Starting the Server

Use one of the following methods to start the TradingView integration server:

#### Windows
```
start_tradingview_server.bat
```

#### Any Platform (Python)
```
python start_tradingview_server.py
```

The server runs on port 5003 to avoid conflicts with other components.

### Testing the Integration

To verify the integration is working correctly, run:
```
python test_tradingview_integration.py
```

This will test all the endpoints and display the results.

## API Endpoints

### Webhook

**Endpoint**: `POST /api/tradingview/webhook`

Receive alerts from TradingView. Example payload:
```json
{
  "symbol": "SPY",
  "interval": "15m",
  "price": 452.75,
  "strategy": "EMA Crossover",
  "signal": "BUY",
  "message": "SPY: Bullish EMA crossover detected"
}
```

### Alerts

**Endpoint**: `GET /api/tradingview/alerts`

Get all received webhook alerts. Optional query parameters:
- `symbol`: Filter alerts by symbol
- `limit`: Limit the number of results (default: 50)

### Technical Indicators

**Endpoint**: `GET /api/tradingview/symbols/technical-data`

Get technical indicators for a symbol. Query parameters:
- `symbol`: Stock symbol (default: SPY)
- `interval`: Time interval (default: 1d, options: 1m, 5m, 15m, 1h, 4h, 1d)

Returns technical indicators including:
- RSI
- MACD
- Moving Averages (SMA 20, 50, 200, EMA 9, 21)
- Bollinger Bands
- Fibonacci Levels

### Market Analysis

**Endpoint**: `GET /api/tradingview/market/analysis`

Get comprehensive market analysis, including:
- Major Indices (SPY, QQQ, DIA, IWM)
- Sector Performance
- Market Breadth Indicators
- Economic Indicators (VIX, Treasury Yields)
- Market Sentiment (Fear & Greed Index)

## TradingView Setup

To send alerts from TradingView to the webhook:

1. Create an alert in TradingView
2. Select "Webhook URL" as the alert action
3. Enter the webhook URL: `http://your-server-ip:5003/api/tradingview/webhook`
4. Format the alert message as JSON with the required fields

Example alert message template for TradingView:
```
{
  "symbol": "{{ticker}}",
  "interval": "{{interval}}",
  "price": {{close}},
  "strategy": "Your Strategy Name",
  "signal": "{{strategy.order.action}}",
  "message": "{{ticker}}: {{strategy.order.comment}}"
}
```

## Frontend Integration

The TradingView integration can be used with the frontend by updating the URL in the `TradingViewIntegration.js` service to point to the new endpoints.

```javascript
// In TradingViewIntegration.js
const TRADINGVIEW_API_URL = 'http://localhost:5003/api/tradingview';
``` 