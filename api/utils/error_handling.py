"""
Error Handling Utilities

Provides error handling mechanisms and custom exceptions for robust API operations.
Includes retry mechanisms, rate limiting handlers, and standardized error formatting.
"""

import functools
import logging
import time
import random
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast

# Configure logging
logger = logging.getLogger(__name__)

# Type variables for the decorator functions
F = TypeVar('F', bound=Callable[..., Any])
R = TypeVar('R')

# Base class for API errors
class ApiError(Exception):
    """Base exception for all API-related errors."""
    
    def __init__(self, message: str, code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary for API responses."""
        error_dict = {
            "error": self.message,
            "success": False
        }
        
        if self.code:
            error_dict["code"] = self.code
            
        if self.details:
            error_dict["details"] = self.details
            
        return error_dict
        
    def __str__(self) -> str:
        error_str = f"API Error: {self.message}"
        if self.code:
            error_str += f" (Code: {self.code})"
        if self.details:
            error_str += f" - Details: {self.details}"
        return error_str

# Authentication and authorization errors
class AuthenticationError(ApiError):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=401, details=details)

class AuthorizationError(ApiError):
    """Exception raised when user lacks permission to access a resource."""
    
    def __init__(self, message: str = "Not authorized to access this resource", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=403, details=details)

# Request/input validation errors
class ValidationError(ApiError):
    """Exception raised when request validation fails."""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=400, details=details)

# Resource errors
class ResourceNotFoundError(ApiError):
    """Exception raised when a requested resource does not exist."""
    
    def __init__(self, resource_type: str = "Resource", resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message=message, code=404, details=details)

class ResourceExistsError(ApiError):
    """Exception raised when trying to create a resource that already exists."""
    
    def __init__(self, resource_type: str = "Resource", resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = f"{resource_type} already exists"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message=message, code=409, details=details)

# Rate limiting
class RateLimitExceededError(ApiError):
    """Exception raised when API rate limit is exceeded."""
    
    def __init__(self, retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        message = "Rate limit exceeded"
        if retry_after:
            message += f", retry after {retry_after} seconds"
        details_dict = details or {}
        if retry_after:
            details_dict["retry_after"] = retry_after
        super().__init__(message=message, code=429, details=details_dict)

# External service errors
class ExternalServiceError(ApiError):
    """Exception raised when an external service fails."""
    
    def __init__(self, service_name: str, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        full_message = f"{service_name} service error: {message}"
        super().__init__(message=full_message, code=502, details=details)

# General errors
class ConfigurationError(ApiError):
    """Exception raised when there is a configuration error."""
    
    def __init__(self, message: str = "Configuration error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=500, details=details)

class DatabaseError(ApiError):
    """Exception raised when there is a database error."""
    
    def __init__(self, message: str = "Database error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=500, details=details)

class TimeoutError(ApiError):
    """Exception raised when a request times out."""
    
    def __init__(self, operation: str = "Operation", details: Optional[Dict[str, Any]] = None):
        message = f"{operation} timed out"
        super().__init__(message=message, code=408, details=details)

# Retry decorators
def retry_with_backoff(
    max_retries: int = 3,
    initial_backoff: float = 1.0,
    max_backoff: float = 30.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions: Optional[List[Type[Exception]]] = None
) -> Callable[[F], F]:
    """
    Retry a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries.
        initial_backoff: Initial backoff time in seconds.
        max_backoff: Maximum backoff time in seconds.
        backoff_factor: Backoff factor for exponential backoff.
        jitter: Whether to add jitter to the backoff time.
        exceptions: List of exceptions to catch and retry. Default is [Exception].
        
    Returns:
        Decorated function.
    """
    if exceptions is None:
        exceptions = [Exception]
        
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retry_count = 0
            retry_exceptions = tuple(exceptions)  # type: ignore
            backoff = initial_backoff
            
            while True:
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:
                    retry_count += 1
                    
                    # Don't retry certain exceptions
                    if isinstance(e, (AuthorizationError, ValidationError, ResourceNotFoundError, ResourceExistsError)):
                        logger.warning(f"Not retrying on exception: {str(e)}")
                        raise
                    
                    # Check if we've reached the max retries
                    if retry_count > max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}: {str(e)}")
                        raise
                    
                    # Calculate backoff with jitter
                    if jitter:
                        sleep_time = min(max_backoff, backoff * (1 + random.uniform(-0.1, 0.1)))
                    else:
                        sleep_time = min(max_backoff, backoff)
                    
                    logger.warning(
                        f"Retry {retry_count}/{max_retries} for {func.__name__} after exception: "
                        f"{type(e).__name__}: {str(e)}. Sleeping for {sleep_time:.2f}s"
                    )
                    
                    time.sleep(sleep_time)
                    
                    # Increase backoff for next iteration
                    backoff = min(max_backoff, backoff * backoff_factor)
                    
        return cast(F, wrapper)
    return decorator

def retry_on_rate_limit(
    max_retries: int = 5,
    initial_backoff: float = 2.0,
    max_backoff: float = 120.0
) -> Callable[[F], F]:
    """
    Retry a function specifically when hitting rate limits.
    
    Args:
        max_retries: Maximum number of retries.
        initial_backoff: Initial backoff time in seconds.
        max_backoff: Maximum backoff time in seconds.
        
    Returns:
        Decorated function.
    """
    return retry_with_backoff(
        max_retries=max_retries,
        initial_backoff=initial_backoff,
        max_backoff=max_backoff,
        backoff_factor=2.0,
        jitter=True,
        exceptions=[RateLimitExceededError]
    )

def handle_api_errors(func: F) -> F:
    """
    Decorator to standardize API error handling.
    
    Converts various exceptions to ApiError instances with appropriate
    status codes and formats the error response consistently.
    
    Args:
        func: The function to decorate.
        
    Returns:
        Decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ApiError:
            # Already an ApiError, re-raise
            raise
        except ValueError as e:
            # Convert ValueError to ValidationError
            logger.warning(f"ValueError in {func.__name__}: {str(e)}")
            raise ValidationError(message=str(e))
        except KeyError as e:
            # Missing required key
            logger.warning(f"KeyError in {func.__name__}: {str(e)}")
            raise ValidationError(message=f"Missing required field: {str(e)}")
        except TimeoutError as e:
            # Request timeout
            logger.warning(f"Timeout in {func.__name__}: {str(e)}")
            raise TimeoutError(operation=func.__name__)
        except Exception as e:
            # Unexpected error, log and convert to ApiError
            logger.error(f"Unexpected error in {func.__name__}: {type(e).__name__}: {str(e)}", exc_info=True)
            raise ApiError(message=f"An unexpected error occurred: {str(e)}")
    
    return cast(F, wrapper)

def with_error_response(func: F) -> F:
    """
    Decorator that catches ApiError exceptions and returns standardized error responses.
    
    Use this on Flask route handlers to standardize error responses.
    
    Args:
        func: The function to decorate.
        
    Returns:
        Decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ApiError as e:
            # Get the error dictionary
            error_response = e.to_dict()
            
            # Log the error
            logger.error(f"API Error in {func.__name__}: {str(e)}")
            
            # Return the error response with the appropriate status code
            from flask import jsonify
            status_code = e.code if e.code else 500
            return jsonify(error_response), status_code
    
    return cast(F, wrapper)

def create_error_response(error: Union[ApiError, str, Exception], status_code: int = 400) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.
    
    Args:
        error: The error object or message.
        status_code: HTTP status code to use if the error doesn't specify one.
        
    Returns:
        Error response dictionary.
    """
    if isinstance(error, ApiError):
        response = error.to_dict()
    elif isinstance(error, Exception):
        response = {
            "error": str(error),
            "success": False,
            "code": status_code
        }
    else:
        response = {
            "error": error,
            "success": False,
            "code": status_code
        }
    
    return response 