from datetime import date
from fetch_data import fetch_data
from signal_engine import calculate_signals, extract_signals
from backtest import run_backtest

if __name__ == '__main__':
    symbols = ['QQQ', 'SPY', 'TSLA']
    data = fetch_data(symbols, start_date=date(2025, 3, 21), end_date=date(2025, 3, 28))
    print("\n✅ All data fetched successfully.\n")
    print(data.tail())

    # Run the signal engine
    data_with_signals = calculate_signals(data)
    signals = extract_signals(data_with_signals)
    print("\n📈 Detected Buy Signals")
    print(signals.tail())

    # Optional: Save signals to CSV
    signals.to_csv("buy_signals.csv", index=False)
    print("\n💾 Buy signals saved to 'buy_signals.csv'")

    # Optional: Save short signals to CSV
    short_signals = data_with_signals[data_with_signals['short_signal']]
    short_signals.to_csv("short_signals.csv", index=False)
    print("\n💾 Short signals saved to 'short_signals.csv'")

    # Running the backtest after signals
    backtest_results = run_backtest(data_with_signals, signals)

    # Optional: Save backtest results to CSV
    backtest_results.to_csv("backtest_results.csv", index=False)
    print("\n📊 Backtest results saved to 'backtest_results.csv'")
