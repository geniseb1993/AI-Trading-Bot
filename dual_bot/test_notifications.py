#!/usr/bin/env python
"""
Test script for Dual Bot notification utilities
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the parent directory to the path to import the dual_bot package
sys.path.append(str(Path(__file__).parent.parent))

from dual_bot.notification_utils import NotificationUtility
from dual_bot.config.config_loader import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NotificationTest")

def main():
    """Test the notification utilities."""
    logger.info("Testing notification utilities...")
    
    # Load configuration
    config = load_config()
    if not config:
        logger.error("Failed to load configuration")
        return
    
    # Initialize notification utility
    notification_util = NotificationUtility(config)
    
    # Test regular notification
    logger.info("Sending test notification...")
    success = notification_util.send_notification(
        message="This is a test notification from the Dual Bot",
        priority="medium",
        title="Test Notification"
    )
    logger.info(f"Regular notification {'sent successfully' if success else 'failed'}")
    
    # Test trade notification
    logger.info("Sending test trade notification...")
    success = notification_util.send_trade_notification(
        symbol="AAPL",
        action="BUY",
        price=150.25,
        quantity=10,
        priority="high"
    )
    logger.info(f"Trade notification {'sent successfully' if success else 'failed'}")
    
    # Test all priority levels with Discord
    priorities = ["low", "medium", "high"]
    for priority in priorities:
        logger.info(f"Testing Discord notification with {priority} priority...")
        success = notification_util.send_discord_notification(
            message=f"This is a test notification with {priority} priority",
            title=f"Discord Test - {priority.upper()}",
            priority=priority
        )
        logger.info(f"Discord {priority} notification {'sent successfully' if success else 'failed'}")
    
    # Test all priority levels with Telegram
    for priority in priorities:
        logger.info(f"Testing Telegram notification with {priority} priority...")
        success = notification_util.send_telegram_notification(
            message=f"This is a test notification with {priority} priority",
            title=f"Telegram Test - {priority.upper()}",
            priority=priority
        )
        logger.info(f"Telegram {priority} notification {'sent successfully' if success else 'failed'}")
    
    logger.info("Notification tests completed")

if __name__ == "__main__":
    main() 