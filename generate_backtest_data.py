import pandas as pd
import os
import random
from datetime import datetime, timedelta

def generate_realistic_backtest_data():
    """Generate realistic backtest data and save to CSV files"""
    # Get a list of common stock symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'AMD', 'META', 'PLTR', 'SPY', 'QQQ', 'INTC', 'JPM', 'BAC']
    
    # Generate 30 days of data with 2-3 trades per day
    now = datetime.now()
    dates = [(now - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    
    # Create an empty list to hold our trade data
    trades = []
    
    # Generate trade data
    for date_idx, date in enumerate(dates):
        # Pick 2-3 random symbols for this day
        day_symbols = random.sample(symbols, min(3, len(symbols)))
        
        for symbol in day_symbols:
            # Generate realistic prices based on the symbol
            if symbol == 'AAPL':
                base_price = 180.0
            elif symbol == 'MSFT':
                base_price = 320.0
            elif symbol == 'GOOGL':
                base_price = 140.0
            elif symbol == 'AMZN':
                base_price = 135.0
            elif symbol == 'TSLA':
                base_price = 230.0
            elif symbol == 'NVDA':
                base_price = 450.0
            elif symbol == 'AMD':
                base_price = 120.0
            elif symbol == 'META':
                base_price = 330.0
            elif symbol == 'PLTR':
                base_price = 25.0
            elif symbol == 'SPY':
                base_price = 460.0
            elif symbol == 'QQQ':
                base_price = 385.0
            elif symbol == 'INTC':
                base_price = 35.0
            elif symbol == 'JPM':
                base_price = 200.0
            elif symbol == 'BAC':
                base_price = 40.0
            else:
                base_price = 100.0
            
            # Determine direction (long or short)
            direction = 'long' if random.random() > 0.3 else 'short'
            
            # Add some randomness to the base price
            entry_price = round(base_price * (1 + (random.random() - 0.5) * 0.05), 2)
            
            # Determine if this trade is a winner or loser
            is_winner = random.random() > 0.35  # 65% win rate
            
            # Exit price depends on direction and whether it's a winner
            if direction == 'long':
                if is_winner:
                    exit_price = round(entry_price * (1 + random.random() * 0.1), 2)  # Up to 10% gain
                else:
                    exit_price = round(entry_price * (1 - random.random() * 0.05), 2)  # Up to 5% loss
            else:  # short
                if is_winner:
                    exit_price = round(entry_price * (1 - random.random() * 0.1), 2)  # Up to 10% gain
                else:
                    exit_price = round(entry_price * (1 + random.random() * 0.05), 2)  # Up to 5% loss
            
            # Determine quantity based on price
            quantity = 10  # Fixed quantity for simplicity
            
            # Calculate profit
            if direction == 'long':
                profit = round((exit_price - entry_price) * quantity, 2)
                profit_percent = round((exit_price - entry_price) / entry_price * 100, 2)
            else:
                profit = round((entry_price - exit_price) * quantity, 2)
                profit_percent = round((entry_price - exit_price) / entry_price * 100, 2)
            
            # Determine exit reason
            exit_reason = 'take_profit' if is_winner else 'stop_loss'
            
            # Exit date is 1-3 days after entry
            exit_date = (datetime.strptime(date, '%Y-%m-%d') + 
                        timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d')
            
            # Add the trade to our list
            trades.append({
                'symbol': symbol,
                'entry_date': date,
                'exit_date': exit_date,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'quantity': quantity,
                'direction': direction,
                'profit': profit,
                'profit_percent': profit_percent,
                'trade_outcome': 'win' if is_winner else 'loss',
                'exit_reason': exit_reason
            })
    
    # Create DataFrame from our trades
    backtest_results = pd.DataFrame(trades)
    
    # Ensure output directories exist
    os.makedirs('api', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Save to multiple locations to ensure the frontend can find it
    backtest_results.to_csv('api/backtest_results.csv', index=False)
    backtest_results.to_csv('data/backtest_results.csv', index=False)
    backtest_results.to_csv('backtest_results.csv', index=False)
    
    print(f"Generated {len(backtest_results)} backtest results and saved to CSV files")
    return backtest_results

if __name__ == "__main__":
    generate_realistic_backtest_data() 