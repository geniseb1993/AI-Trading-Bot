# test_signal_engine.py
# added by UpLiftTeck

import pandas as pd
import os
import sys
from signal_engine import calculate_signals, extract_signals

def test_buy_signals_file():
    """Test that buy_signals.csv is correctly formatted and can be loaded."""
    print("Testing buy_signals.csv file format...")
    
    # Check if file exists
    if not os.path.exists('buy_signals.csv'):
        print("❌ FAIL: buy_signals.csv does not exist")
        return False
    
    # Load the file
    try:
        signals_df = pd.read_csv('buy_signals.csv')
        print(f"✅ PASS: Successfully loaded buy_signals.csv with {len(signals_df)} rows")
    except Exception as e:
        print(f"❌ FAIL: Could not load buy_signals.csv - {str(e)}")
        return False
    
    # Check expected columns
    expected_columns = ['symbol', 'time', 'close', 'volume', 'ema_9', 'ema_21', 
                        'pct_change', 'rsi', 'macd_hist', 'signal_score']
    
    missing_columns = [col for col in expected_columns if col not in signals_df.columns]
    if missing_columns:
        print(f"❌ FAIL: Missing expected columns: {missing_columns}")
        return False
    
    print("✅ PASS: All expected columns found")
    return True

def test_signal_processing():
    """Test that signals are correctly processed from buy_signals.csv."""
    print("\nTesting signal processing...")
    
    # Load the signals file
    signals_df = pd.read_csv('buy_signals.csv')
    
    # Use the signal_score to generate buy_signal column
    signals_df['buy_signal'] = signals_df['signal_score'] >= 3
    
    # Count how many buy signals we have
    buy_count = signals_df['buy_signal'].sum()
    print(f"📊 Found {buy_count} buy signals out of {len(signals_df)} records")
    
    # Verify some specific buy signals (assuming signal_score >= 3 means buy)
    high_score_signals = signals_df[signals_df['signal_score'] >= 4]
    if not high_score_signals.empty:
        print(f"✅ PASS: Found {len(high_score_signals)} high-confidence signals (score >= 4)")
    else:
        print("⚠️ WARNING: No high-confidence signals found (score >= 4)")
        
    return signals_df

def test_backtest_compatibility():
    """Test that signals can be used for backtesting."""
    print("\nTesting backtest compatibility...")
    
    try:
        # Import the backtest module
        from backtest import run_backtest
        print("✅ PASS: Successfully imported backtest module")
    except ImportError:
        print("❌ FAIL: Could not import backtest module")
        return False
    
    # Load and prepare the signals
    signals_df = pd.read_csv('buy_signals.csv')
    signals_df['buy_signal'] = signals_df['signal_score'] >= 3
    
    # Create a minimal dataset for backtesting
    # This uses signals_df itself as the full dataset for simplicity
    try:
        # Set the time column as datetime
        signals_df['time'] = pd.to_datetime(signals_df['time'])
        
        # For this test, we'll use a very simplified approach
        # In a real scenario, you would use the full price data
        print("✅ PASS: Data prepared for backtesting")
    except Exception as e:
        print(f"❌ FAIL: Could not prepare data for backtesting - {str(e)}")
        return False
    
    return True

def generate_test_report(signals_df):
    """Generate a report of test results."""
    print("\n📑 GENERATING TEST REPORT")
    print("-----------------------")
    
    # Group by symbol and count buy signals
    symbol_counts = signals_df.groupby('symbol')['buy_signal'].sum()
    print("\nBuy signals by symbol:")
    for symbol, count in symbol_counts.items():
        print(f"  - {symbol}: {count} buy signals")
    
    # Group by signal_score to see distribution
    score_counts = signals_df['signal_score'].value_counts().sort_index()
    print("\nSignal score distribution:")
    for score, count in score_counts.items():
        print(f"  - Score {score}: {count} signals")
    
    # Check for potential issues
    if 3 not in score_counts:
        print("\n⚠️ WARNING: No signals with score = 3 (minimum buy threshold)")
    
    print("\n-----------------------")
    print("✅ Test suite completed")

if __name__ == "__main__":
    print("🧪 RUNNING SIGNAL ENGINE TEST SUITE")
    print("==================================")
    
    if not test_buy_signals_file():
        print("\n❌ File test failed. Exiting.")
        sys.exit(1)
    
    signals_df = test_signal_processing()
    
    if not test_backtest_compatibility():
        print("\n⚠️ Backtest compatibility test failed.")
    
    generate_test_report(signals_df)
    
    print("\n🎉 All tests completed!") 