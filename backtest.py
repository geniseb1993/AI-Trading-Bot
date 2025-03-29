# backtest.py

import pandas as pd
import matplotlib.pyplot as plt

def simulate_trades(data, buy_signals):
    cash = 10000
    position = 0
    trade_log = []

    for index, row in data.iterrows():
        timestamp = row.name
        price = row['close']
        signal = timestamp in buy_signals.index


        if signal and cash >= price:
            position = cash // price
            cash -= position * price
            trade_log.append((timestamp, 'BUY', price, position))
        elif position > 0:
            cash += position * price
            trade_log.append((timestamp, 'SELL', price, position))
            position = 0

    return cash, trade_log

def run_backtest(data, signals):
    if 'buy_signal' not in signals.columns:
        raise KeyError("❌ 'buy_signal' column not found in signals DataFrame.")

    buy_signals = signals[signals['buy_signal'] == True]

    final_cash, trades = simulate_trades(data, buy_signals)

    print(f"\n💰 Final Cash: ${final_cash:.2f}")
    print("\n📘 Trade Log:")
    for trade in trades:
        print(trade)

    # Plotting results
    plt.figure(figsize=(14, 6))
    plt.plot(data['close'], label='Price')
    plt.scatter(buy_signals.index, buy_signals['close'], label='Buy Signal', marker='^', color='green')
    plt.title('Backtest Results')
    plt.legend()
    plt.show()

# Do NOT call run_backtest() here directly.
# It should only be called from run_pipeline.py or a test script.
