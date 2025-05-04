#!/bin/bash

echo "Starting AI Trading Bot..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not found. Please install Python 3 and try again."
    exit 1
fi

# Try to run using the virtual environment first
if [ -f ".venv/bin/python" ]; then
    echo "Using virtual environment..."
    .venv/bin/python start_unified.py
else
    echo "Virtual environment not found. Using system Python..."
    python3 start_unified.py
fi 