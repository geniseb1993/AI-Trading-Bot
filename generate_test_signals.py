import os
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
from signal_engine import calculate_signals, scan_and_save_signals

def fetch_market_data(symbols, period='1mo', interval='1d'):
    """Fetch market data for the given symbols"""
    data_dict = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            df = df.reset_index()
            df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits']
            df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
            data_dict[symbol] = df
            print(f"✅ Fetched data for {symbol}")
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {str(e)}")
    return data_dict

def main():
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Define symbols
    buy_symbols = ['SPY', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'META', 'AMZN', 'GOOGL', 'QQQ']
    short_symbols = ['IBM', 'INTC', 'BA', 'GE', 'XOM', 'CVX', 'PFE', 'MRK', 'VZ', 'T']
    all_symbols = buy_symbols + short_symbols
    
    print("🔄 Fetching market data...")
    data_dict = fetch_market_data(all_symbols)
    
    print("\n📊 Generating signals...")
    scan_and_save_signals(
        data_dict,
        output_buy='data/buy_signals.csv',
        output_short='data/short_signals.csv'
    )
    
    # Verify signals were generated
    try:
        buy_signals = pd.read_csv('data/buy_signals.csv')
        short_signals = pd.read_csv('data/short_signals.csv')
        print(f"\n✅ Generated {len(buy_signals)} buy signals and {len(short_signals)} short signals")
        
        # Print sample of signals
        if not buy_signals.empty:
            print("\n📈 Sample Buy Signals:")
            print(buy_signals[['symbol', 'close', 'signal_score']].head())
        
        if not short_signals.empty:
            print("\n📉 Sample Short Signals:")
            print(short_signals[['symbol', 'close', 'signal_score']].head())
            
    except Exception as e:
        print(f"\n❌ Error reading signals: {str(e)}")

if __name__ == "__main__":
    main() 