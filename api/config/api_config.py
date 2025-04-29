"""
API Configuration

Centralized configuration for all API integrations, including
endpoints, timeouts, retries, and rate limits.
"""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Default configuration for APIs
DEFAULT_CONFIG = {
    # Alpaca configuration
    "alpaca": {
        "base_url": os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets"),
        "data_url": os.environ.get("ALPACA_DATA_URL", "https://data.alpaca.markets"),
        "api_version": "v2",
        "timeout": 30,  # seconds
        "max_retries": 3,
        "retry_delay": 2,  # seconds
        "rate_limits": {
            "account": {"calls": 5, "period": 60},  # 5 calls per minute
            "orders": {"calls": 10, "period": 60},  # 10 calls per minute
            "market_data": {"calls": 200, "period": 60},  # 200 calls per minute
        }
    },
    
    # OpenAI configuration
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "timeout": 60,  # seconds
        "max_retries": 2,
        "retry_delay": 5,  # seconds
        "rate_limits": {
            "default": {"calls": 20, "period": 60},  # 20 calls per minute
        }
    },
    
    # OpenRouter configuration
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "timeout": 60,  # seconds
        "max_retries": 2,
        "retry_delay": 5,  # seconds
        "rate_limits": {
            "default": {"calls": 10, "period": 60},  # 10 calls per minute
        }
    },
    
    # Hume AI configuration
    "hume": {
        "base_url": "https://api.hume.ai/v1",
        "timeout": 30,  # seconds
        "max_retries": 2,
        "retry_delay": 2,  # seconds
        "rate_limits": {
            "default": {"calls": 20, "period": 60},  # 20 calls per minute
        }
    },
    
    # TradingView configuration
    "tradingview": {
        "webhook_timeout": 5,  # seconds
        "rate_limits": {
            "default": {"calls": 60, "period": 60},  # 60 calls per minute
        }
    },
    
    # Unusual Whales configuration
    "unusual_whales": {
        "base_url": "https://unusualwhales.com/api/v1",
        "timeout": 30,  # seconds
        "max_retries": 3,
        "retry_delay": 2,  # seconds
        "rate_limits": {
            "default": {"calls": 5, "period": 60},  # 5 calls per minute
        }
    },
    
    # Default configuration for all APIs
    "default": {
        "timeout": 30,  # seconds
        "max_retries": 3,
        "retry_delay": 2,  # seconds
        "rate_limits": {
            "default": {"calls": 10, "period": 60},  # 10 calls per minute
        }
    }
}

# Custom environment overrides
ENV_OVERRIDES = {
    "development": {
        "alpaca": {
            "base_url": "https://paper-api.alpaca.markets",
        }
    },
    "production": {
        "alpaca": {
            # Use real account in production if needed
            "base_url": os.environ.get("ALPACA_BASE_URL", "https://api.alpaca.markets"),
        }
    },
    "testing": {
        "alpaca": {
            "base_url": "https://paper-api.alpaca.markets",
            "timeout": 5,  # Faster timeouts for testing
        },
        "openai": {
            "timeout": 10,
        }
    }
}

class APIConfig:
    """API configuration management."""
    
    def __init__(self, environment: str = None):
        """
        Initialize API configuration.
        
        Args:
            environment: Environment name (development, production, testing)
        """
        self.config = DEFAULT_CONFIG.copy()
        self.environment = environment or os.environ.get("APP_ENV", "development")
        
        # Apply environment-specific overrides
        self._apply_env_overrides()
        
        # Set up rate limiters
        from api.auth.rate_limiter import get_rate_limiter
        self._setup_rate_limits(get_rate_limiter())
        
    def _apply_env_overrides(self):
        """Apply environment-specific configuration overrides."""
        if self.environment in ENV_OVERRIDES:
            overrides = ENV_OVERRIDES[self.environment]
            for service, service_config in overrides.items():
                if service in self.config:
                    # Deep merge the configuration
                    self._deep_merge(self.config[service], service_config)
                else:
                    self.config[service] = service_config
        
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """
        Deep merge two dictionaries.
        
        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _setup_rate_limits(self, rate_limiter):
        """
        Set up rate limits from configuration.
        
        Args:
            rate_limiter: Rate limiter instance
        """
        for service, service_config in self.config.items():
            if "rate_limits" in service_config:
                for endpoint, limit in service_config["rate_limits"].items():
                    limiter_key = f"{service}:{endpoint}"
                    rate_limiter.set_limit(
                        limiter_key, 
                        limit["calls"], 
                        limit["period"]
                    )
    
    def get_config(self, service: str):
        """
        Get configuration for a specific service.
        
        Args:
            service: Service name
            
        Returns:
            Service configuration dict
        """
        return self.config.get(service, self.config["default"])
        
    def get_service_endpoint_key(self, service: str, endpoint: str = "default"):
        """
        Get the key used for rate limiting a specific service endpoint.
        
        Args:
            service: Service name
            endpoint: Endpoint name
            
        Returns:
            Rate limiting key string
        """
        return f"{service}:{endpoint}"

# Global instance for convenience
api_config = APIConfig()

def get_api_config() -> APIConfig:
    """Get the global API configuration instance."""
    return api_config 