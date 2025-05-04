#!/bin/bash
# Fix static file organization for Render deployment

set -e  # Exit on any error

echo "===== STARTING STATIC FILES FIX FOR RENDER DEPLOYMENT ====="

# Ensure Python environment is activated
echo "Checking Python environment..."
python --version

# Clean up and reorganize static files
echo "Running static files cleanup script..."
python fix_static_files.py

# Verify static files are properly organized
echo "Verifying static files organization..."
python check_static_files.py

# Print directory structure for debugging
echo "Directory structure after fixes:"
ls -la
ls -la static/
ls -la static/js/ 2>/dev/null || echo "No js directory found"
ls -la static/css/ 2>/dev/null || echo "No css directory found"

echo "===== STATIC FILES FIX COMPLETED =====" 