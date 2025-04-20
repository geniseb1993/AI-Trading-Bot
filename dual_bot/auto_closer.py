"""
Auto closer module for managing trade exits based on predefined rules and AI recommendations.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import pandas as pd
import numpy as np
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import threading
import time

from dual_bot.config import config, logger
from dual_bot.chatgpt_risk_check import ChatGPTRiskManager
from dual_bot.data_fetcher import DataFetcher

class AutoCloser:
    """Manages automated trade exits based on rules and AI recommendations."""
    
    def __init__(self, data_fetcher: DataFetcher):
        """
        Initialize the auto closer.
        
        Args:
            data_fetcher: DataFetcher instance for market data
        """
        self.config = config
        self.risk_manager = ChatGPTRiskManager()
        self.data_fetcher = data_fetcher
        
        # Initialize Alpaca client
        alpaca_config = self.config["brokers"]["alpaca"]
        self.trading_client = TradingClient(
            api_key=alpaca_config["api_key"],
            secret_key=alpaca_config["secret_key"],
            paper=alpaca_config.get("paper", True)
        )
        
        # Load exit rules from config
        self.exit_rules = self.config["trading"]["exit_rules"]
        self.max_loss_percent = self.exit_rules["max_loss_percent"]
        self.profit_target_percent = self.exit_rules["profit_target_percent"]
        self.trailing_stop_percent = self.exit_rules["trailing_stop_percent"]
        
        # Initialize trade tracking
        self.active_trades = {}
        self.trade_history = []
        
        # Setup monitoring interval
        self.monitor_interval = self.config["trading"]["monitor_interval_seconds"]
        
        # Setup monitoring thread
        self.monitoring_thread = None
        self.is_running = False
        self.stop_event = threading.Event()
        
        logger.info("Auto closer initialized with exit rules: " + json.dumps(self.exit_rules, indent=2))
    
    def start(self):
        """Start the auto closer monitoring."""
        if self.is_running:
            logger.warning("Auto closer is already running.")
            return False
        
        logger.info("Starting auto closer...")
        self.is_running = True
        self.stop_event.clear()
        
        # Start monitoring in a separate thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Auto closer started successfully!")
        return True
    
    def stop(self):
        """Stop the auto closer monitoring."""
        if not self.is_running:
            logger.warning("Auto closer is not running.")
            return False
        
        logger.info("Stopping auto closer...")
        self.is_running = False
        self.stop_event.set()
        
        # Wait for monitoring thread to terminate
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Auto closer stopped successfully!")
        return True
    
    def _monitoring_loop(self):
        """Main monitoring loop running in a separate thread."""
        logger.info("Starting trade monitoring loop")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                # Check all positions
                self.check_positions()
                
                # Sleep for monitor interval
                for _ in range(int(self.monitor_interval)):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitor_interval)
    
    def check_positions(self):
        """Check all active positions for exit conditions."""
        for symbol, trade in list(self.active_trades.items()):
            try:
                self.evaluate_position(trade)
            except Exception as e:
                logger.error(f"Error evaluating position for {symbol}: {e}")
    
    async def evaluate_position(self, trade: Dict):
        """
        Evaluate a single position for exit conditions.
        
        Args:
            trade: Dictionary containing trade information
        """
        symbol = trade["symbol"]
        entry_price = trade["entry_price"]
        current_price = await self._get_current_price(symbol)
        position_size = trade["position_size"]
        
        # Calculate metrics
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        if trade["direction"] == "short":
            pnl_percent = -pnl_percent
        
        # Update high water mark
        if "high_water_mark" not in trade:
            trade["high_water_mark"] = entry_price
        elif (trade["direction"] == "long" and current_price > trade["high_water_mark"]) or \
             (trade["direction"] == "short" and current_price < trade["high_water_mark"]):
            trade["high_water_mark"] = current_price
        
        # Check exit conditions
        exit_signal = await self._check_exit_conditions(trade, current_price, pnl_percent)
        
        if exit_signal["should_exit"]:
            await self._execute_exit(trade, exit_signal["reason"])
    
    async def _check_exit_conditions(self, trade: Dict, current_price: float, pnl_percent: float) -> Dict:
        """
        Check all exit conditions for a trade.
        
        Args:
            trade: Trade information
            current_price: Current price of the symbol
            pnl_percent: Current PnL percentage
            
        Returns:
            Dictionary with exit decision and reason
        """
        # Check stop loss
        if pnl_percent <= -self.max_loss_percent:
            return {
                "should_exit": True,
                "reason": f"Stop loss hit at {pnl_percent:.2f}%"
            }
        
        # Check profit target
        if pnl_percent >= self.profit_target_percent:
            return {
                "should_exit": True,
                "reason": f"Profit target reached at {pnl_percent:.2f}%"
            }
        
        # Check trailing stop
        high_water_mark = trade["high_water_mark"]
        trailing_stop_price = high_water_mark * (1 - self.trailing_stop_percent/100)
        if trade["direction"] == "long" and current_price <= trailing_stop_price:
            return {
                "should_exit": True,
                "reason": f"Trailing stop hit at {pnl_percent:.2f}%"
            }
        
        # Check time-based exits
        entry_time = datetime.fromisoformat(trade["entry_time"])
        time_in_trade = (datetime.now() - entry_time).total_seconds() / 3600  # hours
        
        if time_in_trade >= trade.get("max_hold_time", float("inf")):
            return {
                "should_exit": True,
                "reason": f"Maximum hold time reached ({time_in_trade:.1f} hours)"
            }
        
        # Get AI risk assessment if needed
        if self._should_check_risk(trade):
            market_context = await self._get_market_context()
            assessment = self.risk_manager.assess_trade(trade, market_context)
            
            if not assessment["decision"] and assessment["confidence"] > 0.7:
                return {
                    "should_exit": True,
                    "reason": f"AI risk assessment suggests exit: {assessment['summary']}"
                }
        
        return {
            "should_exit": False,
            "reason": None
        }
    
    async def _execute_exit(self, trade: Dict, reason: str):
        """
        Execute the exit for a trade.
        
        Args:
            trade: Trade to exit
            reason: Reason for exit
        """
        symbol = trade["symbol"]
        try:
            # Log exit decision
            logger.info(f"Exiting {symbol} position: {reason}")
            
            # Create market order for exit
            order_side = OrderSide.SELL if trade["direction"] == "long" else OrderSide.BUY
            
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=trade["position_size"],
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            
            # Submit order to Alpaca
            try:
                order = self.trading_client.submit_order(order_data)
                logger.info(f"Exit order submitted for {symbol}: {order.id}")
                
                # Wait for order to fill
                filled_order = self.trading_client.get_order(order.id)
                max_wait = 60  # seconds
                wait_start = datetime.now()
                
                while filled_order.status != "filled" and \
                      (datetime.now() - wait_start).total_seconds() < max_wait:
                    await asyncio.sleep(1)
                    filled_order = self.trading_client.get_order(order.id)
                
                if filled_order.status == "filled":
                    logger.info(f"Exit order filled for {symbol} at {filled_order.filled_avg_price}")
                else:
                    logger.warning(f"Exit order not filled within {max_wait} seconds")
                    
            except Exception as e:
                logger.error(f"Error submitting exit order: {e}")
                raise
            
            # Update trade history
            trade["exit_time"] = datetime.now().isoformat()
            trade["exit_reason"] = reason
            trade["exit_price"] = float(filled_order.filled_avg_price) if filled_order.status == "filled" else None
            self.trade_history.append(trade)
            
            # Remove from active trades
            del self.active_trades[symbol]
            
            # Log success
            logger.info(f"Successfully exited {symbol} position")
            
        except Exception as e:
            logger.error(f"Error executing exit for {symbol}: {e}")
    
    def add_trade(self, trade: Dict):
        """
        Add a new trade to monitor.
        
        Args:
            trade: Dictionary containing trade information
        """
        symbol = trade["symbol"]
        if symbol in self.active_trades:
            logger.warning(f"Trade for {symbol} already exists, updating")
        
        trade["entry_time"] = datetime.now().isoformat()
        self.active_trades[symbol] = trade
        logger.info(f"Added new trade for {symbol}")
    
    async def _get_current_price(self, symbol: str) -> float:
        """
        Get the current price for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Current price
        """
        try:
            # Get latest market data from DataFetcher
            market_data = self.data_fetcher.get_market_data(symbol)
            if market_data:
                latest_trade = market_data[-1]
                return float(latest_trade.get("p", 0.0))  # 'p' is price in Polygon format
            
            # Fallback to Alpaca if market data not available
            position = self.trading_client.get_position(symbol)
            return float(position.current_price)
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            raise
    
    async def _get_market_context(self) -> Dict:
        """
        Get current market context for AI assessment.
        
        Returns:
            Dictionary containing market context
        """
        try:
            # Get market hours
            clock = self.trading_client.get_clock()
            market_hours = "Regular Trading Hours" if clock.is_open else "After Hours"
            
            # Get VIX data if available
            vix_data = self.data_fetcher.get_market_data("VIX")
            vix = float(vix_data[-1].get("p", 0.0)) if vix_data else 0.0
            
            # Get sector performance from news data
            news_data = self.data_fetcher.get_news_data()
            sector_performance = "Neutral"  # Default
            if news_data:
                # Simple sentiment analysis based on news headlines
                tech_keywords = ["technology", "tech", "nasdaq", "software"]
                positive_count = 0
                negative_count = 0
                for article in news_data[:10]:  # Check recent articles
                    title = article.get("title", "").lower()
                    if any(keyword in title for keyword in tech_keywords):
                        if any(word in title for word in ["surge", "jump", "rise", "gain"]):
                            positive_count += 1
                        elif any(word in title for word in ["drop", "fall", "decline", "slip"]):
                            negative_count += 1
                
                if positive_count > negative_count:
                    sector_performance = "Technology +1.2%"  # Approximate
                elif negative_count > positive_count:
                    sector_performance = "Technology -1.0%"  # Approximate
            
            # Determine market conditions
            conditions = []
            if vix > 25:
                conditions.append("High Volatility")
            elif vix < 15:
                conditions.append("Low Volatility")
            
            if clock.is_open:
                if datetime.now().hour < 11:
                    conditions.append("Morning Session")
                elif datetime.now().hour > 14:
                    conditions.append("Late Session")
                else:
                    conditions.append("Mid-Day")
            
            market_conditions = " & ".join(conditions) if conditions else "Normal"
            
            return {
                "market_hours": market_hours,
                "market_conditions": market_conditions,
                "vix": vix,
                "sector_performance": sector_performance
            }
            
        except Exception as e:
            logger.error(f"Error getting market context: {e}")
            return {
                "market_hours": "Regular Trading Hours",
                "market_conditions": "Normal",
                "vix": 0.0,
                "sector_performance": "Neutral"
            }
    
    def _should_check_risk(self, trade: Dict) -> bool:
        """
        Determine if we should perform an AI risk check.
        
        Args:
            trade: Trade information
            
        Returns:
            Boolean indicating whether to check risk
        """
        last_check = trade.get("last_risk_check")
        if not last_check:
            return True
        
        last_check_time = datetime.fromisoformat(last_check)
        time_since_check = (datetime.now() - last_check_time).total_seconds() / 60
        
        return time_since_check >= self.config["trading"]["risk_check_interval_minutes"]
    
    def get_trade_summary(self) -> Dict:
        """
        Get a summary of all trades.
        
        Returns:
            Dictionary containing trade statistics
        """
        if not self.trade_history:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_profit": 0.0,
                "max_drawdown": 0.0
            }
        
        df = pd.DataFrame(self.trade_history)
        
        # Calculate statistics
        total_trades = len(df)
        profitable_trades = len(df[df["pnl_percent"] > 0])
        win_rate = profitable_trades / total_trades
        avg_profit = df["pnl_percent"].mean()
        max_drawdown = df["pnl_percent"].min()
        
        return {
            "total_trades": total_trades,
            "win_rate": win_rate,
            "avg_profit": avg_profit,
            "max_drawdown": max_drawdown,
            "active_trades": len(self.active_trades)
        }

    def should_close_position(self, position: Dict) -> bool:
        """
        Check if a position should be closed.
        
        Args:
            position: Position data dictionary
            
        Returns:
            True if position should be closed, False otherwise
        """
        try:
            # Extract position data
            symbol = position["symbol"]
            entry_price = position["entry_price"]
            current_price = position["current_price"]
            
            # Calculate P&L percentage
            if position["side"] == "bullish":
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
            else:
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
            
            # Check stop loss
            if pnl_percent <= -self.max_loss_percent:
                logger.info(f"Stop loss hit for {symbol} at {pnl_percent:.2f}%")
                return True
            
            # Check profit target
            if pnl_percent >= self.profit_target_percent:
                logger.info(f"Profit target reached for {symbol} at {pnl_percent:.2f}%")
                return True
            
            # Check time-based exit
            entry_time = position["entry_time"]
            max_hold_time = timedelta(hours=self.exit_rules.get("max_hold_time_hours", 8))
            
            if datetime.now() - entry_time > max_hold_time:
                logger.info(f"Maximum hold time reached for {symbol}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking if position should be closed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize data fetcher
    data_fetcher = DataFetcher()
    data_fetcher.initialize()
    
    # Create auto closer
    closer = AutoCloser(data_fetcher)
    
    # Add sample trade
    sample_trade = {
        "symbol": "QQQ",
        "direction": "long",
        "entry_price": 400.0,
        "position_size": 100,
        "trade_type": "0DTE",
        "max_hold_time": 2.0  # hours
    }
    
    closer.add_trade(sample_trade)
    
    # Start data fetcher and monitoring
    data_fetcher.start()
    
    try:
        # Start monitoring
        asyncio.run(closer.start_monitoring())
    except KeyboardInterrupt:
        # Stop data fetcher
        data_fetcher.stop()
        print("Auto closer stopped") 