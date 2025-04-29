"""
Configuration Manager

A centralized system for managing application configuration across different environments.
Supports loading from environment variables, JSON files, and defaults.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Base exception for configuration-related errors."""
    pass

class ConfigManager:
    """
    Configuration manager for handling environment-specific settings.
    
    Features:
    - Environment-based configuration
    - Hierarchical configuration with overrides
    - Environment variable support
    - JSON file loading
    - Default values
    - Configuration validation
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager."""
        # Only initialize once
        if self._initialized:
            return
        
        # Configuration storage
        self._config = {}
        self._env = None
        self._config_files = []
        self._initialized = True
    
    def init_app(self, 
        app=None, 
        env: Optional[str] = None, 
        config_files: Optional[List[str]] = None,
        defaults: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize configuration with application context.
        
        Args:
            app: Flask application instance (optional).
            env: Environment name (development, testing, production).
            config_files: List of configuration file paths.
            defaults: Default configuration values.
        """
        # Determine environment
        self._env = env or os.environ.get("APP_ENV", "development")
        logger.info(f"Initializing configuration for environment: {self._env}")
        
        # Reset configuration
        self._config = {}
        
        # Load defaults
        if defaults:
            self._config.update(defaults)
            logger.debug("Loaded default configuration")
        
        # Load configuration files
        if config_files:
            self._config_files = config_files
            for file_path in config_files:
                self.load_config_file(file_path)
        
        # Load environment-specific configuration
        self._load_env_config()
        
        # Apply configuration to Flask app if provided
        if app:
            for key, value in self._config.items():
                if key.isupper():
                    app.config[key] = value
            logger.debug("Applied configuration to Flask application")
    
    def load_config_file(self, file_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            file_path: Path to the configuration file.
            
        Raises:
            ConfigError: If file cannot be loaded.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Configuration file not found: {file_path}")
                return
            
            with open(path, "r") as f:
                config_data = json.load(f)
            
            # Update configuration
            self._config.update(config_data)
            logger.info(f"Loaded configuration from file: {file_path}")
            
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in configuration file {file_path}: {str(e)}")
        except Exception as e:
            raise ConfigError(f"Failed to load configuration file {file_path}: {str(e)}")
    
    def _load_env_config(self) -> None:
        """
        Load configuration from environment variables.
        
        Environment variables with prefix APP_ are loaded into configuration.
        """
        prefix = "APP_"
        env_config = {}
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):]
                
                # Convert to appropriate type
                if value.lower() in ("true", "yes", "1"):
                    env_config[config_key] = True
                elif value.lower() in ("false", "no", "0"):
                    env_config[config_key] = False
                elif value.isdigit():
                    env_config[config_key] = int(value)
                elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                    env_config[config_key] = float(value)
                else:
                    env_config[config_key] = value
        
        # Update configuration
        self._config.update(env_config)
        logger.debug("Loaded configuration from environment variables")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key.
            value: Configuration value.
        """
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary of all configuration values.
        """
        return self._config.copy()
    
    def get_env(self) -> str:
        """
        Get current environment.
        
        Returns:
            Current environment name.
        """
        return self._env
    
    def is_development(self) -> bool:
        """
        Check if current environment is development.
        
        Returns:
            True if development environment, False otherwise.
        """
        return self._env == "development"
    
    def is_testing(self) -> bool:
        """
        Check if current environment is testing.
        
        Returns:
            True if testing environment, False otherwise.
        """
        return self._env == "testing"
    
    def is_production(self) -> bool:
        """
        Check if current environment is production.
        
        Returns:
            True if production environment, False otherwise.
        """
        return self._env == "production"
    
    def validate_required(self, keys: List[str]) -> List[str]:
        """
        Validate required configuration keys.
        
        Args:
            keys: List of required configuration keys.
            
        Returns:
            List of missing keys.
        """
        missing = []
        for key in keys:
            if key not in self._config:
                missing.append(key)
        return missing
    
    def reload(self) -> None:
        """
        Reload configuration from files and environment variables.
        """
        # Reset configuration
        self._config = {}
        
        # Reload configuration files
        for file_path in self._config_files:
            self.load_config_file(file_path)
        
        # Reload environment variables
        self._load_env_config()
        
        logger.info("Reloaded configuration")

# Factory function to create or get configuration manager instance
def get_config_manager() -> ConfigManager:
    """
    Get configuration manager instance.
    
    Returns:
        ConfigManager instance.
    """
    return ConfigManager() 