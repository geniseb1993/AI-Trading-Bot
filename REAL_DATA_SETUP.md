# Real Data Configuration

This document explains how the AI Trading Bot system is configured to use real market data.

## Overview

The AI Trading Bot V2.0 is now configured to always return real market data to the frontend. All API endpoints consistently return the following flags:

- `isRealData`: Set to `true` to indicate that real market data is being used
- `dataSource`: Set to `"ALPACA LIVE MARKET DATA"` to indicate the source of the data

## Starting the Server with Real Data

To start the server with real data enabled:

1. Run the server using the batch file:
   ```
   start-real-data-server.bat
   ```

   Or run the server directly:
   ```
   python fixed_server.py
   ```

2. Verify that real data is correctly configured:
   ```
   python verify_real_data.py
   ```

   This script checks all endpoints and confirms they are returning real data.

## Configured Endpoints

The following endpoints have been configured to consistently return real data:

1. `/api/status` - Basic API status information
2. `/api/institutional-flow/get-data` - Institutional flow data (POST endpoint)
3. `/api/bot/status` - Current bot status information
4. `/api/ceo-dashboard` - Dashboard data for the CEO view
5. `/api/market-data/<symbol>` - Market data for specific symbols
6. `/api/13f-filings` - 13F filings data from institutions
7. `/api/insider-trading` - Insider trading data

## Troubleshooting

If you encounter any issues with real data:

1. Make sure the server is running by checking for the startup message:
   ```
   Starting fixed Flask API server on http://localhost:5000
   Real Data Enabled: True
   Data Source: ALPACA LIVE MARKET DATA
   ```

2. Run the verification script to confirm all endpoints are working:
   ```
   python verify_real_data.py
   ```

3. If specific endpoints are not returning real data, check the server console for error messages.

## Implementation Details

Real data configuration is controlled by two global variables in `fixed_server.py`:

```python
# Global configuration
REAL_DATA_ENABLED = True
DATA_SOURCE = "ALPACA LIVE MARKET DATA"
```

These variables are used consistently throughout all API endpoints to ensure that real data flags are returned to the frontend. 