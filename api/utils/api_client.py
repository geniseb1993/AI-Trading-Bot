"""
API Client

A robust API client system with rate limiting, retry logic, and comprehensive error handling.
Supports multiple authentication methods and configurable request parameters.
"""

import json
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import httpx
from httpx import Response

from api.utils.credentials_manager import get_credentials_manager

# Configure logging
logger = logging.getLogger(__name__)

class ApiError(Exception):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Response] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)

class RateLimitError(ApiError):
    """Exception raised when API rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[float] = None, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, **kwargs)

class AuthenticationError(ApiError):
    """Exception raised when API authentication fails."""
    pass

class ConnectionError(ApiError):
    """Exception raised when API connection fails."""
    pass

class TimeoutError(ApiError):
    """Exception raised when API request times out."""
    pass

class ServerError(ApiError):
    """Exception raised when API server returns an error."""
    pass

class ClientError(ApiError):
    """Exception raised when API client makes an invalid request."""
    pass

class AuthType(Enum):
    """Supported authentication types."""
    NONE = "none"
    API_KEY = "api_key"
    OAUTH = "oauth"
    BEARER = "bearer"
    BASIC = "basic"
    CUSTOM = "custom"

class RateLimiter:
    """
    Rate limiter for API requests.
    
    Implements token bucket algorithm with configurable refill rate and capacity.
    """
    
    def __init__(self, 
        requests_per_second: float = 1.0,
        burst_capacity: int = 5
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Maximum number of requests per second.
            burst_capacity: Maximum burst capacity.
        """
        self.requests_per_second = requests_per_second
        self.burst_capacity = burst_capacity
        self.tokens = burst_capacity
        self.last_refill_time = time.time()
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill_time
        new_tokens = elapsed * self.requests_per_second
        
        if new_tokens > 0:
            self.tokens = min(self.burst_capacity, self.tokens + new_tokens)
            self.last_refill_time = now
    
    def consume(self, tokens: int = 1) -> float:
        """
        Consume tokens for a request.
        
        Args:
            tokens: Number of tokens to consume.
            
        Returns:
            Wait time in seconds if rate limit exceeded, 0 otherwise.
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return 0
        
        # Calculate time to wait until enough tokens are available
        needed_tokens = tokens - self.tokens
        wait_time = needed_tokens / self.requests_per_second
        
        return wait_time

class ApiClient:
    """
    Robust API client with rate limiting and error handling.
    
    Features:
    - Multiple authentication methods
    - Configurable rate limiting
    - Automatic retries with exponential backoff
    - Comprehensive error handling
    - Request and response logging
    - Support for various HTTP methods
    """
    
    def __init__(self,
        base_url: str,
        service_name: str,
        auth_type: AuthType = AuthType.NONE,
        rate_limit: Optional[RateLimiter] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_codes: Optional[List[int]] = None,
        retry_statuses: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_header: str = "Authorization",
        api_key_param: str = "api_key",
        custom_auth: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        verify_ssl: bool = True,
        debug: bool = False
    ):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API requests.
            service_name: Service name for credentials lookup.
            auth_type: Authentication type.
            rate_limit: Rate limiter instance. Default is 1 request per second with 5 burst capacity.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
            retry_codes: HTTP status codes to retry. Default is [429, 500, 502, 503, 504].
            retry_statuses: API-specific status values to retry.
            headers: Additional headers to include in all requests.
            auth_header: Header name for authentication.
            api_key_param: Parameter name for API key.
            custom_auth: Custom authentication function.
            verify_ssl: Whether to verify SSL certificates.
            debug: Whether to enable debug logging.
        """
        self.base_url = base_url.rstrip('/')
        self.service_name = service_name
        self.auth_type = auth_type
        self.rate_limit = rate_limit or RateLimiter()
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_codes = retry_codes or [429, 500, 502, 503, 504]
        self.retry_statuses = retry_statuses or []
        self.headers = headers or {}
        self.auth_header = auth_header
        self.api_key_param = api_key_param
        self.custom_auth = custom_auth
        self.verify_ssl = verify_ssl
        self.debug = debug
        
        # Configure client
        self.client = httpx.Client(
            timeout=timeout,
            verify=verify_ssl,
            headers=self.headers
        )
        
        # Get credentials manager
        self.credentials_manager = get_credentials_manager()
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'client') and self.client:
            self.client.close()
    
    def _apply_auth(self, 
        request_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply authentication to request.
        
        Args:
            request_kwargs: Request arguments.
            
        Returns:
            Updated request arguments with authentication.
            
        Raises:
            AuthenticationError: If authentication fails.
        """
        if self.auth_type == AuthType.NONE:
            return request_kwargs
        
        try:
            if self.auth_type == AuthType.API_KEY:
                api_key = self.credentials_manager.get(self.service_name, "api_key")
                
                # Check if API key should be in query parameters or headers
                if request_kwargs.get("params") is None:
                    request_kwargs["params"] = {}
                
                request_kwargs["params"][self.api_key_param] = api_key
                
            elif self.auth_type == AuthType.BEARER:
                token = self.credentials_manager.get(self.service_name, "token")
                
                if request_kwargs.get("headers") is None:
                    request_kwargs["headers"] = {}
                
                request_kwargs["headers"][self.auth_header] = f"Bearer {token}"
                
            elif self.auth_type == AuthType.BASIC:
                username = self.credentials_manager.get(self.service_name, "username")
                password = self.credentials_manager.get(self.service_name, "password")
                
                request_kwargs["auth"] = (username, password)
                
            elif self.auth_type == AuthType.OAUTH:
                token = self.credentials_manager.get(self.service_name, "token")
                
                if request_kwargs.get("headers") is None:
                    request_kwargs["headers"] = {}
                
                request_kwargs["headers"][self.auth_header] = f"Bearer {token}"
                
            elif self.auth_type == AuthType.CUSTOM and self.custom_auth:
                # Get all credentials for the service
                credentials = self.credentials_manager.get_service(self.service_name)
                
                # Apply custom authentication
                request_kwargs = self.custom_auth(credentials, request_kwargs)
            
            return request_kwargs
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    def _handle_response(self, 
        response: Response
    ) -> Dict[str, Any]:
        """
        Handle API response.
        
        Args:
            response: API response.
            
        Returns:
            Parsed response data.
            
        Raises:
            ClientError: If client error (4xx).
            ServerError: If server error (5xx).
            ApiError: If other error.
        """
        if self.debug:
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            try:
                logger.debug(f"Response body: {response.text[:1000]}...")
            except Exception:
                pass
        
        # Check for success
        if 200 <= response.status_code < 300:
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    return response.json()
                
                return {"status": "success", "data": response.text}
            except json.JSONDecodeError:
                return {"status": "success", "data": response.text}
        
        # Handle rate limiting
        if response.status_code == 429:
            retry_after = None
            
            # Try to get retry-after header
            if "Retry-After" in response.headers:
                try:
                    retry_after = float(response.headers["Retry-After"])
                except ValueError:
                    # Try to parse date
                    try:
                        retry_date = datetime.strptime(response.headers["Retry-After"], "%a, %d %b %Y %H:%M:%S %Z")
                        retry_after = (retry_date - datetime.now()).total_seconds()
                    except ValueError:
                        pass
            
            raise RateLimitError("Rate limit exceeded", retry_after=retry_after, status_code=429, response=response)
        
        # Handle client errors
        if 400 <= response.status_code < 500:
            error_message = f"Client error: {response.status_code}"
            
            try:
                error_data = response.json()
                if isinstance(error_data, dict):
                    error_message = error_data.get("error", error_message)
            except Exception:
                error_message = response.text or error_message
            
            raise ClientError(error_message, status_code=response.status_code, response=response)
        
        # Handle server errors
        if 500 <= response.status_code < 600:
            error_message = f"Server error: {response.status_code}"
            
            try:
                error_data = response.json()
                if isinstance(error_data, dict):
                    error_message = error_data.get("error", error_message)
            except Exception:
                error_message = response.text or error_message
            
            raise ServerError(error_message, status_code=response.status_code, response=response)
        
        # Handle other errors
        raise ApiError(f"Unexpected status code: {response.status_code}", status_code=response.status_code, response=response)
    
    async def _retry_request(self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Retry request with exponential backoff.
        
        Args:
            method: HTTP method.
            endpoint: API endpoint.
            **kwargs: Additional request arguments.
            
        Returns:
            Parsed response data.
            
        Raises:
            ApiError: If all retries fail.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_kwargs = kwargs.copy()
        
        # Apply authentication
        request_kwargs = self._apply_auth(request_kwargs)
        
        if self.debug:
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Request method: {method}")
            logger.debug(f"Request kwargs: {request_kwargs}")
        
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                # Apply rate limiting
                wait_time = self.rate_limit.consume()
                if wait_time > 0:
                    logger.warning(f"Rate limit exceeded, waiting {wait_time:.2f} seconds")
                    time.sleep(wait_time)
                
                # Execute request
                response = self.client.request(method, url, **request_kwargs)
                
                # Handle response
                return self._handle_response(response)
                
            except RateLimitError as e:
                # Wait for retry-after time
                wait_time = e.retry_after or (2 ** retries)
                logger.warning(f"Rate limit exceeded, waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
                last_error = e
                
            except (ServerError, ConnectionError, TimeoutError) as e:
                # Retry with exponential backoff
                wait_time = 2 ** retries
                logger.warning(f"Request failed, retrying in {wait_time:.2f} seconds: {str(e)}")
                time.sleep(wait_time)
                last_error = e
                
            except Exception as e:
                # Don't retry other errors
                raise
                
            retries += 1
        
        # All retries failed
        if last_error:
            raise last_error
        
        raise ApiError(f"All retries failed for {method} {endpoint}")
    
    def request(self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method.
            endpoint: API endpoint.
            **kwargs: Additional request arguments.
            
        Returns:
            Parsed response data.
            
        Raises:
            ApiError: If request fails.
        """
        try:
            return self._retry_request(method, endpoint, **kwargs)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {str(e)}")
        except httpx.ConnectError as e:
            raise ConnectionError(f"Connection error: {str(e)}")
        except httpx.HTTPError as e:
            raise ApiError(f"HTTP error: {str(e)}")
        except Exception as e:
            if isinstance(e, ApiError):
                raise
            raise ApiError(f"Request failed: {str(e)}")
    
    def get(self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a GET request.
        
        Args:
            endpoint: API endpoint.
            params: Query parameters.
            **kwargs: Additional request arguments.
            
        Returns:
            Parsed response data.
        """
        kwargs["params"] = params or {}
        return self.request("GET", endpoint, **kwargs)
    
    def post(self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a POST request.
        
        Args:
            endpoint: API endpoint.
            json_data: JSON data.
            data: Form data.
            **kwargs: Additional request arguments.
            
        Returns:
            Parsed response data.
        """
        if json_data is not None:
            kwargs["json"] = json_data
        if data is not None:
            kwargs["data"] = data
        return self.request("POST", endpoint, **kwargs)
    
    def put(self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a PUT request.
        
        Args:
            endpoint: API endpoint.
            json_data: JSON data.
            data: Form data.
            **kwargs: Additional request arguments.
            
        Returns:
            Parsed response data.
        """
        if json_data is not None:
            kwargs["json"] = json_data
        if data is not None:
            kwargs["data"] = data
        return self.request("PUT", endpoint, **kwargs)
    
    def patch(self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a PATCH request.
        
        Args:
            endpoint: API endpoint.
            json_data: JSON data.
            data: Form data.
            **kwargs: Additional request arguments.
            
        Returns:
            Parsed response data.
        """
        if json_data is not None:
            kwargs["json"] = json_data
        if data is not None:
            kwargs["data"] = data
        return self.request("PATCH", endpoint, **kwargs)
    
    def delete(self,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a DELETE request.
        
        Args:
            endpoint: API endpoint.
            **kwargs: Additional request arguments.
            
        Returns:
            Parsed response data.
        """
        return self.request("DELETE", endpoint, **kwargs)

# Factory function to create API client instances
def create_api_client(
    base_url: str,
    service_name: str,
    auth_type: Union[AuthType, str] = AuthType.NONE,
    rate_limit: Optional[RateLimiter] = None,
    **kwargs
) -> ApiClient:
    """
    Create an API client instance.
    
    Args:
        base_url: Base URL for API requests.
        service_name: Service name for credentials lookup.
        auth_type: Authentication type (can be string or AuthType enum).
        rate_limit: Rate limiter instance.
        **kwargs: Additional client arguments.
        
    Returns:
        ApiClient instance.
    """
    # Convert string auth_type to enum
    if isinstance(auth_type, str):
        try:
            auth_type = AuthType(auth_type)
        except ValueError:
            auth_type = AuthType.NONE
    
    return ApiClient(
        base_url=base_url,
        service_name=service_name,
        auth_type=auth_type,
        rate_limit=rate_limit,
        **kwargs
    ) 