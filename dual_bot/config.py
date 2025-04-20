import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Optional
import logging

class ConfigManager:
    def __init__(self):
        self.env_path = Path(".env")
        self.load_env()
        self.required_keys = {
            'data_sources': ['POLYGON_API_KEY', 'UNUSUAL_WHALES_API_KEY'],
            'ai_models': ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'DEEPSEEK_API_KEY'],
            'execution': ['ALPACA_API_KEY', 'ALPACA_API_SECRET'],
        }
        self.optional_keys = {
            'notifications': ['DISCORD_WEBHOOK_URL', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID'],
            'logging': ['LOG_LEVEL']
        }
        
    def load_env(self):
        """Load environment variables from .env file"""
        if not self.env_path.exists():
            raise FileNotFoundError(f".env file not found at {self.env_path}")
        load_dotenv(self.env_path)
        
    def validate_api_key(self, key: str, value: str) -> bool:
        """Basic validation for API keys"""
        if not value:
            return False
        # Add specific validation rules for different API keys
        if 'POLYGON' in key and len(value) < 20:
            return False
        if 'OPENAI' in key and not value.startswith('sk-'):
            return False
        return True
        
    def get_env_vars(self, category: str) -> Dict[str, str]:
        """Get environment variables for a specific category"""
        vars_dict = {}
        for key in self.required_keys.get(category, []):
            value = os.getenv(key)
            if not value or not self.validate_api_key(key, value):
                logging.warning(f"Missing or invalid {key} in {category}")
            vars_dict[key] = value
        return vars_dict
        
    def get_optional_env_vars(self, category: str) -> Dict[str, Optional[str]]:
        """Get optional environment variables for a specific category"""
        return {key: os.getenv(key) for key in self.optional_keys.get(category, [])}
        
    def validate_all(self) -> bool:
        """Validate all required environment variables"""
        missing_keys = []
        invalid_keys = []
        
        for category, keys in self.required_keys.items():
            for key in keys:
                value = os.getenv(key)
                if not value:
                    missing_keys.append(key)
                elif not self.validate_api_key(key, value):
                    invalid_keys.append(key)
                    
        if missing_keys or invalid_keys:
            if missing_keys:
                logging.error(f"Missing required keys: {', '.join(missing_keys)}")
            if invalid_keys:
                logging.error(f"Invalid keys: {', '.join(invalid_keys)}")
            return False
        return True

# Create a global instance
config = ConfigManager()

# Example usage:
# polygon_key = config.get_env_vars('data_sources')['POLYGON_API_KEY']
# log_level = config.get_optional_env_vars('logging')['LOG_LEVEL'] 