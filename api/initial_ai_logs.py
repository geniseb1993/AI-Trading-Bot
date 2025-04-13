"""
Initial AI Activity Logs Generator

This script generates sample AI activity logs for testing the UI.
"""

import logging
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

from ai_activity_log import get_activity_logger, ActivityType

logger = logging.getLogger(__name__)

def generate_sample_logs(count: int = 50) -> List[Dict[str, Any]]:
    """
    Generate sample AI activity logs
    
    Args:
        count: Number of log entries to generate
        
    Returns:
        List of generated log entries
    """
    # Get the activity logger
    activity_logger = get_activity_logger()
    
    # Clear existing logs
    activity_logger.clear_logs()
    
    # Common symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'META', 'SPY', 'QQQ', 'XLF']
    
    # Sample log entries
    logs = []
    
    # Start time (48 hours ago)
    start_time = datetime.now() - timedelta(hours=48)
    
    # Generate logs with time progression
    for i in range(count):
        # Calculate timestamp with progressive time
        timestamp = start_time + timedelta(minutes=random.randint(0, 60 * 48))
        
        # Select random symbol
        symbol = random.choice(symbols)
        
        # Generate a random activity type with weighted probabilities
        activity_weights = {
            ActivityType.TRADE_ENTRY: 0.2,
            ActivityType.TRADE_EXIT: 0.2,
            ActivityType.SIGNAL_GENERATED: 0.15,
            ActivityType.MARKET_ANALYSIS: 0.1,
            ActivityType.STRATEGY_SWITCH: 0.05,
            ActivityType.RISK_ADJUSTMENT: 0.1,
            ActivityType.SYSTEM_ACTION: 0.1,
            ActivityType.BACKTEST: 0.05,
            ActivityType.ERROR: 0.05
        }
        
        activity_types = list(activity_weights.keys())
        activity_probabilities = [activity_weights[a] for a in activity_types]
        activity_type = random.choices(activity_types, weights=activity_probabilities, k=1)[0]
        
        # Generate log entry based on activity type
        if activity_type == ActivityType.TRADE_ENTRY:
            entry_price = round(random.uniform(100, 500), 2)
            position_type = random.choice(["LONG", "SHORT"])
            stop_loss = round(entry_price * (0.95 if position_type == "LONG" else 1.05), 2)
            take_profit = round(entry_price * (1.1 if position_type == "LONG" else 0.9), 2)
            
            log_entry = activity_logger.log_activity(
                activity_type=activity_type,
                description=f"Entered {position_type} position in {symbol}",
                details={
                    "position_type": position_type,
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "quantity": random.randint(1, 100),
                    "reason": "Strong momentum detected" if position_type == "LONG" else "Bearish reversal pattern"
                },
                symbol=symbol,
                source="ai_trader"
            )
            # Override timestamp for testing
            log_entry["timestamp"] = timestamp.isoformat()
        
        elif activity_type == ActivityType.TRADE_EXIT:
            exit_price = round(random.uniform(100, 500), 2)
            position_type = random.choice(["LONG", "SHORT"])
            entry_price = round(exit_price * (0.9 if position_type == "LONG" else 1.1), 2)
            profit = round(exit_price - entry_price if position_type == "LONG" else entry_price - exit_price, 2)
            profit_pct = round((profit / entry_price) * 100, 2)
            
            log_entry = activity_logger.log_activity(
                activity_type=activity_type,
                description=f"Exited {position_type} position in {symbol} with {profit_pct}% {'profit' if profit > 0 else 'loss'}",
                details={
                    "position_type": position_type,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "profit": profit,
                    "profit_pct": profit_pct,
                    "exit_reason": random.choice([
                        "Target reached", 
                        "Stop loss hit", 
                        "Risk management", 
                        "Technical reversal",
                        "AI prediction change"
                    ])
                },
                symbol=symbol,
                source="ai_trader"
            )
            # Override timestamp for testing
            log_entry["timestamp"] = timestamp.isoformat()
        
        elif activity_type == ActivityType.SIGNAL_GENERATED:
            signal_score = round(random.uniform(5, 10), 1)
            position_type = random.choice(["LONG", "SHORT"])
            price = round(random.uniform(100, 500), 2)
            
            log_entry = activity_logger.log_activity(
                activity_type=activity_type,
                description=f"Generated {position_type} signal for {symbol}",
                details={
                    "signal_score": signal_score,
                    "position_type": position_type,
                    "price": price,
                    "indicators": {
                        "rsi": round(random.uniform(0, 100), 1),
                        "macd": round(random.uniform(-2, 2), 2),
                        "ma_crossover": random.choice([True, False]),
                        "volume_surge": random.choice([True, False])
                    }
                },
                symbol=symbol,
                source="ai_signal_engine"
            )
            # Override timestamp for testing
            log_entry["timestamp"] = timestamp.isoformat()
        
        elif activity_type == ActivityType.MARKET_ANALYSIS:
            log_entry = activity_logger.log_activity(
                activity_type=activity_type,
                description=f"Completed market analysis for {symbol}",
                details={
                    "prediction": random.choice(["bullish", "bearish", "neutral"]),
                    "confidence": round(random.uniform(0.5, 0.95), 2),
                    "key_levels": {
                        "support": round(random.uniform(100, 400), 2),
                        "resistance": round(random.uniform(200, 500), 2)
                    },
                    "market_sentiment": random.choice(["positive", "negative", "mixed"])
                },
                symbol=symbol,
                source="market_analyzer"
            )
            # Override timestamp for testing
            log_entry["timestamp"] = timestamp.isoformat()
        
        elif activity_type == ActivityType.STRATEGY_SWITCH:
            old_strategy = random.choice(["trend_following", "mean_reversion", "breakout", "momentum"])
            new_strategy = random.choice(["trend_following", "mean_reversion", "breakout", "momentum"])
            
            while new_strategy == old_strategy:
                new_strategy = random.choice(["trend_following", "mean_reversion", "breakout", "momentum"])
            
            log_entry = activity_logger.log_activity(
                activity_type=activity_type,
                description=f"Switched strategy from {old_strategy} to {new_strategy}",
                details={
                    "old_strategy": old_strategy,
                    "new_strategy": new_strategy,
                    "reason": random.choice([
                        "Market conditions changed",
                        "Performance optimization",
                        "Risk management",
                        "Volatility adjustment"
                    ]),
                    "market_regime": random.choice(["bullish", "bearish", "choppy", "trending"])
                },
                source="strategy_manager"
            )
            # Override timestamp for testing
            log_entry["timestamp"] = timestamp.isoformat()
        
        elif activity_type == ActivityType.RISK_ADJUSTMENT:
            old_risk = round(random.uniform(0.005, 0.03), 3)
            new_risk = round(random.uniform(0.005, 0.03), 3)
            
            while abs(new_risk - old_risk) < 0.005:
                new_risk = round(random.uniform(0.005, 0.03), 3)
            
            log_entry = activity_logger.log_activity(
                activity_type=activity_type,
                description=f"Adjusted risk parameters",
                details={
                    "old_risk_per_trade": old_risk,
                    "new_risk_per_trade": new_risk,
                    "max_open_positions": random.randint(3, 10),
                    "reason": random.choice([
                        "Portfolio value change",
                        "Volatility increase",
                        "Drawdown protection",
                        "Performance optimization"
                    ])
                },
                source="risk_manager"
            )
            # Override timestamp for testing
            log_entry["timestamp"] = timestamp.isoformat()
        
        elif activity_type == ActivityType.SYSTEM_ACTION:
            actions = [
                "Trading bot started",
                "Trading bot stopped",
                "Data refresh completed",
                "Scheduled maintenance",
                "Configuration updated",
                "API connection established",
                "Market data updated"
            ]
            
            log_entry = activity_logger.log_activity(
                activity_type=activity_type,
                description=random.choice(actions),
                details={
                    "status": "success",
                    "duration_seconds": random.randint(1, 30)
                },
                source="system"
            )
            # Override timestamp for testing
            log_entry["timestamp"] = timestamp.isoformat()
        
        elif activity_type == ActivityType.BACKTEST:
            log_entry = activity_logger.log_activity(
                activity_type=activity_type,
                description=f"Completed backtest for {random.choice(['trend_following', 'mean_reversion', 'breakout'])} strategy",
                details={
                    "period": f"{random.randint(30, 180)} days",
                    "win_rate": round(random.uniform(0.4, 0.7), 2),
                    "profit_factor": round(random.uniform(1.1, 2.5), 2),
                    "max_drawdown": round(random.uniform(0.05, 0.2), 2),
                    "trade_count": random.randint(20, 100)
                },
                source="backtest_engine"
            )
            # Override timestamp for testing
            log_entry["timestamp"] = timestamp.isoformat()
        
        elif activity_type == ActivityType.ERROR:
            errors = [
                "Failed to fetch market data",
                "Order execution failed",
                "API connection timeout",
                "Invalid signal parameters",
                "Risk calculation error",
                "Position sizing error"
            ]
            
            log_entry = activity_logger.log_activity(
                activity_type=activity_type,
                description=random.choice(errors),
                details={
                    "error_code": random.randint(400, 500),
                    "severity": random.choice(["low", "medium", "high"]),
                    "recovery_action": random.choice([
                        "Automatic retry",
                        "System restart",
                        "Manual intervention required"
                    ])
                },
                symbol=random.choice([symbol, None]),
                source="system"
            )
            # Override timestamp for testing
            log_entry["timestamp"] = timestamp.isoformat()
        
        logs.append(log_entry)
    
    # Save logs to file
    activity_logger._save_logs()
    
    logger.info(f"Generated {len(logs)} sample AI activity logs")
    return logs

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Generate sample logs
    logs = generate_sample_logs(50)
    
    print(f"Generated {len(logs)} sample AI activity logs.") 