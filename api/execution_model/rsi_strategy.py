import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time
import random
import os
from ..config import bot_config
import threading

logger = logging.getLogger(__name__)

class RSIStrategy:
    """
    Implements an RSI (Relative Strength Index) trading strategy.
    """
    
    def __init__(self):
        """Initialize the RSI strategy."""
        self.is_running = False
        self.active_signals = []
        self.config = bot_config.RSI_BOT_CONFIG
        self.trading_thread = None
        self.stop_event = threading.Event()
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
    def start(self) -> bool:
        """Start the RSI trading strategy."""
        try:
            if not self.is_running:
                self.is_running = True
                self.stop_event.clear()
                self.trading_thread = threading.Thread(target=self._trading_loop)
                self.trading_thread.daemon = True
                self.trading_thread.start()
                logger.info("RSI Strategy started successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error starting RSI Strategy: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """Stop the RSI trading strategy."""
        try:
            if self.is_running:
                self.is_running = False
                self.stop_event.set()
                if self.trading_thread and self.trading_thread.is_alive():
                    self.trading_thread.join(timeout=10)
                logger.info("RSI Strategy stopped successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error stopping RSI Strategy: {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the RSI strategy."""
        return {
            'status': self.is_running,
            'signals_count': len(self.active_signals),
            'config': {
                'rsi_period': self.config['rsi_period'],
                'oversold_threshold': self.config['oversold_threshold'],
                'overbought_threshold': self.config['overbought_threshold']
            }
        }
    
    def get_active_signals(self) -> List[Dict[str, Any]]:
        """Get the current active signals."""
        return self.active_signals
    
    def get_current_data(self) -> Dict[str, Any]:
        """Get current market data and analysis."""
        return {
            'timestamp': datetime.now().isoformat(),
            'signals': self.active_signals,
            'metrics': {
                'average_strength': np.mean([s.get('strength', 0) for s in self.active_signals]) if self.active_signals else 0,
                'signal_count': len(self.active_signals)
            }
        }
    
    def _trading_loop(self) -> None:
        """Main trading loop that runs continuously while the strategy is active."""
        logger.info("Starting RSI trading loop")
        while not self.stop_event.is_set():
            try:
                self._scan_for_signals()
                self._update_active_signals()
                # Sleep for a bit to avoid high CPU usage
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error in RSI trading loop: {str(e)}")
                time.sleep(10)  # Wait longer if there was an error
    
    def _scan_for_signals(self) -> None:
        """Scan for new trading signals based on RSI."""
        try:
            # This is a mock implementation
            # In production, this would analyze real market data
            
            # List of potential symbols
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA']
            
            # Randomly generate 0-2 new signals
            if random.random() < 0.3:  # 30% chance to generate new signals
                num_signals = random.randint(0, 2)
                for _ in range(num_signals):
                    symbol = random.choice(symbols)
                    # Generate a random RSI value (0-100)
                    rsi_value = random.uniform(20, 80)
                    
                    # Determine signal type based on RSI thresholds
                    if rsi_value < self.config['oversold_threshold']:
                        signal_type = 'BUY'
                    elif rsi_value > self.config['overbought_threshold']:
                        signal_type = 'SELL'
                    else:
                        continue  # No signal in neutral zone
                    
                    # Create a new signal
                    signal = {
                        'symbol': symbol,
                        'rsi': round(rsi_value, 2),
                        'type': signal_type,
                        'strength': round(abs(rsi_value - 50) / 50 * 100, 2),  # 0-100% strength
                        'timestamp': datetime.now().isoformat(),
                        'price': round(random.uniform(50, 500), 2)  # Mock price
                    }
                    
                    # Check if signal already exists for this symbol
                    existing = next((s for s in self.active_signals if s['symbol'] == symbol), None)
                    if existing:
                        # Update existing signal
                        existing.update(signal)
                    else:
                        # Add new signal
                        self.active_signals.append(signal)
                
                if num_signals > 0:
                    logger.info(f"Generated {num_signals} new RSI signals")
        
        except Exception as e:
            logger.error(f"Error scanning for RSI signals: {str(e)}")
    
    def _update_active_signals(self) -> None:
        """Update or expire active signals."""
        try:
            # Expire signals that are older than 30 minutes
            current_time = datetime.now()
            self.active_signals = [
                signal for signal in self.active_signals
                if datetime.fromisoformat(signal['timestamp']) > current_time - timedelta(minutes=30)
            ]
            
            # Update prices for active signals
            for signal in self.active_signals:
                # In production, this would fetch real market prices
                current_price = signal.get('price', 100)
                # Add a small random change (-3% to +3%)
                price_change = current_price * random.uniform(-0.03, 0.03)
                signal['price'] = round(current_price + price_change, 2)
                signal['updated_at'] = datetime.now().isoformat()
        
        except Exception as e:
            logger.error(f"Error updating active signals: {str(e)}")
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        Calculate the Relative Strength Index (RSI) for a given price series.
        
        Args:
            prices: List of price values
            period: RSI calculation period
            
        Returns:
            The RSI value (0-100)
        """
        if len(prices) < period + 1:
            return 50  # Default to neutral if not enough data
        
        try:
            # Convert to numpy array for calculations
            prices_array = np.array(prices)
            
            # Calculate price changes
            deltas = np.diff(prices_array)
            
            # Create arrays for gains and losses
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            # Calculate average gains and losses
            avg_gain = np.mean(gains[:period])
            avg_loss = np.mean(losses[:period])
            
            # Calculate RS and RSI
            if avg_loss == 0:
                return 100  # No losses, RSI is 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return round(rsi, 2)
        
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return 50  # Default to neutral on error
    
    def run_trading_cycle(self) -> bool:
        """Run a single trading cycle for RSI strategy."""
        try:
            if not self.is_running:
                logger.warning("Cannot run trading cycle: RSI Strategy is not active")
                return False
                
            # Execute a single cycle of the strategy
            self._scan_for_signals()
            self._update_active_signals()
            
            logger.debug("Completed RSI strategy trading cycle")
            return True
        except Exception as e:
            logger.error(f"Error in RSI strategy trading cycle: {str(e)}")
            return False 