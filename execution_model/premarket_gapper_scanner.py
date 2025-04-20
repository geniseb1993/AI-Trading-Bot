"""
Pre-Market Gapper Scanner Module

This module identifies stocks with significant pre-market price gaps and volume,
which are often candidates for morning momentum trades.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import time

logger = logging.getLogger(__name__)

class PreMarketGapperScanner:
    """
    Scanner for identifying stocks with significant pre-market price gaps
    """
    
    def __init__(self, config=None):
        """
        Initialize the Pre-Market Gapper Scanner
        
        Args:
            config: Configuration dictionary with parameters
        """
        self.config = config or {}
        
        # Default configuration
        self.min_gap_percent = self.config.get('min_gap_percent', 2.0)  # Minimum gap % to be significant
        self.min_volume_ratio = self.config.get('min_volume_ratio', 1.5)  # Minimum pre-market volume vs avg
        self.min_price = self.config.get('min_price', 5.0)  # Minimum stock price
        self.max_price = self.config.get('max_price', 500.0)  # Maximum stock price
        self.scan_symbols = self.config.get('scan_symbols', [])  # Specific symbols to scan, empty = all
        self.exclude_symbols = self.config.get('exclude_symbols', [])  # Symbols to exclude
        self.max_alerts = self.config.get('max_alerts', 10)  # Maximum number of alerts to return
        self.sort_by = self.config.get('sort_by', 'gap_percent')  # Sorting criteria
        
        # Market open time
        self.market_open_time = self.config.get('market_open_time', '09:30')
        
        # Internal state
        self.gap_alerts = {
            'gap_up': [],
            'gap_down': []
        }
        self.last_scan_time = None
        
        logger.info(f"Pre-Market Gapper Scanner initialized with min gap: {self.min_gap_percent}%")
        
    def update_config(self, config):
        """
        Update scanner configuration
        
        Args:
            config: New configuration dictionary
        """
        self.config.update(config)
        self.min_gap_percent = self.config.get('min_gap_percent', 2.0)
        self.min_volume_ratio = self.config.get('min_volume_ratio', 1.5)
        self.min_price = self.config.get('min_price', 5.0)
        self.max_price = self.config.get('max_price', 500.0)
        self.scan_symbols = self.config.get('scan_symbols', [])
        self.exclude_symbols = self.config.get('exclude_symbols', [])
        self.max_alerts = self.config.get('max_alerts', 10)
        self.sort_by = self.config.get('sort_by', 'gap_percent')
        self.market_open_time = self.config.get('market_open_time', '09:30')
        
        logger.info("Pre-Market Gapper Scanner configuration updated")
    
    def scan_pre_market(self, market_data, previous_day_data):
        """
        Scan for pre-market gaps
        
        Args:
            market_data: Dictionary of pre-market data by symbol
            previous_day_data: Dictionary of previous day's data by symbol
            
        Returns:
            Dictionary with gap_up and gap_down alerts
        """
        self.last_scan_time = datetime.now()
        self.gap_alerts = {'gap_up': [], 'gap_down': []}
        
        logger.info("Scanning for pre-market gaps...")
        
        # Check if we're actually in pre-market hours
        current_time = datetime.now().strftime('%H:%M')
        if current_time >= self.market_open_time:
            logger.warning(f"Current time {current_time} is after market open {self.market_open_time}")
            return self.gap_alerts
            
        # Get list of symbols to scan
        symbols = list(market_data.keys())
        
        # Filter symbols if specified
        if self.scan_symbols:
            symbols = [s for s in symbols if s in self.scan_symbols]
            
        # Exclude symbols if specified
        if self.exclude_symbols:
            symbols = [s for s in symbols if s not in self.exclude_symbols]
            
        logger.info(f"Scanning {len(symbols)} symbols for pre-market gaps")
        
        for symbol in symbols:
            # Skip if we don't have previous day data
            if symbol not in previous_day_data:
                continue
                
            try:
                # Get pre-market data
                pm_data = market_data[symbol]
                
                # Get previous day's data
                prev_data = previous_day_data[symbol]
                
                # Skip if data is missing
                if pm_data is None or prev_data is None:
                    continue
                    
                # Convert to DataFrame if necessary
                if not isinstance(pm_data, pd.DataFrame):
                    try:
                        pm_data = pd.DataFrame(pm_data)
                    except:
                        logger.error(f"Could not convert {symbol} pre-market data to DataFrame")
                        continue
                        
                if not isinstance(prev_data, pd.DataFrame):
                    try:
                        prev_data = pd.DataFrame(prev_data)
                    except:
                        logger.error(f"Could not convert {symbol} previous day data to DataFrame")
                        continue
                
                # Skip if not enough data
                if len(pm_data) == 0 or len(prev_data) == 0:
                    continue
                    
                # Calculate gap percentage
                prev_close = prev_data['close'].iloc[-1]
                pm_price = pm_data['close'].iloc[-1]  # Use latest pre-market price
                
                # Skip if price is outside our range
                if pm_price < self.min_price or pm_price > self.max_price:
                    continue
                    
                gap_percent = ((pm_price - prev_close) / prev_close) * 100
                
                # Check if gap is significant
                if abs(gap_percent) >= self.min_gap_percent:
                    # Calculate volume ratio if available
                    volume_ratio = 1.0  # Default
                    try:
                        pm_volume = pm_data['volume'].sum()
                        avg_volume = prev_data['volume'].mean()
                        if avg_volume > 0:
                            volume_ratio = pm_volume / avg_volume
                    except Exception as e:
                        logger.warning(f"Error calculating volume ratio for {symbol}: {e}")
                    
                    # Skip if volume is too low
                    if volume_ratio < self.min_volume_ratio:
                        continue
                        
                    # Create alert data
                    alert = {
                        'symbol': symbol,
                        'price': pm_price,
                        'prev_close': prev_close,
                        'gap_percent': gap_percent,
                        'volume': pm_data['volume'].sum() if 'volume' in pm_data else 0,
                        'volume_ratio': volume_ratio,
                        'timestamp': datetime.now().isoformat(),
                        'scan_time': self.last_scan_time.isoformat(),
                        'alert_type': 'gap_up' if gap_percent > 0 else 'gap_down',
                        'significance': self._calculate_significance(gap_percent, volume_ratio)
                    }
                    
                    # Add to appropriate list
                    if gap_percent > 0:
                        self.gap_alerts['gap_up'].append(alert)
                    else:
                        self.gap_alerts['gap_down'].append(alert)
                        
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                
        # Sort and limit results
        for direction in ['gap_up', 'gap_down']:
            self.gap_alerts[direction] = sorted(
                self.gap_alerts[direction],
                key=lambda x: abs(x[self.sort_by]),
                reverse=True
            )[:self.max_alerts]
            
        logger.info(f"Found {len(self.gap_alerts['gap_up'])} gap up and {len(self.gap_alerts['gap_down'])} gap down alerts")
        
        return self.gap_alerts
        
    def _calculate_significance(self, gap_percent, volume_ratio):
        """
        Calculate the significance score of a gap
        
        Args:
            gap_percent: Gap percentage
            volume_ratio: Volume ratio compared to average
            
        Returns:
            Significance score (0.0 to 1.0)
        """
        # Gap percent component (normalized by threshold)
        gap_score = min(abs(gap_percent) / (self.min_gap_percent * 3), 1.0)
        
        # Volume ratio component (normalized)
        volume_score = min((volume_ratio - 1) / (self.min_volume_ratio * 3), 1.0)
        
        # Combined score with heavier weight on gap percent
        significance = (gap_score * 0.7) + (volume_score * 0.3)
        
        return significance
    
    def get_alerts(self):
        """
        Get current gap alerts
        
        Returns:
            Dictionary with gap_up and gap_down alerts
        """
        return self.gap_alerts
    
    def save_alerts(self, file_path=None):
        """
        Save gap alerts to a JSON file
        
        Args:
            file_path: Path to save the file (optional)
        """
        if not file_path:
            # Generate a timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"data/premarket_gaps_{timestamp}.json"
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save alerts to file
        with open(file_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'gap_up': self.gap_alerts['gap_up'],
                'gap_down': self.gap_alerts['gap_down']
            }, f, indent=2)
            
        logger.info(f"Saved {len(self.gap_alerts['gap_up']) + len(self.gap_alerts['gap_down'])} gap alerts to {file_path}")
        
        return file_path
    
    def get_top_gaps(self, limit=5, direction='all'):
        """
        Get top gap alerts
        
        Args:
            limit: Maximum number of alerts to return
            direction: 'gap_up', 'gap_down', or 'all'
            
        Returns:
            List of top gap alerts
        """
        if direction == 'gap_up':
            return self.gap_alerts['gap_up'][:limit]
        elif direction == 'gap_down':
            return self.gap_alerts['gap_down'][:limit]
        else:
            # Combine and sort both directions
            combined = self.gap_alerts['gap_up'] + self.gap_alerts['gap_down']
            return sorted(combined, key=lambda x: abs(x['gap_percent']), reverse=True)[:limit]
    
    def generate_trading_ideas(self):
        """
        Generate trading ideas based on gap alerts
        
        Returns:
            List of trading ideas
        """
        trading_ideas = []
        
        # Process gap up alerts
        for alert in self.gap_alerts['gap_up'][:5]:  # Top 5
            # Create trading idea
            idea = {
                'symbol': alert['symbol'],
                'strategy': 'Gap & Go Long',
                'entry': f"Above {alert['price']:.2f}",
                'stop': f"Below {alert['price'] * 0.97:.2f}",
                'target': f"${alert['price'] * 1.05:.2f} to ${alert['price'] * 1.10:.2f}",
                'confidence': min(alert['significance'] * 100, 100),
                'setup_type': 'Momentum',
                'timestamp': datetime.now().isoformat(),
                'notes': f"Pre-market gap up of {alert['gap_percent']:.1f}% with {alert['volume_ratio']:.1f}x normal volume"
            }
            trading_ideas.append(idea)
            
        # Process gap down alerts
        for alert in self.gap_alerts['gap_down'][:5]:  # Top 5
            # Create trading idea
            idea = {
                'symbol': alert['symbol'],
                'strategy': 'Gap & Go Short',
                'entry': f"Below {alert['price']:.2f}",
                'stop': f"Above {alert['price'] * 1.03:.2f}",
                'target': f"${alert['price'] * 0.95:.2f} to ${alert['price'] * 0.90:.2f}",
                'confidence': min(alert['significance'] * 100, 100),
                'setup_type': 'Momentum',
                'timestamp': datetime.now().isoformat(),
                'notes': f"Pre-market gap down of {alert['gap_percent']:.1f}% with {alert['volume_ratio']:.1f}x normal volume"
            }
            trading_ideas.append(idea)
            
        return trading_ideas


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create scanner
    scanner = PreMarketGapperScanner()
    
    # Example data (replace with actual data in production)
    example_market_data = {
        'AAPL': pd.DataFrame({
            'close': [150.0, 151.0, 152.0],
            'volume': [10000, 15000, 20000]
        }),
        'TSLA': pd.DataFrame({
            'close': [800.0, 830.0, 840.0],
            'volume': [50000, 60000, 70000]
        }),
        'AMZN': pd.DataFrame({
            'close': [3300.0, 3310.0, 3320.0],
            'volume': [5000, 6000, 7000]
        }),
        'MSFT': pd.DataFrame({
            'close': [280.0, 275.0, 270.0],
            'volume': [15000, 16000, 17000]
        })
    }
    
    example_previous_data = {
        'AAPL': pd.DataFrame({
            'close': [148.0, 149.0, 145.0],
            'volume': [50000, 60000, 55000]
        }),
        'TSLA': pd.DataFrame({
            'close': [780.0, 785.0, 790.0],
            'volume': [100000, 110000, 105000]
        }),
        'AMZN': pd.DataFrame({
            'close': [3400.0, 3380.0, 3350.0],
            'volume': [20000, 22000, 21000]
        }),
        'MSFT': pd.DataFrame({
            'close': [290.0, 285.0, 288.0],
            'volume': [30000, 32000, 31000]
        })
    }
    
    # Scan for pre-market gaps
    alerts = scanner.scan_pre_market(example_market_data, example_previous_data)
    
    # Print alerts
    print("\nGap Up Alerts:")
    for alert in alerts['gap_up']:
        print(f"{alert['symbol']}: {alert['gap_percent']:.2f}% gap, {alert['volume_ratio']:.2f}x volume")
        
    print("\nGap Down Alerts:")
    for alert in alerts['gap_down']:
        print(f"{alert['symbol']}: {alert['gap_percent']:.2f}% gap, {alert['volume_ratio']:.2f}x volume")
        
    # Generate trading ideas
    ideas = scanner.generate_trading_ideas()
    
    print("\nTrading Ideas:")
    for idea in ideas:
        print(f"{idea['symbol']} - {idea['strategy']}")
        print(f"Entry: {idea['entry']}, Stop: {idea['stop']}, Target: {idea['target']}")
        print(f"Confidence: {idea['confidence']:.1f}%")
        print(f"Notes: {idea['notes']}")
        print("-" * 40) 