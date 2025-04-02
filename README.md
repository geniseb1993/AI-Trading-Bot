# AI Trading Bot

## Overview
AI Trading Bot is a Python-based algorithmic trading system that uses technical indicators to generate buy and sell signals for stocks and ETFs.

## Recent Fixes and Improvements
<!-- added or modified byUpLiftTeck -->
### Signal Engine Improvements (2025-03-29)
- **Fixed buy_signal handling**: Modified the `extract_signals()` function to automatically create a buy_signal column based on signal_score when it's missing.
- **Added test scripts**: Created comprehensive test scripts to validate the signal engine and full pipeline.

## Features
- Fetches real-time and historical stock data
- Calculates technical indicators (EMA, RSI, MACD)
- Generates buy and sell signals based on configurable criteria
- Backtests trading strategies on historical data

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

## Usage
1. Update configuration in `config.py`
2. Run the pipeline with `python run_pipeline.py`
3. View generated signals in `buy_signals.csv` and `short_signals.csv`
4. Analyze backtest results in `backtest_results.csv`
