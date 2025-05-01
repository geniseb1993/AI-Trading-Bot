#!/usr/bin/env python
"""
WSGI entry point for the AI Trading Bot API.
This file is used by Gunicorn to run the application in production.
"""

import os
import sys
import logging
from flask import request, send_file
from pathlib import Path

# Add current directory and api directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'api'))

# Import the Flask app
from api import app

# -----------------------------
# Logging Configuration
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -----------------------------
# Optional Setup Scripts
# -----------------------------
def try_import_and_run(module_name, function_name):
    try:
        module = __import__(module_name)
        func = getattr(module, function_name)
        func()
        logger.info(f"{function_name} from {module_name} executed successfully.")
    except (ImportError, AttributeError) as e:
        logger.warning(f"{function_name} not run. Reason: {e}")

try_import_and_run("check_static_files", "check_static_files")
try_import_and_run("ensure_directories", "ensure_directories")
try_import_and_run("setup_static_files", "setup_static_files")
try_import_and_run("copy_to_frontend_build", "copy_to_frontend_build")

# -----------------------------
# Default ENV Config
# -----------------------------
if 'SERVE_FRONTEND' not in os.environ:
    os.environ['SERVE_FRONTEND'] = 'true'
    logger.info("Environment variable SERVE_FRONTEND was not set. Defaulting to 'true'.")

# -----------------------------
# Debug Hook (Not for Production)
# -----------------------------
@app.before_request
def enable_debug_in_non_debug_mode():
    if not app.debug:
        app.debug = True

# -----------------------------
# Custom 404 to Serve React SPA
# -----------------------------
@app.errorhandler(404)
def fallback_to_index(e):
    path = request.path
    logger.warning(f"404 for path: {path}")

    if path.startswith('/static/'):
        frontend_path = os.path.join('frontend', 'build', path[1:])
        if os.path.exists(frontend_path):
            logger.info(f"Serving fallback static file: {frontend_path}")
            return send_file(frontend_path)

    if os.environ.get('SERVE_FRONTEND', 'false').lower() == 'true':
        index_paths = [
            os.path.join('frontend', 'build', 'index.html'),
            os.path.join('index.html'),
        ]
        for index_path in index_paths:
            if os.path.exists(index_path):
                logger.info(f"Serving index.html from {index_path}")
                return send_file(index_path)

    return e

# -----------------------------
# Local Run Entry Point
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=True)
