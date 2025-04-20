"""
Data fetcher module for loading and managing market data.
"""

import os
import pandas as pd
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetches and manages market data from various sources."""
    
    def __init__(self):
        """Initialize the data fetcher."""
        self.data_dir = os.path.join(os.getcwd(), 'data')
        self.market_data_callback = None
        self.options_flow_callback = None
        self.dark_pool_callback = None
        self.news_callback = None
    
    def set_market_data_callback(self, callback: Callable):
        """Set callback for market data updates."""
        self.market_data_callback = callback
    
    def set_options_flow_callback(self, callback: Callable):
        """Set callback for options flow updates."""
        self.options_flow_callback = callback
    
    def set_dark_pool_callback(self, callback: Callable):
        """Set callback for dark pool updates."""
        self.dark_pool_callback = callback
    
    def set_news_callback(self, callback: Callable):
        """Set callback for news updates."""
        self.news_callback = callback
    
    def load_signals(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Load buy and short signals from CSV files."""
        try:
            buy_file = os.path.join(self.data_dir, 'buy_signals.csv')
            short_file = os.path.join(self.data_dir, 'short_signals.csv')
            
            buy_signals = pd.read_csv(buy_file) if os.path.exists(buy_file) else pd.DataFrame()
            short_signals = pd.read_csv(short_file) if os.path.exists(short_file) else pd.DataFrame()
            
            return buy_signals, short_signals
        except Exception as e:
            logger.error(f"Error loading signals: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()
    
    def get_status(self) -> Dict:
        """Get the current status of the data fetcher."""
        try:
            buy_signals, short_signals = self.load_signals()
            return {
                'running': True,
                'last_updated': datetime.now().isoformat(),
                'data_sources': {
                    'buy_signals': len(buy_signals),
                    'short_signals': len(short_signals)
                }
            }
        except Exception as e:
            logger.error(f"Error getting data fetcher status: {str(e)}")
            return {
                'running': False,
                'error': str(e)
            } 