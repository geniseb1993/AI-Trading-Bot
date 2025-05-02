#!/usr/bin/env python
"""
Flask App

This is a simplified version of the main Flask application,
serving as a fallback for direct imports or when the main app can't be loaded.
"""

import os
import sys
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# API status endpoint
@app.route('/api/status')
def status():
    return jsonify({
        'status': 'online',
        'version': '1.0',
        'message': 'Fallback API is running'
    })

# Index route
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AI Trading Bot</title>
            <style>
                body { font-family: sans-serif; padding: 2rem; max-width: 800px; margin: 0 auto; }
                h1 { color: #4a90e2; }
            </style>
        </head>
        <body>
            <h1>AI Trading Bot</h1>
            <p>The API is running in fallback mode.</p>
        </body>
    </html>
    """

# Run app if executed directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
