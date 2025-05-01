#!/bin/bash
# Shell script for starting the application on Render

# Run the deployment helper to check and fix common issues
echo "Running deployment helper..."
python deployment_helper.py

# Ensure all required directories exist
echo "Ensuring directories exist..."
python ensure_directories.py

# Run database migrations or initialization if needed
# python init_db.py

# Try different app modules if needed
if [ -f "wsgi.py" ]; then
    echo "Starting with wsgi.py..."
    FLASK_APP=wsgi.py gunicorn wsgi:app \
        --workers=4 \
        --threads=2 \
        --timeout=120 \
        --bind=0.0.0.0:$PORT \
        --log-level=info \
        --access-logfile=- \
        --error-logfile=-
elif [ -f "webhook_receiver.py" ]; then
    echo "Starting with webhook_receiver.py..."
    FLASK_APP=webhook_receiver.py gunicorn webhook_receiver:app \
        --workers=4 \
        --threads=2 \
        --timeout=120 \
        --bind=0.0.0.0:$PORT \
        --log-level=info \
        --access-logfile=- \
        --error-logfile=-
else
    echo "No suitable app module found. Cannot start the application."
    exit 1
fi 