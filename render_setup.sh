#!/bin/bash
# Render setup script for AI Trading Bot

echo "Starting Render setup script"

# Create necessary directories
echo "Creating directories..."
mkdir -p frontend/build/static/css frontend/build/static/js frontend/build/static/images
mkdir -p static/css static/js static/images

# Run the preparation script
echo "Running deployment preparation script..."
python prepare_render_deployment.py

# Verify files were created
echo "Verifying files..."
ls -la frontend/build/static
ls -la frontend/build

echo "Render setup complete" 
