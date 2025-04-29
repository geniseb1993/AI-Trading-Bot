"""
API Rate Limiter

Provides rate limiting capabilities to prevent API abuse and ensure
we stay within usage limits of external APIs.
"""

import time
import logging
from typing import Dict, Optional, Callable, Any
from threading import Lock
from datetime import datetime, timedelta
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting for API calls to prevent exceeding limits."""
    
    def __init__(self):
        """Initialize the rate limiter."""
        self.limits = {}  # Service-specific rate limits
        self.usage = {}   # Track API usage
        self.lock = Lock()  # For thread safety
    
    def set_limit(self, service: str, calls: int, period: int):
        """
        Set rate limit for a service.
        
        Args:
            service: Service identifier
            calls: Maximum number of calls allowed
            period: Time period in seconds
        """
        with self.lock:
            self.limits[service] = {"calls": calls, "period": period}
            if service not in self.usage:
                self.usage[service] = []
    
    def check_limit(self, service: str) -> bool:
        """
        Check if a service is within its rate limit.
        
        Args:
            service: Service identifier
        
        Returns:
            True if within limit, False otherwise
        """
        with self.lock:
            # If no limit is set, allow the call
            if service not in self.limits:
                return True
            
            # Initialize usage tracking if needed
            if service not in self.usage:
                self.usage[service] = []
            
            # Get the limit details
            limit = self.limits[service]
            calls = limit["calls"]
            period = limit["period"]
            
            # Clean up old timestamps
            current_time = time.time()
            cutoff = current_time - period
            self.usage[service] = [t for t in self.usage[service] if t > cutoff]
            
            # Check if we're within the limit
            return len(self.usage[service]) < calls
    
    def record_call(self, service: str):
        """
        Record an API call for rate limiting purposes.
        
        Args:
            service: Service identifier
        """
        with self.lock:
            if service not in self.usage:
                self.usage[service] = []
            
            self.usage[service].append(time.time())
    
    def get_wait_time(self, service: str) -> float:
        """
        Get the time to wait before the next allowed call.
        
        Args:
            service: Service identifier
        
        Returns:
            Wait time in seconds, or 0 if no wait is needed
        """
        with self.lock:
            # If no limit is set or within limit, no wait needed
            if service not in self.limits or self.check_limit(service):
                return 0
            
            # Calculate wait time
            limit = self.limits[service]
            period = limit["period"]
            oldest_call = min(self.usage[service])
            current_time = time.time()
            
            return max(0, oldest_call + period - current_time)

# Global instance
rate_limiter = RateLimiter()

def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return rate_limiter

def rate_limited(service: str, retry: bool = True, max_retries: int = 3):
    """
    Decorator for rate-limited API calls.
    
    Args:
        service: Service identifier for rate limiting
        retry: Whether to retry if rate limit is exceeded
        max_retries: Maximum number of retries
    
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter = get_rate_limiter()
            retries = 0
            
            while retries <= max_retries:
                if limiter.check_limit(service):
                    # Within rate limit, make the call
                    limiter.record_call(service)
                    return func(*args, **kwargs)
                
                # Rate limit exceeded
                wait_time = limiter.get_wait_time(service)
                
                if not retry or retries >= max_retries:
                    logger.warning(f"Rate limit exceeded for {service}. Retry in {wait_time:.2f}s")
                    raise RateLimitExceeded(service, wait_time)
                
                # Wait and retry
                logger.info(f"Rate limit hit for {service}, waiting {wait_time:.2f}s (retry {retries+1}/{max_retries})")
                time.sleep(wait_time)
                retries += 1
            
            # Should not reach here, but just in case
            raise RateLimitExceeded(service, limiter.get_wait_time(service))
        
        return wrapper
    
    return decorator

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, service: str, wait_time: float):
        self.service = service
        self.wait_time = wait_time
        super().__init__(f"Rate limit exceeded for {service}. Try again in {wait_time:.2f}s") 