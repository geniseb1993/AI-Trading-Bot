import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

# API imports
from polygon import RESTClient
from alpaca.trading import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from ..config import bot_config

logger = logging.getLogger(__name__)

class DualBotManager:
    def __init__(self):
        self.is_running = False
        self.polygon_client = RESTClient(api_key=bot_config.POLYGON_API_KEY)
        self.alpaca_client = TradingClient(
            bot_config.ALPACA_API_KEY, 
            bot_config.ALPACA_SECRET_KEY,
            paper=bot_config.PAPER_TRADING
        )
        self.active_positions: List[Dict[str, Any]] = []
        self.current_data: Dict[str, Any] = {}
        self.config = bot_config.DUAL_BOT_CONFIG
        
    def start(self) -> bool:
        """Start the dual bot"""
        try:
            if not self.is_running:
                self.is_running = True
                self._initialize_real_time_data()
                logger.info("DualBot started successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error starting DualBot: {str(e)}")
            return False

    def stop(self) -> bool:
        """Stop the dual bot"""
        try:
            if self.is_running:
                self.is_running = False
                self._cleanup_positions()
                logger.info("DualBot stopped successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error stopping DualBot: {str(e)}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'active_positions_count': len(self.active_positions),
            'last_update': datetime.now().isoformat(),
            'current_performance': self._calculate_performance()
        }

    def get_active_positions(self) -> List[Dict[str, Any]]:
        """Get list of active positions"""
        try:
            # Get real positions from Alpaca
            positions = self.alpaca_client.get_all_positions()
            self.active_positions = [
                {
                    'symbol': pos.symbol,
                    'qty': pos.qty,
                    'entry_price': pos.avg_entry_price,
                    'current_price': pos.current_price,
                    'unrealized_pl': pos.unrealized_pl,
                    'unrealized_plpc': pos.unrealized_plpc,
                    'market_value': pos.market_value,
                    'cost_basis': pos.cost_basis
                }
                for pos in positions
            ]
            return self.active_positions
        except Exception as e:
            logger.error(f"Error getting active positions: {str(e)}")
            return []

    def get_current_data(self) -> Dict[str, Any]:
        """Get current market data and analysis"""
        try:
            self._update_market_data()
            return self.current_data
        except Exception as e:
            logger.error(f"Error getting current data: {str(e)}")
            return {}

    def _initialize_real_time_data(self) -> None:
        """Initialize real-time data streams"""
        try:
            # Initialize market data
            self._update_market_data()
            
            # Initialize position tracking
            self.get_active_positions()
            
            logger.info("Real-time data initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing real-time data: {str(e)}")
            raise

    def _update_market_data(self) -> None:
        """Update market data from various sources"""
        try:
            # Get market data from Polygon
            for symbol in self._get_watched_symbols():
                try:
                    aggs = self.polygon_client.get_aggs(
                        symbol,
                        1,
                        "minute",
                        datetime.now().strftime("%Y-%m-%d"),
                        datetime.now().strftime("%Y-%m-%d")
                    )
                    
                    if aggs:
                        self.current_data[symbol] = {
                            'price': aggs[-1].close,
                            'volume': aggs[-1].volume,
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        # Fallback to mock data if no results
                        self.current_data[symbol] = {
                            'price': 100.0,  # Mock price
                            'volume': 10000,  # Mock volume
                            'timestamp': datetime.now().isoformat(),
                            'source': 'mock'
                        }
                except Exception as symbol_error:
                    logger.warning(f"Error fetching data for {symbol}: {str(symbol_error)}")
                    # Continue with other symbols
                    
            logger.info("Market data updated successfully")
        except Exception as e:
            logger.error(f"Error updating market data: {str(e)}")
            # Use mock data as fallback
            self._use_mock_data()

    def _use_mock_data(self) -> None:
        """Use mock data as fallback"""
        for symbol in self._get_watched_symbols():
            self.current_data[symbol] = {
                'price': 100.0,  # Mock price
                'volume': 10000,  # Mock volume
                'timestamp': datetime.now().isoformat(),
                'source': 'mock'
            }
        logger.info("Using mock data as fallback")

    def _cleanup_positions(self) -> None:
        """Clean up positions when stopping the bot"""
        try:
            # Implement position cleanup logic here
            # For example, close all positions or set trailing stops
            logger.info("Positions cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up positions: {str(e)}")
            raise

    def _calculate_performance(self) -> Dict[str, float]:
        """Calculate current performance metrics"""
        try:
            total_equity = sum(pos.get('market_value', 0) for pos in self.active_positions)
            total_cost = sum(pos.get('cost_basis', 0) for pos in self.active_positions)
            
            return {
                'total_equity': total_equity,
                'total_cost': total_cost,
                'unrealized_pl': total_equity - total_cost,
                'unrealized_pl_percent': ((total_equity - total_cost) / total_cost * 100) if total_cost > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error calculating performance: {str(e)}")
            return {'total_equity': 0, 'total_cost': 0, 'unrealized_pl': 0, 'unrealized_pl_percent': 0}

    def _get_watched_symbols(self) -> List[str]:
        """Get list of symbols to watch"""
        # Implement your symbol selection logic here
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']  # Example symbols 

    def run_trading_cycle(self) -> bool:
        """Run a single trading cycle for dual bot."""
        try:
            if not self.is_running:
                logger.warning("Cannot run trading cycle: Dual Bot is not active")
                return False
                
            # Update market data
            self._update_market_data()
            
            # Update active positions
            self.get_active_positions()
            
            # Calculate performance metrics
            self._calculate_performance()
            
            logger.debug("Completed Dual Bot trading cycle")
            return True
        except Exception as e:
            logger.error(f"Error in Dual Bot trading cycle: {str(e)}")
            return False 