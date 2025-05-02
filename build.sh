#!/bin/bash
# This is a build script for Render deployment

echo "Starting build.sh script for AI Trading Bot"

# Set up Python virtual environment
python -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Copy configuration files
python copy_config_files.py

# Create necessary directories
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p data/logs
mkdir -p data/broker
mkdir -p data/market_data

echo "Build script completed successfully" 