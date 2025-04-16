"""
Simple script to run the Flask API server directly.
This avoids complex import issues by running it directly.
"""

import os
import sys
import subprocess

# Path to the Flask app
api_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api')
app_path = os.path.join(api_dir, 'app.py')

# Print information for debugging
print(f"API directory: {api_dir}")
print(f"App path: {app_path}")

if not os.path.exists(app_path):
    print(f"Error: {app_path} not found!")
    sys.exit(1)

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add api directory to Python path
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

# Add execution_model to Python path
execution_model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'execution_model')
if execution_model_dir not in sys.path:
    sys.path.insert(0, execution_model_dir)

# Use subprocess to run Flask directly
print("Starting Flask API server...")
try:
    # For Windows
    if os.name == 'nt':
        os.system(f'cd {api_dir} && python app.py')
    # For Linux/Mac
    else:
        os.system(f'cd {api_dir} && python3 app.py')
except Exception as e:
    print(f"Error starting Flask app: {str(e)}")
    sys.exit(1) 