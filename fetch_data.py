from datetime import datetime
import pandas as pd
import pytz
from alpaca_trade_api.rest import REST
from config import API_KEY, API_SECRET, BASE_URL, SYMBOLS
from signal_engine import calculate_signals, extract_signals, extract_short_signals, trigger_alerts
from backtest import run_backtest
import pdb  # Added Python Debugger for debugging

def fetch_data_for_symbol(api, symbol, start, end):
    """Fetch minute-level bars for a given symbol and date range."""
    try:
        bars = api.get_bars(symbol, timeframe="1Min", start=start, end=end).df
        print(f"Fetched bars for {symbol}: {bars.head()}")  # Debugging: Check fetched data
        if 'symbol' not in bars.columns:
            bars['symbol'] = symbol  # Manually assign symbol if it's missing
        bars = bars.reset_index()
        return bars[['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']].rename(columns={'timestamp': 'time'})
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()


def fetch_all_data(start, end):
    """Fetch data for all configured symbols."""
    api = REST(API_KEY, API_SECRET, BASE_URL)
    data = {}
    for symbol in SYMBOLS:
        df = fetch_data_for_symbol(api, symbol, start, end)
        if not df.empty:
            df['time'] = pd.to_datetime(df['time'])
            df = df.sort_values('time')
            data[symbol] = df
    return data

def main():
    """Main pipeline: fetch data, calculate signals, and optionally run backtest."""
    eastern = pytz.timezone("US/Eastern")
    today = datetime.now(eastern).date()
    start = f"{today}T04:00:00-05:00"
    end = f"{today}T20:00:00-05:00"

    print(f"\n📅 Fetching data for {today}\n")
    data = fetch_all_data(start, end)

    all_signals = []
    for symbol, df in data.items():
        print(f"Processing data for {symbol}...")
        df = calculate_signals(df)

        # Debugging: Add pdb here to inspect the dataframe before we check for buy_signal
        pdb.set_trace()

        # Ensure 'buy_signal' column exists after calculation
        if 'buy_signal' not in df.columns:
            print(f"❌ 'buy_signal' column is missing in {symbol}. Skipping.")
            continue

        # Check if 'buy_signal' exists for this symbol and print it
        print(f"Checking 'buy_signal' after calculation for {symbol}:\n", df[['symbol', 'buy_signal']].head())

        buy_signals = extract_signals(df)
        short_signals = extract_short_signals(df)

        if not buy_signals.empty:
            all_signals.append(buy_signals)

        if not short_signals.empty:
            all_signals.append(short_signals)

    if all_signals:
        signals_df = pd.concat(all_signals)

        # Debugging: Add pdb here to inspect signals_df before passing to backtest
        pdb.set_trace()

        # Debugging: Check if 'buy_signal' is present in signals_df before passing to backtest
        print(f"📊 Checking the contents of signals_df:\n", signals_df.head())

        signals_df.to_csv("all_signals.csv", index=False)

        # Optional alerting or backtest trigger
        trigger_alerts(signals_df)

        # Debugging: Check 'buy_signal' column before backtest
        print(f"Checking 'buy_signal' column in signals_df:\n", signals_df[['symbol', 'buy_signal']].head())

        run_backtest(data, signals_df)


if __name__ == "__main__":
    main()
