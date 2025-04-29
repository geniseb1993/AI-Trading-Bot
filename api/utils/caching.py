"""
Caching Utilities

Provides caching mechanisms for API responses and data storage.
Includes memory-based and file-based caching strategies with TTL support.
"""

import functools
import json
import logging
import os
import pickle
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union, cast

# Configure logging
logger = logging.getLogger(__name__)

# Type variables for the decorator functions
F = TypeVar('F', bound=Callable[..., Any])
R = TypeVar('R')

class CacheItem:
    """Class representing a cached item with TTL."""
    
    def __init__(self, value: Any, ttl: int = 3600):
        """
        Initialize a cache item.
        
        Args:
            value: The value to cache.
            ttl: Time to live in seconds. Default is 1 hour.
        """
        self.value = value
        self.timestamp = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if the cache item is expired."""
        return time.time() > self.timestamp + self.ttl
    
    def time_remaining(self) -> float:
        """Get the remaining time until expiration in seconds."""
        return max(0, (self.timestamp + self.ttl) - time.time())
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert the cache item to a dictionary."""
        return {
            "value": self.value,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "expires_at": self.timestamp + self.ttl,
            "is_expired": self.is_expired(),
            "time_remaining": self.time_remaining()
        }

class MemoryCache:
    """In-memory cache with TTL support."""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        """Create a singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MemoryCache, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the cache."""
        with self._lock:
            if not getattr(self, "_initialized", False):
                self._cache: Dict[str, CacheItem] = {}
                self._stats: Dict[str, int] = {
                    "hits": 0,
                    "misses": 0,
                    "evictions": 0,
                    "sets": 0
                }
                self._initialized = True
    
    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            Tuple containing (hit, value). If hit is False, value is None.
        """
        with self._lock:
            if key in self._cache:
                cache_item = self._cache[key]
                if cache_item.is_expired():
                    self._stats["evictions"] += 1
                    del self._cache[key]
                    self._stats["misses"] += 1
                    return False, None
                else:
                    self._stats["hits"] += 1
                    return True, cache_item.value
            else:
                self._stats["misses"] += 1
                return False, None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Time to live in seconds. Default is 1 hour.
        """
        with self._lock:
            self._cache[key] = CacheItem(value, ttl)
            self._stats["sets"] += 1
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            True if the key was deleted, False otherwise.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        with self._lock:
            self._cache.clear()
    
    def clear_expired(self) -> int:
        """
        Clear all expired items from the cache.
        
        Returns:
            Number of items cleared.
        """
        with self._lock:
            expired_keys = [
                key for key, item in self._cache.items() if item.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            self._stats["evictions"] += len(expired_keys)
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self._lock:
            stats = self._stats.copy()
            stats["size"] = len(self._cache)
            stats["unexpired_size"] = sum(
                1 for item in self._cache.values() if not item.is_expired()
            )
            return stats
    
    def get_keys(self) -> List[str]:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())
    
    def get_items(self) -> Dict[str, Dict[str, Any]]:
        """Get all cache items as dictionaries."""
        with self._lock:
            return {key: item.as_dict() for key, item in self._cache.items()}

class FileCache:
    """File-based cache with TTL support."""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls, cache_dir: Optional[str] = None):
        """Create a singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(FileCache, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory to store cache files. Default is './data/cache'.
        """
        with self._lock:
            if not getattr(self, "_initialized", False):
                self._cache_dir = cache_dir or os.path.join("data", "cache")
                
                # Create cache directory if it doesn't exist
                os.makedirs(self._cache_dir, exist_ok=True)
                
                self._stats: Dict[str, int] = {
                    "hits": 0,
                    "misses": 0,
                    "evictions": 0,
                    "sets": 0
                }
                self._initialized = True
    
    def _get_cache_path(self, key: str) -> str:
        """
        Get the file path for a cache key.
        
        Args:
            key: The cache key.
            
        Returns:
            File path for the cache key.
        """
        # Create a safe filename from the key
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return os.path.join(self._cache_dir, f"{safe_key}.cache")
    
    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            Tuple containing (hit, value). If hit is False, value is None.
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            self._stats["misses"] += 1
            return False, None
        
        try:
            with open(cache_path, "rb") as f:
                cache_item = pickle.load(f)
                
            if cache_item.is_expired():
                self._stats["evictions"] += 1
                os.remove(cache_path)
                self._stats["misses"] += 1
                return False, None
            else:
                self._stats["hits"] += 1
                return True, cache_item.value
        except Exception as e:
            logger.warning(f"Error reading cache file {cache_path}: {str(e)}")
            self._stats["misses"] += 1
            
            # Remove corrupted cache file
            try:
                os.remove(cache_path)
            except:
                pass
                
            return False, None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Time to live in seconds. Default is 1 hour.
        """
        cache_path = self._get_cache_path(key)
        cache_item = CacheItem(value, ttl)
        
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(cache_item, f)
            self._stats["sets"] += 1
        except Exception as e:
            logger.warning(f"Error writing cache file {cache_path}: {str(e)}")
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            True if the key was deleted, False otherwise.
        """
        cache_path = self._get_cache_path(key)
        
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                return True
            except Exception as e:
                logger.warning(f"Error deleting cache file {cache_path}: {str(e)}")
                return False
        return False
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        try:
            for filename in os.listdir(self._cache_dir):
                if filename.endswith(".cache"):
                    os.remove(os.path.join(self._cache_dir, filename))
        except Exception as e:
            logger.warning(f"Error clearing cache directory {self._cache_dir}: {str(e)}")
    
    def clear_expired(self) -> int:
        """
        Clear all expired items from the cache.
        
        Returns:
            Number of items cleared.
        """
        cleared_count = 0
        
        try:
            for filename in os.listdir(self._cache_dir):
                if filename.endswith(".cache"):
                    cache_path = os.path.join(self._cache_dir, filename)
                    
                    try:
                        with open(cache_path, "rb") as f:
                            cache_item = pickle.load(f)
                            
                        if cache_item.is_expired():
                            os.remove(cache_path)
                            cleared_count += 1
                            self._stats["evictions"] += 1
                    except Exception as e:
                        logger.warning(f"Error processing cache file {cache_path}: {str(e)}")
                        
                        # Remove corrupted cache file
                        try:
                            os.remove(cache_path)
                            cleared_count += 1
                        except:
                            pass
        except Exception as e:
            logger.warning(f"Error clearing expired cache items: {str(e)}")
        
        return cleared_count
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        stats = self._stats.copy()
        
        try:
            stats["size"] = sum(1 for f in os.listdir(self._cache_dir) if f.endswith(".cache"))
        except Exception as e:
            logger.warning(f"Error getting cache size: {str(e)}")
            stats["size"] = -1
        
        return stats

def cached(
    cache_instance: Optional[Union[MemoryCache, FileCache]] = None,
    ttl: int = 3600,
    key_prefix: str = "",
    use_first_arg_as_key: bool = False
) -> Callable[[F], F]:
    """
    Decorator for caching function results.
    
    Args:
        cache_instance: Cache instance to use. Default is a new MemoryCache.
        ttl: Time to live in seconds. Default is 1 hour.
        key_prefix: Prefix for cache keys.
        use_first_arg_as_key: Use the first argument as part of the cache key.
        
    Returns:
        Decorated function.
    """
    cache = cache_instance or MemoryCache()
    
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            if use_first_arg_as_key and args:
                key = f"{key_prefix}{func.__name__}_{args[0]}"
            else:
                key = f"{key_prefix}{func.__name__}"
                
                # Add args and kwargs to cache key if not already included
                if args:
                    key += f"_{hash(args)}"
                if kwargs:
                    key += f"_{hash(frozenset(kwargs.items()))}"
            
            # Try to get from cache
            hit, value = cache.get(key)
            
            if hit:
                return value
            
            # Call function if cache miss
            result = func(*args, **kwargs)
            
            # Cache the result
            cache.set(key, result, ttl)
            
            return result
        
        return cast(F, wrapper)
    
    return decorator

# Convenience function to create/get memory cache
def get_memory_cache() -> MemoryCache:
    """Get the singleton memory cache instance."""
    return MemoryCache()

# Convenience function to create/get file cache
def get_file_cache(cache_dir: Optional[str] = None) -> FileCache:
    """
    Get the singleton file cache instance.
    
    Args:
        cache_dir: Directory to store cache files. Default is './data/cache'.
        
    Returns:
        FileCache instance.
    """
    return FileCache(cache_dir)

# Cache key generation helpers
def generate_cache_key(
    prefix: str, 
    *args: Any, 
    **kwargs: Any
) -> str:
    """
    Generate a cache key from arguments.
    
    Args:
        prefix: Key prefix.
        *args: Positional arguments to include in the key.
        **kwargs: Keyword arguments to include in the key.
        
    Returns:
        Cache key string.
    """
    key_parts = [prefix]
    
    # Add args to key
    if args:
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            elif arg is None:
                key_parts.append("None")
            else:
                # For complex objects, use hash of string representation
                key_parts.append(str(hash(str(arg))))
    
    # Add kwargs to key
    if kwargs:
        # Sort to ensure consistent key generation
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}={v}")
            elif v is None:
                key_parts.append(f"{k}=None")
            else:
                # For complex objects, use hash of string representation
                key_parts.append(f"{k}={hash(str(v))}")
    
    return "_".join(key_parts) 