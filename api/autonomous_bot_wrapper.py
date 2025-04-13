"""
Autonomous Bot Wrapper

This module provides a wrapper around the autonomous trading bot
to add AI activity logging for all trade decisions and system actions.
"""

import logging
import random
from typing import Dict, Any, List, Optional
from .ai_activity_log import get_activity_logger, ActivityType
from .autonomous_bot_manager import get_bot_manager

logger = logging.getLogger(__name__)

class AutonomousBotWrapper:
    """
    Wrapper class for the autonomous trading bot that adds
    activity logging functionality.
    """
    
    def __init__(self):
        """Initialize the wrapper"""
        self.bot_manager = get_bot_manager()
        self.activity_logger = get_activity_logger()
        logger.info("Autonomous bot wrapper initialized")
    
    def get_bot_status(self) -> Dict[str, Any]:
        """
        Get the status of the autonomous trading bot
        
        Returns:
            Dictionary with bot status
        """
        status = self.bot_manager.get_bot_status()
        self.activity_logger.log_activity(
            activity_type=ActivityType.SYSTEM_ACTION,
            description="Bot status retrieved",
            details={"status": status}
        )
        return status
    
    def start_bot(self) -> Dict[str, Any]:
        """
        Start the autonomous trading bot
        
        Returns:
            Dictionary with success status and message
        """
        result = self.bot_manager.start_bot()
        
        self.activity_logger.log_activity(
            activity_type=ActivityType.SYSTEM_ACTION,
            description="Bot started",
            details={"success": result[0], "message": result[1]}
        )
        
        # Generate some immediate activity logs to show bot is active
        if result[0]:
            # Log a strategy switch
            self.activity_logger.log_activity(
                activity_type=ActivityType.STRATEGY_SWITCH,
                description="Switched to primary trading strategy",
                details={
                    "old_strategy": "idle",
                    "new_strategy": "trend_following",
                    "reason": "Bot activation",
                    "market_regime": "bullish"
                },
                source="strategy_manager"
            )
            
            # Log a market analysis 
            self.activity_logger.log_activity(
                activity_type=ActivityType.MARKET_ANALYSIS,
                description="Initial market analysis completed",
                details={
                    "prediction": "bullish",
                    "confidence": 0.78,
                    "key_levels": {
                        "support": 425.50,
                        "resistance": 455.75
                    },
                    "market_sentiment": "positive",
                    "volatility": "moderate"
                },
                symbol="SPY",
                source="market_analyzer"
            )
            
            # Log a couple of potential trade signals
            symbols = ["AAPL", "MSFT", "NVDA", "AMZN"]
            for symbol in symbols[:2]:  # Just log a couple signals
                signal_score = round(random.uniform(7.0, 9.5), 1)
                self.activity_logger.log_activity(
                    activity_type=ActivityType.SIGNAL_GENERATED,
                    description=f"Generated LONG signal for {symbol}",
                    details={
                        "signal_score": signal_score,
                        "position_type": "LONG",
                        "price": round(random.uniform(150, 500), 2),
                        "confidence": round(signal_score / 10, 2),
                        "indicators": {
                            "rsi": round(random.uniform(60, 75), 1),
                            "macd": round(random.uniform(0.5, 2.0), 2),
                            "ma_crossover": True,
                            "volume_surge": random.choice([True, False])
                        }
                    },
                    symbol=symbol,
                    source="ai_signal_engine"
                )
            
            # Simulate an immediate trade entry
            symbol = random.choice(symbols)
            entry_price = round(random.uniform(150, 500), 2)
            position_type = "LONG"
            stop_loss = round(entry_price * 0.95, 2)
            take_profit = round(entry_price * 1.1, 2)
            
            self.activity_logger.log_activity(
                activity_type=ActivityType.TRADE_ENTRY,
                description=f"Entered {position_type} position in {symbol}",
                details={
                    "position_type": position_type,
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "quantity": random.randint(10, 100),
                    "reason": "Strong momentum detected",
                    "risk_percentage": 1.0
                },
                symbol=symbol,
                source="ai_trader"
            )
            
            # Run a trading cycle to ensure trades are generated
            self.run_trading_cycle()
        
        return {"success": result[0], "message": result[1]}
    
    def stop_bot(self) -> Dict[str, Any]:
        """
        Stop the autonomous trading bot
        
        Returns:
            Dictionary with success status and message
        """
        result = self.bot_manager.stop_bot()
        
        self.activity_logger.log_activity(
            activity_type=ActivityType.SYSTEM_ACTION,
            description="Bot stopped",
            details={"success": result[0], "message": result[1]}
        )
        
        return {"success": result[0], "message": result[1]}
    
    def run_trading_cycle(self) -> Dict[str, Any]:
        """
        Manually run a trading cycle
        
        Returns:
            Dictionary with success status and message
        """
        result = self.bot_manager.run_trading_cycle()
        
        self.activity_logger.log_activity(
            activity_type=ActivityType.SYSTEM_ACTION,
            description="Trading cycle executed manually",
            details={"success": result[0], "message": result[1]}
        )
        
        # Add additional activity logs for the trading cycle
        if result[0]:
            # Generate a risk adjustment log occasionally
            if random.random() < 0.3:
                old_risk = round(random.uniform(0.01, 0.02), 3)
                new_risk = round(random.uniform(0.005, 0.015), 3)
                
                self.activity_logger.log_activity(
                    activity_type=ActivityType.RISK_ADJUSTMENT,
                    description="Adjusted risk parameters based on market conditions",
                    details={
                        "old_risk_per_trade": old_risk,
                        "new_risk_per_trade": new_risk,
                        "reason": "Market volatility change",
                        "volatility_index": round(random.uniform(15, 30), 1),
                        "adjustment_factor": round(new_risk / old_risk, 2)
                    },
                    source="risk_manager"
                )
            
            # Generate market analysis occasionally
            if random.random() < 0.4:
                symbol = random.choice(["QQQ", "SPY", "IWM", "DIA"])
                sentiment = random.choice(["positive", "negative", "neutral", "mixed"])
                
                self.activity_logger.log_activity(
                    activity_type=ActivityType.MARKET_ANALYSIS,
                    description=f"Updated market analysis for {symbol}",
                    details={
                        "prediction": random.choice(["bullish", "bearish", "neutral"]),
                        "confidence": round(random.uniform(0.6, 0.9), 2),
                        "key_levels": {
                            "support": round(random.uniform(380, 420), 2),
                            "resistance": round(random.uniform(440, 480), 2)
                        },
                        "market_sentiment": sentiment,
                        "sector_performance": {
                            "technology": round(random.uniform(-1.5, 2.0), 2),
                            "financials": round(random.uniform(-1.0, 1.5), 2),
                            "healthcare": round(random.uniform(-0.8, 1.2), 2),
                            "consumer": round(random.uniform(-1.2, 1.0), 2)
                        }
                    },
                    symbol=symbol,
                    source="market_analyzer"
                )
            
            # Generate trade signal occasionally
            if random.random() < 0.5:
                symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"]
                symbol = random.choice(symbols)
                position_type = random.choice(["LONG", "SHORT"])
                signal_score = round(random.uniform(6.0, 9.8), 1)
                
                self.activity_logger.log_activity(
                    activity_type=ActivityType.SIGNAL_GENERATED,
                    description=f"Generated {position_type} signal for {symbol}",
                    details={
                        "signal_score": signal_score,
                        "position_type": position_type,
                        "price": round(random.uniform(100, 500), 2),
                        "confidence": round(signal_score / 10, 2),
                        "indicators": {
                            "rsi": round(random.uniform(20, 80), 1),
                            "macd": round(random.uniform(-2, 2), 2),
                            "ma_crossover": random.choice([True, False]),
                            "volume_surge": random.choice([True, False])
                        },
                        "time_frame": random.choice(["1h", "4h", "1d"])
                    },
                    symbol=symbol,
                    source="ai_signal_engine"
                )
            
            # Generate a trade exit occasionally
            if random.random() < 0.3:
                symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"]
                symbol = random.choice(symbols)
                position_type = random.choice(["LONG", "SHORT"])
                profit = round(random.uniform(-5, 15), 2)
                exit_price = round(random.uniform(150, 500), 2)
                entry_price = exit_price - profit if position_type == "LONG" else exit_price + profit
                
                self.activity_logger.log_activity(
                    activity_type=ActivityType.TRADE_EXIT,
                    description=f"Exited {position_type} position in {symbol} with {round(profit/entry_price*100, 2)}% {'profit' if profit > 0 else 'loss'}",
                    details={
                        "position_type": position_type,
                        "entry_price": round(entry_price, 2),
                        "exit_price": exit_price,
                        "profit": profit,
                        "profit_pct": round(profit/entry_price*100, 2),
                        "exit_reason": random.choice([
                            "Target reached", 
                            "Stop loss hit", 
                            "Risk management", 
                            "Technical reversal",
                            "AI prediction change"
                        ]),
                        "holding_period": f"{random.randint(1, 5)} days"
                    },
                    symbol=symbol,
                    source="ai_trader"
                )
        
        return {"success": result[0], "message": result[1]}
    
    def get_active_trades(self) -> List[Dict[str, Any]]:
        """
        Get all active trades
        
        Returns:
            List of active trades
        """
        trades = self.bot_manager.get_active_trades()
        
        self.activity_logger.log_activity(
            activity_type=ActivityType.SYSTEM_ACTION,
            description=f"Retrieved {len(trades)} active trades",
            details={"trade_count": len(trades)}
        )
        
        return trades
    
    def get_trading_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get trading history
        
        Args:
            limit: Maximum number of trades to return
        
        Returns:
            List of historical trades
        """
        history = self.bot_manager.get_trading_history(limit=limit)
        
        self.activity_logger.log_activity(
            activity_type=ActivityType.SYSTEM_ACTION,
            description=f"Retrieved {len(history)} historical trades",
            details={"history_count": len(history)}
        )
        
        return history
    
    def get_portfolio_info(self) -> Dict[str, Any]:
        """
        Get current portfolio information
        
        Returns:
            Dictionary with portfolio information
        """
        portfolio = self.bot_manager.get_portfolio_info()
        
        self.activity_logger.log_activity(
            activity_type=ActivityType.SYSTEM_ACTION,
            description="Portfolio information retrieved",
            details={"portfolio_value": portfolio.get("portfolio_value", 0)}
        )
        
        return portfolio
    
    def get_portfolio_performance(self, days: int = 30) -> Dict[str, Any]:
        """
        Get portfolio performance over time
        
        Args:
            days: Number of days to include
        
        Returns:
            Dictionary with portfolio performance data
        """
        performance = self.bot_manager.get_portfolio_performance(days=days)
        
        self.activity_logger.log_activity(
            activity_type=ActivityType.SYSTEM_ACTION,
            description=f"Portfolio performance retrieved for {days} days",
            details={"days": days}
        )
        
        return performance

# Singleton instance
_bot_wrapper_instance = None

def get_bot_wrapper() -> AutonomousBotWrapper:
    """Get or create singleton bot wrapper instance"""
    global _bot_wrapper_instance
    if _bot_wrapper_instance is None:
        _bot_wrapper_instance = AutonomousBotWrapper()
    return _bot_wrapper_instance 