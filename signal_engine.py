import pandas as pd
from config import BUY_ONLY

# --- Indicator Calculations ---
def calculate_ema(dataframe, span):
    """Calculate Exponential Moving Average (EMA)."""
    return dataframe['close'].ewm(span=span, adjust=False).mean()

def calculate_rsi(dataframe, period=14):
    """Calculate Relative Strength Index (RSI)."""
    delta = dataframe['close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    dataframe['rsi'] = rsi
    return dataframe

def calculate_macd(dataframe, fast=12, slow=26, signal=9):
    """Calculate MACD indicator."""
    exp1 = dataframe['close'].ewm(span=fast, adjust=False).mean()
    exp2 = dataframe['close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    dataframe['macd'] = macd
    dataframe['macd_signal'] = signal_line
    dataframe['macd_hist'] = macd - signal_line
    return dataframe

def calculate_vwap(dataframe):
    """Calculate Volume Weighted Average Price (VWAP)."""
    dataframe['vwap_numerator'] = (dataframe['close'] * dataframe['volume']).cumsum()
    dataframe['vwap_denominator'] = dataframe['volume'].cumsum()
    dataframe['vwap'] = dataframe['vwap_numerator'] / dataframe['vwap_denominator']
    return dataframe

# --- Signal Logic ---
<<<<<<< HEAD
def calculate_signals(dataframe):
    """Calculate buy and short signals."""
    dataframe = dataframe.copy()
    dataframe['ema_9'] = calculate_ema(dataframe, 9)
    dataframe['ema_21'] = calculate_ema(dataframe, 21)
    dataframe['pct_change'] = dataframe['close'].pct_change() * 100
    dataframe['avg_volume'] = dataframe['volume'].rolling(window=20).mean()
    dataframe['volume_surge'] = dataframe['volume'] > 1.5 * dataframe['avg_volume']
    dataframe['ema_crossover'] = (
        (dataframe['ema_9'] > dataframe['ema_21']) &
        (dataframe['ema_9'].shift(1) <= dataframe['ema_21'].shift(1))
    )
    dataframe['momentum_up'] = dataframe['pct_change'] > 0.2
=======
def calculate_signals(df):
    df = df.copy()
    df['ema_9'] = calculate_ema(df, 9)
    df['ema_21'] = calculate_ema(df, 21)
    df['pct_change'] = df['close'].pct_change() * 100
    df['avg_volume'] = df['volume'].rolling(window=20).mean()
    df['volume_surge'] = df['volume'] > 1.5 * df['avg_volume']
    df['ema_crossover'] = (df['ema_9'] > df['ema_21']) & (df['ema_9'].shift(1) <= df['ema_21'].shift(1))
    df['momentum_up'] = df['pct_change'] > 0.2

    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_vwap(df)

    df['signal_score'] = 0
    df.loc[df['ema_crossover'], 'signal_score'] += 1
    df.loc[df['volume_surge'], 'signal_score'] += 1
    df.loc[df['momentum_up'], 'signal_score'] += 1
    df.loc[df['rsi'] < 40, 'signal_score'] += 1
    df.loc[df['macd_hist'] > 0, 'signal_score'] += 1

    df['buy_signal'] = df['signal_score'] >= 3

    if not BUY_ONLY:
        df['short_signal'] = (
        (df['ema_9'] < df['ema_21']) &
        (df['ema_9'].shift(1) >= df['ema_21'].shift(1)) &
        (df['volume'] > 2 * df['avg_volume']) &
        (df['pct_change'] <= -0.3)
    )
    else:
        df['short_signal'] = False
>>>>>>> origin/main

    dataframe = calculate_rsi(dataframe)
    dataframe = calculate_macd(dataframe)
    dataframe = calculate_vwap(dataframe)

    dataframe['signal_score'] = 0
    dataframe.loc[dataframe['ema_crossover'], 'signal_score'] += 1
    dataframe.loc[dataframe['volume_surge'], 'signal_score'] += 1
    dataframe.loc[dataframe['momentum_up'], 'signal_score'] += 1
    dataframe.loc[dataframe['rsi'] < 40, 'signal_score'] += 1
    dataframe.loc[dataframe['macd_hist'] > 0, 'signal_score'] += 1

    # Debugging: Checking signal score calculations
    print(f"Signal Scores for {dataframe['symbol'].iloc[0]}:\n", dataframe[['symbol', 'signal_score']].head())

    dataframe['buy_signal'] = dataframe['signal_score'] >= 3

    # Debugging: Checking the buy_signal column
    print(f"Buy Signals for {dataframe['symbol'].iloc[0]}:\n", dataframe[['symbol', 'buy_signal']].head())

    if not BUY_ONLY:
        dataframe['short_signal'] = (
            (dataframe['ema_9'] < dataframe['ema_21']) &
            (dataframe['ema_9'].shift(1) >= dataframe['ema_21'].shift(1)) &
            (dataframe['volume'] > 2 * dataframe['avg_volume']) &
            (dataframe['pct_change'] <= -0.3)
        )
    else:
        dataframe['short_signal'] = False

    return dataframe

# --- Signal Extraction Utilities ---
<<<<<<< HEAD
def extract_signals(dataframe):
    """Return DataFrame containing only buy signals."""
    if 'buy_signal' not in dataframe.columns:
        print("Signal column not found. Run calculate_signals() first.")
        return pd.DataFrame()
    return dataframe[dataframe['buy_signal']][['symbol', 'time', 'close', 'volume', 'ema_9', 'ema_21', 'pct_change', 'rsi', 'macd_hist', 'signal_score']]
=======

def extract_signals(df):
    if 'buy_signal' not in df.columns and 'signal_score' in df.columns:
        print("Buy signal column not found. Creating it based on signal_score.")
        df['buy_signal'] = df['signal_score'] >= 3
    elif 'buy_signal' not in df.columns:
        print("Signal column not found. Run calculate_signals() first.")
        return pd.DataFrame()
        
    return df[df['buy_signal']][['symbol', 'time', 'close', 'volume', 'ema_9', 'ema_21', 'pct_change', 'rsi', 'macd_hist', 'signal_score', 'buy_signal']]
>>>>>>> origin/main

def extract_short_signals(dataframe):
    """Return DataFrame containing only short signals."""
    if 'short_signal' not in dataframe.columns:
        print("Signal column not found. Run calculate_signals() first.")
        return pd.DataFrame()
    return dataframe[dataframe['short_signal']][['symbol', 'time', 'close', 'volume', 'ema_9', 'ema_21', 'pct_change', 'rsi', 'macd_hist', 'signal_score']]

# --- Optional Alert / Autotrade Triggers ---
def trigger_alerts(signals_df):
    """Print alert messages for each buy signal."""
    for _, row in signals_df.iterrows():
        print(f"🚨 ALERT: Buy signal for {row['symbol']} at {row['time']} (Price: ${row['close']})")

def trigger_autotrade(signals_df):
    """Simulate auto-trading logic (to be replaced with Alpaca API)."""
    for _, row in signals_df.iterrows():
        print(f"🤖 Executing paper trade for {row['symbol']} at {row['close']}")

# --- Scanner/Runner Utility ---
def scan_and_save_signals(data_dict, output_buy='buy_signals.csv', output_short='short_signals.csv'):
    """Run signal scan and save results to CSV files."""
    buy_signals_list = []
    short_signals_list = []

    for symbol, df_data in data_dict.items():
        df_data['symbol'] = symbol
        df_data = calculate_signals(df_data)

        buy_signals = extract_signals(df_data)
        short_signals = extract_short_signals(df_data)

        if not buy_signals.empty:
            buy_signals_list.append(buy_signals)
        if not short_signals.empty:
            short_signals_list.append(short_signals)

    if buy_signals_list:
        all_buy_signals = pd.concat(buy_signals_list)
        all_buy_signals.to_csv(output_buy, index=False)
        trigger_alerts(all_buy_signals)

    if short_signals_list:
        all_short_signals = pd.concat(short_signals_list)
        all_short_signals.to_csv(output_short, index=False)

# --- CLI Entry Point ---
if __name__ == "__main__":
    import os
    import glob

    print("🔍 Running signal scanner from CSVs...")

    csv_files = glob.glob("data/*.csv")
    symbol_data = {}

    for file in csv_files:
        sym = os.path.basename(file).split(".")[0]
        df_csv = pd.read_csv(file, parse_dates=["time"])
        symbol_data[sym] = df_csv

    scan_and_save_signals(symbol_data)
    print("✅ Signal scan complete.")
