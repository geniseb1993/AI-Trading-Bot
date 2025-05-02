#!/usr/bin/env python3
"""
Failsafe Frontend Server

This script creates a simple Flask server that focuses on serving the frontend
correctly when other methods fail. It doesn't handle API routes but redirects
them to the main API server.
"""

from flask import Flask, send_from_directory, render_template_string, redirect, request
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Find paths for frontend files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_BUILD = os.path.join(BASE_DIR, 'frontend', 'build')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
FRONTEND_STATIC = os.path.join(FRONTEND_BUILD, 'static')

# API server details
API_HOST = os.environ.get('API_HOST', 'localhost')
API_PORT = os.environ.get('API_PORT', '5000')
API_URL = f"http://{API_HOST}:{API_PORT}"

# Create Flask app with correct static folder config
app = Flask(__name__, static_folder=None)

# Route for serving static files from both possible locations
@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files from either location"""
    # Try frontend build static directory first
    if os.path.exists(FRONTEND_STATIC):
        static_file = os.path.join(FRONTEND_STATIC, path)
        if os.path.exists(static_file) and os.path.isfile(static_file):
            logger.info(f"Serving static file from frontend build: {path}")
            return send_from_directory(FRONTEND_STATIC, path)
    
    # Try root static directory next
    if os.path.exists(STATIC_DIR):
        static_file = os.path.join(STATIC_DIR, path)
        if os.path.exists(static_file) and os.path.isfile(static_file):
            logger.info(f"Serving static file from root static: {path}")
            return send_from_directory(STATIC_DIR, path)
    
    # If neither exists, return a 404
    logger.warning(f"Static file not found: {path}")
    return "File not found", 404

# Redirect API requests to the main API server
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_redirect(path):
    """Redirect API requests to the main API server"""
    return redirect(f"{API_URL}/api/{path}")

# Serve index.html for all other routes (SPA routing)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve the frontend SPA"""
    # Check if the path exists as a file
    if path:
        # Try in frontend build dir first
        if os.path.exists(FRONTEND_BUILD):
            file_path = os.path.join(FRONTEND_BUILD, path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                logger.info(f"Serving file from frontend build: {path}")
                return send_from_directory(FRONTEND_BUILD, path)
        
        # Try in root dir next
        file_path = os.path.join(BASE_DIR, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            logger.info(f"Serving file from root: {path}")
            directory, filename = os.path.split(file_path)
            return send_from_directory(directory, filename)
    
    # Look for index.html in multiple locations
    index_locations = [
        os.path.join(FRONTEND_BUILD, 'index.html'),
        os.path.join(BASE_DIR, 'index.html'),
    ]
    
    for index_path in index_locations:
        if os.path.exists(index_path):
            logger.info(f"Serving index.html from: {index_path}")
            directory, filename = os.path.split(index_path)
            return send_from_directory(directory, filename)
    
    # Fallback to a simple HTML page
    logger.warning("No index.html found, serving fallback page")
    return render_template_string('''
    <!DOCTYPE html>
    <html>
        <head>
            <title>AI Trading Bot</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #121212;
                    color: #e1e1e1;
                }
                .container {
                    max-width: 800px;
                    padding: 2rem;
                    background-color: #1e1e1e;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    text-align: center;
                }
                h1 {
                    color: #4a90e2;
                    margin-bottom: 1rem;
                }
                p {
                    line-height: 1.6;
                    margin-bottom: 1.5rem;
                }
                .status {
                    padding: 0.5rem 1rem;
                    background-color: #e7f3ff;
                    border-radius: 4px;
                    display: inline-block;
                    font-weight: bold;
                    color: #0062cc;
                }
                .api-link {
                    display: inline-block;
                    margin-top: 1rem;
                    padding: 0.5rem 1rem;
                    background-color: #4a90e2;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI Trading Bot</h1>
                <div class="status">Fallback Server Active</div>
                <p>The frontend server is running in failsafe mode. Normal index.html could not be found.</p>
                <a href="/api/health" class="api-link">Check API Health</a>
            </div>
        </body>
    </html>
    ''')

if __name__ == '__main__':
    # Determine port from environment or use default
    port = int(os.environ.get('PORT', 8080))
    
    # Log server information
    logger.info(f"Starting failsafe frontend server on port {port}")
    logger.info(f"Frontend build directory: {FRONTEND_BUILD}")
    logger.info(f"Static directory: {STATIC_DIR}")
    logger.info(f"API server: {API_URL}")
    
    # Check for index.html
    index_exists = False
    index_locations = [
        os.path.join(FRONTEND_BUILD, 'index.html'),
        os.path.join(BASE_DIR, 'index.html')
    ]
    
    for path in index_locations:
        if os.path.exists(path):
            logger.info(f"Found index.html at: {path}")
            index_exists = True
            break
    
    if not index_exists:
        logger.warning("No index.html found in any expected location!")
    
    # Run the server
    app.run(host='0.0.0.0', port=port, debug=False) 