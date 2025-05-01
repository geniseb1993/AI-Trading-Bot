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
        from flask import Flask, render_template_string
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>AI Trading Bot - Error</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                    .container { max-width: 800px; margin: 0 auto; background: #f8f9fa; padding: 20px; border-radius: 5px; }
                    h1 { color: #d9534f; }
                    .card { border: 1px solid #ddd; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>AI Trading Bot - Error</h1>
                    <div class="card">
                        <h2>Application Error</h2>
                        <p>The main application failed to load. This could be due to missing dependencies or configuration issues.</p>
                    </div>
                    <div class="card">
                        <h3>Troubleshooting</h3>
                        <p>Check the application logs for more details on what went wrong.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            return render_template_string(html)
        
        logger.info("Created fallback Flask app")
    except Exception as e:
        logger.critical(f"Could not create fallback Flask app: {e}")
        sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error importing app from wsgi.py: {e}")
    
    # Fallback to creating a minimal Flask app
    try:
        logger.info("Creating fallback Flask app after unexpected error")
        from flask import Flask, render_template_string
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>AI Trading Bot - Error</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                    .container { max-width: 800px; margin: 0 auto; background: #f8f9fa; padding: 20px; border-radius: 5px; }
                    h1 { color: #d9534f; }
                    .card { border: 1px solid #ddd; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>AI Trading Bot - Error</h1>
                    <div class="card">
                        <h2>Application Error</h2>
                        <p>The main application failed to load. Error: {str(e)}</p>
                    </div>
                    <div class="card">
                        <h3>Troubleshooting</h3>
                        <p>Check the application logs for more details on what went wrong.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            return render_template_string(html)
        
        logger.info("Created fallback Flask app")
    except Exception as e2:
        logger.critical(f"Could not create fallback Flask app: {e2}")
        sys.exit(1)

# This file is referenced by Render's default gunicorn command
# No additional code needed - the import above is sufficient 