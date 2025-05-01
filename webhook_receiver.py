"""
Compatibility module for Render deployment.
This file simply imports and exposes the app from wsgi.py.
"""

# Import the app from wsgi.py
from wsgi import app

# This file is referenced by Render's default gunicorn command
# No additional code needed - the import above is sufficient 