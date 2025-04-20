#!/usr/bin/env python
"""
Dual Bot Configuration Setup Script
This script helps set up the configuration for the Dual Bot trading system.
"""

import os
import json
import getpass
from pathlib import Path

def load_config():
    """Load the current configuration file."""
    config_path = Path(__file__).parent / "config" / "config.json"
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return None

def save_config(config):
    """Save the configuration to file."""
    config_path = Path(__file__).parent / "config" / "config.json"
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

def setup_data_sources(config):
    """Set up data source API keys."""
    print("\n=== Data Sources Configuration ===")
    
    # Polygon
    if config["data_sources"]["polygon"]["enabled"]:
        print("\nPolygon.io Configuration:")
        api_key = getpass.getpass("Enter your Polygon.io API key (leave blank to skip): ")
        if api_key:
            config["data_sources"]["polygon"]["api_key"] = api_key
    
    # Unusual Whales
    if config["data_sources"]["unusual_whales"]["enabled"]:
        print("\nUnusual Whales Configuration:")
        api_key = getpass.getpass("Enter your Unusual Whales API key (leave blank to skip): ")
        if api_key:
            config["data_sources"]["unusual_whales"]["api_key"] = api_key
    
    # News API
    if config["data_sources"]["news_api"]["enabled"]:
        print("\nNews API Configuration:")
        api_key = getpass.getpass("Enter your News API key (leave blank to skip): ")
        if api_key:
            config["data_sources"]["news_api"]["api_key"] = api_key
    
    return config

def setup_ai_models(config):
    """Set up AI model API keys."""
    print("\n=== AI Models Configuration ===")
    
    # DeepSeek
    if config["ai_models"]["deepseek"]["enabled"]:
        print("\nDeepSeek Configuration:")
        api_key = getpass.getpass("Enter your DeepSeek API key (leave blank to skip): ")
        if api_key:
            config["ai_models"]["deepseek"]["api_key"] = api_key
    
    # ChatGPT
    if config["ai_models"]["chatgpt"]["enabled"]:
        print("\nChatGPT Configuration:")
        api_key = getpass.getpass("Enter your OpenAI API key (leave blank to skip): ")
        if api_key:
            config["ai_models"]["chatgpt"]["api_key"] = api_key
    
    return config

def setup_execution(config):
    """Set up execution API keys."""
    print("\n=== Execution Configuration ===")
    
    # Alpaca
    if config["execution"]["alpaca"]["enabled"]:
        print("\nAlpaca Configuration:")
        api_key = getpass.getpass("Enter your Alpaca API key (leave blank to skip): ")
        if api_key:
            config["execution"]["alpaca"]["api_key"] = api_key
        
        api_secret = getpass.getpass("Enter your Alpaca API secret (leave blank to skip): ")
        if api_secret:
            config["execution"]["alpaca"]["api_secret"] = api_secret
    
    return config

def setup_notifications(config):
    """Set up notification settings."""
    print("\n=== Notifications Configuration ===")
    
    # Discord
    if config["notifications"]["discord"]["enabled"]:
        print("\nDiscord Configuration:")
        webhook_url = getpass.getpass("Enter your Discord webhook URL (leave blank to skip): ")
        if webhook_url:
            config["notifications"]["discord"]["webhook_url"] = webhook_url
    
    # Telegram
    if config["notifications"]["telegram"]["enabled"]:
        print("\nTelegram Configuration:")
        bot_token = getpass.getpass("Enter your Telegram bot token (leave blank to skip): ")
        if bot_token:
            config["notifications"]["telegram"]["bot_token"] = bot_token
        
        chat_id = input("Enter your Telegram chat ID (leave blank to skip): ")
        if chat_id:
            config["notifications"]["telegram"]["chat_id"] = chat_id
    
    return config

def setup_trading(config):
    """Set up trading parameters."""
    print("\n=== Trading Configuration ===")
    
    # Symbols
    print("\nTrading Symbols:")
    print(f"Current symbols: {', '.join(config['trading']['symbols'])}")
    symbols_input = input("Enter new symbols (comma-separated, leave blank to keep current): ")
    if symbols_input:
        config["trading"]["symbols"] = [s.strip() for s in symbols_input.split(",")]
    
    # Position sizing
    print("\nPosition Sizing:")
    print(f"Current type: {config['trading']['position_sizing']['type']}")
    print(f"Current amount: {config['trading']['position_sizing']['amount']}")
    
    sizing_type = input("Enter position sizing type (fixed/percentage, leave blank to keep current): ")
    if sizing_type:
        config["trading"]["position_sizing"]["type"] = sizing_type
    
    sizing_amount = input("Enter position sizing amount (leave blank to keep current): ")
    if sizing_amount:
        config["trading"]["position_sizing"]["amount"] = float(sizing_amount)
    
    return config

def main():
    """Main function to set up the configuration."""
    print("=== Dual Bot Configuration Setup ===")
    
    # Load current configuration
    config = load_config()
    if not config:
        return
    
    # Set up each section
    config = setup_data_sources(config)
    config = setup_ai_models(config)
    config = setup_execution(config)
    config = setup_notifications(config)
    config = setup_trading(config)
    
    # Save the configuration
    if save_config(config):
        print("\nConfiguration setup completed successfully!")
    else:
        print("\nFailed to save configuration.")

if __name__ == "__main__":
    main() 