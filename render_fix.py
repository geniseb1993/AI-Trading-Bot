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
    \"\"\"Load market data configuration from config file.\"\"\"
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
    \"\"\"Save market data configuration to config file.\"\"\"
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


def create_mock_modules(base_path):
    """Create mock implementations of common external modules that might be missing."""
    mock_modules_dir = os.path.join(base_path, 'mock_modules')
    os.makedirs(mock_modules_dir, exist_ok=True)
    
    # Create __init__.py in the mock_modules directory
    init_path = os.path.join(mock_modules_dir, '__init__.py')
    write_file(init_path, "# Mock modules package", "mock_modules/__init__.py")
    
    # Create mock plyer module
    plyer_path = os.path.join(mock_modules_dir, 'plyer.py')
    plyer_content = """
# Mock implementation of plyer module
class notification:
    @staticmethod
    def notify(title=None, message=None, app_name=None, app_icon=None, timeout=10, ticker=None, toast=False):
        print(f"MOCK NOTIFICATION: {title} - {message}")
"""
    write_file(plyer_path, plyer_content, "mock_modules/plyer.py")
    
    # Create a file to install the mock modules
    install_path = os.path.join(base_path, 'install_mock_modules.py')
    install_content = """
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_mock_modules():
    \"\"\"Install mock modules to handle missing dependencies.\"\"\"
    # Add the mock_modules directory to sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mock_modules_dir = os.path.join(current_dir, 'mock_modules')
    
    if os.path.exists(mock_modules_dir):
        logger.info(f"Adding mock modules directory to sys.path: {mock_modules_dir}")
        sys.path.insert(0, mock_modules_dir)
        
        # List all the mock modules available
        mock_modules = [f[:-3] for f in os.listdir(mock_modules_dir) 
                       if f.endswith('.py') and f != '__init__.py']
        logger.info(f"Available mock modules: {', '.join(mock_modules)}")
        
        # Try importing each mock module
        for module_name in mock_modules:
            try:
                # First try to import the real module
                __import__(module_name)
                logger.info(f"Real module {module_name} found, no need for mock")
            except ImportError:
                # If import fails, the mock will be used instead
                logger.info(f"Real module {module_name} not found, mock will be used")
    else:
        logger.warning(f"Mock modules directory not found: {mock_modules_dir}")

if __name__ == "__main__":
    install_mock_modules()
"""
    write_file(install_path, install_content, "install_mock_modules.py")
    
    # Also create requirements.py to fix missing packages
    requirements_path = os.path.join(base_path, 'check_requirements.py')
    requirements_content = """
import sys
import os
import logging
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_and_install_packages():
    \"\"\"Check if required packages are installed and install them if needed.\"\"\"
    required_packages = [
        'flask',
        'flask-cors',
        'gunicorn',
        'pandas',
        'python-dotenv',
        'requests',
        'alpaca-trade-api',
        'plyer',
        'polygon-api-client'
    ]
    
    installed_packages = []
    missing_packages = []
    
    # Check which packages are already installed
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            installed_packages.append(package)
        except ImportError:
            missing_packages.append(package)
    
    logger.info(f"Installed packages: {', '.join(installed_packages)}")
    logger.info(f"Missing packages: {', '.join(missing_packages)}")
    
    # Try to install missing packages
    if missing_packages:
        try:
            logger.info("Attempting to install missing packages...")
            for package in missing_packages:
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    logger.info(f"Successfully installed {package}")
                except Exception as e:
                    logger.error(f"Failed to install {package}: {e}")
        except Exception as e:
            logger.error(f"Error installing packages: {e}")
    
    return missing_packages

if __name__ == "__main__":
    check_and_install_packages()
"""
    write_file(requirements_path, requirements_content, "check_requirements.py")


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
    
    # Create mock modules for common external dependencies
    create_mock_modules(base_path)

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
