#!/usr/bin/env python
"""
Dual Bot Main Script
This script runs the Dual Bot trading system.
"""

import os
import sys
import json
import logging
import time
import schedule
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the dual_bot package
sys.path.append(str(Path(__file__).parent.parent))

# Import Dual Bot components
from dual_bot.config.config_loader import load_config
from dual_bot.ai.deepseek_scanner import DeepSeekScanner
from dual_bot.chatgpt_risk_check import ChatGPTRiskManager
from dual_bot.auto_closer import AutoCloser
from dual_bot.data_fetcher import DataFetcher

# Set up logging
def setup_logging(config):
    """Set up logging based on configuration."""
    log_level = getattr(logging, config.get("logging", {}).get("level", "INFO"))
    log_file = config.get("logging", {}).get("file", "dual_bot/logs/dual_bot.log")
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("DualBot")

class DualBot:
    """Main class for the Dual Bot trading system."""
    
    def __init__(self, config):
        """Initialize the Dual Bot with configuration."""
        self.config = config
        self.logger = setup_logging(config)
        self.logger.info("Initializing Dual Bot...")
        
        # Initialize components
        self.data_fetcher = DataFetcher(config)
        self.scanner = DeepSeekScanner(config)
        self.risk_manager = ChatGPTRiskManager(config)
        self.auto_closer = AutoCloser(config)
        
        # Initialize state
        self.active_positions = []
        self.trade_history = []
        self.last_scan_time = None
        self.last_risk_check_time = None
        
        self.logger.info("Dual Bot initialized successfully!")
    
    def scan_for_trades(self):
        """Scan for trade opportunities."""
        self.logger.info("Scanning for trade opportunities...")
        
        try:
            # Generate trade recommendations
            recommendations = self.scanner.generate_recommendations()
            
            if not recommendations:
                self.logger.info("No trade recommendations found.")
                return
            
            self.logger.info(f"Found {len(recommendations)} trade recommendations.")
            
            # Process each recommendation
            for recommendation in recommendations:
                self._process_recommendation(recommendation)
            
            self.last_scan_time = datetime.now()
        except Exception as e:
            self.logger.error(f"Error scanning for trades: {e}")
    
    def _process_recommendation(self, recommendation):
        """Process a trade recommendation."""
        self.logger.info(f"Processing recommendation for {recommendation['symbol']}...")
        
        try:
            # Get market context
            market_context = self._get_market_context(recommendation["symbol"])
            
            # Assess risk
            risk_assessment = self.risk_manager.assess_trade(recommendation, market_context)
            
            # Log the risk assessment
            self.logger.info(f"Risk assessment for {recommendation['symbol']}: {risk_assessment}")
            
            # If the trade is approved, add it to active positions
            if risk_assessment["approved"]:
                self.logger.info(f"Trade approved for {recommendation['symbol']}.")
                
                # Create position
                position = {
                    "symbol": recommendation["symbol"],
                    "side": recommendation["direction"],
                    "entry_price": recommendation["entry_price"],
                    "current_price": recommendation["entry_price"],
                    "quantity": self._calculate_position_size(recommendation),
                    "stop_loss": recommendation["stop_loss"],
                    "take_profit": recommendation["take_profit"],
                    "entry_time": datetime.now(),
                    "risk_assessment": risk_assessment
                }
                
                # Add to active positions
                self.active_positions.append(position)
                
                # Log the position
                self.logger.info(f"Added position: {position}")
                
                # Send notification
                self._send_notification(f"New trade: {recommendation['symbol']} {recommendation['direction']} at {recommendation['entry_price']}")
            else:
                self.logger.info(f"Trade rejected for {recommendation['symbol']}: {risk_assessment['reason']}")
        except Exception as e:
            self.logger.error(f"Error processing recommendation: {e}")
    
    def _get_market_context(self, symbol):
        """Get market context for a symbol."""
        try:
            # Get market data
            market_data = self.data_fetcher.get_market_data(symbol)
            
            # Get news data
            news_data = self.data_fetcher.get_news_data(symbol)
            
            # Create market context
            market_context = {
                "market_hours": "open" if self._is_market_open() else "closed",
                "market_condition": self._get_market_condition(),
                "vix": market_data.get("vix", 0),
                "sector_performance": market_data.get("sector_performance", {}),
                "recent_news": news_data
            }
            
            return market_context
        except Exception as e:
            self.logger.error(f"Error getting market context: {e}")
            return {}
    
    def _is_market_open(self):
        """Check if the market is open."""
        now = datetime.now()
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return False
        
        # Check if it's between 9:30 AM and 4:00 PM ET
        # This is a simplified check and should be adjusted for your timezone
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def _get_market_condition(self):
        """Get the current market condition."""
        # This is a simplified implementation
        # In a real system, you would analyze market data to determine the condition
        return "bullish"  # or "bearish" or "neutral"
    
    def _calculate_position_size(self, recommendation):
        """Calculate the position size based on the recommendation."""
        position_sizing = self.config["trading"]["position_sizing"]
        
        if position_sizing["type"] == "fixed":
            return position_sizing["amount"]
        elif position_sizing["type"] == "percentage":
            # This is a simplified implementation
            # In a real system, you would calculate based on account balance
            return 1000  # Default to 1000
        else:
            return 1000  # Default to 1000
    
    def check_positions(self):
        """Check active positions for exit signals."""
        self.logger.info("Checking active positions...")
        
        try:
            # Update current prices
            for position in self.active_positions:
                position["current_price"] = self._get_current_price(position["symbol"])
            
            # Check each position
            for position in self.active_positions[:]:  # Copy the list to avoid modification during iteration
                should_close = self.auto_closer.should_close_position(position)
                
                if should_close:
                    self.logger.info(f"Closing position for {position['symbol']}...")
                    
                    # Close the position
                    self._close_position(position)
                    
                    # Remove from active positions
                    self.active_positions.remove(position)
                    
                    # Add to trade history
                    self.trade_history.append(position)
                    
                    # Send notification
                    self._send_notification(f"Closed position: {position['symbol']} at {position['current_price']}")
            
            self.last_risk_check_time = datetime.now()
        except Exception as e:
            self.logger.error(f"Error checking positions: {e}")
    
    def _get_current_price(self, symbol):
        """Get the current price for a symbol."""
        try:
            market_data = self.data_fetcher.get_market_data(symbol)
            return market_data.get("price", 0)
        except Exception as e:
            self.logger.error(f"Error getting current price for {symbol}: {e}")
            return 0
    
    def _close_position(self, position):
        """Close a position."""
        # This is a simplified implementation
        # In a real system, you would execute the order through your broker
        self.logger.info(f"Position closed: {position}")
    
    def _send_notification(self, message):
        """Send a notification."""
        # This is a simplified implementation
        # In a real system, you would send notifications through your configured channels
        self.logger.info(f"Notification: {message}")
    
    def run(self):
        """Run the Dual Bot."""
        self.logger.info("Starting Dual Bot...")
        
        try:
            # Start components
            self.logger.info("Starting data fetcher...")
            self.data_fetcher.start()
            
            self.logger.info("Starting scanner...")
            self.scanner.start()
            
            self.logger.info("Starting auto closer...")
            self.auto_closer.start()
            
            # Schedule daily tasks
            schedule.every().day.at("09:00").do(self.scan_for_trades)
            schedule.every().day.at("00:01").do(self.scanner.reset_daily_counts)
            
            # Schedule periodic tasks
            risk_check_interval = self.config["trading"]["risk_check_interval_minutes"]
            schedule.every(risk_check_interval).minutes.do(self.check_positions)
            
            # Enter main loop
            self.logger.info("Dual Bot is running...")
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt detected. Shutting down...")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            # Stop components
            self.logger.info("Stopping auto closer...")
            self.auto_closer.stop()
            
            self.logger.info("Stopping scanner...")
            self.scanner.stop()
            
            self.logger.info("Stopping data fetcher...")
            self.data_fetcher.stop()
            
            self.logger.info("Dual Bot stopped.")

def main():
    """Main function to run the Dual Bot."""
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration.")
        return
    
    # Create and run the bot
    bot = DualBot(config)
    bot.run()

if __name__ == "__main__":
    main() 