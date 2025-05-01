"""
Compatibility module for Render deployment.
This file simply imports and exposes the app from wsgi.py.
"""

import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import the app from wsgi.py
try:
    logger.info("Importing Flask app from wsgi.py")
    from wsgi import app
    logger.info("Successfully imported Flask app from wsgi.py")
except ImportError as e:
    logger.error(f"Failed to import app from wsgi.py: {e}")
    
    # Fallback to creating a minimal Flask app
    try:
        logger.info("Creating fallback Flask app")
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return {"status": "running", "message": "Fallback Flask app - main app failed to load"}
        
        logger.info("Created fallback Flask app")
    except Exception as e:
        logger.critical(f"Could not create fallback Flask app: {e}")
        sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error importing app from wsgi.py: {e}")
    
    # Fallback to creating a minimal Flask app
    try:
        logger.info("Creating fallback Flask app after unexpected error")
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return {"status": "error", "message": f"Error loading main app: {str(e)}"}
        
        logger.info("Created fallback Flask app")
    except Exception as e2:
        logger.critical(f"Could not create fallback Flask app: {e2}")
        sys.exit(1)

# This file is referenced by Render's default gunicorn command
# No additional code needed - the import above is sufficient 