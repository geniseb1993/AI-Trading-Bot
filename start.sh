#!/bin/bash
# This is a start script for Render deployment

echo "Starting AI Trading Bot on port $PORT"

# Activate Python virtual environment
source .venv/bin/activate

# Run the application with gunicorn
gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 