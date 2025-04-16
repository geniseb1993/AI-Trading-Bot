"""
Test script for simulating the notification system in different trading scenarios.
This script demonstrates how notifications would work in a production environment.
"""

import logging
import time
import random
from datetime import datetime, timedelta
from notification_service import NotificationService
from config import ExecutionModelConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Market data simulation
SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]
SETUP_TYPES = ["Breakout", "Pullback", "Reversal", "Range", "Trend Following"]
MARKET_CONDITIONS = ["Bullish", "Bearish", "Sideways", "Volatile", "Ranging"]

def generate_realistic_price(base_price, volatility=0.02):
    """Generate realistic price movements"""
    change = base_price * volatility * random.uniform(-1, 1)
    return round(base_price + change, 2)

def simulate_trade_setup():
    """Simulate a trade setup with realistic market data"""
    symbol = random.choice(SYMBOLS)
    base_price = random.uniform(100, 500)
    direction = random.choice(["LONG", "SHORT"])
    setup_type = random.choice(SETUP_TYPES)
    market_condition = random.choice(MARKET_CONDITIONS)
    
    entry_price = generate_realistic_price(base_price)
    stop_loss = generate_realistic_price(entry_price, 0.015) * (-1 if direction == "LONG" else 1)
    profit_target = generate_realistic_price(entry_price, 0.03) * (1 if direction == "LONG" else -1)
    
    return {
        "symbol": symbol,
        "direction": direction,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "profit_target": profit_target,
        "confidence": round(random.uniform(0.7, 0.95), 2),
        "setup_type": setup_type,
        "market_condition": market_condition,
        "volume": int(random.uniform(100000, 2000000)),
        "timestamp": datetime.now().isoformat(),
        "indicators": {
            "rsi": round(random.uniform(20, 80), 2),
            "macd": round(random.uniform(-2, 2), 2),
            "volume_ma": int(random.uniform(800000, 1500000))
        }
    }

def simulate_stop_loss_trigger():
    """Simulate a stop loss being triggered with realistic data"""
    symbol = random.choice(SYMBOLS)
    entry_price = random.uniform(100, 500)
    direction = random.choice(["LONG", "SHORT"])
    
    return {
        "symbol": symbol,
        "direction": direction,
        "entry_price": entry_price,
        "exit_price": generate_realistic_price(entry_price, 0.015) * (-1 if direction == "LONG" else 1),
        "pnl": round(random.uniform(-1000, -100), 2),
        "reason": "Stop Loss",
        "market_condition": random.choice(MARKET_CONDITIONS),
        "volume": int(random.uniform(100000, 2000000)),
        "timestamp": datetime.now().isoformat(),
        "holding_time": str(timedelta(minutes=random.randint(5, 120)))
    }

def simulate_profit_target():
    """Simulate hitting a profit target with realistic data"""
    symbol = random.choice(SYMBOLS)
    entry_price = random.uniform(100, 500)
    direction = random.choice(["LONG", "SHORT"])
    
    return {
        "symbol": symbol,
        "direction": direction,
        "entry_price": entry_price,
        "exit_price": generate_realistic_price(entry_price, 0.03) * (1 if direction == "LONG" else -1),
        "pnl": round(random.uniform(100, 1000), 2),
        "reason": "Profit Target",
        "market_condition": random.choice(MARKET_CONDITIONS),
        "volume": int(random.uniform(100000, 2000000)),
        "timestamp": datetime.now().isoformat(),
        "holding_time": str(timedelta(minutes=random.randint(5, 120)))
    }

def simulate_risk_breach():
    """Simulate a risk management breach with realistic data"""
    return {
        "symbol": random.choice(SYMBOLS),
        "risk_level": random.choice(["HIGH", "MEDIUM", "LOW"]),
        "current_exposure": round(random.uniform(0.06, 0.09), 3),
        "max_allowed": 0.05,
        "total_positions": random.randint(3, 8),
        "max_positions": 5,
        "timestamp": datetime.now().isoformat(),
        "account_risk": round(random.uniform(0.04, 0.07), 3),
        "max_account_risk": 0.05
    }

def simulate_system_error():
    """Simulate various system errors"""
    error_types = [
        ("ConnectionError", "Failed to connect to market data feed"),
        ("DataError", "Invalid data received from exchange"),
        ("ExecutionError", "Order execution failed"),
        ("RiskError", "Risk management system error"),
        ("DatabaseError", "Failed to update trade database")
    ]
    
    error_type, message = random.choice(error_types)
    return {
        "error_type": error_type,
        "message": message,
        "severity": random.choice(["HIGH", "MEDIUM", "LOW"]),
        "timestamp": datetime.now().isoformat(),
        "retry_count": random.randint(1, 3),
        "system_component": random.choice(["Market Data", "Order Execution", "Risk Management", "Database"])
    }

def simulate_market_alert():
    """Simulate market condition alerts"""
    return {
        "alert_type": random.choice(["VOLATILITY_SPIKE", "LIQUIDITY_DROP", "TREND_CHANGE", "NEWS_EVENT"]),
        "symbol": random.choice(SYMBOLS),
        "severity": random.choice(["HIGH", "MEDIUM", "LOW"]),
        "message": f"Market alert: {random.choice(['Unusual volume detected', 'Price spike observed', 'Trend reversal forming', 'Breaking news impact'])}",
        "timestamp": datetime.now().isoformat(),
        "market_data": {
            "volume": int(random.uniform(100000, 2000000)),
            "volatility": round(random.uniform(0.01, 0.05), 3),
            "spread": round(random.uniform(0.01, 0.1), 3)
        }
    }

def main():
    # Load configuration
    config = ExecutionModelConfig()
    
    # Initialize notification service
    notification_service = NotificationService(config.config)
    
    logger.info("Starting enhanced notification system simulation...")
    logger.info("Press Ctrl+C to stop the simulation")
    
    try:
        while True:
            # Simulate trade entry
            logger.info("\nSimulating trade entry...")
            trade_setup = simulate_trade_setup()
            notification_service.send_trade_alert(trade_setup)
            time.sleep(3)
            
            # Simulate market alert
            logger.info("\nSimulating market alert...")
            market_alert = simulate_market_alert()
            notification_service.send_trade_alert(market_alert)
            time.sleep(3)
            
            # Simulate stop loss
            logger.info("\nSimulating stop loss trigger...")
            stop_loss = simulate_stop_loss_trigger()
            notification_service.send_trade_alert(stop_loss)
            time.sleep(3)
            
            # Simulate profit target
            logger.info("\nSimulating profit target hit...")
            profit_target = simulate_profit_target()
            notification_service.send_trade_alert(profit_target)
            time.sleep(3)
            
            # Simulate risk breach
            logger.info("\nSimulating risk management breach...")
            risk_breach = simulate_risk_breach()
            notification_service.send_trade_alert(risk_breach)
            time.sleep(3)
            
            # Simulate system error
            logger.info("\nSimulating system error...")
            system_error = simulate_system_error()
            notification_service.send_trade_alert(system_error)
            time.sleep(3)
            
            # Show notification history
            logger.info("\nRecent notification history:")
            history = notification_service.get_notification_history(limit=5)
            for notification in history:
                logger.info(f"Time: {notification['timestamp']}")
                logger.info(f"Message: {notification['message']}")
                logger.info(f"Success: {notification['success']}")
                logger.info("---")
            
            time.sleep(5)  # Wait before next round
            
    except KeyboardInterrupt:
        logger.info("\nSimulation stopped by user")
    except Exception as e:
        logger.error(f"Error during simulation: {str(e)}")

if __name__ == "__main__":
    main() 