# backtest.py

import pandas as pd
import matplotlib.pyplot as plt

def simulate_trades(data, buy_signals):
    cash = 10000
    position = 0
    trade_log = []

    # Change by UpLiftTeck: Modified the signal checking logic to fix KeyError
    # Original code:
    # for index, row in data.iterrows():
    #     timestamp = row.name
    #     price = row['close']
    #     signal = timestamp in buy_signals.index
    
    # Set the 'time' column as the index for buy_signals to make comparison easier
    if 'time' in buy_signals.columns:
        buy_signals_indexed = buy_signals.set_index('time')
    else:
        buy_signals_indexed = buy_signals
        
    for index, row in data.iterrows():
        # Using row['time'] instead of row.name for timestamp comparison
        if 'time' in row:
            timestamp = row['time']
        else:
            timestamp = row.name
            
        price = row['close']
        signal = timestamp in buy_signals_indexed.index


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

    # Change by UpLiftTeck: Modified the plotting code to handle different index formats
    # Original code:
    # plt.figure(figsize=(14, 6))
    # plt.plot(data['close'], label='Price')
    # plt.scatter(buy_signals.index, buy_signals['close'], label='Buy Signal', marker='^', color='green')
    # plt.title('Backtest Results')
    # plt.legend()
    # plt.show()
    
    # New plotting code that handles different index situations
    plt.figure(figsize=(14, 6))
    
    # Handle the case where 'time' might be a column rather than the index
    if 'time' in data.columns:
        x_data = data['time']
    else:
        x_data = data.index
        
    plt.plot(x_data, data['close'], label='Price')
    
    # Handle buy signals plotting
    if 'time' in buy_signals.columns:
        x_signals = buy_signals['time']
    else:
        x_signals = buy_signals.index
        
    plt.scatter(x_signals, buy_signals['close'], label='Buy Signal', marker='^', color='green')
    plt.title('Backtest Results')
    plt.legend()
    plt.show()
    
    # Return results as DataFrame for saving to CSV
    results_df = pd.DataFrame(trades, columns=['timestamp', 'action', 'price', 'quantity'])
    return results_df

# Do NOT call run_backtest() here directly.
# It should only be called from run_pipeline.py or a test script.
