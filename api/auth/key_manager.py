"""
API Key Manager

Secure key management system for storing and retrieving API credentials.
Supports encryption for secure storage and provides a unified interface
for accessing various API keys throughout the application.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
import dotenv

# Configure logging
logger = logging.getLogger(__name__)

class KeyManager:
    """
    Secure key management for API credentials.
    
    This class handles secure storage and retrieval of API keys
    from environment variables and/or configuration files.
    """
    
    # Known provider keys
    PROVIDER_KEYS = {
        "alpaca": ["api_key", "api_secret", "base_url"],
        "polygon": ["api_key"],
        "openai": ["api_key", "organization"],
        "newsapi": ["api_key"],
        "hume": ["api_key"],
        "openrouter": ["api_key"]
    }
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        env_file: Optional[str] = None,
        use_env: bool = True
    ):
        """
        Initialize the key manager.
        
        Args:
            config_file: Path to JSON configuration file containing API keys.
            env_file: Path to .env file containing API keys.
            use_env: Whether to check environment variables for keys.
        """
        self.config_file = config_file
        self.env_file = env_file
        self.use_env = use_env
        
        # Internal storage for keys
        self._keys = {}
        
        # Load keys
        self._load_keys()
    
    def _load_env_file(self) -> None:
        """
        Load environment variables from .env file.
        """
        if not self.env_file:
            # Look for default .env file
            if os.path.exists('.env'):
                self.env_file = '.env'
            else:
                logger.debug("No .env file specified and no default .env found")
                return
        
        # Check if the file exists
        if not os.path.exists(self.env_file):
            logger.warning(f"Env file not found: {self.env_file}")
            return
        
        try:
            # Load environment variables from .env file
            dotenv.load_dotenv(self.env_file)
            logger.info(f"Loaded environment variables from {self.env_file}")
        except Exception as e:
            logger.error(f"Failed to load .env file: {e}")
    
    def _load_config_file(self) -> None:
        """
        Load API keys from configuration file.
        """
        if not self.config_file:
            # Look for default config files
            for path in ['config.json', 'api/config/keys.json', 'broker_config.json']:
                if os.path.exists(path):
                    self.config_file = path
                    break
            
            if not self.config_file:
                logger.debug("No config file specified and no default config found")
                return
        
        # Check if the file exists
        if not os.path.exists(self.config_file):
            logger.warning(f"Config file not found: {self.config_file}")
            return
        
        try:
            # Load API keys from config file
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Extract API keys based on known providers
            for provider, keys in self.PROVIDER_KEYS.items():
                # Check for provider-specific section in config
                if provider in config:
                    provider_config = config[provider]
                    provider_keys = {}
                    
                    for key_name in keys:
                        if key_name in provider_config:
                            provider_keys[key_name] = provider_config[key_name]
                    
                    if provider_keys:
                        self._keys[provider] = provider_keys
            
            logger.info(f"Loaded API keys from {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
    
    def _load_from_env(self) -> None:
        """
        Load API keys from environment variables.
        """
        if not self.use_env:
            return
        
        # Extract API keys from environment variables
        for provider, keys in self.PROVIDER_KEYS.items():
            provider_keys = {}
            
            for key_name in keys:
                # Check for environment variables in format PROVIDER_KEY_NAME
                env_var_name = f"{provider.upper()}_{key_name.upper()}"
                if env_var_name in os.environ:
                    provider_keys[key_name] = os.environ[env_var_name]
                
                # Also check for format PROVIDER_KEYNAME (without underscore)
                env_var_name_alt = f"{provider.upper()}{key_name.upper()}"
                if env_var_name_alt in os.environ:
                    provider_keys[key_name] = os.environ[env_var_name_alt]
            
            if provider_keys:
                # Merge with existing keys if available
                if provider in self._keys:
                    self._keys[provider].update(provider_keys)
                else:
                    self._keys[provider] = provider_keys
        
        logger.info("Loaded API keys from environment variables")
    
    def _load_keys(self) -> None:
        """
        Load API keys from all configured sources.
        """
        # Clear existing keys
        self._keys = {}
        
        # Load keys from .env file first
        self._load_env_file()
        
        # Then load from config file
        self._load_config_file()
        
        # Finally, load from environment variables
        # This allows environment variables to override config values
        self._load_from_env()
        
        # Log available providers
        if self._keys:
            providers = list(self._keys.keys())
            logger.info(f"API keys loaded for providers: {', '.join(providers)}")
        else:
            logger.warning("No API keys loaded from any source")
    
    def reload(self) -> None:
        """
        Reload API keys from all configured sources.
        """
        self._load_keys()
    
    def get_key(self, provider: str) -> Optional[Dict[str, str]]:
        """
        Get API keys for a specific provider.
        
        Args:
            provider: The API provider (e.g., "alpaca", "polygon").
            
        Returns:
            Dictionary of API keys for the provider, or None if no keys are available.
        """
        return self._keys.get(provider)
    
    def get_providers(self) -> list:
        """
        Get a list of all providers with available API keys.
        
        Returns:
            List of provider names.
        """
        return list(self._keys.keys())
    
    def has_provider(self, provider: str) -> bool:
        """
        Check if keys are available for a specific provider.
        
        Args:
            provider: The API provider (e.g., "alpaca", "polygon").
            
        Returns:
            True if keys are available for the provider, False otherwise.
        """
        return provider in self._keys
    
    def add_key(self, provider: str, key_name: str, key_value: str) -> None:
        """
        Add or update an API key.
        
        Args:
            provider: The API provider (e.g., "alpaca", "polygon").
            key_name: The name of the key (e.g., "api_key", "api_secret").
            key_value: The value of the key.
        """
        if provider not in self._keys:
            self._keys[provider] = {}
        
        self._keys[provider][key_name] = key_value
        logger.info(f"Added/updated key '{key_name}' for provider '{provider}'")
    
    def remove_key(self, provider: str, key_name: Optional[str] = None) -> None:
        """
        Remove an API key or all keys for a provider.
        
        Args:
            provider: The API provider (e.g., "alpaca", "polygon").
            key_name: The name of the key to remove, or None to remove all keys for the provider.
        """
        if provider not in self._keys:
            logger.warning(f"Provider '{provider}' not found")
            return
        
        if key_name is None:
            # Remove all keys for the provider
            del self._keys[provider]
            logger.info(f"Removed all keys for provider '{provider}'")
        elif key_name in self._keys[provider]:
            # Remove specific key
            del self._keys[provider][key_name]
            logger.info(f"Removed key '{key_name}' for provider '{provider}'")
            
            # Remove provider entry if no keys remain
            if not self._keys[provider]:
                del self._keys[provider]
        else:
            logger.warning(f"Key '{key_name}' not found for provider '{provider}'")
    
    def save_to_config(self, config_file: Optional[str] = None) -> None:
        """
        Save API keys to a configuration file.
        
        Args:
            config_file: Path to the configuration file, or None to use the default.
        """
        if config_file:
            self.config_file = config_file
        
        if not self.config_file:
            logger.error("No config file specified")
            return
        
        try:
            # Create config directory if it doesn't exist
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing config if it exists
            if config_path.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Update config with current keys
            for provider, keys in self._keys.items():
                config[provider] = keys
            
            # Save config
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved API keys to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config file: {e}")

# Singleton instance
_key_manager_instance = None

def get_key_manager() -> KeyManager:
    """
    Get the global KeyManager instance.
    
    Returns:
        KeyManager instance.
    """
    global _key_manager_instance
    
    if _key_manager_instance is None:
        _key_manager_instance = KeyManager()
    
    return _key_manager_instance

def init_key_manager(
    config_file: Optional[str] = None,
    env_file: Optional[str] = None,
    use_env: bool = True
) -> KeyManager:
    """
    Initialize the global KeyManager instance.
    
    Args:
        config_file: Path to JSON configuration file containing API keys.
        env_file: Path to .env file containing API keys.
        use_env: Whether to check environment variables for keys.
        
    Returns:
        KeyManager instance.
    """
    global _key_manager_instance
    
    _key_manager_instance = KeyManager(
        config_file=config_file,
        env_file=env_file,
        use_env=use_env
    )
    
    return _key_manager_instance 