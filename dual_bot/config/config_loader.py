"""
Configuration loader for Dual Bot.
Loads settings from config.json and environment variables.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from .config_validator import validate_config
from pathlib import Path
from dotenv import load_dotenv

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(simulation_mode=False):
    """
    Load configuration from config.json and environment variables.
    
    Args:
        simulation_mode (bool): If True, suppress API key warnings for simulation.
        
    Returns:
        Dictionary containing configuration settings
    """
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.info(f"Loaded environment variables from {env_path}")
    else:
        logger.warning(f"Environment file not found at {env_path}")
    
    config_path = Path(__file__).parent / "config.json"
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # Override with environment variables
        config = _override_from_env(config)
        
        # Validate the configuration
        if not simulation_mode:
            validate_config(config)
        
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file at {config_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return None

def _override_from_env(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Override configuration values with environment variables.
    
    Args:
        config: Base configuration dictionary
        
    Returns:
        Updated configuration dictionary
    """
    # Data sources
    if "data_sources" in config:
        # Polygon
        if "polygon" in config["data_sources"] and "POLYGON_API_KEY" in os.environ:
            config["data_sources"]["polygon"]["api_key"] = os.environ["POLYGON_API_KEY"]
        
        # Unusual Whales
        if "unusual_whales" in config["data_sources"] and "UNUSUAL_WHALES_API_KEY" in os.environ:
            config["data_sources"]["unusual_whales"]["api_key"] = os.environ["UNUSUAL_WHALES_API_KEY"]
        
        # News API
        if "news_api" in config["data_sources"] and "NEWS_API_KEY" in os.environ:
            config["data_sources"]["news_api"]["api_key"] = os.environ["NEWS_API_KEY"]
    
    # AI models
    if "ai_models" in config:
        # DeepSeek
        if "deepseek" in config["ai_models"] and "DEEPSEEK_API_KEY" in os.environ:
            config["ai_models"]["deepseek"]["api_key"] = os.environ["DEEPSEEK_API_KEY"]
        
        # ChatGPT
        if "chatgpt" in config["ai_models"] and "OPENAI_API_KEY" in os.environ:
            config["ai_models"]["chatgpt"]["api_key"] = os.environ["OPENAI_API_KEY"]
    
    # Trading settings
    if "trading" in config:
        # Symbols
        if "DUAL_BOT_SYMBOLS" in os.environ:
            config["trading"]["symbols"] = os.environ["DUAL_BOT_SYMBOLS"].split(",")
        
        # Risk management
        if "trading" in config and "risk_management" in config["trading"]:
            risk_config = config["trading"]["risk_management"]
            
            if "DUAL_BOT_MAX_LOSS_PERCENT" in os.environ:
                risk_config["max_loss_per_trade_percent"] = float(os.environ["DUAL_BOT_MAX_LOSS_PERCENT"])
            
            if "DUAL_BOT_DAILY_LOSS_PERCENT" in os.environ:
                risk_config["max_daily_loss_percent"] = float(os.environ["DUAL_BOT_DAILY_LOSS_PERCENT"])
        
        # Exit rules
        if "trading" in config and "exit_rules" in config["trading"]:
            exit_config = config["trading"]["exit_rules"]
            
            if "DUAL_BOT_MAX_LOSS_PERCENT" in os.environ:
                exit_config["max_loss_percent"] = float(os.environ["DUAL_BOT_MAX_LOSS_PERCENT"])
            
            if "DUAL_BOT_PROFIT_TARGET_PERCENT" in os.environ:
                exit_config["profit_target_percent"] = float(os.environ["DUAL_BOT_PROFIT_TARGET_PERCENT"])
            
            if "DUAL_BOT_TRAILING_STOP_PERCENT" in os.environ:
                exit_config["trailing_stop_percent"] = float(os.environ["DUAL_BOT_TRAILING_STOP_PERCENT"])
            
            if "DUAL_BOT_MAX_HOLD_HOURS" in os.environ:
                exit_config["max_hold_time_hours"] = float(os.environ["DUAL_BOT_MAX_HOLD_HOURS"])
        
        # Monitoring settings
        if "DUAL_BOT_MONITOR_INTERVAL" in os.environ:
            config["trading"]["monitor_interval_seconds"] = int(os.environ["DUAL_BOT_MONITOR_INTERVAL"])
        
        if "DUAL_BOT_RISK_CHECK_INTERVAL" in os.environ:
            config["trading"]["risk_check_interval_minutes"] = int(os.environ["DUAL_BOT_RISK_CHECK_INTERVAL"])
    
    # Execution settings
    if "execution" in config and "alpaca" in config["execution"]:
        alpaca_config = config["execution"]["alpaca"]
        
        if "ALPACA_API_KEY" in os.environ:
            alpaca_config["api_key"] = os.environ["ALPACA_API_KEY"]
        
        if "ALPACA_API_SECRET" in os.environ:
            alpaca_config["api_secret"] = os.environ["ALPACA_API_SECRET"]
        
        if "ALPACA_BASE_URL" in os.environ:
            alpaca_config["base_url"] = os.environ["ALPACA_BASE_URL"]
        
        if "ALPACA_DATA_URL" in os.environ:
            alpaca_config["data_url"] = os.environ["ALPACA_DATA_URL"]
        
        if "ALPACA_PAPER_TRADING" in os.environ:
            alpaca_config["paper_trading"] = os.environ["ALPACA_PAPER_TRADING"].lower() == "true"
    
    # Notifications
    if "notifications" in config:
        # Discord
        if "discord" in config["notifications"] and "DISCORD_WEBHOOK_URL" in os.environ:
            config["notifications"]["discord"]["webhook_url"] = os.environ["DISCORD_WEBHOOK_URL"]
        
        # Telegram
        if "telegram" in config["notifications"]:
            if "TELEGRAM_BOT_TOKEN" in os.environ:
                config["notifications"]["telegram"]["bot_token"] = os.environ["TELEGRAM_BOT_TOKEN"]
            
            if "TELEGRAM_CHAT_ID" in os.environ:
                config["notifications"]["telegram"]["chat_id"] = os.environ["TELEGRAM_CHAT_ID"]
    
    return config

def setup_logging(config):
    """
    Set up logging based on configuration.
    
    Args:
        config: Configuration dictionary
    """
    log_level = getattr(logging, config.get("logging", {}).get("level", "INFO"))
    log_file = config.get("logging", {}).get("file", "dual_bot.log")
    
    # Create logs directory if it doesn't exist
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
    )
    
    logger.info(f"Logging configured with level {log_level} and file {log_file}")

# Load configuration and set up logging
config = load_config()
logger = setup_logging(config) 