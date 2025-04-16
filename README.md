# AI Trading Bot V2.0

An advanced AI-powered trading platform with institutional flow analysis, dark pool insights, and real-time market data.

## Getting Started

Follow these steps to set up and run the AI Trading Bot:

### Prerequisites

- Python 3.8 or higher
- Node.js 14+ and npm
- API keys for various services (see Configuration section)

### Installation

1. Clone the repository
2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

### Starting the Application

We provide several ways to start the application:

#### Option 1: Quick Start (Recommended for first-time users)

```
.\quick-start.bat
```

This will:
- Install required packages
- Start the API server
- Start the React frontend

#### Option 2: Full Start with API Verification

```
.\start-all.bat
```

This will:
- Verify all API connections and environment variables
- Start the API server with real data capabilities
- Run extensive tests of API integrations
- Start the React frontend

#### Option 3: Manual Start

Start the API server:
```
python minimal_flask_server.py
```

In a separate terminal, start the frontend:
```
cd frontend
npm start
```

### Configuration

Create a `.env` file in the root directory with the following parameters:

```
# Unusual Whales API
UNUSUAL_WHALES_API_KEY=your_key_here

# Alpaca API credentials
ALPACA_API_KEY=your_key_here
ALPACA_API_SECRET=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# OpenRouter API for GPT-powered insights
OPENROUTER_API_KEY=your_key_here

# Hume AI API Key for voice notifications
HUME_API_KEY=your_key_here

# Application Settings
APP_ENV=production
```

## Testing API Connections

To verify your API connections are working properly:

```
python verify_api_connections.py
```

This will test:
- Environment variables
- Unusual Whales API (dark pool data)
- Alpaca API (trading)
- OpenRouter API (AI insights)
- Local server connectivity

## Troubleshooting

If you're experiencing issues:

1. Verify API connections using `verify_api_connections.py`
2. Check that all environment variables are set correctly in `.env`
3. Try running the minimal server directly: `python minimal_flask_server.py`
4. Look for error messages in the terminal windows

## Features

- Real-time market data integration
- Institutional flow analysis
- Dark pool insights
- AI-powered trading signals
- Portfolio management
- Risk management tools
- Voice notifications
- Automated trading strategies

## 🚀 Quick Start

### Option 1: Start both servers with one command

Use the provided batch file to start both the Flask backend and React frontend servers:

```
start-servers.bat
```

This will:
1. Start the Flask backend server on port 5000
2. Start the React frontend server on port 3000
3. Open browser windows for both

### Option 2: Start servers manually

#### Backend (Flask API)

```bash
cd api
python app.py
```

The Flask server will start on http://localhost:5000

#### Frontend (React)

```bash
cd frontend
npm install  # Only needed the first time
npm start
```

The React app will start on http://localhost:3000

## 🔧 Troubleshooting Common Issues

### Audio Files Not Loading

If you encounter errors with sound files not loading:

1. Make sure the sound files exist in the correct location:
   ```
   frontend/public/sounds/access-granted-87075.mp3
   frontend/public/sounds/access-denied-101308.mp3
   ```

2. Verify file sizes are correct (they should be larger than 1KB)

3. Use the audio test page to diagnose issues:
   ```
   http://localhost:3000/audio-test.html
   ```

### API 500 Errors

If you see HTTP 500 errors in the console:

1. Make sure the Flask backend is running on port 5000
2. Check that the CSV files exist in the `/api` directory:
   - buy_signals.csv
   - short_signals.csv
   - backtest_results.csv

3. Look for error messages in the Flask server console

### Backend Not Connecting

If the frontend can't connect to the backend:

1. Confirm the Flask server is running
2. Check the setupProxy.js configuration
3. Try running the app with HTTPS disabled:
   ```
   HTTPS=false npm start
   ```

## 📋 Features

### Market Data Integration
- Connect to real-time market data sources
- Support for Alpaca, Interactive Brokers, TradingView, and Unusual Whales
- Configure API keys and connection parameters

### Execution Model
- Market condition analysis
- Institutional flow analysis
- Trade setup generation
- Risk management
- Trade execution algorithms

### Backtesting
- Test strategies with historical data
- Detailed performance metrics
- Support for long and short positions

## 🧰 Project Structure

```
AI-Trading-Bot/
├── api/                        # Flask backend
│   ├── app.py                  # Main API routes
│   ├── execution_model_routes.py  # Execution model API endpoints
│   └── lib/                    # Backend libraries
├── frontend/                   # React frontend
│   ├── public/                 # Static assets
│   │   └── sounds/             # Audio files
│   └── src/                    # React source code
│       ├── components/         # UI components
│       └── setupProxy.js       # API proxy configuration
├── execution_model/            # Trading execution logic
└── start-servers.bat           # Helper script to start both servers
```

## 🔒 Security Notes

- API keys and secrets are stored locally
- The Vault interface provides an additional security layer
- Never share your API keys or trading credentials

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## Overview
AI Trading Bot is a Python-based algorithmic trading system that uses technical indicators to generate buy and sell signals for stocks and ETFs.

## Recent Fixes and Improvements
<!-- added or modified byUpLiftTeck -->
### Market Data Integration System (2025-04-03)
- **Multiple Data Sources**: Added support for Alpaca, Interactive Brokers, Unusual Whales APIs, and TradingView webhooks
- **Source Selection**: Implemented the ability to dynamically switch between market data sources
- **Real-time Market Data**: Stream live market data including bars, quotes, and trades
- **TradingView Webhook Integration**: Receive and display custom alerts from TradingView
- **API Configuration**: User-friendly interface for managing API keys and connection settings

### Vault Authentication System (2025-04-02)
- **Secure PIN Authentication**: Implemented a futuristic vault interface with 4-digit PIN protection
- **Audio Feedback**: Added sound effects for successful and failed authentication attempts
- **Automatic Validation**: PIN validates automatically when all 4 digits are entered
- **Session Management**: Added logout functionality and persistent authentication

### UI Enhancements (2025-04-02)
- **Fixed Frontend Issues**: Addressed undefined variables and missing file errors
- **Improved Error Handling**: Enhanced error resilience throughout the application
- **Audio Diagnostics**: Added testing tools for audio playback troubleshooting
- **Responsive Design**: Improved layout and transitions for a seamless user experience

### Signal Engine Improvements (2025-03-29)
- **Fixed buy_signal handling**: Modified the `extract_signals()` function to automatically create a buy_signal column based on signal_score when it's missing.
- **Added test scripts**: Created comprehensive test scripts to validate the signal engine and full pipeline.

## Features
- Fetches real-time and historical stock data
- Calculates technical indicators (EMA, RSI, MACD)
- Generates buy and sell signals based on configurable criteria
- Backtests trading strategies on historical data
- Secure vault interface with PIN authentication
- Audio-visual feedback for enhanced user experience
- Multiple market data sources with dynamic switching
- Real-time market data visualization
- TradingView webhook integration for custom alerts
- Advanced market condition analysis (trend, choppy, no-trade days)
- Institutional flow analysis for tracking "smart money"
- Automatic trade setup generation with confidence scoring
- Risk management with dynamic position sizing
- Execution algorithms with volume confirmation
- Portfolio exposure analysis and correlation tracking
- Real-time trade monitoring and management

## Enhanced UI
For detailed information about the updated user interface, please refer to [README-UI.md](README-UI.md).

## Market Data Integration
The application now supports multiple market data sources:

### Supported Data Sources
- **Alpaca API**: Real-time and historical stock and options data
- **Interactive Brokers API**: Professional-grade market data (requires TWS or IB Gateway)
- **Unusual Whales API**: Dark pool and options flow data for institutional insights
- **TradingView Webhooks**: Custom alerts from TradingView strategies and indicators

### Setting Up Market Data Sources
1. Navigate to the API Configuration page in the application
2. Enter your API keys for the desired data sources
3. Select your preferred active data source
4. Save the configuration

### TradingView Webhook Setup
To set up TradingView webhooks:
1. Create an alert in TradingView with "Webhook URL" as the notification method
2. Set the webhook URL to `http://YOUR_SERVER_IP:5001/tradingview-webhook`
3. Configure the alert message as a JSON payload with your desired fields
4. View incoming alerts in the TradingView Alerts section of the application

## Test Scripts
<!-- added or modified byUpLiftTeck -->
### Testing Signal Engine
Use the following command to verify the signal engine's functionality:
```
python test_signal_engine.py
```

This test script:
- Validates that buy_signals.csv is correctly formatted
- Tests the signal processing logic
- Ensures compatibility with the backtesting module
- Generates a summary report of signal distribution

### Testing Full Pipeline
Use the following command to test the complete trading pipeline:
```
python test_full_pipeline.py
```

This test script:
- Tests data fetching
- Validates signal calculation
- Tests extraction of buy signals
- Verifies that the fix for the missing buy_signal column works correctly
- Tests backtesting with both calculated and CSV-loaded signals

### Testing Market Data Integration
Use the following command to test the market data integration:
```
python test_market_data.py
```

This test script:
- Tests connectivity to all configured market data sources
- Validates API authentication with each provider
- Verifies data retrieval from each source
- Tests the TradingView webhook server

### Testing Execution Model
Use the following command to test the execution model components:
```
python test_execution_model.py
```

This test script:
- Tests the market condition analyzer with different market scenarios
- Validates institutional flow analysis functions
- Tests trade setup generation with various market conditions
- Verifies risk management calculations
- Tests execution algorithms with simulated market data

### Testing Audio Playback
Use the following URL to test the audio components:
```
http://localhost:3000/audio-test.html
```

This test page:
- Verifies that audio files can be loaded and played
- Tests different audio file paths to find what works best
- Provides detailed error reporting for audio playback issues
- Helps diagnose browser-specific audio compatibility issues

## Usage
1. Update configuration in `config.py`
2. Run the pipeline with `python run_pipeline.py`
3. View generated signals in `buy_signals.csv` and `short_signals.csv`
4. Analyze backtest results in `backtest_results.csv`
5. Start the frontend with `cd frontend && npm start`
6. Access the application at `http://localhost:3000`
7. Enter PIN `8080` to access the trading dashboard
8. Configure your preferred market data sources in the API Configuration page
9. View real-time market data in the Market Data page

## API Keys
To use the market data integration features, you'll need API keys from the following providers:
- **Alpaca**: Sign up at https://alpaca.markets/
- **Interactive Brokers**: Sign up at https://www.interactivebrokers.com/
- **Unusual Whales**: Sign up at https://unusualwhales.com/
- **TradingView**: No API key required for webhooks, but you'll need a TradingView account

## Feature Implementation Plan

### Stage 1: Connect to Real-Time Market Data ✅ COMPLETED
As outlined in our implementation plan, Stage 1 focused on connecting the AI Trading Bot to real-time market data through multiple sources:

#### Requirement 1: Dark Pool & Options Flow APIs ✅
- **Unusual Whales Integration**: We've added support for institutional order flow data
- **API Configuration**: Easy setup via the API configuration interface
- **Data Visualization**: View dark pool and unusual options activity

#### Requirement 2: Live Market Data Feeds ✅
- **Interactive Brokers Connection**: Professional-grade real-time data
- **TradingView Webhooks**: Custom alert integration for strategy signals
- **Configuration UI**: Simple interface to manage connections

#### Requirement 3: Volume & Order Flow Tracking ✅
- **Tick-by-Tick Analysis**: View real-time trades through the market data viewer
- **DOM Data**: Access to order book data via Interactive Brokers API
- **Volume Insights**: Track volume patterns with real-time bars

#### Requirement 4: Data Source Selection ✅
- **Dynamic Source Switching**: Toggle between different providers
- **Persistent Configuration**: Saved settings between sessions
- **Unified API Layer**: Consistent data access regardless of source

### Stage 2: Build a Real-Time Trade Execution Model ✅ COMPLETED
Stage 2 focused on building a powerful trade execution model that analyzes market conditions and generates trade setups:

#### Requirement 1: Custom AI Execution Rules ✅
- **Market Condition Analyzer**: Identifies trend days, choppy days, and no-trade days
- **Market Regime Classification**: Categorizes markets into trending, ranging, volatile, or calm states
- **Technical Analysis**: Leverages advanced indicators to detect market conditions

#### Requirement 2: Trade Entry & Exit Algorithms ✅
- **Position Sizing**: Smart position sizing based on risk profile and market conditions
- **Stop-Loss & Profit Targets**: Dynamic calculation based on volatility and setup type
- **Volume Confirmation**: Entry validation based on volume patterns

#### Requirement 3: Hedge Fund-Style Playbook ✅
- **Institutional Flow Analysis**: Integration with unusual options and dark pool data
- **Market Structure Analysis**: Support/resistance detection with advanced algorithms
- **Smart Money Detection**: Correlation between institutional flow and price action

#### Implementation Details
- Comprehensive execution model with modern software architecture
- React-based UI components for market analysis, institutional flow, and trade setups
- Real-time data adapter connecting Stage 1 and Stage 2 components
- Risk management system with portfolio exposure tracking
- Configuration system for fine-tuning trading parameters

## Detailed Modifications
For a complete list of all modifications and improvements, see [UpLiftTeck_Modifications.md](UpLiftTeck_Modifications.md).
