#!/usr/bin/env python
"""
Check Static Files

This script ensures that static files exist and creates them if needed.
It can be imported and used as a Flask before_request handler.
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

def check_static_files():
    """Check that static files exist and create them if needed."""
    # Get the base directory (project root)
    base_dir = Path(os.getcwd())
    static_dir = base_dir / 'static'
    css_dir = static_dir / 'css'
    js_dir = static_dir / 'js'
    
    # Check if index.html exists
    index_path = base_dir / 'index.html'
    if not index_path.exists():
        logger.warning(f"index.html missing at {index_path}, will recreate")
        create_needed = True
    else:
        logger.info(f"index.html exists at {index_path}")
    
    # Check CSS file
    css_file = css_dir / 'main.css'
    if not css_file.exists():
        logger.warning(f"main.css missing at {css_file}, will recreate")
        create_needed = True
    else:
        logger.info(f"main.css exists at {css_file}")
    
    # Check JS file
    js_file = js_dir / 'main.js'
    if not js_file.exists():
        logger.warning(f"main.js missing at {js_file}, will recreate")
        create_needed = True
    else:
        logger.info(f"main.js exists at {js_file}")
    
    # If any files are missing, run the setup script
    if 'create_needed' in locals() and create_needed:
        logger.info("Running setup_static_files.py to recreate missing files")
        try:
            from setup_static_files import setup_static_files
            setup_static_files()
            return True
        except Exception as e:
            logger.error(f"Error creating static files: {e}")
            return False
    
    return True

def emergency_create_static_files():
    """Create minimal static files at required locations as a last resort."""
    logger.info("Emergency creating static files...")
    
    # Get the base directory (project root)
    base_dir = Path(os.getcwd())
    static_dir = base_dir / 'static'
    css_dir = static_dir / 'css'
    js_dir = static_dir / 'js'
    
    # Create directories
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)
    
    # Create index.html
    with open(base_dir / 'index.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vicki AI Trading Bot</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; margin: 0; padding: 20px; }
        h1 { color: #61dafb; }
        a { color: #61dafb; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div id="root">
        <h1>Vicki AI Trading Bot</h1>
        <p>Emergency static version - direct link to API endpoints:</p>
        <ul>
            <li><a href="/api/health">Health Check</a></li>
            <li><a href="/api/bot/status">Bot Status</a></li>
            <li><a href="/api/market-overview">Market Overview</a></li>
            <li><a href="/api/portfolio-performance">Portfolio Performance</a></li>
            <li><a href="/api/diagnostic">Diagnostic Information</a></li>
        </ul>
    </div>
</body>
</html>""")
    
    # Create CSS file
    with open(css_dir / 'main.css', 'w') as f:
        f.write("""
body {
    font-family: Arial, sans-serif;
    background-color: #121212;
    color: #ffffff;
    margin: 0;
    padding: 0;
}
#root {
    padding: 20px;
}
h1 {
    color: #61dafb;
}
a {
    color: #61dafb;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
""")
    
    # Create JS file
    with open(js_dir / 'main.js', 'w') as f:
        f.write("""
console.log('Emergency JS file loaded');
""")
    
    logger.info("Emergency static files created")
    return True

if __name__ == "__main__":
    check_static_files() 