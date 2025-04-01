import pandas as pd
import matplotlib.pyplot as plt

def simulate_trades(data, buy_signals, short_signals):
    """Simulate trading using buy and short signals."""
    cash = 10000
    position = 0
    trade_log = []

    for index, row in data.iterrows():
        timestamp = row.name
        price = row['close']
        buy_signal = timestamp in buy_signals.index
        short_signal = timestamp in short_signals.index

        # Handle Buy Signal
        if buy_signal and cash >= price:
            position = cash // price
            cash -= position * price
            trade_log.append((timestamp, 'BUY', price, position))

        # Handle Short Signal
        elif short_signal and position > 0:
            cash += position * price
            trade_log.append((timestamp, 'SELL', price, position))
            position = 0

        # Sell Position if Still Held
        elif position > 0:
            cash += position * price
            trade_log.append((timestamp, 'SELL', price, position))
            position = 0

    return cash, trade_log

def run_backtest(data, signals):
    """Run backtest based on buy and short signals."""
    if 'buy_signal' not in signals.columns:
        raise KeyError("❌ 'buy_signal' column not found in signals DataFrame.")
    if 'short_signal' not in signals.columns:
        raise KeyError("❌ 'short_signal' column not found in signals DataFrame.")

    buy_signals = signals[signals['buy_signal'] == True]
    short_signals = signals[signals['short_signal'] == True]

    final_cash, trades = simulate_trades(data, buy_signals, short_signals)

    print(f"\n💰 Final Cash: ${final_cash:.2f}")
    print("\n📘 Trade Log:")
    for trade in trades:
        print(trade)

    # Plotting results
    plt.figure(figsize=(14, 6))
    plt.plot(data['close'], label='Price')
    plt.scatter(buy_signals.index, buy_signals['close'], label='Buy Signal', marker='^', color='green')
    plt.scatter(short_signals.index, short_signals['close'], label='Short Signal', marker='v', color='red')
    plt.title('Backtest Results')
    plt.legend()
    plt.show()

# Do NOT call run_backtest() here directly.
# It should only be called from run_pipeline.py or a test script.
