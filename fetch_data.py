from config import API_KEY, API_SECRET, BASE_URL
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import pytz
import pandas as pd
from signal_engine import calculate_signals, extract_signals

# Initialize API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')
eastern = pytz.timezone('US/Eastern')

# Default: Today's date
def get_today_range():
    now = datetime.now(eastern)
    today = now.date()
    return today

# Fetch bars for a session
def fetch_bars(symbol, start_dt, end_dt, timeframe='1Min'):
    try:
        bars = api.get_bars(symbol, timeframe, start=start_dt.isoformat(), end=end_dt.isoformat())
        return pd.DataFrame([{
            'symbol': symbol,
            'time': bar.t,
            'open': bar.o,
            'high': bar.h,
            'low': bar.l,
            'close': bar.c,
            'volume': bar.v
        } for bar in bars])
    except Exception as e:
        print(f"Error fetching bars for {symbol}: {e}")
        return pd.DataFrame()

# Main function to fetch data
def fetch_data(symbols, start_date=None, end_date=None):
    all_data = []

    # Use today's date if none provided
    if not start_date:
        start_date = get_today_range()
    if not end_date:
        end_date = start_date

    # Iterate through dates in range
    date = start_date
    while date <= end_date:
        print(f"\n📅 Fetching data for {date.strftime('%Y-%m-%d')}")

        # Time windows for that day
        pre_start = eastern.localize(datetime.combine(date, datetime.min.time()) + timedelta(hours=4))
        market_open = eastern.localize(datetime.combine(date, datetime.min.time()) + timedelta(hours=9, minutes=30))
        now_end = eastern.localize(datetime.combine(date, datetime.min.time()) + timedelta(hours=16))

        for symbol in symbols:
            print(f"\n🔹 {symbol} — Premarket")
            pre_df = fetch_bars(symbol, pre_start, market_open)
            print(pre_df.tail(2))
            
            print(f"🔸 {symbol} — Regular Market")
            reg_df = fetch_bars(symbol, market_open, now_end)
            print(reg_df.tail(2))

            # Append to full dataset
            all_data.append(pre_df)
            all_data.append(reg_df)

        date += timedelta(days=1)

    return pd.concat(all_data, ignore_index=True)

# Running the fetch function and signal engine
if __name__ == "__main__":
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
