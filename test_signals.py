import os
import pandas as pd
from datetime import datetime

def generate_test_signals():
    # Define symbols
    buy_symbols = ['SPY', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'META', 'AMZN', 'GOOGL', 'QQQ']
    short_symbols = ['IBM', 'INTC', 'BA', 'GE', 'XOM', 'CVX', 'PFE', 'MRK', 'VZ', 'T']
    
    # Generate synthetic signals
    buy_signals = []
    for symbol in buy_symbols:
        base_price = sum(ord(c) for c in symbol) % 400 + 100
        signal = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'symbol': symbol,
            'signal_score': round(7 + (2 * (symbol.count('A') + 1) / 10), 2),
            'close': round(base_price, 2),
            'ema_9': round(base_price * 0.99, 2),
            'ema_21': round(base_price * 0.98, 2),
            'volume': int(base_price * 100000)
        }
        buy_signals.append(signal)
        print(f"Created buy signal for {symbol}: {signal}")
    
    short_signals = []
    for symbol in short_symbols:
        base_price = sum(ord(c) for c in symbol) % 400 + 100
        signal = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'symbol': symbol,
            'signal_score': round(-7 - (2 * (symbol.count('I') + 1) / 10), 2),
            'close': round(base_price, 2),
            'ema_9': round(base_price * 1.01, 2),
            'ema_21': round(base_price * 1.02, 2),
            'volume': int(base_price * 100000)
        }
        short_signals.append(signal)
        print(f"Created short signal for {symbol}: {signal}")
    
    # Convert to DataFrames
    buy_df = pd.DataFrame(buy_signals)
    short_df = pd.DataFrame(short_signals)
    
    print(f"\nBuy DataFrame shape: {buy_df.shape}")
    print(f"Buy DataFrame columns: {buy_df.columns.tolist()}")
    print(f"\nShort DataFrame shape: {short_df.shape}")
    print(f"Short DataFrame columns: {short_df.columns.tolist()}")
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to CSV files
    buy_file = os.path.join(data_dir, 'buy_signals.csv')
    short_file = os.path.join(data_dir, 'short_signals.csv')
    
    buy_df.to_csv(buy_file, index=False)
    short_df.to_csv(short_file, index=False)
    
    print(f"\nSaved buy signals to: {buy_file}")
    print(f"Saved short signals to: {short_file}")
    
    # Verify files
    buy_size = os.path.getsize(buy_file)
    short_size = os.path.getsize(short_file)
    print(f"\nFile sizes:")
    print(f"Buy signals: {buy_size} bytes")
    print(f"Short signals: {short_size} bytes")
    
    # Read back the files
    test_buy_df = pd.read_csv(buy_file)
    test_short_df = pd.read_csv(short_file)
    print(f"\nVerification:")
    print(f"Buy signals read back: {len(test_buy_df)}")
    print(f"Short signals read back: {len(test_short_df)}")

if __name__ == '__main__':
    generate_test_signals() 