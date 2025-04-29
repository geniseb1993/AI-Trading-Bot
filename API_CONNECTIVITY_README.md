# Dual Bot API Connectivity Guide

This document provides instructions for diagnosing and fixing connectivity issues between the frontend and the Dual Bot API server.

## Quick Start

1. Run the API connectivity diagnostic script:
   ```
   node fix-api-connectivity.js
   ```

2. Follow the recommendations provided by the script to fix any issues.

## API Server Details

- **Server File**: `dual_bot_api_server.py`
- **Port**: 5001
- **Base URL**: `http://localhost:5001/api`

## Key Endpoints

| Endpoint | Purpose | Example Response |
|----------|---------|-----------------|
| `/api/health` | Health check | `{ "status": "healthy" }` |
| `/api/status` | Bot status | `{ "status": true, ... }` |
| `/api/dual-bot/status` | Dual bot specific status | `{ "success": true, "status": {...} }` |
| `/api/market-data/{symbol}` | Market data for a symbol | `{ "symbol": "QQQ", "price": 456.78, ... }` |

## Common Issues & Solutions

### 1. API Server Not Running

**Symptoms**:
- "Connection refused" errors in the frontend
- All API requests fail
- Red error indicators in the UI

**Solution**:
1. Start the API server:
   ```
   python dual_bot_api_server.py
   ```
2. Verify it's running:
   ```
   node test_dual_bot_connectivity.js
   ```

### 2. Incorrect API URL Configuration

**Symptoms**:
- Some endpoints work, others don't
- Inconsistent behavior in the UI

**Solution**:
1. Check the API URL configuration in the following files:
   - `frontend/src/services/apiService.js`
   - `frontend/src/services/dualBotService.js`
   - `frontend/src/setupProxy.js`

2. Ensure they all use the correct API URL: `http://localhost:5001/api`

### 3. CORS Issues

**Symptoms**:
- API requests fail in the browser console with CORS errors
- Server works when tested directly, but fails from the frontend

**Solution**:
1. Ensure the API server has CORS properly configured for your frontend origin
2. Check that the following headers are set in responses:
   - `Access-Control-Allow-Origin`: `http://localhost:3001`
   - `Access-Control-Allow-Methods`: `GET,POST,OPTIONS,PUT,DELETE`
   - `Access-Control-Allow-Headers`: `Content-Type,Authorization,Accept,X-Requested-With,X-API-Key`

### 4. Endpoint Path Mismatches

**Symptoms**:
- Specific endpoints return 404 errors
- Frontend shows "Endpoint not found" errors

**Solution**:
1. Verify that the endpoints in the frontend code match those in the API server
2. Common mismatches:
   - Using `/api/dual-bot/status` instead of `/api/status`
   - Using `/api/health-check` instead of `/api/health`

## Testing Tools

1. **API Connectivity Test**:
   ```
   node test_dual_bot_connectivity.js
   ```
   Tests all essential endpoints and reports their status.

2. **Python API Test**:
   ```
   python test_dual_bot_api.py
   ```
   More comprehensive test of the API functionality.

3. **API Endpoint Tester**:
   Use a tool like Postman or curl to test specific endpoints:
   ```
   curl http://localhost:5001/api/health
   ```

## Starting the System

To start the complete system:

1. Start the API server:
   ```
   python dual_bot_api_server.py
   ```

2. Start the frontend (in a new terminal):
   ```
   cd frontend
   npm start
   ```

3. Access the frontend at:
   ```
   http://localhost:3001
   ```

## Additional Resources

- Full API documentation is available in the `API_STATUS.md` file
- For persistent issues, check the `dual_bot_api_server.log` file for server-side errors
- For frontend issues, check the browser console and network tab 