# Broker Integration Module Quickstart Guide

This guide will help you get started with the Broker Integration Module, a unified API for interacting with various trading platforms.

## Installation

The Broker Integration Module is included in the AI Trading Bot, but you'll need a few dependencies:

```bash
pip install alpaca-trade-api requests flask flask-cors
```

## Configuration

Before using the module, you need to set up your broker configuration:

1. Create or edit `broker_config.json` in the project root directory:

```json
{
  "active_broker": "mock",
  "brokers": {
    "mock": {
      "type": "mock",
      "initial_balance": 100000.0
    },
    "alpaca": {
      "type": "alpaca",
      "api_key": "YOUR_ALPACA_API_KEY",
      "api_secret": "YOUR_ALPACA_API_SECRET",
      "is_paper": true
    }
  },
  "data": {
    "trade_history_file": "api/broker_integration/data/trade_history.json"
  }
}
```

2. For Alpaca, replace `YOUR_ALPACA_API_KEY` and `YOUR_ALPACA_API_SECRET` with your actual API credentials.

## Using the Module in Your Code

### Basic Usage

```python
from api.broker_integration import BrokerManager, TradeExecutor, PortfolioTracker

# Initialize broker manager
broker_manager = BrokerManager()
broker_manager.load_config()

# Get active broker
broker = broker_manager.get_active_broker()

# Get account information
account_info = broker.get_account_info()
print(f"Cash available: ${account_info['cash']}")
print(f"Portfolio value: ${account_info['portfolio_value']}")

# Get market data
market_data = broker.get_market_data("AAPL")
print(f"AAPL price: ${market_data['last']}")

# Execute a trade
executor = TradeExecutor(broker_manager)
trade_result = executor.execute_market_order(
    symbol="AAPL",
    qty=1,
    side="buy",
    strategy="example"
)
print(f"Trade executed: {trade_result}")

# Get portfolio information
portfolio = PortfolioTracker(broker_manager)
performance = portfolio.get_performance_metrics()
print(f"Performance: {performance}")
```

### Using the API

The broker integration module comes with a Flask API that you can use to interact with brokers via HTTP requests:

1. Start the API server:
```bash
python run_api.py
```

2. Use the API endpoints:
- `GET /api/broker/info` - Get information about available brokers
- `POST /api/broker/set-active` - Set the active broker
- `GET /api/broker/account` - Get account information
- `POST /api/broker/execute/market` - Execute a market order
- See the full API documentation in the README.md file

You can also use the provided example client:
```bash
python api/broker_integration/example_client.py
```

## Testing

Test the broker integration module:

```bash
python test_broker_integration.py
```

The test script verifies that all components of the broker integration module work correctly.

## Next Steps

1. Explore the `example_client.py` file to see how to interact with the API.
2. Check the `README.md` file for detailed API documentation.
3. Try switching between mock broker and Alpaca.
4. Implement your own trading strategies using the broker integration API.

## Troubleshooting

- **API Connection Issues**: Make sure the Flask server is running.
- **Alpaca Authentication**: Verify your API keys in the config file.
- **Missing Dependencies**: Ensure all required packages are installed.

For more detailed information, refer to the full documentation in the README.md file. 