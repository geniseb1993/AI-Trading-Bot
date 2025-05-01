#!/usr/bin/env python3
"""
Minimalist Flask Application

This serves as a fallback in case the main application fails to load.
It provides basic API endpoints and serves the frontend.
"""

from flask import Flask, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up static folder path
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'build')
if not os.path.exists(static_folder):
    os.makedirs(static_folder, exist_ok=True)
    logger.info(f"Created static folder at {static_folder}")

# Create Flask app
app = Flask(__name__, static_folder=static_folder)
CORS(app)

@app.route('/api/status')
def status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'mode': 'fallback',
        'message': 'Fallback Flask app is running'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/api/health')
def api_health():
    """API health check endpoint"""
    return jsonify({'status': 'healthy', 'api': 'online'})

# Serve the frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve the frontend React application"""
    try:
        # Check if path exists in static folder
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
            
        # Otherwise, serve the index.html file
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
            
        # Fallback to a simple HTML page
        return render_template_string("""
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
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>AI Trading Bot</h1>
                    <div class="status">API Status: Running (Fallback Mode)</div>
                    <p>The fallback API server is operational and ready to process requests.</p>
                </div>
            </body>
        </html>
        """)
    except Exception as e:
        logger.error(f"Error serving frontend: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
