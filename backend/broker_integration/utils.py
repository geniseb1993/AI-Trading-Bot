"""
Utility functions for broker integration.
Contains helper functions and shared utilities for broker implementations.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)

# Constants
BROKER_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CACHED_DATA_DIR = os.path.join(BROKER_DATA_DIR, "cached")
STATE_DATA_DIR = os.path.join(BROKER_DATA_DIR, "state")
LOG_DATA_DIR = os.path.join(BROKER_DATA_DIR, "logs")

# Ensure data directories exist
for directory in [BROKER_DATA_DIR, CACHED_DATA_DIR, STATE_DATA_DIR, LOG_DATA_DIR]:
    os.makedirs(directory, exist_ok=True)

def format_iso_date(dt: Optional[datetime] = None) -> str:
    """
    Format a datetime as ISO 8601 string.
    
    Args:
        dt: Datetime to format. If None, uses current datetime.
        
    Returns:
        ISO 8601 formatted string
    """
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()

def parse_iso_date(date_str: str) -> datetime:
    """
    Parse an ISO 8601 string into a datetime.
    
    Args:
        date_str: ISO 8601 formatted date string
        
    Returns:
        Datetime object
    """
    return datetime.fromisoformat(date_str)

def calculate_order_value(price: float, quantity: float) -> float:
    """
    Calculate the value of an order.
    
    Args:
        price: Price per unit
        quantity: Number of units
        
    Returns:
        Total order value
    """
    return price * quantity

def save_to_cache(data: Any, cache_key: str, subdir: Optional[str] = None) -> bool:
    """
    Save data to the cache.
    
    Args:
        data: Data to cache (must be JSON serializable)
        cache_key: Unique key for the cached data
        subdir: Optional subdirectory within the cache directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    cache_dir = CACHED_DATA_DIR
    if subdir:
        cache_dir = os.path.join(cache_dir, subdir)
        os.makedirs(cache_dir, exist_ok=True)
        
    cache_path = os.path.join(cache_dir, f"{cache_key}.json")
    
    try:
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Saved data to cache: {cache_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving to cache: {str(e)}")
        return False

def load_from_cache(cache_key: str, subdir: Optional[str] = None, max_age_seconds: Optional[int] = None) -> Optional[Any]:
    """
    Load data from the cache.
    
    Args:
        cache_key: Unique key for the cached data
        subdir: Optional subdirectory within the cache directory
        max_age_seconds: Maximum age of cache in seconds. If older, returns None.
        
    Returns:
        Cached data or None if not found or expired
    """
    cache_dir = CACHED_DATA_DIR
    if subdir:
        cache_dir = os.path.join(cache_dir, subdir)
        
    cache_path = os.path.join(cache_dir, f"{cache_key}.json")
    
    if not os.path.exists(cache_path):
        logger.debug(f"Cache miss: {cache_path}")
        return None
        
    # Check if cache is expired
    if max_age_seconds is not None:
        file_age = datetime.now().timestamp() - os.path.getmtime(cache_path)
        if file_age > max_age_seconds:
            logger.debug(f"Cache expired: {cache_path} (age: {file_age:.1f}s, max: {max_age_seconds}s)")
            return None
    
    try:
        with open(cache_path, 'r') as f:
            data = json.load(f)
        logger.debug(f"Loaded data from cache: {cache_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading from cache: {str(e)}")
        return None

def save_broker_state(broker_name: str, state: Dict[str, Any]) -> bool:
    """
    Save broker state for recovery.
    
    Args:
        broker_name: Name of the broker
        state: Dictionary containing broker state
        
    Returns:
        bool: True if successful, False otherwise
    """
    state_file = os.path.join(STATE_DATA_DIR, f"{broker_name}_state.json")
    
    try:
        # Add timestamp
        state['saved_at'] = format_iso_date()
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        logger.debug(f"Saved broker state: {state_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving broker state: {str(e)}")
        return False

def load_broker_state(broker_name: str) -> Optional[Dict[str, Any]]:
    """
    Load broker state for recovery.
    
    Args:
        broker_name: Name of the broker
        
    Returns:
        Dictionary containing broker state or None if not found
    """
    state_file = os.path.join(STATE_DATA_DIR, f"{broker_name}_state.json")
    
    if not os.path.exists(state_file):
        logger.debug(f"No saved state found for broker: {broker_name}")
        return None
    
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        logger.debug(f"Loaded broker state: {state_file}")
        return state
    except Exception as e:
        logger.error(f"Error loading broker state: {str(e)}")
        return None

def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize a symbol.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Normalized symbol (uppercase, no whitespace)
        
    Raises:
        ValueError: If symbol is invalid
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty")
        
    # Normalize
    normalized = symbol.strip().upper()
    
    # Basic validation
    if not normalized or len(normalized) > 10:
        raise ValueError(f"Invalid symbol: {symbol}")
        
    return normalized

def validate_quantity(quantity: float) -> float:
    """
    Validate order quantity.
    
    Args:
        quantity: Order quantity
        
    Returns:
        Validated quantity
        
    Raises:
        ValueError: If quantity is invalid
    """
    if not isinstance(quantity, (int, float)):
        raise ValueError(f"Quantity must be a number, got {type(quantity)}")
        
    if quantity <= 0:
        raise ValueError(f"Quantity must be positive, got {quantity}")
        
    return float(quantity)

def validate_price(price: Optional[float]) -> Optional[float]:
    """
    Validate price value.
    
    Args:
        price: Price value or None
        
    Returns:
        Validated price or None
        
    Raises:
        ValueError: If price is invalid
    """
    if price is None:
        return None
        
    if not isinstance(price, (int, float)):
        raise ValueError(f"Price must be a number, got {type(price)}")
        
    if price <= 0:
        raise ValueError(f"Price must be positive, got {price}")
        
    return float(price)

def log_order(broker_name: str, order: Dict[str, Any]) -> None:
    """
    Log an order to the broker-specific log file.
    
    Args:
        broker_name: Name of the broker
        order: Order dictionary
    """
    log_file = os.path.join(LOG_DATA_DIR, f"{broker_name}_orders.jsonl")
    
    try:
        # Add log timestamp
        log_entry = {
            "log_timestamp": format_iso_date(),
            "order": order
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        logger.error(f"Error logging order: {str(e)}")

def extract_nested_value(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Extract a value from a nested dictionary using a dot-separated path.
    
    Args:
        data: Dictionary to extract from
        key_path: Dot-separated path to the value (e.g., 'account.balance.cash')
        default: Default value if key is not found
        
    Returns:
        Extracted value or default if not found
    """
    keys = key_path.split('.')
    value = data
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default 