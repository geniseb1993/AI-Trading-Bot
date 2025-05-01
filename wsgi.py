#!/usr/bin/env python
"""
WSGI entry point for the AI Trading Bot API.
This file is used by Gunicorn to run the application in production.
"""

import os
import logging
import sys
from pathlib import Path
from ensure_directories import ensure_directories
from api import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Run emergency check for static files
try:
    from check_static_files import check_static_files, emergency_create_static_files
    logger.info("Checking static files on startup...")
    if not check_static_files():
        logger.warning("Static file check failed, using emergency creation")
        emergency_create_static_files()
except Exception as e:
    logger.error(f"Error checking static files: {str(e)}")
    
    # Still try to create static files even if check_static_files.py failed
    logger.info("Creating essential static files directly...")
    try:
        # Get the base directory
        base_dir = Path(os.getcwd())
        
        # Create directories
        static_dir = base_dir / 'static'
        css_dir = static_dir / 'css'
        js_dir = static_dir / 'js'
        os.makedirs(css_dir, exist_ok=True)
        os.makedirs(js_dir, exist_ok=True)
        
        # Create minimal index.html
        with open(base_dir / 'index.html', 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vicki AI Trading Bot</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div id="root"></div>
    <script src="/static/js/main.js"></script>
</body>
</html>""")
        
        # Create minimal CSS
        with open(css_dir / 'main.css', 'w') as f:
            f.write("body { font-family: Arial; background: #121212; color: white; }")
        
        # Create minimal JS
        with open(js_dir / 'main.js', 'w') as f:
            f.write("console.log('Emergency JS loaded');")
        
        logger.info("Created essential static files directly")
    except Exception as e2:
        logger.error(f"Failed to create essential static files: {str(e2)}")

# Ensure all necessary directories exist before starting the app
ensure_directories()

# Create Flask application
app = create_app()

if __name__ == "__main__":
    # Run the app (for development only - use Gunicorn in production)
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting application on port {port}")
    app.run(host="0.0.0.0", port=port) 