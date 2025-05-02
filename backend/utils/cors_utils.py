"""
CORS utility functions for API routes.
These functions help handle Cross-Origin Resource Sharing (CORS) headers
across the application's API endpoints.
"""
from flask import Response


def add_cors_headers(response: Response) -> Response:
    """Add CORS headers to a Flask response.
    
    Args:
        response: Flask Response object to add headers to
        
    Returns:
        Response object with CORS headers
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response 