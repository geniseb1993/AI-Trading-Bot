import os
import pandas as pd
from datetime import datetime

# Create test data
buy_signals = [
    {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'symbol': 'TEST1',
        'signal_score': 7.5,
        'close': 100.0,
        'ema_9': 99.0,
        'ema_21': 98.0,
        'volume': 1000000
    }
]

short_signals = [
    {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'symbol': 'TEST2',
        'signal_score': -7.5,
        'close': 200.0,
        'ema_9': 201.0,
        'ema_21': 202.0,
        'volume': 2000000
    }
]

# Convert to DataFrames
buy_df = pd.DataFrame(buy_signals)
short_df = pd.DataFrame(short_signals)

print("Buy DataFrame:")
print(buy_df)
print("\nShort DataFrame:")
print(short_df)

# Create data directory if it doesn't exist
data_dir = os.path.join(os.getcwd(), 'data')
os.makedirs(data_dir, exist_ok=True)

# Save to CSV files
buy_file = os.path.join(data_dir, 'buy_signals.csv')
short_file = os.path.join(data_dir, 'short_signals.csv')

print(f"\nSaving to files:")
print(f"Buy signals: {buy_file}")
print(f"Short signals: {short_file}")

buy_df.to_csv(buy_file, index=False)
short_df.to_csv(short_file, index=False)

# Verify files
buy_size = os.path.getsize(buy_file)
short_size = os.path.getsize(short_file)
print(f"\nFile sizes:")
print(f"Buy signals: {buy_size} bytes")
print(f"Short signals: {short_size} bytes")

# Read back the files
test_buy_df = pd.read_csv(buy_file)
test_short_df = pd.read_csv(short_file)
print(f"\nRead back data:")
print("Buy signals:")
print(test_buy_df)
print("\nShort signals:")
print(test_short_df) 