#!/bin/bash
# Shell script for starting the application on Render

# Ensure all required directories exist
python ensure_directories.py

# Run database migrations or initialization if needed
# python init_db.py

# Start the application with Gunicorn
# Adjust the number of workers based on your needs
# General rule: 2-4 workers per CPU core
gunicorn wsgi:app \
    --workers=4 \
    --threads=2 \
    --timeout=120 \
    --bind=0.0.0.0:$PORT \
    --log-level=info \
    --access-logfile=- \
    --error-logfile=- 