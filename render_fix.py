#!/usr/bin/env python3
"""
Render Fix Script

This script sets up required directories and static files to ensure
the web application can be served correctly in the Render deployment environment.
"""

import os
import logging
import shutil
from pathlib import Path
import base64
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ensure_directories(base_path):
    """Ensure that all required directories exist."""
    dirs = [
        'static/css',
        'static/js',
        'static/images',
        'frontend/build/static/css',
        'frontend/build/static/js',
        'frontend/build/static/images',
        'api/lib',  # Add lib directory
    ]
    for d in dirs:
        full_path = os.path.join(base_path, d)
        os.makedirs(full_path, exist_ok=True)
        logger.info(f"Ensured directory: {full_path}")


def write_file(filepath, content, description="file"):
    """Write content to a file, handling errors."""
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        logger.info(f"Created/updated {description}: {filepath}")
    except Exception as e:
        logger.error(f"Failed to write {description} at {filepath}: {e}")


def copy_file(src, dst):
    """Copy file from src to dst with logging."""
    try:
        shutil.copy2(src, dst)
        logger.info(f"Copied file from {src} to {dst}")
    except Exception as e:
        logger.error(f"Failed to copy file from {src} to {dst}: {e}")


def create_placeholder_image(filepath):
    """Create a placeholder magenta circle PNG image if it does not exist."""
    if os.path.exists(filepath):
        return

    placeholder_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAB3RJTUUH5QoaFiUw"
        "2kH7uAAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAGySURBVFjD7ZjNSgNBEIY/bCVJpNjaJJWk"
        "UFJ9A/IG0kVJEEkhb8Qo1O+QUsLZEdsIIkFIk8WTSZMGz+w+V+cjdnJr+ybnZ2Zl5u74M+JiIjEyYFHAANnALaARmA7y"
        "2AErQCtwFF4A74A3MBOSApD8R8An8Bs8Obd5jtxXMAdO9MIaCthT0uQEVrZ0AAMW1fipbJ5m+lX5FVDPl1AR1gOcHzUF"
        "sh5qgPGltZgPl9M+S0AzGm8s2u79bAZGzZqAdgzj4QMdYlY5C1h6DFvMAA93lRQCrzgFbBPuAvWYtO91eZ4mgVs5xrLr"
        "uYZM+B4qM1xAyS2U0lhBqApD9lzvTzJh3R+Cw+i5F7U8ZNHsxLEqU8BP+t52RMVz3Rx4ZwAAAABJRU5ErkJggg=="
    )

    try:
        with open(filepath, 'wb') as img:
            img.write(base64.b64decode(placeholder_base64))
        logger.info(f"Created placeholder image: {filepath}")
    except Exception as e:
        logger.error(f"Failed to create placeholder image at {filepath}: {e}")


def create_lib_modules(base_path):
    """Create simple lib module files to prevent import errors."""
    # Create __init__.py in the lib directory
    lib_init_path = os.path.join(base_path, 'api', 'lib', '__init__.py')
    write_file(lib_init_path, "# Lib package", "lib/__init__.py")
    
    # Create market_data.py module
    market_data_path = os.path.join(base_path, 'api', 'lib', 'market_data.py')
    market_data_content = """
# Mock implementation of MarketDataSourceManager
class MarketDataSourceManager:
    def __init__(self, config=None):
        self.active_source = config.get('active_source', 'mock') if config else 'mock'
        self.sources = {'mock': MockDataSource()}
        
    def get_market_data(self, symbols, data_type='bars', timeframe='1Day', limit=100):
        return {'bars': {symbol: [] for symbol in symbols}}
        
    def set_active_source(self, source):
        if source in self.sources:
            self.active_source = source
            return True
        return False

class MockDataSource:
    def __init__(self):
        self.name = 'mock'
        self.server_running = False
        
    def get_alerts(self):
        return []
        
    def clear_webhooks(self):
        pass
"""
    write_file(market_data_path, market_data_content, "lib/market_data.py")
    
    # Create market_data_config.py module
    config_path = os.path.join(base_path, 'api', 'lib', 'market_data_config.py')
    config_content = """
import os
import json

def load_market_data_config():
    """Load market data configuration from config file."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'market_data_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    
    # Return default config if file doesn't exist or has errors
    return {
        'active_source': 'mock',
        'mock': {
            'use_csv_data': True
        }
    }

def save_market_data_config(config):
    """Save market data configuration to config file."""
    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, 'market_data_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False
"""
    write_file(config_path, config_content, "lib/market_data_config.py")


def get_direct_html_content():
    """Return the content of the fallback HTML page."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Vicki AI Trading Bot</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="app">
        <div class="sidebar">
            <h2>Sidebar</h2>
        </div>
        <div class="main-content">
            <h1>Welcome to Vicki AI</h1>
            <button class="btn">Launch</button>
        </div>
    </div>
    <script src="/static/js/main.js"></script>
</body>
</html>
"""


def run_render_fix():
    """Main entry to create all required files and structure."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Starting Render Fix in: {base_path}")

    # Ensure directories exist
    ensure_directories(base_path)
    
    # Create lib modules to prevent import errors
    create_lib_modules(base_path)

    # Create fallback HTML
    direct_html_path = os.path.join(base_path, 'direct.html')
    write_file(direct_html_path, get_direct_html_content(), 'direct.html')

    # Copy to index.html targets
    index_targets = [
        os.path.join(base_path, 'index.html'),
        os.path.join(base_path, 'frontend', 'build', 'index.html')
    ]
    for target in index_targets:
        copy_file(direct_html_path, target)

    # Create main.css
    css_content = """
body { background-color: #121212; color: #ffffff; font-family: Arial, sans-serif; margin: 0; padding: 0; }
.app { display: flex; min-height: 100vh; }
.sidebar { width: 220px; background-color: #111; padding: 20px; border-right: 2px solid #ff00ff; }
.main-content { flex: 1; padding: 20px; }
.card { background-color: #1c1c2e; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
.btn { background-color: #ff00ff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
"""
    for path in ['static/css/main.css', 'frontend/build/static/css/main.css']:
        write_file(os.path.join(base_path, path), css_content, 'main.css')

    # Create main.js
    js_content = "document.addEventListener('DOMContentLoaded', () => console.log('Vicki AI UI Loaded'));"
    for path in ['static/js/main.js', 'frontend/build/static/js/main.js']:
        write_file(os.path.join(base_path, path), js_content, 'main.js')

    # Create manifest.json
    manifest_content = """{
  "short_name": "Vicki",
  "name": "Vicki AI Trading Bot",
  "icons": [
    {
      "src": "/static/images/logo.png",
      "type": "image/png",
      "sizes": "192x192"
    }
  ],
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#121212"
}"""
    for path in [
        'static/manifest.json',
        'frontend/build/manifest.json',
        'frontend/build/static/manifest.json'
    ]:
        write_file(os.path.join(base_path, path), manifest_content, 'manifest.json')

    # Create placeholder images
    for path in [
        'static/images/logo.png',
        'static/images/vicky.png',
        'frontend/build/static/images/logo.png',
        'frontend/build/static/images/vicky.png',
    ]:
        create_placeholder_image(os.path.join(base_path, path))

    logger.info("Render Fix complete.")


if __name__ == "__main__":
    run_render_fix()
