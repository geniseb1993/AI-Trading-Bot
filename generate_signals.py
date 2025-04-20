import os
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import random

# Configure API credentials
ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY')
ALPACA_API_SECRET = os.environ.get('ALPACA_API_SECRET')
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'
ALPACA_DATA_URL = 'https://data.alpaca.markets'

# Symbols to process
symbols = ['SPY', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'META', 'AMZN', 'GOOGL', 'QQQ']
short_symbols = ['IBM', 'INTC', 'BA', 'GE', 'XOM', 'CVX', 'PFE', 'MRK', 'VZ', 'T']

def fetch_market_data(symbol, timeframe='1Day', limit=30):
    """Fetch market data from Alpaca API"""
    try:
        headers = {
            'APCA-API-KEY-ID': ALPACA_API_KEY,
            'APCA-API-SECRET-KEY': ALPACA_API_SECRET
        }
        
        url = f"{ALPACA_DATA_URL}/v2/stocks/{symbol}/bars"
        params = {
            'timeframe': timeframe,
            'limit': limit,
            'adjustment': 'raw'
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'bars' in data and data['bars']:
            df = pd.DataFrame(data['bars'])
            # Rename columns to match signal_engine expectations
            df = df.rename(columns={
                'o': 'open',
                'h': 'high',
                'l': 'low',
                'c': 'close',
                'v': 'volume',
                't': 'date'
            })
            # Convert date
            df['date'] = pd.to_datetime(df['date'])
            return df
        else:
            print(f"No data found for {symbol}")
            return None
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def calculate_ema(df, period):
    """Calculate EMA for a dataframe"""
    return df['close'].ewm(span=period, adjust=False).mean()

def calculate_signals(df):
    """Calculate trading signals"""
    df = df.copy()
    df['ema_9'] = calculate_ema(df, 9)
    df['ema_21'] = calculate_ema(df, 21)
    df['pct_change'] = df['close'].pct_change() * 100
    df['avg_volume'] = df['volume'].rolling(window=20).mean()
    df['volume_surge'] = df['volume'] > 1.5 * df['avg_volume']
    df['ema_crossover'] = (df['ema_9'] > df['ema_21']) & (df['ema_9'].shift(1) <= df['ema_21'].shift(1))
    df['momentum_up'] = df['pct_change'] > 0.2

    # Generate signal score (simulated)
    df['signal_score'] = round(7 + random.random() * 3, 2)
    
    return df

def main():
    """Main function to generate signals"""
    print("Generating current buy and short signals...")
    
    # Check if data directory exists
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate buy signals
    buy_signals = []
    for symbol in symbols:
        print(f"Processing {symbol} for buy signals...")
        df = fetch_market_data(symbol)
        if df is not None:
            df_with_signals = calculate_signals(df)
            latest_data = df_with_signals.iloc[-1].copy()
            buy_signals.append({
                'date': latest_data['date'].strftime('%Y-%m-%d'),
                'symbol': symbol,
                'signal_score': latest_data['signal_score'],
                'close': latest_data['close'],
                'ema_9': latest_data['ema_9'],
                'ema_21': latest_data['ema_21'],
                'volume': latest_data['volume']
            })
    
    # Generate short signals
    short_signals = []
    for symbol in short_symbols:
        print(f"Processing {symbol} for short signals...")
        df = fetch_market_data(symbol)
        if df is not None:
            df_with_signals = calculate_signals(df)
            latest_data = df_with_signals.iloc[-1].copy()
            # Negative score for short signals
            short_signals.append({
                'date': latest_data['date'].strftime('%Y-%m-%d'),
                'symbol': symbol,
                'signal_score': -1 * latest_data['signal_score'],
                'close': latest_data['close'],
                'ema_9': latest_data['ema_9'],
                'ema_21': latest_data['ema_21'],
                'volume': latest_data['volume']
            })
    
    # Save to CSV
    buy_signals_df = pd.DataFrame(buy_signals)
    short_signals_df = pd.DataFrame(short_signals)
    
    buy_file = os.path.join(data_dir, 'buy_signals.csv')
    short_file = os.path.join(data_dir, 'short_signals.csv')
    
    buy_signals_df.to_csv(buy_file, index=False)
    short_signals_df.to_csv(short_file, index=False)
    
    print(f"Generated {len(buy_signals)} buy signals and {len(short_signals)} short signals")
    print(f"Saved to {buy_file} and {short_file}")

if __name__ == "__main__":
    main() 