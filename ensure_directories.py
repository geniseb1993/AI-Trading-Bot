#!/usr/bin/env python
"""
Ensure required directories exist before starting the application.
"""

import os
import logging
from pathlib import Path
import shutil

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
        "frontend/build/static",
        "frontend/build/static/js",
        "frontend/build/static/css",
        "frontend/build/static/media"
    ]
    
    # Create directories
    logger.info("Ensuring all required directories exist...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Checked directory: {directory}")
    
    # Ensure key image files are in both frontend/public and public directories
    try:
        # List of files to sync between directories with [source, destination] format
        files_to_sync = [
            # Images
            ["frontend/public/images/velma.png", "public/images/velma.png"],
            ["frontend/public/images/vicky.png", "public/images/vicky.png"],
            ["frontend/public/images/Vicky-Image.png", "public/images/Vicky-Image.png"],
            
            # Also copy the images to build directory (in case they're referenced directly)
            ["frontend/public/images/velma.png", "frontend/build/images/velma.png"],
            ["frontend/public/images/vicky.png", "frontend/build/images/vicky.png"],
            ["frontend/public/images/Vicky-Image.png", "frontend/build/images/Vicky-Image.png"],
            
            # Create reverse copies if needed
            ["public/images/velma.png", "frontend/public/images/velma.png"],
            ["public/images/vicky.png", "frontend/public/images/vicky.png"],
        ]
        
        # Make sure the frontend/build/images directory exists
        os.makedirs("frontend/build/images", exist_ok=True)
        
        # Copy files if source exists and destination doesn't
        for src, dest in files_to_sync:
            if os.path.exists(src) and not os.path.exists(dest):
                logger.info(f"Copying {src} to {dest}")
                shutil.copy2(src, dest)
            elif not os.path.exists(src) and os.path.exists(dest):
                # If source doesn't exist but destination does, copy back
                parent_dir = os.path.dirname(src)
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                logger.info(f"Copying {dest} to {src}")
                shutil.copy2(dest, src)
    except Exception as e:
        logger.error(f"Error syncing image files: {str(e)}")
    
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
    
    # Create a manifest.json if it doesn't exist
    manifest_path = frontend_build_dir / "manifest.json"
    if not manifest_path.exists():
        logger.warning("Creating placeholder manifest.json")
        with open(manifest_path, 'w') as f:
            f.write("""{
  "short_name": "Vicki",
  "name": "Vicki AI Trading Bot",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    },
    {
      "src": "images/vicky.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "images/vicky.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}""")
    
    logger.info("Directory check complete.")
    return True

if __name__ == "__main__":
    logger.info("Running directory check...")
    ensure_directories()
    logger.info("Directory check complete") 