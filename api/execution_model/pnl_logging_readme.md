# PnL Logging System

## Overview

The PnL (Profit and Loss) Logging System tracks trade performance metrics for the AI Trading Bot. It logs detailed information for individual trades and calculates daily performance statistics. All data is stored in CSV format for easy access and analysis.

## Features

- **Trade-Level Logging**: Records details of each trade including entry/exit prices, position size, and P&L
- **Daily Performance Metrics**: Calculates and stores aggregated metrics like win rate, total P&L, and drawdown
- **Historical Analysis**: Provides methods to retrieve and filter historical trade data
- **Real-time Updates**: Updates metrics automatically when trades are executed
- **Integration with Execution Algorithm**: Seamlessly works with the core trading system

## File Structure

- `trades.csv`: Contains detailed information for each individual trade
- `daily_pnl.csv`: Contains daily aggregated performance metrics

## Trade Fields

The following fields are logged for each trade:

| Field           | Description                                       |
|-----------------|---------------------------------------------------|
| timestamp       | Date and time when the trade was closed           |
| symbol          | Trading symbol (e.g., AAPL, MSFT)                 |
| side            | Trade direction (LONG or SHORT)                   |
| entry_price     | Price at which the position was entered           |
| exit_price      | Price at which the position was closed            |
| quantity        | Size of the position                              |
| pnl             | Absolute profit or loss amount                    |
| pnl_percentage  | Profit or loss as a percentage of investment      |
| trade_duration  | Time duration of the trade in minutes             |
| strategy_name   | Strategy used for the trade                       |
| notes           | Additional information about the trade            |

## Daily Metrics

The following metrics are calculated daily:

| Field           | Description                                       |
|-----------------|---------------------------------------------------|
| date            | The date for which metrics are calculated         |
| total_trades    | Total number of trades for the day                |
| winning_trades  | Number of profitable trades                       |
| losing_trades   | Number of unprofitable trades                     |
| win_rate        | Percentage of winning trades                      |
| total_pnl       | Total profit/loss for the day                     |
| average_pnl     | Average profit/loss per trade                     |
| max_drawdown    | Maximum peak-to-trough decline                    |
| profit_factor   | Ratio of gross profit to gross loss               |
| notes           | Additional notes for the day                      |

## Usage

### Configuration

The PnL logging system is configured in the `config.py` file under the `pnl_logging` section:

```python
"pnl_logging": {
    "enabled": True,
    "log_to_csv": True,
    "logs_directory": "data/logs",
    "trade_log_file": "trades.csv",
    "daily_pnl_file": "daily_pnl.csv",
    "backup_enabled": True,
    "backup_frequency_days": 7,
    "auto_calculate_daily": True,
    "export_to_google_sheets": False,
    "google_sheets_id": "",
    "retention_period_days": 365
}
```

### Integration with Execution Algorithm

The PnL Logger is automatically instantiated in the `ExecutionAlgorithm` class and logs trades when they are closed:

```python
def _close_trade(self, trade, close_price, reason):
    # Calculate P&L and create closed trade record...
    
    # Log trade to CSV
    self.pnl_logger.log_trade(closed_trade)
    
    # Log trade result
    logger.info(f"Closed {direction} trade for {symbol} at {close_price:.4f} with P&L: ${pnl:.2f}")
```

### Retrieving Trade History

You can retrieve the trade history with optional filtering:

```python
# Get all trades for a specific symbol
apple_trades = pnl_logger.get_trade_history(symbol='AAPL')

# Get trades for a date range
start_date = date(2025, 4, 1)
end_date = date(2025, 4, 15)
recent_trades = pnl_logger.get_trade_history(start_date=start_date, end_date=end_date)

# Limit the number of results
last_10_trades = pnl_logger.get_trade_history(limit=10)
```

### Retrieving Daily Statistics

You can retrieve daily performance statistics:

```python
# Get stats for a date range
start_date = date(2025, 4, 1)
daily_stats = pnl_logger.get_daily_stats(start_date=start_date)
```

## Testing

You can test the PnL logging functionality using the provided test script:

```bash
python test_pnl_logging.py
```

This will generate sample trades and demonstrate the logging functionality.

## Visualization

The CSV files can be imported into tools like Excel, Google Sheets, or pandas for visualization and further analysis. Since the data is stored in standard CSV format, it's compatible with most data analysis tools. 