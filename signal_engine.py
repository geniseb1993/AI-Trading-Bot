# signal_engine.py
from config import BUY_ONLY

import pandas as pd

# --- Core Signal Calculations ---

def calculate_ema(df, span):
    return df['close'].ewm(span=span, adjust=False).mean()

# --- Indicator Calculations ---
def calculate_ema(df, span):
    return df['close'].ewm(span=span, adjust=False).mean()

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df['rsi'] = rsi
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    exp1 = df['close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    df['macd'] = macd
    df['macd_signal'] = signal_line
    df['macd_hist'] = macd - signal_line
    return df

def calculate_vwap(df):
    df['vwap_numerator'] = (df['close'] * df['volume']).cumsum()
    df['vwap_denominator'] = df['volume'].cumsum()
    df['vwap'] = df['vwap_numerator'] / df['vwap_denominator']
    return df

# --- Signal Logic ---
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

    return df


# --- Signal Enhancers ---

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df['rsi'] = rsi
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    exp1 = df['close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    df['macd'] = macd
    df['macd_signal'] = signal_line
    df['macd_hist'] = macd - signal_line
    return df

def calculate_vwap(df):
    df['vwap_numerator'] = (df['close'] * df['volume']).cumsum()
    df['vwap_denominator'] = df['volume'].cumsum()
    df['vwap'] = df['vwap_numerator'] / df['vwap_denominator']
    return df

def add_short_signals(df):
    df['ema_crossdown'] = (df['ema_9'] < df['ema_21']) & (df['ema_9'].shift(1) >= df['ema_21'].shift(1))
    df['momentum_down'] = df['pct_change'] < -0.3
    df['short_signal'] = df['ema_crossdown'] & df['volume_surge'] & df['momentum_down']
    return df

def score_signals(df):
    df['signal_score'] = 0
    df.loc[df['ema_crossover'], 'signal_score'] += 1
    df.loc[df['volume_surge'], 'signal_score'] += 1
    df.loc[df['momentum_up'], 'signal_score'] += 1
    df.loc[df['rsi'] < 30, 'signal_score'] += 1
    df.loc[df['macd_hist'] > 0, 'signal_score'] += 1
    return df

def enhance_signals(df):
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_vwap(df)
    df = add_short_signals(df)
    df = score_signals(df)
    return df

# --- Signal Extraction Utilities ---

def extract_signals(df):
    if 'buy_signal' not in df.columns:
        print("Signal column not found. Run calculate_signals() first.")
        return pd.DataFrame()
    return df[df['buy_signal']][['symbol', 'time', 'close', 'volume', 'ema_9', 'ema_21', 'pct_change', 'rsi', 'macd_hist', 'signal_score']]

def extract_short_signals(df):
    if 'short_signal' not in df.columns:
        print("Signal column not found. Run calculate_signals() first.")
        return pd.DataFrame()
    return df[df['short_signal']][['symbol', 'time', 'close', 'volume', 'ema_9', 'ema_21', 'pct_change', 'rsi', 'macd_hist', 'signal_score']]

# --- Optional Alert / Autotrade Triggers ---

def trigger_alerts(signals_df):
    for _, row in signals_df.iterrows():
        print(f"🚨 ALERT: Buy signal for {row['symbol']} at {row['time']} (Price: ${row['close']})")

def trigger_autotrade(signals_df):
    for _, row in signals_df.iterrows():
        print(f"🤖 Executing paper trade for {row['symbol']} at {row['close']}")  # Replace with Alpaca trade execution

# --- Scanner/Runner Utility ---

def scan_and_save_signals(data_dict, output_buy='buy_signals.csv', output_short='short_signals.csv'):
    buy_signals_list = []
    short_signals_list = []

    for symbol, df in data_dict.items():
        df['symbol'] = symbol
        df = calculate_signals(df)

        buy_signals = extract_signals(df)
        short_signals = extract_short_signals(df)

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
        symbol = os.path.basename(file).split(".")[0]
        df = pd.read_csv(file, parse_dates=["time"])
        symbol_data[symbol] = df

    scan_and_save_signals(symbol_data)
    print("✅ Signal scan complete.")
