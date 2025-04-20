#!/usr/bin/env python
"""
Dual Bot Simulation Script
This script runs the Dual Bot in a simulated environment for testing purposes.
"""

import os
import sys
import json
import logging
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the dual_bot package
sys.path.append(str(Path(__file__).parent.parent))

# Import only the config loader, not the actual components
from dual_bot.config.config_loader import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dual_bot/logs/simulate_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SimulateBot")

class Trade:
    def __init__(self, symbol: str, direction: str, entry_price: float, quantity: int,
                 stop_loss: float, take_profit: float):
        self.symbol = symbol
        self.direction = direction
        self.entry_price = entry_price
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.entry_time = datetime.now()

    def get_current_price(self) -> float:
        # Simulate price movement
        price_change = random.uniform(-0.02, 0.02)  # ±2% price change
        return self.entry_price * (1 + price_change)

    def calculate_pnl(self) -> float:
        current_price = self.get_current_price()
        if self.direction == 'long':
            return (current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - current_price) * self.quantity

    def calculate_pnl_percent(self) -> float:
        current_price = self.get_current_price()
        if self.direction == 'long':
            return ((current_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - current_price) / self.entry_price) * 100

class Alert:
    def __init__(self, alert_type: str, message: str, severity: str):
        self.id = random.randint(1000, 9999)
        self.type = alert_type
        self.message = message
        self.severity = severity
        self.timestamp = datetime.now()

class DualBotSimulator:
    def __init__(self):
        self.is_running = True
        self.active_trades: List[Trade] = []
        self.trade_history: List[Trade] = []
        self.alerts: List[Alert] = []
        self.initial_balance = 100000  # $100,000 initial balance
        self.current_balance = self.initial_balance
        self.performance_history: List[Dict[str, Any]] = []
        
        # Initialize with some sample data
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        # Create sample trades
        symbols = ['QQQ', 'TSLA', 'PLTR']
        for symbol in symbols:
            if random.random() < 0.7:  # 70% chance of having an active trade
                direction = random.choice(['long', 'short'])
                entry_price = random.uniform(100, 500)
                quantity = random.randint(1, 10)
                stop_loss = entry_price * (0.95 if direction == 'long' else 1.05)
                take_profit = entry_price * (1.05 if direction == 'long' else 0.95)
                
                trade = Trade(symbol, direction, entry_price, quantity, stop_loss, take_profit)
                self.active_trades.append(trade)

        # Create sample alerts
        alert_types = ['TRADE', 'RISK', 'SYSTEM', 'MARKET']
        severities = ['INFO', 'WARNING', 'ALERT']
        for _ in range(5):
            alert = Alert(
                random.choice(alert_types),
                f"Sample alert message {random.randint(1, 100)}",
                random.choice(severities)
            )
            self.alerts.append(alert)

        # Initialize performance history
        self._generate_performance_history()

    def _generate_performance_history(self):
        # Generate 30 days of performance history
        base_value = self.initial_balance
        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            daily_change = random.uniform(-0.03, 0.03)  # ±3% daily change
            base_value *= (1 + daily_change)
            
            self.performance_history.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': round(base_value, 2),
                'change': round(daily_change * 100, 2)
            })

    def calculate_win_rate(self) -> float:
        if not self.trade_history:
            return 0.0
        winning_trades = sum(1 for trade in self.trade_history if trade.calculate_pnl() > 0)
        return (winning_trades / len(self.trade_history)) * 100

    def calculate_total_pnl(self) -> float:
        return sum(trade.calculate_pnl() for trade in self.active_trades)

    def get_market_indices(self) -> Dict[str, float]:
        # Simulate market indices
        indices = {
            'SPY': random.uniform(450, 550),
            'QQQ': random.uniform(350, 450),
            'IWM': random.uniform(200, 250),
            'DIA': random.uniform(350, 400)
        }
        return {k: round(v, 2) for k, v in indices.items()}

    def get_top_movers(self) -> List[Dict[str, Any]]:
        # Simulate top movers
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        movers = []
        for symbol in symbols:
            change = random.uniform(-0.05, 0.05)
            movers.append({
                'symbol': symbol,
                'change': round(change * 100, 2),
                'volume': random.randint(1000000, 10000000)
            })
        return sorted(movers, key=lambda x: abs(x['change']), reverse=True)

    def calculate_market_sentiment(self) -> str:
        # Simulate market sentiment
        sentiment_score = random.uniform(-1, 1)
        if sentiment_score > 0.3:
            return 'BULLISH'
        elif sentiment_score < -0.3:
            return 'BEARISH'
        else:
            return 'NEUTRAL'

    def get_vix_value(self) -> float:
        # Simulate VIX value
        return round(random.uniform(15, 35), 2)

    def calculate_portfolio_value(self) -> float:
        return self.current_balance + self.calculate_total_pnl()

    def calculate_daily_change(self) -> float:
        if not self.performance_history:
            return 0.0
        today = self.performance_history[-1]['value']
        yesterday = self.performance_history[-2]['value']
        return round(today - yesterday, 2)

    def calculate_daily_change_percent(self) -> float:
        if not self.performance_history:
            return 0.0
        return self.performance_history[-1]['change']

    def get_positions(self) -> List[Dict[str, Any]]:
        positions = []
        for trade in self.active_trades:
            positions.append({
                'symbol': trade.symbol,
                'direction': trade.direction,
                'quantity': trade.quantity,
                'entry_price': trade.entry_price,
                'current_price': trade.get_current_price(),
                'pnl': trade.calculate_pnl(),
                'pnl_percent': trade.calculate_pnl_percent()
            })
        return positions

    def get_performance_history(self) -> List[Dict[str, Any]]:
        return self.performance_history

class SimulatedDataFetcher:
    """Simulated data fetcher for testing purposes."""
    
    def __init__(self, config):
        """Initialize the simulated data fetcher."""
        self.config = config
        self.logger = logging.getLogger("SimulateBot.DataFetcher")
    
    def get_market_data(self, symbol):
        """Get simulated market data."""
        self.logger.info(f"Getting simulated market data for {symbol}...")
        
        # Generate random price data
        base_price = 450.0 if symbol == "QQQ" else 200.0 if symbol == "TSLA" else 20.0
        price_change = random.uniform(-2.0, 2.0)
        price = base_price + price_change
        
        # Generate random volume data
        volume = random.randint(1000000, 5000000)
        
        # Generate random VIX data
        vix = random.uniform(15.0, 25.0)
        
        # Generate random sector performance data
        sector_performance = {
            "technology": random.uniform(-1.0, 2.0),
            "finance": random.uniform(-1.0, 2.0),
            "healthcare": random.uniform(-1.0, 2.0)
        }
        
        return {
            "symbol": symbol,
            "price": price,
            "change": price_change,
            "change_percent": (price_change / base_price) * 100,
            "volume": volume,
            "vix": vix,
            "sector_performance": sector_performance,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_options_data(self, symbol):
        """Get simulated options data."""
        self.logger.info(f"Getting simulated options data for {symbol}...")
        
        # Generate random options data
        base_price = 450.0 if symbol == "QQQ" else 200.0 if symbol == "TSLA" else 20.0
        options_data = []
        
        for i in range(5):
            strike = base_price + (i - 2) * 5
            expiry = (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d")
            
            options_data.append({
                "symbol": symbol,
                "strike": strike,
                "expiry": expiry,
                "option_type": "call",
                "last_price": random.uniform(1.0, 10.0),
                "bid": random.uniform(1.0, 10.0),
                "ask": random.uniform(1.0, 10.0),
                "volume": random.randint(100, 1000),
                "open_interest": random.randint(1000, 10000)
            })
        
        return options_data
    
    def get_news_data(self, symbol):
        """Get simulated news data."""
        self.logger.info(f"Getting simulated news data for {symbol}...")
        
        # Generate random news data
        news_templates = [
            f"{symbol} stock shows strong momentum",
            f"Analysts raise price target for {symbol}",
            f"{symbol} reports better-than-expected earnings",
            f"Market sentiment turns bullish for {symbol}",
            f"{symbol} faces headwinds from market volatility"
        ]
        
        news_data = []
        for i in range(3):
            news_data.append({
                "title": random.choice(news_templates),
                "source": random.choice(["Reuters", "Bloomberg", "CNBC", "Wall Street Journal"]),
                "published_at": (datetime.now() - timedelta(hours=i)).isoformat(),
                "url": f"https://example.com/news/{i}"
            })
        
        return news_data

class SimulatedDeepSeekScanner:
    """Simulated DeepSeek scanner for testing purposes."""
    
    def __init__(self, config):
        """Initialize the simulated DeepSeek scanner."""
        self.config = config
        self.logger = logging.getLogger("SimulateBot.DeepSeekScanner")
    
    def generate_recommendations(self):
        """Generate simulated trade recommendations."""
        self.logger.info("Generating simulated trade recommendations...")
        
        # Get symbols from config
        symbols = self.config["trading"]["symbols"]
        
        # Generate random recommendations
        recommendations = []
        for symbol in symbols:
            # 70% chance of generating a recommendation
            if random.random() < 0.7:
                # Generate random price data
                base_price = 450.0 if symbol == "QQQ" else 200.0 if symbol == "TSLA" else 20.0
                price_change = random.uniform(-2.0, 2.0)
                price = base_price + price_change
                
                # Determine direction based on price change
                direction = "bullish" if price_change > 0 else "bearish"
                
                # Generate random confidence
                confidence = random.uniform(0.6, 0.95)
                
                # Generate random stop loss and take profit
                stop_loss = price - (price * 0.02) if direction == "bullish" else price + (price * 0.02)
                take_profit = price + (price * 0.05) if direction == "bullish" else price - (price * 0.05)
                
                # Generate random expiry and strike
                expiry = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                strike = price
                
                # Generate random option type
                option_type = "call" if direction == "bullish" else "put"
                
                # Generate random reasoning
                reasoning_templates = [
                    "Strong momentum and positive market sentiment",
                    "Technical indicators suggest a breakout",
                    "Institutional buying pressure detected",
                    "Market volatility creating opportunities",
                    "Sector rotation favoring this stock"
                ]
                reasoning = random.choice(reasoning_templates)
                
                # Create recommendation
                recommendation = {
                    "symbol": symbol,
                    "direction": direction,
                    "confidence": confidence,
                    "entry_price": price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "expiry": expiry,
                    "strike": strike,
                    "option_type": option_type,
                    "reasoning": reasoning
                }
                
                recommendations.append(recommendation)
        
        return recommendations

class SimulatedChatGPTRiskManager:
    """Simulated ChatGPT risk manager for testing purposes."""
    
    def __init__(self, config):
        """Initialize the simulated ChatGPT risk manager."""
        self.config = config
        self.logger = logging.getLogger("SimulateBot.ChatGPTRiskManager")
    
    def assess_trade(self, trade_recommendation, market_context):
        """Assess a trade recommendation."""
        self.logger.info(f"Assessing trade recommendation for {trade_recommendation['symbol']}...")
        
        # Get confidence threshold from config
        confidence_threshold = self.config["ai_models"]["chatgpt"]["risk_manager"]["confidence_threshold"]
        
        # Determine if the trade should be approved based on confidence
        approved = trade_recommendation["confidence"] >= confidence_threshold
        
        # Generate random risk score
        risk_score = random.uniform(0.1, 0.9)
        
        # Generate random reasoning
        reasoning_templates = [
            "Market conditions are favorable for this trade",
            "Risk-reward ratio is acceptable",
            "Technical indicators support this direction",
            "Market volatility is within acceptable range",
            "Sector performance is positive",
            "Recent news is supportive of this trade",
            "Market conditions are unfavorable for this trade",
            "Risk-reward ratio is not acceptable",
            "Technical indicators do not support this direction",
            "Market volatility is too high",
            "Sector performance is negative",
            "Recent news is negative for this trade"
        ]
        reasoning = random.choice(reasoning_templates)
        
        # Create risk assessment
        risk_assessment = {
            "approved": approved,
            "confidence": trade_recommendation["confidence"],
            "risk_score": risk_score,
            "reason": reasoning,
            "timestamp": datetime.now().isoformat()
        }
        
        return risk_assessment

class SimulatedAutoCloser:
    """Simulated auto closer for testing purposes."""
    
    def __init__(self, config):
        """Initialize the simulated auto closer."""
        self.config = config
        self.logger = logging.getLogger("SimulateBot.AutoCloser")
    
    def should_close_position(self, position):
        """Determine if a position should be closed."""
        self.logger.info(f"Checking if position for {position['symbol']} should be closed...")
        
        # Get exit rules from config
        exit_rules = self.config["trading"]["exit_rules"]
        
        # Calculate price change percentage
        price_change_percent = ((position["current_price"] - position["entry_price"]) / position["entry_price"]) * 100
        
        # Check if stop loss or take profit is hit
        if position["side"] == "long":
            stop_loss_hit = position["current_price"] <= position["stop_loss"]
            take_profit_hit = position["current_price"] >= position["take_profit"]
        else:
            stop_loss_hit = position["current_price"] >= position["stop_loss"]
            take_profit_hit = position["current_price"] <= position["take_profit"]
        
        # Check if max loss is hit
        max_loss_hit = abs(price_change_percent) >= exit_rules["max_loss_percent"]
        
        # Check if profit target is hit
        profit_target_hit = price_change_percent >= exit_rules["profit_target_percent"]
        
        # Check if trailing stop is hit
        trailing_stop_hit = False
        if position["side"] == "long" and price_change_percent > 0:
            trailing_stop_price = position["entry_price"] + (position["entry_price"] * (price_change_percent - exit_rules["trailing_stop_percent"]) / 100)
            trailing_stop_hit = position["current_price"] <= trailing_stop_price
        elif position["side"] == "short" and price_change_percent < 0:
            trailing_stop_price = position["entry_price"] + (position["entry_price"] * (price_change_percent + exit_rules["trailing_stop_percent"]) / 100)
            trailing_stop_hit = position["current_price"] >= trailing_stop_price
        
        # Check if max hold time is exceeded
        max_hold_time_exceeded = (datetime.now() - position["entry_time"]).total_seconds() / 3600 >= exit_rules["max_hold_time_hours"]
        
        # Determine if the position should be closed
        should_close = stop_loss_hit or take_profit_hit or max_loss_hit or profit_target_hit or trailing_stop_hit or max_hold_time_exceeded
        
        # Log the result
        if should_close:
            reason = "stop loss hit" if stop_loss_hit else "take profit hit" if take_profit_hit else "max loss hit" if max_loss_hit else "profit target hit" if profit_target_hit else "trailing stop hit" if trailing_stop_hit else "max hold time exceeded"
            self.logger.info(f"Position for {position['symbol']} should be closed: {reason}")
        else:
            self.logger.info(f"Position for {position['symbol']} should not be closed")
        
        return should_close

class SimulatedDualBot:
    """Simulated Dual Bot for testing purposes."""
    
    def __init__(self, config):
        """Initialize the simulated Dual Bot."""
        self.config = config
        self.logger = logging.getLogger("SimulateBot")
        self.logger.info("Initializing Simulated Dual Bot...")
        
        # Initialize components
        self.data_fetcher = SimulatedDataFetcher(config)
        self.scanner = SimulatedDeepSeekScanner(config)
        self.risk_manager = SimulatedChatGPTRiskManager(config)
        self.auto_closer = SimulatedAutoCloser(config)
        
        # Initialize state
        self.active_positions = []
        self.trade_history = []
        self.last_scan_time = None
        self.last_risk_check_time = None
        
        self.logger.info("Simulated Dual Bot initialized successfully!")
    
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
        # For simulation purposes, always return True
        return True
    
    def _get_market_condition(self):
        """Get the current market condition."""
        # For simulation purposes, randomly return a market condition
        return random.choice(["bullish", "bearish", "neutral"])
    
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
    
    def run(self, duration_minutes=60):
        """Run the simulated Dual Bot."""
        self.logger.info(f"Starting Simulated Dual Bot for {duration_minutes} minutes...")
        
        try:
            # Calculate end time
            end_time = datetime.now() + timedelta(minutes=duration_minutes)
            
            # Run the bot until the end time
            while datetime.now() < end_time:
                # Scan for trades every 5 minutes
                if self.last_scan_time is None or (datetime.now() - self.last_scan_time).total_seconds() >= 300:
                    self.scan_for_trades()
                
                # Check positions every 30 seconds
                if self.last_risk_check_time is None or (datetime.now() - self.last_risk_check_time).total_seconds() >= 30:
                    self.check_positions()
                
                # Sleep for 5 seconds
                time.sleep(5)
            
            self.logger.info("Simulated Dual Bot stopped.")
        except KeyboardInterrupt:
            self.logger.info("Simulated Dual Bot stopped by user.")
        except Exception as e:
            self.logger.error(f"Error running Simulated Dual Bot: {e}")
        finally:
            self.logger.info("Simulated Dual Bot stopped.")
            
            # Print summary
            self.logger.info("\n=== Simulation Summary ===")
            self.logger.info(f"Total trades: {len(self.trade_history)}")
            self.logger.info(f"Active positions: {len(self.active_positions)}")
            
            # Calculate win rate
            if self.trade_history:
                winning_trades = sum(1 for trade in self.trade_history if trade["current_price"] > trade["entry_price"])
                win_rate = winning_trades / len(self.trade_history) * 100
                self.logger.info(f"Win rate: {win_rate:.2f}%")
            
            self.logger.info("Simulation completed.")

def main():
    """Main function to run the simulated Dual Bot."""
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration.")
        return
    
    # Create and run the simulated bot
    bot = SimulatedDualBot(config)
    bot.run(duration_minutes=60)  # Run for 60 minutes

if __name__ == "__main__":
    main() 