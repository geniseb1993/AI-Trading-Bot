"""
Notification Utilities Module

This module provides notification capabilities for the Dual Bot,
specifically for Discord and Telegram integration.
"""

import logging
import json
import requests
from typing import Dict, Optional, Union, List
from datetime import datetime

# Try to import the required packages
try:
    from discord_webhook import DiscordWebhook, DiscordEmbed
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False

try:
    import telegram
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)

class NotificationUtility:
    """
    Utility class for sending notifications through various channels
    """

    def __init__(self, config: Dict):
        """
        Initialize the notification utility with configuration
        
        Args:
            config: Configuration dictionary containing notification settings
        """
        self.config = config
        self.discord_config = config.get("notifications", {}).get("discord", {})
        self.telegram_config = config.get("notifications", {}).get("telegram", {})
        
        # Check if Discord is enabled
        self.discord_enabled = self.discord_config.get("enabled", False) and DISCORD_AVAILABLE
        self.discord_webhook_url = self.discord_config.get("webhook_url", "")
        
        # Check if Telegram is enabled
        self.telegram_enabled = self.telegram_config.get("enabled", False) and TELEGRAM_AVAILABLE
        self.telegram_bot_token = self.telegram_config.get("bot_token", "")
        self.telegram_chat_id = self.telegram_config.get("chat_id", "")
        
        # Initialize Telegram bot if enabled
        if self.telegram_enabled and self.telegram_bot_token:
            try:
                self.telegram_bot = telegram.Bot(token=self.telegram_bot_token)
                logger.info("Telegram bot initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Telegram bot: {str(e)}")
                self.telegram_enabled = False
        else:
            self.telegram_enabled = False
            
        logger.info(f"Discord notifications {'enabled' if self.discord_enabled else 'disabled'}")
        logger.info(f"Telegram notifications {'enabled' if self.telegram_enabled else 'disabled'}")

    def send_notification(self, message: str, priority: str = "medium", title: str = None) -> bool:
        """
        Send notification to all configured channels
        
        Args:
            message: The notification message
            priority: Priority level (high, medium, low)
            title: Optional title for the notification
        
        Returns:
            bool: True if at least one notification was sent successfully
        """
        success = False
        
        # Format the title based on priority if not provided
        if not title:
            title = f"Trading Bot Alert [{priority.upper()}]"
            
        # Send to Discord
        if self.discord_enabled:
            discord_success = self.send_discord_notification(
                message=message,
                title=title,
                priority=priority
            )
            success = success or discord_success
            
        # Send to Telegram
        if self.telegram_enabled:
            telegram_success = self.send_telegram_notification(
                message=message,
                title=title,
                priority=priority
            )
            success = success or telegram_success
            
        return success
    
    def send_discord_notification(
        self, 
        message: str, 
        title: str = None, 
        priority: str = "medium",
        color: int = None,
        fields: List[Dict] = None
    ) -> bool:
        """
        Send notification to Discord
        
        Args:
            message: The notification message
            title: Title for the Discord embed
            priority: Priority level (high, medium, low)
            color: Optional color for the Discord embed
            fields: Optional fields for the Discord embed
            
        Returns:
            bool: True if notification was sent successfully
        """
        if not self.discord_enabled or not self.discord_webhook_url:
            logger.warning("Discord notifications are disabled or webhook URL is not set")
            return False
            
        try:
            # Create webhook
            webhook = DiscordWebhook(
                url=self.discord_webhook_url,
                username="Trading Bot"
            )
            
            # Set color based on priority if not provided
            if color is None:
                color_map = {
                    "high": 0xFF0000,  # Red
                    "medium": 0xFFA500,  # Orange
                    "low": 0x00FF00  # Green
                }
                color = color_map.get(priority.lower(), 0xFFA500)
            
            # Create embed
            embed = DiscordEmbed(
                title=title if title else "Trading Bot Notification",
                description=message,
                color=color
            )
            
            # Add timestamp
            embed.set_timestamp()
            
            # Add fields if provided
            if fields:
                for field in fields:
                    embed.add_embed_field(
                        name=field.get("name", ""),
                        value=field.get("value", ""),
                        inline=field.get("inline", False)
                    )
                    
            # Add the embed to the webhook
            webhook.add_embed(embed)
            
            # Execute the webhook
            response = webhook.execute()
            
            success = response.status_code == 200
            if success:
                logger.info("Discord notification sent successfully")
            else:
                logger.error(f"Failed to send Discord notification: {response.status_code}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending Discord notification: {str(e)}")
            return False
    
    def send_telegram_notification(
        self, 
        message: str, 
        title: str = None, 
        priority: str = "medium"
    ) -> bool:
        """
        Send notification to Telegram
        
        Args:
            message: The notification message
            title: Title for the Telegram message
            priority: Priority level (high, medium, low)
            
        Returns:
            bool: True if notification was sent successfully
        """
        if not self.telegram_enabled or not self.telegram_chat_id:
            logger.warning("Telegram notifications are disabled or chat ID is not set")
            return False
            
        try:
            # Format the message with title and priority
            formatted_message = f"*{title}*\n\n{message}" if title else message
            
            # Add priority indicator
            priority_indicators = {
                "high": "🔴",
                "medium": "🟠",
                "low": "🟢"
            }
            indicator = priority_indicators.get(priority.lower(), "")
            if indicator:
                formatted_message = f"{indicator} {formatted_message}"
            
            # Send the message
            self.telegram_bot.send_message(
                chat_id=self.telegram_chat_id,
                text=formatted_message,
                parse_mode="Markdown"
            )
            
            logger.info("Telegram notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {str(e)}")
            return False
    
    def send_trade_notification(
        self, 
        symbol: str, 
        action: str, 
        price: float,
        quantity: float = None,
        priority: str = "medium"
    ) -> bool:
        """
        Send a trade-specific notification
        
        Args:
            symbol: The trading symbol
            action: The trade action (BUY, SELL, etc.)
            price: The trade price
            quantity: The trade quantity
            priority: Priority level (high, medium, low)
            
        Returns:
            bool: True if notification was sent successfully
        """
        title = f"Trade Alert: {symbol} {action}"
        
        # Create message
        message = f"Symbol: {symbol}\nAction: {action}\nPrice: ${price:.2f}"
        if quantity:
            message += f"\nQuantity: {quantity}"
            
        # Create fields for Discord
        fields = [
            {"name": "Symbol", "value": symbol, "inline": True},
            {"name": "Action", "value": action, "inline": True},
            {"name": "Price", "value": f"${price:.2f}", "inline": True}
        ]
        
        if quantity:
            fields.append({"name": "Quantity", "value": str(quantity), "inline": True})
            
        # Set color based on action
        color = 0x00FF00 if action.upper() in ["BUY", "LONG"] else 0xFF0000  # Green for buy, red for sell
        
        # Send to Discord
        discord_success = False
        if self.discord_enabled:
            discord_success = self.send_discord_notification(
                message=message,
                title=title,
                priority=priority,
                color=color,
                fields=fields
            )
            
        # Send to Telegram
        telegram_success = False
        if self.telegram_enabled:
            telegram_success = self.send_telegram_notification(
                message=message,
                title=title,
                priority=priority
            )
            
        return discord_success or telegram_success 