"""
Configuration validator for Dual Bot.
Validates settings from config.json and environment variables.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class ConfigValidationError(Exception):
    """Exception raised for configuration validation errors."""
    pass

def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate the configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of validation warnings (empty if no warnings)
    """
    warnings = []
    
    # Validate trading settings
    if "trading" in config:
        trading_warnings = validate_trading_config(config["trading"])
        warnings.extend(trading_warnings)
    
    # Validate execution settings
    if "execution" in config:
        execution_warnings = validate_execution_config(config["execution"])
        warnings.extend(execution_warnings)
    
    # Validate data sources
    if "data_sources" in config:
        data_warnings = validate_data_sources_config(config["data_sources"])
        warnings.extend(data_warnings)
    
    # Validate AI models
    if "ai_models" in config:
        ai_warnings = validate_ai_models_config(config["ai_models"])
        warnings.extend(ai_warnings)
    
    return warnings

def validate_trading_config(trading_config: Dict[str, Any]) -> List[str]:
    """Validate trading configuration."""
    warnings = []
    
    # Validate symbols
    if "symbols" in trading_config:
        if not isinstance(trading_config["symbols"], list):
            warnings.append("trading.symbols must be a list")
        elif not trading_config["symbols"]:
            warnings.append("trading.symbols list is empty")
    
    # Validate risk management
    if "risk_management" in trading_config:
        risk_warnings = validate_risk_management(trading_config["risk_management"])
        warnings.extend(risk_warnings)
    
    # Validate exit rules
    if "exit_rules" in trading_config:
        exit_warnings = validate_exit_rules(trading_config["exit_rules"])
        warnings.extend(exit_warnings)
    
    # Validate monitoring settings
    if "monitor_interval_seconds" in trading_config:
        if not isinstance(trading_config["monitor_interval_seconds"], (int, float)):
            warnings.append("trading.monitor_interval_seconds must be a number")
        elif trading_config["monitor_interval_seconds"] < 1:
            warnings.append("trading.monitor_interval_seconds should be at least 1 second")
    
    if "risk_check_interval_minutes" in trading_config:
        if not isinstance(trading_config["risk_check_interval_minutes"], (int, float)):
            warnings.append("trading.risk_check_interval_minutes must be a number")
        elif trading_config["risk_check_interval_minutes"] < 1:
            warnings.append("trading.risk_check_interval_minutes should be at least 1 minute")
    
    return warnings

def validate_risk_management(risk_config: Dict[str, Any]) -> List[str]:
    """Validate risk management configuration."""
    warnings = []
    
    # Validate percentage values
    percentage_fields = [
        "max_loss_per_trade_percent",
        "max_daily_loss_percent",
        "default_stop_loss_percent",
        "default_take_profit_percent"
    ]
    
    for field in percentage_fields:
        if field in risk_config:
            if not isinstance(risk_config[field], (int, float)):
                warnings.append(f"risk_management.{field} must be a number")
            elif risk_config[field] <= 0:
                warnings.append(f"risk_management.{field} must be positive")
            elif risk_config[field] > 100:
                warnings.append(f"risk_management.{field} should not exceed 100%")
    
    return warnings

def validate_exit_rules(exit_config: Dict[str, Any]) -> List[str]:
    """Validate exit rules configuration."""
    warnings = []
    
    # Validate percentage values
    percentage_fields = [
        "max_loss_percent",
        "profit_target_percent",
        "trailing_stop_percent"
    ]
    
    for field in percentage_fields:
        if field in exit_config:
            if not isinstance(exit_config[field], (int, float)):
                warnings.append(f"exit_rules.{field} must be a number")
            elif exit_config[field] <= 0:
                warnings.append(f"exit_rules.{field} must be positive")
            elif exit_config[field] > 100:
                warnings.append(f"exit_rules.{field} should not exceed 100%")
    
    # Validate max hold time
    if "max_hold_time_hours" in exit_config:
        if not isinstance(exit_config["max_hold_time_hours"], (int, float)):
            warnings.append("exit_rules.max_hold_time_hours must be a number")
        elif exit_config["max_hold_time_hours"] <= 0:
            warnings.append("exit_rules.max_hold_time_hours must be positive")
    
    return warnings

def validate_execution_config(execution_config: Dict[str, Any]) -> List[str]:
    """Validate execution configuration."""
    warnings = []
    
    # Validate Alpaca settings
    if "alpaca" in execution_config:
        alpaca_warnings = validate_alpaca_config(execution_config["alpaca"])
        warnings.extend(alpaca_warnings)
    
    return warnings

def validate_alpaca_config(alpaca_config: Dict[str, Any]) -> List[str]:
    """Validate Alpaca configuration."""
    warnings = []
    
    # Validate API keys
    if alpaca_config.get("enabled", False):
        if not alpaca_config.get("api_key"):
            warnings.append("alpaca.api_key is required when enabled")
        if not alpaca_config.get("api_secret"):
            warnings.append("alpaca.api_secret is required when enabled")
    
    # Validate order settings
    if "order_settings" in alpaca_config:
        order_warnings = validate_order_settings(alpaca_config["order_settings"])
        warnings.extend(order_warnings)
    
    return warnings

def validate_order_settings(order_config: Dict[str, Any]) -> List[str]:
    """Validate order settings configuration."""
    warnings = []
    
    # Validate time in force
    if "default_time_in_force" in order_config:
        valid_tif = ["day", "gtc", "ioc", "fok"]
        if order_config["default_time_in_force"] not in valid_tif:
            warnings.append(f"order_settings.default_time_in_force must be one of: {', '.join(valid_tif)}")
    
    # Validate wait time
    if "max_order_wait_seconds" in order_config:
        if not isinstance(order_config["max_order_wait_seconds"], (int, float)):
            warnings.append("order_settings.max_order_wait_seconds must be a number")
        elif order_config["max_order_wait_seconds"] < 1:
            warnings.append("order_settings.max_order_wait_seconds should be at least 1 second")
    
    # Validate retry settings
    if "retry_attempts" in order_config:
        if not isinstance(order_config["retry_attempts"], int):
            warnings.append("order_settings.retry_attempts must be an integer")
        elif order_config["retry_attempts"] < 0:
            warnings.append("order_settings.retry_attempts should be non-negative")
    
    if "retry_delay_seconds" in order_config:
        if not isinstance(order_config["retry_delay_seconds"], (int, float)):
            warnings.append("order_settings.retry_delay_seconds must be a number")
        elif order_config["retry_delay_seconds"] < 0:
            warnings.append("order_settings.retry_delay_seconds should be non-negative")
    
    return warnings

def validate_data_sources_config(data_config: Dict[str, Any]) -> List[str]:
    """Validate data sources configuration."""
    warnings = []
    
    # Validate Polygon settings
    if "polygon" in data_config and data_config["polygon"].get("enabled", False):
        if not data_config["polygon"].get("api_key"):
            warnings.append("polygon.api_key is required when enabled")
    
    # Validate Unusual Whales settings
    if "unusual_whales" in data_config and data_config["unusual_whales"].get("enabled", False):
        if not data_config["unusual_whales"].get("api_key"):
            warnings.append("unusual_whales.api_key is required when enabled")
    
    # Validate News API settings
    if "news_api" in data_config and data_config["news_api"].get("enabled", False):
        if not data_config["news_api"].get("api_key"):
            warnings.append("news_api.api_key is required when enabled")
    
    return warnings

def validate_ai_models_config(ai_config: Dict[str, Any]) -> List[str]:
    """Validate AI models configuration."""
    warnings = []
    
    # Validate DeepSeek settings
    if "deepseek" in ai_config and ai_config["deepseek"].get("enabled", False):
        if not ai_config["deepseek"].get("api_key"):
            warnings.append("deepseek.api_key is required when enabled")
    
    # Validate ChatGPT settings
    if "chatgpt" in ai_config and ai_config["chatgpt"].get("enabled", False):
        if not ai_config["chatgpt"].get("api_key"):
            warnings.append("chatgpt.api_key is required when enabled")
            
        # Validate ChatGPT risk manager settings
        if "risk_manager" in ai_config["chatgpt"]:
            risk_config = ai_config["chatgpt"]["risk_manager"]
            
            # Validate confidence threshold
            if "confidence_threshold" in risk_config:
                if not isinstance(risk_config["confidence_threshold"], (int, float)):
                    warnings.append("chatgpt.risk_manager.confidence_threshold must be a number")
                elif risk_config["confidence_threshold"] < 0 or risk_config["confidence_threshold"] > 1:
                    warnings.append("chatgpt.risk_manager.confidence_threshold must be between 0 and 1")
            
            # Validate max tokens
            if "max_tokens" in risk_config:
                if not isinstance(risk_config["max_tokens"], int):
                    warnings.append("chatgpt.risk_manager.max_tokens must be an integer")
                elif risk_config["max_tokens"] < 1:
                    warnings.append("chatgpt.risk_manager.max_tokens must be positive")
            
            # Validate temperature
            if "temperature" in risk_config:
                if not isinstance(risk_config["temperature"], (int, float)):
                    warnings.append("chatgpt.risk_manager.temperature must be a number")
                elif risk_config["temperature"] < 0 or risk_config["temperature"] > 1:
                    warnings.append("chatgpt.risk_manager.temperature must be between 0 and 1")
            
            # Validate retry settings
            if "retry_attempts" in risk_config:
                if not isinstance(risk_config["retry_attempts"], int):
                    warnings.append("chatgpt.risk_manager.retry_attempts must be an integer")
                elif risk_config["retry_attempts"] < 0:
                    warnings.append("chatgpt.risk_manager.retry_attempts should be non-negative")
            
            if "retry_delay_seconds" in risk_config:
                if not isinstance(risk_config["retry_delay_seconds"], (int, float)):
                    warnings.append("chatgpt.risk_manager.retry_delay_seconds must be a number")
                elif risk_config["retry_delay_seconds"] < 0:
                    warnings.append("chatgpt.risk_manager.retry_delay_seconds should be non-negative")
    
    return warnings 