#!/usr/bin/env python
"""
WSGI entry point for the AI Trading Bot API.
This file is used by Gunicorn to run the application in production.
"""

import os
import logging
from ensure_directories import ensure_directories
from api import create_app

# Ensure all necessary directories exist before starting the app
ensure_directories()

# Create Flask application
app = create_app()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Run the app (for development only - use Gunicorn in production)
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting application on port {port}")
    app.run(host="0.0.0.0", port=port) 