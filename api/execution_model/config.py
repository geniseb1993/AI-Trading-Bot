"""
Configuration module for the Execution Model

This module handles loading, saving, and accessing the execution model configuration.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "market_analyzer": {
        "trend_detection": {
            "adx_threshold": 25,
            "ma_lookback": 20,
            "directional_threshold": 0.6
        },
        "choppy_detection": {
            "rsi_range": [40, 60],
            "range_threshold": 0.005,
            "volatility_factor": 0.7
        },
        "no_trade_detection": {
            "volume_threshold": 0.7,
            "volatility_threshold": 0.5,
            "news_events": True
        }
    },
    "risk_management": {
        "max_position_size": 0.02,  # 2% of account
        "max_daily_risk": 0.05,     # 5% of account
        "default_risk_reward": 2,   # 1:2 risk to reward
        "adaptive_stops": True,
        "max_positions": 5,
        "correlation_limit": 0.7,   # Limit correlated positions
        "use_ai_risk_management": True,  # Enable AI-powered risk management
        "risk_profile": "moderate"  # Default risk profile (conservative, moderate, aggressive)
    },
    "ai_risk_management": {
        "volatility_multiplier": 2.0,  # Multiplier for ATR in stop-loss calculation
        "risk_tolerance_factor": 1.0,  # Scaling factor for risk tolerance (adjust up/down based on performance)
        "max_position_size_percent": 5.0,  # Maximum position size as percent of portfolio
        "risk_per_trade_percent": 1.0,  # Default risk per trade as percent of portfolio
        "use_gpt_for_risk": True,  # Whether to use GPT for additional risk insights
        "min_risk_score": 60,  # Minimum risk score (0-100) required to take a trade
        "reward_risk_ratio_min": 1.5,  # Minimum reward-to-risk ratio required
        "auto_adjust_position_size": True  # Automatically adjust position size based on setup quality
    },
    "execution": {
        "volume_confirmation": True,
        "volume_threshold": 1.5,    # 150% of average volume
        "time_based_rules": True,
        "avoid_high_spread": True,
        "min_volatility": 0.005,    # Minimum volatility for a trade
        "max_volatility": 0.03,     # Maximum volatility for a trade
        "cooldown_enabled": True,   # Enable cooldown timer to prevent overtrading
        "max_trades_per_hour": 3,   # Maximum number of trades per hour
        "max_trades_per_day": 10,   # Maximum number of trades per day
        "cooldown_minutes": 20,     # Minimum time between trades in minutes
        "cooldown_adaptive": True   # Adjust cooldown based on market volatility and risk
    },
    "institutional_flow": {
        "unusual_options_weight": 0.7,
        "dark_pool_weight": 0.8,
        "min_flow_signal": 0.6,
        "correlation_window": 20    # Days to check for flow-price correlation
    },
    "notifications": {
        "email_enabled": False,
        "email_sender": "",
        "email_password": "",
        "email_recipients": [],
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sms_enabled": False,
        "twilio_account_sid": "",
        "twilio_auth_token": "",
        "twilio_from_number": "",
        "twilio_to_numbers": [],
        "desktop_enabled": True,
        "voice_enabled": False,
        "voice_command": "",
        "notification_history_limit": 100,
        "alert_on_entry": True,
        "alert_on_exit": True,
        "alert_on_stop_loss": True,
        "alert_on_profit_target": True,
        "alert_on_risk_breach": True,
        "alert_on_system_error": True,
        "alert_cooldown_minutes": 5  # Minimum time between alerts for the same symbol
    },
    "pnl_logging": {
        "enabled": True,
        "log_to_csv": True,
        "logs_directory": "data/logs",
        "trade_log_file": "trades.csv",
        "daily_pnl_file": "daily_pnl.csv",
        "backup_enabled": True,
        "backup_frequency_days": 7,
        "auto_calculate_daily": True,
        "export_to_google_sheets": False,
        "google_sheets_id": "",
        "retention_period_days": 365  # How long to keep log entries
    },
    "ai_signal_ranking": {
        "enabled": True,
        "min_confidence_threshold": 0.65,  # Minimum AI confidence to consider a signal valid
        "volume_weight": 0.25,            # Weight for volume factor in ranking
        "trend_weight": 0.25,             # Weight for trend strength in ranking
        "historical_weight": 0.30,        # Weight for historical performance in ranking
        "institutional_weight": 0.20,     # Weight for institutional flow in ranking
        "use_gpt_insights": True,         # Whether to use GPT for market analysis
        "gpt_model": "anthropic/claude-3.7-sonnet",  # Default GPT model to use
        "insights_cache_minutes": 60,     # How long to cache GPT insights 
        "insights_symbols_per_day": 10,   # How many symbols to analyze per day (API cost control)
        "daily_market_summary": True,     # Whether to generate daily market summaries
        "optimize_trade_setups": True,    # Whether to enhance trade setups with GPT insights
        "confidence_boost_threshold": 0.8  # AI confidence above which position size can be increased
    }
}

class ExecutionModelConfig:
    """Manages configuration for the execution model"""
    
    def __init__(self, config_path=None):
        """
        Initialize with optional config path
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or "execution_model_config.json"
        self.config = self._load_config()
        
    def _load_config(self):
        """Load configuration from file or use defaults"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded execution model config from {self.config_path}")
                return config
            except Exception as e:
                logger.error(f"Error loading execution model config: {str(e)}")
                logger.info("Using default execution model configuration")
                return DEFAULT_CONFIG
        else:
            logger.info(f"Config file {self.config_path} not found. Using default configuration")
            return DEFAULT_CONFIG
            
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Saved execution model config to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving execution model config: {str(e)}")
            return False
            
    def get(self, section, key=None, default=None):
        """
        Get a configuration value
        
        Args:
            section: Configuration section
            key: Optional key within the section
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        if section not in self.config:
            return default
            
        if key is None:
            return self.config[section]
            
        return self.config[section].get(key, default)
        
    def update(self, section, key, value):
        """
        Update a configuration value
        
        Args:
            section: Configuration section
            key: Key within the section
            value: New value
            
        Returns:
            True if successful, False otherwise
        """
        if section not in self.config:
            self.config[section] = {}
            
        self.config[section][key] = value
        return self.save_config()
        
    def reset_to_default(self):
        """Reset configuration to default values"""
        self.config = DEFAULT_CONFIG.copy()
        return self.save_config()

def get_config(config_path=None):
    """
    Get execution model configuration
    
    Args:
        config_path: Optional path to the configuration file
    
    Returns:
        ExecutionModelConfig instance
    """
    return ExecutionModelConfig(config_path)

# Add a standalone save_config function to support existing code
def save_config(config_obj):
    """
    Save configuration to file
    
    Args:
        config_obj: ExecutionModelConfig instance or config dictionary
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # If it's already an ExecutionModelConfig instance
        if isinstance(config_obj, ExecutionModelConfig):
            return config_obj.save_config()
        
        # Otherwise, it's likely a dictionary
        # Create a temporary ExecutionModelConfig object and save
        temp_config = ExecutionModelConfig()
        temp_config.config = config_obj
        return temp_config.save_config()
    except Exception as e:
        logger.error(f"Error in save_config: {str(e)}")
        return False 