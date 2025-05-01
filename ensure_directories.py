#!/usr/bin/env python
"""
Ensure required directories exist before starting the application.
"""

import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure all necessary directories exist for the application."""
    # List of directories to ensure exist
    directories = [
        "data",
        "data/logs",
        "data/broker",
        "data/market_data",
        "data/signals",
        "data/dashboard",
        "logs",
        "instance",
        "public/images",
        "public/sounds",
        "frontend/build",
        "frontend/build/static"
    ]
    
    # Create directories
    logger.info("Ensuring all required directories exist...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Checked directory: {directory}")
    
    # Make sure frontend build directory has index.html if it doesn't exist
    frontend_build_dir = Path("frontend/build")
    index_path = frontend_build_dir / "index.html"
    
    if not index_path.exists() and os.environ.get('SERVE_FRONTEND', '').lower() == 'true':
        logger.warning("Frontend build directory doesn't have index.html, creating placeholder")
        # Create a simple placeholder index.html
        with open(index_path, 'w') as f:
            f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vicki AI Trading Bot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background-color: #2c3e50;
            color: white;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #34495e;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }
        h1 {
            color: #3498db;
        }
        .message {
            margin: 20px 0;
            padding: 15px;
            background-color: #2980b9;
            border-radius: 4px;
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Vicki AI Trading Bot</h1>
        <div class="message">
            <p>The frontend build appears to be missing.</p>
            <p>Please rebuild the frontend or check the deployment configuration.</p>
        </div>
        <div class="error">
            <p>Error: Frontend build files not found!</p>
            <p>API endpoints are still accessible at /api/*</p>
        </div>
    </div>
</body>
</html>
            """)
        # Also create static directory with an empty CSS file to avoid errors
        static_dir = frontend_build_dir / "static" / "css"
        os.makedirs(static_dir, exist_ok=True)
        
        with open(static_dir / "main.css", 'w') as f:
            f.write("/* Placeholder CSS */")
    
    logger.info("Directory check complete.")
    return True

if __name__ == "__main__":
    logger.info("Running directory check...")
    ensure_directories()
    logger.info("Directory check complete") 