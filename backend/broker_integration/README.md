# Broker Integration Module

This module provides integration with various trading brokers, offering a unified interface for interacting with different broker APIs.

## Overview

The broker integration module is designed to abstract away the differences between broker APIs, providing a consistent interface for the application to interact with. This allows the application to easily switch between different brokers without changing the core application code.

## Features

- Unified interface for interacting with multiple broker APIs
- Support for mock broker (for testing) and Alpaca broker
- Configuration management for broker settings
- Order management (placing, cancelling, retrieving)
- Position management
- Account information retrieval
- Market data access

## Architecture

The module follows the Adapter pattern, providing a layer of abstraction between the application and broker-specific APIs:

```
Application → BrokerAdapter → BrokerInterface → Specific Broker Implementation
```

### Key Components

- **BrokerInterface**: Abstract interface defining methods all brokers must implement
- **MockBroker/AlpacaBroker**: Specific implementations of the BrokerInterface
- **BrokerAdapter**: Provides a unified interface to the rest of the application
- **BrokerManager**: Manages broker instances and configuration
- **BrokerFactory**: Creates broker instances based on configuration
- **Config**: Handles loading/saving of broker configuration

## Usage

### Basic Usage

```python
from api.broker_integration.broker_adapter import BrokerAdapter

# Create broker adapter (uses the active broker from config)
broker = BrokerAdapter()

# Connect to broker
broker.connect()

# Get account information
account_info = broker.get_account_info()

# Place an order
order = broker.place_order(
    symbol="AAPL",
    qty=10,
    side="buy",
    order_type="market"
)

# Get positions
positions = broker.get_positions()

# Disconnect
broker.disconnect()
```

### Switching Brokers

```python
# Switch to Alpaca broker
broker.switch_broker("alpaca")

# Now using Alpaca broker for all operations
account_info = broker.get_account_info()  # Gets account info from Alpaca
```

## API Endpoints

The module provides the following Flask API endpoints:

- `GET /api/broker/status`: Get broker connection status
- `POST /api/broker/connect`: Connect to broker
- `POST /api/broker/disconnect`: Disconnect from broker
- `GET /api/broker/account`: Get account information
- `GET /api/broker/positions`: Get all positions
- `GET /api/broker/positions/<symbol>`: Get position for a specific symbol
- `GET /api/broker/orders`: Get all orders
- `GET /api/broker/orders/<order_id>`: Get a specific order
- `POST /api/broker/orders`: Place a new order
- `DELETE /api/broker/orders/<order_id>`: Cancel an order
- `GET /api/broker/market-data/<symbol>`: Get market data for a symbol
- `GET /api/broker/brokers`: Get available brokers
- `POST /api/broker/switch`: Switch active broker
- `GET /api/broker/config`: Get broker configuration
- `PUT /api/broker/config`: Update broker configuration
- `POST /api/broker/credentials`: Update broker credentials
- `GET /api/broker/trade-stats`: Get trading statistics

## Configuration

Broker configuration is stored in `broker_config.json`. The configuration includes:

- Active broker
- Broker-specific settings (API keys, etc.)
- Trading parameters (position sizing, risk management, etc.)

Example configuration:

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
      "api_key": "",
      "api_secret": "",
      "is_paper": true
    }
  }
}
```

## Adding New Brokers

To add support for a new broker:

1. Create a new class that implements the `BrokerInterface`
2. Register the new broker in `register_brokers()` in `__init__.py`
3. Update configuration to include the new broker

## Testing

The module includes unit tests in `tests.py`. Run the tests with:

```
python -m api.broker_integration.tests
```

A demonstration script is also available in `demo.py`. Run it with:

```
python -m api.broker_integration.demo
``` 